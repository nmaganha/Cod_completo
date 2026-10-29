"""SM Avulso (Doc_Lib. - Click_25): conferência registrada já com a SM salva (Em análise), antes de gerar o documento. Duas
conferências, uma de cada área, levam a SM direto a Aprovado para Execução; o documento é emitido depois."""
import sqlite3

import pytest

from test_sm_avulso_interface import definir, dialogos, estado, janelas, travado  # noqa: F401

pymupdf = pytest.importorskip("pymupdf")

EM_ANALISE, AGUARDA, APROVADO = "Em análise", "Aguarda Conferência", "Aprovado para Execução"
EM_EXECUCAO, CONCLUIDO, CANCELADO, RESERVADO = "Em Execução", "Concluído", "Cancelado", "Reservado"


def historico_de_status(app, sm_id):
    conexao = app.doc_lib_conectar()
    linhas = conexao.execute("SELECT status_anterior, status_novo FROM doclib_sm_historico WHERE sm_id = ? AND evento = 'status' "
                             "ORDER BY id", (sm_id,)).fetchall()
    conexao.close()
    return linhas


class TestConferenciaAntesDeGerar:
    def test_duas_conferencias_em_analise_levam_a_sm_direto_a_aprovado_sem_emitir(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.aprovar(sm_id)
        doc = fluxo.doc(sm_id)
        assert doc["status"] == APROVADO and not doc["emitido"] and len(doc["conferencias"]) == 2
        assert [c["modalidade"] for c in doc["conferencias"]] == ["manual", "sistema"]
        assert historico_de_status(app, sm_id) == [(None, EM_ANALISE), (EM_ANALISE, APROVADO)]       # sem passar por Aguarda Conferência

    def test_so_a_manutencao_ou_so_a_operacao_nao_aprova(self, app, fluxo):
        for primeira, repetida in ((fluxo.conferencia_manual(), fluxo.conferencia_manual(nome="Outro da Manutencao")),
                                   (fluxo.conferencia_sistema(), fluxo.conferencia_sistema())):
            sm_id = fluxo.salvar()
            fluxo.conferir(sm_id, primeira)
            assert fluxo.doc(sm_id)["status"] == EM_ANALISE and not fluxo.doc(sm_id)["emitido"]
            fluxo.conferir(sm_id, repetida, usuario="operador3")                                     # duas da mesma área: ainda não
            assert fluxo.doc(sm_id)["status"] == EM_ANALISE

    def test_primeira_conferencia_protege_os_dados_gerais(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.alterar(sm_id, motivo="Ainda dá para mudar")                                           # sem conferência, edita
        fluxo.conferir(sm_id, fluxo.conferencia_manual())
        for mudanca in (dict(motivo="Mudou depois de conferido"), dict(p0_data_inicio="30/10/2026", p0_data_termino="30/10/2026"),
                        dict(lib_emergencia=1), dict(observacoes="novo texto")):
            with pytest.raises(app.DocLibBloqueado, match="já tem conferência registrada.*cancele a SM.*SM-Referência"):
                fluxo.alterar(sm_id, **mudanca)
        assert fluxo.doc(sm_id)["motivo"] == "Ainda dá para mudar"

    def test_alteracao_geral_na_mesma_gravacao_da_conferencia_e_recusada(self, app, fluxo):
        sm_id = fluxo.salvar()
        gravadas = fluxo.doc(sm_id)["conferencias"]
        with pytest.raises(app.DocLibBloqueado, match="na mesma gravação da conferência"):
            fluxo.alterar(sm_id, motivo="Outro motivo", conferencias=gravadas + [fluxo.conferencia_manual()])
        assert fluxo.doc(sm_id)["motivo"] != "Outro motivo" and fluxo.doc(sm_id)["conferencias"] == []

    def test_conferencia_nao_vale_com_acao_marcada_para_conferir(self, app, fluxo):
        sm_id = fluxo.salvar(normalizacao=[{"numero": "1", "local": "SE MCP", "acao": "Verificar a seccionadora", "conferir": 1}])
        with pytest.raises(app.DocLibValidacaoSM, match="confira a ação"):
            fluxo.conferir(sm_id, fluxo.conferencia_manual())
        assert fluxo.doc(sm_id)["conferencias"] == []

    def test_sm_nova_reservada_e_cancelada_nao_recebem_conferencia(self, app, fluxo):
        with pytest.raises(app.DocLibBloqueado):
            fluxo.salvar(conferencias=[fluxo.conferencia_manual()])                                  # SM nova
        reservada = app.doc_lib_reservar_sm(1, "operador1")[0]["ateie_id"]
        with pytest.raises(app.DocLibBloqueado):
            fluxo.conferir(reservada, fluxo.conferencia_manual())
        sm_id = fluxo.salvar()
        app.doc_lib_cancelar_sm(sm_id, "operador1", "Cancelada", fluxo.doc(sm_id)["revisao"])
        with pytest.raises(app.DocLibBloqueado):
            fluxo.conferir(sm_id, fluxo.conferencia_manual())

    @pytest.mark.parametrize("status, aceita", [(EM_ANALISE, True), (AGUARDA, True), (APROVADO, True), (EM_EXECUCAO, False),
                                                (CONCLUIDO, False)])
    def test_banco_so_aceita_conferencia_nova_com_status_adequado(self, app, fluxo, status, aceita):
        sm_id = fluxo.salvar() if status == EM_ANALISE else fluxo.ate(status)
        sql = ("INSERT INTO doclib_sm_conferencias (sm_id, ordem, modalidade, nome, area, data, ass, registrado_por, registrado_em) "
               "VALUES (?, 9, 'manual', 'x', 'y', '25/10/2026', 'z', 'op', 'agora')")
        conexao = app.doc_lib_conectar()
        try:
            if aceita:
                conexao.execute(sql, (sm_id,))
            else:
                with pytest.raises(sqlite3.DatabaseError, match="só é registrada com a SM"):
                    conexao.execute(sql, (sm_id,))
        finally:
            conexao.close()


class TestEmissaoDepoisDaAprovacao:
    def aprovada_sem_emitir(self, fluxo, **extras):
        sm_id = fluxo.salvar(**extras)
        fluxo.aprovar(sm_id)
        return sm_id

    def test_horarios_e_executantes_da_liberacao_abrem_com_a_sm_aprovada_sem_gerar_o_documento(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        assert not fluxo.doc(sm_id)["emitido"]
        parcial = fluxo.datar(fluxo.doc(sm_id), "liberacao", 8)
        fluxo.alterar(sm_id, liberacao=parcial[:1] + fluxo.doc(sm_id)["liberacao"][1:])             # horários lançados aos poucos
        assert fluxo.doc(sm_id)["liberacao"][0]["hora"] == "08:00" and fluxo.doc(sm_id)["status"] == APROVADO
        fluxo.executar(sm_id)                                                                        # todos os horários + item 7
        doc = fluxo.doc(sm_id)
        assert doc["status"] == EM_EXECUCAO and doc["exec_lib_local"] == "Fulano (campo)" and not doc["emitido"]
        assert historico_de_status(app, sm_id)[-2:] == [(EM_ANALISE, APROVADO), (APROVADO, EM_EXECUCAO)]

    def test_da_conferencia_antes_de_gerar_ate_concluir_sem_nunca_gerar_o_documento(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        fluxo.executar(sm_id)
        fluxo.concluir(sm_id)
        assert fluxo.doc(sm_id)["status"] == CONCLUIDO and not fluxo.doc(sm_id)["emitido"]
        caminho, _ = fluxo.gerar(sm_id)                                                              # gerar o PDF depois continua possível
        texto = " ".join("\n".join(p.get_text() for p in pymupdf.open(caminho)).split())
        assert "Fulano (campo)" in texto and "Aguardando a Conferência" not in texto

    def test_gerar_com_a_sm_em_execucao_emite_o_documento_sem_mudar_o_status(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        fluxo.executar(sm_id)
        fluxo.gerar(sm_id)
        doc = fluxo.doc(sm_id)
        assert doc["emitido"] == 1 and doc["status"] == EM_EXECUCAO
        fluxo.concluir(sm_id)
        assert fluxo.doc(sm_id)["status"] == CONCLUIDO

    def test_sm_conferida_em_analise_com_a_opcao_sem_manobras_executa_e_conclui_sem_gerar(self, app, fluxo):
        for opcao, etapa in (({"nor_sem_manobras": 1}, "lib"), ({"lib_emergencia": 1}, "nor")):
            sm_id = self.aprovada_sem_emitir(fluxo, **opcao)
            fluxo.executar(sm_id) if etapa == "lib" else fluxo.concluir(sm_id)
            assert fluxo.doc(sm_id)["status"] == CONCLUIDO and not fluxo.doc(sm_id)["emitido"]

    def test_gerar_emite_o_documento_mantem_aprovado_e_libera_a_execucao(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        caminho, _ = fluxo.gerar(sm_id)
        doc = fluxo.doc(sm_id)
        assert doc["emitido"] == 1 and doc["status"] == APROVADO
        assert historico_de_status(app, sm_id)[-1] == (EM_ANALISE, APROVADO)                        # a emissão não mexe no status
        texto = " ".join("\n".join(p.get_text() for p in pymupdf.open(caminho)).split())
        assert "Aguardando a Conferência" not in texto and "Joao da Manutencao" in texto and "COG-0001/26" in texto
        fluxo.executar(sm_id)
        assert fluxo.doc(sm_id)["status"] == EM_EXECUCAO                                            # só com as duas primeiras conferências

    def test_as_duas_primeiras_conferencias_bastam_para_executar_as_manobras(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        fluxo.gerar(sm_id)
        assert len(fluxo.doc(sm_id)["conferencias"]) == 2
        fluxo.executar(sm_id)
        fluxo.concluir(sm_id)
        assert fluxo.doc(sm_id)["status"] == CONCLUIDO

    def test_com_a_sm_aprovada_antes_de_gerar_ainda_entram_mais_conferencias_ate_10(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        for numero in range(3, 11):
            fluxo.conferir(sm_id, fluxo.conferencia_manual(nome=f"Conferente {numero:02d}"))
        assert len(fluxo.doc(sm_id)["conferencias"]) == 10
        with pytest.raises(app.DocLibValidacaoSM, match="no máximo 10"):
            fluxo.conferir(sm_id, fluxo.conferencia_manual(nome="Onze"))
        fluxo.gerar(sm_id)
        assert fluxo.doc(sm_id)["status"] == APROVADO

    def test_gerar_com_uma_so_conferencia_vai_a_aguarda_e_a_segunda_aprova(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.conferir(sm_id, fluxo.conferencia_manual())
        fluxo.gerar(sm_id)
        assert fluxo.doc(sm_id)["status"] == AGUARDA and fluxo.doc(sm_id)["emitido"] == 1
        fluxo.conferir(sm_id, fluxo.conferencia_sistema())
        assert fluxo.doc(sm_id)["status"] == APROVADO
        assert historico_de_status(app, sm_id)[-2:] == [(EM_ANALISE, AGUARDA), (AGUARDA, APROVADO)]

    def test_fluxo_antigo_continua_igual(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.gerar(sm_id)
        assert fluxo.doc(sm_id)["status"] == AGUARDA
        fluxo.aprovar(sm_id)
        assert fluxo.doc(sm_id)["status"] == APROVADO and fluxo.doc(sm_id)["emitido"] == 1

    def test_aprovada_antes_de_gerar_aceita_reprogramacao_e_cancelamento_e_serve_de_referencia(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        fluxo.alterar(sm_id, p1_data_inicio="26/10/2026", p1_hora_inicio="08:00", p1_data_termino="26/10/2026",
                      p1_hora_termino="17:00", reprogramacoes=1)
        assert fluxo.doc(sm_id)["p1_hora_termino"] == "17:00"
        nova = fluxo.salvar(**app.doc_lib_dados_referencia_sm(fluxo.doc(sm_id)))
        assert fluxo.doc(nova)["referencia_id"] == sm_id
        app.doc_lib_cancelar_sm(sm_id, "operador1", "Cancelada", fluxo.doc(sm_id)["revisao"])
        assert fluxo.doc(sm_id)["status"] == CANCELADO

    def test_sm_aprovada_antes_de_gerar_pode_ser_encaminhada_por_e_mail_para_conhecimento(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        app.doc_lib_validar_envio_sm(fluxo.doc(sm_id))
        assert app.doc_lib_assunto_e_texto_envio_sm(fluxo.doc(sm_id))[0].endswith("Para conhecimento")

    def test_sm_com_a_opcao_sem_manobras_tambem_pode_ser_conferida_antes_de_gerar(self, app, fluxo):
        for opcao in ({"lib_emergencia": 1}, {"nor_sem_manobras": 1}):
            sm_id = self.aprovada_sem_emitir(fluxo, **opcao)
            assert fluxo.doc(sm_id)["status"] == APROVADO
            fluxo.gerar(sm_id)
            if opcao.get("nor_sem_manobras"):
                fluxo.executar(sm_id)
            else:
                fluxo.concluir(sm_id)
            assert fluxo.doc(sm_id)["status"] == CONCLUIDO


# ======================================================================================================================
# janela
# ======================================================================================================================
def preencher_e_salvar(app, janela):
    from test_sm_avulso_interface import preencher
    preencher(app, janela)
    janela.salvar()
    assert janela.sm_id is not None and janela.status == EM_ANALISE


def entrar_como(app, monkeypatch, login):
    """Troca a pessoa logada (a SM segue elaborada por quem a salvou)."""
    monkeypatch.setattr(app, "current_user", f"{login} em 29/10/2026 - 10:00h")


class TestJanelaComConferenciaEmAnalise:
    def test_botoes_de_conferencia_ficam_ativos_com_a_sm_salva_em_analise(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        assert estado(janela.conferencias.btn_manual) == "disabled"                                  # SM nova, ainda não salva
        preencher_e_salvar(app, janela)
        assert estado(janela.conferencias.btn_manual) == "normal" and estado(janela.conferencias.btn_sistema) == "normal"
        assert estado(janela.btn_editar) == "normal" and estado(janela.btn_gerar) == "normal"
        janela.editar()                                                                              # em edição: só os dados gerais
        assert estado(janela.conferencias.btn_manual) == "disabled" and estado(janela.conferencias.btn_sistema) == "disabled"
        janela.salvar()
        assert estado(janela.conferencias.btn_manual) == "normal"

    def test_registrar_duas_conferencias_aprova_a_sm_antes_de_gerar_o_documento(self, app, banco, janelas, mensagens, dialogos, monkeypatch):
        janela = janelas()
        preencher_e_salvar(app, janela)
        entrar_como(app, monkeypatch, "operador2")                                                   # outra pessoa confere
        conferencias = janela.conferencias
        manutencao = conferencias.adicionar_nova("manual")
        assert estado(janela.btn_salvar) == "normal" and estado(janela.btn_editar) == "disabled"       # há conferência por salvar
        definir(app, manutencao["nome"], "Joao da Manutencao")
        conferencias.adicionar_nova("sistema")
        janela.salvar()
        assert not mensagens.avisos and janela.status == APROVADO and not janela.emitido
        texto = mensagens.infos[-1][1]
        assert "Conferência registrada (2 de 10)" in texto and "Gerar SM Avulso" in texto
        assert estado(janela.btn_editar) == "disabled" and estado(janela.btn_gerar) == "normal"
        assert all(linha["registrada"] for linha in conferencias.linhas)
        assert estado(conferencias.btn_manual) == "normal"                                           # as demais são facultativas
        assert "documento ainda não gerado" in janela.lbl_status.cget("text")
        # dados gerais protegidos; horários e executantes da liberação já abertos, mesmo com o documento ainda não gerado
        assert all(travado(w) for w in janela.periodo["p0"]["widgets"]) and all(travado(w) for w in janela.tab_nor.linhas[0].values()
                                                                                  if hasattr(w, "cget") and w.winfo_class() == "Entry")
        assert all(not travado(linha[campo]) for linha in janela.tab_lib.linhas for campo in ("data", "hora", "icone"))
        assert not travado(janela.ent_exec_lib_local) and not travado(janela.ent_exec_lib_remoto)
        assert estado(janela.periodo["p1"]["botao"]) == "normal"                                    # Aprovada: Habilitar disponível
        assert "Os horários das manobras de liberação e os executantes (itens 6 e 7) já podem ser lançados" in texto
        janela.gerar()
        assert janela.emitido and janela.status == APROVADO and dialogos["gerado"]
        assert not travado(janela.ent_exec_lib_local) and not travado(janela.tab_lib.linhas[0]["data"])
        assert mensagens.perguntas[-1][0] == "Gerar SM Avulso" and "'Aprovado para Execução'" in mensagens.perguntas[-1][1]

    def test_lancar_horarios_e_executantes_pela_janela_com_a_sm_aprovada_sem_gerar(self, app, banco, janelas, mensagens, dialogos, monkeypatch):
        janela = janelas()
        preencher_e_salvar(app, janela)
        entrar_como(app, monkeypatch, "operador2")
        definir(app, janela.conferencias.adicionar_nova("manual")["nome"], "Joao da Manutencao")
        janela.conferencias.adicionar_nova("sistema")
        janela.salvar()
        assert janela.status == APROVADO and not janela.emitido
        for indice, linha in enumerate(janela.tab_lib.linhas):
            definir(app, linha["data"], "25/10/2026")
            definir(app, linha["hora"], f"08:{indice * 10:02d}")
        definir(app, janela.ent_exec_lib_local, "Fulano (campo)")
        janela.salvar()
        assert not [a for a in mensagens.avisos if "Regra" in a[0]] and janela.status == EM_EXECUCAO and not janela.emitido
        assert "passou a Em Execução" in mensagens.infos[-1][1]
        assert all(travado(linha["data"]) for linha in janela.tab_lib.linhas) and travado(janela.ent_exec_lib_local)   # item 6 e 7 bloqueados
        assert not travado(janela.tab_nor.linhas[0]["data"]) and not travado(janela.ent_exec_nor_local)
        assert "documento ainda não gerado" in janela.lbl_status.cget("text")
        janela.gerar()                                                                              # o PDF pode ser gerado com a SM em execução
        assert janela.emitido and janela.status == EM_EXECUCAO and dialogos["gerado"]
        assert "emitido" in janela.lbl_status.cget("text") or "emitida" in janela.lbl_status.cget("text")

    def test_uma_so_conferencia_nao_aprova_e_ja_trava_os_dados_gerais(self, app, banco, janelas, mensagens, dialogos, monkeypatch):
        janela = janelas()
        preencher_e_salvar(app, janela)
        entrar_como(app, monkeypatch, "operador2")
        definir(app, janela.conferencias.adicionar_nova("manual")["nome"], "Joao da Manutencao")
        janela.salvar()
        assert janela.status == EM_ANALISE and "Os dados gerais já não podem ser alterados" in mensagens.infos[-1][1]
        assert estado(janela.btn_editar) == "disabled" and estado(janela.btn_gerar) == "normal"
        janela.editar()                                                                              # (sem efeito)
        assert janela.salvo and travado(janela.periodo["p0"]["data_inicio"])
        assert estado(janela.conferencias.btn_sistema) == "normal"
        janela.conferencias.adicionar_nova("sistema")
        janela.salvar()
        assert janela.status == APROVADO

    def test_digitar_o_nome_da_conferencia_habilita_o_salvar(self, app, banco, janelas, mensagens, dialogos, monkeypatch):
        janela = janelas()
        preencher_e_salvar(app, janela)
        entrar_como(app, monkeypatch, "operador2")
        linha = janela.conferencias.adicionar_nova("manual")
        janela.conferencias.linhas[0]["nome"].delete(0, "end")
        janela._atualizar_estado()
        assert estado(janela.btn_salvar) == "normal"
        janela.salvar()
        assert "Conferido por" in mensagens.avisos[-1][1]                                           # o nome é obrigatório
        assert linha["registrada"] is False

    def test_reabrir_a_sm_aprovada_antes_de_gerar(self, app, banco, janelas, fluxo):
        sm_id = fluxo.salvar()
        fluxo.aprovar(sm_id)
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        assert janela.status == APROVADO and not janela.emitido and len(janela.conferencias.linhas) == 2
        assert estado(janela.btn_gerar) == "normal" and estado(janela.btn_editar) == "disabled"
        assert "documento ainda não gerado" in janela.lbl_status.cget("text")
        assert not travado(janela.ent_exec_lib_local) and travado(janela.ent_exec_nor_local)        # liberação aberta, normalização ainda não
        assert not travado(janela.tab_lib.linhas[0]["data"]) and travado(janela.tab_nor.linhas[0]["data"])

    def test_dica_dos_botoes_explica_quando_ficam_inativos(self, app, banco, janelas):
        from test_sm_avulso_interface import _todos_os_widgets
        textos = [w.cget("text") for w in _todos_os_widgets(janelas().janela) if w.winfo_class() == "Label"]
        assert any("Pode ser registrada já com a SM salva (Em análise), antes de gerar o documento" in t for t in textos)


# ======================================================================================================================
# a mesma pessoa não confere a SM duas vezes (Conferência Operação)
# ======================================================================================================================
MENSAGEM = "já efetuou a conferência deste documento"


class TestMesmaPessoaNaoConfereDuasVezes:
    @pytest.mark.parametrize("status", [EM_ANALISE, AGUARDA, APROVADO])
    def test_segunda_conferencia_operacao_da_mesma_pessoa_e_recusada_em_qualquer_status(self, app, fluxo, status):
        sm_id = fluxo.salvar() if status == EM_ANALISE else fluxo.ate(status)
        if status != APROVADO:
            fluxo.conferir(sm_id, fluxo.conferencia_sistema())                                       # operador2 confere pela Operação
        quantas = len(fluxo.doc(sm_id)["conferencias"])
        with pytest.raises(app.DocLibRegra, match=MENSAGEM) as erro:
            fluxo.conferir(sm_id, fluxo.conferencia_sistema(nome="Outro nome digitado"))             # a mesma pessoa de novo
        assert "Você (operador2)" in str(erro.value) and "não pode conferir a SM novamente" in str(erro.value)
        assert len(fluxo.doc(sm_id)["conferencias"]) == quantas

    def test_outra_pessoa_pode_conferir_pela_operacao(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)                                                                  # operador2 já conferiu
        fluxo.conferir(sm_id, fluxo.conferencia_sistema(), usuario="operador3")
        fluxo.conferir(sm_id, fluxo.conferencia_sistema(), usuario="Operador4")
        assert [c["ass"] for c in fluxo.doc(sm_id)["conferencias"] if c["modalidade"] == "sistema"] == ["operador2", "operador3", "Operador4"]

    def test_comparacao_ignora_maiusculas_e_espacos_do_login(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.conferir(sm_id, fluxo.conferencia_sistema(), usuario="Operador2")
        with pytest.raises(app.DocLibRegra, match=MENSAGEM):
            fluxo.conferir(sm_id, fluxo.conferencia_sistema(), usuario="OPERADOR2")

    def test_duas_conferencias_operacao_da_mesma_pessoa_na_mesma_gravacao_sao_recusadas(self, app, fluxo):
        sm_id = fluxo.salvar()
        with pytest.raises(app.DocLibRegra, match=MENSAGEM):
            fluxo.conferir(sm_id, fluxo.conferencia_sistema(), fluxo.conferencia_sistema())
        assert fluxo.doc(sm_id)["conferencias"] == []

    def test_a_conferencia_manutencao_pode_repetir_o_nome(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.conferir(sm_id, fluxo.conferencia_manual(), fluxo.conferencia_manual())
        assert len(fluxo.doc(sm_id)["conferencias"]) == 2

    def test_quem_fez_a_operacao_pode_fazer_a_manutencao_da_mesma_sm(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.conferir(sm_id, fluxo.conferencia_sistema(), fluxo.conferencia_manual())
        assert fluxo.doc(sm_id)["status"] == APROVADO

    def test_banco_recusa_a_repeticao_mas_aceita_banco_antigo_com_repeticoes(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.conferir(sm_id, fluxo.conferencia_sistema())                                           # operador2
        sql = ("INSERT INTO doclib_sm_conferencias (sm_id, ordem, modalidade, nome, area, data, ass, registrado_por, registrado_em) "
               "VALUES (?, 5, 'sistema', 'x', 'y', '25/10/2026', ?, 'op', 'agora')")
        conexao = app.doc_lib_conectar(manual=True)
        with pytest.raises(sqlite3.DatabaseError, match="já efetuou a Conferência Operação"):
            conexao.execute(sql, (sm_id, " OPERADOR2 "))
        conexao.execute(sql, (sm_id, "operador9"))                                                   # outra pessoa: aceita
        # banco de quem já tinha repetições gravadas antes da regra: o gatilho some, as repetições entram e a preparação do banco passa
        conexao.execute("DROP TRIGGER trg_doclib_sm_conferencia_repetida")
        conexao.execute(sql.replace(", 5,", ", 6,"), (sm_id, "operador2"))
        conexao.close()
        app.garantir_banco_doc_lib()                                                                 # não falha com repetições antigas
        conexao = app.doc_lib_conectar()
        assert conexao.execute("SELECT COUNT(*) FROM doclib_sm_conferencias WHERE sm_id = ? AND ass = 'operador2'", (sm_id,)).fetchone()[0] == 2
        conexao.close()


class TestJanelaMesmaPessoaNaoConfereDuasVezes:
    def test_botao_operacao_avisa_quando_a_pessoa_logada_ja_conferiu(self, app, banco, janelas, fluxo, mensagens, monkeypatch):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(APROVADO)))                                   # operador2 já conferiu
        entrar_como(app, monkeypatch, "operador2")
        conferencias = janela.conferencias
        antes = len(conferencias.linhas)
        assert conferencias.adicionar_nova("sistema") is None
        titulo, texto = mensagens.avisos[-1]
        assert titulo == "Conferência Operação" and "Você (operador2) já efetuou a conferência deste documento" in texto
        assert len(conferencias.linhas) == antes and not janela._pendente()
        assert conferencias.adicionar_nova("manual") is not None                                    # a Manutenção segue liberada
        entrar_como(app, monkeypatch, "operador3")
        assert conferencias.adicionar_nova("sistema") is not None

    def test_clicar_duas_vezes_antes_de_salvar_tambem_avisa(self, app, banco, janelas, mensagens, dialogos, monkeypatch):
        janela = janelas()
        preencher_e_salvar(app, janela)
        entrar_como(app, monkeypatch, "operador2")
        assert janela.conferencias.adicionar_nova("sistema") is not None                             # linha ainda não salva
        assert janela.conferencias.adicionar_nova("sistema") is None
        assert MENSAGEM in mensagens.avisos[-1][1] and len(janela.conferencias.linhas) == 1

    def test_o_botao_tambem_avisa_com_a_sm_em_aguarda_conferencia(self, app, banco, janelas, fluxo, mensagens, monkeypatch):
        sm_id = fluxo.ate(AGUARDA)
        fluxo.conferir(sm_id, fluxo.conferencia_sistema())                                           # operador2
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        entrar_como(app, monkeypatch, "operador2")
        assert janela.conferencias.adicionar_nova("sistema") is None and MENSAGEM in mensagens.avisos[-1][1]

    def test_gravacao_com_a_mesma_pessoa_mostra_a_regra(self, app, banco, janelas, fluxo, mensagens, monkeypatch):
        sm_id = fluxo.ate(APROVADO)
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        entrar_como(app, monkeypatch, "operador2")
        doc = fluxo.doc(sm_id)
        # (força a linha, como um defeito da tela faria, para provar que a gravação também recusa)
        janela.conferencias.adicionar_linha("sistema", {"nome": "operador2", "area": "COG", "data": "29/10/2026", "ass": "operador2"},
                                            registrada=False)
        janela._atualizar_estado()
        janela.salvar()
        assert MENSAGEM in mensagens.avisos[-1][1] and len(fluxo.doc(sm_id)["conferencias"]) == len(doc["conferencias"])
