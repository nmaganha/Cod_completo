"""SM Avulso (Doc_Lib. - Click_25): janela, tabelas, botões, bloqueios por status, GRID e menu (Tk real, em tela virtual)."""
from datetime import datetime

import pytest

EM_ANALISE, AGUARDA, APROVADO = "Em análise", "Aguarda Conferência", "Aprovado para Execução"
EM_EXECUCAO, CONCLUIDO, CANCELADO, RESERVADO = "Em Execução", "Concluído", "Cancelado", "Reservado"

CAMPOS_EQUIP = ("local", "instalacao", "equipamento", "caracterizacao", "local_execucao", "tempo_retorno")


@pytest.fixture()
def janelas(app, mensagens):
    """Abre janelas da SM e as fecha ao final do teste (as caixas de mensagem são as do fixture 'mensagens': um aviso agendado
    pela janela, como o do nome completo, nunca fica esperando um clique)."""
    abertas = []

    def abrir(**kwargs):
        janela = app.JanelaSMAvulso(**kwargs)
        abertas.append(janela)
        app.root.update()
        return janela

    yield abrir
    for janela in abertas:
        try:
            janela.janela.destroy()
        except Exception:
            pass


@pytest.fixture()
def dialogos(app, monkeypatch):
    """Os diálogos modais (documento gerado, reserva, justificativa) não esperam clique: registram a chamada."""
    chamadas = {"gerado": [], "justificativa": "Serviço cancelado pela manutenção"}
    monkeypatch.setattr(app, "doc_lib_dialogo_documento_gerado", lambda *args, **kw: chamadas["gerado"].append(args[1:]))
    monkeypatch.setattr(app, "solicitar_justificativa", lambda *args, **kw: chamadas["justificativa"])
    return chamadas


def definir(app, entrada, texto):
    app.doc_lib_definir_entrada(entrada, texto)


def preencher(app, janela, motivo="Manutenção preventiva do disjuntor 52-1."):
    """Digita uma SM válida na janela (como o usuário faria)."""
    p0 = janela.periodo["p0"]
    for campo, valor in (("data_inicio", "25/10/2026"), ("hora_inicio", "08:00"), ("data_termino", "25/10/2026"),
                         ("hora_termino", "17:00")):
        definir(app, p0[campo], valor)
    preencher_equipamento(app, janela, 0)
    janela._definir_texto(janela.txt_motivo, motivo)
    for campo, texto in janela.txt_condicoes.items():
        janela._definir_texto(texto, "Nenhuma")
    janela.tab_lib.preencher([{"numero": "1", "local": "SE MCP", "acao": "Abrir DJ 52-1"},
                              {"numero": "1", "local": "SE MCP", "acao": "Abrir seccionadora 89-1"},
                              {"numero": "2", "local": "SE MCP", "acao": "Bloquear seccionadora 89-1"}])
    janela.tab_nor.preencher([{"numero": "1", "local": "SE MCP", "acao": "Desbloquear seccionadora 89-1"},
                              {"numero": "2", "local": "SE MCP", "acao": "Fechar seccionadora 89-1"},
                              {"numero": "2", "local": "SE MCP", "acao": "Fechar DJ 52-1"}])


def preencher_equipamento(app, janela, indice, caracterizacao="Sem desligamento de UG/LT", local_execucao="UHE MGP",
                          tempo="2:30", local="SE MCP", instalacao="Pátio 230 kV", equipamento="DJ 52-1"):
    """Linha da tabela 3 preenchida como o usuário faz: texto nos três primeiros campos, escolha nas duas listas e, no 3.6,
    a opção Indisponível ou a opção do tempo com o HH:MM digitado."""
    for campo, valor in (("local", local), ("instalacao", instalacao), ("equipamento", equipamento)):
        definir(app, janela.equip[indice][campo], valor)
    janela.equip[indice]["caracterizacao"].set(caracterizacao)
    janela.equip[indice]["local_execucao"].set(local_execucao)
    if tempo == "Indisponível":
        janela.tempo_modo[indice].set("indisponivel")
        janela._ao_mudar_tempo(indice)
    else:
        janela.tempo_modo[indice].set("tempo")
        janela._ao_mudar_tempo(indice, True)
        definir(app, janela.equip[indice]["tempo_retorno"], tempo)


def estado(widget):
    return str(widget.cget("state"))


def travado(widget):
    """Campo que não aceita lançamento: Entry somente leitura, Text/botão/lista desabilitados ou ícone de calendário inativo.
    (Uma lista de seleção liberada fica "readonly", pois aceita só a escolha; por isso o teste dela usa liberado.)"""
    if hasattr(widget, "habilitado"):
        return not widget.habilitado
    return estado(widget) in ("readonly", "disabled")


def liberado(widget):
    """Campo que aceita lançamento: Entry normal, lista de seleção pronta para escolher, ícone ativo."""
    if hasattr(widget, "habilitado"):
        return widget.habilitado
    return estado(widget) == ("readonly" if widget.winfo_class() == "TCombobox" else "normal")


def botoes(janela):
    return {"voltar": janela.btn_voltar, "salvar": janela.btn_salvar, "editar": janela.btn_editar, "gerar": janela.btn_gerar,
            "reservar": janela.btn_reservar, "cancelar": janela.btn_cancelar, "referencia": janela.btn_referencia}


def habilitados(janela):
    return {nome for nome, botao in botoes(janela).items() if estado(botao) == "normal"}


class TestAberturaEPadroes:
    def test_numero_previsto_no_alto_e_a_direita_sem_consumir(self, app, banco, janelas):
        janela = janelas()
        assert janela.lbl_numero.cget("text") == "0001/26"
        assert "só é consumido ao salvar" in janela.lbl_nota_numero.cget("text")
        assert janela.lbl_numero.winfo_rootx() > janela.janela.winfo_rootx() + janela.janela.winfo_width() // 2
        assert janela.lbl_numero.winfo_rooty() < janela.janela.winfo_rooty() + 200          # no alto da janela
        assert app.doc_lib_numeros_previstos(1, "SM") == ["0001/26"]

    def test_valores_padrao_do_elaborador(self, app, banco, janelas):
        janela = janelas()
        assert janela.ent_elaborado_area.get() == "COG"
        assert janela.ent_elaborado_data.get() == datetime.now().strftime("%d/%m/%Y")
        assert janela.lbl_elaborado_ass.cget("text") == "operador1"
        assert janela.lbl_elaborado_nome.cget("text") == "operador1"                         # sem nome completo cadastrado

    def test_estado_inicial_dos_botoes(self, app, banco, janelas):
        assert habilitados(janelas()) == {"voltar", "salvar", "reservar"}

    def test_somente_a_programacao_original_esta_habilitada(self, app, banco, janelas):
        janela = janelas()
        assert not travado(janela.periodo["p0"]["data_inicio"]) and not travado(janela.periodo["p0"]["hora_termino"])
        for prefixo in ("p1", "p2", "p3"):
            assert all(travado(janela.periodo[prefixo][campo]) for campo in
                       ("data_inicio", "hora_inicio", "data_termino", "hora_termino"))

    def test_titulo_e_botao_grid(self, app, banco, janelas):
        janela = janelas()
        assert janela.janela.title() == "COG - DOC_LIB. - SM AVULSO"
        assert "Gerar SM Avulso" in janela.btn_gerar.cget("text")

    def test_dica_do_botao_nao_tira_o_efeito_de_hover(self, app, banco, janelas):
        janela = janelas()
        for botao in (janela.btn_inverter, janela.periodo["p1"]["botao"]):
            assert estado(botao) == "normal"
            fundo, fundo_hover, _ = app.SGA_ESTILOS_BOTAO[botao._doclib_estilo]
            botao.event_generate("<Enter>")
            app.root.update()
            assert str(botao.cget("bg")) == fundo_hover
            botao.event_generate("<Leave>")
            app.root.update()
            assert str(botao.cget("bg")) == fundo


