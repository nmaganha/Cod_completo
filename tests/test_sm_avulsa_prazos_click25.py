"""SM Avulsa (Doc_Lib. - Click_25): regras de tempo.

  1. Reprogramações (itens 2.2 a 2.4):
       - o início não pode ser anterior ao momento atual (não se programa uma sequência de manobras para um período passado);
       - não há reprogramação se o término programado do período em vigor venceu há mais de 6 horas.
  2. Manobras de Liberação (item 6): a data e a hora ficam entre 3 horas antes e 3 horas depois do início programado.

O relógio da SM é o fixture 'relogio' (conftest): começa em 24/10/2026 10:00, e os dados de teste têm programação em 25/10/2026
das 08:00 às 17:00.
"""
from datetime import datetime

import pytest

from test_sm_avulsa_interface import definir, dialogos, janelas, preencher_reprogramacao, travado  # noqa: F401  (fixtures e atalhos)

EM_ANALISE, AGUARDA, APROVADO = "Em análise", "Aguarda Conferência", "Aprovado para Execução"
EM_EXECUCAO = "Em Execução"


def reprogramacao(prefixo, inicio, termino, habilitadas=None):
    """Campos de uma reprogramação ((data, hora) de início e de término) mais a contagem de reprogramações habilitadas."""
    return {f"{prefixo}_data_inicio": inicio[0], f"{prefixo}_hora_inicio": inicio[1],
            f"{prefixo}_data_termino": termino[0], f"{prefixo}_hora_termino": termino[1],
            "reprogramacoes": habilitadas or int(prefixo[1])}


def liberacao_em(fluxo, sm_id, *momentos):
    """Liberação gravada com os (data, hora) informados, na ordem das linhas (as que sobram ficam sem horário)."""
    base = fluxo.doc(sm_id)["liberacao"]
    return [dict(m, data=data, hora=hora) for m, (data, hora) in zip(base, momentos)] + base[len(momentos):]


# ======================================================================================================================
# Reprogramação: início anterior ao momento atual
# ======================================================================================================================
class TestReprogramacaoNaoVaiParaOPassado:
    def test_inicio_anterior_ao_momento_atual_e_recusado_e_o_igual_e_aceito(self, app, fluxo, relogio):
        sm_id = fluxo.ate(APROVADO)
        relogio.definir(datetime(2026, 10, 25, 9, 0))
        with pytest.raises(app.DocLibValidacaoSM) as erro:
            fluxo.alterar(sm_id, **reprogramacao("p1", ("25/10/2026", "08:59"), ("25/10/2026", "18:00")))
        texto = str(erro.value)
        assert "Reprogramação-1" in texto and "25/10/2026 08:59" in texto and "25/10/2026 09:00" in texto
        assert "período passado" in texto
        assert fluxo.doc(sm_id)["p1_data_inicio"] == ""                                   # nada foi gravado
        fluxo.alterar(sm_id, **reprogramacao("p1", ("25/10/2026", "09:00"), ("25/10/2026", "18:00")))   # início = agora
        assert fluxo.doc(sm_id)["p1_hora_inicio"] == "09:00"

    def test_dia_anterior_tambem_e_recusado(self, app, fluxo, relogio):
        sm_id = fluxo.ate(APROVADO)
        relogio.definir(datetime(2026, 10, 25, 0, 30))
        with pytest.raises(app.DocLibValidacaoSM, match="período passado"):
            fluxo.alterar(sm_id, **reprogramacao("p1", ("24/10/2026", "23:59"), ("25/10/2026", "18:00")))

    def test_reprogramacao_futura_e_aceita(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)                                                       # agora: 24/10/2026 10:00
        fluxo.alterar(sm_id, **reprogramacao("p1", ("26/10/2026", "09:00"), ("26/10/2026", "18:00")))
        assert fluxo.doc(sm_id)["p1_data_inicio"] == "26/10/2026"

    def test_campos_apontados_sao_os_do_inicio(self, app, fluxo, relogio):
        sm_id = fluxo.ate(APROVADO)
        relogio.definir(datetime(2026, 10, 25, 9, 0))
        dados = app.doc_lib_normalizar_sm(dict(fluxo.doc(sm_id), **reprogramacao("p1", ("25/10/2026", "08:00"),
                                                                                 ("25/10/2026", "18:00"))))
        erros = app.doc_lib_validar_sm(dados, fluxo.doc(sm_id))
        assert [chaves for chaves, _ in erros] == [("p1_data_inicio", "p1_hora_inicio")]

    def test_a_programacao_original_nao_passa_por_estas_regras(self, app, fluxo, relogio):
        """Só a Reprogramação tem regra de tempo: uma SM nova pode ser programada para qualquer data (a programação de 25/10
        continua válida com o relógio em dezembro)."""
        relogio.definir(datetime(2026, 12, 1, 9, 0))
        sm_id = fluxo.salvar()
        assert fluxo.doc(sm_id)["p0_data_inicio"] == "25/10/2026"


