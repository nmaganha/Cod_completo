"""SM Avulsa (Doc_Lib. - Click_25), ajuste de 01/11/2026:
  1. item 3: uma linha de equipamento + botão Adicionar Equipamento (até 5); o impresso mantém 3 linhas; 3.1 Local vira lista;
  2. item 5: condições de segurança já vêm com Nenhuma (5.3: Nenhum), editáveis e ainda obrigatórias;
  3. itens 6 e 8: limite de 30 para 40 manobras (tela, validação, banco e PDF), com migração do banco já existente;
  4. o termo SM_Avulso passa a SM_Avulsa em todo o código."""
import os
import re
import sqlite3

import pytest

pymupdf = pytest.importorskip("pymupdf")

from test_sm_avulsa_interface import (definir, dialogos, estado, janelas, liberado, preencher_equipamento,  # noqa: F401
                                      preencher as preencher_completa, travado)
from test_sm_avulsa_pdf import MM, ler, pdf  # noqa: F401  (fixture do PDF)

EM_ANALISE = "Em análise"

LOCAIS_INFORMADOS = ["COG", "UHE MGP", "UHE SJO", "UHE FGO", "PCH QUE", "PCH LAV", "PCH VIE", "CGE PTM", "CGE JDT", "UFV PTM",
                     "EOL VHZ", "EOL SCA", "EOL PTM", "EOL UBA", "EOL GOB", "EOL SAJ", "EOL SRE", "SE MCP", "SE IGU", "SE RSD",
                     "SE SCA", "SE CLA", "SE JDD"]


def equipamento(app, numero, **valores):
    return dict({"local": app.DOC_LIB_LOCAIS_SM[numero], "instalacao": f"PÁTIO {numero}", "equipamento": f"EQUIP-{numero}",
                 "caracterizacao": "Sem desligamento de UG/LT", "local_execucao": "UHE MGP", "tempo_retorno": "02:30"}, **valores)


def dados_validaveis(fluxo, **alteracoes):
    """Dados de uma SM nova como a janela os envia: o Elaborado por (nome e Ass.) é o do usuário autenticado."""
    return fluxo.dados(**dict({"elaborado_por": "Operador Um", "elaborado_ass": "operador1"}, **alteracoes))


def erros_de(app, fluxo, **alteracoes):
    dados = app.doc_lib_normalizar_sm(dados_validaveis(fluxo, **alteracoes))
    return [chaves for chaves, _ in app.doc_lib_validar_sm(dados, None)]


# Linha em branco mede 6,0 mm e linha preenchida 6,3 mm (altura = 3,9 mm por linha de texto + 2,4 mm, no mínimo 6,0 mm). Uma
# linha a mais da tabela 3 acrescentaria no mínimo 6,0 mm (17 pt): abaixo desta folga a tabela tem o mesmo número de linhas.
FOLGA_MESMAS_LINHAS = 3.0


def y_do_motivo(documento):
    """Posição vertical (pt) do título '4. Motivo:' na primeira página: sobe ou desce conforme a altura da tabela 3."""
    return documento[0].search_for("Motivo:")[0].y0


# ======================================================================================================================
# 1. Equipamento(s) a impedir
# ======================================================================================================================
class TestLocalDoItem31:
    def test_lista_e_exatamente_a_informada(self, app):
        assert app.DOC_LIB_LOCAIS_SM == LOCAIS_INFORMADOS and len(app.DOC_LIB_LOCAIS_SM) == 23

    @pytest.mark.parametrize("local", LOCAIS_INFORMADOS)
    def test_cada_local_da_lista_e_aceito(self, app, fluxo, local):
        assert erros_de(app, fluxo, equipamentos=[equipamento(app, 0, local=local)]) == []

    def test_texto_fora_da_lista_e_recusado(self, app, fluxo):
        assert ("equip:1:local",) in erros_de(app, fluxo, equipamentos=[equipamento(app, 0, local="SE XYZ")])
        with pytest.raises(app.DocLibValidacaoSM):
            fluxo.salvar(equipamentos=[equipamento(app, 0, local="OUTRO LUGAR")])

    def test_vazio_pede_a_escolha_na_lista(self, app, fluxo):
        dados = app.doc_lib_normalizar_sm(dados_validaveis(fluxo, equipamentos=[equipamento(app, 0, local="")]))
        mensagens = [m for chaves, m in app.doc_lib_validar_sm(dados, None) if chaves == ("equip:1:local",)]
        assert mensagens and "3.1 Local: selecione uma opção da lista" in mensagens[0]

    def test_minusculas_viram_a_opcao_da_lista(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar(equipamentos=[equipamento(app, 0, local=" se   igu ")]))
        assert doc["equipamentos"][0]["local"] == "SE IGU"

    def test_sm_antiga_com_texto_livre_continua_legivel(self, app, fluxo):
        """SM gravada antes da lista (3.1 era texto livre): abre para consulta; só exige a lista ao editar uma SM em análise."""
        sm_id = fluxo.ate("Aprovado para Execução")
        conexao = app.doc_lib_conectar()
        conexao.execute("UPDATE doclib_sm_equipamentos SET local = 'PÁTIO ANTIGO' WHERE sm_id = ?", (sm_id,))
        conexao.commit()
        conexao.close()
        assert fluxo.doc(sm_id)["equipamentos"][0]["local"] == "PÁTIO ANTIGO"
        fluxo.executar(sm_id)                         # as etapas de acompanhamento não revalidam a tabela 3
        assert fluxo.doc(sm_id)["status"] == "Em Execução"
        assert fluxo.doc(sm_id)["equipamentos"][0]["local"] == "PÁTIO ANTIGO"


