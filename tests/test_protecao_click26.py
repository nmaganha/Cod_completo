"""Proteção (Click_26): menu, janelas por equipamento e estrutura para receber cada proteção (Tk real, em tela virtual)."""
import pytest

PROTECOES = {
    "UG": ["12", "21G", "24", "49", "50", "64R", "64s1", "64s2", "67", "81O", "81U", "86", "87G"],
    "TR": ["26", "49", "50/51", "63", "87", "64R", "64s1", "64s2", "67", "71", "81O", "81U", "86", "87G", "97"],
    "LT": ["21", "27", "50BF", "67", "68", "78", "81O", "81U", "86", "87"],
    "BARRA": ["25", "50BF", "86", "87"],
    "RMT": ["50/51", "86", "87"],
    "AERO": ["50/51", "86", "87"],
    "UFV": ["50/51", "86", "87"],
}


def _todos(widget):
    yield widget
    for filho in widget.winfo_children():
        yield from _todos(filho)


def _textos(janela):
    return [w.cget("text") for w in _todos(janela) if w.winfo_class() == "Label" and w.cget("text")]


def _botoes(janela, texto):
    return [w for w in _todos(janela) if w.winfo_class() == "Button" and w.cget("text") == texto]


def _toplevels(app):
    return [w for w in app.root.winfo_children() if w.winfo_class() == "Toplevel"]


def _situacoes(janela):
    """{proteção: situação} lidas da lista da janela do equipamento (cabeçalho: 'Proteção', 'Situação')."""
    textos = _textos(janela)
    corpo = textos[textos.index("Situação") + 1:]
    corpo = [t for t in corpo if "proteção(ões)" not in t]
    return dict(zip(corpo[0::2], corpo[1::2]))


@pytest.fixture()
def protecao(app, mensagens, monkeypatch):
    """Usuário logado, registro de proteções vazio e as janelas criadas pelo teste fechadas ao final."""
    monkeypatch.setattr(app, "current_user", "operador1 em 30/10/2026 - 10:00h")
    monkeypatch.setattr(app, "PROTECAO_CONSTRUIDAS", {})
    monkeypatch.setattr(app, "_PROTECAO_JANELAS_ABERTAS", {})
    antes = set(_toplevels(app))
    yield mensagens
    for janela in _toplevels(app):
        if janela not in antes:
            janela.destroy()
    app.root.update()


def _abrir_equipamento(app, sigla):
    antes = set(_toplevels(app))
    app.janela_protecao(sigla)
    app.root.update()
    novas = [w for w in _toplevels(app) if w not in antes]
    assert len(novas) == 1
    return novas[0]


def test_cascade_protecao_fica_entre_doc_lib_e_admin(app):
    menu = app.meuMenu
    rotulos = [menu.entrycget(i, "label") for i in range(menu.index("end") + 1) if menu.type(i) == "cascade"]
    assert "Proteção." in rotulos
    assert rotulos.index("DOC_LIB.") + 1 == rotulos.index("Proteção.") == rotulos.index("ADMIN") - 1
    sub = app.filePROTECAO
    itens = [sub.entrycget(i, "label") for i in range(sub.index("end") + 1) if sub.type(i) == "command"]
    assert itens == ["UG", "TR", "LT", "BARRA", "RMT", "AERO", "UFV", "Sair"]


def test_menu_abre_a_janela_de_cada_equipamento(app, protecao):
    for posicao, sigla in enumerate(PROTECOES):
        antes = set(_toplevels(app))
        app.filePROTECAO.invoke(posicao)
        app.root.update()
        novas = [w for w in _toplevels(app) if w not in antes]
        assert [w.title() for w in novas] == [f"COG - Proteção - {sigla}"]


@pytest.mark.parametrize("sigla", list(PROTECOES))
def test_lista_de_protecoes_do_equipamento_toda_em_construcao(app, protecao, sigla):
    janela = _abrir_equipamento(app, sigla)
    situacoes = _situacoes(janela)
    assert list(situacoes) == PROTECOES[sigla]
    assert set(situacoes.values()) == {"Em construção"}
    assert not _botoes(janela, "Abrir")
    assert f"{len(PROTECOES[sigla])} proteção(ões) - 0 disponível(is)" in _textos(janela)
    _botoes(janela, "Voltar")[0].invoke()
    app.root.update()
    assert not janela.winfo_exists()


