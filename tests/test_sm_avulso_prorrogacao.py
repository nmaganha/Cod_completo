"""SM Avulso (Doc_Lib. - Click_25): botão Prorrogar (término do período em vigor, P1, P2...), no banco, na janela e no PDF."""
import sqlite3

import pytest

from test_sm_avulso_interface import definir, dialogos, estado, janelas, travado  # noqa: F401  (fixtures e atalhos da janela da SM)

pymupdf = pytest.importorskip("pymupdf")

EM_ANALISE, AGUARDA, APROVADO = "Em análise", "Aguarda Conferência", "Aprovado para Execução"
EM_EXECUCAO, CONCLUIDO, CANCELADO, RESERVADO = "Em Execução", "Concluído", "Cancelado", "Reservado"

REPROGRAMACAO_1 = dict(p1_data_inicio="27/10/2026", p1_hora_inicio="08:00", p1_data_termino="27/10/2026", p1_hora_termino="17:00",
                       reprogramacoes=1)


def outro_usuario_salva(fluxo, sm_id):
    """Grava uma alteração qualquer (data e hora da primeira manobra de normalização), como outro usuário faria."""
    normalizacao = fluxo.doc(sm_id)["normalizacao"]
    fluxo.alterar(sm_id, normalizacao=[dict(normalizacao[0], data="25/10/2026", hora="17:00")] + normalizacao[1:])


def ate_em_execucao_reprogramada(fluxo):
    """SM que foi reprogramada ainda Aprovada para Execução (Reprogramação-1 em vigor, 27/10/2026 08:00 a 17:00) e já está Em Execução."""
    sm_id = fluxo.ate(APROVADO)
    fluxo.alterar(sm_id, **REPROGRAMACAO_1)
    liberacao = [dict(m, data="27/10/2026", hora=f"08:{i * 10:02d}") for i, m in enumerate(fluxo.doc(sm_id)["liberacao"])]
    fluxo.alterar(sm_id, liberacao=liberacao, exec_lib_local="Fulano (campo)")
    assert fluxo.doc(sm_id)["status"] == EM_EXECUCAO
    return sm_id


def prorrogar(app, fluxo, sm_id, data, hora, usuario="operador1"):
    return app.doc_lib_prorrogar_sm(sm_id, data, hora, usuario, fluxo.doc(sm_id)["revisao"])