class TestLinhasDeEquipamento:
    def test_uma_linha_informada_grava_tres_com_duas_em_branco(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar(equipamentos=[equipamento(app, 1)]))
        assert len(doc["equipamentos"]) == 3 == app.DOC_LIB_LINHAS_EQUIPAMENTOS_SM
        assert doc["equipamentos"][0]["equipamento"] == "EQUIP-1"
        assert all(not any(item[c] for c, _, _ in app.DOC_LIB_COLUNAS_EQUIPAMENTO_SM) for item in doc["equipamentos"][1:])

    @pytest.mark.parametrize("quantas", [2, 3, 4, 5])
    def test_ate_cinco_equipamentos_sao_gravados_na_ordem(self, app, fluxo, quantas):
        linhas = [equipamento(app, i) for i in range(1, quantas + 1)]
        doc = fluxo.doc(fluxo.salvar(equipamentos=linhas))
        assert len(doc["equipamentos"]) == max(3, quantas)
        assert [item["equipamento"] for item in doc["equipamentos"][:quantas]] == [f"EQUIP-{i}" for i in range(1, quantas + 1)]
        assert [item["ordem"] for item in doc["equipamentos"]] == list(range(1, max(3, quantas) + 1))

    def test_linhas_em_branco_no_fim_alem_das_tres_primeiras_saem(self, app, fluxo):
        linhas = [equipamento(app, 1), {}, {}, {}, {}]
        assert len(fluxo.doc(fluxo.salvar(equipamentos=linhas))["equipamentos"]) == 3
        linhas = [equipamento(app, 1), equipamento(app, 2), equipamento(app, 3), equipamento(app, 4), {}]
        assert len(fluxo.doc(fluxo.salvar(equipamentos=linhas))["equipamentos"]) == 4

    def test_linha_em_branco_no_meio_e_mantida_na_posicao(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar(equipamentos=[equipamento(app, 1), {}, equipamento(app, 3)]))
        assert [item["equipamento"] for item in doc["equipamentos"]] == ["EQUIP-1", "", "EQUIP-3"]

    def test_quarta_e_quinta_linhas_so_valem_por_inteiro(self, app, fluxo):
        base = [equipamento(app, i) for i in (1, 2, 3)]
        erros = erros_de(app, fluxo, equipamentos=base + [{"equipamento": "SO ISTO"}])
        assert ("equip:4:local",) in erros and ("equip:4:instalacao",) in erros and ("equip:4:tempo_retorno",) in erros
        erros = erros_de(app, fluxo, equipamentos=base + [equipamento(app, 4), {"local": "SE IGU"}])
        assert ("equip:5:instalacao",) in erros and not any(chave[0].startswith("equip:4") for chave in erros)

    def test_sexta_linha_nao_existe(self, app, fluxo):
        assert app.DOC_LIB_LIMITE_EQUIPAMENTOS_SM == 5
        dados = app.doc_lib_normalizar_sm(dados_validaveis(fluxo, equipamentos=[equipamento(app, i) for i in range(1, 8)]))
        assert len(dados["equipamentos"]) == 5
        bruto = dados_validaveis(fluxo, equipamentos=[equipamento(app, i) for i in range(1, 8)])
        assert any("no máximo 5" in m for _, m in app.doc_lib_validar_sm(dict(dados, equipamentos=bruto["equipamentos"]), None))

    def test_alterar_so_a_quarta_linha_conta_como_alteracao_dos_dados_gerais(self, app, fluxo):
        sm_id = fluxo.salvar(equipamentos=[equipamento(app, i) for i in (1, 2, 3, 4)])
        doc = fluxo.doc(sm_id)
        antes = doc["revisao"]
        fluxo.alterar(sm_id, equipamentos=[dict(item, equipamento="MUDOU") if item["ordem"] == 4 else item
                                           for item in doc["equipamentos"]])
        depois = fluxo.doc(sm_id)
        assert depois["equipamentos"][3]["equipamento"] == "MUDOU" and depois["revisao"] > antes

    def test_banco_aceita_cinco_linhas_e_recusa_a_sexta(self, app, fluxo):
        sm_id = fluxo.salvar(equipamentos=[equipamento(app, i) for i in range(1, 6)])
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.IntegrityError):
            conexao.execute("INSERT INTO doclib_sm_equipamentos (sm_id, ordem) VALUES (?, 6)", (sm_id,))
        conexao.close()

    def test_referencia_herda_as_quatro_linhas(self, app, fluxo):
        sm_id = fluxo.salvar(equipamentos=[equipamento(app, i) for i in (1, 2, 3, 4)])
        referencia = app.doc_lib_dados_referencia_sm(fluxo.doc(sm_id))
        assert [item["equipamento"] for item in referencia["equipamentos"]] == [f"EQUIP-{i}" for i in (1, 2, 3, 4)]


