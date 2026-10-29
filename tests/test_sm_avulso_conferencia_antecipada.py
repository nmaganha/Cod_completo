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
            fluxo.conferir(sm_id, repetida)                                                          # duas da mesma área: ainda não
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

    def test_horarios_e_executantes_so_depois_de_gerar_o_documento(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        with pytest.raises(app.DocLibBloqueado, match="Data e hora das manobras de liberação"):
            fluxo.alterar(sm_id, liberacao=fluxo.datar(fluxo.doc(sm_id), "liberacao", 8))
        with pytest.raises(app.DocLibBloqueado, match="Executantes da Liberação"):
            fluxo.alterar(sm_id, exec_lib_local="Fulano")
        assert fluxo.doc(sm_id)["status"] == APROVADO

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

    def test_encaminhar_por_e_mail_continua_so_em_aguarda_conferencia(self, app, fluxo):
        sm_id = self.aprovada_sem_emitir(fluxo)
        with pytest.raises(app.DocLibRegra, match="Situação atual: Aprovado para Execução"):
            app.doc_lib_validar_envio_sm(fluxo.doc(sm_id))

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

    def test_registrar_duas_conferencias_aprova_a_sm_antes_de_gerar_o_documento(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_e_salvar(app, janela)
        conferencias = janela.conferencias
        manutencao = conferencias.adicionar_nova("manual")
        assert estado(janela.btn_salvar) == "normal" and estado(janela.btn_editar) == "disabled"       # há conferência por salvar
        definir(app, manutencao["nome"], "Joao da Manutencao")
        conferencias.adicionar_nova("sistema")
        janela.salvar()
        assert not mensagens.avisos and janela.status == APROVADO and not janela.emitido
        texto = mensagens.infos[-1][1]
        assert "Conferência registrada (2 de 10)" in texto and "Gerar SM Avulso" in texto and "só são lançados depois" in texto
        assert estado(janela.btn_editar) == "disabled" and estado(janela.btn_gerar) == "normal"
        assert all(linha["registrada"] for linha in conferencias.linhas)
        assert estado(conferencias.btn_manual) == "normal"                                           # as demais são facultativas
        assert "documento ainda não gerado" in janela.lbl_status.cget("text")
        # dados gerais protegidos; horários e executantes ainda não
        assert all(travado(w) for w in janela.periodo["p0"]["widgets"]) and travado(janela.ent_exec_lib_local)
        assert all(travado(linha["data"]) for linha in janela.tab_lib.linhas)
        assert estado(janela.periodo["p1"]["botao"]) == "normal"                                    # Aprovada: Habilitar disponível
        janela.gerar()
        assert janela.emitido and janela.status == APROVADO and dialogos["gerado"]
        assert not travado(janela.ent_exec_lib_local) and not travado(janela.tab_lib.linhas[0]["data"])
        assert mensagens.perguntas[-1][0] == "Gerar SM Avulso" and "'Aprovado para Execução'" in mensagens.perguntas[-1][1]

    def test_uma_so_conferencia_nao_aprova_e_ja_trava_os_dados_gerais(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_e_salvar(app, janela)
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

    def test_digitar_o_nome_da_conferencia_habilita_o_salvar(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_e_salvar(app, janela)
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
        assert travado(janela.ent_exec_lib_local) and travado(janela.ent_exec_nor_local)

    def test_dica_dos_botoes_explica_quando_ficam_inativos(self, app, banco, janelas):
        from test_sm_avulso_interface import _todos_os_widgets
        textos = [w.cget("text") for w in _todos_os_widgets(janelas().janela) if w.winfo_class() == "Label"]
        assert any("Pode ser registrada já com a SM salva (Em análise), antes de gerar o documento" in t for t in textos)
