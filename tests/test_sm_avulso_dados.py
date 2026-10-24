"""SM Avulso (Doc_Lib. - Click_25): numeração, reserva, validações, status, conferência, persistência e triggers."""
import concurrent.futures
import copy
import sqlite3
from datetime import datetime

import pytest

EM_ANALISE, AGUARDA, APROVADO = "Em análise", "Aguarda Conferência", "Aprovado para Execução"
EM_EXECUCAO, CONCLUIDO, CANCELADO, RESERVADO = "Em Execução", "Concluído", "Cancelado", "Reservado"


def numeros(app):
    conexao = app.doc_lib_conectar()
    try:
        return [linha[0] for linha in conexao.execute("SELECT numero FROM doclib_sm ORDER BY id")]
    finally:
        conexao.close()


def erros_de(app, fluxo, **alteracoes):
    """Chaves dos campos apontados pela validação dos dados (None = sem erros)."""
    # o Elaborado por (nome e Ass.) é preenchido pelo usuário autenticado ao salvar; a janela os envia na validação
    dados = app.doc_lib_normalizar_sm(fluxo.dados(**dict({"elaborado_por": "Operador Um", "elaborado_ass": "operador1"},
                                                         **alteracoes)))
    return [chaves for chaves, _ in app.doc_lib_validar_sm(dados, None)]


