"""SM Avulso (Doc_Lib. - Click_25): opções "sem manobras" dos itens 6 (manobras executadas em emergência ou manutenção da
configuração vigente) e 8 (sem necessidade de manobras de normalização): dados, status, banco, PDF e janela."""
import sqlite3

import pytest

from test_sm_avulso_interface import definir, dialogos, estado, janelas, liberado, preencher, travado  # noqa: F401

pymupdf = pytest.importorskip("pymupdf")

EM_ANALISE, AGUARDA, APROVADO = "Em análise", "Aguarda Conferência", "Aprovado para Execução"
EM_EXECUCAO, CONCLUIDO, CANCELADO, RESERVADO = "Em Execução", "Concluído", "Cancelado", "Reservado"

TEXTO_LIB = "Manobras executadas em emergência ou manutenção da configuração vigente"
TEXTO_NOR = "Sem necessidade de manobras de normalização, pois a configuração será mantida como se encontra"


def aprovada(fluxo, **opcao):
    """SM com a opção informada (lib_emergencia=1 ou nor_sem_manobras=1), já emitida e Aprovada para Execução."""
    sm_id = fluxo.salvar(**opcao)
    fluxo.gerar(sm_id)
    fluxo.aprovar(sm_id)
    assert fluxo.doc(sm_id)["status"] == APROVADO
    return sm_id


def historico_de_status(app, sm_id):
    conexao = app.doc_lib_conectar()
    linhas = conexao.execute("SELECT status_anterior, status_novo FROM doclib_sm_historico WHERE sm_id = ? AND evento = 'status' "
                             "ORDER BY id", (sm_id,)).fetchall()
    conexao.close()
    return linhas


