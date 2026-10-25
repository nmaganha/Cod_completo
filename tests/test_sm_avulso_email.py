"""SM Avulso (Doc_Lib. - Click_25): Encaminhar SM por e-mail (status Aguarda Conferência), lista de contatos Para e Cc, registro dos
envios, PDF anexado, botão da janela e coluna Enviado e-mail do GRID SM."""
import os
import sqlite3
from datetime import datetime

import pytest

from test_sm_avulso_interface import definir, dialogos, estado, janelas  # noqa: F401  (fixtures e atalhos da janela da SM)

pymupdf = pytest.importorskip("pymupdf")

EM_ANALISE, AGUARDA, APROVADO = "Em análise", "Aguarda Conferência", "Aprovado para Execução"
EM_EXECUCAO, CONCLUIDO, CANCELADO, RESERVADO = "Em Execução", "Concluído", "Cancelado", "Reservado"
HOJE = datetime.now().strftime("%d/%m/%Y")


@pytest.fixture()
def envios(app, monkeypatch):
    """Troca o envio real (SMTP ou Outlook) por um registro das chamadas; envios.falhar = mensagem faz o envio falhar."""
    class Registro:
        chamadas = []
        falhar = None
    registro = Registro()
    registro.chamadas = []

    def enviar(remetente, destinatarios, copias, assunto, corpo, anexo):
        if registro.falhar:
            raise app.DocLibEmailErro(registro.falhar)
        registro.chamadas.append({"remetente": remetente, "para": destinatarios, "cc": copias, "assunto": assunto,
                                  "corpo": corpo, "anexo": anexo})
        return "SMTP"

    monkeypatch.setattr(app, "doc_lib_enviar_email", enviar)
    return registro


def contatos(app):
    return {c["email"]: c for c in app.doc_lib_listar_contatos_sm()}


class TestContatos:
    def test_lista_inicial_criada_com_o_banco(self, app, banco):
        assert set(contatos(app)) == {"nmaganha@alupar.com.br", "jbarros@alupar.com.br"}
        assert all(c["padrao_para"] == 0 and c["padrao_copia"] == 0 for c in contatos(app).values())

    def test_lista_nao_volta_depois_de_excluida(self, app, banco):
        for contato in app.doc_lib_listar_contatos_sm():
            app.doc_lib_remover_contato_sm(contato["id"])
        app.garantir_banco_doc_lib()                                                  # nova preparação do banco
        assert app.doc_lib_listar_contatos_sm() == []

    def test_incluir_contato_novo_com_e_sem_nome(self, app, banco):
        novo = app.doc_lib_incluir_contato_sm("  Maria.Silva@Alupar.com.br ", "  Maria   Silva ", "operador1")
        assert novo["criado"] and novo["email"] == "maria.silva@alupar.com.br" and novo["nome"] == "Maria Silva"
        sem_nome = app.doc_lib_incluir_contato_sm("operacao@alupar.com.br", "", "operador1")
        assert sem_nome["criado"] and sem_nome["nome"] == ""
        lista = contatos(app)
        assert lista["maria.silva@alupar.com.br"]["nome"] == "Maria Silva" and "operacao@alupar.com.br" in lista

    def test_email_repetido_nao_duplica_e_aproveita_o_nome_so_se_faltava(self, app, banco):
        primeiro = app.doc_lib_incluir_contato_sm("ana@alupar.com.br", "", "operador1")
        repetido = app.doc_lib_incluir_contato_sm("ANA@alupar.com.br", "Ana Souza", "operador1")
        assert not repetido["criado"] and repetido["id"] == primeiro["id"]
        assert contatos(app)["ana@alupar.com.br"]["nome"] == "Ana Souza"
        app.doc_lib_incluir_contato_sm("ana@alupar.com.br", "Outro Nome", "operador1")
        assert contatos(app)["ana@alupar.com.br"]["nome"] == "Ana Souza"            # nome existente não é trocado
        assert len([c for c in app.doc_lib_listar_contatos_sm() if c["email"] == "ana@alupar.com.br"]) == 1

    @pytest.mark.parametrize("email", ["", "   ", "sem-arroba", "a@b", "dois@@alupar.com.br", "espaco @alupar.com.br"])
    def test_email_invalido_e_recusado(self, app, banco, email):
        with pytest.raises(app.DocLibRegra):
            app.doc_lib_incluir_contato_sm(email, "", "operador1")

    def test_ordem_alfabetica_pelo_nome_ou_pelo_email(self, app, banco):
        for email, nome in (("z@alupar.com.br", "Ana"), ("a@alupar.com.br", "Zeca"), ("m@alupar.com.br", "")):
            app.doc_lib_incluir_contato_sm(email, nome, "operador1")
        textos = [app.doc_lib_texto_contato_sm(c) for c in app.doc_lib_listar_contatos_sm()]
        assert textos == ["Ana - z@alupar.com.br", "jbarros@alupar.com.br", "m@alupar.com.br", "nmaganha@alupar.com.br",
                          "Zeca - a@alupar.com.br"]

    def test_padroes_da_ultima_escolha(self, app, banco):
        lista = contatos(app)
        para, copia = lista["nmaganha@alupar.com.br"]["id"], lista["jbarros@alupar.com.br"]["id"]
        app.doc_lib_salvar_padroes_contatos_sm([para], [copia])
        atual = contatos(app)
        assert (atual["nmaganha@alupar.com.br"]["padrao_para"], atual["nmaganha@alupar.com.br"]["padrao_copia"]) == (1, 0)
        assert (atual["jbarros@alupar.com.br"]["padrao_para"], atual["jbarros@alupar.com.br"]["padrao_copia"]) == (0, 1)
        app.doc_lib_salvar_padroes_contatos_sm([], [])                                # a nova escolha substitui a anterior
        assert all(c["padrao_para"] == 0 and c["padrao_copia"] == 0 for c in contatos(app).values())

    def test_contato_nao_pode_estar_em_para_e_em_copia(self, app, banco):
        identificador = contatos(app)["nmaganha@alupar.com.br"]["id"]
        with pytest.raises(app.DocLibRegra):
            app.doc_lib_salvar_padroes_contatos_sm([identificador], [identificador])
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.IntegrityError):                                    # e o banco também recusa
            conexao.execute("UPDATE doclib_sm_contatos SET padrao_para = 1, padrao_copia = 1")
        conexao.close()

    def test_enderecos_do_envio(self, app):
        para, copia = app.doc_lib_enderecos_envio_sm(["A@x.com.br", "a@x.com.br", "b@x.com.br"], ["b@x.com.br", "C@x.com.br", ""])
        assert (para, copia) == (["a@x.com.br", "b@x.com.br"], ["c@x.com.br"])         # sem repetição; quem está em Para sai do Cc
        with pytest.raises(app.DocLibRegra, match="pelo menos um destinatário"):
            app.doc_lib_enderecos_envio_sm([], ["c@x.com.br"])
        with pytest.raises(app.DocLibRegra, match="E-mail inválido: ruim"):
            app.doc_lib_enderecos_envio_sm(["a@x.com.br", "ruim"], [])