# ======================================================================================================================
# Reprogramação: período em vigor vencido há mais de 6 horas
# ======================================================================================================================
class TestReprogramacaoComPeriodoVencido:
    def test_seis_horas_depois_do_termino_e_aceito_e_um_minuto_a_mais_nao(self, app, fluxo, relogio):
        """Programação até 25/10/2026 17:00: com o relógio às 23:00 (exatamente 6 horas) a reprogramação é aceita."""
        sm_id = fluxo.ate(APROVADO)
        relogio.definir(datetime(2026, 10, 25, 23, 1))
        with pytest.raises(app.DocLibValidacaoSM) as erro:
            fluxo.alterar(sm_id, **reprogramacao("p1", ("26/10/2026", "08:00"), ("26/10/2026", "12:00")))
        texto = str(erro.value)
        assert "Reprogramação-1" in texto and "mais de 6 horas" in texto
        assert "terminou em 25/10/2026 17:00" in texto and "(até 25/10/2026 23:00)" in texto
        assert fluxo.doc(sm_id)["p1_data_inicio"] == ""
        relogio.definir(datetime(2026, 10, 25, 23, 0))
        fluxo.alterar(sm_id, **reprogramacao("p1", ("26/10/2026", "08:00"), ("26/10/2026", "12:00")))
        assert fluxo.doc(sm_id)["p1_hora_termino"] == "12:00"

    def test_vencido_atravessando_a_meia_noite(self, app, fluxo, relogio):
        sm_id = fluxo.ate(APROVADO)
        relogio.definir(datetime(2026, 10, 26, 0, 0))                                      # 7 horas depois de 25/10 17:00
        with pytest.raises(app.DocLibValidacaoSM, match="mais de 6 horas"):
            fluxo.alterar(sm_id, **reprogramacao("p1", ("26/10/2026", "08:00"), ("26/10/2026", "12:00")))

    def test_vencido_e_inicio_no_passado_sao_apontados_juntos(self, app, fluxo, relogio):
        sm_id = fluxo.ate(APROVADO)
        relogio.definir(datetime(2026, 10, 26, 8, 0))
        dados = app.doc_lib_normalizar_sm(dict(fluxo.doc(sm_id), **reprogramacao("p1", ("26/10/2026", "07:00"),
                                                                                 ("26/10/2026", "12:00"))))
        erros = app.doc_lib_validar_sm(dados, fluxo.doc(sm_id))
        chaves = [chaves for chaves, _ in erros]
        assert ("p1_data_inicio", "p1_hora_inicio", "p1_data_termino", "p1_hora_termino") in chaves   # período vencido
        assert ("p1_data_inicio", "p1_hora_inicio") in chaves                                         # início no passado

    def test_o_periodo_em_vigor_de_uma_reprogramacao_e_o_da_reprogramacao_anterior(self, app, fluxo, relogio):
        """A Reprogramação-2 é medida pelo término da Reprogramação-1 (o período em vigor), e não pelo da Programação."""
        sm_id = fluxo.ate(APROVADO)
        fluxo.alterar(sm_id, **reprogramacao("p1", ("26/10/2026", "09:00"), ("26/10/2026", "12:00")))
        relogio.definir(datetime(2026, 10, 26, 18, 1))                                     # 6h01 depois de 26/10 12:00
        with pytest.raises(app.DocLibValidacaoSM) as erro:
            fluxo.alterar(sm_id, **reprogramacao("p2", ("26/10/2026", "19:00"), ("26/10/2026", "23:00")))
        assert "Reprogramação-2" in str(erro.value) and "(Reprogramação-1) terminou em 26/10/2026 12:00" in str(erro.value)
        relogio.definir(datetime(2026, 10, 26, 18, 0))
        fluxo.alterar(sm_id, **reprogramacao("p2", ("26/10/2026", "19:00"), ("26/10/2026", "23:00")))
        assert fluxo.doc(sm_id)["reprogramacoes"] == 2 and fluxo.doc(sm_id)["p2_hora_termino"] == "23:00"

    def test_reprogramacao_antecipando_o_periodo_tambem_usa_o_termino_em_vigor(self, app, fluxo, relogio):
        """Vencimento é do período que está em vigor, ainda que a reprogramação nova comece antes do término dele."""
        sm_id = fluxo.ate(APROVADO)
        relogio.definir(datetime(2026, 10, 25, 12, 0))                                     # Programação ainda em curso
        fluxo.alterar(sm_id, **reprogramacao("p1", ("25/10/2026", "13:00"), ("25/10/2026", "15:00")))
        assert fluxo.doc(sm_id)["p1_hora_inicio"] == "13:00"