def test_sem_usuario_logado_avisa_e_nao_abre_janela(app, protecao, monkeypatch):
    monkeypatch.setattr(app, "current_user", None)
    antes = set(_toplevels(app))
    app.janela_protecao("UG")
    assert set(_toplevels(app)) == antes
    assert len(protecao.avisos) == 1


def test_protecao_registrada_fica_disponivel_e_abre_a_janela_padrao(app, protecao):
    chamadas = []

    @app.protecao_construida("UG", "87G")
    def construir_87g(sigla, funcao, corpo, rodape):
        chamadas.append((sigla, funcao))
        app.Label(corpo, text="CONTEUDO 87G").pack()
        app.Button(rodape, text="Salvar").place(x=10, y=10)

    lista = _abrir_equipamento(app, "UG")
    situacoes = _situacoes(lista)
    assert situacoes["87G"] == "Disponível"
    assert {c: s for c, s in situacoes.items() if c != "87G"} == {c: "Em construção" for c in PROTECOES["UG"][:-1]}
    assert "13 proteção(ões) - 1 disponível(is)" in _textos(lista)

    antes = set(_toplevels(app))
    _botoes(lista, "Abrir")[0].invoke()
    app.root.update()
    item = [w for w in _toplevels(app) if w not in antes]
    assert [w.title() for w in item] == ["COG - Proteção - UG - 87G"]
    assert chamadas == [("UG", "87G")]
    assert "UG - Proteção 87G" in _textos(item[0]) and "CONTEUDO 87G" in _textos(item[0])
    assert _botoes(item[0], "Voltar") and _botoes(item[0], "Salvar")

    _botoes(lista, "Abrir")[0].invoke()                    # já aberta: não abre outra nem chama o construtor de novo
    app.root.update()
    assert [w for w in _toplevels(app) if w not in antes] == item and len(chamadas) == 1

    _botoes(item[0], "Voltar")[0].invoke()
    app.root.update()
    assert not item[0].winfo_exists()
    _botoes(lista, "Abrir")[0].invoke()                    # fechada: abre de novo
    app.root.update()
    assert len(chamadas) == 2


def test_mesma_funcao_atende_varias_siglas(app, protecao):
    chamadas = []

    def construir_50_51(sigla, funcao, corpo, rodape):
        chamadas.append((sigla, funcao))

    for sigla in ("RMT", "AERO", "UFV"):
        app.protecao_construida(sigla, "50/51")(construir_50_51)
    for sigla in ("RMT", "AERO", "UFV"):
        lista = _abrir_equipamento(app, sigla)
        assert _situacoes(lista)["50/51"] == "Disponível"
        _botoes(lista, "Abrir")[0].invoke()
        app.root.update()
    assert chamadas == [("RMT", "50/51"), ("AERO", "50/51"), ("UFV", "50/51")]


def test_registro_recusa_sigla_ou_funcao_inexistente_e_duplicidade(app, protecao):
    with pytest.raises(ValueError):
        app.protecao_construida("XX", "87G")
    with pytest.raises(ValueError):
        app.protecao_construida("UG", "999")
    app.protecao_construida("UG", "87G")(lambda sigla, funcao, corpo, rodape: None)
    with pytest.raises(ValueError):
        app.protecao_construida("UG", "87G")
    assert list(app.PROTECAO_CONSTRUIDAS) == [("UG", "87G")]


def test_construtor_com_erro_nao_deixa_janela_pela_metade(app, protecao):
    def construir(sigla, funcao, corpo, rodape):
        raise RuntimeError("falha de teste")

    app.protecao_construida("TR", "26")(construir)
    antes = set(_toplevels(app))
    with pytest.raises(RuntimeError):
        app.abrir_protecao(app.root, "TR", "26")
    app.root.update()
    assert set(_toplevels(app)) == antes


def test_protecao_sem_construtor_continua_em_construcao(app, protecao):
    app.abrir_protecao(app.root, "UG", "12")
    assert protecao.infos == [("Proteção - UG - 12", "Em construção")]