class TestRegrasDoEnvio:
    @pytest.mark.parametrize("status", [EM_ANALISE, APROVADO, EM_EXECUCAO, CONCLUIDO])
    def test_so_aguarda_conferencia_pode_ser_encaminhada(self, app, fluxo, status):
        sm_id = fluxo.ate(status)
        with pytest.raises(app.DocLibRegra, match=f"Situação atual: {status}"):
            app.doc_lib_validar_envio_sm(fluxo.doc(sm_id))
        with pytest.raises(app.DocLibRegra):
            app.doc_lib_pdf_para_envio_sm(fluxo.doc(sm_id), "operador1")

    def test_reservada_e_cancelada_nao_sao_encaminhadas(self, app, fluxo):
        app.doc_lib_reservar_sm(1, "operador1")
        with pytest.raises(app.DocLibRegra, match="reservada"):
            app.doc_lib_validar_envio_sm(fluxo.doc(1))
        sm_id = fluxo.ate(AGUARDA)
        app.doc_lib_cancelar_sm(sm_id, "operador1", "Cancelada", fluxo.doc(sm_id)["revisao"])
        with pytest.raises(app.DocLibRegra, match="Cancelado"):
            app.doc_lib_validar_envio_sm(fluxo.doc(sm_id))

    def test_aguarda_conferencia_emitida_e_aceita(self, app, fluxo):
        app.doc_lib_validar_envio_sm(fluxo.doc(fluxo.ate(AGUARDA)))