class TestDadosDasOpcoes:
    def test_textos_das_opcoes(self, app):
        assert app.DOC_LIB_TEXTO_LIB_EMERGENCIA_SM == TEXTO_LIB and app.DOC_LIB_TEXTO_NOR_SEM_MANOBRAS_SM == TEXTO_NOR

    def test_emergencia_substitui_a_tabela_de_liberacao_pelo_dizer_e_limpa_os_executantes(self, app, fluxo):
        sm_id = fluxo.salvar(lib_emergencia=1, exec_lib_local="Fulano")                    # manobras digitadas continuam nos dados
        doc = fluxo.doc(sm_id)
        assert doc["lib_emergencia"] == 1 and doc["nor_sem_manobras"] == 0
        assert [(m["numero"], m["local"], m["acao"], m["data"], m["hora"]) for m in doc["liberacao"]] == [("", "", TEXTO_LIB, "", "")]
        assert doc["liberacao"][0]["identificacao"] == "" and not doc["exec_lib_local"]
        assert len(doc["normalizacao"]) == 3                                                # a outra etapa não muda

    def test_sem_normalizacao_substitui_a_tabela_de_normalizacao(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar(nor_sem_manobras=1))
        assert doc["nor_sem_manobras"] == 1 and doc["lib_emergencia"] == 0
        assert [(m["numero"], m["local"], m["acao"]) for m in doc["normalizacao"]] == [("", "", TEXTO_NOR)]
        assert len(doc["liberacao"]) == 3

    def test_sem_opcao_tudo_continua_como_antes(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar())
        assert (doc["lib_emergencia"], doc["nor_sem_manobras"]) == (0, 0) and len(doc["liberacao"]) == 3 and len(doc["normalizacao"]) == 3

    def test_a_tabela_com_a_opcao_nao_exige_numero_nem_local(self, app, fluxo):
        def erros(**alteracoes):                                                           # (o Elaborado por vem do usuário, não dos dados)
            dados = app.doc_lib_normalizar_sm(dict(fluxo.dados(**alteracoes), elaborado_por="Operador", elaborado_ass="operador1"))
            return app.doc_lib_validar_sm(dados)

        assert erros(lib_emergencia=1) == [] and erros(nor_sem_manobras=1) == []
        sem_opcao = erros(liberacao=[{"numero": "", "local": "", "acao": TEXTO_LIB}])         # o mesmo dizer, sem a opção marcada
        assert any("Sequência" in mensagem for _, mensagem in sem_opcao)

    def test_as_duas_opcoes_juntas_sao_recusadas_na_validacao_e_no_banco(self, app, fluxo):
        with pytest.raises(app.DocLibValidacaoSM, match="não existe SM sem manobras de liberação e de normalização"):
            fluxo.salvar(lib_emergencia=1, nor_sem_manobras=1)
        erros = app.doc_lib_validar_sm(app.doc_lib_normalizar_sm(fluxo.dados(lib_emergencia=1, nor_sem_manobras=1)))
        assert any(chaves == ("lib_emergencia", "nor_sem_manobras") for chaves, _ in erros)
        sm_id = fluxo.salvar(lib_emergencia=1)
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.DatabaseError, match="não podem ser marcadas juntas"):
            conexao.execute("UPDATE doclib_sm SET nor_sem_manobras = 1 WHERE id = ?", (sm_id,))
        with pytest.raises(sqlite3.IntegrityError):                                         # valor fora de 0 e 1
            conexao.execute("UPDATE doclib_sm SET lib_emergencia = 2 WHERE id = ?", (sm_id,))
        conexao.close()
        assert fluxo.doc(sm_id)["nor_sem_manobras"] == 0

    def test_marcar_e_desmarcar_em_analise_traz_a_tabela_digitada_de_volta_nos_dados_novos(self, app, fluxo):
        sm_id = fluxo.salvar(lib_emergencia=1)
        fluxo.alterar(sm_id, lib_emergencia=0, liberacao=[{"numero": "1", "local": "SE", "acao": "Abrir DJ"}])
        doc = fluxo.doc(sm_id)
        assert doc["lib_emergencia"] == 0 and [m["acao"] for m in doc["liberacao"]] == ["Abrir DJ"]

    def test_opcao_nao_muda_depois_de_gerado_o_documento(self, app, fluxo):
        sm_id = aprovada(fluxo, lib_emergencia=1)
        with pytest.raises(app.DocLibBloqueado, match="edição geral"):
            fluxo.alterar(sm_id, lib_emergencia=0)
        with pytest.raises(app.DocLibBloqueado, match="edição geral"):
            fluxo.alterar(sm_id, nor_sem_manobras=1, lib_emergencia=0)
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.DatabaseError, match="não pode ser alterada"):             # nem direto no banco
            conexao.execute("UPDATE doclib_sm SET lib_emergencia = 0 WHERE id = ?", (sm_id,))
        conexao.close()
        assert fluxo.doc(sm_id)["lib_emergencia"] == 1

    def test_referencia_herda_a_opcao_e_a_linha(self, app, fluxo):
        origem = fluxo.doc(fluxo.salvar(nor_sem_manobras=1))
        referencia = app.doc_lib_dados_referencia_sm(origem)
        assert referencia["nor_sem_manobras"] == 1 and referencia["lib_emergencia"] == 0
        nova = fluxo.doc(fluxo.salvar(**referencia))
        assert nova["nor_sem_manobras"] == 1 and [m["acao"] for m in nova["normalizacao"]] == [TEXTO_NOR]
        assert nova["referencia_id"] == origem["id"]

    def test_banco_antigo_recebe_as_colunas_das_opcoes(self, app, fluxo, banco):
        sm_id = fluxo.salvar()
        conexao = app.doc_lib_conectar(manual=True)
        for gatilho in ("trg_doclib_sm_opcoes_nova", "trg_doclib_sm_opcoes_altera", "trg_doclib_sm_opcoes_emitida"):
            conexao.execute(f"DROP TRIGGER {gatilho}")
        conexao.execute("ALTER TABLE doclib_sm DROP COLUMN lib_emergencia")
        conexao.execute("ALTER TABLE doclib_sm DROP COLUMN nor_sem_manobras")
        conexao.close()
        app.garantir_banco_doc_lib()
        doc = fluxo.doc(sm_id)
        assert (doc["lib_emergencia"], doc["nor_sem_manobras"]) == (0, 0)
        assert fluxo.doc(fluxo.salvar(lib_emergencia=1))["lib_emergencia"] == 1


