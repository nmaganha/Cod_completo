"""SM Avulso (Doc_Lib. - Click_25): quem elabora a SM (item 11) não a confere; GRID SM com o botão NOVA SM."""
import sqlite3

import pytest

from test_sm_avulso_interface import definir, dialogos, estado, janelas, preencher  # noqa: F401

EM_ANALISE, AGUARDA, APROVADO = "Em análise", "Aguarda Conferência", "Aprovado para Execução"
EM_EXECUCAO, CONCLUIDO, CANCELADO, RESERVADO = "Em Execução", "Concluído", "Cancelado", "Reservado"
MENSAGEM = "Esta SM foi elaborada por você (operador1) e, portanto, não é possível que você efetue a conferência da SM."


def entrar_como(app, monkeypatch, login):
    monkeypatch.setattr(app, "current_user", f"{login} em 29/10/2026 - 10:00h")


class TestElaboradorNaoConfere:
    @pytest.mark.parametrize("status", [EM_ANALISE, AGUARDA, APROVADO])
    def test_conferencia_operacao_do_elaborador_e_recusada_com_a_mensagem(self, app, fluxo, status):
        sm_id = fluxo.salvar() if status == EM_ANALISE else fluxo.ate(status)
        quantas = len(fluxo.doc(sm_id)["conferencias"])
        with pytest.raises(app.DocLibRegra) as erro:
            fluxo.conferir(sm_id, fluxo.conferencia_sistema(), usuario="operador1")                  # operador1 elaborou a SM
        assert MENSAGEM in str(erro.value) and "outra pessoa" in str(erro.value)
        assert len(fluxo.doc(sm_id)["conferencias"]) == quantas

    def test_comparacao_do_login_ignora_maiusculas_e_espacos(self, app, fluxo):
        sm_id = fluxo.salvar()
        for login in ("OPERADOR1", " Operador1 "):
            with pytest.raises(app.DocLibRegra, match="foi elaborada por você"):
                fluxo.conferir(sm_id, fluxo.conferencia_sistema(), usuario=login)

    def test_outra_pessoa_confere_normalmente(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.conferir(sm_id, fluxo.conferencia_sistema(), fluxo.conferencia_manual(), usuario="operador2")
        assert fluxo.doc(sm_id)["status"] == APROVADO

    def test_o_elaborador_pode_registrar_a_conferencia_manutencao_de_outra_pessoa(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.conferir(sm_id, fluxo.conferencia_manual(nome="Maria da Manutencao"), usuario="operador1")   # registra o que a Manutenção conferiu
        assert fluxo.doc(sm_id)["conferencias"][0]["nome"] == "Maria da Manutencao"

    @pytest.mark.parametrize("nome", ["operador1", "OPERADOR1", " Operador1 ", "José da Silva", "jose da silva", "JOSÉ  DA SILVA"])
    def test_conferencia_manutencao_com_o_nome_do_elaborador_e_recusada(self, app, fluxo, nome):
        sm_id = fluxo.salvar()
        conexao = app.doc_lib_conectar()
        conexao.execute("UPDATE doclib_sm SET elaborado_por = 'José da Silva' WHERE id = ?", (sm_id,))
        conexao.commit()
        conexao.close()
        with pytest.raises(app.DocLibRegra, match="é o de quem elaborou esta SM") as erro:
            fluxo.conferir(sm_id, fluxo.conferencia_manual(nome=nome))
        assert "não é possível que ele(a) efetue a conferência da SM" in str(erro.value)
        fluxo.conferir(sm_id, fluxo.conferencia_manual(nome="José da Silva Junior"))               # outro nome parecido passa
        assert len(fluxo.doc(sm_id)["conferencias"]) == 1

    def test_o_elaborador_continua_podendo_gerar_executar_e_concluir(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.aprovar(sm_id)                                                                       # conferida por outra pessoa
        fluxo.gerar(sm_id)
        fluxo.executar(sm_id)
        fluxo.concluir(sm_id)
        assert fluxo.doc(sm_id)["status"] == CONCLUIDO

    def test_banco_recusa_a_conferencia_do_elaborador_mas_nao_mexe_nas_antigas(self, app, fluxo):
        sm_id = fluxo.salvar()
        sql = ("INSERT INTO doclib_sm_conferencias (sm_id, ordem, modalidade, nome, area, data, ass, registrado_por, registrado_em) "
               "VALUES (?, ?, ?, ?, 'y', '25/10/2026', ?, 'op', 'agora')")
        conexao = app.doc_lib_conectar(manual=True)
        with pytest.raises(sqlite3.DatabaseError, match="quem elabora a SM não pode efetuar a conferência"):
            conexao.execute(sql, (sm_id, 1, "sistema", "operador1", " OPERADOR1 "))
        with pytest.raises(sqlite3.DatabaseError, match="quem elabora a SM não pode efetuar a conferência"):
            conexao.execute(sql, (sm_id, 1, "manual", " OPERADOR1 ", "via fonia"))
        conexao.execute(sql, (sm_id, 1, "manual", "Maria", "via fonia"))                           # outra pessoa: aceita
        conexao.execute("DROP TRIGGER trg_doclib_sm_conferencia_elaborador")                       # banco de antes da regra
        conexao.execute(sql, (sm_id, 2, "sistema", "operador1", "operador1"))
        conexao.close()
        app.garantir_banco_doc_lib()                                                               # a conferência antiga não impede nada
        fluxo.conferir(sm_id, fluxo.conferencia_manual(nome="Pedro"))
        assert len(fluxo.doc(sm_id)["conferencias"]) == 3


class TestJanelaElaboradorNaoConfere:
    def test_botao_operacao_avisa_o_elaborador_e_nao_inclui_a_linha(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        janela.salvar()                                                                            # operador1 elabora e segue logado
        antes = len(janela.conferencias.linhas)
        assert janela.conferencias.adicionar_nova("sistema") is None
        titulo, texto = mensagens.avisos[-1]
        assert titulo == "Conferência Operação" and MENSAGEM in texto
        assert len(janela.conferencias.linhas) == antes and not janela._pendente()

    def test_outra_pessoa_logada_confere_a_sm_elaborada_por_operador1(self, app, banco, janelas, mensagens, dialogos, monkeypatch):
        janela = janelas()
        preencher(app, janela)
        janela.salvar()
        entrar_como(app, monkeypatch, "operador2")
        linha = janela.conferencias.adicionar_nova("sistema")
        assert linha is not None and linha["ass"].get() == "operador2"

    def test_manutencao_com_o_nome_do_elaborador_e_recusada_ao_salvar(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        janela.salvar()
        linha = janela.conferencias.adicionar_nova("manual")
        definir(app, linha["nome"], "operador1")
        janela.salvar()
        titulo, texto = mensagens.avisos[-1]
        assert titulo == "Regra da SM" and "é o de quem elaborou esta SM" in texto
        assert janela.status == EM_ANALISE and app.doc_lib_carregar_sm(janela.sm_id)["conferencias"] == []

    def test_elaborador_registra_a_manutencao_de_outra_pessoa(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        janela.salvar()
        definir(app, janela.conferencias.adicionar_nova("manual")["nome"], "Maria da Manutencao")
        janela.salvar()
        assert not [a for a in mensagens.avisos if a[0] == "Regra da SM"]
        assert [c["nome"] for c in app.doc_lib_carregar_sm(janela.sm_id)["conferencias"]] == ["Maria da Manutencao"]

    def test_o_aviso_vale_tambem_para_a_sm_reaberta_com_a_sm_aprovada(self, app, banco, janelas, fluxo, mensagens):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(APROVADO)))
        assert janela.conferencias.adicionar_nova("sistema") is None and MENSAGEM in mensagens.avisos[-1][1]


class TestGridSmNovaSm:
    def test_botao_nova_sm_existe_no_grid_sm_como_nos_demais_documentos(self, app, banco, janelas):
        janela = janelas()
        grid = app.JanelaListaSM(janela.janela)
        outros = [app.JanelaListaAteie(janela.janela), app.JanelaListaMO(janela.janela)]
        app.root.update()
        try:
            textos = lambda g: [w.cget("text") for w in g.janela.winfo_children() if w.winfo_class() == "Button"]
            assert "NOVA SM" in textos(grid) and "NOVA ATEIE" in textos(outros[0]) and "NOVA MO" in textos(outros[1])
            assert textos(grid)[:2] == ["Abrir", "NOVA SM"]                                       # na mesma posição dos demais
        finally:
            for g in [grid] + outros:
                g.janela.destroy()

    def test_nova_sm_abre_a_tela_inicial_de_emissao_no_lugar_da_janela_atual(self, app, banco, janelas, fluxo, mensagens):
        fluxo.ate(AGUARDA)
        janela = janelas()
        janela._carregar_documento(fluxo.doc(1))
        janelas_sm = lambda: [w for w in app.root.winfo_children() if w.winfo_class() == "Toplevel" and w.title() == "COG - DOC_LIB. - SM AVULSO"]
        antes = set(janelas_sm())
        grid = app.JanelaListaSM(janela.janela)
        app.root.update()
        botao = next(w for w in grid.janela.winfo_children() if w.winfo_class() == "Button" and w.cget("text") == "NOVA SM")
        botao.invoke()
        app.root.update()
        novas = set(janelas_sm()) - antes
        try:
            assert len(novas) == 1 and not janela.janela.winfo_exists()                           # a nova substitui a que estava aberta
            assert not grid.janela.winfo_exists()
        finally:
            for w in novas:
                w.destroy()
