"""Regressão do Doc_Lib. (Click_25): ATEIE, AI e MO continuam funcionando depois da inclusão da SM Avulso.

Cada documento é percorrido pelas mesmas funções do aplicativo (salvar, gerar o PDF, De acordo, reserva, cancelamento, GRID e
janela). A SM compartilha com eles o banco, a tabela de numeração (por tipo) e o GRID; aqui se confere que nada disso mudou."""
import pytest

pymupdf = pytest.importorskip("pymupdf")


def carga_ateie(app, **extras):
    dados = {"id": None, "revisao": None, "classificacao": "Programado", "equipamento": "LT 230 kV TESTE",
             "empresa": "FOZ DO RIO CLARO ENERGIA SA", "empresa_outra": "", "local": "SE MCP", "servicos": "Inspeção geral",
             "observacoes": app.DOC_LIB_TEXTO_PADRAO_OBSERVACOES, "documentos_vinculados": "", "nota": "",
             "solicitado_por": "Operador Um", "solicitado_por_usuario": "operador1", "data_preenchimento": "24/10/2026",
             "hora_preenchimento": "10:00", "notificacoes": [],
             "pessoal": [{"nome": "Fulano", "empresa": "AXIA", "empresa_outra": "", "setor": "Operação", "data": "24/10/2026",
                          "hora": "10:00"}],
             "intervencoes": [{"ordem": 1, "prev_data_inicio": "25/10/26", "prev_hora_inicio": "08:00",
                               "prev_data_termino": "25/10/26", "prev_hora_termino": "17:00"}]}
    dados.update(extras)
    return dados


def carga_ai(app, **extras):
    dados = {"id": None, "revisao": None, "empresa": "FOZ DO RIO CLARO ENERGIA SA", "empresa_outra": "",
             "classificacao": "Programado", "equipamento": "TR 1", "local": "SE MCP", "tempo_manobras": "01:00",
             "disponivel_em": "Indisponível", "condicoes": "Equipamento desenergizado", "servicos": "Troca de bucha",
             "observacoes": "", "documentos_vinculados": "", "nota": "", "solicitado_por": "Operador Um",
             "solicitado_por_usuario": "operador1", "data_preenchimento": "24/10/2026", "hora_preenchimento": "10:00",
             "notificacoes": [],
             "pessoal": [{"nome": "Fulano", "setor": "Operação", "empresa": "AXIA", "empresa_outra": "", "data": "24/10/2026",
                          "hora": "10:00"}],
             "intervencoes": [{"ordem": 1, "prev_data_inicio": "25/10/26", "prev_hora_inicio": "08:00",
                               "prev_data_termino": "25/10/26", "prev_hora_termino": "17:00"}]}
    dados.update(extras)
    return dados


def carga_mo(app, **extras):
    dados = {"id": None, "revisao": None, "data_envio": "24/10/26", "classificacao": "Programado",
             "emitente_empresa": "FOZ DO RIO CLARO ENERGIA SA", "emitente_empresa_outra": "", "emitente_orgao": "Operação",
             "emitente_nome": "Operador Um", "destinatario_empresa": "AXIA", "destinatario_empresa_outra": "",
             "destinatario_orgao": "Operação", "destinatario_nome": "Fulano", "recebido_nome": "Beltrano",
             "recebido_data": "24/10/2026", "recebido_hora": "10:00", "assunto": "TESTE DE MO", "descricao": "Texto da MO.",
             "observacoes": "", "informativa": 0, "de_acordo_nome": "", "de_acordo_data": "", "de_acordo_hora": "",
             "prev_data_inicio": "25/10/26", "prev_hora_inicio": "08:00", "prev_data_termino": "25/10/26",
             "prev_hora_termino": "17:00"}
    dados.update(extras)
    return dados


def numero_de(app, tabela, doc_id):
    conexao = app.doc_lib_conectar()
    try:
        if tabela == "doclib_mo":
            return conexao.execute("SELECT numero FROM doclib_mo WHERE id = ?", (doc_id,)).fetchone()[0]
        coluna_id = "ateie_id" if tabela == "doclib_ateie_intervencoes" else "ai_id"
        return conexao.execute(f"SELECT numero FROM {tabela} WHERE {coluna_id} = ?", (doc_id,)).fetchone()[0]
    finally:
        conexao.close()