class TestStatusComAsOpcoes:
    def test_grupos_editaveis_por_status_e_opcao(self, app):
        grupos = app.doc_lib_grupos_editaveis_sm
        assert grupos(APROVADO, {}) == ("reprogramacao", "datas_lib", "exec_lib")
        assert grupos(APROVADO, {"nor_sem_manobras": 1}) == ("reprogramacao", "datas_lib", "exec_lib")
        assert grupos(APROVADO, {"lib_emergencia": 1}) == ("reprogramacao", "datas_nor", "exec_nor")
        assert grupos(EM_EXECUCAO, {}) == ("datas_nor", "exec_nor") and grupos(AGUARDA, {}) == ("conferencias",)
        assert grupos(EM_ANALISE, {"lib_emergencia": 1}) == ("geral",) and grupos(CONCLUIDO, {}) == ()

    def test_sem_normalizacao_conclui_ao_lancar_horarios_e_executantes_da_liberacao(self, app, fluxo):
        sm_id = aprovada(fluxo, nor_sem_manobras=1)
        fluxo.executar(sm_id)                                                                # horários da liberação + item 7
        doc = fluxo.doc(sm_id)
        assert doc["status"] == CONCLUIDO and doc["exec_lib_local"] == "Fulano (campo)"
        assert all(m["data"] and m["hora"] for m in doc["liberacao"])
        assert historico_de_status(app, sm_id)[-1] == (APROVADO, CONCLUIDO)                 # direto, sem Em Execução
        assert EM_EXECUCAO not in [novo for _, novo in historico_de_status(app, sm_id)]

    def test_sem_normalizacao_exige_todos_os_horarios_e_os_executantes_para_concluir(self, app, fluxo):
        sm_id = aprovada(fluxo, nor_sem_manobras=1)
        parcial = fluxo.datar(fluxo.doc(sm_id), "liberacao", 8)
        parcial[1] = dict(parcial[1], data="", hora="")
        with pytest.raises(app.DocLibRegra, match="Manobra de liberação 1B"):
            fluxo.alterar(sm_id, liberacao=parcial, exec_lib_local="Fulano")
        fluxo.alterar(sm_id, liberacao=parcial)                                              # só os horários parciais: segue Aprovada
        assert fluxo.doc(sm_id)["status"] == APROVADO
        fluxo.alterar(sm_id, liberacao=fluxo.datar(fluxo.doc(sm_id), "liberacao", 8))       # horários completos, mas sem executantes
        assert fluxo.doc(sm_id)["status"] == APROVADO                                      # não conclui sem os executantes

    def test_sem_normalizacao_ignora_horarios_e_executantes_da_normalizacao(self, app, fluxo):
        sm_id = aprovada(fluxo, nor_sem_manobras=1)
        normalizacao = fluxo.doc(sm_id)["normalizacao"]
        fluxo.alterar(sm_id, normalizacao=[dict(normalizacao[0], data="25/10/2026", hora="09:00")], exec_nor_local="Fulano")
        doc = fluxo.doc(sm_id)                                       # a opção prevalece: nada da normalização é gravado
        assert doc["status"] == APROVADO and doc["normalizacao"][0]["data"] == "" and not doc["exec_nor_local"]
        assert [m["acao"] for m in doc["normalizacao"]] == [TEXTO_NOR]

    def test_emergencia_conclui_ao_lancar_horarios_e_executantes_da_normalizacao(self, app, fluxo):
        sm_id = aprovada(fluxo, lib_emergencia=1)
        fluxo.concluir(sm_id)                                                                # horários da normalização + item 9
        doc = fluxo.doc(sm_id)
        assert doc["status"] == CONCLUIDO and doc["exec_nor_remoto"] == "Sicrano (COG)"
        assert all(m["data"] and m["hora"] for m in doc["normalizacao"])
        assert historico_de_status(app, sm_id)[-1] == (APROVADO, CONCLUIDO)
        assert doc["liberacao"][0]["data"] == "" and not doc["exec_lib_local"]

    def test_emergencia_exige_todos_os_horarios_da_normalizacao(self, app, fluxo):
        sm_id = aprovada(fluxo, lib_emergencia=1)
        parcial = fluxo.datar(fluxo.doc(sm_id), "normalizacao", 8)
        parcial[2] = dict(parcial[2], data="", hora="")
        with pytest.raises(app.DocLibRegra, match="Manobra de normalização 2B"):
            fluxo.alterar(sm_id, normalizacao=parcial, exec_nor_local="Fulano")
        fluxo.alterar(sm_id, normalizacao=parcial)
        assert fluxo.doc(sm_id)["status"] == APROVADO

    def test_emergencia_ignora_horarios_e_executantes_da_liberacao(self, app, fluxo):
        sm_id = aprovada(fluxo, lib_emergencia=1)
        liberacao = fluxo.doc(sm_id)["liberacao"]
        fluxo.alterar(sm_id, liberacao=[dict(liberacao[0], data="25/10/2026", hora="09:00")], exec_lib_local="Fulano")
        doc = fluxo.doc(sm_id)
        assert doc["status"] == APROVADO and doc["liberacao"][0]["data"] == "" and not doc["exec_lib_local"]
        assert [m["acao"] for m in doc["liberacao"]] == [TEXTO_LIB]

    def test_antecedencia_de_3_horas_vale_na_liberacao_da_sm_sem_normalizacao_e_nao_na_de_emergencia(self, app, fluxo):
        sm_id = aprovada(fluxo, nor_sem_manobras=1)                                          # programação 25/10 08:00
        antecipada = [dict(m, data="25/10/2026", hora="04:00") for m in fluxo.doc(sm_id)["liberacao"]]
        with pytest.raises(app.DocLibValidacaoSM, match="3 horas do início programado"):
            fluxo.alterar(sm_id, liberacao=antecipada)
        emergencia = aprovada(fluxo, lib_emergencia=1)
        fluxo.concluir(emergencia)                                                           # sem manobras de liberação: sem a regra
        assert fluxo.doc(emergencia)["status"] == CONCLUIDO

    def test_reprogramacao_e_cancelamento_continuam_possiveis_com_as_opcoes(self, app, fluxo):
        for opcao in ({"lib_emergencia": 1}, {"nor_sem_manobras": 1}):
            sm_id = aprovada(fluxo, **opcao)
            fluxo.alterar(sm_id, p1_data_inicio="26/10/2026", p1_hora_inicio="08:00", p1_data_termino="26/10/2026",
                          p1_hora_termino="17:00", reprogramacoes=1)
            assert fluxo.doc(sm_id)["p1_hora_termino"] == "17:00" and fluxo.doc(sm_id)["status"] == APROVADO
            app.doc_lib_cancelar_sm(sm_id, "operador1", "Cancelada", fluxo.doc(sm_id)["revisao"])
            assert fluxo.doc(sm_id)["status"] == CANCELADO

    def test_sm_concluida_pelas_opcoes_nao_aceita_mais_nada_nem_prorrogacao(self, app, fluxo):
        sm_id = aprovada(fluxo, nor_sem_manobras=1)
        fluxo.executar(sm_id)
        with pytest.raises(app.DocLibBloqueado):
            fluxo.alterar(sm_id, exec_lib_remoto="Outro")
        with pytest.raises(app.DocLibRegra, match="Situação atual: Concluído"):
            app.doc_lib_prorrogar_sm(sm_id, "26/10/2026", "10:00", "operador1", fluxo.doc(sm_id)["revisao"])

    def test_banco_aceita_a_transicao_direta_aprovado_concluido_e_continua_recusando_as_outras(self, app, fluxo):
        sm_id = aprovada(fluxo, nor_sem_manobras=1)
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.IntegrityError, match="transição de status"):
            conexao.execute("UPDATE doclib_sm SET status = ? WHERE id = ?", (EM_ANALISE, sm_id))
        conexao.close()