class TestTabelaEquipamentos:
    def test_caracterizacao_e_local_da_execucao_sao_listas_de_selecao(self, app, banco, janelas):
        janela = janelas()
        for indice in range(3):
            caracterizacao, local = janela.equip[indice]["caracterizacao"], janela.equip[indice]["local_execucao"]
            assert caracterizacao.winfo_class() == "TCombobox" and local.winfo_class() == "TCombobox"
            assert estado(caracterizacao) == "readonly" and estado(local) == "readonly"          # não aceitam texto livre
            assert list(caracterizacao.cget("values")) == app.DOC_LIB_CARACTERIZACOES_SM and len(app.DOC_LIB_CARACTERIZACOES_SM) == 44
            assert list(local.cget("values")) == app.DOC_LIB_LOCAIS_EXECUCAO_SM and len(app.DOC_LIB_LOCAIS_EXECUCAO_SM) == 30
            assert caracterizacao.get() == "" and local.get() == ""
        for campo in ("local", "instalacao", "equipamento"):
            assert janela.equip[0][campo].winfo_class() == "Entry"

    def test_escolha_da_lista_e_coletada_e_gravada(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        janela.equip[0]["caracterizacao"].set("Com risco desligamento das UG-1, 2, 3 e 4")
        janela.equip[0]["local_execucao"].current(app.DOC_LIB_LOCAIS_EXECUCAO_SM.index("EOL Ventos de Horizonte"))
        janela.salvar()
        assert not mensagens.avisos and janela.status == EM_ANALISE
        gravado = app.doc_lib_carregar_sm(janela.sm_id)["equipamentos"][0]
        assert gravado["caracterizacao"] == "Com risco desligamento das UG-1, 2, 3 e 4"
        assert gravado["local_execucao"] == "EOL Ventos de Horizonte"

    def test_lista_vazia_marca_o_combobox_em_vermelho_e_nao_grava(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        janela.equip[0]["caracterizacao"].set("")
        janela.equip[0]["local_execucao"].set("")
        janela.salvar()
        texto = mensagens.avisos[-1][1]
        assert "3.4 Caracterização: selecione uma opção da lista" in texto and "3.5 Local da Execução do(s) Serviço(s): selecione" in texto
        assert str(janela.equip[0]["caracterizacao"].cget("style")) == "DocLibErro.TCombobox"
        assert janela.sm_id is None
        janela.equip[0]["caracterizacao"].event_generate("<<ComboboxSelected>>")            # ao escolher, a marca sai
        assert str(janela.equip[0]["caracterizacao"].cget("style")) != "DocLibErro.TCombobox"

    def test_tempo_de_retorno_indisponivel_ou_hh_mm_como_no_ai(self, app, banco, janelas):
        janela = janelas()
        entrada, modo = janela.equip[0]["tempo_retorno"], janela.tempo_modo[0]
        assert modo.get() == "" and travado(entrada) and janela._equip_valor(0, "tempo_retorno") == ""
        entrada.event_generate("<Button-1>")                                                  # clicar no campo escolhe a opção do tempo
        assert modo.get() == "tempo" and not travado(entrada)
        definir(app, entrada, "0930")
        janela._ao_sair_campo(entrada, "hora", False)
        assert janela._equip_valor(0, "tempo_retorno") == "09:30"
        modo.set("indisponivel")                                                              # Indisponível limpa e trava o campo
        janela._ao_mudar_tempo(0)
        assert entrada.get() == "" and travado(entrada) and janela._equip_valor(0, "tempo_retorno") == "Indisponível"
        modo.set("tempo")
        janela._ao_mudar_tempo(0, True)
        assert not travado(entrada) and janela._equip_valor(0, "tempo_retorno") == ""

    def test_indisponivel_e_gravado_e_reaberto(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        preencher_equipamento(app, janela, 1, tempo="Indisponível", caracterizacao="Com desligamento da LT", local_execucao="Ao longo da LT",
                              local="se igu")
        janela.salvar()
        assert not mensagens.avisos
        doc = app.doc_lib_carregar_sm(janela.sm_id)
        assert [i["tempo_retorno"] for i in doc["equipamentos"]] == ["02:30", "Indisponível", ""] and doc["equipamentos"][1]["local"] == "SE IGU"
        outra = janelas()
        outra._carregar_documento(doc)
        assert outra.tempo_modo[1].get() == "indisponivel" and outra.equip[1]["tempo_retorno"].get() == "" and travado(outra.equip[1]["tempo_retorno"])
        assert outra._equip_valor(1, "tempo_retorno") == "Indisponível" and outra.tempo_modo[2].get() == ""

    def test_sem_escolher_o_tempo_a_primeira_linha_e_recusada(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        janela.tempo_modo[0].set("")
        janela._ao_mudar_tempo(0)
        janela.salvar()
        assert "3.6 Tempo Retorno à Operação: selecione Indisponível ou informe o tempo" in mensagens.avisos[-1][1]

    def test_campos_de_texto_ficam_em_caixa_alta_enquanto_se_digita(self, app, banco, janelas):
        janela = janelas()
        for campo in ("local", "instalacao", "equipamento"):
            entrada = janela.equip[0][campo]
            entrada.focus_force()
            janela.janela.update()
            entrada.insert("end", "dj 52-1 ação")
            entrada.event_generate("<KeyRelease>", keysym="a")
            janela.janela.update()
            assert entrada.get() == "DJ 52-1 AÇÃO", campo
        linha = janela.tab_lib.linhas[0]
        linha["local"].focus_force()
        for caractere in "se mcp":
            linha["local"].insert("end", caractere)
        linha["local"].event_generate("<KeyRelease>", keysym="a")
        assert linha["local"].get() == "SE MCP"

    def test_local_das_manobras_em_caixa_alta_na_liberacao_e_na_normalizacao(self, app, banco, janelas):
        janela = janelas()
        janela.tab_lib.preencher([{"numero": "1", "local": "se igu", "acao": "Abrir DJ"}])
        janela.tab_nor.preencher([{"numero": "1", "local": "cog", "acao": "Fechar DJ"}])
        assert janela.tab_lib.coletar()[0]["local"] == "SE IGU" and janela.tab_nor.coletar()[0]["local"] == "COG"

    def test_tabela_travada_depois_de_salvar_e_liberada_pelo_editar(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        janela.salvar()
        campos = [janela.equip[0][c] for c in ("local", "instalacao", "equipamento", "caracterizacao", "local_execucao", "tempo_retorno")]
        assert all(travado(widget) for widget in campos)
        assert all(estado(rad) == "disabled" for rad in janela.equip[0]["tempo_retorno"].master.winfo_children() if rad.winfo_class() == "Radiobutton")
        janela.editar()
        assert all(liberado(widget) for widget in campos)
        janela.tempo_modo[0].set("indisponivel")
        janela._ao_mudar_tempo(0)
        assert travado(janela.equip[0]["tempo_retorno"]) and liberado(janela.equip[0]["caracterizacao"])


class TestBloqueioDosItens6e7:
    def test_aprovado_aceita_horarios_e_executantes_e_em_execucao_bloqueia(self, app, banco, janelas, fluxo):
        sm_id = fluxo.ate(APROVADO)
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        assert not travado(janela.tab_lib.linhas[0]["data"]) and not travado(janela.ent_exec_lib_local) and not travado(janela.ent_exec_lib_remoto)
        fluxo.executar(sm_id)
        janela._carregar_documento(fluxo.doc(sm_id))
        assert janela.status == EM_EXECUCAO
        for linha in janela.tab_lib.linhas:
            assert all(travado(linha[campo]) for campo in ("data", "hora", "icone", "numero", "local", "acao"))
            assert all(estado(linha[botao]) == "disabled" for botao in ("btn_subir", "btn_descer", "btn_remover"))
        assert travado(janela.ent_exec_lib_local) and travado(janela.ent_exec_lib_remoto) and estado(janela.tab_lib.btn_adicionar) == "disabled"
        # o item 8 e os executantes da normalização continuam liberados até a conclusão
        assert not travado(janela.tab_nor.linhas[0]["data"]) and not travado(janela.ent_exec_nor_local)

    def test_tentativa_de_alterar_o_item_6_pela_janela_e_recusada_pelo_banco(self, app, banco, janelas, fluxo, mensagens):
        sm_id = fluxo.ate(EM_EXECUCAO)
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        definir(app, janela.tab_lib.linhas[0]["hora"], "07:00")                     # (campo travado: só por um defeito da tela)
        janela.salvar()
        assert mensagens.avisos and "Data e hora das manobras de liberação" in mensagens.avisos[-1][1]
        assert app.doc_lib_carregar_sm(sm_id)["liberacao"][0]["hora"] == "08:00"


class TestOrdemDosHorariosPelaJanela:
    """Item 6 e item 8: número arábico maior nunca antes de número menor; com o mesmo número a letra não conta."""

    @staticmethod
    def datar(app, tabela, horas):
        for linha, hora in zip(tabela.linhas, horas):
            definir(app, linha["data"], "25/10/2026")
            definir(app, linha["hora"], hora)

    def test_liberacao_2a_antes_de_1a_e_recusada_e_marcada_na_linha(self, app, banco, janelas, fluxo, mensagens):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(APROVADO)))                         # liberação: 1A, 1B, 2A
        self.datar(app, janela.tab_lib, ("08:30", "08:40", "08:10"))                      # 2A (08:10) antes de 1B (08:40)
        janela.salvar()
        texto = mensagens.avisos[-1][1]
        assert "linha 3 (sequência 2A)" in texto and "sequência 1B (linha 2)" in texto and "número arábico menor" in texto
        assert str(janela.tab_lib.linhas[2]["data"].cget("highlightbackground")) == app.SGA_VERMELHO
        assert str(janela.tab_lib.linhas[2]["hora"].cget("highlightbackground")) == app.SGA_VERMELHO
        assert str(janela.tab_lib.linhas[0]["hora"].cget("highlightbackground")) != app.SGA_VERMELHO
        assert fluxo.doc(janela.sm_id)["liberacao"][0]["hora"] in (None, "")                # nada foi gravado

    def test_mesma_sequencia_em_qualquer_ordem_e_aceita(self, app, banco, janelas, fluxo, mensagens):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(APROVADO)))
        self.datar(app, janela.tab_lib, ("08:30", "08:10", "08:30"))                      # 1B (08:10) antes de 1A (08:30); 2A igual
        janela.salvar()
        assert not mensagens.avisos
        assert [m["hora"] for m in fluxo.doc(janela.sm_id)["liberacao"]] == ["08:30", "08:10", "08:30"]

    def test_normalizacao_segue_a_mesma_regra(self, app, banco, janelas, fluxo, mensagens):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(EM_EXECUCAO)))                      # normalização: 1A, 2A, 2B
        self.datar(app, janela.tab_nor, ("10:00", "10:30", "10:05"))                      # 2B antes de 2A: livre
        janela.salvar()
        assert not mensagens.avisos
        self.datar(app, janela.tab_nor, ("10:00", "09:59", "10:05"))                      # 2A antes de 1A: recusado
        janela.salvar()
        assert "Manobras de Normalização, linha 2 (sequência 2A)" in mensagens.avisos[-1][1]

    def test_dicas_dos_itens_6_e_8_explicam_a_regra(self, app, banco, janelas):
        janela = janelas()
        fontes = [w.cget("text") for w in _todos_os_widgets(janela.janela) if w.winfo_class() == "Label"]
        assert sum("a letra não conta" in texto for texto in fontes) == 2