class TestAteie:
    def test_salvar_gerar_e_aguardar_de_acordo(self, app, banco):
        dados = carga_ateie(app)
        assert app.doc_lib_validar_ateie(app.doc_lib_normalizar_ateie(dados)) == []
        ateie_id = app.doc_lib_salvar_ateie(dados, "operador1")
        doc = app.doc_lib_carregar_ateie(ateie_id)
        assert doc["intervencoes"][0]["numero"] == "0001/26" and doc["intervencoes"][0]["status"] == "Em análise"
        caminho, _ = app.doc_lib_arquivar_pdf_ateie(doc, "operador1")
        assert "ATEIE" in pymupdf.open(caminho)[0].get_text()
        doc = app.doc_lib_carregar_ateie(ateie_id)
        assert doc["emitido"] == 1 and doc["intervencoes"][0]["status"] == "Aguarda De Acordo"

    def test_reserva_e_listagem(self, app, banco):
        reservados = app.doc_lib_reservar_ateie(2, "operador1", "Operador Um")
        assert [item["numero"] for item in reservados] == ["0001/26", "0002/26"]
        assert [linha["status"] for linha in app.doc_lib_listar_ateie()] == ["Reservado", "Reservado"]


class TestAI:
    def test_salvar_gerar_e_aguardar_de_acordo(self, app, banco):
        dados = carga_ai(app)
        assert app.doc_lib_validar_ai(app.doc_lib_normalizar_ai(dados)) == []
        ai_id = app.doc_lib_salvar_ai(dados, "operador1")
        doc = app.doc_lib_carregar_ai(ai_id)
        assert doc["intervencoes"][0]["numero"] == "0001/26"
        caminho, _ = app.doc_lib_arquivar_pdf_ai(doc, "operador1")
        assert pymupdf.open(caminho).page_count >= 1
        assert app.doc_lib_carregar_ai(ai_id)["intervencoes"][0]["status"] == "Aguarda De Acordo"

    def test_reserva(self, app, banco):
        assert [i["numero"] for i in app.doc_lib_reservar_ai(1, "operador1")] == ["0001/26"]


class TestMO:
    def test_ciclo_salvar_gerar_de_acordo_e_cancelar(self, app, banco):
        dados = carga_mo(app)
        assert app.doc_lib_validar_mo(app.doc_lib_normalizar_mo(dados)) == []
        mo_id = app.doc_lib_salvar_mo(dados, "operador1")
        doc = app.doc_lib_carregar_mo(mo_id)
        assert (doc["numero"], doc["status"]) == ("0001/26", "Em análise")
        caminho, _ = app.doc_lib_arquivar_pdf_mo(doc, "operador1")
        assert "MENSAGEM OPERATIVA" in pymupdf.open(caminho)[0].get_text()
        doc = app.doc_lib_carregar_mo(mo_id)
        assert doc["status"] == "Aguarda De Acordo" and doc["emitido"] == 1
        dados = dict(doc, de_acordo_nome="Sicrano", de_acordo_data="24/10/2026", de_acordo_hora="11:00")
        app.doc_lib_salvar_mo(dados, "operador1")
        assert app.doc_lib_carregar_mo(mo_id)["status"] == "Aprovado para Execução"

    def test_cancelamento_so_antes_da_execucao(self, app, banco):
        mo_id = app.doc_lib_salvar_mo(carga_mo(app), "operador1")
        app.doc_lib_cancelar_mo(mo_id, "operador1", "Teste", app.doc_lib_carregar_mo(mo_id)["revisao"])
        assert app.doc_lib_carregar_mo(mo_id)["status"] == "Cancelado"

    def test_reserva_listagem_e_referencia(self, app, banco):
        reservados = app.doc_lib_reservar_mo(2, "operador1")
        assert [i["numero"] for i in reservados] == ["0001/26", "0002/26"]
        mo_id = app.doc_lib_salvar_mo(carga_mo(app, descricao="Descrição de origem"), "operador1")
        assert app.doc_lib_texto_referencia_mo(app.doc_lib_carregar_mo(mo_id)) == "Descrição de origem"
        assert [linha["status"] for linha in app.doc_lib_listar_mo()] == ["Em análise", "Reservado", "Reservado"]

    def test_botao_mo_referencia_continua_abrindo_nova_mo(self, app, banco, mensagens):
        mo_id = app.doc_lib_salvar_mo(carga_mo(app, descricao="Descrição de origem"), "operador1")
        janela = app.JanelaMO()
        janela._carregar_documento(app.doc_lib_carregar_mo(mo_id))
        criadas = []
        original = app.JanelaMO
        app.JanelaMO = lambda **kw: criadas.append(original(**kw)) or criadas[-1]
        try:
            janela.referencia()
        finally:
            app.JanelaMO = original
        nova = criadas[0]
        try:
            assert nova._texto(nova.txt_descricao) == "Descrição de origem" and nova.numero_previsto == "0002/26"
            assert nova.mo_id is None
        finally:
            nova.janela.destroy()