def spans_do_pdf(caminho):
    return [t["text"].strip() for pagina in pymupdf.open(caminho) for bloco in pagina.get_text("dict")["blocks"]
            for linha in bloco.get("lines", []) for t in linha["spans"]]


class TestPdfComAsOpcoes:
    def test_dizer_da_emergencia_sai_na_coluna_acao_do_item_6(self, app, fluxo):
        sm_id = fluxo.salvar(lib_emergencia=1)
        caminho, _ = fluxo.gerar(sm_id)
        texto = " ".join("\n".join(p.get_text() for p in pymupdf.open(caminho)).split())
        assert TEXTO_LIB in texto and TEXTO_NOR not in texto
        assert "Abrir DJ 52-1" not in texto and "Fechar DJ 52-1" in texto                  # a normalização segue normal

    def test_dizer_da_normalizacao_sai_na_coluna_acao_do_item_8(self, app, fluxo):
        sm_id = fluxo.salvar(nor_sem_manobras=1)
        caminho, _ = fluxo.gerar(sm_id)
        texto = " ".join("\n".join(p.get_text() for p in pymupdf.open(caminho)).split())
        assert TEXTO_NOR in texto and TEXTO_LIB not in texto
        assert "Fechar DJ 52-1" not in texto and "Abrir DJ 52-1" in texto

    def test_a_linha_do_dizer_nao_imprime_sequencia_nem_local(self, app, fluxo):
        sm_id = fluxo.salvar(lib_emergencia=1)
        caminho, _ = fluxo.gerar(sm_id)
        trechos = spans_do_pdf(caminho)
        assert "1B" not in trechos and trechos.count("1A") == 1                              # só a normalização tem sequência
        assert "2A" in trechos and "2B" in trechos


