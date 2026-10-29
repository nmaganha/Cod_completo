"""SM Avulso (Doc_Lib. - Click_25): documento impresso (PDF) - conteúdo, quebras, paginação, alinhamento e arquivamento."""
import glob
import os
import re

import pytest

pymupdf = pytest.importorskip("pymupdf")

EM_ANALISE, AGUARDA, APROVADO = "Em análise", "Aguarda Conferência", "Aprovado para Execução"
EM_EXECUCAO, CONCLUIDO, CANCELADO, RESERVADO = "Em Execução", "Concluído", "Cancelado", "Reservado"

MM = 72 / 25.4                                  # pontos por milímetro
MARGEM_DIREITA = 196.0 * MM + 1.0               # PDFSM.X1 (com folga de 1 pt)
BASE_DO_CONTEUDO = 282.0 * MM                   # régua do rodapé


def ler(caminho):
    documento = pymupdf.open(caminho)
    return documento, "\n".join(pagina.get_text() for pagina in documento)


def sem_quebras(texto):
    return " ".join(texto.split())


@pytest.fixture()
def pdf(app, fluxo):
    """Gera o PDF da SM informada (a partir do que está gravado) e devolve (documento pymupdf, texto)."""
    def gerar(sm_id, usuario="operador1"):
        caminho, _ = fluxo.gerar(sm_id, usuario)
        return caminho, *ler(caminho)
    return gerar