class TestProrrogacaoNoBanco:
    def test_substitui_o_termino_registra_p1_e_muda_a_revisao(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        antes = fluxo.doc(sm_id)
        resultado = prorrogar(app, fluxo, sm_id, "25/10/2026", "19:30")
        depois = fluxo.doc(sm_id)
        assert resultado == {"periodo": "p0", "numero": 1, "termino": "25/10/2026 19:30", "revisao": antes["revisao"] + 1}
        assert (depois["p0_data_termino"], depois["p0_hora_termino"]) == ("25/10/2026", "19:30")
        assert (depois["p0_data_inicio"], depois["p0_hora_inicio"]) == ("25/10/2026", "08:00")           # o início não muda
        assert depois["status"] == EM_EXECUCAO and depois["revisao"] == antes["revisao"] + 1
        assert depois["p0_prorrogacoes"] == 1 and depois["p1_prorrogacoes"] == 0
        registro = depois["prorrogacoes"][0]
        assert (registro["periodo"], registro["numero"], registro["termino_anterior_data"], registro["termino_anterior_hora"],
                registro["termino_data"], registro["termino_hora"], registro["prorrogado_por"]) == \
               ("p0", 1, "25/10/2026", "17:00", "25/10/2026", "19:30", "operador1")
        conexao = app.doc_lib_conectar()
        historico = conexao.execute("SELECT descricao, usuario FROM doclib_sm_historico WHERE evento = 'prorrogacao'").fetchall()
        conexao.close()
        assert historico == [("Programação prorrogada (P1): término de 25/10/2026 17:00 para 25/10/2026 19:30", "operador1")]

    def test_prorrogacoes_sucessivas_viram_p2_p3_p4_p5(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        for numero, hora in enumerate(("18:00", "19:00", "20:00", "21:00", "22:00"), start=1):
            assert prorrogar(app, fluxo, sm_id, "25/10/2026", hora)["numero"] == numero
        doc = fluxo.doc(sm_id)
        assert doc["p0_prorrogacoes"] == 5 and [p["numero"] for p in doc["prorrogacoes"]] == [1, 2, 3, 4, 5]
        assert doc["p0_hora_termino"] == "22:00" and doc["prorrogacoes"][4]["termino_anterior_hora"] == "21:00"

    def test_aceita_data_e_hora_em_formatos_curtos_e_vira_o_dia(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        prorrogar(app, fluxo, sm_id, "26/10/26", "1:30")
        doc = fluxo.doc(sm_id)
        assert (doc["p0_data_termino"], doc["p0_hora_termino"]) == ("26/10/2026", "01:30")

    @pytest.mark.parametrize("data, hora", [("25/10/2026", "17:00"), ("25/10/2026", "16:59"), ("24/10/2026", "23:00")])
    def test_novo_termino_precisa_ser_posterior_ao_atual(self, app, fluxo, data, hora):
        sm_id = fluxo.ate(EM_EXECUCAO)
        with pytest.raises(app.DocLibRegra, match=r"precisa ser posterior ao término em vigor \(25/10/2026 17:00\)"):
            prorrogar(app, fluxo, sm_id, data, hora)
        assert fluxo.doc(sm_id)["p0_prorrogacoes"] == 0 and fluxo.doc(sm_id)["p0_hora_termino"] == "17:00"

    @pytest.mark.parametrize("data, hora, mensagem", [("", "18:00", "nova data"), ("32/13/2026", "18:00", "nova data"),
                                                      ("25/10/2026", "", "nova hora"), ("25/10/2026", "25:99", "nova hora")])
    def test_data_ou_hora_invalida(self, app, fluxo, data, hora, mensagem):
        sm_id = fluxo.ate(EM_EXECUCAO)
        with pytest.raises(app.DocLibRegra, match=mensagem):
            prorrogar(app, fluxo, sm_id, data, hora)

    @pytest.mark.parametrize("status", [EM_ANALISE, AGUARDA, APROVADO, CONCLUIDO])
    def test_so_com_a_sm_em_execucao(self, app, fluxo, status):
        sm_id = fluxo.ate(status)
        with pytest.raises(app.DocLibRegra, match=f"Situação atual: {status}"):
            prorrogar(app, fluxo, sm_id, "26/10/2026", "18:00")
        assert fluxo.doc(sm_id)["prorrogacoes"] == []

    def test_cancelada_e_reservada_nao_prorrogam(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        app.doc_lib_cancelar_sm(sm_id, "operador1", "Cancelada", fluxo.doc(sm_id)["revisao"])
        with pytest.raises(app.DocLibRegra, match="Situação atual: Cancelado"):
            prorrogar(app, fluxo, sm_id, "26/10/2026", "18:00")
        reservada = app.doc_lib_reservar_sm(1, "operador1")[0]["ateie_id"]
        with pytest.raises(app.DocLibRegra, match="Reservado"):
            prorrogar(app, fluxo, reservada, "26/10/2026", "18:00")

    def test_revisao_desatualizada_e_conflito_e_sm_inexistente(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        revisao = fluxo.doc(sm_id)["revisao"]
        outro_usuario_salva(fluxo, sm_id)                                               # outro usuário salvou antes
        with pytest.raises(app.DocLibConflito):
            app.doc_lib_prorrogar_sm(sm_id, "25/10/2026", "19:00", "operador1", revisao)
        with pytest.raises(app.DocLibConflito):
            app.doc_lib_prorrogar_sm(999, "25/10/2026", "19:00", "operador1", 1)

    def test_prorrogacao_e_gravacao_simultanea_nao_se_atropelam(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        aberta = fluxo.doc(sm_id)                                                        # duas telas abertas na mesma revisão
        app.doc_lib_prorrogar_sm(sm_id, "25/10/2026", "18:00", "operador1", aberta["revisao"])
        with pytest.raises(app.DocLibConflito):                                          # a segunda grava sobre a revisão antiga
            app.doc_lib_prorrogar_sm(sm_id, "25/10/2026", "19:00", "operador2", aberta["revisao"])
        with pytest.raises(app.DocLibConflito):
            fluxo.app.doc_lib_salvar_sm(dict(aberta, exec_nor_local="Fulano", exec_nor_remoto="Sicrano"), "operador1")
        assert fluxo.doc(sm_id)["p0_hora_termino"] == "18:00" and fluxo.doc(sm_id)["p0_prorrogacoes"] == 1

    def test_registro_da_prorrogacao_nao_aceita_alteracao_nem_exclusao(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        prorrogar(app, fluxo, sm_id, "25/10/2026", "18:00")
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.DatabaseError, match="não pode ser alterada"):
            conexao.execute("UPDATE doclib_sm_prorrogacoes SET termino_hora = '23:59'")
        with pytest.raises(sqlite3.DatabaseError, match="não pode ser excluída"):
            conexao.execute("DELETE FROM doclib_sm_prorrogacoes")
        with pytest.raises(sqlite3.IntegrityError):                                       # nº do período é único por SM
            conexao.execute("INSERT INTO doclib_sm_prorrogacoes (sm_id, periodo, numero, termino_anterior_data, termino_anterior_hora, "
                            "termino_data, termino_hora) VALUES (?, 'p0', 1, 'a', 'b', 'c', 'd')", (sm_id,))
        conexao.close()

    def test_depois_de_prorrogar_a_sm_continua_a_ser_salva_e_concluida(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        prorrogar(app, fluxo, sm_id, "25/10/2026", "19:30")
        fluxo.concluir(sm_id)                                                             # o término novo vem junto e é aceito
        doc = fluxo.doc(sm_id)
        assert doc["status"] == CONCLUIDO and doc["p0_hora_termino"] == "19:30" and doc["p0_prorrogacoes"] == 1
        with pytest.raises(app.DocLibRegra):
            prorrogar(app, fluxo, sm_id, "26/10/2026", "10:00")                           # concluída não prorroga

    def test_grid_mostra_o_termino_vigente(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        prorrogar(app, fluxo, sm_id, "26/10/2026", "03:00")
        registro = next(r for r in app.doc_lib_listar_sm() if r["ateie_id"] == sm_id)
        assert registro["prog_termino"] == "26/10/2026 03:00"

    def test_banco_antigo_recebe_a_tabela_das_prorrogacoes(self, app, fluxo, banco):
        sm_id = fluxo.ate(EM_EXECUCAO)
        conexao = app.doc_lib_conectar(manual=True)
        conexao.execute("DROP TRIGGER trg_doclib_sm_prorrogacoes_altera")
        conexao.execute("DROP TRIGGER trg_doclib_sm_prorrogacoes_exclui")
        conexao.execute("DROP TABLE doclib_sm_prorrogacoes")
        conexao.close()
        app.garantir_banco_doc_lib()
        assert fluxo.doc(sm_id)["prorrogacoes"] == [] and fluxo.doc(sm_id)["p0_prorrogacoes"] == 0
        assert prorrogar(app, fluxo, sm_id, "25/10/2026", "18:00")["numero"] == 1


class TestPeriodoEmVigorEReprogramacao:
    def test_reprogramada_a_prorrogacao_vale_para_a_reprogramacao_em_vigor(self, app, fluxo):
        sm_id = ate_em_execucao_reprogramada(fluxo)
        antes = fluxo.doc(sm_id)
        resultado = prorrogar(app, fluxo, sm_id, "27/10/2026", "19:00")
        resultado2 = prorrogar(app, fluxo, sm_id, "27/10/2026", "20:00")
        doc = fluxo.doc(sm_id)
        assert (resultado["periodo"], resultado["numero"], resultado2["numero"]) == ("p1", 1, 2)
        assert (doc["p0_prorrogacoes"], doc["p1_prorrogacoes"]) == (0, 2)
        assert (doc["p0_hora_termino"], doc["p0_data_termino"]) == (antes["p0_hora_termino"], antes["p0_data_termino"])
        assert (doc["p1_hora_termino"], doc["p1_data_termino"]) == ("20:00", "27/10/2026")
        assert [(p["periodo"], p["numero"]) for p in doc["prorrogacoes"]] == [("p1", 1), ("p1", 2)]
        registro = next(r for r in app.doc_lib_listar_sm() if r["ateie_id"] == sm_id)
        assert registro["prog_termino"] == "27/10/2026 20:00"

    def test_reprogramacao_habilitada_e_vazia_nao_impede_prorrogar_o_periodo_em_vigor(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        fluxo.alterar(sm_id, reprogramacoes=1)                                             # habilitada, sem datas
        fluxo.executar(sm_id)
        assert fluxo.doc(sm_id)["status"] == EM_EXECUCAO
        assert prorrogar(app, fluxo, sm_id, "25/10/2026", "18:00")["periodo"] == "p0"       # com a SM Em Execução ela não é mais preenchida

    def test_periodo_salvo_so_muda_pela_prorrogacao_com_a_sm_em_execucao(self, app, fluxo):
        sm_id = ate_em_execucao_reprogramada(fluxo)
        with pytest.raises(app.DocLibBloqueado, match="Reprogramação-1 já registrada.*botão Prorrogar"):
            fluxo.alterar(sm_id, p1_hora_termino="23:00")                                  # editar o término salvo direto: não
        with pytest.raises(app.DocLibBloqueado, match="Reprogramação-1 já registrada"):
            fluxo.alterar(sm_id, p1_data_inicio="28/10/2026")
        with pytest.raises(app.DocLibBloqueado):
            fluxo.alterar(sm_id, p0_hora_termino="23:00")                                  # a programação já era protegida
        assert fluxo.doc(sm_id)["p1_hora_termino"] == "17:00"
        prorrogar(app, fluxo, sm_id, "27/10/2026", "23:00")                                # o caminho é o Prorrogar
        assert fluxo.doc(sm_id)["p1_hora_termino"] == "23:00"

    def test_com_a_sm_em_execucao_nao_ha_mais_reprogramacao(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        with pytest.raises(app.DocLibBloqueado, match="Reprogramações"):
            fluxo.alterar(sm_id, **REPROGRAMACAO_1)
        with pytest.raises(app.DocLibBloqueado, match="Reprogramações"):
            fluxo.alterar(sm_id, reprogramacoes=1)
        assert fluxo.doc(sm_id)["reprogramacoes"] == 0 and fluxo.doc(sm_id)["p1_data_inicio"] in (None, "")


def spans(caminho):
    """[(texto, tamanho, caixa)] de todos os trechos de texto do PDF."""
    resultado = []
    for pagina in pymupdf.open(caminho):
        for bloco in pagina.get_text("dict")["blocks"]:
            for linha in bloco.get("lines", []):
                for trecho in linha["spans"]:
                    resultado.append((trecho["text"].strip(), trecho["size"], trecho["bbox"]))
    return resultado


class TestPdfComP:
    def test_p1_aparece_ao_lado_do_novo_termino_em_fonte_menor(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        prorrogar(app, fluxo, sm_id, "26/10/2026", "03:15")
        caminho, _ = fluxo.gerar(sm_id)
        trechos = spans(caminho)
        rotulos = [t for t in trechos if t[0] == "P1"]
        assert len(rotulos) == 1
        rotulo = rotulos[0]
        horas = [t for t in trechos if t[0] == "03:15 hs"]
        data_nova = [t for t in trechos if t[0] == "26/10/2026"]
        assert len(horas) == 1 and len(data_nova) == 1
        hora = horas[0]
        assert rotulo[1] < hora[1]                                                       # fonte menor que a da data e da hora
        assert abs(rotulo[2][1] - hora[2][1]) < 3 and rotulo[2][0] >= hora[2][2] - 0.5       # na mesma linha, à direita da hora
        assert rotulo[2][0] - hora[2][2] < 6.0                                           # e encostado nela
        assert abs(data_nova[0][2][1] - hora[2][1]) < 3                                  # data e hora do término na mesma linha

    def test_o_termo_acompanha_o_numero_da_prorrogacao(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        for numero, hora in enumerate(("18:00", "19:00", "20:00", "21:00"), start=1):
            prorrogar(app, fluxo, sm_id, "25/10/2026", hora)
            caminho, _ = fluxo.gerar(sm_id)
            assert [t[0] for t in spans(caminho) if t[0].startswith("P") and t[0][1:].isdigit()] == [f"P{numero}"]

    def test_sem_prorrogacao_nao_ha_termo_e_o_pdf_continua_igual(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        caminho, _ = fluxo.gerar(sm_id)
        assert not [t for t in spans(caminho) if t[0].startswith("P") and t[0][1:].isdigit()]

    def test_so_o_periodo_prorrogado_leva_o_termo_e_o_numero_acompanha_as_prorrogacoes(self, app, fluxo):
        sm_id = ate_em_execucao_reprogramada(fluxo)                                      # Reprogramação-1 em vigor
        prorrogar(app, fluxo, sm_id, "27/10/2026", "18:00")
        prorrogar(app, fluxo, sm_id, "27/10/2026", "19:00")
        caminho, _ = fluxo.gerar(sm_id)
        trechos = spans(caminho)
        termos = [t for t in trechos if t[0].startswith("P") and t[0][1:].isdigit()]
        assert [t[0] for t in termos] == ["P2"]                                           # a Programação (esquerda) não tem prorrogação
        hora_programacao = next(t for t in trechos if t[0] == "17:00 hs")
        assert termos[0][2][0] > hora_programacao[2][2]                                   # P2 fica à direita, no quadro da Reprogramação-1

    def test_dentro_das_margens_da_pagina(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        for hora in range(18, 24):
            prorrogar(app, fluxo, sm_id, "25/10/2026", f"{hora}:00")
        caminho, _ = fluxo.gerar(sm_id)
        margem = 196.0 * 72 / 25.4 + 1.0
        assert all(t[2][2] <= margem for t in spans(caminho))


@pytest.fixture()
def em_execucao(app, fluxo, janelas):
    """Janela da SM aberta sobre uma SM Em Execução."""
    janela = janelas()
    janela._carregar_documento(fluxo.doc(fluxo.ate(EM_EXECUCAO)))
    return janela


def visivel(botao):
    return bool(botao.winfo_manager())


def botoes_do_quadro(janela, prefixo):
    dados = janela.periodo[prefixo]
    return dados["botao"], dados["botao_prorrogar"]


@pytest.fixture()
def resposta_prorrogar(app, monkeypatch):
    """Substitui a janela do Prorrogar: devolve a data e hora programadas (None = o usuário cancelou)."""
    class Resposta:
        valor = {"data": "25/10/2026", "hora": "19:30"}
        chamadas = []
    registro = Resposta()
    registro.chamadas = []

    def dialogo(parent, dados):
        registro.chamadas.append(dados)
        return registro.valor

    monkeypatch.setattr(app, "doc_lib_dialogo_prorrogar_sm", dialogo)
    return registro


class TestBotaoProrrogarNaJanela:
    def test_programacao_em_vigor_tem_o_prorrogar_e_nenhum_quadro_tem_o_habilitar(self, app, banco, em_execucao):
        janela = em_execucao
        habilitar, prorrogar_p0 = botoes_do_quadro(janela, "p0")
        assert habilitar is None and visivel(prorrogar_p0) and estado(prorrogar_p0) == "normal"
        assert prorrogar_p0.cget("text") == "Prorrogar"
        for prefixo in ("p1", "p2", "p3"):                                                  # Em Execução: não há mais reprogramação
            habilitar, prorrogar_pn = botoes_do_quadro(janela, prefixo)
            assert not visivel(habilitar) and not visivel(prorrogar_pn)

    def test_o_prorrogar_ocupa_o_lugar_do_habilitar_a_cada_reprogramacao(self, app, banco, janelas, fluxo):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(APROVADO)))
        _, p0 = botoes_do_quadro(janela, "p0")
        assert visivel(p0) and estado(p0) == "disabled"                                     # Aprovada: ainda não está em andamento
        janela.habilitar_reprogramacao("p1")                                                # clicar em Habilitar (ainda sem salvar)
        habilitar_p1, prorrogar_p1 = botoes_do_quadro(janela, "p1")
        assert not visivel(p0) and visivel(prorrogar_p1) and not visivel(habilitar_p1)     # trocou de quadro
        assert estado(prorrogar_p1) == "disabled"
        assert visivel(janela.periodo["p2"]["botao"]) and estado(janela.periodo["p2"]["botao"]) == "normal"
        for campo, valor in (("data_inicio", "27/10/2026"), ("hora_inicio", "08:00"), ("data_termino", "27/10/2026"),
                             ("hora_termino", "17:00")):
            definir(app, janela.periodo["p1"][campo], valor)
        janela.salvar()
        assert visivel(prorrogar_p1) and not visivel(botoes_do_quadro(janela, "p0")[1])
        janela.habilitar_reprogramacao("p2")
        assert visivel(botoes_do_quadro(janela, "p2")[1]) and not visivel(prorrogar_p1) and visivel(janela.periodo["p1"]["botao"])
        assert janela.periodo["p1"]["botao"].cget("text") == "Habilitada" and estado(janela.periodo["p1"]["botao"]) == "disabled"

    def test_em_execucao_o_prorrogar_fica_no_quadro_da_reprogramacao_em_vigor_e_fica_ativo(self, app, banco, janelas, fluxo):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(ate_em_execucao_reprogramada(fluxo)))
        _, p0 = botoes_do_quadro(janela, "p0")
        habilitar_p1, prorrogar_p1 = botoes_do_quadro(janela, "p1")
        assert not visivel(p0) and visivel(prorrogar_p1) and estado(prorrogar_p1) == "normal" and not visivel(habilitar_p1)
        assert all(not visivel(janela.periodo[p]["botao"]) for p in ("p1", "p2", "p3"))

    @pytest.mark.parametrize("status, esperado", [(EM_ANALISE, "disabled"), (AGUARDA, "disabled"), (APROVADO, "disabled"),
                                                  (EM_EXECUCAO, "normal"), (CONCLUIDO, "disabled")])
    def test_so_fica_ativo_com_a_sm_em_execucao(self, app, banco, janelas, fluxo, status, esperado):
        janela = janelas()
        assert estado(janela.periodo["p0"]["botao_prorrogar"]) == "disabled" and visivel(janela.periodo["p0"]["botao_prorrogar"])
        janela._carregar_documento(fluxo.doc(fluxo.ate(status)))
        assert estado(janela.periodo["p0"]["botao_prorrogar"]) == esperado

    def test_alteracao_pendente_desativa_o_botao(self, app, banco, em_execucao, resposta_prorrogar, mensagens):
        janela = em_execucao
        definir(app, janela.ent_exec_nor_local, "Fulano")
        janela._atualizar_estado()
        assert estado(janela.periodo["p0"]["botao_prorrogar"]) == "disabled"
        janela.prorrogar()
        assert "Salve as alterações" in mensagens.avisos[-1][1] and resposta_prorrogar.chamadas == []

    def test_prorrogar_grava_mostra_o_novo_termino_e_o_p1(self, app, banco, em_execucao, fluxo, resposta_prorrogar, mensagens):
        janela = em_execucao
        p0 = janela.periodo["p0"]
        assert p0["lbl_prorrogacao"].cget("text") == ""
        janela.prorrogar()
        dados = resposta_prorrogar.chamadas[0]
        assert (dados["nome"], dados["item"], dados["termino"], dados["numero"]) == ("Programação", "2.1", "25/10/2026 17:00", 1)
        assert (p0["data_termino"].get(), p0["hora_termino"].get()) == ("25/10/2026", "19:30")
        assert p0["lbl_prorrogacao"].cget("text") == "P1" and p0["lbl_prorrogacao"].cget("fg") == app.SGA_AZUL
        assert fluxo.doc(janela.sm_id)["p0_prorrogacoes"] == 1 and janela.revisao == fluxo.doc(janela.sm_id)["revisao"]
        titulo, texto = mensagens.infos[-1]
        assert titulo == "Prorrogar SM" and "Programação prorrogada (P1)" in texto and "25/10/2026 19:30 hs" in texto
        assert "Gere o documento novamente" in texto
        assert estado(p0["botao_prorrogar"]) == "normal" and not janela._pendente()                # pode prorrogar de novo
        resposta_prorrogar.valor = {"data": "25/10/2026", "hora": "21:00"}
        janela.prorrogar()
        assert p0["lbl_prorrogacao"].cget("text") == "P2" and resposta_prorrogar.chamadas[1]["numero"] == 2
        assert p0["hora_termino"].get() == "21:00"

    def test_prorrogar_cancelado_nao_grava(self, app, banco, em_execucao, fluxo, resposta_prorrogar, mensagens):
        resposta_prorrogar.valor = None
        em_execucao.prorrogar()
        assert fluxo.doc(em_execucao.sm_id)["prorrogacoes"] == [] and not mensagens.infos
        assert em_execucao.periodo["p0"]["lbl_prorrogacao"].cget("text") == ""

    def test_termino_nao_posterior_volta_como_aviso(self, app, banco, em_execucao, fluxo, resposta_prorrogar, mensagens):
        resposta_prorrogar.valor = {"data": "25/10/2026", "hora": "16:00"}
        em_execucao.prorrogar()
        assert "precisa ser posterior ao término em vigor" in mensagens.avisos[-1][1]
        assert fluxo.doc(em_execucao.sm_id)["p0_hora_termino"] == "17:00"

    def test_sm_alterada_por_outro_usuario_nao_prorroga(self, app, banco, em_execucao, fluxo, resposta_prorrogar, mensagens):
        outro_usuario_salva(fluxo, em_execucao.sm_id)
        em_execucao.prorrogar()
        assert "foi alterada por outro usuário" in mensagens.avisos[-1][1] and resposta_prorrogar.chamadas == []

    def test_periodo_salvo_fica_travado_em_execucao_e_a_programacao_tambem(self, app, banco, janelas, fluxo):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(EM_EXECUCAO)))
        assert all(travado(w) for w in janela.periodo["p0"]["widgets"])
        janela.habilitar_reprogramacao("p1")                                                # sem efeito: não há reprogramação em execução
        assert all(travado(w) for w in janela.periodo["p1"]["widgets"])
        janela._carregar_documento(fluxo.doc(ate_em_execucao_reprogramada(fluxo)))
        assert all(travado(w) for w in janela.periodo["p1"]["widgets"])                      # salva: só muda pelo Prorrogar

    def test_reabrir_mostra_o_p_e_o_botao_no_quadro_certo(self, app, banco, janelas, fluxo, resposta_prorrogar):
        sm_id = ate_em_execucao_reprogramada(fluxo)
        for hora in ("18:00", "19:00", "20:00"):
            prorrogar(app, fluxo, sm_id, "27/10/2026", hora)
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        assert janela.periodo["p1"]["lbl_prorrogacao"].cget("text") == "P3" and janela.periodo["p0"]["lbl_prorrogacao"].cget("text") == ""
        assert janela.periodo["p2"]["lbl_prorrogacao"].cget("text") == "" and visivel(janela.periodo["p1"]["botao_prorrogar"])
        assert not visivel(janela.periodo["p0"]["botao_prorrogar"])

    def test_sm_referencia_nao_herda_prorrogacoes(self, app, banco, janelas, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        prorrogar(app, fluxo, sm_id, "25/10/2026", "18:00")
        nova = janelas()
        nova._aplicar_referencia(app.doc_lib_dados_referencia_sm(fluxo.doc(sm_id)))
        assert nova.periodo["p0"]["lbl_prorrogacao"].cget("text") == "" and nova.periodo["p0"]["data_termino"].get() == ""


class TestJanelaDoProrrogar:
    def dialogo(self, app, janela, **mudancas):
        dados = {"prefixo": "p0", "item": "2.1", "nome": "Programação", "termino": "25/10/2026 17:00", "numero": 1}
        dados.update(mudancas)
        dialogo = app.DialogoProrrogarSM(janela.janela, dados)
        app.root.update()
        return dialogo

    def test_mostra_periodo_termino_atual_e_numero_da_prorrogacao(self, app, banco, em_execucao):
        dialogo = self.dialogo(app, em_execucao, numero=3, nome="Reprogramação-1", item="2.2")
        try:
            textos = [w.cget("text") for w in dialogo.janela.winfo_children()[1].winfo_children() if w.winfo_class() == "Label"]
            assert "2.2  Reprogramação-1" in textos and "25/10/2026 17:00 hs" in textos and "P3" in textos
            assert dialogo.ent_data.get() == "25/10/2026" and dialogo.ent_hora.get() == ""          # a data atual vem sugerida
            assert dialogo.icone.winfo_exists()
        finally:
            dialogo.janela.destroy()

    def test_confirmar_devolve_data_e_hora_normalizadas(self, app, banco, em_execucao):
        dialogo = self.dialogo(app, em_execucao)
        definir(app, dialogo.ent_data, "26/10/26")
        definir(app, dialogo.ent_hora, "930")
        dialogo.confirmar()
        assert dialogo.resultado == {"data": "26/10/2026", "hora": "09:30"}

    def test_saindo_dos_campos_o_formato_padrao_aparece(self, app, banco, em_execucao):
        dialogo = self.dialogo(app, em_execucao)
        try:
            definir(app, dialogo.ent_data, "2610")
            definir(app, dialogo.ent_hora, "1h30")
            dialogo._normalizar(dialogo.ent_data, app.doc_lib_normalizar_data)
            dialogo._normalizar(dialogo.ent_hora, app.doc_lib_normalizar_hora)
            assert dialogo.ent_hora.get() == "01:30"
            assert dialogo.ent_data.get() in ("26/10/2026", "2610")                                   # (só se o formato for reconhecido)
        finally:
            dialogo.janela.destroy()

    @pytest.mark.parametrize("data, hora, trecho", [("", "18:00", "nova data"), ("32/01/2026", "18:00", "nova data"),
                                                    ("25/10/2026", "", "nova hora"), ("25/10/2026", "99:99", "nova hora"),
                                                    ("25/10/2026", "17:00", "posterior ao término atual"),
                                                    ("24/10/2026", "23:59", "posterior ao término atual")])
    def test_recusa_data_hora_invalida_ou_nao_posterior(self, app, banco, em_execucao, mensagens, data, hora, trecho):
        dialogo = self.dialogo(app, em_execucao)
        try:
            definir(app, dialogo.ent_data, data)
            definir(app, dialogo.ent_hora, hora)
            dialogo.confirmar()
            assert dialogo.resultado is None and dialogo.janela.winfo_exists() and trecho in mensagens.avisos[-1][1]
        finally:
            dialogo.janela.destroy()