class TestPdfParaEnvio:
    def test_pdf_arquivado_em_sm_enviados_com_o_aviso_de_conferencia(self, app, fluxo, banco):
        sm_id = fluxo.ate(AGUARDA)
        caminho, _ = app.doc_lib_pdf_para_envio_sm(fluxo.doc(sm_id), "operador1")
        assert os.path.isfile(caminho) and os.sep.join(["SM", "Enviados"]) in caminho and caminho.endswith(".pdf")
        texto = " ".join("\n".join(p.get_text() for p in pymupdf.open(caminho)).split())
        assert "COG-0001/26" in texto and "Aguardando a Conferência do documento" in texto
        conexao = app.doc_lib_conectar()
        linhas = conexao.execute("SELECT tipo, revisao_final, caminho FROM doclib_sm_pdfs WHERE tipo = 'envio'").fetchall()
        conexao.close()
        assert linhas == [("envio", fluxo.doc(sm_id)["revisao"], caminho)]

    def test_reaproveita_o_pdf_enquanto_o_documento_nao_muda_e_gera_outro_depois(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        primeiro, _ = app.doc_lib_pdf_para_envio_sm(fluxo.doc(sm_id), "operador1")
        igual, _ = app.doc_lib_pdf_para_envio_sm(fluxo.doc(sm_id), "operador1")
        assert igual == primeiro
        fluxo.alterar(sm_id, p1_data_inicio="26/10/2026", p1_hora_inicio="08:00", p1_data_termino="26/10/2026",
                      p1_hora_termino="17:00", reprogramacoes=1)                                    # reprogramação: nova revisão
        novo, _ = app.doc_lib_pdf_para_envio_sm(fluxo.doc(sm_id), "operador1")
        assert novo != primeiro and os.path.isfile(primeiro) and os.path.isfile(novo)
        assert "26/10/2026" in " ".join("\n".join(p.get_text() for p in pymupdf.open(novo)).split())

    def test_arquivo_apagado_e_gerado_de_novo(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        primeiro, _ = app.doc_lib_pdf_para_envio_sm(fluxo.doc(sm_id), "operador1")
        os.remove(primeiro)
        novo, _ = app.doc_lib_pdf_para_envio_sm(fluxo.doc(sm_id), "operador1")
        assert os.path.isfile(novo)

    def test_documento_alterado_por_outro_usuario_nao_gera_pdf_orfao(self, app, fluxo, banco):
        sm_id = fluxo.ate(AGUARDA)
        antigo = fluxo.doc(sm_id)
        fluxo.alterar(sm_id, p1_data_inicio="26/10/2026", p1_hora_inicio="08:00", p1_data_termino="26/10/2026",
                      p1_hora_termino="17:00", reprogramacoes=1)
        with pytest.raises(app.DocLibConflito):
            app.doc_lib_arquivar_pdf_envio_sm(antigo, "operador1")
        arquivos = [f for _, _, fs in os.walk(str(banco / "doc_lib_arquivo" / "SM" / "Enviados")) for f in fs] \
            if os.path.isdir(str(banco / "doc_lib_arquivo" / "SM" / "Enviados")) else []
        assert arquivos == []

    def test_envio_nao_emite_nem_muda_a_sm(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        antes = fluxo.doc(sm_id)
        app.doc_lib_pdf_para_envio_sm(antes, "operador1")
        depois = fluxo.doc(sm_id)
        assert (depois["status"], depois["revisao"], depois["emitido"]) == (antes["status"], antes["revisao"], antes["emitido"])


class TestRegistroDosEnvios:
    def test_registra_o_envio_e_marca_o_grid_sem_mudar_a_revisao(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        antes = fluxo.doc(sm_id)
        data = app.doc_lib_registrar_envio_sm(sm_id, "preoperacao@alupar.com.br", ["a@x.com.br", "b@x.com.br"], ["c@x.com.br"],
                                              "Assunto: 0001/26", "/tmp/x.pdf", "SMTP", "operador1")
        assert data == HOJE
        depois = fluxo.doc(sm_id)
        assert (depois["revisao"], depois["status"]) == (antes["revisao"], AGUARDA)
        assert (depois["email_enviado_em"], depois["email_enviado_por"], depois["email_enviado_origem"]) == (HOJE, "operador1", "Sistema")
        envios = app.doc_lib_emails_enviados_sm(sm_id)
        assert len(envios) == 1 and envios[0]["destinatarios"] == "a@x.com.br; b@x.com.br" and envios[0]["copias"] == "c@x.com.br"
        assert envios[0]["remetente"] == "preoperacao@alupar.com.br" and envios[0]["revisao"] == antes["revisao"]
        assert app.doc_lib_email_enviado_sm(sm_id) == HOJE
        registro = next(r for r in app.doc_lib_listar_sm() if r["ateie_id"] == sm_id)
        assert registro["email_enviado"] == f"Sim, em {HOJE}"

    def test_novo_envio_fica_no_historico_e_a_coluna_mostra_o_mais_recente(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        conexao = app.doc_lib_conectar()
        for _ in range(2):
            app.doc_lib_registrar_envio_sm(sm_id, "temporeal@alupar.com.br", ["a@x.com.br"], [], "A", "/tmp/x.pdf", "SMTP", "operador1")
        conexao.execute("UPDATE doclib_sm SET email_enviado_em = '01/01/2026' WHERE id = ?", (sm_id,))
        conexao.commit()
        conexao.close()
        app.doc_lib_registrar_envio_sm(sm_id, "temporeal@alupar.com.br", ["a@x.com.br"], [], "A", "/tmp/x.pdf", "SMTP", "operador1")
        assert len(app.doc_lib_emails_enviados_sm(sm_id)) == 3 and app.doc_lib_email_enviado_sm(sm_id) == HOJE

    def test_registro_de_envio_nao_aceita_alteracao_nem_exclusao(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        app.doc_lib_registrar_envio_sm(sm_id, "temporeal@alupar.com.br", ["a@x.com.br"], [], "A", "/tmp/x.pdf", "SMTP", "operador1")
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.DatabaseError, match="não pode ser alterado"):
            conexao.execute("UPDATE doclib_sm_emails SET destinatarios = 'outro@x.com.br'")
        with pytest.raises(sqlite3.DatabaseError, match="não pode ser excluído"):
            conexao.execute("DELETE FROM doclib_sm_emails")
        conexao.close()

    def test_sm_cancelada_durante_o_envio_registra_o_envio_sem_tocar_na_sm(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        app.doc_lib_cancelar_sm(sm_id, "operador1", "Cancelada", fluxo.doc(sm_id)["revisao"])
        app.doc_lib_registrar_envio_sm(sm_id, "temporeal@alupar.com.br", ["a@x.com.br"], [], "A", "/tmp/x.pdf", "SMTP", "operador1")
        assert len(app.doc_lib_emails_enviados_sm(sm_id)) == 1 and fluxo.doc(sm_id)["email_enviado_em"] in (None, "")

    def test_sm_inexistente(self, app, banco):
        with pytest.raises(app.DocLibConflito):
            app.doc_lib_registrar_envio_sm(999, "temporeal@alupar.com.br", ["a@x.com.br"], [], "A", "/tmp/x.pdf", "SMTP", "operador1")

    def test_banco_antigo_recebe_as_colunas_e_as_tabelas_sem_perder_dados(self, app, fluxo, banco):
        sm_id = fluxo.ate(AGUARDA)
        conexao = app.doc_lib_conectar(manual=True)
        for gatilho in ("trg_doclib_sm_emails_altera", "trg_doclib_sm_emails_exclui"):
            conexao.execute(f"DROP TRIGGER {gatilho}")
        conexao.execute("DROP TABLE doclib_sm_emails")
        conexao.execute("DROP TABLE doclib_sm_contatos")
        conexao.execute("ALTER TABLE doclib_sm DROP COLUMN email_enviado_em")
        conexao.execute("ALTER TABLE doclib_sm DROP COLUMN email_enviado_por")
        conexao.execute("ALTER TABLE doclib_sm DROP COLUMN email_enviado_origem")
        conexao.execute("ALTER TABLE doclib_sm_pdfs DROP COLUMN tipo")
        conexao.close()
        app.garantir_banco_doc_lib()
        assert fluxo.doc(sm_id)["status"] == AGUARDA and fluxo.doc(sm_id)["email_enviado_em"] is None
        assert len(app.doc_lib_listar_contatos_sm()) == 2
        app.doc_lib_registrar_envio_sm(sm_id, "temporeal@alupar.com.br", ["a@x.com.br"], [], "A", "/tmp/x.pdf", "SMTP", "operador1")


class TestMarcacaoManualNoGrid:
    def test_marca_e_volta_para_nao(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        assert app.doc_lib_definir_email_enviado_sm([(sm_id, 1)], "25/10/2026", "operador1") == 1
        doc = fluxo.doc(sm_id)
        assert (doc["email_enviado_em"], doc["email_enviado_por"], doc["email_enviado_origem"]) == ("25/10/2026", "operador1", "Manual")
        with pytest.raises(app.DocLibRegra, match="já consta|Já consta"):
            app.doc_lib_definir_email_enviado_sm([(sm_id, 1)], "26/10/2026", "operador1")
        app.doc_lib_definir_email_enviado_sm([(sm_id, 1)], None, "operador1")
        assert fluxo.doc(sm_id)["email_enviado_em"] is None and app.doc_lib_email_enviado_sm(sm_id) == ""

    @pytest.mark.parametrize("status", [AGUARDA, APROVADO, EM_EXECUCAO])
    def test_vale_para_sm_emitida_em_andamento(self, app, fluxo, status):
        sm_id = fluxo.ate(status)
        app.doc_lib_definir_email_enviado_sm([(sm_id, 1)], "25/10/2026", "operador1")
        assert fluxo.doc(sm_id)["email_enviado_em"] == "25/10/2026"

    def test_nao_vale_para_em_analise_reservada_concluida_e_cancelada(self, app, fluxo):
        em_analise = fluxo.salvar()
        with pytest.raises(app.DocLibRegra, match="depois que o documento é gerado"):
            app.doc_lib_definir_email_enviado_sm([(em_analise, 1)], "25/10/2026", "operador1")
        reservada = app.doc_lib_reservar_sm(1, "operador1")[0]["ateie_id"]
        with pytest.raises(app.DocLibRegra, match="Reservado"):
            app.doc_lib_definir_email_enviado_sm([(reservada, 1)], "25/10/2026", "operador1")
        concluida = fluxo.ate(CONCLUIDO)
        with pytest.raises(app.DocLibRegra, match="não pode mais ser alterada"):
            app.doc_lib_definir_email_enviado_sm([(concluida, 1)], "25/10/2026", "operador1")
        with pytest.raises(app.DocLibRegra, match="não pode mais ser alterada"):
            app.doc_lib_definir_email_enviado_sm([(concluida, 1)], None, "operador1")

    def test_selecao_vazia_e_sm_inexistente(self, app, banco):
        with pytest.raises(app.DocLibRegra, match="Selecione"):
            app.doc_lib_definir_email_enviado_sm([], "25/10/2026", "operador1")
        with pytest.raises(app.DocLibConflito):
            app.doc_lib_definir_email_enviado_sm([(999, 1)], "25/10/2026", "operador1")

    def test_varias_sm_de_uma_vez_so_valem_se_todas_puderem(self, app, fluxo):
        primeira, segunda = fluxo.ate(AGUARDA), fluxo.salvar()                      # a segunda ainda está Em análise
        with pytest.raises(app.DocLibRegra):
            app.doc_lib_definir_email_enviado_sm([(primeira, 1), (segunda, 1)], "25/10/2026", "operador1")
        assert fluxo.doc(primeira)["email_enviado_em"] is None                      # nada foi gravado


@pytest.fixture()
def aguardando(app, fluxo, janelas):
    """Janela da SM aberta sobre uma SM no status Aguarda Conferência."""
    janela = janelas()
    janela._carregar_documento(fluxo.doc(fluxo.ate(AGUARDA)))
    return janela


def abrir_dialogo(app, janela, fluxo):
    dialogo = app.DialogoEncaminharSM(janela.janela, fluxo.doc(janela.sm_id), "operador1", "/tmp/SM_0001-26.pdf", "/tmp/Downloads/SM.pdf")
    app.root.update()
    return dialogo


class TestJanelaDeEnvio:
    def test_mostra_remetentes_sm_anexo_assunto_e_a_lista_de_contatos(self, app, banco, aguardando, fluxo):
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        try:
            textos = " ".join(w.cget("text") for w in dialogo.cartao.winfo_children() if w.winfo_class() == "Label")
            assert "0001/26 (Aguarda Conferência)" in textos and "SM_0001-26.pdf" in textos and "/tmp/Downloads/SM.pdf" in textos
            assert dialogo.assunto == "TESTE DE ENVIO DE E-MAIL - SM - Para Conferência: 0001/26"
            assert dialogo.assunto in textos
            assert [c["email"] for c in dialogo.contatos] == ["jbarros@alupar.com.br", "nmaganha@alupar.com.br"]
            assert dialogo.escolhidos() == ([], []) and "escolha pelo menos um destinatário" in dialogo.lbl_para.cget("text")
            assert "número: 0001/26" in dialogo.previa.get("1.0", "end")
        finally:
            dialogo.janela.destroy()

    def test_marcar_para_e_cc_e_o_contato_nao_fica_nos_dois(self, app, banco, aguardando, fluxo):
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        try:
            assert dialogo.marcar("nmaganha@alupar.com.br", "para") and dialogo.marcar("jbarros@alupar.com.br", "copia")
            assert dialogo.escolhidos() == (["nmaganha@alupar.com.br"], ["jbarros@alupar.com.br"])
            dialogo.marcar("nmaganha@alupar.com.br", "copia")                           # passa de Para para Cc
            assert dialogo.escolhidos() == ([], ["jbarros@alupar.com.br", "nmaganha@alupar.com.br"])
            assert dialogo.lbl_copia.cget("text") == "jbarros@alupar.com.br; nmaganha@alupar.com.br"
            assert not dialogo.marcar("fora@da-lista.com.br", "para")
        finally:
            dialogo.janela.destroy()

    def test_novo_email_entra_na_lista_fica_marcado_e_permanece_nos_proximos_envios(self, app, banco, aguardando, fluxo):
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        try:
            dialogo.marcar("nmaganha@alupar.com.br", "para")
            definir(app, dialogo.ent_email, "  Novo.Contato@Alupar.com.br ")
            definir(app, dialogo.ent_nome, "Novo Contato")
            dialogo.var_tipo_novo.set("copia")
            contato = dialogo.adicionar()
            assert contato["criado"] and contato["email"] == "novo.contato@alupar.com.br"
            assert dialogo.escolhidos() == (["nmaganha@alupar.com.br"], ["novo.contato@alupar.com.br"])
            assert dialogo.ent_email.get() == "" and dialogo.ent_nome.get() == ""
            assert contatos(app)["novo.contato@alupar.com.br"]["nome"] == "Novo Contato"        # já faz parte da lista
            outro = abrir_dialogo(app, aguardando, fluxo)                                       # outra janela de envio vê o contato
            try:
                assert "novo.contato@alupar.com.br" in [c["email"] for c in outro.contatos]
            finally:
                outro.janela.destroy()
        finally:
            dialogo.janela.destroy()

    def test_email_ja_existente_so_e_marcado_e_invalido_e_recusado(self, app, banco, aguardando, fluxo, mensagens):
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        try:
            definir(app, dialogo.ent_email, "JBARROS@alupar.com.br")
            assert not dialogo.adicionar()["criado"]
            assert dialogo.escolhidos() == (["jbarros@alupar.com.br"], []) and len(app.doc_lib_listar_contatos_sm()) == 2
            definir(app, dialogo.ent_email, "isso-nao-e-email")
            assert dialogo.adicionar() is None and "E-mail inválido" in mensagens.avisos[-1][1]
            definir(app, dialogo.ent_email, "")
            assert dialogo.adicionar() is None and "Digite o e-mail" in mensagens.avisos[-1][1]
            assert len(app.doc_lib_listar_contatos_sm()) == 2
        finally:
            dialogo.janela.destroy()

    def test_confirmar_sem_destinatario_em_para_e_recusado(self, app, banco, aguardando, fluxo, mensagens):
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        try:
            dialogo.marcar("jbarros@alupar.com.br", "copia")
            dialogo.confirmar()
            assert "pelo menos um destinatário em Para" in mensagens.avisos[-1][1] and dialogo.resultado is None
            assert dialogo.janela.winfo_exists()
        finally:
            dialogo.janela.destroy()

    def test_confirmar_devolve_o_envio_e_guarda_a_escolha_para_a_proxima_vez(self, app, banco, aguardando, fluxo):
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        dialogo.var_remetente.set("temporeal@alupar.com.br")
        dialogo.marcar("nmaganha@alupar.com.br", "para")
        dialogo.marcar("jbarros@alupar.com.br", "copia")
        dialogo.confirmar()
        assert dialogo.resultado == {"remetente": "temporeal@alupar.com.br", "destinatarios": ["nmaganha@alupar.com.br"],
                                     "copias": ["jbarros@alupar.com.br"]}
        assert app._DOC_LIB_ULTIMO_REMETENTE["valor"] == "temporeal@alupar.com.br"
        proximo = abrir_dialogo(app, aguardando, fluxo)                                          # a escolha vem marcada
        try:
            assert proximo.escolhidos() == (["nmaganha@alupar.com.br"], ["jbarros@alupar.com.br"])
            assert proximo.var_remetente.get() == "temporeal@alupar.com.br"
        finally:
            proximo.janela.destroy()
            app._DOC_LIB_ULTIMO_REMETENTE["valor"] = app.EMAIL_ATEIE_REMETENTE

    def test_email_digitado_e_nao_adicionado_entra_ao_confirmar(self, app, banco, aguardando, fluxo):
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        definir(app, dialogo.ent_email, "ultimo@alupar.com.br")
        dialogo.confirmar()
        assert dialogo.resultado["destinatarios"] == ["ultimo@alupar.com.br"] and dialogo.resultado["copias"] == []
        assert "ultimo@alupar.com.br" in contatos(app)

    def test_email_invalido_digitado_impede_a_confirmacao(self, app, banco, aguardando, fluxo, mensagens):
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        try:
            dialogo.marcar("nmaganha@alupar.com.br", "para")
            definir(app, dialogo.ent_email, "errado")
            dialogo.confirmar()
            assert dialogo.resultado is None and "E-mail inválido" in mensagens.avisos[-1][1]
        finally:
            dialogo.janela.destroy()

    def test_excluir_contato_da_lista_pede_confirmacao(self, app, banco, aguardando, fluxo, mensagens):
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        try:
            dialogo.marcar("nmaganha@alupar.com.br", "para")
            identificador = contatos(app)["jbarros@alupar.com.br"]["id"]
            mensagens.resposta = False
            assert not dialogo.remover(identificador) and "jbarros@alupar.com.br" in contatos(app)
            mensagens.resposta = True
            assert dialogo.remover(identificador) and "jbarros@alupar.com.br" not in contatos(app)
            assert "jbarros@alupar.com.br" in mensagens.perguntas[-1][1]
            assert dialogo.escolhidos() == (["nmaganha@alupar.com.br"], [])                  # as demais marcações ficam
        finally:
            dialogo.janela.destroy()

    def test_lista_vazia_orienta_a_digitar_o_email(self, app, banco, aguardando, fluxo):
        for contato in app.doc_lib_listar_contatos_sm():
            app.doc_lib_remover_contato_sm(contato["id"])
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        try:
            textos = [w.cget("text") for w in dialogo.lista.winfo_children() if w.winfo_class() == "Label"]
            assert any("Nenhum e-mail na lista" in texto for texto in textos)
        finally:
            dialogo.janela.destroy()

    def test_lista_longa_rola(self, app, banco, aguardando, fluxo):
        for i in range(25):
            app.doc_lib_incluir_contato_sm(f"pessoa{i:02d}@alupar.com.br", f"Pessoa {i:02d}", "operador1")
        dialogo = abrir_dialogo(app, aguardando, fluxo)
        try:
            assert len(dialogo.linhas) == 27
            app.root.update()
            regiao = dialogo.canvas.cget("scrollregion").split()
            assert float(regiao[3]) > float(dialogo.canvas.cget("height")) and dialogo.janela.winfo_height() <= max(
                760, dialogo.janela.winfo_screenheight())
        finally:
            dialogo.janela.destroy()


class TestBotaoEncaminharNaJanelaDaSM:
    def test_botao_so_fica_ativo_em_aguarda_conferencia_sem_alteracoes_pendentes(self, app, banco, janelas, fluxo):
        janela = janelas()
        assert estado(janela.btn_encaminhar) == "disabled"                                      # SM nova
        for status, esperado in ((EM_ANALISE, "disabled"), (AGUARDA, "normal"), (APROVADO, "disabled")):
            janela._carregar_documento(fluxo.doc(fluxo.ate(status)))
            assert estado(janela.btn_encaminhar) == esperado, status
        janela._carregar_documento(fluxo.doc(fluxo.ate(AGUARDA)))
        janela._definir_texto(janela.txt_observacoes, "alteração ainda não salva")
        janela._atualizar_estado()
        assert estado(janela.btn_encaminhar) == "disabled"

    def test_oito_botoes_no_rodape_dentro_da_largura_minima(self, app, banco, janelas):
        janela = janelas()
        janela.janela.geometry("1180x700")
        app.root.update()
        botoes = [janela.btn_voltar, janela.btn_salvar, janela.btn_editar, janela.btn_gerar, janela.btn_encaminhar,
                  janela.btn_reservar, janela.btn_cancelar, janela.btn_referencia]
        assert [b.cget("text") for b in botoes][4] == "Encaminhar SM"
        esquerda = min(b.winfo_rootx() for b in botoes) - janela.janela.winfo_rootx()
        direita = max(b.winfo_rootx() + b.winfo_width() for b in botoes) - janela.janela.winfo_rootx()
        assert esquerda >= 0 and direita <= 1180
        caixas = sorted((b.winfo_rootx(), b.winfo_rootx() + b.winfo_width()) for b in botoes)
        assert all(proximo[0] >= anterior[1] for anterior, proximo in zip(caixas, caixas[1:]))       # nenhum sobre o outro


@pytest.fixture()
def escolha(app, monkeypatch):
    """Substitui a janela de envio: devolve a escolha programada (None = usuário cancelou)."""
    class Escolha:
        resposta = {"remetente": "preoperacao@alupar.com.br", "destinatarios": ["a@x.com.br", "b@x.com.br"], "copias": ["c@x.com.br"]}
        chamadas = []
    registro = Escolha()
    registro.chamadas = []

    def dialogo(parent, doc, usuario, caminho_pdf=None, caminho_copia=None, erro_copia=None):
        registro.chamadas.append({"doc": doc, "pdf": caminho_pdf, "copia": caminho_copia})
        return registro.resposta

    monkeypatch.setattr(app, "doc_lib_dialogo_encaminhar_sm", dialogo)
    return registro


class TestEncaminharPelaJanela:
    def test_envia_registra_e_informa(self, app, banco, aguardando, fluxo, envios, escolha, mensagens):
        aguardando.encaminhar()
        assert len(envios.chamadas) == 1
        chamada = envios.chamadas[0]
        assert chamada["remetente"] == "preoperacao@alupar.com.br" and chamada["para"] == ["a@x.com.br", "b@x.com.br"]
        assert chamada["cc"] == ["c@x.com.br"] and chamada["assunto"] == "TESTE DE ENVIO DE E-MAIL - SM - Para Conferência: 0001/26"
        assert "número: 0001/26" in chamada["corpo"] and chamada["anexo"].endswith(".pdf") and os.path.isfile(chamada["anexo"])
        assert os.sep.join(["SM", "Enviados"]) in chamada["anexo"]
        info = mensagens.infos[-1][1]
        assert "E-mail enviado (SMTP)" in info and "Para: a@x.com.br; b@x.com.br" in info and "Cc: c@x.com.br" in info
        assert f"Enviado e-mail: Sim, em {HOJE}" in info
        doc = fluxo.doc(aguardando.sm_id)
        assert doc["status"] == AGUARDA and doc["email_enviado_em"] == HOJE and doc["revisao"] == aguardando.revisao
        assert len(app.doc_lib_emails_enviados_sm(aguardando.sm_id)) == 1
        assert estado(aguardando.btn_encaminhar) == "normal" and not aguardando._pendente()        # a janela segue válida
        assert escolha.chamadas[0]["copia"] and os.path.isfile(escolha.chamadas[0]["copia"])      # cópia na pasta Downloads

    def test_cancelar_a_janela_de_envio_nao_envia_nada(self, app, banco, aguardando, fluxo, envios, escolha, mensagens):
        escolha.resposta = None
        aguardando.encaminhar()
        assert envios.chamadas == [] and app.doc_lib_emails_enviados_sm(aguardando.sm_id) == []
        assert fluxo.doc(aguardando.sm_id)["email_enviado_em"] is None

    def test_falha_no_envio_orienta_o_envio_manual_e_nao_registra(self, app, banco, aguardando, fluxo, envios, escolha, mensagens):
        envios.falhar = "Servidor SMTP fora do ar"
        aguardando.encaminhar()
        titulo, texto = mensagens.erros[-1]
        assert titulo == "Encaminhar SM" and "O e-mail NÃO foi enviado" in texto and "Servidor SMTP fora do ar" in texto
        assert "Para enviar manualmente, use o arquivo" in texto and "Marcar e-mail enviado" in texto
        assert app.doc_lib_emails_enviados_sm(aguardando.sm_id) == [] and fluxo.doc(aguardando.sm_id)["email_enviado_em"] is None

    def test_segundo_envio_pede_confirmacao_mostrando_os_anteriores(self, app, banco, aguardando, fluxo, envios, escolha, mensagens):
        aguardando.encaminhar()
        mensagens.resposta = False
        aguardando.encaminhar()                                                                   # não quer reenviar
        pergunta = mensagens.perguntas[-1][1]
        assert "já foi encaminhada" in pergunta and "Para: a@x.com.br; b@x.com.br" in pergunta and "Cc: c@x.com.br" in pergunta
        assert len(envios.chamadas) == 1 and len(escolha.chamadas) == 1
        mensagens.resposta = True
        aguardando.encaminhar()                                                                   # confirma o reenvio
        assert len(envios.chamadas) == 2 and len(app.doc_lib_emails_enviados_sm(aguardando.sm_id)) == 2

    def test_nao_encaminha_com_alteracoes_nao_salvas_nem_fora_do_status(self, app, banco, aguardando, fluxo, envios, escolha, mensagens):
        aguardando._definir_texto(aguardando.txt_observacoes, "novo texto")
        aguardando.encaminhar()
        assert "Salve a SM" in mensagens.avisos[-1][1] and envios.chamadas == []
        aguardando._definir_texto(aguardando.txt_observacoes, "")
        fluxo.aprovar(aguardando.sm_id)                                                           # outro usuário aprovou a SM
        aguardando.encaminhar()
        assert "foi alterada por outro usuário" in mensagens.avisos[-1][1] and envios.chamadas == []

    def test_sm_que_mudou_com_a_janela_de_envio_aberta_nao_e_enviada(self, app, banco, aguardando, fluxo, envios, escolha, mensagens, monkeypatch):
        original = app.doc_lib_dialogo_encaminhar_sm

        def com_alteracao(*args, **kw):
            fluxo.aprovar(aguardando.sm_id)                                                        # muda enquanto o diálogo está aberto
            return original(*args, **kw)

        monkeypatch.setattr(app, "doc_lib_dialogo_encaminhar_sm", com_alteracao)
        aguardando.encaminhar()
        assert "O e-mail NÃO foi enviado" in mensagens.avisos[-1][1] and envios.chamadas == []
        assert app.doc_lib_emails_enviados_sm(aguardando.sm_id) == []

    def test_envio_feito_mas_nao_registrado_avisa_para_marcar_no_grid(self, app, banco, aguardando, fluxo, envios, escolha, mensagens, monkeypatch):
        def falha(*args, **kw):
            raise sqlite3.OperationalError("database is locked")

        monkeypatch.setattr(app, "doc_lib_registrar_envio_sm", falha)
        aguardando.encaminhar()
        info = mensagens.infos[-1][1]
        assert "E-mail enviado (SMTP)" in info and "não pôde ser registrado" in info and "Marcar e-mail enviado" in info

    def test_sem_configuracao_de_envio_a_mensagem_e_a_do_sistema(self, app, banco, aguardando, fluxo, escolha, mensagens, monkeypatch):
        monkeypatch.setattr(app, "doc_lib_config_email", lambda: {})
        monkeypatch.setattr(app.platform, "system", lambda: "Linux")
        aguardando.encaminhar()
        assert "ainda não foi configurado" in mensagens.erros[-1][1]

    def test_remetente_fora_da_lista_autorizada_e_recusado(self, app, banco, aguardando, fluxo, escolha, mensagens):
        escolha.resposta = dict(escolha.resposta, remetente="intruso@fora.com")
        aguardando.encaminhar()
        assert "Remetente não autorizado" in mensagens.erros[-1][1]
        assert app.doc_lib_emails_enviados_sm(aguardando.sm_id) == []


class TestGridSM:
    def test_coluna_enviado_email_mostra_o_envio_feito_pela_janela(self, app, banco, janelas, fluxo, envios, escolha, mensagens, monkeypatch):
        sm_id = fluxo.ate(AGUARDA)
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        janela.encaminhar()
        grid = app.JanelaListaSM(janela.janela)
        app.root.update()
        try:
            assert grid.registros[0]["email_enviado"] == f"Sim, em {HOJE}"
            assert grid.valores_distintos("email_enviado") == ["Sim"]          # o filtro da coluna agrupa em Sim e Não
        finally:
            grid.janela.destroy()

    def test_marcar_e_voltar_para_nao_pelo_grid(self, app, banco, janelas, fluxo, mensagens, monkeypatch):
        sm_id = fluxo.ate(AGUARDA)
        janela = janelas()
        grid = app.JanelaListaSM(janela.janela)
        app.root.update()
        try:
            monkeypatch.setattr(grid.tabela, "dados_selecionados", lambda: [(sm_id, 1)])
            monkeypatch.setattr(app, "doc_lib_dialogo_email_manual", lambda *a, **k: {"data": "26/10/2026"})
            grid.marcar_email_enviado()
            assert fluxo.doc(sm_id)["email_enviado_em"] == "26/10/2026" and grid.registros[0]["email_enviado"] == "Sim, em 26/10/2026"
            grid.marcar_email_enviado()                                                               # de novo: recusado
            assert "Já consta" in mensagens.avisos[-1][1]
            monkeypatch.setattr(app, "doc_lib_dialogo_email_manual", lambda *a, **k: {"data": None})
            grid.marcar_email_enviado()
            assert fluxo.doc(sm_id)["email_enviado_em"] is None and grid.registros[0]["email_enviado"] == "Não"
        finally:
            grid.janela.destroy()