def _todos_os_widgets(raiz):
    for filho in raiz.winfo_children():
        yield filho
        yield from _todos_os_widgets(filho)


class TestRotulosDaConferencia:
    def test_botoes_e_modalidades_manutencao_e_operacao(self, app, banco, janelas, fluxo):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(AGUARDA)))
        conferencias = janela.conferencias
        assert conferencias.btn_manual.cget("text") == "Conferência Manutenção" and conferencias.btn_sistema.cget("text") == "Conferência Operação"
        assert app.DOC_LIB_MODALIDADES_SM == {"manual": "Manutenção", "sistema": "Operação"}
        manutencao, operacao = conferencias.adicionar_nova("manual"), conferencias.adicionar_nova("sistema")
        assert (manutencao["selo"].cget("text"), operacao["selo"].cget("text")) == ("Manutenção", "Operação")
        assert "Manual" not in {linha["selo"].cget("text") for linha in conferencias.linhas}
        definir(app, manutencao["nome"], "Joao da Manutencao")
        janela.salvar()
        assert janela.status == APROVADO
        assert [linha["selo"].cget("text") for linha in conferencias.linhas] == ["Manutenção", "Operação"]
        assert [c["modalidade"] for c in app.doc_lib_carregar_sm(janela.sm_id)["conferencias"]] == ["manual", "sistema"]    # valores gravados

    def test_mensagem_ao_registrar_uma_so_conferencia(self, app, banco, janelas, fluxo, mensagens, dialogos):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(AGUARDA)))
        linha = janela.conferencias.adicionar_nova("manual")
        definir(app, linha["nome"], "Joao da Manutencao")
        janela.salvar()
        assert "Conferência Manutenção E uma Conferência Operação" in mensagens.infos[-1][1] and janela.status == AGUARDA