# ======================================================================================================================
# janela
# ======================================================================================================================
def preencher_sem_tabelas(app, janela):
    """SM válida na janela, com as tabelas de manobras ainda vazias (as opções serão marcadas em seguida)."""
    preencher(app, janela)
    janela.tab_lib.preencher([])
    janela.tab_nor.preencher([])


def campos_da_tabela(tabela):
    return [linha[campo] for linha in tabela.linhas for campo in ("data", "hora", "icone", "numero", "local", "acao")]


def botoes_da_tabela(tabela):
    return [tabela.btn_adicionar] + [linha[b] for linha in tabela.linhas for b in ("btn_subir", "btn_descer", "btn_remover", "btn_conferir")]


def marcar(janela, chave, valor=True):
    janela._opcoes[chave].set(valor)
    janela._ao_marcar_opcao(chave)


class TestJanelaComAsOpcoes:
    def test_checkbuttons_ficam_depois_da_tabela_e_antes_dos_executantes(self, app, banco, janelas):
        janela = janelas()
        janela.janela.geometry("1280x2400")
        app.root.update()
        assert janela.chk_lib_emergencia.cget("text") == TEXTO_LIB and janela.chk_nor_sem_manobras.cget("text") == TEXTO_NOR
        y = lambda widget: widget.winfo_rooty()
        assert y(janela.tab_lib.btn_adicionar) < y(janela.chk_lib_emergencia) < y(janela.ent_exec_lib_local)
        assert y(janela.tab_nor.btn_adicionar) < y(janela.chk_nor_sem_manobras) < y(janela.ent_exec_nor_local)
        assert y(janela.ent_exec_lib_local) < y(janela.tab_nor.btn_adicionar)

    def test_marcar_emergencia_poe_o_dizer_na_primeira_linha_e_desabilita_o_resto(self, app, banco, janelas):
        janela = janelas()
        marcar(janela, "liberacao")
        tabela = janela.tab_lib
        assert len(tabela.linhas) == 1 and tabela.linhas[0]["acao"].get("1.0", "end-1c") == TEXTO_LIB
        assert all(travado(w) for w in campos_da_tabela(tabela))                                # inclusive data, hora, número e local
        assert all(estado(b) == "disabled" for b in botoes_da_tabela(tabela))
        assert tabela.linhas[0]["numero"].get() == "" and tabela.linhas[0]["local"].get() == ""
        assert travado(janela.ent_exec_lib_local) and travado(janela.ent_exec_lib_remoto)       # item 7 não se preenche
        assert estado(janela.chk_nor_sem_manobras) == "disabled" and estado(janela.chk_lib_emergencia) == "normal"
        assert estado(janela.btn_inverter) == "disabled"
        assert not janela.tab_nor.texto_fixo and not travado(janela.tab_nor.linhas[0]["numero"])  # a normalização segue normal

    def test_marcar_sem_normalizacao_faz_o_mesmo_no_item_8(self, app, banco, janelas):
        janela = janelas()
        marcar(janela, "normalizacao")
        tabela = janela.tab_nor
        assert [l["acao"].get("1.0", "end-1c") for l in tabela.linhas] == [TEXTO_NOR]
        assert all(travado(w) for w in campos_da_tabela(tabela)) and all(estado(b) == "disabled" for b in botoes_da_tabela(tabela))
        assert travado(janela.ent_exec_nor_local) and travado(janela.ent_exec_nor_remoto)
        assert estado(janela.chk_lib_emergencia) == "disabled" and estado(janela.btn_inverter) == "disabled"

    def test_nao_e_possivel_marcar_as_duas_opcoes(self, app, banco, janelas):
        janela = janelas()
        marcar(janela, "liberacao")
        assert estado(janela.chk_nor_sem_manobras) == "disabled"
        marcar(janela, "normalizacao")                                                            # (clique simultâneo forçado)
        assert not janela._opcoes["normalizacao"].get() and janela._opcoes["liberacao"].get()
        assert not janela.tab_nor.texto_fixo
        marcar(janela, "liberacao", False)                                                        # desmarcada a primeira, a outra libera
        assert estado(janela.chk_nor_sem_manobras) == "normal"
        marcar(janela, "normalizacao")
        assert estado(janela.chk_lib_emergencia) == "disabled"

    def test_manobras_digitadas_mais_a_opcao_mostram_aviso_e_prevalece_o_dizer(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)                                                                    # 3 manobras de liberação digitadas
        marcar(janela, "liberacao")
        titulo, texto = mensagens.avisos[-1]
        assert titulo == "Item 6" and "serão mantidos os dizeres da opção" in texto and TEXTO_LIB in texto
        assert [l["acao"].get("1.0", "end-1c") for l in janela.tab_lib.linhas] == [TEXTO_LIB]
        assert [m["acao"] for m in app.doc_lib_normalizar_sm(janela._coletar())["liberacao"]] == [TEXTO_LIB]

    def test_sem_manobras_digitadas_nao_ha_aviso(self, app, banco, janelas, mensagens):
        janela = janelas()
        marcar(janela, "liberacao")
        marcar(janela, "liberacao", False)
        marcar(janela, "normalizacao")
        assert not mensagens.avisos

    def test_aviso_tambem_no_item_8(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        marcar(janela, "normalizacao")
        assert mensagens.avisos[-1][0] == "Item 8" and TEXTO_NOR in mensagens.avisos[-1][1]

    def test_desmarcar_devolve_as_manobras_digitadas_e_libera_a_tabela(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        antes = janela.tab_lib.coletar()
        marcar(janela, "liberacao")
        marcar(janela, "liberacao", False)
        assert janela.tab_lib.coletar() == antes and not janela.tab_lib.texto_fixo
        assert not travado(janela.tab_lib.linhas[0]["numero"]) and estado(janela.tab_lib.btn_adicionar) == "normal"
        assert estado(janela.chk_nor_sem_manobras) == "normal" and estado(janela.btn_inverter) == "normal"

    @pytest.mark.parametrize("chave, tabela", [("liberacao", "tab_lib"), ("normalizacao", "tab_nor")])
    def test_o_dizer_inteiro_fica_visivel_na_celula_da_acao(self, app, banco, janelas, chave, tabela):
        janela = janelas()
        marcar(janela, chave)
        janela.janela.update()
        celula = getattr(janela, tabela).linhas[0]["acao"]
        janela.janela.update()
        assert celula.yview() == (0.0, 1.0) and int(celula.cget("height")) >= 2        # o texto quebra em 2 linhas e as duas aparecem

    def test_texto_digitado_que_quebra_em_duas_linhas_mostra_as_duas(self, app, banco, janelas):
        janela = janelas()
        linha = janela.tab_lib.linhas[0]
        janela._definir_texto(linha["acao"], "Manobras executadas em emergência ou manutenção da configuração vigente")
        janela.janela.update()
        janela.tab_lib._ajustar_altura(linha)
        janela.janela.update()
        assert linha["acao"].yview() == (0.0, 1.0)

    def test_desmarcar_sem_manobras_antes_deixa_uma_linha_em_branco(self, app, banco, janelas):
        janela = janelas()
        marcar(janela, "liberacao")
        marcar(janela, "liberacao", False)
        assert len(janela.tab_lib.linhas) == 1 and janela.tab_lib.linhas[0]["acao"].get("1.0", "end-1c") == ""

    def test_salvar_grava_a_opcao_e_a_janela_reaberta_mostra_a_opcao(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        marcar(janela, "normalizacao")
        janela.salvar()
        assert not mensagens.avisos[1:] and janela.status == EM_ANALISE
        doc = app.doc_lib_carregar_sm(janela.sm_id)
        assert doc["nor_sem_manobras"] == 1 and [m["acao"] for m in doc["normalizacao"]] == [TEXTO_NOR]
        assert all(travado(w) for w in (janela.chk_lib_emergencia, janela.chk_nor_sem_manobras))      # salva: tudo travado
        outra = janelas()
        outra._carregar_documento(doc)
        assert outra._opcoes["normalizacao"].get() and not outra._opcoes["liberacao"].get()
        assert [l["acao"].get("1.0", "end-1c") for l in outra.tab_nor.linhas] == [TEXTO_NOR] and outra.tab_nor.texto_fixo == TEXTO_NOR
        janela.editar()                                                                           # Editar: as opções voltam a ser mexidas
        assert estado(janela.chk_nor_sem_manobras) == "normal" and estado(janela.chk_lib_emergencia) == "disabled"

    def test_documento_gerado_trava_as_duas_opcoes(self, app, banco, janelas, fluxo, dialogos):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.salvar(lib_emergencia=1)))
        janela.gerar()
        assert janela.status == AGUARDA and estado(janela.chk_lib_emergencia) == "disabled" and estado(janela.chk_nor_sem_manobras) == "disabled"
        assert janela._opcoes["liberacao"].get()

    def test_aprovada_com_emergencia_libera_a_normalizacao_e_o_item_9_e_conclui(self, app, banco, janelas, fluxo, mensagens):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(aprovada(fluxo, lib_emergencia=1)))
        assert all(travado(w) for w in campos_da_tabela(janela.tab_lib))
        assert travado(janela.ent_exec_lib_local) and travado(janela.ent_exec_lib_remoto)
        assert not travado(janela.tab_nor.linhas[0]["data"]) and not travado(janela.ent_exec_nor_local)
        for indice, linha in enumerate(janela.tab_nor.linhas):
            definir(app, linha["data"], "25/10/2026")
            definir(app, linha["hora"], f"09:{indice * 10:02d}")
        definir(app, janela.ent_exec_nor_local, "Fulano (campo)")
        janela.salvar()
        assert janela.status == CONCLUIDO and "passou a Concluído" in mensagens.infos[-1][1]
        assert all(travado(w) for w in campos_da_tabela(janela.tab_nor))

    def test_aprovada_sem_normalizacao_libera_a_liberacao_e_o_item_7_e_conclui(self, app, banco, janelas, fluxo, mensagens):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(aprovada(fluxo, nor_sem_manobras=1)))
        assert all(travado(w) for w in campos_da_tabela(janela.tab_nor))
        assert travado(janela.ent_exec_nor_local) and travado(janela.ent_exec_nor_remoto)
        assert not travado(janela.tab_lib.linhas[0]["data"]) and not travado(janela.ent_exec_lib_local)
        for indice, linha in enumerate(janela.tab_lib.linhas):
            definir(app, linha["data"], "25/10/2026")
            definir(app, linha["hora"], f"08:{indice * 10:02d}")
        definir(app, janela.ent_exec_lib_local, "Fulano (campo)")
        janela.salvar()
        assert janela.status == CONCLUIDO and "passou a Concluído" in mensagens.infos[-1][1]

    def test_referencia_herda_a_opcao_marcada(self, app, banco, janelas, fluxo):
        origem = fluxo.doc(fluxo.salvar(lib_emergencia=1))
        nova = app.JanelaSMAvulso(referencia=app.doc_lib_dados_referencia_sm(origem))
        try:
            app.root.update()
            assert nova._opcoes["liberacao"].get() and nova.tab_lib.texto_fixo == TEXTO_LIB
            assert estado(nova.chk_nor_sem_manobras) == "disabled" and travado(nova.ent_exec_lib_local)
            assert [l["acao"].get("1.0", "end-1c") for l in nova.tab_lib.linhas] == [TEXTO_LIB]
        finally:
            nova.janela.destroy()

    def test_inverter_manobras_fica_desabilitado_com_qualquer_opcao(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        marcar(janela, "normalizacao")
        antes = [l["acao"].get("1.0", "end-1c") for l in janela.tab_nor.linhas]
        janela.inverter_manobras()
        assert [l["acao"].get("1.0", "end-1c") for l in janela.tab_nor.linhas] == antes == [TEXTO_NOR]
