"""Infraestrutura dos testes automatizados do Doc_Lib. (Click_25).

O sistema é um único arquivo (main.py) que monta a janela principal ao ser importado. Aqui ele é carregado uma vez por
sessão, sem o mainloop final, dentro de uma pasta temporária (o banco dados_turno.db usado nos testes NUNCA é o de produção:
o caminho dele é relativo à pasta de trabalho). Cada teste recebe uma pasta e um banco novos.

Como executar (precisa de tkinter, tkcalendar, fpdf2, pandas, matplotlib, requests e pytest instalados):
    Windows ........ python -m pytest tests
    Linux sem tela . xvfb-run -a python -m pytest tests     (ou apenas pytest: o Xvfb é iniciado sozinho, se existir)
"""
import os
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carregar_main import carregar_main  # noqa: E402


def _garantir_tela():
    """Linux sem DISPLAY: inicia um Xvfb para o Tk poder abrir janelas."""
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY") and shutil.which("Xvfb"):
        processo = subprocess.Popen(["Xvfb", ":97", "-screen", "0", "1600x1000x24"], stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        os.environ["DISPLAY"] = ":97"
        return processo
    return None


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    """O main.py carregado como módulo (sem abrir o mainloop), em uma pasta temporária."""
    xvfb = _garantir_tela()
    pasta = tmp_path_factory.mktemp("cog_sessao")
    anterior = os.getcwd()
    modulo = carregar_main(str(pasta))
    yield modulo
    try:
        modulo.root.destroy()
    except Exception:
        pass
    os.chdir(anterior)
    if xvfb:
        xvfb.terminate()


@pytest.fixture()
def banco(app, tmp_path, monkeypatch):
    """Banco e pasta de arquivamento novos para o teste (o caminho do banco é relativo à pasta de trabalho)."""
    monkeypatch.chdir(tmp_path)
    arquivo = str(tmp_path / "doc_lib_arquivo")
    monkeypatch.setattr(app, "PASTA_ARQUIVO_DOC_LIB", arquivo)
    monkeypatch.setattr(app, "PASTA_ARQUIVO_DOC_LIB_LOCAL", arquivo)
    monkeypatch.setattr(app, "current_user", "operador1 em 24/10/2026 - 10:00h")
    app.garantir_banco_doc_lib()
    return tmp_path


@pytest.fixture()
def mensagens(app, monkeypatch):
    """Substitui as caixas de mensagem do Tk (que esperariam um clique): registra o que foi mostrado e responde 'sim' às
    perguntas (altere mensagens.resposta para responder 'não')."""
    class Registro:
        def __init__(self):
            self.avisos, self.infos, self.erros, self.perguntas = [], [], [], []
            self.resposta = True

    registro = Registro()
    monkeypatch.setattr(app.messagebox, "showwarning", lambda titulo, texto, **kw: registro.avisos.append((titulo, texto)))
    monkeypatch.setattr(app.messagebox, "showinfo", lambda titulo, texto, **kw: registro.infos.append((titulo, texto)))
    monkeypatch.setattr(app.messagebox, "showerror", lambda titulo, texto, **kw: registro.erros.append((titulo, texto)))
    monkeypatch.setattr(app.messagebox, "askyesno", lambda titulo, texto, **kw: (registro.perguntas.append((titulo, texto)),
                                                                                  registro.resposta)[1])
    return registro


class FluxoSM:
    """Atalhos para percorrer o ciclo de vida de uma SM Avulso nos testes (usa as mesmas funções do aplicativo)."""
    OPERADOR = "operador1"                       # quem elabora as SM dos testes
    CONFERENTE = "operador2"                     # quem as confere (a mesma pessoa não elabora e confere)

    def __init__(self, app):
        self.app = app

    def dados(self, **alteracoes):
        """Dados de uma SM nova, válida (programação em 25/10/2026, 3 manobras de liberação e 3 de normalização)."""
        dados = {
            "id": None, "revisao": None, "reprogramacoes": 0,
            "p0_data_inicio": "25/10/2026", "p0_hora_inicio": "08:00", "p0_data_termino": "25/10/2026",
            "p0_hora_termino": "17:00",
            "equipamentos": [{"local": "SE MCP", "instalacao": "PÁTIO 230 KV", "equipamento": "DJ 52-1",
                              "caracterizacao": "Sem desligamento de UG/LT", "local_execucao": "UHE MGP",
                              "tempo_retorno": "02:30"}],
            "motivo": "Manutenção preventiva no disjuntor 52-1.",
            "cond_chaves_abertas": "89-1 e 89-2", "cond_chaves_fechadas": "Nenhuma", "cond_disjuntores": "Nenhum",
            "cond_loto_com": "89-1", "cond_loto_sem": "Nenhuma",
            "liberacao": [{"numero": "1", "local": "SE MCP", "acao": "Abrir DJ 52-1"},
                          {"numero": "1", "local": "SE MCP", "acao": "Abrir seccionadora 89-1"},
                          {"numero": "2", "local": "SE MCP", "acao": "Bloquear seccionadora 89-1"}],
            "normalizacao": [{"numero": "1", "local": "SE MCP", "acao": "Desbloquear seccionadora 89-1"},
                             {"numero": "2", "local": "SE MCP", "acao": "Fechar seccionadora 89-1"},
                             {"numero": "2", "local": "SE MCP", "acao": "Fechar DJ 52-1"}],
            "observacoes": "", "elaborado_area": "COG", "elaborado_data": "24/10/2026", "conferencias": [],
            "exec_lib_local": "", "exec_lib_remoto": "", "exec_nor_local": "", "exec_nor_remoto": "",
        }
        dados.update(alteracoes)
        return dados

    def salvar(self, usuario=None, **alteracoes):
        return self.app.doc_lib_salvar_sm(self.dados(**alteracoes), usuario or self.OPERADOR)

    def doc(self, sm_id):
        return self.app.doc_lib_carregar_sm(sm_id)

    def alterar(self, sm_id, usuario=None, **alteracoes):
        """Salva alterações sobre a SM gravada (parte dos dados gravados, como a janela faz)."""
        import copy
        dados = copy.deepcopy(self.doc(sm_id))
        dados.update(alteracoes)
        return self.app.doc_lib_salvar_sm(dados, usuario or self.OPERADOR)

    def gerar(self, sm_id, usuario=None):
        return self.app.doc_lib_registrar_e_arquivar_sm(self.doc(sm_id), usuario or self.OPERADOR)

    def conferencia_manual(self, **valores):
        return dict({"modalidade": "manual", "nome": "Joao da Manutencao", "area": "Manutenção", "data": "25/10/2026",
                     "ass": "via fonia"}, **valores)

    def conferencia_sistema(self, **valores):
        return dict({"modalidade": "sistema", "nome": "digitado errado", "area": "COG", "data": "25/10/2026",
                     "ass": "digitado errado"}, **valores)

    def conferir(self, sm_id, *novas, usuario=None):
        """Registra as conferências informadas (as já gravadas são mantidas). Por padrão quem confere é OUTRA pessoa que não o
        elaborador (CONFERENTE): quem elabora a SM não a confere."""
        gravadas = self.doc(sm_id)["conferencias"]
        return self.alterar(sm_id, usuario=usuario or self.CONFERENTE, conferencias=gravadas + list(novas))

    def aprovar(self, sm_id):
        return self.conferir(sm_id, self.conferencia_manual(), self.conferencia_sistema())

    def datar(self, doc, chave, hora_inicial=8):
        """Lista de manobras com data e hora em ordem crescente (uma por dez minutos)."""
        manobras = []
        for indice, manobra in enumerate(doc[chave]):
            minutos = hora_inicial * 60 + indice * 10
            manobras.append(dict(manobra, data="25/10/2026", hora=f"{minutos // 60:02d}:{minutos % 60:02d}"))
        return manobras

    def executar(self, sm_id):
        """Executantes da liberação com todas as manobras de liberação datadas: a SM passa a Em Execução."""
        return self.alterar(sm_id, liberacao=self.datar(self.doc(sm_id), "liberacao", 8), exec_lib_local="Fulano (campo)")

    def concluir(self, sm_id):
        """Executantes da normalização com todas as manobras de normalização datadas: a SM passa a Concluído."""
        return self.alterar(sm_id, normalizacao=self.datar(self.doc(sm_id), "normalizacao", 16),
                            exec_nor_local="Fulano (campo)", exec_nor_remoto="Sicrano (COG)")

    def ate(self, status):
        """Cria uma SM e a leva até o status pedido; devolve o id."""
        sm_id = self.salvar()
        etapas = ["Em análise", "Aguarda Conferência", "Aprovado para Execução", "Em Execução", "Concluído"]
        for destino in etapas[1:etapas.index(status) + 1]:
            {"Aguarda Conferência": self.gerar, "Aprovado para Execução": self.aprovar, "Em Execução": self.executar,
             "Concluído": self.concluir}[destino](sm_id)
        assert self.doc(sm_id)["status"] == status
        return sm_id


@pytest.fixture()
def fluxo(app, banco):
    return FluxoSM(app)