class TestReprogramacoes:
    def test_habilitacao_em_ordem_e_dados_preservados(self, app, banco, janelas):
        janela = janelas()
        preencher(app, janela)
        p = janela.periodo
        assert estado(p["p1"]["botao"]) == "normal" and estado(p["p2"]["botao"]) == "disabled" \
            and estado(p["p3"]["botao"]) == "disabled"
        janela.habilitar_reprogramacao("p3")                         # fora de ordem: ignorado
        janela.habilitar_reprogramacao("p2")
        assert janela.reprogramacoes_habilitadas == 0 and travado(p["p3"]["data_inicio"])
        janela.habilitar_reprogramacao("p1")
        assert janela.reprogramacoes_habilitadas == 1 and not travado(p["p1"]["data_inicio"]) and travado(p["p2"]["data_inicio"])
        assert estado(p["p1"]["botao"]) == "disabled" and p["p1"]["botao"].cget("text") == "Habilitada"
        assert estado(p["p2"]["botao"]) == "normal" and estado(p["p3"]["botao"]) == "disabled"
        definir(app, p["p1"]["data_inicio"], "26/10/2026")
        janela.habilitar_reprogramacao("p2")
        janela.habilitar_reprogramacao("p3")
        assert janela.reprogramacoes_habilitadas == 3 and all(not travado(p["p3"][c]) for c in ("data_inicio", "hora_termino"))
        assert p["p0"]["data_inicio"].get() == "25/10/2026" and p["p1"]["data_inicio"].get() == "26/10/2026"   # preservados

    def test_reprogramacoes_salvas_e_reabertas(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        janela.habilitar_reprogramacao("p1")
        for campo, valor in (("data_inicio", "26/10/2026"), ("hora_inicio", "09:00"), ("data_termino", "26/10/2026"),
                             ("hora_termino", "18:00")):
            definir(app, janela.periodo["p1"][campo], valor)
        janela.habilitar_reprogramacao("p2")
        janela.salvar()
        assert not mensagens.avisos and janela.status == EM_ANALISE
        doc = app.doc_lib_carregar_sm(janela.sm_id)
        assert doc["reprogramacoes"] == 2 and doc["p1_hora_termino"] == "18:00" and not doc["p2_data_inicio"]
        outra = janelas()
        outra._carregar_documento(doc)
        assert outra.reprogramacoes_habilitadas == 2 and outra.periodo["p1"]["hora_inicio"].get() == "09:00"
        assert outra.periodo["p0"]["data_inicio"].get() == "25/10/2026"

    def test_reprogramacao_depois_de_gerada_a_sm(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        janela.salvar()
        janela.gerar()
        assert janela.status == AGUARDA and travado(janela.periodo["p0"]["data_inicio"])
        assert estado(janela.periodo["p1"]["botao"]) == "normal"             # a reprogramação ainda pode ser habilitada
        janela.habilitar_reprogramacao("p1")
        for campo, valor in (("data_inicio", "27/10/2026"), ("hora_inicio", "09:00"), ("data_termino", "27/10/2026"),
                             ("hora_termino", "18:00")):
            definir(app, janela.periodo["p1"][campo], valor)
        janela._atualizar_estado()
        assert estado(janela.btn_salvar) == "normal" and estado(janela.btn_gerar) == "disabled"
        janela.salvar()
        assert app.doc_lib_carregar_sm(janela.sm_id)["p1_data_inicio"] == "27/10/2026" and janela.status == AGUARDA


class TestTabelasDeManobras:
    def test_comeca_com_uma_linha_e_vai_ate_trinta(self, app, banco, janelas):
        tabela = janelas().tab_lib
        assert len(tabela.linhas) == 1 and estado(tabela.btn_adicionar) == "normal"
        for _ in range(29):
            tabela._ao_adicionar()
        assert len(tabela.linhas) == 30 and estado(tabela.btn_adicionar) == "disabled"
        assert tabela.adicionar_linha() is None and len(tabela.linhas) == 30
        assert tabela.lbl_contador.cget("text") == "30 de 30 manobras"

    def test_letra_automatica_acompanha_numero_inclusao_exclusao_e_ordem(self, app, banco, janelas):
        tabela = janelas().tab_lib
        tabela.preencher([{"numero": n, "local": "SE", "acao": f"acao {i}"} for i, n in enumerate("1112334", start=1)])
        letras = lambda: [linha["letra"].cget("text") for linha in tabela.linhas]
        assert letras() == ["A", "B", "C", "A", "A", "B", "A"]
        definir(app, tabela.linhas[1]["numero"], "2")                            # troca de número: recalcula
        tabela.atualizar_identificacoes()
        assert letras() == ["A", "A", "B", "B", "A", "B", "A"]
        tabela.remover_linha(tabela.linhas[0])                                   # exclusão
        assert [linha["numero"].get() for linha in tabela.linhas] == ["2", "1", "2", "3", "3", "4"]
        assert letras() == ["A", "A", "B", "A", "B", "A"]                        # 2A 1A 2B 3A 3B 4A
        tabela.mover(tabela.linhas[3], -1)                                       # troca de ordem
        assert [linha["numero"].get() for linha in tabela.linhas] == ["2", "1", "3", "2", "3", "4"]
        assert letras() == ["A", "A", "A", "B", "B", "A"]                        # 2A 1A 3A 2B 3B 4A
        tabela._ao_adicionar()                                                   # inclusão
        assert len(tabela.linhas) == 7 and letras()[-1] == ""

    def test_numero_aceita_somente_ate_dois_digitos(self, app, banco, janelas):
        linha = janelas().tab_lib.linhas[0]
        for caractere in "1a2x3":
            linha["numero"].insert("end", caractere)
        assert linha["numero"].get() == "12"

    def test_local_aceita_no_maximo_seis_caracteres(self, app, banco, janelas):
        linha = janelas().tab_lib.linhas[0]
        for caractere in "SE MCP-1":
            linha["local"].insert("end", caractere)
        assert linha["local"].get() == "SE MCP"

    def test_acao_quebra_a_linha_e_a_altura_acompanha(self, app, banco, janelas):
        janela = janelas()
        linha = janela.tab_lib.linhas[0]
        janela._definir_texto(linha["acao"], "Abrir o disjuntor 52-1 do vão de linha e confirmar a posição aberta " * 6)
        janela.janela.update()
        janela.tab_lib._ajustar_altura(linha)
        janela.janela.update()
        assert int(linha["acao"].cget("height")) > 1
        assert linha["acao"].winfo_width() > linha["local"].winfo_width() * 3        # a Ação é a coluna mais larga

    def test_remover_a_unica_linha_apenas_limpa(self, app, banco, janelas):
        tabela = janelas().tab_lib
        definir(app, tabela.linhas[0]["local"], "SE")
        tabela.remover_linha(tabela.linhas[0])
        assert len(tabela.linhas) == 1 and tabela.linhas[0]["local"].get() == ""

    def test_linhas_vazias_somem_ao_salvar(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        janela.tab_lib._ao_adicionar()
        janela.tab_lib._ao_adicionar()
        janela.salvar()
        assert len(janela.tab_lib.linhas) == 3 and not mensagens.avisos


class TestSalvarEValidacoes:
    def test_condicao_em_branco_marca_o_campo_e_nao_grava(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        janela._definir_texto(janela.txt_condicoes["cond_loto_sem"], "   ")
        janela.salvar()
        assert mensagens.avisos and "5.4.2 Sem bloqueio por LOTO" in mensagens.avisos[-1][1]
        assert str(janela.txt_condicoes["cond_loto_sem"].cget("highlightbackground")) == app.SGA_VERMELHO
        assert janela.sm_id is None and app.doc_lib_numeros_previstos(1, "SM") == ["0001/26"]

    @pytest.mark.parametrize("campo", ["cond_chaves_abertas", "cond_chaves_fechadas", "cond_disjuntores", "cond_loto_com",
                                       "cond_loto_sem"])
    def test_cada_condicao_e_obrigatoria_na_interface(self, app, banco, janelas, mensagens, campo):
        janela = janelas()
        preencher(app, janela)
        janela._definir_texto(janela.txt_condicoes[campo], "")
        janela.salvar()
        assert mensagens.avisos and janela.sm_id is None

    def test_hora_e_tempo_de_retorno_invalidos(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        definir(app, janela.equip[0]["tempo_retorno"], "25:99")
        definir(app, janela.periodo["p0"]["hora_inicio"], "7x")
        janela.salvar()
        texto = mensagens.avisos[-1][1]
        assert "tempo inválido" in texto and "hora inválida" in texto
        assert janela.sm_id is None

    def test_tempo_de_retorno_e_normalizado_ao_sair_do_campo(self, app, banco, janelas):
        janela = janelas()
        janela.tempo_modo[0].set("tempo")
        janela._ao_mudar_tempo(0, True)
        entrada = janela.equip[0]["tempo_retorno"]
        definir(app, entrada, "1h30")
        janela._ao_sair_campo(entrada, "hora", False)
        assert entrada.get() == "01:30" and janela._equip_valor(0, "tempo_retorno") == "01:30"

    def test_motivo_mostra_o_contador_e_recusa_mais_de_seis_linhas(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela, motivo="\n".join(f"Linha {i}" for i in range(1, 8)))
        janela._atualizar_contador_motivo()
        assert janela.lbl_linhas_motivo.cget("text") == "7 de 6 linhas" and str(janela.lbl_linhas_motivo.cget("fg")) == app.SGA_VERMELHO
        janela.salvar()
        assert "Motivo" in mensagens.avisos[-1][1] and janela.sm_id is None
        janela._definir_texto(janela.txt_motivo, "\n".join(f"Linha {i}" for i in range(1, 7)))
        janela._atualizar_contador_motivo()
        assert janela.lbl_linhas_motivo.cget("text") == "6 de 6 linhas"

    def test_salvar_grava_trava_os_campos_e_habilita_editar_e_gerar(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        janela.salvar()
        assert janela.status == EM_ANALISE and janela.numero == "0001/26" and janela.lbl_numero.cget("text") == "0001/26"
        assert "SM salva com sucesso" in mensagens.infos[-1][1]
        assert habilitados(janela) == {"voltar", "editar", "gerar", "reservar", "cancelar", "referencia"}
        assert travado(janela.equip[0]["local"]) and travado(janela.periodo["p0"]["data_inicio"])
        assert estado(janela.txt_motivo) == "disabled" and estado(janela.tab_lib.btn_adicionar) == "disabled"
        assert estado(janela.btn_inverter) == "disabled" and travado(janela.ent_exec_lib_local)
        janela.editar()
        assert not travado(janela.equip[0]["local"]) and habilitados(janela) >= {"salvar"} and "gerar" not in habilitados(janela)
        assert estado(janela.btn_inverter) == "normal"

    def test_dados_salvos_sao_recuperados_na_reabertura(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        janela.salvar()
        outra = janelas()
        outra._carregar_documento(app.doc_lib_carregar_sm(janela.sm_id))
        assert outra._equip_valor(0, "tempo_retorno") == "02:30" and outra.tempo_modo[0].get() == "tempo"
        assert outra.equip[0]["equipamento"].get() == "DJ 52-1" and outra.equip[0]["local"].get() == "SE MCP"
        assert outra.equip[0]["instalacao"].get() == "PÁTIO 230 KV" and outra.equip[0]["local_execucao"].get() == "UHE MGP"
        assert outra.equip[0]["caracterizacao"].get() == "Sem desligamento de UG/LT"
        assert [linha["letra"].cget("text") for linha in outra.tab_lib.linhas] == ["A", "B", "A"]
        assert [linha["acao"].get("1.0", "end-1c") for linha in outra.tab_nor.linhas][2] == "Fechar DJ 52-1"
        assert outra._texto(outra.txt_condicoes["cond_loto_com"]) == "Nenhuma"
        assert outra.numero == "0001/26" and outra.status == EM_ANALISE

    def test_voltar_pergunta_antes_de_descartar_alteracoes(self, app, banco, janelas, mensagens):
        janela = janelas()
        mensagens.resposta = False
        janela._definir_texto(janela.txt_motivo, "algo digitado")
        janela.voltar()
        assert mensagens.perguntas and janela.janela.winfo_exists()
        mensagens.resposta = True
        janela.voltar()
        assert not janela.janela.winfo_exists()


class TestFluxoCompletoPelaInterface:
    def test_do_salvamento_a_conclusao(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        janela.salvar()
        # --- Em análise -> Aguarda Conferência
        janela.gerar()
        assert janela.status == AGUARDA and janela.emitido and dialogos["gerado"]
        assert mensagens.perguntas and "Aguarda Conferência" in mensagens.perguntas[-1][1]
        assert travado(janela.equip[0]["local"]) and estado(janela.tab_lib.btn_adicionar) == "disabled"
        assert estado(janela.conferencias.btn_manual) == "normal" and estado(janela.conferencias.btn_sistema) == "normal"
        assert travado(janela.ent_exec_lib_local) and travado(janela.tab_lib.linhas[0]["data"])      # ainda não
        # --- só a conferência manual: continua aguardando
        conferencias = janela.conferencias
        linha = conferencias.adicionar_nova("manual")
        assert linha["area"].get() == "Manutenção" and linha["ass"].get() == "via fonia"
        assert linha["selo"].cget("text") == "Manutenção"
        assert linha["data"].get() == datetime.now().strftime("%d/%m/%Y") and linha["modalidade"] == "manual"
        janela.salvar()
        assert mensagens.avisos and "Conferido por" in mensagens.avisos[-1][1]               # nome obrigatório
        definir(app, linha["nome"], "Joao da Manutencao")
        janela.salvar()
        assert janela.status == AGUARDA and conferencias.linhas[0]["registrada"]
        assert travado(conferencias.linhas[0]["nome"])
        # --- conferência pelo sistema completa a aprovação
        linha = conferencias.adicionar_nova("sistema")
        assert linha["nome"].get() == "operador1" and linha["ass"].get() == "operador1" and linha["area"].get() == "COG"
        assert linha["selo"].cget("text") == "Operação"
        assert travado(linha["nome"]) and travado(linha["ass"]) and not travado(linha["area"])
        janela.salvar()
        assert janela.status == APROVADO and len(app.doc_lib_carregar_sm(janela.sm_id)["conferencias"]) == 2
        assert estado(conferencias.btn_manual) == "disabled"
        # --- Aprovado: horários das manobras de liberação e executantes
        assert not travado(janela.tab_lib.linhas[0]["data"]) and travado(janela.tab_nor.linhas[0]["data"])
        assert not travado(janela.ent_exec_lib_local) and travado(janela.ent_exec_nor_local)
        for indice, linha_lib in enumerate(janela.tab_lib.linhas):
            definir(app, linha_lib["data"], "25/10/2026")
            definir(app, linha_lib["hora"], f"13:{indice * 10:02d}")
        definir(app, janela.ent_exec_lib_local, "Fulano (campo)")
        janela.salvar()
        assert janela.status == EM_EXECUCAO
        # itens 6 e 7 (horários e executantes da liberação) ficam desabilitados para qualquer lançamento
        assert all(travado(linha_lib[campo]) for linha_lib in janela.tab_lib.linhas for campo in ("data", "hora", "icone"))
        assert travado(janela.ent_exec_lib_local) and travado(janela.ent_exec_lib_remoto)
        assert janela.tab_lib.linhas[0]["data"].get() == "25/10/2026" and janela.ent_exec_lib_local.get() == "Fulano (campo)"
        # --- Em Execução: normalização e conclusão
        assert not travado(janela.tab_nor.linhas[0]["data"]) and not travado(janela.ent_exec_nor_local)
        assert estado(janela.btn_cancelar) == "normal"
        for indice, linha_nor in enumerate(janela.tab_nor.linhas):
            definir(app, linha_nor["data"], "25/10/2026")
            definir(app, linha_nor["hora"], f"15:{indice * 10:02d}")
        definir(app, janela.ent_exec_nor_remoto, "Sicrano (COG)")
        janela.salvar()
        assert janela.status == CONCLUIDO and not mensagens.erros
        assert "cancelar" not in habilitados(janela) and "salvar" not in habilitados(janela)
        assert "gerar" in habilitados(janela) and "referencia" in habilitados(janela)
        assert all(travado(widget) for widget in (janela.ent_exec_nor_remoto, janela.tab_nor.linhas[0]["hora"],
                                                  janela.periodo["p1"]["data_inicio"]))

    def test_conclusao_recusada_com_manobra_sem_horario(self, app, banco, janelas, mensagens, dialogos, fluxo):
        sm_id = fluxo.ate(EM_EXECUCAO)
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        definir(app, janela.ent_exec_nor_local, "Fulano")
        janela.salvar()
        assert mensagens.avisos and "pendências de execução" in mensagens.avisos[-1][1] and janela.status == EM_EXECUCAO

    def test_conferencias_ate_dez_e_remocao_das_nao_registradas(self, app, banco, janelas, mensagens, dialogos, fluxo):
        sm_id = fluxo.ate(AGUARDA)
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        conferencias = janela.conferencias
        for _ in range(10):
            conferencias.adicionar_nova("manual")
        assert len(conferencias.linhas) == 10 and estado(conferencias.btn_manual) == "disabled"
        assert conferencias.adicionar_nova("sistema") is None
        conferencias.remover_linha(conferencias.linhas[-1])
        assert len(conferencias.linhas) == 9 and estado(conferencias.btn_sistema) == "normal"

    def test_botoes_acompanham_a_inclusao_e_a_remocao_de_conferencias_na_hora(self, app, banco, janelas, mensagens, dialogos, fluxo):
        janela = janelas()
        janela._carregar_documento(fluxo.doc(fluxo.ate(AGUARDA)))
        assert "salvar" not in habilitados(janela) and "gerar" in habilitados(janela)
        linha = janela.conferencias.adicionar_nova("manual")
        assert "salvar" in habilitados(janela) and "gerar" not in habilitados(janela)       # sem esperar a vigilância de 300 ms
        janela.conferencias.remover_linha(linha)
        assert "salvar" not in habilitados(janela) and "gerar" in habilitados(janela)

    def test_cancelar_em_qualquer_status_menos_concluido(self, app, banco, janelas, mensagens, dialogos, fluxo):
        for status in (EM_ANALISE, AGUARDA, APROVADO, EM_EXECUCAO):
            sm_id = fluxo.ate(status)
            janela = janelas()
            janela._carregar_documento(fluxo.doc(sm_id))
            assert estado(janela.btn_cancelar) == "normal"
            janela.cancelar_sm()
            assert janela.status == CANCELADO and janela.cancelada and "SM cancelada" in mensagens.infos[-1][0]
            assert habilitados(janela) == {"voltar", "gerar", "reservar", "referencia"}
            if status == EM_EXECUCAO:
                assert "EM EXECUÇÃO" in mensagens.perguntas[-1][1]          # aviso extra: a liberação já foi executada
        concluida = janelas()
        concluida._carregar_documento(fluxo.doc(fluxo.ate(CONCLUIDO)))
        assert estado(concluida.btn_cancelar) == "disabled"
        concluida.cancelar_sm()
        assert concluida.status == CONCLUIDO

    def test_cancelar_pode_ser_desistido(self, app, banco, janelas, mensagens, dialogos, fluxo):
        sm_id = fluxo.salvar()
        janela = janelas()
        janela._carregar_documento(fluxo.doc(sm_id))
        dialogos["justificativa"] = None                                     # o usuário fechou a justificativa
        janela.cancelar_sm()
        assert janela.status == EM_ANALISE
        mensagens.resposta = False
        dialogos["justificativa"] = "x"
        janela.cancelar_sm()
        assert janela.status == EM_ANALISE


class TestInverterManobras:
    def test_inverte_a_liberacao_sem_altera_la(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        antes = janela.tab_lib.coletar()
        janela.tab_nor.preencher([])
        janela.btn_inverter.invoke()
        assert janela.tab_lib.coletar() == antes
        nor = janela.tab_nor.coletar()
        assert [m["acao"] for m in nor] == ["Desbloquear seccionadora 89-1", "Fechar seccionadora 89-1", "Fechar DJ 52-1"]
        assert [m["numero"] for m in nor] == ["1", "2", "2"] and [m["local"] for m in nor] == ["SE MCP"] * 3
        assert [linha["letra"].cget("text") for linha in janela.tab_nor.linhas] == ["A", "A", "B"]
        assert mensagens.infos[-1][0] == "Inverter Manobras" and not mensagens.perguntas       # tabela vazia: sem confirmação

    def test_pede_confirmacao_antes_de_substituir_e_respeita_a_recusa(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        janela.tab_nor.preencher([{"numero": "1", "local": "COG", "acao": "Texto digitado à mão"}])
        antes = janela.tab_nor.coletar()
        mensagens.resposta = False
        janela.btn_inverter.invoke()
        assert mensagens.perguntas and "SUBSTITUI" in mensagens.perguntas[-1][1] and janela.tab_nor.coletar() == antes
        mensagens.resposta = True
        janela.btn_inverter.invoke()
        assert janela.tab_nor.coletar() != antes and len(janela.tab_nor.linhas) == 3

    def test_editar_manualmente_depois_de_gerada(self, app, banco, janelas, mensagens):
        janela = janelas()
        preencher(app, janela)
        janela.btn_inverter.invoke()
        linha = janela.tab_nor.linhas[0]
        janela._definir_texto(linha["acao"], "Texto ajustado à mão")
        assert janela.tab_nor.coletar()[0]["acao"] == "Texto ajustado à mão"

    def test_acao_sem_antonimo_inequivoco_fica_marcada_e_impede_a_geracao(self, app, banco, janelas, mensagens, dialogos):
        janela = janelas()
        preencher(app, janela)
        janela.tab_lib.preencher([{"numero": "1", "local": "SE", "acao": "Abrir DJ 52-1"},
                                  {"numero": "2", "local": "SE", "acao": "Isolar a linha e abrir 89-1"}])
        janela.btn_inverter.invoke()
        nor = janela.tab_nor.coletar()
        assert nor[0] == {"data": "", "hora": "", "numero": "1", "local": "SE", "acao": "Isolar a linha e abrir 89-1", "conferir": 1}
        assert nor[1]["conferir"] == 0 and nor[1]["acao"] == "Fechar DJ 52-1"
        assert "1 ação(ões) NÃO foram invertidas" in mensagens.infos[-1][1]
        marcada = janela.tab_nor.linhas[0]
        assert str(marcada["acao"].cget("highlightbackground")) == "#CC8400" and marcada["btn_conferir"].winfo_manager()
        janela.salvar()
        assert janela.status == EM_ANALISE
        janela.gerar()
        assert mensagens.avisos and "confira a ação" in mensagens.avisos[-1][1] and janela.status == EM_ANALISE
        janela.editar()
        assert janela.tab_nor.linhas[0]["conferir"] == 1                      # a marca foi gravada e reaparece ao reabrir
        janela.tab_nor.linhas[0]["btn_conferir"].invoke()                    # confirma que a ação mantida está correta
        assert janela.tab_nor.coletar()[0]["conferir"] == 0 and not janela.tab_nor.linhas[0]["btn_conferir"].winfo_manager()
        janela.salvar()
        janela.gerar()
        assert janela.status == AGUARDA

    def test_alterar_o_texto_da_acao_marcada_a_considera_conferida(self, app, banco, janelas, mensagens):
        janela = janelas()
        janela.tab_lib.preencher([{"numero": "1", "local": "SE", "acao": "Isolar a linha"}])
        janela.btn_inverter.invoke()
        linha = janela.tab_nor.linhas[0]
        assert linha["conferir"] == 1
        assert linha["acao"].bind("<KeyRelease>")                          # a digitação chama a conferência implícita
        linha["acao"].insert("end", " (conferido)")
        janela.tab_nor._ao_digitar_acao(linha)
        assert linha["conferir"] == 0 and not linha["btn_conferir"].winfo_manager()

    def test_exige_manobras_de_liberacao_e_so_vale_na_edicao_geral(self, app, banco, janelas, mensagens, fluxo):
        janela = janelas()
        janela.btn_inverter.invoke()
        assert "Informe as Manobras de Liberação" in mensagens.avisos[-1][1]
        sm_id = fluxo.ate(AGUARDA)
        emitida = janelas()
        emitida._carregar_documento(fluxo.doc(sm_id))
        assert estado(emitida.btn_inverter) == "disabled"


class TestReferenciaReservaGridEMenu:
    def test_sm_referencia_copia_o_aplicavel_e_zera_o_resto(self, app, banco, janelas, mensagens, dialogos, fluxo, monkeypatch):
        origem_id = fluxo.ate(CONCLUIDO)
        origem = janelas()
        origem._carregar_documento(fluxo.doc(origem_id))
        criadas = []
        original = app.JanelaSMAvulso
        monkeypatch.setattr(app, "JanelaSMAvulso", lambda **kw: criadas.append(original(**kw)) or criadas[-1])
        assert estado(origem.btn_referencia) == "normal"
        origem.referencia()
        nova = criadas[0]
        app.root.update()
        assert not origem.janela.winfo_exists()
        assert nova.referencia_numero == "0001/26" and "SM de referência: COG-0001/26" in nova.lbl_referencia.cget("text")
        assert nova.lbl_numero.cget("text") == "0002/26" and nova.status == "" and nova.sm_id is None
        assert nova._texto(nova.txt_motivo) == "Manutenção preventiva no disjuntor 52-1."
        assert nova.equip[0]["equipamento"].get() == "DJ 52-1" and nova._equip_valor(0, "tempo_retorno") == "02:30"
        assert nova.equip[0]["caracterizacao"].get() == "Sem desligamento de UG/LT" and nova.equip[0]["local_execucao"].get() == "UHE MGP"
        assert nova._texto(nova.txt_condicoes["cond_chaves_abertas"]) == "89-1 e 89-2"
        assert [m["acao"] for m in nova.tab_lib.coletar()] == ["Abrir DJ 52-1", "Abrir seccionadora 89-1",
                                                               "Bloquear seccionadora 89-1"]
        assert all(m["data"] == "" and m["hora"] == "" for m in nova.tab_lib.coletar() + nova.tab_nor.coletar())
        assert nova.ent_exec_lib_local.get() == "" and nova.ent_exec_nor_local.get() == "" and not nova.conferencias.linhas
        assert all(nova.periodo["p0"][campo].get() == "" for campo in ("data_inicio", "hora_inicio", "data_termino", "hora_termino"))
        assert nova.reprogramacoes_habilitadas == 0 and habilitados(nova) == {"voltar", "salvar", "reservar"}
        # a nova SM precisa do período; ao salvar recebe número novo, status Em análise e o vínculo com a origem
        for campo, valor in (("data_inicio", "01/11/2026"), ("hora_inicio", "08:00"), ("data_termino", "01/11/2026"),
                             ("hora_termino", "12:00")):
            definir(app, nova.periodo["p0"][campo], valor)
        nova.salvar()
        gravada = app.doc_lib_carregar_sm(nova.sm_id)
        assert (gravada["numero"], gravada["status"], gravada["emitido"], gravada["referencia_id"]) == \
            ("0002/26", EM_ANALISE, 0, origem_id)
        assert fluxo.doc(origem_id)["status"] == CONCLUIDO

    def test_referencia_pergunta_quando_ha_dados_nao_salvos_e_nao_vale_para_reservada(self, app, banco, janelas, mensagens, fluxo):
        janela = janelas()
        assert estado(janela.btn_referencia) == "disabled"                   # SM nova (ainda sem número)
        reservado = app.doc_lib_reservar_sm(1, "operador1")[0]["ateie_id"]
        janela._carregar_documento(fluxo.doc(reservado))
        assert estado(janela.btn_referencia) == "disabled"
        janela.referencia()
        assert janela.janela.winfo_exists()

    def test_reservar_numeros_e_preencher_a_reservada(self, app, banco, janelas, mensagens, dialogos, monkeypatch):
        janela = janelas()
        monkeypatch.setattr(app, "doc_lib_dialogo_reserva", lambda *args, **kw: kw["reservar_numeros"](2, "operador1", ""))
        janela.reservar()
        assert "0001/26, 0002/26" in mensagens.infos[-1][1] and janela.lbl_numero.cget("text") == "0003/26"
        reservada = app.doc_lib_listar_sm()[-1]
        outra = janelas()
        outra._carregar_documento(app.doc_lib_carregar_sm(reservada["ateie_id"]))
        assert outra.status == RESERVADO and outra.reservado and not travado(outra.equip[0]["local"])
        assert outra.ent_elaborado_area.get() == "COG"
        preencher(app, outra)
        outra.salvar()
        assert outra.numero == "0001/26" and outra.status == EM_ANALISE and "reservada preenchida" in mensagens.infos[-1][1]

    def test_gerar_uma_reservada_emite_formulario_em_branco_sem_mudar_o_status(self, app, banco, janelas, mensagens, dialogos, fluxo):
        reservado = app.doc_lib_reservar_sm(1, "operador1")[0]["ateie_id"]
        janela = janelas()
        janela._carregar_documento(fluxo.doc(reservado))
        janela.gerar()
        assert janela.status == RESERVADO and dialogos["gerado"] and "formulário em branco" in dialogos["gerado"][-1][2]

    def test_grid_lista_as_sms_com_o_botao_e_a_coluna_de_email(self, app, banco, janelas, fluxo):
        fluxo.ate(AGUARDA)
        fluxo.salvar()
        app.doc_lib_reservar_sm(1, "operador1")
        janela = janelas()
        grid = app.JanelaListaSM(janela.janela)
        app.root.update()
        try:
            textos = {widget.cget("text") for widget in grid.janela.winfo_children() if widget.winfo_class() == "Button"}
            assert "Abrir" in textos and "NOVA SM" in textos and "Voltar" in textos
            assert "Marcar e-mail enviado" in textos and not any("Agrupar" in texto for texto in textos)
            assert "Enviado e-mail" in [coluna[1] for coluna in grid.COLUNAS]
            assert {registro["email_enviado"] for registro in grid.registros} == {"Não"}
            assert [registro["numero"] for registro in grid.registros] == ["0003/26", "0002/26", "0001/26"]
            assert grid.valores_distintos("status") == [EM_ANALISE, AGUARDA, RESERVADO]
            assert grid.janela.title() == "GRID SM" and grid.contador.cget("text").startswith("3 de 3 SM(s)")
        finally:
            grid.janela.destroy()

    def test_grid_de_mo_e_ateie_continuam_com_o_botao_de_email(self, app, banco, janelas):
        janela = janelas()
        for classe in (app.JanelaListaMO, app.JanelaListaAI, app.JanelaListaAteie):
            grid = classe(janela.janela)
            app.root.update()
            try:
                textos = {w.cget("text") for w in grid.janela.winfo_children() if w.winfo_class() == "Button"}
                assert "Marcar e-mail enviado" in textos
            finally:
                grid.janela.destroy()

    def test_abrir_pelo_grid_carrega_a_sm_escolhida(self, app, banco, janelas, fluxo, monkeypatch, mensagens):
        sm_id = fluxo.ate(APROVADO)
        janela = janelas()
        monkeypatch.setattr(app, "doc_lib_escolher_sm", lambda parent: (sm_id, 1))
        janela._atualizar_estado()
        janela.abrir_salvo()
        assert janela.sm_id == sm_id and janela.status == APROVADO and len(janela.conferencias.linhas) == 2

    def test_menu_doc_lib_tem_as_quatro_opcoes_e_abre_a_sm(self, app, banco, janelas, monkeypatch, mensagens):
        menu = app.fileDOC_LIB
        rotulos = [menu.entrycget(i, "label") for i in range(menu.index("end") + 1) if menu.type(i) == "command"]
        assert rotulos[:4] == ["ATEIE", "AI", "MO", "SM_Avulso"]
        abertas = []
        monkeypatch.setattr(app, "JanelaSMAvulso", lambda: abertas.append(1))
        monkeypatch.setattr(app, "current_user", None)
        app.cmd_click25_sm_avulso()
        assert not abertas and "login" in mensagens.avisos[-1][1]
        monkeypatch.setattr(app, "current_user", "operador1 em 24/10/2026 - 10:00h")
        app.cmd_click25_sm_avulso()
        assert abertas == [1]

    def test_comando_do_menu_abre_a_janela_real(self, app, banco, mensagens):
        antes = set(app.root.winfo_children())
        app.cmd_click25_sm_avulso()
        app.root.update()
        novas = [w for w in app.root.winfo_children() if w not in antes and w.winfo_class() == "Toplevel"]
        try:
            assert any(w.title() == "COG - DOC_LIB. - SM AVULSO" for w in novas)
        finally:
            for w in novas:
                w.destroy()