# ======================================================================================================================
# Reprogramação já salva não é conferida de novo
# ======================================================================================================================
class TestReprogramacaoSalvaNaoEhConferidaDeNovo:
    def test_outras_gravacoes_continuam_aceitas_depois_que_o_tempo_passa(self, app, fluxo, relogio):
        sm_id = fluxo.ate(APROVADO)
        fluxo.alterar(sm_id, **reprogramacao("p1", ("26/10/2026", "09:00"), ("26/10/2026", "12:00")))
        relogio.definir(datetime(2026, 12, 1, 9, 0))                                       # semanas depois: tudo vencido
        fluxo.conferir(sm_id, fluxo.conferencia_manual(nome="Maria da Manutencao"))        # grava a SM com a reprogramação salva
        doc = fluxo.doc(sm_id)
        assert len(doc["conferencias"]) == 3 and doc["p1_data_inicio"] == "26/10/2026"

    def test_validar_a_sm_gravada_nao_aplica_as_regras_de_tempo(self, app, fluxo, relogio):
        sm_id = fluxo.ate(APROVADO)
        fluxo.alterar(sm_id, **reprogramacao("p1", ("26/10/2026", "09:00"), ("26/10/2026", "12:00")))
        relogio.definir(datetime(2027, 1, 10, 9, 0))
        doc = fluxo.doc(sm_id)
        assert app.doc_lib_validar_sm(doc, doc) == []
        assert app.doc_lib_erros_geracao_sm(doc) == []