class TestConvivenciaComAsDemaisJanelas:
    def test_numeracoes_independentes_por_tipo_documento(self, app, banco, fluxo):
        app.doc_lib_salvar_ateie(carga_ateie(app), "operador1")
        app.doc_lib_salvar_ai(carga_ai(app), "operador1")
        app.doc_lib_salvar_mo(carga_mo(app), "operador1")
        fluxo.salvar()
        fluxo.salvar()
        conexao = app.doc_lib_conectar()
        ultimos = dict(conexao.execute("SELECT tipo, ultimo FROM doclib_numeracao WHERE ano = 2026").fetchall())
        conexao.close()
        assert ultimos == {"ATEIE": 1, "AI": 1, "MO": 1, "SM": 2}
        assert app.doc_lib_numeros_previstos(1, "ATEIE") == ["0002/26"]
        assert app.doc_lib_numeros_previstos(1, "MO") == ["0002/26"]
        assert app.doc_lib_numeros_previstos(1, "SM") == ["0003/26"]

    @pytest.mark.parametrize("nome_classe", ["JanelaAteie", "JanelaAI", "JanelaMO", "JanelaSMAvulso"])
    def test_as_quatro_janelas_abrem(self, app, banco, nome_classe):
        janela = getattr(app, nome_classe)()
        app.root.update()
        try:
            assert janela.janela.winfo_exists() and "DOC_LIB" in janela.janela.title()
        finally:
            janela.janela.destroy()

    def test_janela_da_mo_mantem_os_oito_botoes(self, app, banco):
        janela = app.JanelaMO()
        try:
            assert [b.cget("text") for b in (janela.btn_voltar, janela.btn_salvar, janela.btn_editar, janela.btn_gerar,
                                             janela.btn_encaminhar, janela.btn_reservar, janela.btn_cancelar,
                                             janela.btn_referencia)] == \
                ["Voltar", "Salvar", "Editar", "Gerar Documento", "Encaminhar MO", "MO-Reservado", "Cancelar MO", "MO-Referência"]
        finally:
            janela.janela.destroy()

    @pytest.mark.parametrize("comando", ["cmd_click25_ateie", "cmd_click25_ai", "cmd_click25_mo", "cmd_click25_sm_avulso"])
    def test_comandos_do_menu_exigem_login_e_abrem_a_janela(self, app, banco, comando, mensagens, monkeypatch):
        antes = set(app.root.winfo_children())
        monkeypatch.setattr(app, "current_user", None)
        getattr(app, comando)()
        assert mensagens.avisos and "login" in mensagens.avisos[-1][1]
        monkeypatch.setattr(app, "current_user", "operador1 em 24/10/2026 - 10:00h")
        getattr(app, comando)()
        app.root.update()
        novas = [w for w in app.root.winfo_children() if w not in antes and w.winfo_class() == "Toplevel"]
        try:
            assert len(novas) == 1
        finally:
            for w in novas:
                w.destroy()

    def test_garantir_banco_cria_todas_as_tabelas_sem_alterar_as_existentes(self, app, banco):
        app.doc_lib_salvar_mo(carga_mo(app), "operador1")
        antes = app.doc_lib_listar_mo()
        app.garantir_banco_doc_lib()
        assert app.doc_lib_listar_mo() == antes