class TestDocumentoImpressoDaTabela3:
    def test_uma_linha_ou_tres_imprimem_o_mesmo_formulario(self, app, fluxo, pdf):
        uma = fluxo.salvar(equipamentos=[equipamento(app, 1)])
        tres = fluxo.salvar(equipamentos=[equipamento(app, 1), equipamento(app, 2), equipamento(app, 3)])
        _, doc_uma, texto_uma = pdf(uma)
        _, doc_tres, _ = pdf(tres)
        assert abs(y_do_motivo(doc_uma) - y_do_motivo(doc_tres)) < FOLGA_MESMAS_LINHAS      # não encolhe com 1 equipamento
        assert "EQUIP-1" in texto_uma and "EQUIP-2" not in texto_uma

    def test_quatro_e_cinco_equipamentos_aumentam_a_tabela(self, app, fluxo, pdf):
        alturas, textos = {}, {}
        for quantas in (3, 4, 5):
            sm_id = fluxo.salvar(equipamentos=[equipamento(app, i) for i in range(1, quantas + 1)])
            _, documento, textos[quantas] = pdf(sm_id)
            alturas[quantas] = y_do_motivo(documento)
        linha_minima = 6.0 * MM - 0.5                                                 # cada linha tem ao menos 6 mm
        assert alturas[4] - alturas[3] >= linha_minima and alturas[5] - alturas[4] >= linha_minima
        assert "EQUIP-4" in textos[4] and "EQUIP-5" not in textos[4] and "EQUIP-5" in textos[5]

    def test_quatro_linhas_com_a_quarta_em_branco_nao_aumentam_a_tabela(self, app, fluxo, pdf):
        tres = fluxo.salvar(equipamentos=[equipamento(app, 1)])
        quatro = fluxo.salvar(equipamentos=[equipamento(app, 1), {}, {}, {}])
        assert abs(y_do_motivo(pdf(tres)[1]) - y_do_motivo(pdf(quatro)[1])) < FOLGA_MESMAS_LINHAS

    def test_local_do_item_3_1_sai_no_documento(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(equipamentos=[equipamento(app, 1, local="EOL VHZ")])
        _, _, texto = pdf(sm_id)
        assert "EOL VHZ" in texto

    def test_formulario_reservado_continua_com_tres_linhas_em_branco(self, app, fluxo, pdf):
        reservado = app.doc_lib_reservar_sm(1, "operador1", "")[0]["ateie_id"]
        normal = fluxo.salvar(equipamentos=[equipamento(app, 1)])
        _, doc_reservado, _ = pdf(reservado)
        _, doc_normal, _ = pdf(normal)
        assert abs(y_do_motivo(doc_reservado) - y_do_motivo(doc_normal)) < FOLGA_MESMAS_LINHAS


class TestJanelaTabela3:
    def test_abre_com_uma_linha_visivel_e_o_botao(self, app, banco, janelas):
        janela = janelas()
        assert janela.equip_visiveis == 1
        assert janela.btn_adicionar_equip.cget("text") == "Adicionar Equipamento"
        assert estado(janela.btn_adicionar_equip) == "normal"
        assert janela.lbl_contador_equip.cget("text") == "1 de 5 equipamentos"
        visiveis = [all(celula.grid_info() for celula in celulas) for celulas in janela.celulas_equip]
        assert visiveis == [True, False, False, False, False]
        assert len(janela.equip) == 5 and len(janela.celulas_equip[0]) == 6

    def test_botao_fica_logo_abaixo_da_ultima_linha_visivel(self, app, banco, janelas):
        janela = janelas()
        barra = janela.btn_adicionar_equip.master                                        # posição relativa ao quadro da tabela
        antes = barra.winfo_y()
        assert antes >= janela.celulas_equip[0][0].winfo_y() + janela.celulas_equip[0][0].winfo_height()
        janela.adicionar_equipamento()
        app.root.update()
        assert barra.winfo_y() > antes                                                   # desceu para abrir a nova linha
        assert barra.winfo_y() >= janela.celulas_equip[1][0].winfo_y() + janela.celulas_equip[1][0].winfo_height()

    def test_adiciona_ate_cinco_e_desabilita_o_botao(self, app, banco, janelas):
        janela = janelas()
        for esperado in (2, 3, 4, 5):
            janela.btn_adicionar_equip.invoke()
            app.root.update()
            assert janela.equip_visiveis == esperado
            assert all(celula.grid_info() for celula in janela.celulas_equip[esperado - 1])
        assert estado(janela.btn_adicionar_equip) == "disabled"
        assert janela.lbl_contador_equip.cget("text") == "5 de 5 equipamentos"
        janela.adicionar_equipamento()                                                   # além do limite: nada acontece
        assert janela.equip_visiveis == 5

    def test_nova_linha_vem_liberada_para_preenchimento(self, app, banco, janelas):
        janela = janelas()
        janela.adicionar_equipamento()
        assert janela.equip_visiveis == 2 and liberado(janela.equip[1]["local"])

    def test_salva_cinco_equipamentos_e_reabre_com_as_cinco_linhas(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_completa(app, janela)
        for indice in range(1, 5):
            janela.adicionar_equipamento()
            preencher_equipamento(app, janela, indice, local=app.DOC_LIB_LOCAIS_SM[indice], equipamento=f"EQUIP-{indice + 1}")
        janela.salvar()
        assert not mensagens.avisos and janela.status == EM_ANALISE
        doc = app.doc_lib_carregar_sm(janela.sm_id)
        assert len(doc["equipamentos"]) == 5 and doc["equipamentos"][4]["equipamento"] == "EQUIP-5"
        outra = janelas()
        outra._carregar_documento(doc)
        assert outra.equip_visiveis == 5 and outra.equip[4]["equipamento"].get() == "EQUIP-5"
        assert outra.equip[3]["local"].get() == app.DOC_LIB_LOCAIS_SM[3]

    def test_uma_so_linha_reabre_com_uma_linha(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_completa(app, janela)
        janela.salvar()
        doc = app.doc_lib_carregar_sm(janela.sm_id)
        assert len(doc["equipamentos"]) == 3                                            # 2 em branco, como no impresso
        outra = janelas()
        outra._carregar_documento(doc)
        assert outra.equip_visiveis == 1

    def test_linhas_adicionadas_e_deixadas_em_branco_nao_impedem_salvar(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_completa(app, janela)
        for _ in range(4):
            janela.adicionar_equipamento()
        janela.salvar()
        assert not mensagens.avisos and janela.status == EM_ANALISE
        assert len(app.doc_lib_carregar_sm(janela.sm_id)["equipamentos"]) == 3
        assert janela.equip_visiveis == 1                                               # depois de salvar mostra só o que foi usado

    def test_linha_adicionada_pela_metade_e_recusada_e_marcada(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher_completa(app, janela)
        janela.adicionar_equipamento()
        definir(app, janela.equip[1]["equipamento"], "so isto")
        janela.salvar()
        assert janela.sm_id is None and "linha 2, 3.1 Local" in mensagens.avisos[-1][1]

    def test_botao_so_funciona_na_edicao_geral(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_completa(app, janela)
        janela.salvar()
        assert estado(janela.btn_adicionar_equip) == "disabled"                         # SM salva: dados gerais travados
        janela.adicionar_equipamento()
        assert janela.equip_visiveis == 1
        janela.editar()
        assert estado(janela.btn_adicionar_equip) == "normal"
        janela.adicionar_equipamento()
        assert janela.equip_visiveis == 2

    def test_botao_desabilitado_com_a_sm_gerada(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_completa(app, janela)
        janela.salvar()
        janela.gerar()
        assert estado(janela.btn_adicionar_equip) == "disabled"

    def test_pendencia_em_linha_oculta_faz_a_linha_aparecer(self, app, banco, janelas):
        janela = janelas()
        assert janela.equip_visiveis == 1
        widget, _ = janela._alvo_da_chave("equip:4:local")
        assert janela.equip_visiveis == 4 and widget is janela.equip[3]["local"]

    def test_referencia_com_quatro_equipamentos_mostra_quatro_linhas(self, app, banco, janelas, fluxo):
        sm_id = fluxo.salvar(equipamentos=[equipamento(app, i) for i in (1, 2, 3, 4)])
        nova = janelas(referencia=app.doc_lib_dados_referencia_sm(fluxo.doc(sm_id)))
        assert nova.equip_visiveis == 4 and nova.equip[3]["equipamento"].get() == "EQUIP-4"

    def test_trocar_o_local_na_lista_e_gravar(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_completa(app, janela)
        combo = janela.equip[0]["local"]
        combo.current(app.DOC_LIB_LOCAIS_SM.index("PCH VIE"))
        combo.event_generate("<<ComboboxSelected>>")
        janela.salvar()
        assert app.doc_lib_carregar_sm(janela.sm_id)["equipamentos"][0]["local"] == "PCH VIE"


# ======================================================================================================================
# 2. Condições de Segurança
# ======================================================================================================================
CAMPOS_FEMININOS = ("cond_chaves_abertas", "cond_chaves_fechadas", "cond_loto_com", "cond_loto_sem")


def preencher_sem_condicoes(app, janela):
    """Como 'preencher' do teste da interface, mas sem digitar as Condições de Segurança (ficam como a janela as trouxe)."""
    p0 = janela.periodo["p0"]
    for campo, valor in (("data_inicio", "25/10/2026"), ("hora_inicio", "08:00"), ("data_termino", "25/10/2026"),
                         ("hora_termino", "17:00")):
        definir(app, p0[campo], valor)
    preencher_equipamento(app, janela, 0)
    janela._definir_texto(janela.txt_motivo, "Manutenção preventiva do disjuntor 52-1.")
    janela.tab_lib.preencher([{"numero": "1", "local": "SE MCP", "acao": "Abrir DJ 52-1"}])
    janela.tab_nor.preencher([{"numero": "1", "local": "SE MCP", "acao": "Fechar DJ 52-1"}])


class TestCondicoesDeSegurancaPadrao:
    def test_padroes_da_constante(self, app):
        assert app.DOC_LIB_PADRAO_CONDICOES_SM == {"cond_chaves_abertas": "Nenhuma", "cond_chaves_fechadas": "Nenhuma",
                                                   "cond_disjuntores": "Nenhum", "cond_loto_com": "Nenhuma",
                                                   "cond_loto_sem": "Nenhuma"}
        assert set(app.DOC_LIB_PADRAO_CONDICOES_SM) == set(app.DOC_LIB_CAMPOS_CONDICOES_SM)

    def test_sm_nova_abre_com_nenhuma_e_5_3_com_nenhum(self, app, banco, janelas):
        janela = janelas()
        valores = {campo: janela._texto(texto) for campo, texto in janela.txt_condicoes.items()}
        assert valores == {"cond_chaves_abertas": "Nenhuma", "cond_chaves_fechadas": "Nenhuma", "cond_disjuntores": "Nenhum",
                           "cond_loto_com": "Nenhuma", "cond_loto_sem": "Nenhuma"}
        assert all(liberado(texto) for texto in janela.txt_condicoes.values())

    def test_salvar_sem_mexer_nas_condicoes_grava_os_padroes(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_sem_condicoes(app, janela)
        janela.salvar()
        assert not mensagens.avisos and janela.status == EM_ANALISE
        doc = app.doc_lib_carregar_sm(janela.sm_id)
        assert [doc[c] for c in app.DOC_LIB_CAMPOS_CONDICOES_SM] == ["Nenhuma", "Nenhuma", "Nenhum", "Nenhuma", "Nenhuma"]

    def test_campos_podem_ser_editados_durante_a_elaboracao(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_sem_condicoes(app, janela)
        janela._definir_texto(janela.txt_condicoes["cond_chaves_abertas"], "89-1 e 89-2")
        janela._definir_texto(janela.txt_condicoes["cond_disjuntores"], "52-1")
        janela.salvar()
        doc = app.doc_lib_carregar_sm(janela.sm_id)
        assert doc["cond_chaves_abertas"] == "89-1 e 89-2" and doc["cond_disjuntores"] == "52-1"
        assert doc["cond_chaves_fechadas"] == "Nenhuma" and doc["cond_loto_sem"] == "Nenhuma"

    @pytest.mark.parametrize("campo", ["cond_chaves_abertas", "cond_chaves_fechadas", "cond_disjuntores", "cond_loto_com",
                                       "cond_loto_sem"])
    def test_campo_apagado_continua_obrigatorio(self, app, banco, janelas, mensagens, campo):
        janela = janelas()
        preencher_sem_condicoes(app, janela)
        janela._definir_texto(janela.txt_condicoes[campo], "")
        janela.salvar()
        assert janela.sm_id is None and "preencha o campo" in mensagens.avisos[-1][1]

    def test_validacao_e_banco_seguem_exigindo_o_campo(self, app, fluxo):
        """O padrão é só da janela: a camada de dados e o banco não preenchem nada sozinhos."""
        for campo in app.DOC_LIB_CAMPOS_CONDICOES_SM:
            assert (campo,) in erros_de(app, fluxo, **{campo: ""})

    def test_sm_reservada_no_banco_continua_em_branco_mas_abre_com_os_padroes(self, app, banco, janelas):
        reservada = app.doc_lib_reservar_sm(1, "operador1", "")[0]["ateie_id"]
        doc = app.doc_lib_carregar_sm(reservada)
        assert all(not (doc[campo] or "") for campo in app.DOC_LIB_CAMPOS_CONDICOES_SM)
        janela = janelas()
        janela._carregar_documento(doc)
        assert janela.status == "Reservado"
        assert [janela._texto(janela.txt_condicoes[c]) for c in app.DOC_LIB_CAMPOS_CONDICOES_SM] == \
            ["Nenhuma", "Nenhuma", "Nenhum", "Nenhuma", "Nenhuma"]
        assert estado(janela.btn_salvar) == "disabled"                       # os padrões, sozinhos, não são alteração pendente

    def test_sm_ja_gravada_mostra_o_que_foi_gravado(self, app, banco, janelas, fluxo):
        sm_id = fluxo.salvar(cond_chaves_abertas="89-1", cond_disjuntores="52-1")
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        assert janela._texto(janela.txt_condicoes["cond_chaves_abertas"]) == "89-1"
        assert janela._texto(janela.txt_condicoes["cond_disjuntores"]) == "52-1"

    def test_referencia_herda_as_condicoes_da_sm_de_origem(self, app, banco, janelas, fluxo):
        sm_id = fluxo.salvar(cond_chaves_abertas="89-1", cond_loto_sem="Nenhuma")
        nova = janelas(referencia=app.doc_lib_dados_referencia_sm(fluxo.doc(sm_id)))
        assert nova._texto(nova.txt_condicoes["cond_chaves_abertas"]) == "89-1"
        assert nova._texto(nova.txt_condicoes["cond_disjuntores"]) == "Nenhum"

    def test_referencia_de_origem_sem_condicoes_volta_aos_padroes(self, app, banco, janelas, fluxo):
        sm_id = fluxo.salvar()
        referencia = app.doc_lib_dados_referencia_sm(fluxo.doc(sm_id))
        referencia["cond_disjuntores"] = ""
        nova = janelas(referencia=referencia)
        assert nova._texto(nova.txt_condicoes["cond_disjuntores"]) == "Nenhum"

    def test_pdf_traz_os_padroes(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(cond_chaves_abertas="Nenhuma", cond_chaves_fechadas="Nenhuma", cond_disjuntores="Nenhum",
                             cond_loto_com="Nenhuma", cond_loto_sem="Nenhuma")
        _, _, texto = pdf(sm_id)
        assert texto.count("Nenhuma") >= 4 and re.search(r"Nenhum(?!a)", texto)


# ======================================================================================================================
# 3. Itens 6 e 8: 40 manobras
# ======================================================================================================================
class TestQuarentaManobras:
    def test_dicas_dos_itens_6_e_8_informam_o_limite_de_40(self, app, banco, janelas):
        from test_sm_avulsa_interface import _todos_os_widgets
        janela = janelas()
        textos = [w.cget("text") for w in _todos_os_widgets(janela.janela) if w.winfo_class() == "Label"]
        assert any("Limite de 40 linhas para as manobras de liberação" in t for t in textos)
        assert any("Limite de 40 linhas para as manobras de normalização" in t for t in textos)
        assert not any("Limite de 30" in t for t in textos)

    @pytest.mark.parametrize("nome", ["tab_lib", "tab_nor"])
    def test_tabelas_tem_limite_de_40(self, app, banco, janelas, nome):
        tabela = getattr(janelas(), nome)
        assert tabela.limite == 40

    def test_janela_salva_40_manobras_nas_duas_tabelas(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher_completa(app, janela)
        acoes = [{"numero": str(i), "local": "SE MCP", "acao": f"Abrir {i}"} for i in range(1, 41)]
        janela.tab_lib.preencher(acoes)
        janela.tab_nor.preencher(acoes)
        assert len(janela.tab_lib.linhas) == 40 and len(janela.tab_nor.linhas) == 40
        janela.salvar()
        assert not mensagens.avisos and janela.status == EM_ANALISE
        doc = app.doc_lib_carregar_sm(janela.sm_id)
        assert len(doc["liberacao"]) == 40 and len(doc["normalizacao"]) == 40
        assert doc["liberacao"][39]["identificacao"] == "40A"

    def test_quarenta_na_mesma_sequencia_recebe_letras_ate_an(self, app):
        letras = app.doc_lib_identificar_sequencias_sm(["3"] * 40)
        assert letras[26] == "3AA" and letras[39] == "3AN" and len(set(letras)) == 40

    def test_pdf_com_40_manobras_em_cada_tabela(self, app, fluxo, pdf):
        def acoes(prefixo):
            return [{"numero": str(1 + i // 3), "local": "SE MCP",
                     "acao": f"{prefixo}{i + 1:02d} " + "Verificar a posição e abrir o equipamento do vão conforme o procedimento "
                                                        "aprovado pelo COG " * 2} for i in range(40)]
        sm_id = fluxo.salvar(liberacao=acoes("LIB"), normalizacao=acoes("NOR"))
        _, documento, texto = pdf(sm_id)
        plano = " ".join(texto.split())
        assert "Manobras de Liberação (continuação):" in plano and "Manobras de Normalização (continuação):" in plano
        for prefixo in ("LIB", "NOR"):
            for i in range(1, 41):
                assert plano.count(f"{prefixo}{i:02d} ") == 1, f"{prefixo}{i:02d}"
        for numero in range(1, len(documento) + 1):
            assert f"Página {numero} de {len(documento)}" in plano

    def test_sequencia_de_40_manobras_pode_ser_invertida(self, app, fluxo):
        liberacao = [{"numero": str(i % 8 + 1), "local": "SE MCP", "acao": f"Abrir DJ {i}"} for i in range(40)]
        geradas = app.doc_lib_inverter_manobras_sm(liberacao)
        assert len(geradas) == 40


def _recriar_com_limite_antigo(app, tabela, ddl, de, para):
    """Devolve a tabela ao desenho da versão anterior (CHECK de ordem com limite menor), mantendo as linhas."""
    conexao = app.doc_lib_conectar()
    antiga = f"{tabela}_antiga"
    conexao.execute(ddl(antiga).replace(f"BETWEEN 1 AND {de}", f"BETWEEN 1 AND {para}"))
    conexao.execute(f"INSERT INTO {antiga} SELECT * FROM {tabela}")
    conexao.execute(f"DROP TABLE {tabela}")
    conexao.execute(f"ALTER TABLE {antiga} RENAME TO {tabela}")
    conexao.execute("CREATE INDEX IF NOT EXISTS idx_doclib_sm_manobras ON doclib_sm_manobras (sm_id, tipo, ordem)")
    conexao.commit()
    conexao.close()


def _foto(app, tabela):
    conexao = app.doc_lib_conectar()
    linhas = conexao.execute(f"SELECT * FROM {tabela} ORDER BY id").fetchall()
    conexao.close()
    return linhas


class TestMigracaoDoBancoExistente:
    @pytest.fixture()
    def banco_antigo(self, app, fluxo):
        """Banco como o da versão anterior: SMs gravadas e as tabelas 3 e de manobras com limites de 3 e de 30 linhas."""
        ids = [fluxo.salvar(), fluxo.salvar(equipamentos=[equipamento(app, i) for i in (1, 2, 3)])]
        quase = [{"numero": str(i), "local": "SE", "acao": f"Abrir {i}"} for i in range(1, 31)]
        ids.append(fluxo.salvar(liberacao=quase, normalizacao=quase))
        _recriar_com_limite_antigo(app, "doclib_sm_equipamentos", app._doc_lib_ddl_equipamentos_sm, 5, 3)
        _recriar_com_limite_antigo(app, "doclib_sm_manobras", app._doc_lib_ddl_manobras_sm, 40, 30)
        return ids

    def limite(self, app, tabela):
        conexao = app.doc_lib_conectar()
        sql = conexao.execute("SELECT sql FROM sqlite_master WHERE name = ?", (tabela,)).fetchone()[0]
        conexao.close()
        return int(re.search(r"ordem\s+BETWEEN\s+1\s+AND\s+(\d+)", sql).group(1))

    def test_estado_inicial_e_o_da_versao_anterior(self, app, banco_antigo):
        assert self.limite(app, "doclib_sm_equipamentos") == 3 and self.limite(app, "doclib_sm_manobras") == 30
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.IntegrityError):
            conexao.execute("INSERT INTO doclib_sm_manobras (sm_id, tipo, ordem) VALUES (1, 'L', 31)")
        conexao.close()

    def test_migracao_amplia_os_limites_e_preserva_todos_os_dados(self, app, banco_antigo):
        equipamentos_antes, manobras_antes = _foto(app, "doclib_sm_equipamentos"), _foto(app, "doclib_sm_manobras")
        assert len(equipamentos_antes) == 9 and len(manobras_antes) == 6 + 6 + 60
        app.garantir_banco_doc_lib()
        assert self.limite(app, "doclib_sm_equipamentos") == 5 and self.limite(app, "doclib_sm_manobras") == 40
        assert _foto(app, "doclib_sm_equipamentos") == equipamentos_antes
        assert _foto(app, "doclib_sm_manobras") == manobras_antes

    def test_depois_da_migracao_cabem_5_equipamentos_e_40_manobras(self, app, fluxo, banco_antigo):
        app.garantir_banco_doc_lib()
        quarenta = [{"numero": str(i), "local": "SE", "acao": f"Abrir {i}"} for i in range(1, 41)]
        doc = fluxo.doc(fluxo.salvar(equipamentos=[equipamento(app, i) for i in range(1, 6)],
                                     liberacao=quarenta, normalizacao=quarenta))
        assert len(doc["equipamentos"]) == 5 and len(doc["liberacao"]) == 40 and len(doc["normalizacao"]) == 40
        for sm_id in banco_antigo:                                              # as SM antigas continuam abrindo
            assert fluxo.doc(sm_id)["numero"]

    def test_migracao_e_idempotente(self, app, banco_antigo):
        app.garantir_banco_doc_lib()
        depois_da_primeira = (_foto(app, "doclib_sm_equipamentos"), _foto(app, "doclib_sm_manobras"))
        app.garantir_banco_doc_lib()
        assert (_foto(app, "doclib_sm_equipamentos"), _foto(app, "doclib_sm_manobras")) == depois_da_primeira

    def test_migracao_nao_deixa_tabela_temporaria_e_recria_o_indice(self, app, banco_antigo):
        app.garantir_banco_doc_lib()
        conexao = app.doc_lib_conectar()
        tabelas = {linha[0] for linha in conexao.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        indices = {linha[0] for linha in conexao.execute("SELECT name FROM sqlite_master WHERE type = 'index'")}
        conexao.close()
        assert not {n for n in tabelas if n.endswith("_nova") or n.endswith("_antiga")}
        assert "idx_doclib_sm_manobras" in indices

    def test_migracao_mantem_o_contador_de_ids(self, app, banco_antigo):
        conexao = app.doc_lib_conectar()
        antes = conexao.execute("SELECT seq FROM sqlite_sequence WHERE name = 'doclib_sm_manobras'").fetchone()[0]
        conexao.close()
        app.garantir_banco_doc_lib()
        conexao = app.doc_lib_conectar()
        depois = conexao.execute("SELECT seq FROM sqlite_sequence WHERE name = 'doclib_sm_manobras'").fetchone()[0]
        conexao.close()
        assert depois >= antes

    def test_sobra_de_tentativa_interrompida_nao_atrapalha(self, app, banco_antigo):
        conexao = app.doc_lib_conectar()
        conexao.execute("CREATE TABLE doclib_sm_manobras_nova (x INTEGER)")
        conexao.commit()
        conexao.close()
        app.garantir_banco_doc_lib()
        assert self.limite(app, "doclib_sm_manobras") == 40

    def test_banco_novo_ja_nasce_com_os_limites_atuais(self, app, fluxo):
        assert self.limite(app, "doclib_sm_equipamentos") == 5 and self.limite(app, "doclib_sm_manobras") == 40


# ======================================================================================================================
# 4. SM_Avulso -> SM_Avulsa
# ======================================================================================================================
class TestTermoSMAvulsa:
    def test_menu_janela_e_botao_usam_avulsa(self, app, banco, janelas):
        rotulos = [app.fileDOC_LIB.entrycget(i, "label") for i in range(app.fileDOC_LIB.index("end") + 1)
                   if app.fileDOC_LIB.type(i) == "command"]
        assert "SM_Avulsa" in rotulos and "SM_Avulso" not in rotulos
        janela = janelas()
        assert janela.janela.title() == "COG - DOC_LIB. - SM AVULSA"
        assert "Gerar SM Avulsa" in janela.btn_gerar.cget("text")
        assert hasattr(app, "JanelaSMAvulsa") and hasattr(app, "cmd_click25_sm_avulsa")
        assert not hasattr(app, "JanelaSMAvulso") and not hasattr(app, "cmd_click25_sm_avulso")

    def test_nenhum_avulso_sobrou_no_codigo(self, app):
        raiz = os.path.dirname(os.path.abspath(app.__file__))
        with open(os.path.join(raiz, "main.py"), encoding="utf-8") as arquivo:
            assert "avulso" not in arquivo.read().lower()
        assert os.path.exists(os.path.join(raiz, "docs", "SM_Avulsa.md"))
        assert not os.path.exists(os.path.join(raiz, "docs", "SM_Avulso.md"))      # o histórico da mudança fica na decisão 27