class TestConteudo:
    def test_cabecalho_itens_e_dados_da_sm(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(observacoes="Observação de teste")
        caminho, documento, texto = pdf(sm_id)
        plano = sem_quebras(texto)
        for esperado in ("SEQUÊNCIA DE MANOBRAS - SM", "SM Nº COG-0001/26", "Período programado para execução do(s) serviço(s):",
                         "Programação:", "Reprogramação-1:", "Reprogramação-2:", "Reprogramação-3:",
                         "25/10/2026", "08:00 hs", "17:00 hs", "Equipamento(s) a impedir:", "3.1. Local", "3.2. Instalação",
                         "3.3. Equipamento", "3.4. Caracterização", "3.5. Local da Execução do(s) Serviço(s)",
                         "3.6. Tempo Retorno à Operação", "SE MCP", "PÁTIO 230 KV", "DJ 52-1", "Sem desligamento de UG/LT", "UHE MGP", "02:30",
                         "Motivo:", "Manutenção preventiva no disjuntor 52-1.", "Condições de Segurança:",
                         "Chaves abertas e bloqueadas:", "89-1 e 89-2", "Chaves fechadas e bloqueadas:",
                         "Disjuntores Extraídos:", "Outras condições:", "Com bloqueio por LOTO:", "Sem bloqueio por LOTO:",
                         "Manobras de Liberação:", "Sequência", "Local", "Ação", "Abrir DJ 52-1", "Bloquear seccionadora 89-1",
                         "Executantes", "No local:", "Remotamente:", "Manobras de Normalização:", "Desbloquear seccionadora 89-1",
                         "Observações:", "Observação de teste", "Elaborado por:", "operador1", "Área:", "COG", "24/10/2026",
                         "Ass:", "Conferência:", "Nome:", "Aguardando a Conferência do documento"):
            assert esperado in plano, esperado
        assert "Pátio 230 kV" not in plano                                                  # 3.1 a 3.3 saem sempre em caixa alta
        assert len(documento) <= 2                                                          # Elaborado por e Conferência ficam juntos
        assert f"Página 1 de {len(documento)}" in plano and plano.count("SM Nº COG-0001/26") == 2 * len(documento)

    def test_caixa_alta_nos_itens_3_1_a_3_3_e_no_local_das_manobras(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(equipamentos=[{"local": "se igu", "instalacao": "pátio 69 kv", "equipamento": "dj 52-1",
                                            "caracterizacao": "Com desligamento da LT", "local_execucao": "Ao longo da LT",
                                            "tempo_retorno": "Indisponível"}],
                             liberacao=[{"numero": "1", "local": "cog", "acao": "Abrir DJ 52-1"}],
                             normalizacao=[{"numero": "1", "local": "se igu", "acao": "Fechar DJ 52-1"}])
        _, documento, texto = pdf(sm_id)
        plano = sem_quebras(texto)
        for esperado in ("SE IGU", "PÁTIO 69 KV", "DJ 52-1", "Com desligamento da LT", "Ao longo da LT"):
            assert esperado in plano, esperado
        for minusculo in ("se igu", "pátio 69 kv", "dj 52-1"):
            assert minusculo not in plano, minusculo
        palavras = [p[4] for p in documento[0].get_text("words")]
        assert "COG" in palavras and "cog" not in palavras                                    # Local das manobras também

    def test_tempo_de_retorno_indisponivel_e_impresso_como_texto(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(equipamentos=[
            {"local": "SE MCP", "instalacao": "PÁTIO", "equipamento": "DJ 1", "caracterizacao": "Sem desligamento de UG/LT",
             "local_execucao": "COG-P", "tempo_retorno": "Indisponível"},
            {"local": "SE MCP", "instalacao": "PÁTIO", "equipamento": "DJ 2", "caracterizacao": "Sem desligamento de UG/LT",
             "local_execucao": "COG-R", "tempo_retorno": "9:05"}])
        _, _, texto = pdf(sm_id)
        plano = sem_quebras(texto)
        assert "Indisponível" in plano and "09:05" in plano

    def test_numeracao_da_secao_e_sequencia_impressa(self, app, fluxo, pdf):
        _, documento, texto = pdf(fluxo.salvar())
        palavras = [p[4] for p in documento[0].get_text("words")]
        assert {"1A", "1B", "2A"} <= set(palavras)
        for numero_e_titulo in ("1.SM", "2.Período", "2.1.Programação:", "2.2.Reprogramação-1:", "2.3.Reprogramação-2:",
                                "2.4.Reprogramação-3:", "3.Equipamento(s)", "4.Motivo:", "5.Condições", "5.1.Chaves",
                                "5.2.Chaves", "5.3.Disjuntores", "5.4.Outras", "5.4.1.Com", "5.4.2.Sem", "6.Manobras",
                                "7.Executantes", "7.1.No", "7.2.Remotamente:", "8.Manobras", "9.Executantes", "9.1.No",
                                "9.2.Remotamente:", "10.Observações:", "11.Elaborado", "12.Conferência:"):
            assert numero_e_titulo in palavras, numero_e_titulo

    def test_data_e_hora_das_manobras_nao_vao_para_o_impresso(self, app, fluxo, pdf):
        sm_id = fluxo.ate(APROVADO)
        liberacao = [dict(m, data="25/10/2026", hora=f"13:{i * 10:02d}") for i, m in enumerate(fluxo.doc(sm_id)["liberacao"])]
        fluxo.alterar(sm_id, liberacao=liberacao, exec_lib_local="Fulano (campo)", exec_lib_remoto="Sicrano (COG)")
        normalizacao = [dict(m, data="25/10/2026", hora=f"15:{i * 10:02d}") for i, m in enumerate(fluxo.doc(sm_id)["normalizacao"])]
        fluxo.alterar(sm_id, normalizacao=normalizacao, exec_nor_local="Beltrano (campo)")
        assert fluxo.doc(sm_id)["status"] == CONCLUIDO
        _, _, texto = pdf(sm_id)
        sem_rodape = re.sub(r"Gerado pelo sistema COG-Alupar em \S+ às \d\d:\d\d por \S+", "", texto)   # a hora da geração não conta
        assert "13:" not in sem_rodape and "15:" not in sem_rodape                  # horários das manobras
        assert "08:00 hs" in texto and "17:00 hs" in texto                          # período programado continua
        assert "Fulano (campo)" in texto and "Sicrano (COG)" in texto and "Beltrano (campo)" in texto   # executantes
        assert "Aguardando a Conferência" not in texto

    def test_conferencias_registradas_aparecem_e_ha_linhas_em_branco_para_completar(self, app, fluxo, pdf):
        sm_id = fluxo.ate(APROVADO)
        _, documento, texto = pdf(sm_id)
        plano = sem_quebras(texto)
        assert "Joao da Manutencao" in plano and "via fonia" in plano and "Manutenção" in plano
        assert "Aguardando a Conferência" not in plano
        assert plano.count("Nome:") == 3                                             # 2 registradas + 1 em branco

    def test_dez_conferencias_no_documento(self, app, fluxo, pdf):
        sm_id = fluxo.ate(AGUARDA)
        fluxo.conferir(sm_id, *[fluxo.conferencia_manual(nome=f"Conferente {i:02d}") for i in range(1, 11)])
        _, _, texto = pdf(sm_id)
        assert all(f"Conferente {i:02d}" in texto for i in range(1, 11)) and sem_quebras(texto).count("Nome:") == 10

    def test_reprogramacoes_impressas_e_campos_vazios_com_o_traco_do_formulario(self, app, fluxo, pdf):
        sm_id = fluxo.ate(APROVADO)
        fluxo.alterar(sm_id, p1_data_inicio="26/10/2026", p1_hora_inicio="09:00", p1_data_termino="26/10/2026",
                      p1_hora_termino="18:30", reprogramacoes=1)
        _, _, texto = pdf(sm_id)
        assert "26/10/2026" in texto and "09:00 hs" in texto and "18:30 hs" in texto
        assert "____:____ hs" in texto                                               # Reprogramação-2 e 3 em branco

    def test_o_pdf_reflete_o_que_esta_gravado(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(motivo="Motivo original")
        fluxo.gerar(sm_id)
        fluxo.aprovar(sm_id)
        _, _, primeiro = pdf(sm_id)
        fluxo.alterar(sm_id, p1_data_inicio="26/10/2026", p1_hora_inicio="09:00", p1_data_termino="26/10/2026",
                      p1_hora_termino="18:30", reprogramacoes=1)                    # aprovada: só os campos de acompanhamento
        _, _, segundo = pdf(sm_id)
        assert "18:30 hs" not in primeiro and "26/10/2026" not in primeiro
        assert "18:30 hs" in segundo and "26/10/2026" in segundo and "Motivo original" in segundo

    def test_pdf_nao_traz_valores_temporarios_da_tela(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(motivo="Gravado")
        doc = fluxo.doc(sm_id)
        doc_na_tela = dict(doc, motivo="Digitado e ainda não salvo")                 # a geração parte do que está no banco
        caminho, _ = app.doc_lib_registrar_e_arquivar_sm(fluxo.doc(sm_id), "operador1")
        assert "Digitado e ainda não salvo" not in ler(caminho)[1] and "Gravado" in ler(caminho)[1]
        assert doc_na_tela["motivo"] != fluxo.doc(sm_id)["motivo"]


class TestQuebrasEPaginacao:
    def acoes_longas(self, quantidade, prefixo):
        return [{"numero": str(1 + i // 3), "local": "SE MCP",
                 "acao": f"{prefixo}{i + 1:02d} " + "Verificar a posição e abrir o equipamento do vão de linha conforme o "
                                                    "procedimento de manobra aprovado pelo COG " * 3}
                for i in range(quantidade)]

    def test_30_manobras_em_cada_tabela_continuam_nas_paginas_seguintes(self, app, fluxo, pdf):
        liberacao, normalizacao = self.acoes_longas(30, "LIB"), self.acoes_longas(30, "NOR")
        sm_id = fluxo.salvar(liberacao=liberacao, normalizacao=normalizacao)
        _, documento, texto = pdf(sm_id)
        plano = sem_quebras(texto)
        assert len(documento) >= 4
        assert "Manobras de Liberação (continuação):" in plano and "Manobras de Normalização (continuação):" in plano
        for prefixo in ("LIB", "NOR"):
            for i in range(1, 31):
                assert plano.count(f"{prefixo}{i:02d} ") == 1, f"{prefixo}{i:02d}"
        for numero in range(1, len(documento) + 1):
            assert f"Página {numero} de {len(documento)}" in plano

    def test_colunas_alinhadas_e_nada_ultrapassa_as_margens(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(liberacao=self.acoes_longas(30, "LIB"), normalizacao=self.acoes_longas(12, "NOR"),
                             motivo="Motivo " * 80, cond_chaves_abertas="chave 89-1 " * 60, observacoes="Observação extensa " * 120)
        _, documento, _ = pdf(sm_id)
        for pagina in documento:
            palavras = pagina.get_text("words")
            assert all(p[2] <= MARGEM_DIREITA for p in palavras), "texto ultrapassou a margem direita"
            assert all(p[3] <= BASE_DO_CONTEUDO or p[1] >= BASE_DO_CONTEUDO for p in palavras), "texto invadiu o rodapé"
            primeiras = [p for p in palavras if p[4][:3] in ("LIB", "NOR") and p[4][3:5].isdigit()]
            assert len({round(p[0], 1) for p in primeiras}) <= 1                    # a coluna Ação começa no mesmo x
            if primeiras:
                assert primeiras[0][0] > 41.0 * MM                                  # à direita das colunas Sequência e Local

    def test_acao_extensa_quebra_em_varias_linhas_dentro_da_celula(self, app, fluxo, pdf):
        acao = "Abrir o disjuntor " + "muito longo " * 40
        sm_id = fluxo.salvar(liberacao=[{"numero": "1", "local": "SE", "acao": acao}])
        _, documento, texto = pdf(sm_id)
        linhas = [linha for linha in texto.splitlines() if "muito longo" in linha]
        assert len(linhas) >= 4 and sem_quebras(texto).count("muito longo") == 40

    def test_motivo_de_seis_linhas_e_condicoes_de_varias_linhas(self, app, fluxo, pdf):
        motivo = "\n".join(f"Linha {i} do motivo" for i in range(1, 7))
        sm_id = fluxo.salvar(motivo=motivo, cond_disjuntores="52-1\n52-2\n52-3", cond_loto_com="a\nb\nc\nd\ne")
        _, documento, texto = pdf(sm_id)
        assert all(f"Linha {i} do motivo" in texto for i in range(1, 7))
        assert all(f"\n{c}\n" in texto for c in "abcde") and len(documento) <= 2

    def test_texto_digitado_com_quebras_preserva_as_linhas(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(observacoes="primeira linha\nsegunda linha\n\nquarta linha")
        _, _, texto = pdf(sm_id)
        assert "primeira linha\nsegunda linha" in texto and "quarta linha" in texto

    def test_uma_pagina_para_uma_sm_pequena(self, app, fluxo, pdf):
        _, documento, _ = pdf(fluxo.salvar())
        assert len(documento) == 1


class TestSituacoesEArquivo:
    def test_formulario_reservado_em_branco(self, app, fluxo, pdf):
        reservado = app.doc_lib_reservar_sm(1, "operador1")[0]["ateie_id"]
        caminho, documento, texto = pdf(reservado)
        plano = sem_quebras(texto)
        assert os.path.basename(caminho).startswith("SM_RESERVADA_0001-26_") and "SM Nº COG-0001/26" in plano
        assert "Nenhuma" not in plano and "Aguardando" not in plano and "____:____ hs" in plano
        assert "Elaborado por:" in plano and "Conferência:" in plano
        doc = fluxo.doc(reservado)
        assert doc["status"] == RESERVADO and doc["emitido"] == 0                    # o formulário em branco não emite

    def test_sm_cancelada_mostra_o_cancelamento(self, app, fluxo, pdf):
        sm_id = fluxo.ate(APROVADO)
        app.doc_lib_cancelar_sm(sm_id, "operador9", "Serviço adiado pela Manutenção", fluxo.doc(sm_id)["revisao"])
        _, documento, texto = pdf(sm_id)
        plano = sem_quebras(texto)
        assert "SM cancelada em" in plano and "operador9" in plano and "Serviço adiado pela Manutenção" in plano
        assert fluxo.doc(sm_id)["status"] == CANCELADO
        cores = {span["color"] for bloco in documento[0].get_text("dict")["blocks"] for linha in bloco.get("lines", [])
                 for span in linha["spans"] if "COG-0001/26" in span["text"] and span["size"] > 9}
        assert cores == {0xB00000}                                                   # número riscado em vermelho

    def test_aviso_de_conferencia_so_enquanto_aguarda(self, app, fluxo, pdf):
        sm_id = fluxo.ate(AGUARDA)
        assert "Aguardando a Conferência do documento" in pdf(sm_id)[2]
        fluxo.aprovar(sm_id)
        assert "Aguardando a Conferência do documento" not in pdf(sm_id)[2]

    def test_arquivamento_registro_no_banco_e_sem_sobrescrever(self, app, fluxo, banco):
        sm_id = fluxo.salvar()
        primeiro, aviso = fluxo.gerar(sm_id)
        segundo, _ = fluxo.gerar(sm_id)
        terceiro, _ = fluxo.gerar(sm_id)
        assert aviso is None and len({primeiro, segundo, terceiro}) == 3 and all(os.path.isfile(c) for c in (primeiro, segundo, terceiro))
        assert os.path.dirname(primeiro) == str(banco / "doc_lib_arquivo" / "SM" / "2026")
        assert not glob.glob(str(banco / "doc_lib_arquivo" / "SM" / "2026" / "*.tmp"))
        conexao = app.doc_lib_conectar()
        registros = conexao.execute("SELECT caminho, gerado_por, revisao_final FROM doclib_sm_pdfs WHERE sm_id = ?", (sm_id,)).fetchall()
        conexao.close()
        assert [r[0] for r in registros] == [primeiro, segundo, terceiro] and all(r[1] == "operador1" for r in registros)

    def test_falha_ao_registrar_nao_deixa_arquivo_orfao_nem_emite(self, app, fluxo, banco, monkeypatch):
        sm_id = fluxo.salvar()

        def falha(*args, **kwargs):
            raise app.DocLibConflito("simulado")
        with monkeypatch.context() as contexto:
            contexto.setattr(app, "doc_lib_registrar_geracao_sm", falha)
            with pytest.raises(app.DocLibConflito):
                fluxo.gerar(sm_id)
        assert not glob.glob(str(banco / "doc_lib_arquivo" / "SM" / "2026" / "*"))
        assert fluxo.doc(sm_id)["status"] == EM_ANALISE and fluxo.doc(sm_id)["emitido"] == 0

    def test_nome_completo_do_elaborador_no_documento(self, app, fluxo, pdf):
        conexao = app.doc_lib_conectar()
        conexao.execute("CREATE TABLE IF NOT EXISTS Usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha TEXT, admin INTEGER, "
                        "primeiro_acesso INTEGER, nome_completo TEXT)")
        conexao.execute("INSERT INTO Usuarios (usuario, senha, admin, primeiro_acesso, nome_completo) "
                        "VALUES ('operador1', 'x', 0, 0, 'Operador de Teste Um')")
        conexao.commit()
        conexao.close()
        _, _, texto = pdf(fluxo.salvar())
        assert "Operador de Teste Um" in sem_quebras(texto) and "operador1" in texto


class TestTextosSemEspacoOuExtremos:
    def test_palavra_enorme_sem_espaco_quebra_dentro_da_margem(self, app, fluxo, pdf):
        sm_id = fluxo.salvar(liberacao=[{"numero": "1", "local": "SE", "acao": "X" * 400}], cond_chaves_abertas="Y" * 400,
                             observacoes="Z" * 600, motivo="W" * 300)
        _, documento, texto = pdf(sm_id)
        for pagina in documento:
            assert all(p[2] <= MARGEM_DIREITA for p in pagina.get_text("words"))
        assert texto.count("X") == 400 and texto.count("Y") == 400 and texto.count("Z") == 600

    def test_sm_com_tudo_no_limite_gera_o_documento(self, app, fluxo, pdf):
        trinta = [{"numero": str(i), "local": "SE MCP", "acao": f"Abrir equipamento {i} " * 8} for i in range(1, 31)]
        sm_id = fluxo.salvar(liberacao=trinta, normalizacao=trinta, motivo="\n".join(f"linha {i}" for i in range(1, 7)),
                             cond_chaves_abertas="a\nb\nc", observacoes="o\n" * 30,
                             equipamentos=[{"local": f"L{i}", "instalacao": "I" * 40, "equipamento": "E" * 60,
                                            "caracterizacao": "Com risco desligamento das UG-1, 2, 3 e 4",
                                            "local_execucao": "EOL Ventos de Horizonte", "tempo_retorno": "23:59"} for i in (1, 2, 3)])
        fluxo.gerar(sm_id)
        fluxo.conferir(sm_id, *[fluxo.conferencia_manual(nome=f"C{i}") for i in range(9)], fluxo.conferencia_sistema())
        assert fluxo.doc(sm_id)["status"] == APROVADO and len(fluxo.doc(sm_id)["conferencias"]) == 10
        _, documento, texto = pdf(sm_id)
        assert len(documento) >= 4 and "23:59" in texto and sem_quebras(texto).count("Nome:") == 10
        assert "Com risco desligamento das UG-1, 2, 3 e 4" in sem_quebras(texto) and "EOL Ventos de Horizonte" in sem_quebras(texto)