# ======================================================================================================================
# Tela: botão Habilitar e marcação dos campos
# ======================================================================================================================
class TestReprogramacaoPelaJanela:
    def test_habilitar_com_periodo_vencido_ha_mais_de_6_horas_avisa_e_nao_habilita(self, app, banco, janelas, fluxo, mensagens,
                                                                                    relogio):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(APROVADO)))
        relogio.definir(datetime(2026, 10, 25, 23, 1))
        janela.habilitar_reprogramacao("p1")
        assert janela.reprogramacoes_habilitadas == 0 and travado(janela.periodo["p1"]["data_inicio"])
        titulo, texto = mensagens.avisos[-1]
        assert titulo == "Reprogramação não permitida" and "mais de 6 horas" in texto and "25/10/2026 17:00" in texto

    def test_habilitar_dentro_das_6_horas_funciona(self, app, banco, janelas, fluxo, mensagens, relogio):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(APROVADO)))
        relogio.definir(datetime(2026, 10, 25, 23, 0))
        janela.habilitar_reprogramacao("p1")
        assert janela.reprogramacoes_habilitadas == 1 and not travado(janela.periodo["p1"]["data_inicio"])
        assert not mensagens.avisos

    def test_inicio_no_passado_e_recusado_ao_salvar_e_marcado_em_vermelho(self, app, banco, janelas, fluxo, mensagens, relogio):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(APROVADO)))
        relogio.definir(datetime(2026, 10, 25, 9, 0))
        janela.habilitar_reprogramacao("p1")
        preencher_reprogramacao(app, janela, "p1", ("25/10/2026", "08:00"), ("25/10/2026", "18:00"))
        janela.salvar()
        assert "período passado" in mensagens.avisos[-1][1]
        p1 = janela.periodo["p1"]
        assert str(p1["hora_inicio"].cget("highlightbackground")) == app.SGA_VERMELHO
        assert str(p1["hora_termino"].cget("highlightbackground")) != app.SGA_VERMELHO
        assert app.doc_lib_carregar_sm(janela.sm_id)["p1_data_inicio"] == ""
        definir(app, p1["hora_inicio"], "09:00")                                           # corrigido: grava
        janela.salvar()
        assert app.doc_lib_carregar_sm(janela.sm_id)["p1_hora_inicio"] == "09:00"