# ======================================================================================================================
# Numeração e reserva
# ======================================================================================================================
class TestNumeracao:
    def test_numero_previsto_so_e_consumido_ao_salvar(self, app, fluxo):
        assert app.doc_lib_numeros_previstos(1, "SM") == ["0001/26"]
        assert app.doc_lib_numeros_previstos(1, "SM") == ["0001/26"]          # abrir a janela não consome
        sm_id = fluxo.salvar()
        assert fluxo.doc(sm_id)["numero"] == "0001/26"
        assert app.doc_lib_numeros_previstos(1, "SM") == ["0002/26"]

    def test_varios_documentos_em_sequencia_crescente(self, app, fluxo):
        for _ in range(5):
            fluxo.salvar()
        assert numeros(app) == ["0001/26", "0002/26", "0003/26", "0004/26", "0005/26"]

    def test_numero_permanece_apos_alteracoes_e_mudancas_de_status(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.alterar(sm_id, motivo="Outro motivo")
        fluxo.gerar(sm_id)
        fluxo.aprovar(sm_id)
        fluxo.executar(sm_id)
        fluxo.concluir(sm_id)
        assert fluxo.doc(sm_id)["numero"] == "0001/26"

    def test_reinicio_anual_da_numeracao(self, app, fluxo, monkeypatch):
        fluxo.salvar()
        fluxo.salvar()

        class Em2027(datetime):
            @classmethod
            def now(cls, tz=None):
                return datetime(2027, 1, 4, 9, 30)

        monkeypatch.setattr(app, "datetime", Em2027)
        assert app.doc_lib_numeros_previstos(1, "SM") == ["0001/27"]
        fluxo.salvar()
        fluxo.salvar()
        assert numeros(app) == ["0001/26", "0002/26", "0001/27", "0002/27"]

    def test_reserva_usa_a_sequencia_do_ano_e_o_proximo_documento_segue(self, app, fluxo):
        fluxo.salvar()
        reservados = app.doc_lib_reservar_sm(3, "operador1", "Operador Um")
        assert [item["numero"] for item in reservados] == ["0002/26", "0003/26", "0004/26"]
        assert all(fluxo.doc(item["ateie_id"])["status"] == RESERVADO for item in reservados)
        fluxo.salvar()
        assert numeros(app)[-1] == "0005/26"

    @pytest.mark.parametrize("quantidade", [0, 11, -1, "x", ""])
    def test_reserva_com_quantidade_invalida_nao_consome_numero(self, app, fluxo, quantidade):
        with pytest.raises(app.DocLibRegra):
            app.doc_lib_reservar_sm(quantidade, "operador1")
        assert app.doc_lib_numeros_previstos(1, "SM") == ["0001/26"]

    def test_reservada_preenchida_mantem_o_numero_e_vira_em_analise(self, app, fluxo):
        reservado = app.doc_lib_reservar_sm(1, "operador1", "Operador Um")[0]
        doc = fluxo.doc(reservado["ateie_id"])
        dados = fluxo.dados(id=doc["id"], revisao=doc["revisao"])
        sm_id = app.doc_lib_salvar_sm(dados, "operador2")
        doc = fluxo.doc(sm_id)
        assert (doc["numero"], doc["status"], doc["reservado_por"], doc["elaborado_ass"]) == \
            ("0001/26", EM_ANALISE, "operador1", "operador2")

    def test_numero_cancelado_nao_e_reaproveitado(self, app, fluxo):
        sm_id = fluxo.salvar()
        app.doc_lib_cancelar_sm(sm_id, "operador1", "Teste", fluxo.doc(sm_id)["revisao"])
        fluxo.salvar()
        assert numeros(app) == ["0001/26", "0002/26"]

    def test_criacao_simultanea_nao_duplica_numeros(self, app, fluxo):
        dados = [fluxo.dados() for _ in range(16)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            ids = list(executor.map(lambda item: app.doc_lib_salvar_sm(item, "operador1"), dados))
        assert len(set(ids)) == 16
        assert sorted(numeros(app)) == [f"{n:04d}/26" for n in range(1, 17)]

    def test_reserva_simultanea_nao_duplica_numeros(self, app, fluxo):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            blocos = list(executor.map(lambda _: app.doc_lib_reservar_sm(3, "operador1"), range(6)))
        todos = [item["numero"] for bloco in blocos for item in bloco]
        assert sorted(todos) == [f"{n:04d}/26" for n in range(1, 19)]

    def test_falha_ao_salvar_nao_consome_numero_nem_grava_parcial(self, app, fluxo, monkeypatch):
        def falha(*args, **kwargs):
            raise sqlite3.OperationalError("disco cheio (simulado)")
        with monkeypatch.context() as contexto:
            contexto.setattr(app, "_doc_lib_gravar_filhos_sm", falha)
            with pytest.raises(sqlite3.OperationalError):
                fluxo.salvar()
        assert numeros(app) == []
        assert app.doc_lib_numeros_previstos(1, "SM") == ["0001/26"]


# ======================================================================================================================
# Programação e reprogramações
# ======================================================================================================================
class TestProgramacao:
    def test_programacao_original_e_recuperada(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar())
        assert (doc["p0_data_inicio"], doc["p0_hora_inicio"], doc["p0_data_termino"], doc["p0_hora_termino"]) == \
            ("25/10/2026", "08:00", "25/10/2026", "17:00")
        assert doc["reprogramacoes"] == 0

    def test_formatos_de_data_e_hora_digitados_sao_normalizados(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar(p0_data_inicio="251026", p0_hora_inicio="800", p0_data_termino="26-10-26",
                                     p0_hora_termino="9h15"))
        assert (doc["p0_data_inicio"], doc["p0_hora_inicio"], doc["p0_data_termino"], doc["p0_hora_termino"]) == \
            ("25/10/2026", "08:00", "26/10/2026", "09:15")

    @pytest.mark.parametrize("campo", ["p0_data_inicio", "p0_hora_inicio", "p0_data_termino", "p0_hora_termino"])
    def test_programacao_original_e_obrigatoria(self, app, fluxo, campo):
        assert (campo,) in erros_de(app, fluxo, **{campo: ""})

    @pytest.mark.parametrize("campo,valor", [("p0_data_inicio", "31/02/2026"), ("p0_data_termino", "abc"),
                                             ("p0_hora_inicio", "25:00"), ("p0_hora_termino", "12:60")])
    def test_data_e_hora_invalidas(self, app, fluxo, campo, valor):
        assert (campo,) in erros_de(app, fluxo, **{campo: valor})

    def test_termino_nao_pode_ser_anterior_ao_inicio(self, app, fluxo):
        erros = erros_de(app, fluxo, p0_data_termino="24/10/2026")
        assert ("p0_data_termino", "p0_hora_termino") in erros
        assert erros_de(app, fluxo, p0_data_termino="25/10/2026", p0_hora_inicio="08:00", p0_hora_termino="08:00") == []

    def test_reprogramacao_incompleta_ou_fora_de_ordem(self, app, fluxo):
        assert ("p1_hora_termino",) in erros_de(app, fluxo, p1_data_inicio="26/10/2026", p1_hora_inicio="08:00",
                                                p1_data_termino="26/10/2026")
        erros = erros_de(app, fluxo, p2_data_inicio="27/10/2026", p2_hora_inicio="08:00", p2_data_termino="27/10/2026",
                         p2_hora_termino="17:00")
        assert any("p2_data_inicio" in chaves for chaves in erros)           # a 2 exige a 1 completa

    def test_habilitacao_sequencial_persiste_e_preserva_as_anteriores(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.gerar(sm_id)
        fluxo.alterar(sm_id, p1_data_inicio="26/10/2026", p1_hora_inicio="08:00", p1_data_termino="26/10/2026",
                      p1_hora_termino="17:00", reprogramacoes=1)
        fluxo.alterar(sm_id, p2_data_inicio="27/10/2026", p2_hora_inicio="09:00", p2_data_termino="27/10/2026",
                      p2_hora_termino="18:00", reprogramacoes=2)
        doc = fluxo.doc(sm_id)
        assert doc["reprogramacoes"] == 2
        assert (doc["p0_data_inicio"], doc["p1_data_inicio"], doc["p2_data_inicio"], doc["p3_data_inicio"]) == \
            ("25/10/2026", "26/10/2026", "27/10/2026", "")

    def test_reprogramacao_habilitada_e_vazia_e_lembrada(self, app, fluxo):
        sm_id = fluxo.salvar(reprogramacoes=1)
        assert fluxo.doc(sm_id)["reprogramacoes"] == 1

    def test_programacao_original_fica_protegida_depois_da_emissao(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.gerar(sm_id)
        with pytest.raises(app.DocLibBloqueado, match="edição geral"):
            fluxo.alterar(sm_id, p0_data_inicio="30/10/2026", p0_data_termino="30/10/2026")

    def test_reprogramacao_vale_ate_a_conclusao(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        fluxo.alterar(sm_id, p1_data_inicio="26/10/2026", p1_hora_inicio="08:00", p1_data_termino="26/10/2026",
                      p1_hora_termino="19:00", reprogramacoes=1)
        assert fluxo.doc(sm_id)["status"] == EM_EXECUCAO
        fluxo.concluir(sm_id)
        with pytest.raises(app.DocLibBloqueado):
            fluxo.alterar(sm_id, p1_hora_termino="20:00")


# ======================================================================================================================
# Equipamentos, motivo, condições de segurança e observações
# ======================================================================================================================
class TestCamposObrigatorios:
    @pytest.mark.parametrize("campo", ["cond_chaves_abertas", "cond_chaves_fechadas", "cond_disjuntores", "cond_loto_com",
                                       "cond_loto_sem"])
    @pytest.mark.parametrize("valor", ["", "   ", "\n \n"])
    def test_condicao_de_seguranca_em_branco_e_recusada(self, app, fluxo, campo, valor):
        assert (campo,) in erros_de(app, fluxo, **{campo: valor})
        with pytest.raises(app.DocLibValidacaoSM):
            fluxo.salvar(**{campo: valor})
        assert numeros(app) == []                                    # nada gravado, número não consumido

    def test_condicoes_aceitam_texto_livre_e_sao_recuperadas(self, app, fluxo):
        texto = "89-1\n89-2\n89-3"
        doc = fluxo.doc(fluxo.salvar(cond_chaves_abertas=texto, cond_loto_sem="Nenhuma"))
        assert doc["cond_chaves_abertas"] == texto and doc["cond_loto_sem"] == "Nenhuma"

    def test_banco_recusa_condicao_em_branco_mesmo_sem_passar_pelo_aplicativo(self, app, fluxo):
        sm_id = fluxo.salvar()
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.IntegrityError):
            conexao.execute("UPDATE doclib_sm SET cond_disjuntores = '  ' WHERE id = ?", (sm_id,))
        with pytest.raises(sqlite3.IntegrityError):
            conexao.execute("INSERT INTO doclib_sm (numero, ano, sequencia, status) VALUES ('0099/26', 2026, 99, 'Em análise')")
        conexao.close()

    def test_primeira_linha_de_equipamento_e_obrigatoria(self, app, fluxo):
        erros = erros_de(app, fluxo, equipamentos=[])
        assert {f"equip:1:{campo}" for campo in ("local", "instalacao", "equipamento", "caracterizacao", "local_execucao",
                                                 "tempo_retorno")} <= {chave for chaves in erros for chave in chaves}

    def test_linha_parcial_de_equipamento_e_recusada_e_vazia_e_aceita(self, app, fluxo):
        primeira = fluxo.dados()["equipamentos"][0]
        erros = erros_de(app, fluxo, equipamentos=[primeira, {"local": "SE IGU"}])
        assert ("equip:2:instalacao",) in erros and ("equip:2:tempo_retorno",) in erros
        assert erros_de(app, fluxo, equipamentos=[primeira, {}, {}]) == []

    def test_tres_linhas_de_equipamento_sao_persistidas_na_ordem(self, app, fluxo):
        linhas = [{"local": f"L{i}", "instalacao": f"I{i}", "equipamento": f"E{i}", "caracterizacao": f"C{i}",
                   "local_execucao": f"X{i}", "tempo_retorno": f"0{i}:15"} for i in (1, 2, 3)]
        doc = fluxo.doc(fluxo.salvar(equipamentos=linhas))
        assert [(item["local"], item["tempo_retorno"]) for item in doc["equipamentos"]] == \
            [("L1", "01:15"), ("L2", "02:15"), ("L3", "03:15")]

    @pytest.mark.parametrize("texto,esperado", [("1:30", "01:30"), ("0130", "01:30"), ("1h30", "01:30"), ("00:45", "00:45"),
                                                ("99:59", "99:59"), (" 2:05 ", "02:05")])
    def test_tempo_de_retorno_valido_vira_hh_mm(self, app, texto, esperado):
        assert app.doc_lib_normalizar_duracao_sm(texto) == esperado

    @pytest.mark.parametrize("texto", ["", "abc", "1:7", "130", "1:60", "100:00", "12:5", "-1:00", "1:30:00", "１２:30"])
    def test_tempo_de_retorno_invalido(self, app, fluxo, texto):
        assert app.doc_lib_normalizar_duracao_sm(texto) is None
        item = dict(fluxo.dados()["equipamentos"][0], tempo_retorno=texto)
        assert ("equip:1:tempo_retorno",) in erros_de(app, fluxo, equipamentos=[item])

    def test_motivo_obrigatorio_e_limitado_a_seis_linhas(self, app, fluxo):
        assert ("motivo",) in erros_de(app, fluxo, motivo="  ")
        assert erros_de(app, fluxo, motivo="\n".join(f"linha {i}" for i in range(1, 7))) == []
        assert ("motivo",) in erros_de(app, fluxo, motivo="\n".join(f"linha {i}" for i in range(1, 8)))

    def test_motivo_longo_que_quebra_alem_de_seis_linhas_e_recusado(self, app, fluxo):
        assert ("motivo",) in erros_de(app, fluxo, motivo="palavra " * 400)
        assert app.doc_lib_linhas_texto_sm("palavra " * 50) <= 6
        assert erros_de(app, fluxo, motivo="palavra " * 50) == []

    def test_motivo_e_observacoes_preservam_quebras(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar(motivo="a\nb\n\nc", observacoes="x\ny\nz"))
        assert doc["motivo"] == "a\nb\n\nc" and doc["observacoes"] == "x\ny\nz"

    def test_elaborador_e_do_usuario_autenticado_mesmo_com_dados_forjados(self, app, fluxo):
        sm_id = fluxo.salvar(elaborado_por="Outra Pessoa", elaborado_ass="outro_login")
        doc = fluxo.doc(sm_id)
        assert (doc["elaborado_ass"], doc["elaborado_por"]) == ("operador1", "operador1")      # sem nome completo cadastrado
        assert (doc["elaborado_area"], doc["elaborado_data"]) == ("COG", "24/10/2026")

    def test_elaborador_usa_o_nome_completo_cadastrado(self, app, fluxo):
        conexao = app.doc_lib_conectar()
        conexao.execute("CREATE TABLE IF NOT EXISTS Usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT, admin INTEGER, "
                        "primeiro_acesso INTEGER, nome_completo TEXT)")
        conexao.execute("INSERT INTO Usuarios (usuario, senha, admin, primeiro_acesso, nome_completo) "
                        "VALUES ('operador1', 'x', 0, 0, 'Operador de Teste Um')")
        conexao.commit()
        conexao.close()
        doc = fluxo.doc(fluxo.salvar())
        assert (doc["elaborado_por"], doc["elaborado_ass"]) == ("Operador de Teste Um", "operador1")

    def test_area_e_data_do_elaborador_sao_obrigatorias(self, app, fluxo):
        assert ("elaborado_area",) in erros_de(app, fluxo, elaborado_area="")
        assert ("elaborado_data",) in erros_de(app, fluxo, elaborado_data="")
        assert ("elaborado_data",) in erros_de(app, fluxo, elaborado_data="99/99/2026")


# ======================================================================================================================
# Manobras de liberação e de normalização
# ======================================================================================================================
class TestManobras:
    def test_sequencia_do_exemplo_do_enunciado(self, app):
        assert app.doc_lib_identificar_sequencias_sm([1, 1, 1, 2, 3, 3, 4]) == ["1A", "1B", "1C", "2A", "3A", "3B", "4A"]

    def test_numero_repetido_depois_de_outro_continua_a_contagem(self, app):
        assert app.doc_lib_identificar_sequencias_sm(["1", "2", "1", "2", "1"]) == ["1A", "2A", "1B", "2B", "1C"]

    def test_linha_sem_numero_valido_nao_recebe_letra_nem_conta(self, app):
        assert app.doc_lib_identificar_sequencias_sm(["", "1", "x", "0", "100", "1"]) == ["", "1A", "", "", "", "1B"]

    def test_letras_passam_de_z_ate_o_limite_de_30(self, app):
        letras = app.doc_lib_identificar_sequencias_sm(["7"] * 30)
        assert letras[0] == "7A" and letras[25] == "7Z" and letras[26] == "7AA" and letras[29] == "7AD"
        assert len(set(letras)) == 30

    def test_letras_acompanham_inclusao_exclusao_e_troca_de_ordem(self, app):
        base = ["1", "1", "2"]
        assert app.doc_lib_identificar_sequencias_sm(base) == ["1A", "1B", "2A"]
        assert app.doc_lib_identificar_sequencias_sm(["1"] + base) == ["1A", "1B", "1C", "2A"]            # inclusão
        assert app.doc_lib_identificar_sequencias_sm(base[1:]) == ["1A", "2A"]                             # exclusão
        assert app.doc_lib_identificar_sequencias_sm(["2", "1", "1"]) == ["2A", "1A", "1B"]               # nova ordem

    def test_identificacao_recuperada_ao_reabrir(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar())
        assert [m["identificacao"] for m in doc["liberacao"]] == ["1A", "1B", "2A"]
        assert [m["identificacao"] for m in doc["normalizacao"]] == ["1A", "2A", "2B"]

    def test_limite_de_30_linhas(self, app, fluxo):
        trinta = [{"numero": str(i), "local": "SE", "acao": f"Abrir {i}"} for i in range(1, 31)]
        doc = fluxo.doc(fluxo.salvar(liberacao=trinta, normalizacao=trinta))
        assert len(doc["liberacao"]) == 30 and len(doc["normalizacao"]) == 30
        trinta_e_uma = trinta + [{"numero": "31", "local": "SE", "acao": "Abrir 31"}]
        assert any("máximo 30" in mensagem for _, mensagem in app.doc_lib_validar_sm(
            app.doc_lib_normalizar_sm(fluxo.dados(liberacao=trinta_e_uma)), None))
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.IntegrityError):                                   # o banco também recusa a 31ª
            conexao.execute("INSERT INTO doclib_sm_manobras (sm_id, tipo, ordem) VALUES (1, 'L', 31)")
        conexao.close()

    def test_exige_ao_menos_uma_manobra_em_cada_tabela(self, app, fluxo):
        assert ("lib:1:acao",) in erros_de(app, fluxo, liberacao=[])
        assert ("nor:1:acao",) in erros_de(app, fluxo, normalizacao=[{}])

    def test_linhas_totalmente_vazias_sao_descartadas(self, app, fluxo):
        vazia = {"numero": "", "local": "", "acao": ""}
        liberacao = [vazia] + fluxo.dados()["liberacao"] + [vazia]
        assert len(fluxo.doc(fluxo.salvar(liberacao=liberacao))["liberacao"]) == 3

    @pytest.mark.parametrize("campo,valor,chave", [("numero", "", "numero"), ("numero", "0", "numero"), ("numero", "100", "numero"),
                                                   ("numero", "1a", "numero"), ("local", "", "local"),
                                                   ("local", "1234567", "local"), ("acao", "  ", "acao")])
    def test_linha_de_manobra_invalida(self, app, fluxo, campo, valor, chave):
        linha = dict(fluxo.dados()["liberacao"][0], **{campo: valor})
        assert (f"lib:1:{chave}",) in erros_de(app, fluxo, liberacao=[linha])

    def test_local_aceita_exatamente_seis_caracteres(self, app, fluxo):
        linha = dict(fluxo.dados()["liberacao"][0], local="SE MCP")
        assert len(linha["local"]) == 6 and erros_de(app, fluxo, liberacao=[linha]) == []

    def test_banco_recusa_local_com_mais_de_seis_caracteres(self, app, fluxo):
        sm_id = fluxo.salvar()
        conexao = app.doc_lib_conectar()
        with pytest.raises(sqlite3.IntegrityError):
            conexao.execute("UPDATE doclib_sm_manobras SET local = 'SE MCP1' WHERE sm_id = ?", (sm_id,))
        conexao.close()

    def test_acao_longa_e_multilinha_e_preservada(self, app, fluxo):
        acao = "Abrir o disjuntor 52-1 " * 12 + "\nSegunda linha"
        doc = fluxo.doc(fluxo.salvar(liberacao=[{"numero": "1", "local": "SE", "acao": acao}]))
        assert doc["liberacao"][0]["acao"] == acao.strip()

    def test_data_e_hora_das_manobras_so_depois_da_conferencia(self, app, fluxo):
        sm_id = fluxo.salvar()
        liberacao = fluxo.datar(fluxo.doc(sm_id), "liberacao")
        with pytest.raises(app.DocLibBloqueado):                                # Em análise
            fluxo.alterar(sm_id, liberacao=liberacao)
        fluxo.gerar(sm_id)
        with pytest.raises(app.DocLibBloqueado):                                # Aguarda Conferência
            fluxo.alterar(sm_id, liberacao=liberacao)
        fluxo.aprovar(sm_id)
        fluxo.alterar(sm_id, liberacao=liberacao[:2] + [fluxo.doc(sm_id)["liberacao"][2]])       # Aprovado: aceita
        assert fluxo.doc(sm_id)["liberacao"][0]["hora"] == "08:00"
        with pytest.raises(app.DocLibBloqueado):                                # a normalização só com a SM Em Execução
            fluxo.alterar(sm_id, normalizacao=fluxo.datar(fluxo.doc(sm_id), "normalizacao", 16))

    def test_data_e_hora_exigem_as_duas_e_formato_valido(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        base = fluxo.doc(sm_id)["liberacao"]
        for alteracao in ({"data": "25/10/2026"}, {"hora": "08:00"}):
            with pytest.raises(app.DocLibValidacaoSM):
                fluxo.alterar(sm_id, liberacao=[dict(base[0], **alteracao)] + base[1:])
        with pytest.raises(app.DocLibValidacaoSM):
            fluxo.alterar(sm_id, liberacao=[dict(base[0], data="32/13/2026", hora="08:00")] + base[1:])

    def test_horarios_das_manobras_seguem_a_ordem(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        base = fluxo.doc(sm_id)["liberacao"]
        invertida = [dict(base[0], data="25/10/2026", hora="09:00"), dict(base[1], data="25/10/2026", hora="08:00")] + base[2:]
        with pytest.raises(app.DocLibValidacaoSM, match="não podem ser anteriores"):
            fluxo.alterar(sm_id, liberacao=invertida)

    def test_correcao_de_horario_e_permitida_e_apagar_nao(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        base = fluxo.doc(sm_id)["liberacao"]
        fluxo.alterar(sm_id, liberacao=[dict(base[0], hora="07:55")] + base[1:])
        assert fluxo.doc(sm_id)["liberacao"][0]["hora"] == "07:55"
        with pytest.raises(app.DocLibBloqueado, match="não apagadas"):
            fluxo.alterar(sm_id, liberacao=[dict(base[0], data="", hora="")] + base[1:])
        historico = app.doc_lib_conectar().execute(
            "SELECT descricao FROM doclib_sm_historico WHERE evento = 'data_manobra'").fetchall()
        assert any("corrigidas" in descricao for (descricao,) in historico)


# ======================================================================================================================
# Inversão das manobras
# ======================================================================================================================
class TestInversao:
    @pytest.mark.parametrize("acao,esperada", [
        ("Abrir DJ 52-1", "Fechar DJ 52-1"), ("Fechar DJ 52-1", "Abrir DJ 52-1"),
        ("Bloquear seccionadora 89-1", "Desbloquear seccionadora 89-1"),
        ("Desbloquear seccionadora 89-1", "Bloquear seccionadora 89-1"),
        ("ABRIR DJ 52-1", "FECHAR DJ 52-1"), ("abrir dj 52-1", "fechar dj 52-1"),
        ("Ligar bomba", "Desligar bomba"), ("Desligar bomba", "Ligar bomba"),
        ("Energizar barra 1", "Desenergizar barra 1"), ("Extrair disjuntor 52-1", "Inserir disjuntor 52-1"),
        ("Inserir disjuntor 52-1", "Extrair disjuntor 52-1"), ("Aterrar linha", "Desaterrar linha"),
        ("Habilitar religamento", "Desabilitar religamento"), ("Ativar proteção", "Desativar proteção"),
        ("Conectar cabo", "Desconectar cabo"), ("Travar comporta", "Destravar comporta"),
        ("Abrir a seccionadora 89-1 (campo)", "Fechar a seccionadora 89-1 (campo)")])
    def test_acao_com_antonimo_inequivoco_e_invertida(self, app, acao, esperada):
        assert app.doc_lib_inverter_acao_sm(acao) == (esperada, False)

    @pytest.mark.parametrize("acao", [
        "Abrir e bloquear seccionadora 89-1",          # dois verbos: a ordem das operações também inverteria
        "Colocar em serviço o transformador",           # verbo de sentido duplo
        "Retirar aterramento temporário",
        "Isolar a linha",
        "Verificar DJ 52-1 aberto",                     # verificação + estado descrito
        "Confirmar abertura do DJ 52-1",
        "Não abrir o DJ 52-1",                          # negação
        "Se o DJ estiver fechado, abrir",               # condicional
        "DJ 52-1 aberto e bloqueado",                   # só estado
        "Religar linha",                                # verbo fora da tabela
        "",                                             # sem ação
        "Manter chave 89-1 aberta",
        "Isolar a linha e abrir 89-1",                  # verbo desconhecido junto de um conhecido
        "Abrir DJ 52-1 para permitir trabalhar",        # outro verbo no infinitivo
        "Chave 89-1: abrir",                            # o verbo conhecido não é a primeira palavra
        "Após isolar a linha, abrir o DJ"])
    def test_acao_ambigua_e_mantida_e_marcada_para_conferencia(self, app, acao):
        assert app.doc_lib_inverter_acao_sm(acao) == (acao, True)

    def test_exemplo_do_enunciado_ordem_inversa_e_sequencia_recalculada(self, app):
        liberacao = [{"numero": str(n), "local": f"L{i}", "acao": f"Abrir equipamento {i}"}
                     for i, n in enumerate([1, 1, 1, 2, 3, 3, 4], start=1)]
        geradas = app.doc_lib_inverter_manobras_sm(liberacao)
        assert [m["acao"] for m in geradas] == [f"Fechar equipamento {i}" for i in range(7, 0, -1)]
        assert [m["local"] for m in geradas] == [f"L{i}" for i in range(7, 0, -1)]
        assert [m["numero"] for m in geradas] == ["1", "2", "2", "3", "4", "4", "4"]
        assert app.doc_lib_identificar_sequencias_sm([m["numero"] for m in geradas]) == \
            ["1A", "2A", "2B", "3A", "4A", "4B", "4C"]
        assert all(m["data"] == "" and m["hora"] == "" and m["conferir"] == 0 for m in geradas)

    def test_nao_altera_as_manobras_de_liberacao(self, app):
        liberacao = [{"numero": "1", "local": "SE", "acao": "Abrir DJ", "data": "25/10/2026", "hora": "08:00", "conferir": 0},
                     {"numero": "2", "local": "SE", "acao": "Isolar linha", "data": "", "hora": "", "conferir": 0}]
        copia = copy.deepcopy(liberacao)
        geradas = app.doc_lib_inverter_manobras_sm(liberacao)
        assert liberacao == copia
        assert geradas[0]["acao"] == "Isolar linha" and geradas[0]["conferir"] == 1             # mantida e sinalizada
        assert geradas[1]["acao"] == "Fechar DJ" and geradas[1]["conferir"] == 0

    def test_tabela_parcialmente_preenchida(self, app):
        liberacao = [{"numero": "1", "local": "SE", "acao": "Abrir DJ"}, {"numero": "", "local": "", "acao": ""},
                     {"numero": "", "local": "SE", "acao": "Bloquear 89-1"}, {"numero": "2", "local": "", "acao": ""}]
        geradas = app.doc_lib_inverter_manobras_sm(liberacao)
        assert len(geradas) == 3                                                    # a linha vazia é ignorada
        assert [m["conferir"] for m in geradas] == [1, 1, 0] and geradas[2]["acao"] == "Fechar DJ"
        assert app.doc_lib_inverter_manobras_sm([]) == []

    def test_sem_numero_valido_a_linha_fica_marcada(self, app):
        geradas = app.doc_lib_inverter_manobras_sm([{"numero": "", "local": "SE", "acao": "Abrir DJ"}])
        assert geradas[0]["numero"] == "" and geradas[0]["conferir"] == 1

    def test_ate_30_manobras(self, app):
        liberacao = [{"numero": str(i % 5 + 1), "local": "SE", "acao": f"Abrir {i}"} for i in range(30)]
        geradas = app.doc_lib_inverter_manobras_sm(liberacao)
        assert len(geradas) == 30 and len(set(app.doc_lib_identificar_sequencias_sm([m["numero"] for m in geradas]))) == 30

    def test_marca_de_conferencia_e_gravada_e_impede_gerar_o_documento(self, app, fluxo):
        normalizacao = [{"numero": "1", "local": "SE", "acao": "Isolar linha", "conferir": 1}]
        sm_id = fluxo.salvar(normalizacao=normalizacao)
        assert fluxo.doc(sm_id)["normalizacao"][0]["conferir"] == 1
        with pytest.raises(app.DocLibValidacaoSM, match="confira a ação"):
            fluxo.gerar(sm_id)
        assert fluxo.doc(sm_id)["status"] == EM_ANALISE
        fluxo.alterar(sm_id, normalizacao=[dict(normalizacao[0], conferir=0)])
        fluxo.gerar(sm_id)
        assert fluxo.doc(sm_id)["status"] == AGUARDA


# ======================================================================================================================
# Status, conferência e execução
# ======================================================================================================================
class TestStatus:
    def test_salvamento_inicial_em_analise(self, app, fluxo):
        doc = fluxo.doc(fluxo.salvar())
        assert (doc["status"], doc["emitido"], doc["revisao"]) == (EM_ANALISE, 0, 1)

    def test_gerar_leva_a_aguarda_conferencia_e_protege_o_documento(self, app, fluxo):
        sm_id = fluxo.salvar()
        fluxo.gerar(sm_id)
        doc = fluxo.doc(sm_id)
        assert (doc["status"], doc["emitido"]) == (AGUARDA, 1)
        with pytest.raises(app.DocLibBloqueado, match="edição geral"):
            fluxo.alterar(sm_id, motivo="Alterado depois de gerado")
        with pytest.raises(app.DocLibBloqueado):
            fluxo.alterar(sm_id, liberacao=fluxo.doc(sm_id)["liberacao"][:1])
        with pytest.raises(app.DocLibBloqueado):
            fluxo.alterar(sm_id, cond_loto_sem="Alterada")

    def test_gerar_de_novo_nao_muda_o_status(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        revisao = fluxo.doc(sm_id)["revisao"]
        fluxo.gerar(sm_id)
        assert fluxo.doc(sm_id)["status"] == APROVADO and fluxo.doc(sm_id)["revisao"] == revisao

    def test_so_a_conferencia_manual_nao_aprova(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        fluxo.conferir(sm_id, fluxo.conferencia_manual())
        doc = fluxo.doc(sm_id)
        assert doc["status"] == AGUARDA and [c["modalidade"] for c in doc["conferencias"]] == ["manual"]

    def test_so_a_conferencia_pelo_sistema_nao_aprova(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        fluxo.conferir(sm_id, fluxo.conferencia_sistema())
        assert fluxo.doc(sm_id)["status"] == AGUARDA

    @pytest.mark.parametrize("ordem", [("manual", "sistema"), ("sistema", "manual")])
    def test_manual_mais_sistema_aprova_em_qualquer_ordem_e_persiste_apos_reabrir(self, app, fluxo, ordem):
        sm_id = fluxo.ate(AGUARDA)
        fluxo.conferir(sm_id, getattr(fluxo, f"conferencia_{ordem[0]}")())
        assert fluxo.doc(sm_id)["status"] == AGUARDA
        fluxo.conferir(sm_id, getattr(fluxo, f"conferencia_{ordem[1]}")())
        doc = fluxo.doc(sm_id)
        assert doc["status"] == APROVADO
        assert [c["modalidade"] for c in doc["conferencias"]] == list(ordem)         # modalidade gravada explicitamente
        assert app.doc_lib_calcular_status_sm(doc, True) == APROVADO                 # o status se recalcula do que está gravado

    def test_conferencia_pelo_sistema_grava_o_usuario_autenticado(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        fluxo.conferir(sm_id, fluxo.conferencia_sistema(nome="Fulano Forjado", ass="forjado"), usuario="operador7")
        conferencia = fluxo.doc(sm_id)["conferencias"][0]
        assert (conferencia["nome"], conferencia["ass"], conferencia["registrado_por"]) == ("operador7", "operador7", "operador7")

    def test_conferencia_manual_exige_os_quatro_campos_e_data_valida(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        for campo in ("nome", "area", "data", "ass"):
            with pytest.raises(app.DocLibValidacaoSM):
                fluxo.conferir(sm_id, fluxo.conferencia_manual(**{campo: ""}))
        with pytest.raises(app.DocLibValidacaoSM):
            fluxo.conferir(sm_id, fluxo.conferencia_manual(data="31/02/2026"))
        with pytest.raises(app.DocLibValidacaoSM):
            fluxo.conferir(sm_id, fluxo.conferencia_manual(modalidade="outra"))
        assert fluxo.doc(sm_id)["conferencias"] == []

    def test_conferencia_so_com_aguarda_conferencia(self, app, fluxo):
        sm_id = fluxo.salvar()                                           # Em análise
        with pytest.raises(app.DocLibBloqueado):
            fluxo.conferir(sm_id, fluxo.conferencia_manual())
        fluxo.ate  # (a SM aprovada também não aceita mais conferências)
        aprovada = fluxo.ate(APROVADO)
        with pytest.raises(app.DocLibBloqueado):
            fluxo.conferir(aprovada, fluxo.conferencia_manual())

    def test_conferencia_registrada_nao_muda_nem_sai(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        fluxo.conferir(sm_id, fluxo.conferencia_manual())
        gravada = fluxo.doc(sm_id)["conferencias"]
        with pytest.raises(app.DocLibBloqueado):
            fluxo.alterar(sm_id, conferencias=[dict(gravada[0], nome="Outro Nome")])
        with pytest.raises(app.DocLibBloqueado):
            fluxo.alterar(sm_id, conferencias=[])

    def test_ate_dez_conferencias(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        for _ in range(10):
            fluxo.conferir(sm_id, fluxo.conferencia_manual())
        assert len(fluxo.doc(sm_id)["conferencias"]) == 10 and fluxo.doc(sm_id)["status"] == AGUARDA
        with pytest.raises(app.DocLibValidacaoSM, match="no máximo 10"):
            fluxo.conferir(sm_id, fluxo.conferencia_sistema())

    def test_executantes_da_liberacao_nao_valem_antes_da_aprovacao(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        with pytest.raises(app.DocLibBloqueado, match="Executantes da Liberação"):
            fluxo.alterar(sm_id, exec_lib_local="Fulano")
        assert fluxo.doc(sm_id)["status"] == AGUARDA

    def test_executantes_da_liberacao_levam_a_em_execucao(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        fluxo.executar(sm_id)
        doc = fluxo.doc(sm_id)
        assert doc["status"] == EM_EXECUCAO and doc["exec_lib_local"] == "Fulano (campo)"

    def test_so_executantes_remotos_tambem_vale(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        fluxo.alterar(sm_id, liberacao=fluxo.datar(fluxo.doc(sm_id), "liberacao"), exec_lib_remoto="Sicrano (COG)")
        assert fluxo.doc(sm_id)["status"] == EM_EXECUCAO

    def test_nao_entra_em_execucao_com_manobra_de_liberacao_sem_data(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        parcial = fluxo.datar(fluxo.doc(sm_id), "liberacao")
        parcial[2] = dict(parcial[2], data="", hora="")
        with pytest.raises(app.DocLibRegra, match="pendências de execução"):
            fluxo.alterar(sm_id, liberacao=parcial, exec_lib_local="Fulano")
        doc = fluxo.doc(sm_id)                                             # nada foi gravado (transação desfeita)
        assert doc["status"] == APROVADO and doc["exec_lib_local"] is None and doc["liberacao"][0]["hora"] == ""

    def test_horarios_podem_ser_salvos_aos_poucos_antes_dos_executantes(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        parcial = fluxo.datar(fluxo.doc(sm_id), "liberacao")
        parcial[2] = dict(parcial[2], data="", hora="")
        fluxo.alterar(sm_id, liberacao=parcial)
        assert fluxo.doc(sm_id)["status"] == APROVADO

    def test_executantes_da_normalizacao_so_com_a_sm_em_execucao(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        with pytest.raises(app.DocLibBloqueado, match="Executantes da Normalização"):
            fluxo.alterar(sm_id, exec_nor_local="Fulano")
        assert fluxo.doc(sm_id)["status"] == APROVADO                       # não pula direto para Concluído

    def test_executantes_da_normalizacao_concluem_a_sm(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        fluxo.concluir(sm_id)
        doc = fluxo.doc(sm_id)
        assert doc["status"] == CONCLUIDO and doc["exec_nor_remoto"] == "Sicrano (COG)"

    def test_nao_conclui_com_pendencias_de_execucao(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        parcial = fluxo.datar(fluxo.doc(sm_id), "normalizacao", 16)
        parcial[1] = dict(parcial[1], data="", hora="")
        with pytest.raises(app.DocLibRegra, match="Manobra de normalização 2A"):
            fluxo.alterar(sm_id, normalizacao=parcial, exec_nor_local="Fulano")
        assert fluxo.doc(sm_id)["status"] == EM_EXECUCAO
        with pytest.raises(app.DocLibBloqueado):                             # nem vazio nem em branco o campo basta
            fluxo.alterar(sm_id, exec_lib_local="")

    def test_normalizacao_nao_pode_ser_anterior_a_liberacao(self, app, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        with pytest.raises(app.DocLibValidacaoSM, match="anteriores às da última manobra de liberação"):
            fluxo.alterar(sm_id, normalizacao=fluxo.datar(fluxo.doc(sm_id), "normalizacao", 6), exec_nor_local="Fulano")

    def test_concluida_nao_aceita_mais_nada(self, app, fluxo):
        sm_id = fluxo.ate(CONCLUIDO)
        with pytest.raises(app.DocLibBloqueado, match="Concluído"):
            fluxo.alterar(sm_id, observacoes="tarde demais")
        with pytest.raises(ValueError, match="não pode ser cancelada"):
            app.doc_lib_cancelar_sm(sm_id, "operador1", "Tentativa", fluxo.doc(sm_id)["revisao"])

    @pytest.mark.parametrize("status", [EM_ANALISE, AGUARDA, APROVADO, EM_EXECUCAO])
    def test_cancelamento_permitido_antes_da_conclusao(self, app, fluxo, status):
        sm_id = fluxo.ate(status)
        app.doc_lib_cancelar_sm(sm_id, "operador1", "Serviço cancelado", fluxo.doc(sm_id)["revisao"])
        doc = fluxo.doc(sm_id)
        assert (doc["status"], doc["cancelada_por"], doc["justificativa_cancelamento"]) == (CANCELADO, "operador1", "Serviço cancelado")
        with pytest.raises(app.DocLibBloqueado):
            fluxo.alterar(sm_id, observacoes="x")

    def test_cancelamento_de_numero_reservado(self, app, fluxo):
        reservado = app.doc_lib_reservar_sm(1, "operador1")[0]["ateie_id"]
        app.doc_lib_cancelar_sm(reservado, "operador1", "Número não usado", fluxo.doc(reservado)["revisao"])
        assert fluxo.doc(reservado)["status"] == CANCELADO

    def test_cancelamento_exige_justificativa_e_nao_repete(self, app, fluxo):
        sm_id = fluxo.salvar()
        revisao = fluxo.doc(sm_id)["revisao"]
        with pytest.raises(app.DocLibRegra):
            app.doc_lib_cancelar_sm(sm_id, "operador1", "  ", revisao)
        app.doc_lib_cancelar_sm(sm_id, "operador1", "Motivo", revisao)
        with pytest.raises(ValueError, match="já está cancelada"):
            app.doc_lib_cancelar_sm(sm_id, "operador1", "De novo", revisao + 1)

    def test_somente_em_analise_permite_edicao_geral(self, app, fluxo):
        for status in (AGUARDA, APROVADO, EM_EXECUCAO):
            sm_id = fluxo.ate(status)
            with pytest.raises(app.DocLibBloqueado, match="edição geral"):
                fluxo.alterar(sm_id, motivo=f"alterado em {status}")
        em_analise = fluxo.salvar()
        fluxo.alterar(em_analise, motivo="alterado em Em análise")
        assert fluxo.doc(em_analise)["motivo"] == "alterado em Em análise"

    def test_conflito_de_edicao_simultanea(self, app, fluxo):
        sm_id = fluxo.salvar()
        antiga = copy.deepcopy(fluxo.doc(sm_id))
        fluxo.alterar(sm_id, motivo="Primeira alteração")
        antiga["motivo"] = "Segunda alteração (sobre versão antiga)"
        with pytest.raises(app.DocLibConflito):
            app.doc_lib_salvar_sm(antiga, "operador2")
        assert fluxo.doc(sm_id)["motivo"] == "Primeira alteração"
        with pytest.raises(app.DocLibConflito):
            app.doc_lib_cancelar_sm(sm_id, "operador2", "x", antiga["revisao"])

    def test_geracao_simultanea_emite_uma_unica_vez(self, app, fluxo):
        sm_id = fluxo.salvar()
        doc = fluxo.doc(sm_id)
        app.doc_lib_registrar_geracao_sm(doc, "a.pdf", "operador1")
        with pytest.raises(app.DocLibConflito):                           # a segunda usa a revisão antiga
            app.doc_lib_registrar_geracao_sm(doc, "b.pdf", "operador2")
        assert fluxo.doc(sm_id)["status"] == AGUARDA

    def test_geracao_exige_documento_valido(self, app, fluxo):
        sm_id = fluxo.salvar()
        conexao = app.doc_lib_conectar()
        conexao.execute("UPDATE doclib_sm SET motivo = '' WHERE id = ?", (sm_id,))      # dado corrompido por fora
        conexao.commit()
        conexao.close()
        with pytest.raises(app.DocLibValidacaoSM, match="Motivo"):
            fluxo.gerar(sm_id)
        assert fluxo.doc(sm_id)["status"] == EM_ANALISE


# ======================================================================================================================
# Triggers e histórico: o banco protege as regras mesmo contra operação direta
# ======================================================================================================================
class TestBanco:
    def direto(self, app, sql, parametros=()):
        conexao = app.doc_lib_conectar()
        try:
            conexao.execute(sql, parametros)
            conexao.commit()
        finally:
            conexao.close()

    @pytest.mark.parametrize("origem,destino", [(EM_ANALISE, CONCLUIDO), (EM_ANALISE, APROVADO), (EM_ANALISE, EM_EXECUCAO),
                                                (AGUARDA, EM_EXECUCAO), (AGUARDA, CONCLUIDO), (APROVADO, CONCLUIDO),
                                                (AGUARDA, EM_ANALISE), (APROVADO, AGUARDA), (EM_EXECUCAO, APROVADO)])
    def test_transicao_invalida_e_recusada_pelo_banco(self, app, fluxo, origem, destino):
        sm_id = fluxo.ate(origem)
        with pytest.raises(sqlite3.IntegrityError, match="transição de status"):
            self.direto(app, "UPDATE doclib_sm SET status = ? WHERE id = ?", (destino, sm_id))
        assert fluxo.doc(sm_id)["status"] == origem

    def test_concluida_e_cancelada_nao_saem_do_status(self, app, fluxo):
        concluida = fluxo.ate(CONCLUIDO)
        for destino in (CANCELADO, EM_EXECUCAO, EM_ANALISE):
            with pytest.raises(sqlite3.IntegrityError):
                self.direto(app, "UPDATE doclib_sm SET status = ? WHERE id = ?", (destino, concluida))
        cancelada = fluxo.salvar()
        app.doc_lib_cancelar_sm(cancelada, "operador1", "x", fluxo.doc(cancelada)["revisao"])
        with pytest.raises(sqlite3.IntegrityError):
            self.direto(app, "UPDATE doclib_sm SET status = ? WHERE id = ?", (EM_ANALISE, cancelada))
        with pytest.raises(sqlite3.IntegrityError, match="concluída ou cancelada"):
            self.direto(app, "UPDATE doclib_sm SET motivo = 'x' WHERE id = ?", (concluida,))

    def test_numero_nao_muda_e_sm_nao_e_excluida(self, app, fluxo):
        sm_id = fluxo.salvar()
        with pytest.raises(sqlite3.IntegrityError, match="número"):
            self.direto(app, "UPDATE doclib_sm SET numero = '0099/26' WHERE id = ?", (sm_id,))
        with pytest.raises(sqlite3.IntegrityError, match="número"):
            self.direto(app, "UPDATE doclib_sm SET sequencia = 7 WHERE id = ?", (sm_id,))
        with pytest.raises(sqlite3.IntegrityError, match="excluída"):
            self.direto(app, "DELETE FROM doclib_sm WHERE id = ?", (sm_id,))

    def test_numero_duplicado_e_recusado(self, app, fluxo):
        fluxo.salvar()
        with pytest.raises(sqlite3.IntegrityError):
            self.direto(app, "INSERT INTO doclib_sm (numero, ano, sequencia, status) VALUES ('0001/26', 2026, 50, 'Reservado')")
        with pytest.raises(sqlite3.IntegrityError):
            self.direto(app, "INSERT INTO doclib_sm (numero, ano, sequencia, status) VALUES ('0050/26', 2026, 1, 'Reservado')")

    def test_conferencia_registrada_nao_pode_ser_alterada_nem_apagada(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        with pytest.raises(sqlite3.IntegrityError, match="conferência"):
            self.direto(app, "UPDATE doclib_sm_conferencias SET nome = 'x' WHERE sm_id = ?", (sm_id,))
        with pytest.raises(sqlite3.IntegrityError, match="conferência"):
            self.direto(app, "DELETE FROM doclib_sm_conferencias WHERE sm_id = ?", (sm_id,))

    def test_modalidade_invalida_e_recusada_pelo_banco(self, app, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        with pytest.raises(sqlite3.IntegrityError):
            self.direto(app, "INSERT INTO doclib_sm_conferencias (sm_id, ordem, modalidade, nome, area, data, ass) "
                             "VALUES (?, 1, 'outra', 'a', 'b', '25/10/2026', 'c')", (sm_id,))

    def test_historico_registra_cada_mudanca_de_status_com_usuario_e_momento(self, app, fluxo):
        sm_id = fluxo.ate(CONCLUIDO)
        conexao = app.doc_lib_conectar()
        historico = conexao.execute("SELECT status_anterior, status_novo, usuario, momento FROM doclib_sm_historico "
                                    "WHERE evento = 'status' AND sm_id = ? ORDER BY id", (sm_id,)).fetchall()
        conexao.close()
        assert [(h[0], h[1]) for h in historico] == [(None, EM_ANALISE), (EM_ANALISE, AGUARDA), (AGUARDA, APROVADO),
                                                     (APROVADO, EM_EXECUCAO), (EM_EXECUCAO, CONCLUIDO)]
        assert all(h[2] == "operador1" and h[3] for h in historico)

    def test_tabela_de_transicoes_do_banco_acompanha_o_codigo(self, app, fluxo):
        conexao = app.doc_lib_conectar()
        no_banco = set(conexao.execute("SELECT origem, destino FROM doclib_sm_transicoes").fetchall())
        conexao.close()
        assert no_banco == {(o, d) for o, ds in app.DOC_LIB_TRANSICOES_SM.items() for d in ds}

    def test_garantir_banco_pode_ser_repetido_sem_perder_dados(self, app, fluxo):
        sm_id = fluxo.ate(APROVADO)
        for _ in range(3):
            app.garantir_banco_doc_lib()
        assert fluxo.doc(sm_id)["status"] == APROVADO and len(fluxo.doc(sm_id)["conferencias"]) == 2

    def test_tabelas_de_ai_ateie_e_mo_continuam_criadas(self, app, banco):
        conexao = app.doc_lib_conectar()
        tabelas = {linha[0] for linha in conexao.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        conexao.close()
        assert {"doclib_ateie", "doclib_ai", "doclib_mo", "doclib_sm", "doclib_numeracao"} <= tabelas


# ======================================================================================================================
# SM-Referência (dados herdados)
# ======================================================================================================================
class TestReferencia:
    def preparar_origem(self, app, fluxo):
        sm_id = fluxo.ate(CONCLUIDO)
        return sm_id, fluxo.doc(sm_id)

    def test_dados_herdados_e_excluidos(self, app, fluxo):
        sm_id, doc = self.preparar_origem(app, fluxo)
        dados = app.doc_lib_dados_referencia_sm(doc)
        assert dados["referencia_id"] == sm_id and dados["referencia_numero"] == "0001/26"
        assert dados["motivo"] == doc["motivo"] and dados["cond_loto_com"] == doc["cond_loto_com"]
        assert [m["acao"] for m in dados["liberacao"]] == [m["acao"] for m in doc["liberacao"]]
        assert all(m["data"] == "" and m["hora"] == "" for m in dados["liberacao"] + dados["normalizacao"])
        proibidos = {"id", "numero", "status", "revisao", "emitido", "conferencias", "exec_lib_local", "exec_lib_remoto",
                     "exec_nor_local", "exec_nor_remoto", "p0_data_inicio", "p1_data_inicio", "elaborado_por",
                     "elaborado_ass", "elaborado_data", "reprogramacoes", "cancelada_por"}
        assert not proibidos & set(dados)

    def test_nova_sm_a_partir_da_referencia(self, app, fluxo):
        origem_id, origem = self.preparar_origem(app, fluxo)
        herdados = app.doc_lib_dados_referencia_sm(origem)
        nova_id = fluxo.salvar(**herdados, usuario="operador2",
                               p0_data_inicio="01/11/2026", p0_data_termino="01/11/2026")
        nova = fluxo.doc(nova_id)
        assert nova["numero"] == "0002/26" and nova["status"] == EM_ANALISE and nova["emitido"] == 0
        assert (nova["referencia_id"], nova["referencia_numero"]) == (origem_id, "0001/26")
        assert nova["exec_lib_local"] in (None, "") and nova["exec_nor_local"] in (None, "") and nova["conferencias"] == []
        assert all(not m["data"] and not m["hora"] for m in nova["liberacao"] + nova["normalizacao"])
        assert nova["elaborado_ass"] == "operador2" and nova["p0_data_inicio"] == "01/11/2026"
        assert nova["motivo"] == origem["motivo"] and nova["cond_chaves_abertas"] == origem["cond_chaves_abertas"]
        assert [m["acao"] for m in nova["normalizacao"]] == [m["acao"] for m in origem["normalizacao"]]
        # a SM de origem não foi alterada
        assert fluxo.doc(origem_id)["status"] == CONCLUIDO and fluxo.doc(origem_id)["exec_lib_local"] == "Fulano (campo)"

    def test_referencia_de_sm_reservada_ou_inexistente_e_recusada(self, app, fluxo):
        reservado = app.doc_lib_reservar_sm(1, "operador1")[0]["ateie_id"]
        with pytest.raises(app.DocLibRegra, match="referência"):
            fluxo.salvar(referencia_id=reservado)
        with pytest.raises(app.DocLibRegra, match="referência"):
            fluxo.salvar(referencia_id=999)
        assert len(numeros(app)) == 1                                        # só a reserva: nenhum número consumido

    @pytest.mark.parametrize("status", [EM_ANALISE, AGUARDA, APROVADO, EM_EXECUCAO, CONCLUIDO])
    def test_referencia_vale_para_qualquer_status_menos_reservado(self, app, fluxo, status):
        sm_id = fluxo.ate(status)
        nova_id = fluxo.salvar(**app.doc_lib_dados_referencia_sm(fluxo.doc(sm_id)))
        assert fluxo.doc(nova_id)["referencia_id"] == sm_id


# ======================================================================================================================
# GRID
# ======================================================================================================================
class TestListagem:
    def test_listagem_do_grid(self, app, fluxo):
        fluxo.salvar()
        sm_id = fluxo.salvar(p0_data_inicio="26/10/2026", p0_data_termino="26/10/2026")
        fluxo.gerar(sm_id)
        fluxo.alterar(sm_id, p1_data_inicio="27/10/2026", p1_hora_inicio="09:00", p1_data_termino="27/10/2026",
                      p1_hora_termino="18:00", reprogramacoes=1)
        app.doc_lib_reservar_sm(1, "operador1")
        lista = app.doc_lib_listar_sm()
        assert [item["numero"] for item in lista] == ["0003/26", "0002/26", "0001/26"]        # mais recente primeiro
        reservada, vigente = lista[0], lista[1]
        assert (reservada["status"], reservada["motivo"], reservada["prog_inicio"]) == (RESERVADO, "SM RESERVADA", "")
        assert (vigente["prog_inicio"], vigente["prog_termino"]) == ("27/10/2026 09:00", "27/10/2026 18:00")   # reprogramação em vigor
        assert (vigente["local"], vigente["equipamento"], vigente["status"]) == ("SE MCP", "DJ 52-1", AGUARDA)