# ======================================================================================================================
# Manobras de Liberação: no máximo 3 horas depois do início programado
# ======================================================================================================================
class TestLiberacaoNoMaximo3HorasDepoisDoInicio:
    def test_tres_horas_depois_do_inicio_e_aceito_e_um_minuto_a_mais_nao(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)                                                        # programação: 25/10/2026 08:00
        fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("25/10/2026", "11:00")))
        assert fluxo.doc(sm_id)["liberacao"][0]["hora"] == "11:00"
        with pytest.raises(app.DocLibValidacaoSM) as erro:
            fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("25/10/2026", "11:01")))
        texto = str(erro.value)
        assert "linha 1 (sequência 1A)" in texto and "posteriores a 3 horas do início programado (25/10/2026 08:00)" in texto
        assert "último horário permitido é 25/10/2026 11:00" in texto
        assert fluxo.doc(sm_id)["liberacao"][0]["hora"] == "11:00"                         # nada foi gravado

    def test_exemplo_10_10_2026_14h_janela_de_11h_ate_17h(self, app, fluxo):
        sm_id = fluxo.salvar(p0_data_inicio="10/10/2026", p0_hora_inicio="14:00", p0_data_termino="10/10/2026",
                             p0_hora_termino="20:00")
        fluxo.gerar(sm_id)
        fluxo.aprovar(sm_id)
        casos = ((("10/10/2026", "10:59"), False), (("10/10/2026", "11:00"), True), (("10/10/2026", "14:00"), True),
                 (("10/10/2026", "17:00"), True), (("10/10/2026", "17:01"), False), (("11/10/2026", "14:00"), False))
        for momento, aceito in casos:
            if aceito:
                fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, momento))
                assert fluxo.doc(sm_id)["liberacao"][0]["hora"] == momento[1]
            else:
                with pytest.raises(app.DocLibValidacaoSM, match="3 horas do início programado"):
                    fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, momento))

    def test_o_limite_atravessa_a_meia_noite(self, app, fluxo):
        sm_id = fluxo.salvar(p0_data_inicio="25/10/2026", p0_hora_inicio="22:00", p0_data_termino="26/10/2026",
                             p0_hora_termino="06:00")
        fluxo.gerar(sm_id)
        fluxo.aprovar(sm_id)
        fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("26/10/2026", "01:00")))
        with pytest.raises(app.DocLibValidacaoSM, match="posteriores a 3 horas do início programado"):
            fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("26/10/2026", "01:01")))

    def test_o_limite_inferior_de_3_horas_antes_continua_valendo(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        with pytest.raises(app.DocLibValidacaoSM, match="anteriores a 3 horas do início programado"):
            fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("25/10/2026", "04:59")))
        fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("25/10/2026", "05:00")))

    def test_so_a_linha_fora_da_janela_e_apontada(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        dados = app.doc_lib_normalizar_sm(dict(fluxo.doc(sm_id), liberacao=liberacao_em(
            fluxo, sm_id, ("25/10/2026", "08:00"), ("25/10/2026", "09:00"), ("25/10/2026", "11:30"))))   # em ordem crescente
        erros = app.doc_lib_validar_sm(dados, fluxo.doc(sm_id))
        assert [chaves for chaves, _ in erros] == [("lib:3:data", "lib:3:hora")]

    def test_vale_o_inicio_do_periodo_em_vigor_depois_de_uma_reprogramacao(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        reprogramada = reprogramacao("p1", ("26/10/2026", "14:00"), ("26/10/2026", "20:00"))
        with pytest.raises(app.DocLibValidacaoSM, match=r"posteriores a 3 horas do início programado \(26/10/2026 14:00\)"):
            fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("26/10/2026", "17:01")), **reprogramada)
        fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("26/10/2026", "17:00")), **reprogramada)
        assert fluxo.doc(sm_id)["liberacao"][0]["hora"] == "17:00"

    def test_reprogramar_para_mais_cedo_com_a_liberacao_ja_lancada_exige_corrigir_as_manobras(self, app, fluxo):
        """Manobra lançada às 08:00; ao reprogramar o início para 25/10 04:00 o limite passa a ser 07:00: a gravação é recusada
        até a manobra ser corrigida na mesma gravação."""
        sm_id = fluxo.ate(APROVADO)
        fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("25/10/2026", "08:00")))
        reprogramada = reprogramacao("p1", ("25/10/2026", "04:00"), ("25/10/2026", "12:00"))
        with pytest.raises(app.DocLibValidacaoSM, match=r"posteriores a 3 horas do início programado \(25/10/2026 04:00\)"):
            fluxo.alterar(sm_id, **reprogramada)
        fluxo.alterar(sm_id, liberacao=liberacao_em(fluxo, sm_id, ("25/10/2026", "06:30")), **reprogramada)
        assert fluxo.doc(sm_id)["p1_hora_inicio"] == "04:00"

    def test_regra_nao_vale_para_a_normalizacao_nem_depois_de_registrada_a_liberacao(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)                                                     # liberação 25/10 08:00 a 08:20
        normalizacao = [dict(m, data="25/10/2026", hora=f"22:{indice * 10:02d}")
                        for indice, m in enumerate(fluxo.doc(sm_id)["normalizacao"])]
        fluxo.alterar(sm_id, normalizacao=normalizacao)                                    # 14 horas depois do início: aceito
        assert fluxo.doc(sm_id)["normalizacao"][0]["hora"] == "22:00"

    def test_a_tela_recusa_marca_o_campo_e_aceita_no_limite(self, app, banco, janelas, fluxo, mensagens):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(APROVADO)))                         # programação: 25/10/2026 08:00
        for indice, hora in enumerate(("11:01", "11:00")):                                 # 1A e 1B (a 3ª linha fica sem horário)
            definir(app, janela.tab_lib.linhas[indice]["data"], "25/10/2026")
            definir(app, janela.tab_lib.linhas[indice]["hora"], hora)
        janela.salvar()
        texto = mensagens.avisos[-1][1]
        assert "linha 1 (sequência 1A)" in texto and "posteriores a 3 horas do início programado (25/10/2026 08:00)" in texto
        assert "linha 2" not in texto and "linha 3" not in texto
        assert str(janela.tab_lib.linhas[0]["hora"].cget("highlightbackground")) == app.SGA_VERMELHO
        assert str(janela.tab_lib.linhas[1]["hora"].cget("highlightbackground")) != app.SGA_VERMELHO
        definir(app, janela.tab_lib.linhas[0]["hora"], "11:00")                            # no limite: aceita
        janela.salvar()
        assert fluxo.doc(janela.sm_id)["liberacao"][0]["hora"] == "11:00"
