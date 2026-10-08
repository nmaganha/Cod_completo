# Código atualizado em 08-10-26 – 00:33h - (Click25: ATEIE - Observações padrão obrigatória e dica sob Equipamento de Interligação)
import sqlite3
from tkinter import *
# from tkinter import ttk, messagebox
from tkinter import Tk
from tkcalendar import Calendar
from datetime import datetime, timedelta
from fpdf import FPDF, XPos, YPos
import os
import platform
import shutil #exclusivo para o click24
import subprocess
import random #exclusivo para o click23
#import webbrowser
import pandas as pd
import json
import webbrowser
from tkinter import ttk, messagebox, Toplevel, Frame, Label, Button, Entry, Listbox, Scrollbar, END, BOTH, LEFT, RIGHT, \
    X, Y, VERTICAL, HORIZONTAL, filedialog
import requests  # exclusivo para o click22
import threading  # exclusivo para o click22
from concurrent.futures import ThreadPoolExecutor, as_completed #exclusivo para o click22
import re  # exclusivo para o click22 (destaque da instalação no PDF)
import unicodedata  # exclusivo para o click22 (destaque da instalação no PDF)
import base64  # exclusivo para o click22 (destaque da instalação no PDF)
import tempfile  # exclusivo para o click22 (destaque da instalação no PDF)
try:
    import pymupdf as fitz  # exclusivo para o click22 (destaque da instalação no PDF)
    PYMUPDF_DISPONIVEL = True
except ImportError:
    try:
        import fitz  # versões antigas do PyMuPDF
        PYMUPDF_DISPONIVEL = True
    except ImportError:
        fitz = None
        PYMUPDF_DISPONIVEL = False
from matplotlib.figure import Figure  # exclusivo para o click23
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # exclusivo para o click23

# ===========================================================================================
# TEMA VISUAL MODERNO - identidade única para TODAS as janelas do sistema
# ===========================================================================================
# Os componentes abaixo (Button, Label, Entry, Text, Toplevel, Frame, Checkbutton, ...) substituem
# os componentes padrão do Tkinter em todo o programa. Eles aceitam exatamente os mesmos parâmetros
# de antes, então nenhuma janela precisa ser reescrita: cores antigas são convertidas para a
# paleta atual, fontes Arial passam para Segoe UI, botões ficam planos com efeito ao passar o
# mouse e campos de texto ganham contorno que muda de cor ao receber o foco.
# Componentes que já definem 'relief' (como os dos módulos Click_23 e Click_24, que já têm
# visual próprio) são preservados como estão.
import tkinter as _tk
import tkinter.font as _tkfont

UI_FONTE = "Segoe UI"
UI_AZUL = "#024593"
UI_AZUL_ESCURO = "#013573"
UI_FUNDO = "#EEF2F7"
UI_CARD = "#FFFFFF"
UI_BORDA = "#D5DDE8"
UI_TEXTO = "#1F2937"
UI_TEXTO_SUAVE = "#6B7280"
UI_VERDE = "#0A7A2E"
UI_VERMELHO = "#B00000"
UI_NEUTRO = "#E3E8EF"
UI_NEUTRO_HOVER = "#D0D7E2"

# Cores antigas -> cores da paleta atual (aplicado a qualquer opção de cor de qualquer componente)
_UI_CORES = {
    "#a4bad2": UI_FUNDO,       # fundo antigo das janelas
    "#cdd505": UI_FUNDO,       # fundo antigo das janelas de filtro
    "#f0f0f0": UI_FUNDO,
    "#41719c": "#2F5F9E",      # painéis azuis dos simuladores
    "#ff0000": "#C62828",      # vermelho (Novo Cálculo, Fechar, Cancelar...)
    "#8b0000": "#8E1B1B",
    "#ff8c00": "#CC8400",
    "#808080": "#6B7280",
    "#cdcdcd": UI_NEUTRO,
    "#3498db": UI_AZUL,
    "#2196f3": UI_AZUL,
    "#1d9bff": UI_AZUL,
    "#2ecc71": "#079541",
    "#009f4d": "#079541",
    "#fff3cd": "#FFF6DD",
}
# Nomes de cor usados como texto (fg) -> cores da paleta
_UI_CORES_TEXTO = {
    "blue": UI_AZUL,
    "red": UI_VERMELHO,
    "green": UI_VERDE,
    "gray": UI_TEXTO_SUAVE,
    "#555": UI_TEXTO_SUAVE,
    "#666": UI_TEXTO_SUAVE,
}
_UI_OPCOES_COR = ("bg", "background", "fg", "foreground", "activebackground", "activeforeground",
                  "highlightbackground", "highlightcolor", "selectbackground", "selectforeground",
                  "disabledforeground", "insertbackground", "selectcolor", "troughcolor")
_UI_OPCOES_TEXTO = ("fg", "foreground", "activeforeground", "disabledforeground")
_UI_FONTES_ANTIGAS = ("arial", "helvetica", "tahoma", "verdana", "calibri", "times new roman")


def _ui_cor(opcao, valor):
    """Converte uma cor antiga para a cor equivalente da paleta atual."""
    if isinstance(valor, str):
        chave = valor.strip().lower()
        if opcao in _UI_OPCOES_TEXTO and chave in _UI_CORES_TEXTO:
            return _UI_CORES_TEXTO[chave]
        if chave in _UI_CORES:
            return _UI_CORES[chave]
    return valor


def _ui_fonte(valor):
    """Troca a família Arial (e similares) por Segoe UI, mantendo tamanho e estilo."""
    if isinstance(valor, (tuple, list)) and valor and isinstance(valor[0], str) \
            and valor[0].strip().lower() in _UI_FONTES_ANTIGAS:
        return (UI_FONTE,) + tuple(valor[1:])
    return valor


def _ui_ajustar(opcoes):
    """Aplica a conversão de cores e fontes ao conjunto de opções de um componente."""
    for opcao in list(opcoes):
        if opcao in _UI_OPCOES_COR:
            opcoes[opcao] = _ui_cor(opcao, opcoes[opcao])
        elif opcao == "font":
            opcoes[opcao] = _ui_fonte(opcoes[opcao])
    return opcoes


def _ui_juntar(cnf, kw):
    opcoes = dict(cnf or {})
    opcoes.update(kw)
    return _ui_ajustar(opcoes)


def _ui_escurecer(cor, fator=0.85):
    """Devolve a cor um pouco mais escura (usada no efeito ao passar o mouse)."""
    try:
        r, g, b = [c // 257 for c in _tk._default_root.winfo_rgb(cor)]
        return "#%02X%02X%02X" % (int(r * fator), int(g * fator), int(b * fator))
    except Exception:
        return cor


def _ui_e_escura(cor):
    try:
        r, g, b = [c // 257 for c in _tk._default_root.winfo_rgb(cor)]
        return (0.299 * r + 0.587 * g + 0.114 * b) < 150
    except Exception:
        return False


def _ui_fundo_do_pai(master):
    try:
        return master.cget("bg")
    except Exception:
        return UI_FUNDO


class _TemaWidget:
    """Mistura aplicada a todos os componentes: qualquer configure()/config()/widget['bg']=...
    posterior também passa pela conversão de cores e fontes."""

    def configure(self, cnf=None, **kw):
        if isinstance(cnf, dict):
            cnf = _ui_ajustar(dict(cnf))
        if kw:
            kw = _ui_ajustar(kw)
        return super().configure(cnf, **kw)

    config = configure


class Tk(_TemaWidget, _tk.Tk):
    """Janela principal (e qualquer outra janela raiz): já nasce com o tema global aplicado."""

    def __init__(self, *args, **kw):
        _tk.Tk.__init__(self, *args, **kw)
        _ui_aplicar_tema_global(self)


class Toplevel(_TemaWidget, _tk.Toplevel):
    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_juntar(cnf, kw)
        if "bg" not in kw and "background" not in kw:
            kw["bg"] = UI_FUNDO
        _tk.Toplevel.__init__(self, master, **kw)


def _ui_contorno_fino(kw):
    """Bordas 3D antigas (solid, ridge, groove, sunken) viram um contorno fino e suave."""
    if kw.get("relief") in ("solid", "ridge", "groove", "sunken", "raised"):
        for opcao in ("relief", "bd", "borderwidth"):
            kw.pop(opcao, None)
        kw.update(relief="flat", bd=0, highlightthickness=1, highlightbackground=UI_BORDA,
                  highlightcolor=UI_BORDA)
    return kw


class Frame(_TemaWidget, _tk.Frame):
    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_contorno_fino(_ui_juntar(cnf, kw))
        if "bg" not in kw and "background" not in kw:
            kw["bg"] = _ui_fundo_do_pai(master)
        if kw.get("highlightthickness") and "highlightcolor" not in kw:
            kw["highlightcolor"] = kw.get("highlightbackground", kw["bg"])   # sem contorno preto ao focar
        _tk.Frame.__init__(self, master, **kw)


class LabelFrame(_TemaWidget, _tk.LabelFrame):
    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_contorno_fino(_ui_juntar(cnf, kw))
        if "bg" not in kw and "background" not in kw:
            kw["bg"] = _ui_fundo_do_pai(master)
        if "relief" not in kw:
            kw.update(relief="flat", bd=0, highlightthickness=1, highlightbackground=UI_BORDA,
                      highlightcolor=UI_BORDA)
        _tk.LabelFrame.__init__(self, master, **kw)


class Label(_TemaWidget, _tk.Label):
    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_juntar(cnf, kw)
        if "bg" not in kw and "background" not in kw:
            kw["bg"] = _ui_fundo_do_pai(master)
        _tk.Label.__init__(self, master, **kw)

    def _ui_e_titulo(self):
        """Faixa azul de título de janela: fundo azul, texto branco, negrito e tamanho 14 ou mais."""
        try:
            fonte = _tkfont.Font(font=self.cget("font"))
            return (str(self.cget("bg")).lower() == UI_AZUL.lower() and str(self.cget("fg")).lower() == "white"
                    and fonte.actual("weight") == "bold" and abs(fonte.actual("size")) >= 14)
        except Exception:
            return False

    def _ui_estilo_titulo(self):
        _tk.Label.configure(self, anchor="w", padx=24, font=(UI_FONTE, 15, "bold"))

    def place_configure(self, cnf={}, **kw):
        """Título no topo da janela: passa a acompanhar a largura da janela (permite maximizar) e fica
        alinhado à esquerda, como nos módulos novos."""
        opcoes = dict(cnf)
        opcoes.update(kw)
        if (opcoes.get("relx") == 0 and opcoes.get("rely") == 0 and opcoes.get("height") == 60
                and (opcoes.get("width") or 0) >= 1000 and self._ui_e_titulo()):
            opcoes.pop("width")
            opcoes["relwidth"] = 1.0
            self._ui_estilo_titulo()
        return super().place_configure(**opcoes)

    place = place_configure

    def pack_configure(self, cnf={}, **kw):
        opcoes = dict(cnf)
        opcoes.update(kw)
        if opcoes.get("fill") in ("x", "both", X) and self._ui_e_titulo():
            self._ui_estilo_titulo()
        return super().pack_configure(**opcoes)

    pack = pack_configure


class Button(_TemaWidget, _tk.Button):
    """Botão plano, com efeito ao passar o mouse (no lugar do botão 3D padrão)."""

    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_juntar(cnf, kw)
        self._ui_estilado = "relief" not in kw
        if self._ui_estilado:
            fundo = kw.get("bg", kw.get("background"))
            if fundo is not None and str(fundo).lower() in (UI_FUNDO.lower(), "systembuttonface"):
                fundo = None            # botão "sem cor" (ficaria invisível): vira o botão neutro com contorno
                kw.pop("bg", None)
                kw.pop("background", None)
            if fundo is None:
                fundo, hover, texto = "white", "#EAF0F8", UI_TEXTO
                kw.setdefault("highlightbackground", "#C3CFE0")
                kw.setdefault("highlightthickness", 1)
            else:
                hover = _ui_escurecer(fundo)
                texto = "white" if _ui_e_escura(fundo) else UI_TEXTO
            texto = kw.get("fg", kw.get("foreground", texto))
            kw.pop("background", None)
            kw.update(bg=fundo, fg=texto, activebackground=hover, activeforeground=texto,
                      relief="flat", bd=0, cursor="hand2")
            kw.setdefault("highlightthickness", 0)
            kw.setdefault("font", (UI_FONTE, 9, "bold"))
            if "width" not in kw:
                kw.setdefault("padx", 6)
            if "height" not in kw:
                kw.setdefault("pady", 2)
            self._ui_fundo, self._ui_hover = fundo, hover
        _tk.Button.__init__(self, master, **kw)
        if self._ui_estilado:
            self.bind("<Enter>", self._ui_entrar)
            self.bind("<Leave>", self._ui_sair)

    def _ui_entrar(self, evento=None):
        if str(self.cget("state")) != "disabled":
            _tk.Button.configure(self, bg=self._ui_hover)

    def _ui_sair(self, evento=None):
        _tk.Button.configure(self, bg=self._ui_fundo)

    def configure(self, cnf=None, **kw):
        resultado = _TemaWidget.configure(self, cnf, **kw)
        novo = kw.get("bg", kw.get("background"))
        if novo is not None and getattr(self, "_ui_estilado", False):
            novo = _ui_cor("bg", novo)
            self._ui_fundo, self._ui_hover = novo, _ui_escurecer(novo)
        return resultado

    config = configure


class Entry(_TemaWidget, _tk.Entry):
    """Campo de uma linha, plano, com contorno que muda de cor ao receber o foco."""

    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_juntar(cnf, kw)
        if "relief" not in kw:
            kw.update(relief="flat", bd=2, highlightthickness=1, highlightbackground=UI_BORDA,
                      highlightcolor=UI_AZUL)
            kw.setdefault("bg", "white")
            kw.setdefault("fg", UI_TEXTO)
            kw.setdefault("insertbackground", UI_TEXTO)
            kw.setdefault("disabledbackground", "#EEF1F6")
            kw.setdefault("readonlybackground", "#EEF1F6")
            kw.setdefault("disabledforeground", UI_TEXTO_SUAVE)
        _tk.Entry.__init__(self, master, **kw)


class Text(_TemaWidget, _tk.Text):
    """Área de texto de várias linhas, plana, com margem interna e contorno com foco."""

    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_juntar(cnf, kw)
        if "relief" not in kw or kw.get("relief") in ("solid", "sunken", "groove", "ridge"):
            kw.pop("borderwidth", None)
            kw.update(relief="flat", bd=0, highlightthickness=1, highlightbackground=UI_BORDA,
                      highlightcolor=UI_AZUL)
            kw.setdefault("padx", 8)
            kw.setdefault("pady", 6)
            kw.setdefault("fg", UI_TEXTO)
            kw.setdefault("insertbackground", UI_TEXTO)
        _tk.Text.__init__(self, master, **kw)


class _Selecao(_TemaWidget):
    """Base de Checkbutton e Radiobutton: mesmo fundo do local onde estão e fonte moderna."""

    @staticmethod
    def _preparar(master, kw):
        if "bg" not in kw and "background" not in kw:
            kw["bg"] = _ui_fundo_do_pai(master)
        if "relief" not in kw:
            kw.setdefault("activebackground", kw["bg"])
            kw.setdefault("fg", UI_TEXTO)
            kw.setdefault("activeforeground", UI_TEXTO)
            kw.setdefault("selectcolor", "white")
            kw.setdefault("cursor", "hand2")
        return kw


class Checkbutton(_Selecao, _tk.Checkbutton):
    def __init__(self, master=None, cnf={}, **kw):
        _tk.Checkbutton.__init__(self, master, **self._preparar(master, _ui_juntar(cnf, kw)))


class Radiobutton(_Selecao, _tk.Radiobutton):
    def __init__(self, master=None, cnf={}, **kw):
        _tk.Radiobutton.__init__(self, master, **self._preparar(master, _ui_juntar(cnf, kw)))


class Listbox(_TemaWidget, _tk.Listbox):
    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_juntar(cnf, kw)
        if "relief" not in kw:
            kw.update(relief="flat", bd=0, highlightthickness=1, highlightbackground=UI_BORDA,
                      highlightcolor=UI_AZUL, activestyle="none")
            kw.setdefault("bg", "white")
            kw.setdefault("fg", UI_TEXTO)
            kw.setdefault("selectbackground", "#DCE8F8")
            kw.setdefault("selectforeground", UI_TEXTO)
        _tk.Listbox.__init__(self, master, **kw)


class Spinbox(_TemaWidget, _tk.Spinbox):
    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_juntar(cnf, kw)
        if "relief" not in kw:
            kw.update(relief="flat", bd=2, highlightthickness=1, highlightbackground=UI_BORDA,
                      highlightcolor=UI_AZUL)
            kw.setdefault("bg", "white")
            kw.setdefault("fg", UI_TEXTO)
        _tk.Spinbox.__init__(self, master, **kw)


class Menu(_TemaWidget, _tk.Menu):
    def __init__(self, master=None, cnf={}, **kw):
        kw = _ui_juntar(cnf, kw)
        kw.setdefault("font", (UI_FONTE, 10))
        kw.setdefault("bg", "white")
        kw.setdefault("fg", UI_TEXTO)
        kw.setdefault("activebackground", "#DCE8F8")
        kw.setdefault("activeforeground", UI_TEXTO)
        _tk.Menu.__init__(self, master, **kw)


class Scrollbar(ttk.Scrollbar):
    """Barra de rolagem fina e plana (a barra padrão do Tk não aceita cores no Windows)."""

    def __init__(self, master=None, cnf={}, **kw):
        opcoes = dict(cnf)
        opcoes.update(kw)
        for opcao in ("bg", "background", "troughcolor", "activebackground", "relief", "bd", "borderwidth",
                      "width", "highlightthickness", "highlightbackground", "highlightcolor", "elementborderwidth",
                      "jump", "repeatdelay", "repeatinterval"):
            opcoes.pop(opcao, None)
        ttk.Scrollbar.__init__(self, master, **opcoes)


_CalendarioOriginal = Calendar


class Calendar(_CalendarioOriginal):
    """Calendário nas cores do sistema e em português (a data continua no mesmo formato de antes)."""

    def __init__(self, master=None, **kw):
        kw.setdefault("background", UI_AZUL_ESCURO)
        kw.setdefault("foreground", "white")
        kw.setdefault("headersbackground", UI_AZUL)
        kw.setdefault("headersforeground", "white")
        kw.setdefault("selectbackground", UI_AZUL)
        kw.setdefault("selectforeground", "white")
        kw.setdefault("normalbackground", "white")
        kw.setdefault("normalforeground", UI_TEXTO)
        kw.setdefault("weekendbackground", "#F3F6FB")
        kw.setdefault("weekendforeground", UI_TEXTO)
        kw.setdefault("othermonthbackground", UI_FUNDO)
        kw.setdefault("othermonthwebackground", UI_FUNDO)
        kw.setdefault("othermonthforeground", UI_TEXTO_SUAVE)
        kw.setdefault("othermonthweforeground", UI_TEXTO_SUAVE)
        kw.setdefault("bordercolor", UI_BORDA)
        kw.setdefault("font", (UI_FONTE, 10))
        try:
            _CalendarioOriginal.__init__(self, master, locale="pt_BR", **kw)
        except Exception:                      # sem o pacote de idiomas (babel): calendário em inglês, como antes
            _CalendarioOriginal.__init__(self, master, **kw)


def _ui_aplicar_tema_global(janela_raiz):
    """Fontes padrão, estilos ttk (caixas de seleção, tabelas, barras) e cores das listas suspensas.
    É chamada automaticamente por cada janela raiz (Tk) no momento em que ela é criada."""
    for nome_fonte in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont", "TkCaptionFont"):
        try:
            _tkfont.nametofont(nome_fonte, root=janela_raiz).configure(family=UI_FONTE)
        except _tk.TclError:
            pass

    estilo = ttk.Style(janela_raiz)
    try:
        estilo.theme_use("clam")
    except _tk.TclError:
        pass

    estilo.configure("TCombobox", fieldbackground="white", background=UI_NEUTRO, foreground=UI_TEXTO,
                     bordercolor=UI_BORDA, lightcolor=UI_BORDA, darkcolor=UI_BORDA, arrowcolor=UI_TEXTO_SUAVE,
                     arrowsize=14, padding=(6, 2), relief="flat")
    estilo.map("TCombobox",
               fieldbackground=[("readonly", "white"), ("disabled", "#EEF1F6")],
               foreground=[("readonly", UI_TEXTO), ("disabled", UI_TEXTO_SUAVE)],
               selectbackground=[("readonly", "white")], selectforeground=[("readonly", UI_TEXTO)],
               bordercolor=[("focus", UI_AZUL), ("active", UI_AZUL)],
               background=[("active", UI_NEUTRO_HOVER)],
               arrowcolor=[("active", UI_AZUL)])
    janela_raiz.option_add("*TCombobox*Listbox.font", (UI_FONTE, 10))
    janela_raiz.option_add("*TCombobox*Listbox.selectBackground", UI_AZUL)
    janela_raiz.option_add("*TCombobox*Listbox.selectForeground", "white")
    janela_raiz.option_add("*TCombobox*Listbox.background", "white")

    estilo.configure("Treeview", background="white", fieldbackground="white", foreground=UI_TEXTO,
                     rowheight=26, borderwidth=0, font=(UI_FONTE, 10))
    estilo.configure("Treeview.Heading", background=UI_AZUL, foreground="white", relief="flat",
                     font=(UI_FONTE, 10, "bold"), padding=(6, 6))
    estilo.map("Treeview.Heading", background=[("active", UI_AZUL_ESCURO)])
    estilo.map("Treeview", background=[("selected", "#DCE8F8")], foreground=[("selected", UI_TEXTO)])

    estilo.configure("Horizontal.TProgressbar", troughcolor="#E5EAF1", background=UI_AZUL,
                     bordercolor=UI_BORDA, lightcolor=UI_AZUL, darkcolor=UI_AZUL)

    for orientacao in ("Vertical", "Horizontal"):
        estilo.configure(f"{orientacao}.TScrollbar", background="#C9D3E0", troughcolor=UI_FUNDO,
                         bordercolor=UI_FUNDO, arrowcolor=UI_TEXTO_SUAVE, lightcolor="#C9D3E0",
                         darkcolor="#C9D3E0", relief="flat")
        estilo.map(f"{orientacao}.TScrollbar", background=[("active", "#A9B7CB"), ("pressed", UI_AZUL)])


def ui_dialogo(janela, titulo, subtitulo=None, altura_faixa=64):
    """Faixa azul de título de um pequeno diálogo, com o título alinhado à esquerda."""
    faixa = Frame(janela, bg=UI_AZUL)
    faixa.place(x=0, y=0, relwidth=1.0, height=altura_faixa)
    Label(faixa, text=titulo, bg=UI_AZUL, fg="white", font=(UI_FONTE, 15, "bold")).place(
        x=24, rely=0.5 if not subtitulo else 0.36, anchor="w")
    if subtitulo:
        Label(faixa, text=subtitulo, bg=UI_AZUL, fg="#B8CCE8", font=(UI_FONTE, 9)).place(x=24, rely=0.72, anchor="w")
    return faixa


def ui_cartao(janela, y, altura):
    """Cartão branco com contorno fino onde ficam os campos do diálogo."""
    cartao = Frame(janela, bg=UI_CARD, highlightthickness=1, highlightbackground=UI_BORDA)
    cartao.place(x=24, y=y, relwidth=1.0, width=-48, height=altura)
    return cartao


def ui_campo(cartao, texto, y, **opcoes_entry):
    """Rótulo pequeno + campo de texto de uma linha (largura total do cartão). Devolve o Entry."""
    Label(cartao, text=texto, bg=UI_CARD, fg=UI_TEXTO_SUAVE, font=(UI_FONTE, 9, "bold")).place(x=20, y=y)
    entrada = Entry(cartao, font=(UI_FONTE, 11), **opcoes_entry)
    entrada.place(x=20, y=y + 24, relwidth=1.0, width=-40, height=34)
    return entrada

# ================================== fim do TEMA VISUAL MODERNO =============================

# ---------------------------------------------------
# VARIÁVEL DE CONTROLE DE LOGIN
# ---------------------------------------------------
logged_in = False
current_user = None  # usuário logado
# ---------------------------------------------------
# VARIÁVEIS PARA DEFINIR MESAS DE OPERAÇÃO
# ---------------------------------------------------
mesa1 = ["COG-P", "COG-R", "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM", "CGE JDT", "UFV PTM", "SE RSD", "SE JDD",
         "SE IPG", "SE SCA"]
mesa2 = ["COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO", "SE IGU", "SE MCP", "SE CLA"]

# Dicionário global para armazenar dos campos de entrada Sim_hidro_fgo
entries = {}
# Lista para armazenar as manobras/alteracoes do sim_hidro_fgo
resultados = []
manobras = []

# ---------------------------------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS
# ---------------------------------------------------
def criar_banco():
    conexao = sqlite3.connect('dados_turno.db')
    cursor = conexao.cursor()

    # Tabelas para diferentes janelas
    cursor.execute('''CREATE TABLE IF NOT EXISTS InformacoesRelevantes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_hora TEXT,
                        localidade TEXT,
                        instalacao TEXT,
                        equipamento TEXT,
                        descricao TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS AlarmesSinalizacoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_hora TEXT,
                        localidade TEXT,
                        instalacao TEXT,
                        tag_alarme TEXT,
                        descricao_alarme TEXT,
                        comunicado TEXT,
                        profissional TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS AnormalidadesTelemetricas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_hora TEXT,
                        localidade TEXT,
                        estacao TEXT,
                        complem_estacao TEXT,
                        descricao_anormal TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ComprovacaoDisponibilidade (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_inicio TEXT,
                        data_termino TEXT,
                        localidade TEXT,
                        unidade_geradora TEXT,
                        potencia_gerada TEXT,
                        informacoes_adicionais TEXT,
                        observacao TEXT,
                        centro_ons TEXT,
                        operador_ons TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS MalhaControle (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_inicio TEXT,
                        data_termino TEXT,
                        localidade TEXT,
                        unidade_geradora TEXT,
                        modo_controle TEXT,
                        rede TEXT,
                        motivo_causa TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ContatoBalseiro (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_hora TEXT,
                        localidade TEXT,
                        motivo TEXT,
                        complem_motivo TEXT,
                        informacao TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS DescargasParciais (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_inicio TEXT,
                        data_termino TEXT,
                        localidade TEXT,
                        unidade_geradora TEXT,
                        informacao TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS FalhaComunicacao (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_inicio TEXT,
                        data_termino TEXT,
                        localidade TEXT,
                        estacao TEXT,
                        complem_estacao TEXT,
                        descricao TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS FalhaSupervisao (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_inicio TEXT,
                        data_termino TEXT,
                        localidade TEXT,
                        atend_local TEXT,
                        complem_local TEXT,
                        descricao TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Perturbacao (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_inicio TEXT,
                        data_termino TEXT,
                        localidade TEXT,
                        instalacao TEXT,
                        equipamento TEXT,
                        causa TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ServicoAuxiliar (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_inicio TEXT,
                        data_termino TEXT,
                        localidade TEXT,
                        concessionaria TEXT,
                        protocol TEXT,
                        informacao TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS InformacaoOns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_hora TEXT,
                        localidade TEXT,
                        centro_op TEXT,
                        operador_ons TEXT,
                        descricao TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Transbordo (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_inicio TEXT,
                        data_termino TEXT,
                        localidade TEXT,
                        informacao_ons TEXT,
                        operador_ons TEXT,
                        informacao TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS HabilitacaoEce (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_hora TEXT,
                        localidade TEXT,
                        sep_ece TEXT,
                        complem_ece TEXT,
                        informacao_ad TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS SacaAgente (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_inicio TEXT,
                        data_termino TEXT,
                        localidade TEXT,
                        alimentacao_da TEXT,
                        solicitado_por TEXT,
                        informacao TEXT,
                        observacao TEXT,
                        ativo TEXT,
                        usuario TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS TagAvato (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        instalacao TEXT,
                        ons TEXT,
                        nome_zabbix TEXT,
                        nome_proposta TEXT,
                        link_zabbix TEXT,
                        responsavel TEXT,
                        telefone_responsavel TEXT,
                        disponivel TEXT,
                        condicao_acesso TEXT,
                        endereco TEXT,
                        observacao TEXT,
                        ativo TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Protocolo (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         instalacao TEXT,
                         concessionaria TEXT,
                         atendimento_grandes_clientes TEXT,
                         whatsapp TEXT,
                         site TEXT,
                         titular_da_conta TEXT,
                         cnpj TEXT,
                         endereco TEXT,
                         cep_cidade_uf TEXT,
                         unidade_consumidora TEXT,
                         parceiro_negocio TEXT,
                         numero_cliente TEXT,
                         numero_instalacao TEXT,
                         codigo_cliente TEXT,
                         codigo_instalacao TEXT,
                         codigo_unico TEXT,
                         senha TEXT,
                         ativo TEXT)''')

    conexao.commit()
    conexao.close()

# ---------------------------------------------------
# FUNÇÃO PARA SALVAR DADOS NO BANCO
# ---------------------------------------------------
def salvar_dados(tabela, dados):
    conexao = sqlite3.connect('dados_turno.db')
    cursor = conexao.cursor()

    placeholders = ', '.join(['?'] * len(dados))
    campos = ', '.join(dados.keys())
    valores = tuple(dados.values())

    query = f'INSERT INTO {tabela} ({campos}) VALUES ({placeholders})'
    cursor.execute(query, valores)

    conexao.commit()
    conexao.close()


# ---------------------------------------------------
# FUNÇÃO PARA COMPLEMENTAR DATA-HORA DE TÉRMINO
# ---------------------------------------------------
def atualizar_data_termino(tabela, id_registro, nova_data_termino):
    conexao = sqlite3.connect('dados_turno.db')
    cursor = conexao.cursor()

    # Verifica se o registro está cancelado
    cursor.execute(f"SELECT ativo FROM {tabela} WHERE id = ?", (id_registro,))
    resultado_ativo = cursor.fetchone()

    if resultado_ativo and "CANCELADO" in resultado_ativo[0]:
        messagebox.showwarning("Atenção", "O registro está cancelado e não pode ser alterado.")
        conexao.close()
        return

    # Verifica se a data de término já foi preenchida
    cursor.execute(f"SELECT data_termino, data_inicio FROM {tabela} WHERE id = ?", (id_registro,))
    resultado = cursor.fetchone()

    if resultado and resultado[0] is not None:
        messagebox.showwarning("Atenção", "A Data/Hora de Término já foi lançada e não pode ser alterada.")
        conexao.close()
        return

    # Verifica se a nova data de término é anterior à data de início
    if resultado and resultado[1] is not None:
        try:
            dt_inicio = datetime.strptime(resultado[1], "%d/%m/%Y - %H:%Mh")
            dt_termino = datetime.strptime(nova_data_termino, "%d/%m/%Y - %H:%Mh")
            if dt_termino < dt_inicio:
                messagebox.showerror("Erro", "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                conexao.close()
                return
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use o calendário.")
            conexao.close()
            return

    # Se a data de término ainda não foi preenchida, atualiza o campo
    query = f"UPDATE {tabela} SET data_termino = ? WHERE id = ?"
    cursor.execute(query, (nova_data_termino, id_registro))

    conexao.commit()
    conexao.close()
    messagebox.showinfo("Sucesso", "Data/Hora de Término atualizada!")


def abrir_janela_atualizacao_data_termino(tabela, id_registro):
    janela_atualizacao = Toplevel(root)
    janela_atualizacao.title("Atualizar Data/Hora de Término")
    janela_atualizacao.geometry("300x150")
    janela_atualizacao.resizable(False, False)
    janela_atualizacao['bg'] = "#a4bad2"

    Label(janela_atualizacao, text="Data e Hora de Término:", bg="#a4bad2").place(relx=0.1, rely=0.2, anchor="w")
    entry_nova_data_termino = Entry(janela_atualizacao, width=30)
    entry_nova_data_termino.place(relx=0.1, rely=0.4, width=130, height=25, anchor="w")

    Button(janela_atualizacao, text="Selecionar", width=12, height=1,
           command=lambda: selecionar_data(entry_nova_data_termino, "Término")).place(relx=0.6,
                                                                                      rely=0.4,
                                                                                      anchor="w")
    Button(janela_atualizacao, text="Atualizar", width=10, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: atualizar_data_termino(tabela, id_registro, entry_nova_data_termino.get().strip())).place(
        relx=0.5,
        rely=0.7,
        anchor="center")


# ---------------------------------------------------
# FUNÇÃO PARA GERAR RELATÓRIO EM PDF
# ---------------------------------------------------
def gerar_pdf():
    conn = sqlite3.connect('dados_turno.db')
    cursor = conn.cursor()

    # Define formato A4 em orientação retrato (P = Portrait)
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Título do PDF
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Relatório Consolidado', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)


# ---------------------------------------------------
# MAPEAMENTO DE TABELAS PARA CAMPOS DE DATA
# ---------------------------------------------------
tabela_para_campo_data = {
    'InformacoesRelevantes': 'data_hora',
    'AlarmesSinalizacoes': 'data_hora',
    'AnormalidadesTelemetricas': 'data_hora',
    'ContatoBalseiro': 'data_hora',
    'InformacaoOns': 'data_hora',
    'HabilitacaoEce': 'data_hora',
    # A tabela abaixo não tem 'data_hora'; usamos 'data_inicio'
    'ComprovacaoDisponibilidade': 'data_inicio',
    'MalhaControle': 'data_inicio',
    'DescargasParciais': 'data_inicio',
    'FalhaComunicacao': 'data_inicio',
    'FalhaSupervisao': 'data_inicio',
    'Perturbacao': 'data_inicio',
    'ServicoAuxiliar': 'data_inicio',
    'Transbordo': 'data_inicio',
    'SacaAgente': 'data_inicio'
}
# ---------------------------------------------------
# LISTA DE CATEGORIAS (ITENS) PARA O RELATÓRIO
# ---------------------------------------------------
categorias = [
    ('Informações Relevantes', 'InformacoesRelevantes',
     ["ID", "Data e Hora", "Localidade", "Instalação", "Equipamento", "Descrição", "Observação", "Registro",
      "Lançado por"]),
    ("Alarmes e Sinalizações", "AlarmesSinalizacoes",
     ["ID", "Data e Hora", "Localidade", "Instalação", "TAG-Alarme", "Descrição", "Comunicado",
      "Profissional", "Registro", "Lançado por"]),
    ('Anormalidades Estações Telemétricas', 'AnormalidadesTelemetricas',
     ["ID", "Data e Hora", "Localidade", "Estação", "Complemento", "Descrição",
      "Observação", "Registro", "Lançado por"]),
    ('Comprovação de Disponibilidade', 'ComprovacaoDisponibilidade',
     ["ID", "Data Início", "Data Término", "Localidade", "Unidade Geradora", "Potência Média",
      "Info. Adicionais", "Observações", "COSR-ONS", "Operador ONS",
      "Registro", "Lançado por"]),
    ('Comutação de Malha de Controle', 'MalhaControle',
     ["ID", "Data Início", "Data Término", "Localidade", "Unidade Geradora", "Modo de Controle",
      "Rede", "Motivo-causa", "Observações", "Registro", "Lançado por"]),
    ('Contato com Balseiro da UHE SJO', 'ContatoBalseiro',
     ["ID", "Data e Hora", "Localidade", "Motivo:", "Complemento:", "Info. Adicionais",
      "Observação", "Registro", "Lançado por"]),
    ("Testes de Descargas Parciais", "DescargasParciais",
     ["ID", "Data Início", "Data Término", "Localidade", "Unidade Geradora", "Info. Adicionais",
      "Observações", "Registro", "Lançado por"]),
    ("Falha de Comunicação", "FalhaComunicacao",
     ["ID", "Data Início", "Data Término", "Localidade", "Estação", "Complemento",
      "Descrição", "Observação", "Registro", "Lançado por"]),
    ('Falha de Supervisão', 'FalhaSupervisao',
     ["ID", "Data Início", "Data Término", "Localidade", "Atend.Op.Local", "Complemento",
      "Descrição", "Observação", "Registro", "Lançado por"]),
    ('Perturbações', 'Perturbacao',
     ["ID", "Data Início", "Data Término", "Localidade", "Instalação", "Equipamentos",
      "Causa", "Observação", "Registro", "Lançado por"]),
    ('Falha Fonte externa Serviço Auxiliar CA', 'ServicoAuxiliar',
     ["ID", "Data Início", "Data Término", "Localidade", "Aberto Chamado", "Núm.Protocolo",
      "Info. Adicionais", "Observação", "Registro", "Lançado por"]),
    ('Informações do ONS', 'InformacaoOns',
     ["ID", "Data e Hora", "Localidade", "COS", "Operador ONS", "Descrição",
      "Observação", "Registro", "Lançado por"]),
    ('Transbordo Plantas Aquáticas', 'Transbordo',
     ["ID", "Data Início", "Data Término", "Localidade", "Inform.ONS", "Operador ONS",
      "Info. Adicionais", "Observação", "Registro", "Lançado por"]),
    ('Habilitação-Desabilitação do SEP-ECE', 'HabilitacaoEce',
     ["ID", "Data e Hora", "Localidade", "SEP/ECE", "Complemento", "Info. Adicionais",
      "Observação", "Registro", "Lançado por"]),
    ('Alim. SACA por outro Agente', 'SacaAgente',
     ["ID", "Data Início", "Data Término", "Localidade", "Alimentação_da", "Solicitado_por",
      "Info. Adicionais", "Observação", "Registro", "Lançado por"])
]
instalacoes = [
    ('Tag da Ávato', 'TagAvato',
     ["ID", "instalacao", "ons", "nome_Zabbix", "nome_proposta", "link_Zabbix", "responsavel", "tel_responsavel",
      "disponivel", "condicao_acesso", "endereco", "observacao", "ativo"])
]
protocolo = [
    ('Protocolo', 'Protocolo',
     ["ID", "instalacao", "concessionaria", "atendimento_grandes_cliente", "whatsapp", "site", "titular_da_conta",
      "cnpj", "endereco", "cep_cidade_uf", "unidade_consumidora", "parceiro_negocio", "numero_cliente",
      "numero_instalacao", "codigo_cliente", "codigo_instalacao", "codigo_unico", "senha", "ativo"])
]


# ---------------------------------------------------
# VERIFICA SE A TABELA POSSUI UMA COLUNA ESPECÍFICA
# ---------------------------------------------------
def tabela_tem_coluna(cursor, nome_tabela, nome_coluna):
    cursor.execute(f"PRAGMA table_info({nome_tabela})")
    colunas = [info[1] for info in cursor.fetchall()]
    return nome_coluna in colunas


# ---------------------------------------------------
# GERAR RELATÓRIO COMPLETO EM PDF (SEM FILTROS)
# ---------------------------------------------------

class PDF(FPDF):
    def header(self):
        # Inserir figura no cabeçalho
        imagem = 'logo_cog2.png'
        self.image(imagem, x=10, y=3, w=190)
        self.ln(20)  # Adiciona um espaço após a imagem


def gerar_pdf_completo():
    conn = sqlite3.connect('dados_turno.db')
    cursor = conn.cursor()

    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    margem_esquerda = 10

    for titulo, nome_tabela, colunas in categorias:
        query = f"SELECT * FROM {nome_tabela}"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            continue

        # Lógica corrigida para evitar página em branco no início
        altura_estimada = 20 + (len(rows) * 12)
        posicao_atual = pdf.get_y()

        # Se não couber E não for o topo da página, pula
        if posicao_atual + altura_estimada > pdf.h - 15 and posicao_atual > 40:
            pdf.add_page()

        # Título em negrito
        pdf.set_font('DejaVu', 'B', 12)
        pdf.set_text_color(0, 159, 77)
        pdf.cell(0, 10, f"# {titulo}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('DejaVu', '', 10)
        pdf.set_text_color(0, 0, 0)

        for row in rows:
            for i, valor in enumerate(row):
                nome_coluna = colunas[i] if i < len(colunas) else f"Campo {i}"
                valor_exibicao = str(valor) if valor is not None else "(Pendente de Lançamento)"

                pdf.set_x(margem_esquerda + 5)

                largura_coluna = 35
                largura_valor = 155

                pdf.set_font("DejaVu", "B", 10)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(largura_coluna, 6, f"{nome_coluna}: ", new_x="RIGHT", new_y="TOP")

                pdf.set_font("DejaVu", "", 10)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(largura_valor, 6, valor_exibicao)

            # Adicionar uma linha tracejada horizontal de cor verde para separar lançamentos
            pdf.ln(3)  # espaço 3mm antes da linha tracejada
            x1, x2 = 17, 200
            y = pdf.get_y()
            pdf.set_draw_color(0, 159, 77)  # Cor verde
            pdf.set_dash_pattern(dash=1, gap=3)  # Define o tracejado
            pdf.line(x1, y, x2, y)  # Desenha a linha
            pdf.set_dash_pattern()  # Reseta para linha sólida
            pdf.ln(3)  # espaço de 3mm depois da linha tracejada

        # Linhas duplas para separar categorias (opcional)
        y = pdf.get_y()
        pdf.set_draw_color(2, 69, 147)  # Azul Alupar
        pdf.line(margem_esquerda, y, 200, y)
        pdf.line(margem_esquerda, y + 1, 200, y + 1)
        pdf.ln(4)

    conn.close()
    pdf.output('relatorio_turno_completo.pdf')
    messagebox.showinfo("Relatório", "PDF completo gerado com sucesso!")
    caminho_pdf = "relatorio_turno_completo.pdf"
    abrir_pdf(caminho_pdf)


# Função para abrir o PDF (assumindo que você já tem essa função definida)
def abrir_pdf(caminho_pdf):
    """
    Abre o PDF no leitor padrão do sistema operacional.
    """
    if not os.path.exists(caminho_pdf):
        print(f"Erro: O arquivo {caminho_pdf} não foi encontrado.")
        return

    so = platform.system()

    try:
        if so == "Windows":
            os.startfile(caminho_pdf)
        elif so == "Darwin":  # macOS
            subprocess.run(["open", caminho_pdf], check=True)
        else:  # Linux (Ubuntu, Debian, etc)
            subprocess.run(["xdg-open", caminho_pdf], check=True)
    except Exception as e:
        print(f"Não foi possível abrir o PDF: {e}")


# ---------------------------------------------------
# GERAR RELATÓRIO COMPLETO EM PDF (COM FILTROS)
# ---------------------------------------------------
class PDF(FPDF):
    def header(self):
        # Inserir figura no cabeçalho
        imagem = 'logo_cog2.png'
        self.image(imagem, x=10, y=3, w=190)
        self.ln(20)  # Adiciona um espaço após a imagem


def gerar_pdf_com_filtros(filtros):
    conn = sqlite3.connect('dados_turno.db')
    cursor = conn.cursor()

    pdf = PDF(orientation='P', unit='mm', format='A4')

    # Adiciona as fontes Unicode
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf')

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    margem_esquerda = 10

    data_inicial = filtros.get('data_inicial', '').strip()
    data_final = filtros.get('data_final', '').strip()
    localidade = filtros.get('localidade', '')
    grupo_localidade = filtros.get('grupo_localidade', '')
    status = filtros.get('status', '')
    categorias_selecionadas = filtros.get('categorias_selecionadas', [])

    # Se o usuário não selecionar NENHUMA categoria, avisa
    if not categorias_selecionadas:
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 7, "Nenhuma categoria foi selecionada.", new_x="LMARGIN", new_y="NEXT")
        pdf.output('relatorio_turno_filtrado.pdf')
        messagebox.showinfo("Relatório", "PDF gerado (sem categorias).")
        conn.close()
        return

    # Filtra as categorias com base nas seleções
    categorias_filtradas = [cat for cat in categorias if cat in categorias_selecionadas]

    for titulo, nome_tabela, colunas in categorias_filtradas:
        # Construir WHERE
        where_clauses = []
        campo_data = tabela_para_campo_data.get(nome_tabela)
        if campo_data:
            if data_inicial and data_final:
                where_clauses.append(
                    f"(substr({campo_data}, 1, 10) >= '{data_inicial}' AND substr({campo_data}, 1, 10) <= '{data_final}')"
                )
            elif data_inicial and not data_final:
                where_clauses.append(f"substr({campo_data}, 1, 10) = '{data_inicial}'")
            elif data_final and not data_inicial:
                where_clauses.append(f"substr({campo_data}, 1, 10) = '{data_final}'")

        # Filtro 'localidade'
        if localidade and tabela_tem_coluna(cursor, nome_tabela, 'localidade'):
            where_clauses.append(f"localidade = '{localidade}'")

        # Filtro 'grupo_localidade'
        if grupo_localidade and tabela_tem_coluna(cursor, nome_tabela, 'localidade'):
            if grupo_localidade == "Mesa1 (PCH)":
                localidades_filtro = mesa1
            elif grupo_localidade == "Mesa2 (UHE)":
                localidades_filtro = mesa2
            else:
                localidades_filtro = []

            if localidades_filtro:
                localidades_str = "', '".join(localidades_filtro)
                where_clauses.append(f"localidade IN ('{localidades_str}')")

        # Filtro 'status'
        if status != "" and tabela_tem_coluna(cursor, nome_tabela, 'ativo'):
            if status == "CANCELADO":
                where_clauses.append(f"ativo LIKE '%CANCELADO%'")
            else:
                where_clauses.append(f"ativo = '{status}'")

        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        else:
            where_sql = ""

        # Buscar registros
        query = f"SELECT * FROM {nome_tabela} {where_sql}"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            continue

        altura_estimada = 20 + (len(rows) * 12)
        if pdf.get_y() + altura_estimada > pdf.h - 15:
            pdf.add_page()

        # Se houver registros, imprime o título
        pdf.set_font('DejaVu', 'B', 12)
        pdf.set_text_color(0, 159, 77)  # verde
        pdf.cell(0, 10, f"# {titulo}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('DejaVu', '', 10)
        pdf.set_text_color(0, 0, 0)  # preto

        # Se houver registros, imprime cada registro
        for row in rows:
            for i, valor in enumerate(row):
                nome_coluna = colunas[i] if i < len(colunas) else f"Campo {i}"

                # Converte o valor para string (já com suporte a acentos)
                valor_exibicao = str(valor) if valor is not None else "(Pendente de Lançamento)"

                pdf.set_x(margem_esquerda + 5)

                # Define larguras para as células
                largura_coluna = 35
                largura_valor = 155

                # Exibe o nome da coluna em negrito
                pdf.set_font("DejaVu", style="B", size=10)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(largura_coluna, 6, f"{nome_coluna}: ", new_x="RIGHT", new_y="TOP")

                # Exibe o valor normalmente
                pdf.set_font("DejaVu", style="", size=10)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(largura_valor, 6, valor_exibicao)

            # Adicionar uma linha tracejada horizontal de cor verde para separar lançamentos
            pdf.ln(3)  # Pula 3mm antes da linha
            x1, x2 = 17, 200
            y = pdf.get_y()
            pdf.set_draw_color(0, 159, 77)  # Verde
            pdf.set_dash_pattern(dash=1, gap=3)  # Define o padrão tracejado
            pdf.line(x1, y, x2, y)  # Desenha a linha
            pdf.set_dash_pattern()  # Reseta para linha sólida
            pdf.ln(3)  # Pula 3mm depois da linha

        # Adicionar duas linhas horizontais de cor azul para separar categorias
        y = pdf.get_y()
        pdf.set_draw_color(2, 69, 147)  # Azul Alupar
        pdf.line(margem_esquerda, y, 200, y)
        pdf.line(margem_esquerda, y + 1, 200, y + 1)
        pdf.ln(4)

    conn.close()
    pdf.output('relatorio_turno_filtrado.pdf')
    messagebox.showinfo("Relatório", "PDF (filtrado) gerado com sucesso!")
    caminho_pdf = "relatorio_turno_filtrado.pdf"
    abrir_pdf(caminho_pdf)

    # ---------------------------------------------------
    # FUNÇÕES PARA DEFINIÇÃO DOS FILTROS NA GERAÇÃO DO RELATÓRIO.
    # ---------------------------------------------------


def abrir_janela_filtros():
    def selecionar_data_inicial():
        def salvar_data():
            data_selecionada = cal.selection_get().strftime('%d/%m/%Y')
            entry_data_inicial.delete(0, END)
            entry_data_inicial.insert(0, data_selecionada)
            janela_cal.destroy()

        janela_cal = Toplevel(filtro_window)
        janela_cal.title("Data Inicial")
        cal = Calendar(janela_cal, selectmode='day', date_pattern='dd-mm-yyyy')
        cal.pack(pady=20)
        Button(janela_cal, text="Salvar", command=salvar_data).pack(pady=10)

    def selecionar_data_final():
        def salvar_data():
            data_selecionada = cal.selection_get().strftime('%d/%m/%Y')
            entry_data_final.delete(0, END)
            entry_data_final.insert(0, data_selecionada)
            janela_cal.destroy()

        janela_cal = Toplevel(filtro_window)
        janela_cal.title("Data Final")
        cal = Calendar(janela_cal, selectmode='day', date_pattern='dd-mm-yyyy')
        cal.pack(pady=20)
        Button(janela_cal, text="Salvar", command=salvar_data).pack(pady=10)

    def gerar_pdf_filtrado():
        data_inicial_val = entry_data_inicial.get().strip()
        data_final_val = entry_data_final.get().strip()
        localidade_sel = combo_localidade_filtro.get().strip()
        grupo_localidade_sel = combo_grupo_localidade.get().strip()
        status_sel = combo_status.get().strip()
        categorias_selecionadas = []

        # Verifica quais categorias foram selecionadas
        if var_cat_ir.get() == 1:
            categorias_selecionadas.append(categorias[0])
        if var_cat_as.get() == 1:
            categorias_selecionadas.append(categorias[1])
        if var_cat_at.get() == 1:
            categorias_selecionadas.append(categorias[2])
        if var_cat_cd.get() == 1:
            categorias_selecionadas.append(categorias[3])
        if var_cat_mc.get() == 1:
            categorias_selecionadas.append(categorias[4])
        if var_cat_cb.get() == 1:
            categorias_selecionadas.append(categorias[5])
        if var_cat_dp.get() == 1:
            categorias_selecionadas.append(categorias[6])
        if var_cat_fc.get() == 1:
            categorias_selecionadas.append(categorias[7])
        if var_cat_fs.get() == 1:
            categorias_selecionadas.append(categorias[8])
        if var_cat_pe.get() == 1:
            categorias_selecionadas.append(categorias[9])
        if var_cat_sa.get() == 1:
            categorias_selecionadas.append(categorias[10])
        if var_cat_io.get() == 1:
            categorias_selecionadas.append(categorias[11])
        if var_cat_tb.get() == 1:
            categorias_selecionadas.append(categorias[12])
        if var_cat_hd.get() == 1:
            categorias_selecionadas.append(categorias[13])
        if var_cat_so.get() == 1:
            categorias_selecionadas.append(categorias[14])

        filtros = {
            'data_inicial': data_inicial_val if data_inicial_val else '',
            'data_final': data_final_val if data_final_val else '',
            'localidade': localidade_sel,
            'grupo_localidade': grupo_localidade_sel,
            'status': status_sel,
            'categorias_selecionadas': categorias_selecionadas
        }
        gerar_pdf_com_filtros(filtros)
        filtro_window.destroy()

    filtro_window = Toplevel(root)
    filtro_window.title("Filtros para Relatório")
    filtro_window.geometry("400x650")
    filtro_window.resizable(False, False)
    filtro_window.configure(bg="#CDD505")

    # --------------- Filtro por "Data Inicial" ---------------
    label_data_inicial = Label(filtro_window, text="Data Inicial:", bg="#CDD505")
    label_data_inicial.place(x=133, y=12)

    entry_data_inicial = Entry(filtro_window, width=20)
    entry_data_inicial.place(x=100, y=32, width=120, height=25)

    button_cal_inicial = Button(filtro_window, text="Calendário", font=('arial', 9, 'bold'), fg='#024593',
                                command=selecionar_data_inicial)
    button_cal_inicial.place(x=230, y=32)

    # --------------- Filtro por "Data Final" ---------------
    label_data_final = Label(filtro_window, text="Data Final:", bg="#CDD505")
    label_data_final.place(x=133, y=72)

    entry_data_final = Entry(filtro_window, width=20)
    entry_data_final.place(x=100, y=92, width=120, height=25)

    button_cal_final = Button(filtro_window, text="Calendário", font=('arial', 9, 'bold'), fg='#024593',
                              command=selecionar_data_final)
    button_cal_final.place(x=230, y=92)

    # --------------- Filtro por "Localidades" ---------------
    label_localidade = Label(filtro_window, text="Localidade:", bg="#CDD505")
    label_localidade.place(x=80, y=130)

    lista_localidades = [
        "", "COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO",
        "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM", "CGE JDT", "UFV PTM",
        "SE RSD", "SE JDD", "SE MCP", "SE IGU", "SE CLA", "SE IPG", "SE SCA"
    ]
    combo_localidade_filtro = ttk.Combobox(filtro_window, values=lista_localidades, state="readonly")
    combo_localidade_filtro.current(0)
    combo_localidade_filtro.place(x=50, y=150, width=120, height=25)

    # opção de filtro
    label_localidade = Label(filtro_window, text="ou", bg="#CDD505")
    label_localidade.place(x=185, y=150)

    # --------------- Filtro por Mesas de Operação ---------------
    label_grupo_localidade = Label(filtro_window, text="Mesas de Operação:", bg="#CDD505")
    label_grupo_localidade.place(x=230, y=130)

    lista_grupos = ["", "Mesa1 (PCH)", "Mesa2 (UHE)"]
    combo_grupo_localidade = ttk.Combobox(filtro_window, values=lista_grupos, state="readonly")
    combo_grupo_localidade.current(0)
    combo_grupo_localidade.place(x=230, y=150, width=120, height=25)
    # ---------------------------------------------------
    # CHECKBUTTONS DAS CATEGORIAS
    # ---------------------------------------------------
    var_cat_ir = IntVar(value=1)  # Informações Relevantes
    var_cat_as = IntVar(value=1)  # Alarmes e Sinalizações
    var_cat_at = IntVar(value=1)  # Anormalidades telemétricas
    var_cat_cd = IntVar(value=1)  # Comprovação Disponibilidade
    var_cat_mc = IntVar(value=1)  # Malha e controle
    var_cat_cb = IntVar(value=1)  # Contato com Balseiro
    var_cat_dp = IntVar(value=1)  # Descargas Parciais
    var_cat_fc = IntVar(value=1)  # Falha comunicação
    var_cat_fs = IntVar(value=1)  # Falha de Supervisão
    var_cat_pe = IntVar(value=1)  # Perturbações
    var_cat_sa = IntVar(value=1)  # Falha fonte externa SA
    var_cat_io = IntVar(value=1)  # Informações do ONS
    var_cat_tb = IntVar(value=1)  # Transbordo de plantas aquáticas
    var_cat_hd = IntVar(value=1)  # Habilitação e Desabilitação ECE
    var_cat_so = IntVar(value=1)  # Habilitação e Desabilitação ECE

    Label(filtro_window, text="Stadus do Registro:", bg="#CDD505").place(x=145, y=185)
    status_options = ["", "VÁLIDO", "CANCELADO"]
    combo_status = ttk.Combobox(filtro_window, values=status_options, state="readonly")
    combo_status.current(1)
    combo_status.place(x=140, y=205, width=120, height=25)

    Label(filtro_window, text="Selecione as Categorias:", bg="#CDD505").place(x=140, y=245)
    Checkbutton(filtro_window, text="Informações Relevantes", variable=var_cat_ir, bg="#CDD505").place(x=100, y=266)
    Checkbutton(filtro_window, text="Alarmes e Sinalizações", variable=var_cat_as, bg="#CDD505").place(x=100, y=289)
    Checkbutton(filtro_window, text="Anormalidades nas Telemétricas", variable=var_cat_at, bg="#CDD505").place(x=100,
                                                                                                               y=312)
    Checkbutton(filtro_window, text="Comprovação de Disponibilidade", variable=var_cat_cd, bg="#CDD505").place(x=100,
                                                                                                               y=335)
    Checkbutton(filtro_window, text="Comutação de Malha de Controle", variable=var_cat_mc, bg="#CDD505").place(x=100,
                                                                                                               y=358)
    Checkbutton(filtro_window, text="Contato com o Balseiro", variable=var_cat_cb, bg="#CDD505").place(x=100, y=381)
    Checkbutton(filtro_window, text="Descargas Parciais", variable=var_cat_dp, bg="#CDD505").place(x=100, y=404)
    Checkbutton(filtro_window, text="Falha de Comunicação", variable=var_cat_fc, bg="#CDD505").place(x=100, y=427)
    Checkbutton(filtro_window, text="Falha de Supervisão", variable=var_cat_fs, bg="#CDD505").place(x=100, y=450)
    Checkbutton(filtro_window, text="Perturbações de Equipamentos", variable=var_cat_pe, bg="#CDD505").place(x=100,
                                                                                                             y=473)
    Checkbutton(filtro_window, text="Falha fonte externa do Serviço Auxiliar CA", variable=var_cat_sa,
                bg="#CDD505").place(x=100, y=496)
    Checkbutton(filtro_window, text="Informações do ONS", variable=var_cat_io, bg="#CDD505").place(x=100, y=519)
    Checkbutton(filtro_window, text="Transbordo de Macrofitas", variable=var_cat_tb, bg="#CDD505").place(x=100, y=542)
    Checkbutton(filtro_window, text="Habilitação e desabilitação do ECE", variable=var_cat_hd, bg="#CDD505").place(
        x=100, y=565)
    Checkbutton(filtro_window, text="Alimentação SACA por outro Agente", variable=var_cat_so, bg="#CDD505").place(
        x=100, y=588)
    Button(filtro_window, text="Gerar Relatório PDF", font=('arial', 10, 'bold'), fg='#024593',
           command=gerar_pdf_filtrado).place(x=140, y=615, width=140, height=25)


# ---------------------------------------------------
# GERAR RELATÓRIO AVATO PDF (COM FILTROS)
# ---------------------------------------------------
def gerar_pdf_avato(filtros):
    conn = sqlite3.connect('dados_turno.db')
    cursor = conn.cursor()

    pdf = PDF(orientation='P', unit='mm', format='A4')

    # Adiciona as fontes Unicode
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf')

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Inserir figura no cabeçalho
    imagem = 'logo_cog3.png'
    pdf.image(imagem, x=10, y=3, w=190)
    pdf.ln(20)
    margem_esquerda = 10

    instalacoes_selecionadas = filtros.get('instalacoes_selecionadas', [])
    status = filtros.get('status', '')

    # Se não selecionar instalação, avisa e retorna
    if not instalacoes_selecionadas:
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 7, "Nenhuma instalação foi selecionada.", new_x="LMARGIN", new_y="NEXT")
        pdf.output('relatorio_tag_avato.pdf')
        messagebox.showinfo("Relatório", "Nenhuma instalação foi selecionada.")
        conn.close()
        return

    # Define a tabela e as colunas para o relatório avato
    nome_tabela = 'TagAvato'
    colunas = ["ID", "Instalação", "Etiqueta", "Nome no Zabbix", "Nome da Proposta", "Link Zabbix/IP",
               "Responsável", "Telefone Responsável", "Disponibilidade 24h", "Condições de Acesso", "Endereço",
               "Observação", "Dados Atuais"]

    where_clauses = []

    # Filtro por instalações selecionadas
    if instalacoes_selecionadas:
        instalacoes_str = "', '".join(instalacoes_selecionadas)
        where_clauses.append(f"instalacao IN ('{instalacoes_str}')")

    # Filtro por status
    if status != "" and tabela_tem_coluna(cursor, nome_tabela, 'ativo'):
        if status == "CANCELADO":
            where_clauses.append(f"ativo LIKE '%CANCELADO%'")  # Verifica se contém "CANCELADO"
        else:
            where_clauses.append(f"ativo = '{status}'")

    # Monta a cláusula WHERE
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)
    else:
        where_sql = ""

    # Buscar registros da tabela Tagavato
    query = f"SELECT * FROM {nome_tabela} {where_sql}"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Se não houver registros, exibe uma mensagem
    if not rows:
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 7, "Nenhum registro encontrado para os filtros selecionados.", new_x="LMARGIN", new_y="NEXT")
        pdf.output('relatorio_tag_avato.pdf')
        messagebox.showinfo("Relatório", "Nenhum registro encontrado para os filtros selecionados.")
        conn.close()
        return

    # Se houver registros, imprime o título
    pdf.set_font('DejaVu', 'B', 12)
    pdf.set_text_color(0, 159, 77)  # verde
    pdf.cell(0, 10, f"# Dados da TAG-Ávato para abertura de chamado", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('DejaVu', '', 10)
    pdf.set_text_color(0, 0, 0)  # preto

    # Imprime cada registro
    for row in rows:
        for i, valor in enumerate(row):
            nome_coluna = colunas[i] if i < len(colunas) else f"Campo {i}"
            # Converte o valor para string (já com suporte a acentos)
            valor_exibicao = str(valor) if valor is not None else "(Pendente de Lançamento)"

            pdf.set_x(margem_esquerda + 5)

            # Define larguras para as células
            largura_coluna = 45
            largura_valor = 145
            # Exibe o nome da coluna em negrito
            pdf.set_font("DejaVu", style="B", size=10)
            pdf.set_text_color(0, 0, 0)  # Azul Alupar
            pdf.cell(largura_coluna, 6, f"{nome_coluna}: ", new_x="RIGHT", new_y="TOP")

            # Exibe o valor normalmente
            pdf.set_font("DejaVu", style="", size=10)
            pdf.set_text_color(0, 0, 0)  # Preto
            pdf.multi_cell(largura_valor, 6, f"{valor_exibicao}")

        pdf.ln(3)
        # Adicionar uma linha tracejada horizontal de cor verde para separar lançamentos
        x1, x2 = 17, 200
        y = pdf.get_y()
        pdf.set_draw_color(0, 159, 77)
        pdf.set_dash_pattern(dash=1, gap=3)  # Define o padrão tracejado
        pdf.line(x1, y, x2, y)  # Desenha a linha
        pdf.set_dash_pattern()  # Reseta para linha sólida
        pdf.ln(3)  # Pula 3mm depois da linha

    # Adicionar duas linhas horizontais de cor azul para separar categorias
    y = pdf.get_y()
    pdf.set_draw_color(2, 69, 147)
    pdf.line(margem_esquerda, y, 200, y)
    pdf.line(margem_esquerda, y + 1, 200, y + 1)
    pdf.ln(5)

    conn.close()
    pdf.output('relatorio_tag_avato.pdf')
    messagebox.showinfo("Ávato", "Dados gerados com sucesso!")
    caminho1_pdf = "relatorio_tag_avato.pdf"
    abrir_pdf(caminho1_pdf)


# -----------------------------------------------
# FUNÇÕES PARA DEFINIÇÃO DOS FILTROS NA GERAÇÃO DO RELATÓRIO.
# -----------------------------------------------

def abrir_janela_avato_filtro():
    def coletar_instalacoes_selecionadas():
        return [instalacao for instalacao, var in zip(instalacoes, vars) if var.get() == 1]

    # Função para selecionar/desmarcar todos
    def selecionar_tudo():
        estado = var_todos.get()
        for var in vars:
            var.set(estado)

    def gerar_relatorio():
        instalacoes_selecionadas = coletar_instalacoes_selecionadas()
        status_sel = combo_status.get().strip()
        filtros = {
            'instalacoes_selecionadas': instalacoes_selecionadas,
            'status': status_sel
        }
        gerar_pdf_avato(filtros)
        filtro_avato.destroy()

    # Lista de instalações
    instalacoes = [
        "UHE Ferreira Gomes", "SE Macapá", "UHE São José", "UHE Mulher Godoy Pereira",
        "COG-P - Cruzeiro", "COG-R - Lavrinhas", "PCH Queluz", "PCH Verde 8",
        "CGE Pitombeira", "CGE Jandaíra-III", "Florianópolis-SAL (COSR-S)",
        "Florianópolis-SAR (COSR-S)", "Recife-SAL (COSR-NE)", "Recife-SAR (COSR-NE)",
        "Brasília-SAL (COSR-NCO)", "Rio de Janeiro-SAL (COSR-SE)", "Rio de Janeiro-SAR (COSR-SE)"
    ]

    filtro_avato = Toplevel(root)
    filtro_avato.title("Filtros para Relatório Ávato")
    filtro_avato.geometry("400x700")  # Aumentei um pouco a altura
    filtro_avato.resizable(False, False)
    filtro_avato.configure(bg="#CDD505")

    # Lista para armazenar as variáveis dos Checkbuttons individuais
    vars = [IntVar() for _ in instalacoes]

    label_instalacao = Label(filtro_avato, text="Selecionar Instalações:", bg="#CDD505", font=('Arial', 10, 'bold'))
    label_instalacao.place(x=120, y=10)

    # NOVO: Checkbutton "Todas as Instalações"
    var_todos = IntVar()
    chk_todos = Checkbutton(filtro_avato, text="Selecionar Todas", variable=var_todos,
                            command=selecionar_tudo, bg="#CDD505", font=('Arial', 9))
    chk_todos.place(x=100, y=40)

    # Cria os Checkbuttons dinamicamente (ajustei o y inicial para 70 para não sobrepor)
    for i, (instalacao, var) in enumerate(zip(instalacoes, vars)):
        Checkbutton(filtro_avato, text=instalacao, variable=var, bg="#CDD505").place(x=100, y=70 + 25 * i)

    label_categoria = Label(filtro_avato, text="Status do Registro:", bg="#CDD505")
    label_categoria.place(x=145, y=550)

    status_options = ["", "VÁLIDO", "CANCELADO"]
    combo_status = ttk.Combobox(filtro_avato, values=status_options, state="readonly")
    combo_status.current(1)
    combo_status.place(x=140, y=575, width=120, height=30)

    bt1 = Button(filtro_avato, text="Gerar Relatório", font=('arial', 10, 'bold'), fg='#024593',
                 command=gerar_relatorio).place(x=140, y=630, width=120, height=30)


# ---------------------------------------------------
# EXIBIR PDF EM TELA DA TAG-ÁVATO
# ---------------------------------------------------
def abrir_pdf(caminho1_pdf):
    so = platform.system()

    if so == "Windows":
        os.startfile(caminho1_pdf)
    elif so == "Darwin":  # macOS
        subprocess.run(["open", caminho1_pdf])
    else:  # Linux e afins
        subprocess.run(["xdg-open", caminho1_pdf])


# ---------------------------------------------------
# GERAR RELATÓRIO PROTOCOLO PDF (COM FILTROS)
# ---------------------------------------------------
def gerar_pdf_protocolo(filtros):
    conn = sqlite3.connect('dados_turno.db')
    cursor = conn.cursor()

    pdf = PDF(orientation='P', unit='mm', format='A4')

    # Adiciona as fontes Unicode
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf')

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Inserir figura no cabeçalho
    imagem = 'logo_cog4.png'
    pdf.image(imagem, x=10, y=3, w=190)
    pdf.ln(20)
    margem_esquerda = 10  # Define um deslocamento geral para o conteúdo

    instalacao_selecionadas = filtros.get('instalacao_selecionadas', [])
    status = filtros.get('status', '')

    # Se o usuário não selecionar NENHUMA instalação, avise e retorne
    if not instalacao_selecionadas:
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 7, "Nenhuma instalação foi selecionada.", new_x="LMARGIN", new_y="NEXT")
        pdf.output('relatorio_tag_protocolo.pdf')
        messagebox.showinfo("Relatório", "Nenhuma instalação foi selecionada.")
        conn.close()
        return

    # Define a tabela e as colunas para o relatório protocolo
    nome_tabela = 'Protocolo'
    colunas = ["ID", "Instalação", "Concessionária", "Atend. Grandes Clientes", "WhatsApp", "Site",
               "Titular da Conta", "CNPJ", "Endereço", "CEP, Cidade e UF", "Unidade Consumidora", "Parceiro de Negócio",
               "Número do Cliente", "Número da Instalação", "Código do Cliente", "Código da Instalação", "Código Único",
               "Senha", "Dados Atuais"]

    where_clauses = []

    # Filtro por instalações selecionadas
    if instalacao_selecionadas:
        instalacao_str = "', '".join(instalacao_selecionadas)
        where_clauses.append(f"instalacao IN ('{instalacao_str}')")

    # Filtro por status
    if status != "" and tabela_tem_coluna(cursor, nome_tabela, 'ativo'):
        if status == "CANCELADO":
            where_clauses.append(f"ativo LIKE '%CANCELADO%'")  # Verifica se contém "CANCELADO"
        else:
            where_clauses.append(f"ativo = '{status}'")

    # Monta a cláusula WHERE
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)
    else:
        where_sql = ""

    # Buscar registros da tabela Protocolo
    query = f"SELECT * FROM {nome_tabela} {where_sql}"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Se não houver registros, exibe uma mensagem
    if not rows:
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 7, "Nenhum registro encontrado para os filtros selecionados.", new_x="LMARGIN", new_y="NEXT")
        pdf.output('relatorio_tag_protocolo.pdf')
        messagebox.showinfo("Relatório", "Nenhum registro encontrado para os filtros selecionados.")
        conn.close()
        return

    # Se houver registros, imprime o título
    pdf.set_font('DejaVu', 'B', 12)
    pdf.set_text_color(0, 159, 77)  # verde
    pdf.cell(0, 10, f"# Dados para abertura de chamado nas Concessionárias", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('DejaVu', '', 10)
    pdf.set_text_color(0, 0, 0)  # preto

    # Imprime cada registro
    for row in rows:
        for i, valor in enumerate(row):
            nome_coluna = colunas[i] if i < len(colunas) else f"Campo {i}"
            valor_exibicao = str(valor) if valor is not None else "(Pendente de Lançamento)"
            pdf.set_x(margem_esquerda + 5)

            # Define larguras para as células
            largura_coluna = 55  # Largura
            largura_valor = 135  # Largura

            # Exibe o nome da coluna em negrito
            pdf.set_font("DejaVu", style="B", size=10)
            pdf.set_text_color(0, 0, 0)  # Azul Alupar
            pdf.cell(largura_coluna, 6, f"{nome_coluna}: ", new_x="RIGHT", new_y="TOP")

            # Exibe o valor normalmente
            pdf.set_font("DejaVu", style="", size=10)
            pdf.set_text_color(0, 0, 0)  # Preto
            pdf.multi_cell(largura_valor, 6, f"{valor_exibicao}")

        # Adicionar uma linha tracejada horizontal de cor verde para separar lançamentos
        pdf.ln(3)  # pula 3mm antes da linha
        x1, x2 = 17, 200
        y = pdf.get_y()
        pdf.set_draw_color(0, 159, 77)
        pdf.set_dash_pattern(dash=1, gap=3)  # Define o padrão tracejado
        pdf.line(x1, y, x2, y)  # Desenha a linha
        pdf.set_dash_pattern()  # Reseta para linha sólida
        pdf.ln(3)  # Pula 3mm depois da linha

    # Adicionar duas linhas horizontais de cor azul para separar categorias
    y = pdf.get_y()
    pdf.set_draw_color(2, 69, 147)
    pdf.line(margem_esquerda, y, 200, y)
    pdf.line(margem_esquerda, y + 1, 200, y + 1)
    pdf.ln(5)

    conn.close()
    pdf.output('relatorio_protocolo.pdf')
    messagebox.showinfo("Protocolos", "Dados gerados com sucesso!")
    caminho2_pdf = "relatorio_protocolo.pdf"
    abrir_pdf(caminho2_pdf)


# ---------------------------------------------------
# FUNÇÕES PARA DEFINIÇÃO DOS FILTROS NA GERAÇÃO DO RELATÓRIO.
# ---------------------------------------------------
def abrir_janela_protocolo_filtro():
    def coletar_instalacao_selecionadas():
        instalacao_selecionadas = []
        if var_cb1p.get() == 1:
            instalacao_selecionadas.append("UHE Mülher de Godoy Pereira")
        if var_cb2p.get() == 1:
            instalacao_selecionadas.append("SE Itaguaçu")
        if var_cb3p.get() == 1:
            instalacao_selecionadas.append("CGE Pitombeira")
        if var_cb4p.get() == 1:
            instalacao_selecionadas.append("SE Russas-II")
        if var_cb5p.get() == 1:
            instalacao_selecionadas.append("CGE Jandaíra-III")
        if var_cb6p.get() == 1:
            instalacao_selecionadas.append("UHE Ferreira Gomes")
        if var_cb7p.get() == 1:
            instalacao_selecionadas.append("SE Macapá")
        if var_cb8p.get() == 1:
            instalacao_selecionadas.append("COG-P - Cruzeiro")
        return instalacao_selecionadas

    def gerar_relatorio():
        instalacao_selecionadas = coletar_instalacao_selecionadas()
        status_sel = combo_status.get().strip()
        filtros = {
            'instalacao_selecionadas': instalacao_selecionadas,
            'status': status_sel
        }
        gerar_pdf_protocolo(filtros)  # Chama a função correta para gerar o relatório protocolo
        filtro_protocolo.destroy()

    filtro_protocolo = Toplevel(root)
    filtro_protocolo.title("PROTOCOLOS COM EMPRESAS")
    filtro_protocolo.geometry("400x450")
    filtro_protocolo.resizable(False, False)
    filtro_protocolo.configure(bg="#CDD505")
    # ---------------------------------------------------
    # CHECKBUTTONS DAS INSTALAÇÕES
    # ---------------------------------------------------
    var_cb1p = IntVar()  # UHE MGP
    var_cb2p = IntVar()  # SE IGU
    var_cb3p = IntVar()  # CGE PTM
    var_cb4p = IntVar()  # SE RSD
    var_cb5p = IntVar()  # CGE JDT
    var_cb6p = IntVar()  # UHE FGO
    var_cb7p = IntVar()  # SE MCP
    var_cb8p = IntVar()  # COG-P

    Label(filtro_protocolo, text="Selecionar Instalações:", bg="#CDD505").place(x=140, y=15)
    Checkbutton(filtro_protocolo, text="UHE MGP", variable=var_cb1p, bg="#CDD505").place(x=100, y=60)
    Checkbutton(filtro_protocolo, text="SE IGU", variable=var_cb2p, bg="#CDD505").place(x=100, y=85)
    Checkbutton(filtro_protocolo, text="CGE PTM", variable=var_cb3p, bg="#CDD505").place(x=100, y=110)
    Checkbutton(filtro_protocolo, text="SE RSD", variable=var_cb4p, bg="#CDD505").place(x=100, y=135)
    Checkbutton(filtro_protocolo, text="CGE JDT", variable=var_cb5p, bg="#CDD505").place(x=100, y=160)
    Checkbutton(filtro_protocolo, text=" UHE FGO ", variable=var_cb6p, bg="#CDD505").place(x=100, y=185)
    Checkbutton(filtro_protocolo, text=" SE MCP ", variable=var_cb7p, bg="#CDD505").place(x=100, y=210)
    Checkbutton(filtro_protocolo, text=" COG-P ", variable=var_cb8p, bg="#CDD505").place(x=100, y=235)

    Label(filtro_protocolo, text="Status do Registro:", bg="#CDD505").place(x=145, y=280)
    status_options = ["", "VÁLIDO", "CANCELADO"]
    combo_status = ttk.Combobox(filtro_protocolo, values=status_options, state="readonly")
    combo_status.current(1)
    combo_status.place(x=140, y=300, width=120, height=30)

    bt1 = Button(filtro_protocolo, text="Gerar Relatório", font=('arial', 10, 'bold'), fg='#024593',
                 command=gerar_relatorio)
    bt1.place(x=140, y=380, width=120, height=30)

    # ---------------------------------------------------
    # EXIBIR PDF EM TELA PROTOCOLO
    # ---------------------------------------------------
    def abrir_pdf(caminho2_pdf):
        so = platform.system()

        if so == "Windows":
            os.startfile(caminho2_pdf)
        elif so == "Darwin":  # macOS
            subprocess.run(["open", caminho2_pdf])
        else:  # Linux e afins
            subprocess.run(["xdg-open", caminho2_pdf])


# ---------------------------------------------------
# FUNÇÃO PARA SELECIONAR DATA E HORA
# ---------------------------------------------------
def selecionar_data(entry, tipo):
    def salvar_data():
        data_selecionada = cal.selection_get().strftime('%d/%m/%Y')
        hora_atual = datetime.now().strftime('%H:%M')
        if tipo == "inicio":
            entry.delete(0, END)
            entry.insert(0, f"{data_selecionada} - {hora_atual}h")
        else:
            entry.delete(0, END)
            entry.insert(0, f"{data_selecionada} - {hora_atual}h")

        janela_cal.destroy()

    janela_cal = Toplevel(root)
    janela_cal.title("Selecione a Data")
    cal = Calendar(janela_cal, selectmode='day', date_pattern='dd-mm-yyyy')
    cal.pack(pady=20)

    Button(janela_cal, text="Salvar", command=salvar_data).pack(pady=10)


# ---------------------------------------------------
# CANCELAMENTO DE REGISTROS:
# ---------------------------------------------------
def invalidar_registro(tabela, id_registro):
    conexao = sqlite3.connect('dados_turno.db')
    cursor = conexao.cursor()

    # Atualiza o campo 'ativo' para 'NÃO' para o registro específico
    query = f"UPDATE {tabela} SET ativo = ? WHERE id = ?"
    cursor.execute(query, (f"CANCELADO - (Cancelado por: {current_user})", id_registro))

    conexao.commit()
    conexao.close()
    messagebox.showinfo("Sucesso", "Registro marcado como CANCELADO!")


# ---------------------------------------------------
# JANELAS PARA LANÇAMENTOS DAS INFORMAÇÕES
# ---------------------------------------------------
# Função para janela de Informações Relevantes
def cmd_click1():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    info_relev = Toplevel(root)
    info_relev.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    info_relev.geometry('1100x667')
    info_relev.resizable(True, True)
    info_relev.minsize(1100, 667)
    info_relev['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(info_relev, text='Informações Relevantes', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    Label(info_relev, text='Data e Hora:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(info_relev)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(info_relev, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.40,
                                                                                                            rely=0.15,
                                                                                                            anchor="w")
    Label(info_relev, text='Cancelar Registro', bg="#a4bad2").place(relx=0.85, rely=0.15, anchor="w")

    Label(info_relev, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    localidades = ["COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM",
                   "CGE JDT", "UFV PTM", "SE IGU", "SE MCP", "SE CLA", "SE SCA", "SE IPG", "SE RSD", "SE JDD"]
    combobox_localidade = ttk.Combobox(info_relev, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")

    Label(info_relev, text='Instalação:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    entry_instalacao = Entry(info_relev)
    entry_instalacao.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    Label(info_relev, text='Equipamento:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    entry_equipamento = Entry(info_relev, width=30)
    entry_equipamento.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    Label(info_relev, text='Descrição:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="nw")
    text_descricao = Text(info_relev, width=70, height=4)
    text_descricao.place(relx=0.2, rely=0.60, anchor="w")

    Label(info_relev, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.75, anchor="nw")
    text_observacao = Text(info_relev, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.80, anchor="w")

    ativos = ["VÁLIDO", "CANCELADO"]
    Label(info_relev, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    combobox_ativo = ttk.Combobox(info_relev, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        combobox_localidade.set('')
        entry_instalacao.delete(0, END)
        entry_equipamento.delete(0, END)
        text_descricao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_info_relev():
        # Obter valores digitados
        data_hora = entry_data_hora.get().strip()
        localidade = combobox_localidade.get().strip()
        instalacao = entry_instalacao.get().strip()
        equipamento = entry_equipamento.get().strip()
        descricao = text_descricao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_hora or not localidade or not instalacao or not equipamento or not descricao or not ativo:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Se estiver tudo preenchido, salvar
        salvar_dados(
            'InformacoesRelevantes',
            {
                'data_hora': data_hora,
                'localidade': localidade,
                'instalacao': instalacao,
                'equipamento': equipamento,
                'descricao': descricao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        info_relev.destroy()

    # Botão "Salvar"
    Button(info_relev, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_info_relev).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(info_relev, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(info_relev, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=info_relev.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('InformacoesRelevantes', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(info_relev, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(info_relev, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(info_relev, text="Confirmar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# =============================================================================================
# Função para janela de Alarmnes e Sinalizações
def cmd_click2():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    alar_sinal = Toplevel(root)
    alar_sinal.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    alar_sinal.geometry('1100x667')
    alar_sinal.resizable(True, True)
    alar_sinal.minsize(1100, 667)
    alar_sinal['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(alar_sinal, text='Alarmes e Sinalizações', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(alar_sinal, text='Data e Hora:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(alar_sinal, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(alar_sinal, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.40,
                                                                                                            rely=0.15,
                                                                                                            anchor="w")
    Label(alar_sinal, text='Cancelar Registro', bg="#a4bad2").place(relx=0.85, rely=0.15, anchor="w")

    # ComboBox para Localidade
    Label(alar_sinal, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    localidades = ["COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM",
                   "CGE JDT", "UFV PTM", "SE IGU", "SE MCP", "SE CLA", "SE SCA", "SE IPG", "SE RSD", "SE JDD"]
    combobox_localidade = ttk.Combobox(alar_sinal, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")

    # Entry para Instalação
    Label(alar_sinal, text='Instalação:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    entry_instalacao = Entry(alar_sinal, width=30)
    entry_instalacao.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # Entry para TAG do Alarme
    Label(alar_sinal, text='TAG-Alarme:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    entry_tagalarme = Entry(alar_sinal, width=30)
    entry_tagalarme.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Text para Descrição do Alarme
    Label(alar_sinal, text='Descrição do Alarme:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="nw")
    text_descricao = Text(alar_sinal, width=70, height=4)
    text_descricao.place(relx=0.2, rely=0.60, anchor="w")

    # ComboBox para Informado Instalação
    Label(alar_sinal, text='Comunicado Instalação:', bg="#a4bad2").place(relx=0.05, rely=0.75, anchor="w")
    centros = ["SIM", "NÃO"]
    combobox_resp = ttk.Combobox(alar_sinal, values=centros, state="readonly")
    combobox_resp.place(relx=0.2, rely=0.75, width=200, height=25, anchor="w")
    combobox_resp.set("SIM")  # Define "SIM" como padrão

    # Entry para Responsável Instalação
    Label(alar_sinal, text='Profissional:', bg="#a4bad2").place(relx=0.4, rely=0.75, anchor="w")
    entry_operador = Entry(alar_sinal, width=33)
    entry_operador.place(relx=0.48, rely=0.75, width=200, height=25, anchor="w")

    # ComboBox para Ativo
    Label(alar_sinal, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.90, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(alar_sinal, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.90, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    # limpa os campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        combobox_localidade.set('')
        entry_instalacao.delete(0, END)
        entry_tagalarme.delete(0, END)
        text_descricao.delete('1.0', END)
        combobox_resp.set('')
        entry_operador.delete(0, END)
        combobox_ativo.set('')

    def salvar_alar_sinal():
        data_hora = entry_data_hora.get().strip()
        localidade = combobox_localidade.get().strip()
        instalacao = entry_instalacao.get().strip()
        tag_alarme = entry_tagalarme.get().strip()
        descricao_alarme = text_descricao.get("1.0", END).strip()
        comunicado = combobox_resp.get().strip()
        profissional = entry_operador.get().strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_hora or not localidade or not instalacao or not tag_alarme or not descricao_alarme or not comunicado or not profissional or not ativo:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        salvar_dados(
            'AlarmesSinalizacoes',
            {
                'data_hora': data_hora,
                'localidade': localidade,
                'instalacao': instalacao,
                'tag_alarme': tag_alarme,
                'descricao_alarme': descricao_alarme,
                'comunicado': comunicado,
                'profissional': profissional,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        alar_sinal.destroy()

    # Botão "Salvar"
    Button(alar_sinal, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_alar_sinal).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(alar_sinal, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(alar_sinal, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=alar_sinal.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('AlarmesSinalizacoes', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(alar_sinal, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(alar_sinal, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(alar_sinal, text="Confirmar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# ==================================================================================================
# Função para janela de Anormalidades Telemétricas

def cmd_click3():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    anom_telem = Toplevel(root)
    anom_telem.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    anom_telem.geometry('1100x667')
    anom_telem.resizable(True, True)
    anom_telem.minsize(1100, 667)
    anom_telem['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(anom_telem, text='Anormalidades nas Estações Telemétricas', font=('Arial', 14, 'bold'), bg="#024593",
          fg="white", anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(anom_telem, text='Data e Hora:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(anom_telem, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(anom_telem, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.4,
                                                                                                            rely=0.15,
                                                                                                            anchor="w")
    Label(anom_telem, text='Cancelar Registro', bg="#a4bad2").place(relx=0.85, rely=0.15, anchor="w")

    # ComboBox para Localidade
    Label(anom_telem, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    localidades = ["COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM",
                   "CGE JDT", "UFV PTM", "SE IGU", "SE MCP", "SE CLA", "SE SCA", "SE IPG", "SE RSD", "SE JDD"]
    combobox_localidade = ttk.Combobox(anom_telem, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")

    # ComboBox para Estação
    Label(anom_telem, text='Estação:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    estacoes = ["Nível Montante", "Nível Jusante", "Vazão Defluente", "Pluviômetro", "Fluviômetro", "Sonda-1",
                "Sonda-2", "Outras"]
    combobox_estacao = ttk.Combobox(anom_telem, values=estacoes, state="readonly")
    combobox_estacao.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # Entry para Complemento da Estação
    Label(anom_telem, text='Complemento da Estação:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    entry_complemento = Entry(anom_telem, width=92)
    entry_complemento.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Text para Descrição da Anormalidade
    Label(anom_telem, text='Descrição da Anormalidade:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    text_descricao = Text(anom_telem, width=70, height=4)
    text_descricao.place(relx=0.2, rely=0.59, anchor="w")

    # Text para Observação
    Label(anom_telem, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.75, anchor="w")
    text_observacao = Text(anom_telem, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.78, anchor="w")

    # ComboBox para Ativo
    Label(anom_telem, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(anom_telem, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        combobox_localidade.set('')
        combobox_estacao.delete('')
        entry_complemento.delete(0, END)
        text_descricao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_anom_telem():
        data_hora = entry_data_hora.get().strip()
        localidade = combobox_localidade.get().strip()
        estacao = combobox_estacao.get().strip()
        complem_estacao = entry_complemento.get().strip()
        descricao_anormal = text_descricao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_hora or not localidade or not estacao or not complem_estacao or not descricao_anormal or not ativo:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        salvar_dados(
            'AnormalidadesTelemetricas',
            {
                'data_hora': data_hora,
                'localidade': localidade,
                'estacao': estacao,
                'complem_estacao': complem_estacao,
                'descricao_anormal': descricao_anormal,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        anom_telem.destroy()

    # Botão "Salvar"
    Button(anom_telem, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_anom_telem).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(anom_telem, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(anom_telem, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=anom_telem.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro
    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('AnormalidadesTelemetricas', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(anom_telem, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(anom_telem, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(anom_telem, text="Confirmar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# ========================================================================================================
# Função para janela de Comprovação de Disponibilidade de Ugs
def cmd_click4():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    comp_disp = Toplevel(root)
    comp_disp.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    comp_disp.geometry('1100x667')
    comp_disp.resizable(True, True)
    comp_disp.minsize(1100, 667)
    comp_disp['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(comp_disp, text='Comprovação de Disponibilidade', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(comp_disp, text='Data e Hora de Início:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(comp_disp, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(comp_disp, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.4,
                                                                                                           rely=0.15,
                                                                                                           anchor="w")
    Label(comp_disp, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83, rely=0.15,
                                                                                                   anchor="w")

    # Campos de Data e Hora de Término
    Label(comp_disp, text='Data e Hora de Término:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_termino = Entry(comp_disp, width=30)
    entry_termino.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")
    Button(comp_disp, text="Selecionar", command=lambda: selecionar_data(entry_termino, "termino")).place(relx=0.4,
                                                                                                          rely=0.25,
                                                                                                          anchor="w")
    # ComboBox para Localidade
    Label(comp_disp, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    localidades = ["UHE MGP", "UHE FGO", "UHE SJO"]
    combobox_localidade = ttk.Combobox(comp_disp, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # ComboBox para Unidade Geradora
    Label(comp_disp, text='Unidade Geradora:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    unidades = ["UG-1", "UG-2", "UG-3"]
    combobox_unidade = ttk.Combobox(comp_disp, values=unidades, state="readonly")
    combobox_unidade.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Entry para Potência Média Gerada durante o teste
    Label(comp_disp, text='Potência média gerada:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    entry_potencia = Entry(comp_disp, width=23)
    entry_potencia.place(relx=0.2, rely=0.55, width=200, height=25, anchor="w")

    # Text para Informação Adicionais
    Label(comp_disp, text='Informações Adicionais:', bg="#a4bad2").place(relx=0.05, rely=0.65, anchor="w")
    text_informacao = Text(comp_disp, width=65, height=4)
    text_informacao.place(relx=0.2, rely=0.65, anchor="w")

    # Text para Observação
    Label(comp_disp, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.75, anchor="w")
    text_observacao = Text(comp_disp, width=65, height=3)
    text_observacao.place(relx=0.2, rely=0.78, anchor="w")

    # ComboBox para Identificação do COSR-ONS
    Label(comp_disp, text='Centro Operação ONS:', bg="#a4bad2").place(relx=0.05, rely=0.88, anchor="w")
    centros = ["COSR-S", "COSR-NCO"]
    combobox_ons = ttk.Combobox(comp_disp, values=centros, state="readonly")
    combobox_ons.place(relx=0.2, rely=0.88, width=200, height=25, anchor="w")

    # Entry para Operador do ONS
    Label(comp_disp, text='Operador ONS:', bg="#a4bad2").place(relx=0.39, rely=0.88, anchor="w")
    entry_operador = Entry(comp_disp, width=27)
    entry_operador.place(relx=0.47, rely=0.88, width=200, height=25, anchor="w")

    # ComboBox para Ativo
    Label(comp_disp, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(comp_disp, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    # Botão para atualizar a data de término
    Button(comp_disp, text="Inserir", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: abrir_janela_atualizacao_data_termino('ComprovacaoDisponibilidade',
                                                                 entry_id_registro.get().strip())).place(relx=0.85,
                                                                                                         rely=0.35,
                                                                                                         anchor="w")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        entry_termino.delete(0, END)
        combobox_localidade.set('')
        combobox_unidade.set('')
        entry_potencia.delete(0, END)
        text_informacao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ons.set('')
        entry_operador.delete(0, END)
        combobox_ativo.set('')

    def salvar_comp_disp():
        data_inicio = entry_data_hora.get().strip()
        data_termino = entry_termino.get().strip() if entry_termino.get().strip() else None
        localidade = combobox_localidade.get().strip()
        unidade_geradora = combobox_unidade.get().strip()
        potencia_gerada = entry_potencia.get().strip()
        informacoes_adicionais = text_informacao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        centro_ons = combobox_ons.get().strip()
        operador_ons = entry_operador.get().strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not unidade_geradora or not centro_ons:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Data de término posterior a data de início
        if data_termino:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y - %H:%Mh")
                dt_termino = datetime.strptime(data_termino, "%d/%m/%Y - %H:%Mh")
                if dt_termino < dt_inicio:
                    messagebox.showerror("Erro",
                                         "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use o calendário")
                return

        salvar_dados(
            'ComprovacaoDisponibilidade',
            {
                'data_inicio': data_inicio,
                'data_termino': data_termino,
                'localidade': localidade,
                'unidade_geradora': unidade_geradora,
                'potencia_gerada': potencia_gerada,
                'informacoes_adicionais': informacoes_adicionais,
                'observacao': observacao,
                'centro_ons': centro_ons,
                'operador_ons': operador_ons,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        comp_disp.destroy()

    # Botão "Salvar"
    Button(comp_disp, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_comp_disp).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(comp_disp, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(comp_disp, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=comp_disp.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('ComprovacaoDisponibilidade', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(comp_disp, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(comp_disp, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(comp_disp, text="Cancelar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# ==========================================================================================================
# Função para janela de Comutação de Malha de Controle
def cmd_click5():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    comut_malha = Toplevel(root)
    comut_malha.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    comut_malha.geometry('1100x667')
    comut_malha.resizable(True, True)
    comut_malha.minsize(1100, 667)
    comut_malha['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(comut_malha, text='Comutação de Malha de Controle', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(comut_malha, text='Data e Hora de Início:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(comut_malha, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(comut_malha, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.4,
                                                                                                             rely=0.15,
                                                                                                             anchor="w")
    Label(comut_malha, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83,
                                                                                                     rely=0.15,
                                                                                                     anchor="w")
    # Campos de Data e Hora de Término
    Label(comut_malha, text='Data e Hora de Término:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_termino = Entry(comut_malha, width=30)
    entry_termino.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")
    Button(comut_malha, text="Selecionar", command=lambda: selecionar_data(entry_termino, "termino")).place(relx=0.4,
                                                                                                            rely=0.25,
                                                                                                            anchor="w")
    # ComboBox para Localidade
    Label(comut_malha, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    localidades = ["UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE"]
    combobox_localidade = ttk.Combobox(comut_malha, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # ComboBox para Unidade Geradora
    Label(comut_malha, text='Unidade Geradora:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    unidades = ["UG-1", "UG-2", "UG-3"]
    combobox_unidade = ttk.Combobox(comut_malha, values=unidades, state="readonly")
    combobox_unidade.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # ComboBox para Modo de Controle
    Label(comut_malha, text='Modo de Controle:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    mcontrole = ["Controle de Potência", "Controle de Velocidade", "Controle de Abertura"]
    combobox_mcontrole = ttk.Combobox(comut_malha, values=mcontrole, state="readonly")
    combobox_mcontrole.place(relx=0.2, rely=0.55, width=200, height=25, anchor="w")

    # ComboBox para Modo de Rede
    Label(comut_malha, text='Rede:', bg="#a4bad2").place(relx=0.38, rely=0.55, anchor="w")
    mredes = ["Isolada", "Interligada"]
    combobox_mrede = ttk.Combobox(comut_malha, values=mredes, state="readonly")
    combobox_mrede.place(relx=0.43, rely=0.55, width=200, height=25, anchor="w")

    # Text para Motivo/Causa
    Label(comut_malha, text='Motivo / Causa:', bg="#a4bad2").place(relx=0.05, rely=0.65, anchor="w")
    text_motivo = Text(comut_malha, width=70, height=4)
    text_motivo.place(relx=0.2, rely=0.70, anchor="w")

    # Text para Observação
    Label(comut_malha, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.8, anchor="w")
    text_observacao = Text(comut_malha, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.85, anchor="w")

    # ComboBox para Ativo
    Label(comut_malha, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(comut_malha, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    # Botão para atualizar a data de término
    Button(comut_malha, text="Inserir", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: abrir_janela_atualizacao_data_termino('MalhaControle',
                                                                 entry_id_registro.get().strip())).place(relx=0.85,
                                                                                                         rely=0.35,
                                                                                                         anchor="w")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        entry_termino.delete(0, END)
        combobox_localidade.set('')
        combobox_unidade.set('')
        combobox_mcontrole.set('')
        combobox_mrede.set('')
        text_motivo.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_comut_malha():
        data_inicio = entry_data_hora.get().strip()
        data_termino = entry_termino.get().strip() if entry_termino.get().strip() else None
        localidade = combobox_localidade.get().strip()
        unidade_geradora = combobox_unidade.get().strip()
        modo_controle = combobox_mcontrole.get().strip()
        rede = combobox_mrede.get().strip()
        motivo_causa = text_motivo.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not unidade_geradora or not modo_controle or not rede or not motivo_causa:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Data de término posterior a data de início
        if data_termino:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y - %H:%Mh")
                dt_termino = datetime.strptime(data_termino, "%d/%m/%Y - %H:%Mh")
                if dt_termino < dt_inicio:
                    messagebox.showerror("Erro",
                                         "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use o calendário")
                return

        salvar_dados(
            'MalhaControle',
            {
                'data_inicio': data_inicio,
                'data_termino': data_termino,
                'localidade': localidade,
                'unidade_geradora': unidade_geradora,
                'modo_controle': modo_controle,
                'rede': rede,
                'motivo_causa': motivo_causa,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        comut_malha.destroy()

    # Botão "Salvar"
    Button(comut_malha, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_comut_malha).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(comut_malha, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(comut_malha, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=comut_malha.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('MalhaControle', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(comut_malha, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(comut_malha, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(comut_malha, text="Cancelar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# ================================================================================================================
# Função para janela de Balseiro da UHE SJO
def cmd_click6():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    cont_balsa = Toplevel(root)
    cont_balsa.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    cont_balsa.geometry('1100x667')
    cont_balsa.resizable(True, True)
    cont_balsa.minsize(1100, 667)
    cont_balsa['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(cont_balsa, text='Contato com Balseiro da UHE SJO', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(cont_balsa, text='Data e Hora:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(cont_balsa, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(cont_balsa, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.4,
                                                                                                            rely=0.15,
                                                                                                            anchor="w")
    Label(cont_balsa, text='Cancelar Registro', bg="#a4bad2").place(relx=0.85, rely=0.15, anchor="w")

    # ComboBox para Localidade
    Label(cont_balsa, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    localidades = ["COG-P", "UHE SJO"]
    combobox_localidade = ttk.Combobox(cont_balsa, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")

    # ComboBox para Estação
    Label(cont_balsa, text='Motivo Contato:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    estacoes = ["Aumento de Vazão > 200 m3/s", "Outros"]
    combobox_motivo = ttk.Combobox(cont_balsa, values=estacoes, state="readonly")
    combobox_motivo.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # Entry para Complemento da Estação
    Label(cont_balsa, text='Complemento Mot. Contato:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    entry_complemento = Entry(cont_balsa, width=92)
    entry_complemento.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Text para Descrição da Anormalidade
    Label(cont_balsa, text='Informações Adicionais:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="nw")
    text_informacao = Text(cont_balsa, width=70, height=4)
    text_informacao.place(relx=0.2, rely=0.60, anchor="w")

    # Text para Observação
    Label(cont_balsa, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.75, anchor="nw")
    text_observacao = Text(cont_balsa, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.80, anchor="w")

    # ComboBox para Ativo
    Label(cont_balsa, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(cont_balsa, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        combobox_localidade.set('')
        combobox_motivo.set('')
        entry_complemento.delete(0, END)
        text_informacao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_cont_balsa():
        data_inicio = entry_data_hora.get().strip()
        localidade = combobox_localidade.get().strip()
        motivo = combobox_motivo.get().strip()
        complem_motivo = entry_complemento.get().strip()
        informacao = text_informacao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not motivo or not complem_motivo:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        salvar_dados(
            'ContatoBalseiro',
            {
                'data_hora': data_inicio,
                'localidade': localidade,
                'motivo': motivo,
                'complem_motivo': complem_motivo,
                'informacao': informacao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        cont_balsa.destroy()

    # Botão "Salvar"
    Button(cont_balsa, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_cont_balsa).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(cont_balsa, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(cont_balsa, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=cont_balsa.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('ContatoBalseiro', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(cont_balsa, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(cont_balsa, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(cont_balsa, text="Confirmar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# ==================================================================
# Função para janela de Descargas Parciais
def cmd_click7():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    desc_parc = Toplevel(root)
    desc_parc.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    desc_parc.geometry('1100x667')
    desc_parc.resizable(True, True)
    desc_parc.minsize(1100, 667)
    desc_parc['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(desc_parc, text='Testes de Descargas Parciais', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(desc_parc, text='Data e Hora de Início:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(desc_parc, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(desc_parc, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.4,
                                                                                                           rely=0.15,
                                                                                                           anchor="w")
    Label(desc_parc, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83, rely=0.15,
                                                                                                   anchor="w")
    # Campos de Data e Hora de Término
    Label(desc_parc, text='Data e Hora de Término:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_termino = Entry(desc_parc, width=30)
    entry_termino.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")
    Button(desc_parc, text="Selecionar", command=lambda: selecionar_data(entry_termino, "termino")).place(relx=0.4,
                                                                                                          rely=0.25,
                                                                                                          anchor="w")
    # ComboBox para Localidade
    Label(desc_parc, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    localidades = ["UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE"]
    combobox_localidade = ttk.Combobox(desc_parc, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # ComboBox para Unidades Geradoras
    Label(desc_parc, text='Unidade Geradora:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    unidades = ["UG-1", "UG-2", "UG-3", "UG-1 e 2", "UG-1 e UG-3", "UG-2 e 3", "UG-1, 2 e 3"]
    combobox_unidade = ttk.Combobox(desc_parc, values=unidades, state="readonly")
    combobox_unidade.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Text para Informações Adcionais
    Label(desc_parc, text='Informações Adicionais:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="nw")
    text_informacao = Text(desc_parc, width=70, height=4)
    text_informacao.place(relx=0.2, rely=0.60, anchor="w")

    # Text para Observação
    Label(desc_parc, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.75, anchor="nw")
    text_observacao = Text(desc_parc, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.80, anchor="w")

    # ComboBox para Ativo
    Label(desc_parc, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(desc_parc, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    Button(desc_parc, text="Inserir", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: abrir_janela_atualizacao_data_termino('DescargasParciais',
                                                                 entry_id_registro.get().strip())).place(relx=0.85,
                                                                                                         rely=0.35,
                                                                                                         anchor="w")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        entry_termino.delete(0, END)
        combobox_localidade.set('')
        combobox_unidade.set('')
        text_informacao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_desc_parc():
        data_inicio = entry_data_hora.get().strip()
        data_termino = entry_termino.get().strip() if entry_termino.get().strip() else None
        localidade = combobox_localidade.get().strip()
        unidade_geradora = combobox_unidade.get().strip()
        informacao = text_informacao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()
        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not unidade_geradora or not informacao:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Data de término posterior a data de início
        if data_termino:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y - %H:%Mh")
                dt_termino = datetime.strptime(data_termino, "%d/%m/%Y - %H:%Mh")
                if dt_termino < dt_inicio:
                    messagebox.showerror("Erro",
                                         "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use o calendário")
                return

        salvar_dados(
            'DescargasParciais',
            {
                'data_inicio': data_inicio,
                'data_termino': data_termino,
                'localidade': localidade,
                'unidade_geradora': unidade_geradora,
                'informacao': informacao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        desc_parc.destroy()

    # Botão "Salvar"
    Button(desc_parc, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_desc_parc).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(desc_parc, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(desc_parc, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=desc_parc.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('DescargasParciais', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(desc_parc, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(desc_parc, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(desc_parc, text="Cancelar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# ===========================================================================================================
# Função para janela de Falha de Comunicação
def cmd_click8():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    falh_comm = Toplevel(root)
    falh_comm.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    falh_comm.geometry('1100x667')
    falh_comm.resizable(True, True)
    falh_comm.minsize(1100, 667)
    falh_comm['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(falh_comm, text='Falha de Comunicação', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(falh_comm, text='Data e Hora de Início:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(falh_comm, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)
    Button(falh_comm, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.4,
                                                                                                           rely=0.15,
                                                                                                           anchor="w")
    Label(falh_comm, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83, rely=0.15,
                                                                                                   anchor="w")
    # Campos de Data e Hora de Término
    Label(falh_comm, text='Data e Hora de Término:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_termino = Entry(falh_comm, width=30)
    entry_termino.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")
    Button(falh_comm, text="Selecionar", command=lambda: selecionar_data(entry_termino, "termino")).place(relx=0.40,
                                                                                                          rely=0.25,
                                                                                                          anchor="w")
    # ComboBox para Localidade
    Label(falh_comm, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    localidades = ["COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM",
                   "CGE JDT", "UFV PTM", "SE IGU", "SE MCP", "SE CLA", "SE SCA", "SE IPG", "SE RSD", "SE JDD"]
    combobox_localidade = ttk.Combobox(falh_comm, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # ComboBox para Estação
    Label(falh_comm, text='Estação:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    estacoes = ["LINK-1", "LINK-2", "LINK-3", "LINK-1 e 2", "LINK-1 e 3", "LINK-2 e 3", "LINK-1,2 e 3", "HOTLINE",
                "REDE COMUTADA"]
    combobox_estacao = ttk.Combobox(falh_comm, values=estacoes, state="readonly")
    combobox_estacao.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Entry para Complemento do Atendimento Operativo Local
    Label(falh_comm, text='Complemento Estação:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    entry_complemento = Entry(falh_comm, width=92)
    entry_complemento.place(relx=0.2, rely=0.55, width=200, height=25, anchor="w")

    # Text para Descrição da Anormalidade
    Label(falh_comm, text='Descrição da Anormalidade:', bg="#a4bad2").place(relx=0.05, rely=0.65, anchor="nw")
    text_descricao = Text(falh_comm, width=70, height=4)
    text_descricao.place(relx=0.2, rely=0.70, anchor="w")

    # Text para Observação
    Label(falh_comm, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.8, anchor="nw")
    text_observacao = Text(falh_comm, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.85, anchor="w")

    # ComboBox para Ativo
    Label(falh_comm, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(falh_comm, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    Button(falh_comm, text="Inserir", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: abrir_janela_atualizacao_data_termino('FalhaComunicacao',
                                                                 entry_id_registro.get().strip())).place(relx=0.85,
                                                                                                         rely=0.35,
                                                                                                         anchor="w")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        entry_termino.delete(0, END)
        combobox_localidade.set('')
        combobox_estacao.set('')
        entry_complemento.delete(0, END)
        text_descricao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_falh_comm():
        data_inicio = entry_data_hora.get().strip()
        data_termino = entry_termino.get().strip() if entry_termino.get().strip() else None
        localidade = combobox_localidade.get().strip()
        estacao = combobox_estacao.get().strip()
        complem_estacao = entry_complemento.get().strip()
        descricao = text_descricao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not estacao or not complem_estacao or not descricao or not ativo:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Data de término posterior a data de início
        if data_termino:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y - %H:%Mh")
                dt_termino = datetime.strptime(data_termino, "%d/%m/%Y - %H:%Mh")
                if dt_termino < dt_inicio:
                    messagebox.showerror("Erro",
                                         "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use o calendário")
                return

        salvar_dados(
            'FalhaComunicacao',
            {
                'data_inicio': data_inicio,
                'data_termino': data_termino,
                'localidade': localidade,
                'estacao': estacao,
                'complem_estacao': complem_estacao,
                'descricao': descricao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        falh_comm.destroy()

    # Botão "Salvar"
    Button(falh_comm, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_falh_comm).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(falh_comm, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(falh_comm, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=falh_comm.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('FalhaComunicacao', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(falh_comm, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(falh_comm, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(falh_comm, text="Cancelar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# =========================================================================================================
# Função para janela de Falha de Supervisão
def cmd_click9():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    falh_sdsc = Toplevel(root)
    falh_sdsc.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    falh_sdsc.geometry('1100x650')
    falh_sdsc.resizable(True, True)
    falh_sdsc.minsize(1100, 650)
    falh_sdsc['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(falh_sdsc, text='Falha de Supervisão', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(falh_sdsc, text='Data e Hora de Início:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(falh_sdsc, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(falh_sdsc, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.4,
                                                                                                           rely=0.15,
                                                                                                           anchor="w")
    Label(falh_sdsc, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83,
                                                                                                   rely=0.15, anchor="w")
    # Campos de Data e Hora de Término
    Label(falh_sdsc, text='Data e Hora de Término:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_termino = Entry(falh_sdsc, width=30)
    entry_termino.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")

    Button(falh_sdsc, text="Selecionar", command=lambda: selecionar_data(entry_termino, "termino")).place(relx=0.4,
                                                                                                          rely=0.25,
                                                                                                          anchor="w"),
    # ComboBox para Localidade
    Label(falh_sdsc, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w"),
    localidades = ["COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM",
                   "CGE JDT", "UFV PTM", "SE IGU", "SE MCP", "SE CLA", "SE SCA", "SE IPG", "SE RSD", "SE JDD"]
    combobox_localidade = ttk.Combobox(falh_sdsc, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # ComboBox para Atendimento Operativo Local
    Label(falh_sdsc, text='Atend. Operativo Local:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    estacoes = ["SIM", "NÃO"]
    combobox_local = ttk.Combobox(falh_sdsc, values=estacoes, state="readonly")
    combobox_local.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Entry para Complemento do Atendimento Operativo Local
    Label(falh_sdsc, text='Complemento Atend. Local:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    entry_complemento = Entry(falh_sdsc, width=92)
    entry_complemento.place(relx=0.2, rely=0.55, width=200, height=25, anchor="w")

    # Text para Descrição da Anormalidade
    Label(falh_sdsc, text='Descrição da Anormalidade:', bg="#a4bad2").place(relx=0.05, rely=0.65, anchor="nw")
    text_descricao = Text(falh_sdsc, width=70, height=4)
    text_descricao.place(relx=0.2, rely=0.70, anchor="w")

    # Text para Observação
    Label(falh_sdsc, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.8, anchor="nw")
    text_observacao = Text(falh_sdsc, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.85, anchor="w")

    # ComboBox para Ativo
    Label(falh_sdsc, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(falh_sdsc, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    Button(falh_sdsc, text="Inserir", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: abrir_janela_atualizacao_data_termino('FalhaSupervisao',
                                                                 entry_id_registro.get().strip())).place(relx=0.85,
                                                                                                         rely=0.35,
                                                                                                         anchor="w")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        entry_termino.delete(0, END)
        combobox_localidade.set('')
        combobox_local.set('')
        entry_complemento.delete(0, END)
        text_descricao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_falh_sdsc():
        data_inicio = entry_data_hora.get().strip()
        data_termino = entry_termino.get().strip() if entry_termino.get().strip() else None
        localidade = combobox_localidade.get().strip()
        atend_local = combobox_local.get().strip()
        complem_local = entry_complemento.get().strip()
        descricao = text_descricao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not atend_local or not complem_local or not descricao:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Data de término posterior a data de início
        if data_termino:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y - %H:%Mh")
                dt_termino = datetime.strptime(data_termino, "%d/%m/%Y - %H:%Mh")
                if dt_termino < dt_inicio:
                    messagebox.showerror("Erro",
                                         "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use o calendário")
                return

        salvar_dados(
            'FalhaSupervisao',
            {
                'data_inicio': data_inicio,
                'data_termino': data_termino,
                'localidade': localidade,
                'atend_local': atend_local,
                'complem_local': complem_local,
                'descricao': descricao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        falh_sdsc.destroy()

    # Botão "Salvar"
    Button(falh_sdsc, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_falh_sdsc).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(falh_sdsc, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(falh_sdsc, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=falh_sdsc.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('FalhaSupervisao', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(falh_sdsc, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(falh_sdsc, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(falh_sdsc, text="Cancelar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# =========================================================================================================
# Função para janela de Perturbações
def cmd_click10():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    pert_equip = Toplevel(root)
    pert_equip.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    pert_equip.geometry('1100x667')
    pert_equip.resizable(True, True)
    pert_equip.minsize(1100, 667)
    pert_equip['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(pert_equip, text='Perturbações', font=('Arial', 14, 'bold'), bg="#024593", fg="white", anchor="center").place(
        relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(pert_equip, text='Data e Hora de Início:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(pert_equip, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(pert_equip, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.40,
                                                                                                            rely=0.15,
                                                                                                            anchor="w")
    Label(pert_equip, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83,
                                                                                                    rely=0.15,
                                                                                                    anchor="w")
    # Campos de Data e Hora de Término
    Label(pert_equip, text='Data e Hora de Término:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_termino = Entry(pert_equip, width=30)
    entry_termino.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")
    Button(pert_equip, text="Selecionar", command=lambda: selecionar_data(entry_termino, "termino")).place(relx=0.40,
                                                                                                           rely=0.25,
                                                                                                           anchor="w")
    # ComboBox para Localidade
    Label(pert_equip, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    localidades = ["COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM",
                   "CGE JDT", "UFV PTM", "SE IGU", "SE MCP", "SE CLA", "SE SCA", "SE IPG", "SE RSD", "SE JDD"]
    combobox_localidade = ttk.Combobox(pert_equip, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # ComboBox para Instalação
    Label(pert_equip, text='Instalação:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    estacoes = ["Aerogerador", "BARRA - 138 KV", "BARRA-1 - 230 KV", "BARRA - 13,8 KV", "BARRA-2 - 230 KV",
                "BARRA - 34,5 KV", "BARRA - 6,9 KV", "BARRA - 69 KV", "BARRA - 88 KV", "Eletrocentro",
                "Linha de Transmissão", "RMT 34,5 KV", "Serviço Auxiliar CA", "Serviço Auxiliar CC",
                "Subestação", "Unidade Geradora", "Outros"]
    combobox_estacao = ttk.Combobox(pert_equip, values=estacoes, state="readonly")
    combobox_estacao.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Entry para Equipamentos
    Label(pert_equip, text='Equipamentos:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    entry_equipamento = Entry(pert_equip, width=92)
    entry_equipamento.place(relx=0.2, rely=0.55, width=200, height=25, anchor="w")

    # Text para Causa
    Label(pert_equip, text='Causa:', bg="#a4bad2").place(relx=0.05, rely=0.65, anchor="nw")
    text_descricao = Text(pert_equip, width=70, height=4)
    text_descricao.place(relx=0.2, rely=0.70, anchor="w")

    # Text para Observação
    Label(pert_equip, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.8, anchor="nw")
    text_observacao = Text(pert_equip, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.85, anchor="w")

    # ComboBox para Ativo
    Label(pert_equip, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(pert_equip, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    Button(pert_equip, text="Inserir", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: abrir_janela_atualizacao_data_termino('Perturbacao',
                                                                 entry_id_registro.get().strip())).place(relx=0.85,
                                                                                                         rely=0.35,
                                                                                                         anchor="w")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        entry_termino.delete(0, END)
        combobox_localidade.set('')
        combobox_estacao.set('')
        entry_equipamento.delete(0, END)
        text_descricao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_pert_equip():
        data_inicio = entry_data_hora.get().strip()
        data_termino = entry_termino.get().strip() if entry_termino.get().strip() else None
        localidade = combobox_localidade.get().strip()
        estacao = combobox_estacao.get().strip()
        equipamento = entry_equipamento.get().strip()
        descricao = text_descricao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not estacao or not equipamento or not descricao:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Data de término posterior a data de início
        if data_termino:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y - %H:%Mh")
                dt_termino = datetime.strptime(data_termino, "%d/%m/%Y - %H:%Mh")
                if dt_termino < dt_inicio:
                    messagebox.showerror("Erro",
                                         "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use o calendário")
                return

        salvar_dados(
            'Perturbacao',
            {
                'data_inicio': data_inicio,
                'data_termino': data_termino,
                'localidade': localidade,
                'instalacao': estacao,
                'equipamento': equipamento,
                'causa': descricao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        pert_equip.destroy()

    # Botão "Salvar"
    Button(pert_equip, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_pert_equip).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(pert_equip, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(pert_equip, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=pert_equip.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('Perturbacao', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(pert_equip, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(pert_equip, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(pert_equip, text="Cancelar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# =========================================================================================================
# Função para janela de Falha fonte externa serviço auxiliar CA
def cmd_click11():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    falh_saca = Toplevel(root)
    falh_saca.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    falh_saca.geometry('1100x667')
    falh_saca.resizable(True, True)
    falh_saca.minsize(1100, 667)
    falh_saca['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(falh_saca, text='Falha na fonte externa do Serviço Auxiliar CA', font=('Arial', 14, 'bold'), bg="#024593",
          fg="white", anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(falh_saca, text='Data e Hora de Início:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(falh_saca, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(falh_saca, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.40,
                                                                                                           rely=0.15,
                                                                                                           anchor="w")
    Label(falh_saca, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83,
                                                                                                   rely=0.15,
                                                                                                   anchor="w")
    # Campos de Data e Hora de Término
    Label(falh_saca, text='Data e Hora de Término:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_termino = Entry(falh_saca, width=30)
    entry_termino.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")
    Button(falh_saca, text="Selecionar", command=lambda: selecionar_data(entry_termino, "termino")).place(relx=0.40,
                                                                                                          rely=0.25,
                                                                                                          anchor="w")
    # ComboBox para Localidade
    Label(falh_saca, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    localidades = ["COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM",
                   "CGE JDT", "UFV PTM", "SE IGU", "SE MCP", "SE CLA", "SE SCA", "SE IPG", "SE RSD", "SE JDD"]
    combobox_localidade = ttk.Combobox(falh_saca, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # ComboBox para Comunicação à Concessionaria
    Label(falh_saca, text='Comunicado Concessionária:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    estacoes = ["SIM", "NÃO"]
    combobox_estacao = ttk.Combobox(falh_saca, values=estacoes, state="readonly")
    combobox_estacao.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Entry para Complemento do comunicado
    Label(falh_saca, text='Número de Protocolo:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    entry_protocolo = Entry(falh_saca, width=92)
    entry_protocolo.place(relx=0.2, rely=0.55, width=200, height=25, anchor="w")

    # Text para Descrição da Anormalidade
    Label(falh_saca, text='Informações Adicionais:', bg="#a4bad2").place(relx=0.05, rely=0.65, anchor="nw")
    text_informacao = Text(falh_saca, width=70, height=4)
    text_informacao.place(relx=0.2, rely=0.70, anchor="w")

    # Text para Observação
    Label(falh_saca, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.8, anchor="nw")
    text_observacao = Text(falh_saca, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.85, anchor="w")

    # ComboBox para Ativo
    Label(falh_saca, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(falh_saca, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    Button(falh_saca, text="Inserir", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: abrir_janela_atualizacao_data_termino('ServicoAuxiliar',
                                                                 entry_id_registro.get().strip())).place(relx=0.85,
                                                                                                         rely=0.35,
                                                                                                         anchor="w")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        entry_termino.delete(0, END)
        combobox_localidade.set('')
        combobox_estacao.set('')
        entry_protocolo.delete(0, END)
        text_informacao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_falh_saca():
        data_inicio = entry_data_hora.get().strip()
        data_termino = entry_termino.get().strip() if entry_termino.get().strip() else None
        localidade = combobox_localidade.get().strip()
        concessionaria = combobox_estacao.get().strip()
        protocol = entry_protocolo.get().strip()
        informacao = text_informacao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not concessionaria or not protocol or not informacao:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Data de término posterior a data de início
        if data_termino:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y - %H:%Mh")
                dt_termino = datetime.strptime(data_termino, "%d/%m/%Y - %H:%Mh")
                if dt_termino < dt_inicio:
                    messagebox.showerror("Erro",
                                         "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use o calendário")
                return

        salvar_dados(
            'ServicoAuxiliar',
            {
                'data_inicio': data_inicio,
                'data_termino': data_termino,
                'localidade': localidade,
                'concessionaria': concessionaria,
                'protocol': protocol,
                'informacao': informacao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        falh_saca.destroy()

    # Botão "Salvar"
    Button(falh_saca, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_falh_saca).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(falh_saca, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(falh_saca, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=falh_saca.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('ServicoAuxiliar', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(falh_saca, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(falh_saca, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(falh_saca, text="Cancelar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# =========================================================================================================
# Função para janela de Informações do ONS
def cmd_click12():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    info_ons = Toplevel(root)
    info_ons.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    info_ons.geometry('1100x667')
    info_ons.resizable(True, True)
    info_ons.minsize(1100, 667)
    info_ons['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(info_ons, text='Informações do ONS', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(info_ons, text='Data e Hora:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(info_ons, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(info_ons, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.40,
                                                                                                          rely=0.15,
                                                                                                          anchor="w")
    Label(info_ons, text='Cancelar Registro', bg="#a4bad2").place(relx=0.85, rely=0.15, anchor="w")

    # ComboBox para Localidade
    Label(info_ons, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    localidades = ["COG-P", "COG-R", "UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE", "CGE PTM",
                   "CGE JDT", "UFV PTM", "SE IGU", "SE MCP", "SE CLA", "SE SCA", "SE IPG", "SE RSD", "SE JDD"]
    combobox_localidade = ttk.Combobox(info_ons, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")

    # ComboBox para seleção do centro de operação do ONS
    Label(info_ons, text='Centro de Operação:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    estacoes = ["COS-ONS", "COSR-S", "COSR-SE", "COSR-NE", "COSR-NCO"]
    combobox_estacao = ttk.Combobox(info_ons, values=estacoes, state="readonly")
    combobox_estacao.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # Entry para Complemento da Estação
    Label(info_ons, text='Operador do ONS:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    entry_operador = Entry(info_ons, width=92)
    entry_operador.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Text para Descrição da Anormalidade
    Label(info_ons, text='Descrição das Informações:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="nw")
    text_descricao = Text(info_ons, width=70, height=4)
    text_descricao.place(relx=0.2, rely=0.60, anchor="w")

    # Text para Observação
    Label(info_ons, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.75, anchor="nw")
    text_observacao = Text(info_ons, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.80, anchor="w")

    # ComboBox para Ativo
    Label(info_ons, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(info_ons, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        combobox_localidade.set('')
        combobox_estacao.set('')
        entry_operador.delete(0, END)
        text_descricao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_info_ons():
        data_hora = entry_data_hora.get().strip()
        localidade = combobox_localidade.get().strip()
        centro_ons = combobox_estacao.get().strip()
        operador_ons = entry_operador.get().strip()
        descricao = text_descricao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_hora or not localidade or not centro_ons or not descricao or not ativo:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        salvar_dados(
            'InformacaoOns',
            {
                'data_hora': data_hora,
                'localidade': localidade,
                'centro_op': centro_ons,
                'operador_ons': operador_ons,
                'descricao': descricao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        info_ons.destroy()

    # Botão "Salvar"
    Button(info_ons, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_info_ons).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(info_ons, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(info_ons, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=info_ons.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('InformacaoOns', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(info_ons, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(info_ons, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(info_ons, text="Confirmar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# =========================================================================================================
# Função para janela de Transbordo de Planta Aquaticas
def cmd_click13():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    trans_paqu = Toplevel(root)
    trans_paqu.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    trans_paqu.geometry('1100x667')
    trans_paqu.resizable(True, True)
    trans_paqu.minsize(1100, 667)
    trans_paqu['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(trans_paqu, text='Transbordo Plantas Aquáticas', font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(trans_paqu, text='Data e Hora de Início:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(trans_paqu, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")
    # ---------------------------------------------------------
    # PREENCHEMINTO AUTOMÁTICO COM DATA/HORA ATUAL
    # ---------------------------------------------------------
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(trans_paqu, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.40,
                                                                                                            rely=0.15,
                                                                                                            anchor="w")
    Label(trans_paqu, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83,
                                                                                                    rely=0.15,
                                                                                                    anchor="w")
    # Campos de Data e Hora de Término
    Label(trans_paqu, text='Data e Hora de Término:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_termino = Entry(trans_paqu, width=30)
    entry_termino.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")
    Button(trans_paqu, text="Selecionar", command=lambda: selecionar_data(entry_termino, "termino")).place(relx=0.40,
                                                                                                           rely=0.25,
                                                                                                           anchor="w")
    # ComboBox para Localidade
    Label(trans_paqu, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    localidades = ["UHE MGP", "UHE FGO", "UHE SJO", "PCH LAV", "PCH QUE", "PCH VIE"]
    combobox_localidade = ttk.Combobox(trans_paqu, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # ComboBox para Estação
    Label(trans_paqu, text='Informado ONS:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    estacoes = ["SIM", "NÃO"]
    combobox_estacao = ttk.Combobox(trans_paqu, values=estacoes, state="readonly")
    combobox_estacao.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Entry para identificação Opereador do ONS
    Label(trans_paqu, text='Operador do ONS:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    entry_operador = Entry(trans_paqu, width=92)
    entry_operador.place(relx=0.2, rely=0.55, width=200, height=25, anchor="w")

    # Text para Informações Adicionais
    Label(trans_paqu, text='Informações Adicionais:', bg="#a4bad2").place(relx=0.05, rely=0.65, anchor="nw")
    text_informacao = Text(trans_paqu, width=80, height=4)
    text_informacao.place(relx=0.2, rely=0.70, anchor="w")

    # Text para Observação
    Label(trans_paqu, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.8, anchor="nw")
    text_observacao = Text(trans_paqu, width=80, height=3)
    text_observacao.place(relx=0.2, rely=0.85, anchor="w")

    # ComboBox para Ativo
    Label(trans_paqu, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(trans_paqu, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    Button(trans_paqu, text="Inserir", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: abrir_janela_atualizacao_data_termino('Transbordo',
                                                                 entry_id_registro.get().strip())).place(relx=0.85,
                                                                                                         rely=0.35,
                                                                                                         anchor="w")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        entry_termino.delete(0, END)
        combobox_localidade.set('')
        combobox_estacao.set('')
        entry_operador.delete(0, END)
        text_informacao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_trans_paqu():
        data_inicio = entry_data_hora.get().strip()
        data_termino = entry_termino.get().strip() if entry_termino.get().strip() else None
        localidade = combobox_localidade.get().strip()
        informacao_ons = combobox_estacao.get().strip()
        operador_ons = entry_operador.get().strip()
        informacao = text_informacao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not informacao_ons or not informacao:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Data de término posterior a data de início
        if data_termino:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y - %H:%Mh")
                dt_termino = datetime.strptime(data_termino, "%d/%m/%Y - %H:%Mh")
                if dt_termino < dt_inicio:
                    messagebox.showerror("Erro",
                                         "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use o calendário")
                return

        salvar_dados(
            'Transbordo',
            {
                'data_inicio': data_inicio,
                'data_termino': data_termino,
                'localidade': localidade,
                'informacao_ons': informacao_ons,
                'operador_ons': operador_ons,
                'informacao': informacao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        trans_paqu.destroy()

    # Botão "Salvar"
    Button(trans_paqu, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_trans_paqu).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(trans_paqu, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(trans_paqu, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=trans_paqu.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('Transbordo', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(trans_paqu, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(trans_paqu, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(trans_paqu, text="Cancelar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# =========================================================================================================
# Função para janela de Habilitação e Desabilitação do SEP/ECE
def cmd_click14():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    habil_ece = Toplevel(root)
    habil_ece.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    habil_ece.geometry('1100x667')
    habil_ece.resizable(True, True)
    habil_ece.minsize(1100, 667)
    habil_ece['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(habil_ece, text='Habilitação/Desabilitação do SEP/ECE', font=('Arial', 14, 'bold'), bg="#024593",
          fg="white", anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(habil_ece, text='Data e Hora:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(habil_ece, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(habil_ece, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.40,
                                                                                                           rely=0.15,
                                                                                                           anchor="w")
    Label(habil_ece, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83,
                                                                                                   rely=0.15,
                                                                                                   anchor="w")

    # ComboBox para Localidade
    Label(habil_ece, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    localidades = ["UHE MGP", "UHE FGO", "UHE SJO", "CGE PTM", "CGE JDT", "UFV PTM"]
    combobox_localidade = ttk.Combobox(habil_ece, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")

    # ComboBox para Estação
    Label(habil_ece, text='SEP/ECE:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    estacoes = ["HABILITADO", "DESABILITADO"]
    combobox_estacao = ttk.Combobox(habil_ece, values=estacoes, state="readonly")
    combobox_estacao.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # Entry para Complemento da SEP-ECE
    Label(habil_ece, text='Complemento SEP-ECE:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    entry_complemento = Entry(habil_ece, width=92)
    entry_complemento.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Text para Informações Adicionais
    Label(habil_ece, text='Informações Adicionais:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="nw")
    text_informacao = Text(habil_ece, width=70, height=4)
    text_informacao.place(relx=0.2, rely=0.60, anchor="w")

    # Text para Observação
    Label(habil_ece, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.75, anchor="nw")
    text_observacao = Text(habil_ece, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.80, anchor="w")

    # ComboBox para Ativo
    Label(habil_ece, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(habil_ece, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        combobox_localidade.set('')
        combobox_estacao.set('')
        entry_complemento.delete(0, END)
        text_informacao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_habil_ece():
        data_hora = entry_data_hora.get().strip()
        localidade = combobox_localidade.get().strip()
        sep_ece = combobox_estacao.get().strip()
        complem_ece = entry_complemento.get().strip()
        informacao_ad = text_informacao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_hora or not localidade or not sep_ece or not complem_ece or not informacao_ad or not ativo:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        salvar_dados(
            'HabilitacaoEce',
            {
                'data_hora': data_hora,
                'localidade': localidade,
                'sep_ece': sep_ece,
                'complem_ece': complem_ece,
                'informacao_ad': informacao_ad,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        habil_ece.destroy()

    # Botão "Salvar"
    Button(habil_ece, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_habil_ece).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(habil_ece, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(habil_ece, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=habil_ece.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('HabilitacaoEce', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(habil_ece, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(habil_ece, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(habil_ece, text="Confirmar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# =========================================================================================================
# Função para janela de Transbordo de Planta Aquaticas
def cmd_click15():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    saca_agente = Toplevel(root)
    saca_agente.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    saca_agente.geometry('1100x667')
    saca_agente.resizable(True, True)
    saca_agente.minsize(1100, 667)
    saca_agente['bg'] = "#a4bad2"

    # Cabeçalho do página
    Label(saca_agente, text='Alimentação do Serviço Auxiliar CA de uma Empresa por outra Empresa',
          font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    # Campos de Data e Hora de Início
    Label(saca_agente, text='Data e Hora de Início:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_data_hora = Entry(saca_agente, width=30)
    entry_data_hora.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")
    # ---------------------------------------------------------
    # PREENCHEMINTO AUTOMÁTICO COM DATA/HORA ATUAL
    # ---------------------------------------------------------
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(saca_agente, text="Selecionar", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(relx=0.40,
                                                                                                             rely=0.15,
                                                                                                             anchor="w")
    Label(saca_agente, text='Cancelar Registro ou \n Inserir Data-Hora Término', bg="#a4bad2").place(relx=0.83,
                                                                                                     rely=0.15,
                                                                                                     anchor="w")
    # Campos de Data e Hora de Término
    Label(saca_agente, text='Data e Hora de Término:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_termino = Entry(saca_agente, width=30)
    entry_termino.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")
    Button(saca_agente, text="Selecionar", command=lambda: selecionar_data(entry_termino, "termino")).place(relx=0.40,
                                                                                                            rely=0.25,
                                                                                                            anchor="w")
    # ComboBox para Localidade
    Label(saca_agente, text='Localidade:', bg="#a4bad2").place(relx=0.05, rely=0.35, anchor="w")
    localidades = ["UHE Ferreira Gomes", "SE Macapá"]
    combobox_localidade = ttk.Combobox(saca_agente, values=localidades, state="readonly")
    combobox_localidade.place(relx=0.2, rely=0.35, width=200, height=25, anchor="w")

    # ComboBox para Estação
    Label(saca_agente, text='Alimentação da:', bg="#a4bad2").place(relx=0.05, rely=0.45, anchor="w")
    alimentacao = ["Casa Relés da EDP", "Casa Relés da FGE"]
    combobox_alimentacao_da = ttk.Combobox(saca_agente, values=alimentacao, state="readonly")
    combobox_alimentacao_da.place(relx=0.2, rely=0.45, width=200, height=25, anchor="w")

    # Entry para identificação Opereador do ONS
    Label(saca_agente, text='Solicitado por:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    entry_solicitado_por = Entry(saca_agente, width=92)
    entry_solicitado_por.place(relx=0.2, rely=0.55, width=200, height=25, anchor="w")

    # Text para Informações Adicionais
    Label(saca_agente, text='Informações Adicionais:', bg="#a4bad2").place(relx=0.05, rely=0.65, anchor="nw")
    text_informacao = Text(saca_agente, width=80, height=4)
    text_informacao.place(relx=0.2, rely=0.70, anchor="w")

    # Text para Observação
    Label(saca_agente, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.8, anchor="nw")
    text_observacao = Text(saca_agente, width=80, height=3)
    text_observacao.place(relx=0.2, rely=0.85, anchor="w")

    # ComboBox para Ativo
    Label(saca_agente, text='Registro:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(saca_agente, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    Button(saca_agente, text="Inserir", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=lambda: abrir_janela_atualizacao_data_termino('SacaAgente',
                                                                 entry_id_registro.get().strip())).place(relx=0.85,
                                                                                                         rely=0.35,
                                                                                                         anchor="w")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        entry_data_hora.delete(0, END)
        entry_termino.delete(0, END)
        combobox_localidade.set('')
        combobox_alimentacao_da.set('')
        entry_solicitado_por.delete(0, END)
        text_informacao.delete('1.0', END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_saca_agente():
        data_inicio = entry_data_hora.get().strip()
        data_termino = entry_termino.get().strip() if entry_termino.get().strip() else None
        localidade = combobox_localidade.get().strip()
        alimentacao_da = combobox_alimentacao_da.get().strip()
        solicitado_por = entry_solicitado_por.get().strip()
        informacao = text_informacao.get("1.0", END).strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not data_inicio or not localidade or not alimentacao_da or not solicitado_por:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Data de término posterior a data de início
        if data_termino:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y - %H:%Mh")
                dt_termino = datetime.strptime(data_termino, "%d/%m/%Y - %H:%Mh")
                if dt_termino < dt_inicio:
                    messagebox.showerror("Erro",
                                         "A Data e Hora de Término não pode ser anterior à Data e Hora de Início.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use o calendário")
                return

        salvar_dados(
            'SacaAgente',
            {
                'data_inicio': data_inicio,
                'data_termino': data_termino,
                'localidade': localidade,
                'alimentacao_da': alimentacao_da,
                'solicitado_por': solicitado_por,
                'informacao': informacao,
                'observacao': observacao,
                'ativo': ativo,
                'usuario': current_user
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        saca_agente.destroy()

    # Botão "Salvar"
    Button(saca_agente, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_saca_agente).place(relx=0.76, rely=0.94, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(saca_agente, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.94, anchor="e")

    # --- Botão "Sair" ---
    Button(saca_agente, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=saca_agente.destroy).place(relx=0.98, rely=0.94, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('SacaAgente', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(saca_agente, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(saca_agente, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(saca_agente, text="Cancelar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# ---------------------------------------------------
# FUNÇÕES PARA TAG-ÁVATO
# ___________________________________________________
def cmd_click16():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    tag_avato = Toplevel(root)
    tag_avato.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    tag_avato.geometry('1100x667')
    tag_avato.resizable(True, True)
    tag_avato.minsize(1100, 667)
    tag_avato['bg'] = "#a4bad2"
    # Cabeçalho do página
    Label(tag_avato, text='Cadastro ou Atualização da Relação de TAGs da ÁVATO', font=('Arial', 14, 'bold'),
          bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    Label(tag_avato, text='Cancelar Registro', bg="#a4bad2").place(relx=0.85, rely=0.15, anchor="w")

    Label(tag_avato, text='Instalação:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    entry_instalacao = Entry(tag_avato)
    entry_instalacao.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    Label(tag_avato, text='Instalação:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    instalacoes = ["UHE Ferreira Gomes", "SE Macapá", "UHE São José", "UHE Muller Godoy Pereira", "COG-P - Cruzeiro",
                   "COG-R - Lavrinhas", "PCH Queluz", "PCH Verde 8", "CGE Pitombeira", "CGE Jandaíra-III",
                   "Florianópolis-SAL (COSR-S)", "Florianópolis-SAR (COSR-S)", "Recife-SAL (COSR-NE)",
                   "Recife-SAR (COSR-NE)", "Brasília-SAL (COSR-NCO)", "Rio de Janeiro-SAL (COSR-SE)",
                   "Rio de Janeiro-SAR (COSR-SE)"]
    combobox_instalacoes = ttk.Combobox(tag_avato, values=instalacoes, state="readonly")
    combobox_instalacoes.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    Label(tag_avato, text='Etiqueta:', bg="#a4bad2").place(relx=0.05, rely=0.23, anchor="w")
    entry_ons = Entry(tag_avato)
    entry_ons.place(relx=0.2, rely=0.23, width=200, height=25, anchor="w")

    Label(tag_avato, text='Nome no Zabbix:', bg="#a4bad2").place(relx=0.05, rely=0.31, anchor="w")
    entry_nome_zabbix = Entry(tag_avato)
    entry_nome_zabbix.place(relx=0.2, rely=0.31, width=200, height=25, anchor="w")

    Label(tag_avato, text='Nome da Proposta:', bg="#a4bad2").place(relx=0.05, rely=0.39, anchor="w")
    entry_nome_proposta = Entry(tag_avato)
    entry_nome_proposta.place(relx=0.2, rely=0.39, width=200, height=25, anchor="w")

    Label(tag_avato, text='Link Zabbix-IP:', bg="#a4bad2").place(relx=0.05, rely=0.47, anchor="w")
    entry_link_zabbix = Entry(tag_avato)
    entry_link_zabbix.place(relx=0.2, rely=0.47, width=200, height=25, anchor="w")

    Label(tag_avato, text='Responsável:', bg="#a4bad2").place(relx=0.05, rely=0.55, anchor="w")
    entry_responsavel = Entry(tag_avato)
    entry_responsavel.place(relx=0.2, rely=0.55, width=200, height=25, anchor="w")

    Label(tag_avato, text='Telefone do Responsável:', bg="#a4bad2").place(relx=0.4, rely=0.55, anchor="w")
    entry_telefone_responsavel = Entry(tag_avato)
    entry_telefone_responsavel.place(relx=0.53, rely=0.55, width=200, height=25, anchor="w")

    Label(tag_avato, text='Disponível 24h:', bg="#a4bad2").place(relx=0.05, rely=0.63, anchor="w")
    disponivel = ["SIM", "NÃO"]
    combobox_disponivel = ttk.Combobox(tag_avato, values=disponivel, state="readonly")
    combobox_disponivel.place(relx=0.2, rely=0.63, width=200, height=25, anchor="w")

    Label(tag_avato, text='Condição de Acesso:', bg="#a4bad2").place(relx=0.05, rely=0.71, anchor="w")
    condicao_acesso = ["Solicitar Autorização de Acesso", "Acesso já Liberado"]
    combobox_condicao_acesso = ttk.Combobox(tag_avato, values=condicao_acesso, state="readonly")
    combobox_condicao_acesso.place(relx=0.2, rely=0.71, width=200, height=25, anchor="w")

    Label(tag_avato, text='Endereço:', bg="#a4bad2").place(relx=0.05, rely=0.79, anchor="w")
    entry_endereco = Entry(tag_avato)
    entry_endereco.place(relx=0.2, rely=0.79, width=560, height=25, anchor="w")

    Label(tag_avato, text='Observação:', bg="#a4bad2").place(relx=0.05, rely=0.87, anchor="nw")
    text_observacao = Text(tag_avato, width=70, height=3)
    text_observacao.place(relx=0.2, rely=0.87, anchor="w")

    # ComboBox para Ativo
    Label(tag_avato, text='Dados Atuais:', bg="#a4bad2").place(relx=0.05, rely=0.95, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(tag_avato, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.95, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")  # Define "VÁLIDO" como padrão

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        combobox_instalacoes.set('')
        entry_ons.delete(0, END)
        entry_nome_zabbix.delete(0, END)
        entry_nome_proposta.delete(0, END)
        entry_link_zabbix.delete(0, END)
        entry_responsavel.delete(0, END)
        entry_telefone_responsavel.delete(0, END)
        combobox_disponivel.set('')
        combobox_condicao_acesso.set('')
        entry_endereco.delete(0, END)
        text_observacao.delete('1.0', END)
        combobox_ativo.set('')

    def salvar_tag_avato():
        # Obter valores digitados
        instalacoes = combobox_instalacoes.get().strip()
        ons = entry_ons.get().strip()
        nome_zabbix = entry_nome_zabbix.get().strip()
        nome_proposta = entry_nome_proposta.get().strip()
        link_zabbix = entry_link_zabbix.get().strip()
        responsavel = entry_responsavel.get().strip()
        telefone_responsavel = entry_telefone_responsavel.get().strip()
        disponivel = combobox_disponivel.get().strip()
        condicao_acesso = combobox_condicao_acesso.get().strip()
        endereco = entry_endereco.get().strip()
        observacao = text_observacao.get("1.0", END).strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not instalacoes or not ons or not nome_zabbix or not ativo:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Se estiver tudo preenchido, salvar
        salvar_dados(
            'TagAvato',
            {
                'instalacao': instalacoes,
                'ons': ons,
                'nome_zabbix': nome_zabbix,
                'nome_proposta': nome_proposta,
                'link_zabbix': link_zabbix,
                'responsavel': responsavel,
                'telefone_responsavel': telefone_responsavel,
                'disponivel': disponivel,
                'condicao_acesso': condicao_acesso,
                'endereco': endereco,
                'observacao': observacao,
                'ativo': ativo
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        tag_avato.destroy()

    # Botão "Salvar"
    Button(tag_avato, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_tag_avato).place(relx=0.76, rely=0.96, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(tag_avato, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.96, anchor="e")

    # --- Botão "Sair" ---
    Button(tag_avato, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=tag_avato.destroy).place(relx=0.98, rely=0.96, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('TagAvato', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(tag_avato, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(tag_avato, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(tag_avato, text="Confirmar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")


# ---------------------------------------------------
# FUNÇÃO PARA PROTOCOLO
# ___________________________________________________
def cmd_click17():
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    protocolo = Toplevel(root)
    protocolo.title('COG-ALUPAR - INFORMAÇÕES DE TROCA DE TURNO')
    protocolo.geometry('1100x667')
    protocolo.resizable(True, True)
    protocolo.minsize(1100, 667)
    protocolo['bg'] = "#a4bad2"
    # Cabeçalho do página
    Label(protocolo, text='Cadastro ou Atualização dos Dados para abertura de Protocolos nas Concessionárias',
          font=('Arial', 14, 'bold'), bg="#024593", fg="white",
          anchor="center").place(relx=0.00, rely=0.00, width=1100, height=60)

    Label(protocolo, text='Cancelar Registro', bg="#a4bad2").place(relx=0.85, rely=0.15, anchor="w")

    Label(protocolo, text='Instalação:', bg="#a4bad2").place(relx=0.05, rely=0.15, anchor="w")
    instalacao = ["UHE Mülher de Godoy Pereira", "SE Itaguaçu", "CGE Pitombeira", "SE Russas-II", "CGE Jandaíra-III",
                  "UHE Ferreira Gomes", "SE Macapá", "COG-P - Cruzeiro"]
    combobox_instalacao = ttk.Combobox(protocolo, values=instalacao, state="readonly")
    combobox_instalacao.place(relx=0.2, rely=0.15, width=200, height=25, anchor="w")

    Label(protocolo, text='Concessionária:', bg="#a4bad2").place(relx=0.05, rely=0.20, anchor="w")
    entry_concessionaria = Entry(protocolo)
    entry_concessionaria.place(relx=0.2, rely=0.20, width=200, height=25, anchor="w")

    Label(protocolo, text='Atendimento Grandes Clientes:', bg="#a4bad2").place(relx=0.05, rely=0.25, anchor="w")
    entry_atendimento_grandes_clientes = Entry(protocolo)
    entry_atendimento_grandes_clientes.place(relx=0.2, rely=0.25, width=200, height=25, anchor="w")

    Label(protocolo, text='WhatsApp:', bg="#a4bad2").place(relx=0.42, rely=0.25, anchor="w")
    entry_whatsapp = Entry(protocolo)
    entry_whatsapp.place(relx=0.52, rely=0.25, width=200, height=25, anchor="w")

    Label(protocolo, text='Site:', bg="#a4bad2").place(relx=0.42, rely=0.20, anchor="w")
    entry_site = Entry(protocolo)
    entry_site.place(relx=0.52, rely=0.20, width=200, height=25, anchor="w")

    Label(protocolo, text='Titular da Conta:', bg="#a4bad2").place(relx=0.05, rely=0.33, anchor="w")
    entry_titular_da_conta = Entry(protocolo)
    entry_titular_da_conta.place(relx=0.2, rely=0.33, width=200, height=25, anchor="w")

    Label(protocolo, text='CNPJ:', bg="#a4bad2").place(relx=0.42, rely=0.33, anchor="w")
    entry_cnpj = Entry(protocolo)
    entry_cnpj.place(relx=0.52, rely=0.33, width=200, height=25, anchor="w")

    Label(protocolo, text='Endereço:', bg="#a4bad2").place(relx=0.05, rely=0.38, anchor="w")
    entry_endereco = Entry(protocolo)
    entry_endereco.place(relx=0.20, rely=0.38, width=200, height=25, anchor="w")

    Label(protocolo, text='Cep, Cidade e UF:', bg="#a4bad2").place(relx=0.42, rely=0.38, anchor="w")
    entry_cep_cidade_uf = Entry(protocolo)
    entry_cep_cidade_uf.place(relx=0.52, rely=0.38, width=200, height=25, anchor="w")

    Label(protocolo, text='Unidade Consumidora:', bg="#a4bad2").place(relx=0.05, rely=0.46, anchor="w")
    entry_unidade_consumidora = Entry(protocolo)
    entry_unidade_consumidora.place(relx=0.2, rely=0.46, width=200, height=25, anchor="w")

    Label(protocolo, text='Parceiro do Negócio:', bg="#a4bad2").place(relx=0.05, rely=0.51, anchor="w")
    entry_parceiro_negocio = Entry(protocolo)
    entry_parceiro_negocio.place(relx=0.2, rely=0.51, width=200, height=25, anchor="w")

    Label(protocolo, text='Número do Cliente:', bg="#a4bad2").place(relx=0.05, rely=0.56, anchor="w")
    entry_numero_cliente = Entry(protocolo)
    entry_numero_cliente.place(relx=0.2, rely=0.56, width=200, height=25, anchor="w")

    Label(protocolo, text='Número da Instalação:', bg="#a4bad2").place(relx=0.05, rely=0.61, anchor="w")
    entry_numero_instalacao = Entry(protocolo)
    entry_numero_instalacao.place(relx=0.2, rely=0.61, width=200, height=25, anchor="w")

    Label(protocolo, text='Código do Cliente:', bg="#a4bad2").place(relx=0.05, rely=0.66, anchor="w")
    entry_codigo_cliente = Entry(protocolo)
    entry_codigo_cliente.place(relx=0.2, rely=0.66, width=200, height=25, anchor="w")

    Label(protocolo, text='Código da Instalação:', bg="#a4bad2").place(relx=0.05, rely=0.71, anchor="w")
    entry_codigo_instalacao = Entry(protocolo)
    entry_codigo_instalacao.place(relx=0.2, rely=0.71, width=200, height=25, anchor="w")

    Label(protocolo, text='Código Único:', bg="#a4bad2").place(relx=0.05, rely=0.76, anchor="w")
    entry_codigo_unico = Entry(protocolo)
    entry_codigo_unico.place(relx=0.2, rely=0.76, width=200, height=25, anchor="w")

    Label(protocolo, text='Senha:', bg="#a4bad2").place(relx=0.05, rely=0.81, anchor="w")
    entry_senha = Entry(protocolo)
    entry_senha.place(relx=0.2, rely=0.81, width=200, height=25, anchor="w")

    # ComboBox para Ativo
    Label(protocolo, text='Dados Atuais:', bg="#a4bad2").place(relx=0.05, rely=0.90, anchor="w")
    ativos = ["VÁLIDO", "CANCELADO"]
    combobox_ativo = ttk.Combobox(protocolo, values=ativos, state="readonly")
    combobox_ativo.place(relx=0.2, rely=0.90, width=200, height=25, anchor="w")
    combobox_ativo.set("VÁLIDO")

    # --- Limpar campos para novo lançamento
    def novo_lancamento():
        combobox_instalacao.set('')
        entry_concessionaria.delete(0, END)
        entry_atendimento_grandes_clientes.delete(0, END)
        entry_whatsapp.delete(0, END)
        entry_site.delete(0, END)
        entry_titular_da_conta.delete(0, END)
        entry_cnpj.delete(0, END)
        entry_endereco.delete(0, END)
        entry_cep_cidade_uf.delete(0, END)
        entry_unidade_consumidora.delete(0, END)
        entry_parceiro_negocio.delete(0, END)
        entry_numero_cliente.delete(0, END)
        entry_numero_instalacao.delete(0, END)
        entry_codigo_cliente.delete(0, END)
        entry_codigo_instalacao.delete(0, END)
        entry_codigo_unico.delete(0, END)
        entry_senha.delete(0, END)
        combobox_ativo.set('')

    def salvar_protocolo():
        # Obter valores digitados
        instalacao = combobox_instalacao.get().strip()
        concessionaria = entry_concessionaria.get().strip()
        atendimento_grandes_clientes = entry_atendimento_grandes_clientes.get().strip()
        whatsapp = entry_whatsapp.get().strip()
        site = entry_site.get().strip()
        titular_da_conta = entry_titular_da_conta.get().strip()
        cnpj = entry_cnpj.get().strip()
        endereco = entry_endereco.get().strip()
        cep_cidade_uf = entry_cep_cidade_uf.get().strip()
        unidade_consumidora = entry_unidade_consumidora.get().strip()
        parceiro_negocio = entry_parceiro_negocio.get().strip()
        numero_cliente = entry_numero_cliente.get().strip()
        numero_instalacao = entry_numero_instalacao.get().strip()
        codigo_cliente = entry_codigo_cliente.get().strip()
        codigo_instalacao = entry_codigo_instalacao.get().strip()
        codigo_unico = entry_codigo_unico.get().strip()
        senha = entry_senha.get().strip()
        ativo = combobox_ativo.get().strip()

        # Verificar se algum dos campos está vazio
        if not instalacao or not concessionaria or not titular_da_conta or not ativo:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos antes de salvar.")
            return

        # Se estiver tudo preenchido, salvar
        salvar_dados(
            'Protocolo',
            {
                'instalacao': instalacao,
                'concessionaria': concessionaria,
                'atendimento_grandes_clientes': atendimento_grandes_clientes,
                'whatsapp': whatsapp,
                'site': site,
                'titular_da_conta': titular_da_conta,
                'cnpj': cnpj,
                'endereco': endereco,
                'cep_cidade_uf': cep_cidade_uf,
                'unidade_consumidora': unidade_consumidora,
                'parceiro_negocio': parceiro_negocio,
                'numero_cliente': numero_cliente,
                'numero_instalacao': numero_instalacao,
                'codigo_cliente': codigo_cliente,
                'codigo_instalacao': codigo_instalacao,
                'codigo_unico': codigo_unico,
                'senha': senha,
                'ativo': ativo
            }
        )
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        protocolo.destroy()

    # Botão "Salvar"
    Button(protocolo, text="Salvar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=salvar_protocolo).place(relx=0.76, rely=0.96, anchor="e")

    # --- Botão "Novo Lançamento" ---
    Button(protocolo, text="Limpar", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=novo_lancamento).place(relx=0.87, rely=0.96, anchor="e")

    # --- Botão "Sair" ---
    Button(protocolo, text="Sair", width=10, height=1, fg="white", bg="#024593", font=('Arial', 12, 'bold'),
           command=protocolo.destroy).place(relx=0.98, rely=0.96, anchor="e")

    # Botão para cancelar um registro

    def invalidar_registro_selecionado():
        id_registro = entry_id_registro.get().strip()
        if not id_registro:
            messagebox.showwarning("Atenção", "Por favor, insira o ID do registro que deseja invalidar.")
            return
        try:
            id_registro = int(id_registro)
            invalidar_registro('Protocolo', id_registro)
        except ValueError:
            messagebox.showerror("Erro", "ID do registro deve ser um número inteiro.")

    Label(protocolo, text='ID do Registro:', bg="#a4bad2").place(relx=0.86, rely=0.19, anchor="w")
    entry_id_registro = Entry(protocolo, justify='center')
    entry_id_registro.place(relx=0.85, rely=0.22, width=100, height=25, anchor="w")

    Button(protocolo, text="Confirmar", width=9, height=1, fg="white", bg="#024593",
           font=('Arial', 12, 'bold'),
           command=invalidar_registro_selecionado).place(relx=0.85, rely=0.28, anchor="w")

    # ---------------------------------------------------
    # SIMULADOR PARA TRIP NA UHE FGO
    # ---------------------------------------------------

"""
# Dicionário global para armazenar as referências dos campos de entrada
entries = {}
"""


def cmd_click18():
    global current_user, entries
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    def formatar_numero(event, entry):
        """Substitui vírgula por ponto mantendo a posição do cursor"""
        conteudo = entry.get()
        if ',' in conteudo:
            posicao_cursor = entry.index(INSERT)  # Guarda posição do cursor
            novo_conteudo = conteudo.replace(',', '.')
            entry.delete(0, END)
            entry.insert(0, novo_conteudo)
            entry.icursor(posicao_cursor)  # Devolve o cursor para o lugar certo

    def configurar_entries_numericos():
        """Configura todos os entries numéricos para converter vírgula em ponto automaticamente"""
        # Removido o espaço extra de "nam_m"
        campos_numericos = [
            "nam_a", "nam_m", "tmp_man", "aflref", "vert", "ugv",
            "potdisp", "abcs2"
        ]

        for campo in campos_numericos:
            if campo in entries:
                # O evento <KeyRelease> garante que pegamos o caractere após a digitação
                entries[campo].bind("<KeyRelease>",
                                    lambda e, entry=entries[campo]: formatar_numero(e, entry))

    sim_trip_fgo = Toplevel(root)
    sim_trip_fgo.title('COG-ALUPAR - SIMULAR TRIP NA UHE FERREIRA GOMES')
    sim_trip_fgo.geometry('1200x710')
    sim_trip_fgo.resizable(False, False)
    sim_trip_fgo['bg'] = "#a4bad2"

    # Frame a esquerda para a inserção dos dados
    left_frame = Frame(sim_trip_fgo, borderwidth=1, relief="solid", bg="#a4bad2")
    left_frame.place(x=5, y=85, width=400, height=613)

    # Frame a direita para exibir os resultados
    right_frame = Frame(sim_trip_fgo, borderwidth=1, relief="solid", bg="#F0F0F0")
    right_frame.place(x=400, y=85, width=790, height=613)

    # Título
    lf1 = Label(sim_trip_fgo, text='Simulador para o caso de TRIP na UHE FGO', font=('Arial', 14, 'bold'),
                bg="#024593", fg="white")
    lf1.place(relx=0.00, rely=0.00, width=1200, height=60)

    lf = Label(sim_trip_fgo, text="Entre com os dados solicitados abaixo:", bg="#a4bad2", font=("Arial", 10, "bold"))
    lf.place(x=80, y=62)

    lf2 = Label(sim_trip_fgo, text="Resultado da Simulação", bg="#a4bad2", font=("Arial", 10, "bold"))
    lf2.place(x=700, y=62)

    # Campos de entrada
    Label(left_frame, text="Nível Montante Atual:", bg="#a4bad2", font=("Arial", 10)).place(x=10, y=20)
    entries["nam_a"] = Entry(left_frame, justify='center')
    entries["nam_a"].place(x=270, y=20, width=110, height=25)

    Label(left_frame, text="Nível Montante Desejado:", bg="#a4bad2", font=("Arial", 10)).place(x=10, y=60)
    entries["nam_m"] = Entry(left_frame, justify='center')
    entries["nam_m"].place(x=270, y=60, width=110, height=25)

    Label(left_frame, text="Tempo entre manobras (minutos):", bg="#a4bad2", font=("Arial", 10)).place(x=10, y=100)
    entries["tmp_man"] = Entry(left_frame, justify='center')
    entries["tmp_man"].place(x=270, y=100, width=110, height=25)

    Label(left_frame, text="Vazão Afluente de Referência:", bg="#a4bad2", font=("Arial", 10)).place(x=10, y=140)
    entries["aflref"] = Entry(left_frame, justify='center')
    entries["aflref"].place(x=270, y=140, width=110, height=25)

    Label(left_frame, text="Vazão Vertida Atual:", bg="#a4bad2", font=("Arial", 10)).place(x=10, y=180)
    entries["vert"] = Entry(left_frame, justify='center')
    entries["vert"].place(x=270, y=180, width=110, height=25)

    Label(left_frame, text="Número de UGs rodando à vazio:", bg="#a4bad2", font=("Arial", 10)).place(x=10, y=220)
    entries["ugv"] = Entry(left_frame, justify='center')
    entries["ugv"].place(x=270, y=220, width=110, height=25)

    Label(left_frame, text="Potência disponível nas UGs Sincronizadas:", bg="#a4bad2", font=("Arial", 10)).place(x=10,
                                                                                                                 y=260)
    entries["potdisp"] = Entry(left_frame, justify='center')
    entries["potdisp"].place(x=270, y=260, width=110, height=25)

    Label(left_frame, text="Abertura da Comporta 2 (mm):", bg="#a4bad2", font=("Arial", 10)).place(x=10, y=300)
    entries["abcs2"] = Entry(left_frame, justify='center')
    entries["abcs2"].place(x=270, y=300, width=110, height=25)

    # Label para exibir os resultados
    result_label = Label(right_frame, text="", justify="left", wraplength=800, anchor="w")
    result_label.pack(pady=10)

    nomes_campos = {
        "nam_a": "Nível Montante Atual",
        "nam_m": "Nível Montante Desejado",
        "tmp_man": "Tempo entre manobras (minutos)",
        "aflref": "Vazão Afluente de Referência",
        "vert": "Vazão Vertida Atual",
        "ugv": "Número de UGs rodando à vazio",
        "potdisp": "Potência disponível nas UGs Sincronizadas",
        "abcs2": "Abertura da Comporta 2 (mm)"
    }

    def validar_entradas():
        # Definir os limites mínimos e máximos para cada campo
        limites = {
            "nam_a": (19.80, 22),
            "nam_m": (19.80, 22),
            "tmp_man": (3, 60),
            "aflref": (0, 10000),
            "vert": (0, 8000),
            "ugv": (0, 3),
            "potdisp": (0, 252),
            "abcs2": (0, 13001)
        }
        for key, entry in entries.items():
            try:
                valor = float(entry.get())
                minimo, maximo = limites[key]
                if not (minimo <= valor <= maximo):
                    sim_trip_fgo.focus_force()
                    messagebox.showerror("Erro",
                                         f"Valor fora do intervalo permitido para {nomes_campos[key]}: {minimo} a {maximo}")
                    return False
            except ValueError:
                messagebox.showerror("Erro", f"Valor inválido para {nomes_campos[key]}. Use ponto ao invés de vírgula.")
                return False
        return True

    def ajustar_tempo(horas, minutos):
        # Ajusta os minutos e horas se minutos >= 60
        if minutos >= 60:
            horas += minutos // 60
            minutos = minutos % 60
        return horas, minutos

    def calcular():
        if not validar_entradas():
            return
        try:
            nam_a = float(entries["nam_a"].get())
            nam_m = float(entries["nam_m"].get())
            tmp_man = float(entries["tmp_man"].get())
            aflref = float(entries["aflref"].get())
            vert = float(entries["vert"].get())
            ugv = float(entries["ugv"].get())
            potdisp = float(entries["potdisp"].get())
            abcs2 = float(entries["abcs2"].get())

            # Lógica de cálculo
            potencia = potdisp * 6.7
            vazio = ugv * 60.0
            qaflu_acum = aflref - (potencia + vazio)

            if aflref > (potencia + vazio):
                if qaflu_acum < vert:
                    qaflu_acum = vert
            else:
                if abcs2 > 0:
                    qaflu_acum = vert
                else:
                    qaflu_acum = 0

            nec_vert = qaflu_acum - vert

            if aflref > (potencia + vazio + 46.5):
                meta = ((nam_m - nam_a) * 100) / (nec_vert / 46.5)
                horas = int(meta)
                minutos = round(int(60 * (meta - horas)))
            else:
                horas = "∞"
                minutos = "∞"

            # Cálculo do tempo para concluir as manobras
            if nec_vert <= 650 and aflref <= 2600:
                ab2 = round((nec_vert * 2 + abcs2) / 100) * 100
                if ab2 > 300:
                    temp_man = (ab2 - 300 - abcs2) / 100 * tmp_man / 60
                    if abcs2 < 300:
                        if potdisp >= 20 and abcs2 == 0:
                            hour_man = int(temp_man)
                            minuts_man = round(int(60 * (temp_man - hour_man))) + 7  # abertura de 50/50 mm
                        else:
                            hour_man = int(temp_man)
                            minuts_man = round(int(60 * (temp_man - hour_man))) + 3  # abertura de 100/100 mm
                    else:
                        hour_man = int(temp_man)
                        minuts_man = round(int(60 * (temp_man - hour_man)))
                else:
                    if potdisp >= 20 and abcs2 == 0:
                        hour_man = 0
                        minuts_man = 7
                    else:
                        hour_man = 0
                        minuts_man = 3

            elif nec_vert > 650 and aflref <= 2600:
                ab2 = round(((qaflu_acum - 650) * 6 + 1300) / 100) * 100
                if ab2 > 300:
                    temp_man = (ab2 - 300 - abcs2) / 100 * tmp_man / 60
                    if abcs2 < 300:
                        if potdisp >= 20 and abcs2 == 0:
                            hour_man = int(temp_man)
                            minuts_man = round(int(60 * (temp_man - hour_man))) + 7  # abertura de 50/50 mm
                        else:
                            hour_man = int(temp_man)
                            minuts_man = round(int(60 * (temp_man - hour_man))) + 3  # abertura de 100/100 mm
                    else:
                        hour_man = int(temp_man)
                        minuts_man = round(int(60 * (temp_man - hour_man)))
                else:
                    if potdisp >= 20 and abcs2 == 0:
                        hour_man = int(0)
                        minuts_man = int(7)
                    else:
                        hour_man = int(0)
                        minuts_man = int(3)

            elif 2600 < aflref <= 6500:
                if abcs2 >= 13000:
                    ab_adcs13 = round(
                        ((aflref - (potdisp * 6.7)) - (ugv * 60 - 1953 - 650)) / 0.17 / 2 / 100) * 100 + 1300
                    ab_adcs13i = round(vert - 1953 - 650) / 0.17 / 2 / 100 * 100 + 1300
                    temp_man = (ab_adcs13 - ab_adcs13i) / 100 * tmp_man / 60
                    hour_man = int(temp_man)
                    minuts_man = round(int(60 * (temp_man - hour_man)))

                else:
                    if round(((aflref - (potdisp * 6.7) - (ugv * 60) - 650) * 6 + 1300) / 100) * 100 >= 13000:
                        ab_adcs2 = 13000
                        ab_adcs13 = round(
                            (aflref - (potdisp * 6.7) - (ugv * 60)) - 1953 - 650) / 0.17 / 2 / 100 * 100
                        ab_necess = ab_adcs2 - abcs2 + ab_adcs13
                        temp_man = ab_necess / 100 * tmp_man / 60
                        hour_man = int(temp_man)
                        minuts_man = round(int(60 * (temp_man - hour_man)))
                    else:
                        ab_adcs2 = round((aflref - (potdisp * 6.7) - (ugv * 60) - 650) * 6 + 1300) / 100 * 100
                        ab_adcs13 = 1300
                        ab_necess = ab_adcs2 - abcs2
                        temp_man = ab_necess / 100 * tmp_man / 60
                        hour_man = int(temp_man)
                        minuts_man = round(int(60 * (temp_man - hour_man)))

            elif 6500 < aflref <= 7113:
                temp_man = 0.25
                hour_man = int(temp_man)
                minuts_man = round(int(60 * (temp_man - hour_man)))

            elif 7113 < aflref <= 7568:
                temp_man = 0.25
                hour_man = int(temp_man)
                minuts_man = round(int(60 * (temp_man - hour_man)))

            elif aflref > 7568:
                temp_man = 0.25
                hour_man = int(temp_man)
                minuts_man = round(int(60 * (temp_man - hour_man)))

            else:
                pass

            msg_1a = "Até 200 mm - Manobras de 50/50 mm e de 200 a 300 - manobras de 100/100 mm\n      Aguardar 1 minuto entre as manobras."
            msg_1b = "Até 300 mm - Manobras de 100/100 mm - Uma manobra após a outra."
            msg_2a = "De 300 à 1300 mm - Manobras de 100/100 mm - Acompanhar Delta da Comporta e Saturação de Oxigênio."
            msg_3a = (
                "Acima de 1300 mm - Manobras de 100/100 mm - Somente na CS-2 + Acompanhar Delta da Comporta\n       e Saturação de Oxigênio,"
                " lembrando que em algum momento você poderá ter que aumentar esse steep.")
            msg_4a = "Neste caso, haverá necessidade de efetuar a abertura Total da CS-2, que provocará\n      um incremento de +455 m3/s na vazão vertida."
            msg_4b = "Neste caso, haverá necessidade de efetuar a abertura Total da CS-3, que provocará\n      um incremento de +455 m3/s na vazão vertida."
            msg_4c = "Neste caso, haverá necessidade de efetuar a abertura Total da CS-1, que provocará\n      um incremento de +455 m3/s na vazão vertida."
            msg_5a = "Remanejar a carga nas demais UGs."
            msg_5b = "Não há necessidade de manobrar as Comportas do Vertedouro."
            msg_5c = "Acompanhar evolução do Nível de Montante."
            msg_6a = "Atenção: Como o tempo necessário para concluir as manobras de abertura do vertedouro é muito\n" \
                     "                           maior do que o tempo para o Nível Montante atingir o valor desejado, em algum momento desta\n" \
                     "                           ocorrência você terá que tomar a seguinte decisão:\n\n" \
                     "                           - Reduzir o tempo (entre uma manobra e outra) nas comportas do vertedouro;\n" \
                     "                           - Aumentar os steps de abertura das comportas do vertedouro;\n" \
                     "                           - Aumentar a vazão turbinada, retornando com UGs que sofreram Trip.\n"
            msg_6b = "Acompanhar a evolução dos índices de Saturação de oxigênio.\n"

            # if horas < hour_man or (horas == hour_man and minutos > (minuts_man + 25)):
            if (((hour_man * 60) + minuts_man) - ((horas * 60) + minutos)) > 25:
                msg_6 = msg_6a
            else:
                msg_6 = msg_6b
                pass

            if aflref <= 650 and nec_vert <= 650:
                if potdisp >= 20 and abcs2 == 0:
                    cs_13 = round((nec_vert * 2 + abcs2) / 100) * 100  # Para arredondar
                    cs_2 = cs_13
                    if cs_2 == abcs2 or cs_2 == 0:
                        msg_1 = msg_5a
                        msg_2 = msg_5b
                        msg_3 = msg_5c
                    else:
                        msg_1 = msg_1a
                        msg_2 = msg_2a
                        msg_3 = msg_3a
                else:
                    cs_13 = round((nec_vert * 2 + abcs2) / 100) * 100
                    cs_2 = cs_13
                    if cs_2 == abcs2 or cs_2 == 0:
                        msg_1 = msg_5a
                        msg_2 = msg_5b
                        msg_3 = msg_5c
                    else:
                        msg_1 = msg_1b
                        msg_2 = msg_2a
                        msg_3 = msg_3a

            elif aflref > 650 and nec_vert > 650:
                if potdisp >= 20 and abcs2 == 0:
                    if qaflu_acum < 2600:
                        cs_13 = 1300
                        cs_2 = round(((qaflu_acum - 650) * 6 + 1300) / 100) * 100
                        if cs_2 == abcs2 or cs_2 == 0:
                            msg_1 = msg_5a
                            msg_2 = msg_5b
                            msg_3 = msg_5c
                        else:
                            msg_1 = msg_1a
                            msg_2 = msg_2a
                            msg_3 = msg_3a

                    elif 2600 <= qaflu_acum <= 6500:
                        cs_13 = round(((qaflu_acum - 2170) / 0.17 / 2 / 100) * 100)
                        cs_2 = 13000
                        msg_1 = msg_1a
                        msg_2 = msg_2a
                        msg_3 = msg_3a

                    elif 6500 < qaflu_acum <= 7113:
                        cs_13 = 13000
                        cs_2a = 'Total'
                        msg_1 = msg_4a

                    elif 7113 < qaflu_acum <= 7568:
                        cs_3 = 'Total'
                        cs_13 = 13000
                        cs_2a = 'Total'
                        msg_1 = msg_4b

                    else:
                        cs_3 = 'Total'
                        cs_1 = 'Total'
                        cs_2a = 'Total'
                        msg_1 = msg_4c

                else:
                    if qaflu_acum < 2600:
                        cs_13 = 1300
                        cs_2 = round(((qaflu_acum - 650) * 6 + 1300) / 100) * 100
                        msg_1 = msg_1b
                        msg_2 = msg_2a
                        msg_3 = msg_3a

                    elif 2600 <= qaflu_acum <= 6500:
                        cs_13 = round(((qaflu_acum - 2170) / 0.17 / 2) / 100) * 100
                        cs_2 = 13000
                        msg_1 = msg_1b
                        msg_2 = msg_2a
                        msg_3 = msg_3a

                    elif 6500 < qaflu_acum <= 7113:
                        cs_13 = 13000
                        cs_2a = 'Total'
                        msg_1 = msg_4a

                    elif 7113 < qaflu_acum <= 7568:
                        cs_3 = 'Total'
                        cs_13 = 13000
                        cs_2a = 'Total'
                        msg_1 = msg_4b

                    else:
                        cs_3 = 'Total'
                        cs_1 = 'Total'
                        cs_2a = 'Total'
                        msg_1 = msg_4c

            elif aflref > 650 and nec_vert <= 650:
                if potdisp >= 20 and abcs2 == 0:
                    if nec_vert * 2 + abcs2 <= 1300:
                        cs_13 = round((nec_vert * 2 + abcs2) / 100) * 100
                        cs_2 = cs_13
                        if cs_2 == abcs2 or cs_2 == 0:
                            msg_1 = msg_5a
                            msg_2 = msg_5b
                            msg_3 = msg_5c
                        else:
                            msg_1 = msg_1a
                            msg_2 = msg_2a
                            msg_3 = msg_3a
                    else:
                        cs_13 = 1300
                        cs_2 = round(((qaflu_acum - 650) * 6 + 1300) / 100) * 100
                        if cs_2 == abcs2 or cs_2 == 0:
                            msg_1 = msg_5a
                            msg_2 = msg_5b
                            msg_3 = msg_5c
                        else:
                            msg_1 = msg_1a
                            msg_2 = msg_2a
                            msg_3 = msg_3a
                else:
                    if nec_vert * 2 + abcs2 <= 1300:
                        cs_13 = round((nec_vert * 2 + abcs2) / 100) * 100
                        cs_2 = cs_13
                        if cs_2 == abcs2 or cs_2 == 0:
                            msg_1 = msg_5a
                            msg_2 = msg_5b
                            msg_3 = msg_5c
                        else:
                            msg_1 = msg_1b
                            msg_2 = msg_2a
                            msg_3 = msg_3a
                    else:
                        cs_13 = 1300
                        cs_2 = round(((qaflu_acum - 650) * 6 + 1300) / 100) * 100
                        if cs_2 == abcs2 or cs_2 == 0:
                            msg_1 = msg_5a
                            msg_2 = msg_5b
                            msg_3 = msg_5c
                        else:
                            msg_1 = msg_1b
                            msg_2 = msg_2a
                            msg_3 = msg_3a
            else:
                pass

            # Ajustar minutos e horas para ambos os casos
            if minutos != "∞":
                horas, minutos = ajustar_tempo(horas, minutos)
            if minuts_man != "∞":
                hour_man, minuts_man = ajustar_tempo(hour_man, minuts_man)

            minutos_formatado = f"{minutos:02d}"  # Formata para dois dígitos
            minuts_man_formatado = f"{minuts_man:02d}"  # Formata para dois dígitos

            # Exibir resultados
            result = (
                f"Tempo para atingir o NA Desejado: ==> {horas} h : {minutos_formatado} min\n\n"
                f"Tempo para concluir as manobras: ==> {hour_man} h : {minuts_man_formatado} min\n\n"
                f"Importante: ==> {msg_6}\n\n"
                f"Vazão Vertida Final: ==> {qaflu_acum:.0f} m³/s\n\n\n"
                f"Posição final das Comportas do Vertedouro:\n\n"
                f" ==> Comporta-1: {cs_13} mm                    Comporta-2: {cs_2} mm                    Comporta-3: {cs_13} mm  <==\n\n\n"
                f"  Manobras no Vertedouro:\n\n==> {msg_1}\n\n==> {msg_2}\n\n==> {msg_3}\n"
            )
            result_label.config(text=result, wraplength=800, justify="left", font=("arial", 11))

        except ValueError:
            result_label.config(text="Erro: Por favor, insira valores válidos: ponto e não vírgula.")

    def novo_calculo():
        # Limpa todos os campos de entrada
        for entry in entries.values():
            entry.delete(0, 'end')
        result_label.config(text="Entre com os novos dados!")

    def mostrar_dicas1():
        dicas = (
            "Atenção:\n\n"
            "- Somente os valores de níveis, serão inseridos com duas\n"
            "  casas decimais separadas por ponto,demais dados serão\n"
            "  inseridos utilizando números inteiros\n\n"
            "- O Nível de Montante Desejado, é o nível escolhido para\n"
            "  efetuar os cálculos, a fim de, auxiliar o Operador na\n"
            "  tomada de decisão. Não é nível META que não possa ser\n"
            "  ultrapassado.\n\n"
            "- A potência disponivel nas UGs sincronizadas, são a potência\n"
            "  de maquinas que estão sincronizadas e ou maquinas que\n"
            "  estão rodando a vazio e podem assumir a carga\n"
            "  imediatamente.\n\n"
            "- Ficar atento pois os valores a serem inseridos, possuem\n"
            "  limitações máximas e mínimas.\n\n"
        )
        messagebox.showinfo("Orientações de Preenchimento", dicas, parent=sim_trip_fgo)

    configurar_entries_numericos()

    Button(left_frame, text="Orientações de Preenchimento", command=mostrar_dicas1, bg="#a4bad2", fg="black",
           font=("Arial", 9)).place(relx=0.22, rely=0.62, width=200, height=25)

    Button(left_frame, text="Calcular", command=calcular, bg="#024593", fg="white",
           font=("Arial", 12, "bold")).place(relx=0.35, rely=0.8, width=120, height=30)

    Button(left_frame, text="Novo Cálculo", command=novo_calculo, bg="#FF0000", fg="white",
           font=("Arial", 12, "bold")).place(relx=0.35, rely=0.9, width=120, height=30)


# ---------------------------------------------------
# SIMULADOR PARA VERIFICAR ÍNDICES DE SATURAÇÃO UHE FGO DURANTE LIBERAÇÕES
# ---------------------------------------------------
def cmd_click19():
    def criar_campos(frame, campos, x_entry, y_inicial, y_incremento):
        entries = {}
        for i, (key, label_text) in enumerate(campos.items()):
            y = y_inicial + i * y_incremento
            Label(frame, text=label_text, bg="#a4bad2", font=("Arial", 10)).place(x=10, y=y)
            entry = Entry(frame, justify='center')
            entry.place(x=x_entry, y=y, width=110, height=25)
            entries[key] = entry
        return entries

    def formatar_numero(event, entry):
        """Substitui vírgula por ponto mantendo a posição do cursor"""
        conteudo = entry.get()
        if ',' in conteudo:
            posicao_cursor = entry.index(INSERT)  # Guarda posição do cursor
            novo_conteudo = conteudo.replace(',', '.')
            entry.delete(0, END)
            entry.insert(0, novo_conteudo)
            entry.icursor(posicao_cursor)  # Devolve o cursor para o lugar certo

    def configurar_entries_numericos():
        """Configura todos os entries numéricos para converter vírgula em ponto automaticamente"""
        # Removido o espaço extra de "nam_m"
        campos_numericos = [
            "nam_a", "nam_m", "aflref", "tmp_int", "abcs1_i", "abcs2_i",
            "abcs3_i", "v_vertida_i", "ugv", "potdisp"
        ]

        for campo in campos_numericos:
            if campo in entries:
                # O evento <KeyRelease> garante que pegamos o caractere após a digitação
                entries[campo].bind("<KeyRelease>",
                                    lambda e, entry=entries[campo]: formatar_numero(e, entry))

    def validar_entradas(entries, limites, nomes_campos):
        for key, entry in entries.items():
            try:
                valor = float(entry.get())
                minimo, maximo = limites[key]
                if not (minimo <= valor <= maximo):
                    messagebox.showerror("Erro",
                                         f"Valor fora do intervalo permitido para {nomes_campos[key]}: {minimo} a {maximo}")
                    return False
            except ValueError:
                messagebox.showerror("Erro", f"Valor inválido para {nomes_campos[key]}. Use ponto ao invés de vírgula.")
                return False
        return True

    def atualizar_imagem():
        escolha = opcao_sonda.get()

        # Seleciona o arquivo baseado na escolha
        if escolha == 1:
            nova_img = PhotoImage(file="grafico1.png")
        elif escolha == 2:
            nova_img = PhotoImage(file="grafico2.png")
        else:
            nova_img = PhotoImage(file="grafico3.png")

        # Atualiza a Label
        right_frame_Image_Label.config(image=nova_img)
        right_frame_Image_Label.image = nova_img  # Garante que o Python não apague a imagem da memória

    def arredondar_para_multiplo_de_100(valor):
        resto = valor % 100
        if resto >= 50:
            return valor + (100 - resto)
        else:
            return valor - resto

    def calcular_vazao_vertida(abcs_f, nam_a):
        if abcs_f == 0:
            return 0
        elif 0 < abcs_f <= 1000:
            return int(abcs_f * ((-0.2857 * nam_a ** 2 + 24.6 * nam_a + 114.53) / 3) / 1000)
        elif 1000 < abcs_f <= 2000:
            return int(abcs_f * ((-0.2143 * nam_a ** 2 + 22.3 * nam_a + 138.24) / 3) / 1000)
        elif 2000 < abcs_f <= 3000:
            return int(abcs_f * ((-0.1667 * nam_a ** 2 + 20.933 * nam_a + 150.4) / 3) / 1000)
        elif 3000 < abcs_f <= 4000:
            return int(abcs_f * ((-0.1964 * nam_a ** 2 + 22.7 * nam_a + 129.43) / 3) / 1000)
        elif 4000 < abcs_f <= 5000:
            return int(abcs_f * ((-0.2286 * nam_a ** 2 + 24.44 * nam_a + 108.8) / 3) / 1000)
        elif 5000 < abcs_f <= 6000:
            return int(abcs_f * ((-0.2381 * nam_a ** 2 + 25.3 * nam_a + 94.236) / 3) / 1000)
        elif 6000 < abcs_f <= 7000:
            return int(abcs_f * ((-0.2551 * nam_a ** 2 + 26.429 * nam_a + 77.364) / 3) / 1000)
        elif 7000 < abcs_f <= 8000:
            return int(abcs_f * ((-0.2589 * nam_a ** 2 + 27.1 * nam_a + 63.665) / 3) / 1000)
        elif 8000 < abcs_f <= 9000:
            return int(abcs_f * ((-0.2937 * nam_a ** 2 + 29 * nam_a + 37.32) / 3) / 1000)
        elif 9000 < abcs_f <= 10000:
            return int(abcs_f * ((-0.3071 * nam_a ** 2 + 30.06 * nam_a + 18.887) / 3) / 1000)
        elif 10000 < abcs_f <= 11000:
            return int(abcs_f * ((-0.3247 * nam_a ** 2 + 31.309 * nam_a - 1.8388) / 3) / 1000)
        elif 11000 < abcs_f <= 12000:
            return int(abcs_f * ((-0.3333 * nam_a ** 2 + 32.2 * nam_a - 19.38) / 3) / 1000)
        elif 12000 < abcs_f <= 13000:
            return int(abcs_f * ((-0.321 * nam_a ** 2 + 31.691 * nam_a - 14.156) / 3) / 1000)
        else:
            return 8023

    def calcular_impactos_s1(delta2, abcs2_f):

        if delta2 <= -4.25:
            if 4001 < abcs2_f <= 14000:
                return "0,0%", "0,0%", "0,3%", "1,6%", "29,5%", "38,2%", "30,3%"
            elif 3000 < abcs2_f <= 4000:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        if -4.25 < delta2 <= -0.75:
            if 4001 < abcs2_f <= 14000:
                return "1,2%", "2,1%", "20,4%", "47,1%", "23,2%", "3,9%", "2,0%"
            elif 3000 < abcs2_f <= 4000:
                return "4,0%", "0,0%", "0,0%", "16,0%", "24,0%", "4,0%", "52,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        elif -0.75 < delta2 <= 0:
            if 4001 < abcs2_f <= 14000:
                return "2,0%", "4,0%", "60,6%", "25,2%", "5,8%", "2,4%", "0,1%"
            elif 3000 < abcs2_f <= 4000:
                return "2,1%", "0,6%", "15,0%", "30,2%", "38,3%", "10,3%", "3,5%"
            elif 2500 < abcs2_f <= 3000:
                return "0,0%", "0,0%", "4,8%", "23,8%", "52,4%", "0,0%", "19,0%"
            elif 2000 < abcs2_f <= 2500:
                return "0,0%", "0,0%", "0,0%", "80,0%", "0,0%", "0,0%", "20,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        elif 0 < delta2 <= 0.75:
            if 4001 < abcs2_f <= 14000:
                return "0,3%", "2,7%", "84,1%", "6,5%", "2,8%", "3,5%", "0,1%"
            elif 3000 < abcs2_f <= 4000:
                return "4,2%", "2,7%", "53,6%", "26,8%", "9,4%", "3,0%", "0,5%"
            elif 2500 < abcs2_f <= 3000:
                return "0,5%", "1,4%", "32,9%", "40,2%", "18,5%", "4,0%", "2,5%"
            elif 2000 < abcs2_f <= 2500:
                return "3,3%", "4,1%", "18,2%", "39,7%", "16,1%", "11,6%", "7,0%"
            elif 1300 < abcs2_f <= 2000:
                return "2,5%", "12,5%", "12,5%", "16,3%", "10,0%", "11,3%", "35,0%"
            elif 0 < abcs2_f <= 1000:
                return "70,8%", "18,5%", "10,7%", "0,0%", "0,0%", "0,0%", "0,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        elif delta2 > 0.75:
            if 4001 < abcs2_f <= 14000:
                return "0,0%", "0,0%", "0,0%", "0,0%", "30,4%", "0,0%", "69,6%"
            elif 3000 < abcs2_f <= 4000:
                return "5,7%", "6,7%", "54,2%", "20,0%", "12,5%", "0,9%", "0,0%"
            elif 2500 < abcs2_f <= 3000:
                return "4,2%", "8,0%", "39,1%", "33,0%", "13,0%", "1,4%", "1,3%"
            elif 2000 < abcs2_f <= 2500:
                return "13,0%", "19,5%", "38,0%", "17,7%", "8,9%", "1,3%", "1,7%"
            elif 1300 < abcs2_f <= 2000:
                return "23,9%", "28,0%", "25,2%", "16,7%", "5,5%", "0,6%", "0,2%"
            elif 1000 < abcs2_f <= 1300:
                return "29,6%", "38,1%", "20,8%", "10,2%", "1,1%", "0,0%", "0,1%"
            else:
                return "88,6%", "8,0%", "2,9%", "0,4%", "0,0%", "0,0%", "0,0%"
        else:
            return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

    def calcular_impactos_s2(delta2, abcs2_f):

        if delta2 <= -4.25:
            if 4001 < abcs2_f <= 14000:
                return "0,0%", "0,0%", "0,9%", "3,6%", "27,5%", "36,2%", "32,3%"
            elif 3000 < abcs2_f <= 4000:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        if -4.25 < delta2 <= -0.75:
            if 4001 < abcs2_f <= 14000:
                return "3,2%", "4,1%", "16,4%", "44,1%", "26,2%", "4,9%", "1,0%"
            elif 3000 < abcs2_f <= 4000:
                return "4,0%", "0,0%", "4,0%", "12,0%", "20,0%", "8,0%", "52,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        elif -0.75 < delta2 <= 0:
            if 4001 < abcs2_f <= 14000:
                return "2,0%", "4,0%", "60,6%", "25,2%", "5,8%", "2,4%", "0,1%"
            elif 3000 < abcs2_f <= 4000:
                return "2,1%", "0,6%", "15,0%", "30,2%", "38,3%", "10,3%", "3,5%"
            elif 2500 < abcs2_f <= 3000:
                return "0,0%", "0,0%", "4,8%", "23,8%", "52,4%", "0,0%", "19,0%"
            elif 2000 < abcs2_f <= 2500:
                return "0,0%", "0,0%", "0,0%", "80,0%", "0,0%", "0,0%", "20,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        elif 0 < delta2 <= 0.75:
            if 4001 < abcs2_f <= 14000:
                return "0,3%", "2,7%", "84,1%", "6,5%", "2,8%", "3,5%", "0,1%"
            elif 3000 < abcs2_f <= 4000:
                return "4,2%", "2,7%", "53,6%", "26,8%", "9,4%", "3,0%", "0,5%"
            elif 2500 < abcs2_f <= 3000:
                return "0,5%", "1,4%", "32,9%", "40,2%", "18,5%", "4,0%", "2,5%"
            elif 2000 < abcs2_f <= 2500:
                return "3,3%", "4,1%", "18,2%", "39,7%", "16,1%", "11,6%", "7,0%"
            elif 1300 < abcs2_f <= 2000:
                return "2,5%", "12,5%", "12,5%", "16,3%", "10,0%", "11,3%", "35,0%"
            elif 0 < abcs2_f <= 1000:
                return "70,8%", "18,5%", "10,7%", "0,0%", "0,0%", "0,0%", "0,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        elif delta2 > 0.75:
            if 4001 < abcs2_f <= 14000:
                return "0,0%", "0,0%", "0,0%", "0,0%", "30,4%", "0,0%", "69,6%"
            elif 3000 < abcs2_f <= 4000:
                return "5,7%", "6,7%", "54,2%", "20,0%", "12,5%", "0,9%", "0,0%"
            elif 2500 < abcs2_f <= 3000:
                return "4,2%", "8,0%", "39,1%", "33,0%", "13,0%", "1,4%", "1,3%"
            elif 2000 < abcs2_f <= 2500:
                return "13,0%", "19,5%", "38,0%", "17,7%", "8,9%", "1,3%", "1,7%"
            elif 1300 < abcs2_f <= 2000:
                return "23,9%", "28,0%", "25,2%", "16,7%", "5,5%", "0,6%", "0,2%"
            elif 1000 < abcs2_f <= 1300:
                return "29,6%", "38,1%", "20,8%", "10,2%", "1,1%", "0,0%", "0,1%"
            else:
                return "88,6%", "8,0%", "2,9%", "0,4%", "0,0%", "0,0%", "0,0%"
        else:
            return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

    def calcular_impactos_maior_s1_s2(delta2, abcs2_f):

        if delta2 <= -4.25:
            if 4001 < abcs2_f <= 14000:
                return "0,0%", "0,0%", "0,9%", "3,6%", "27,5%", "36,2%", "32,3%"
            elif 3000 < abcs2_f <= 4000:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        if -4.25 < delta2 <= -0.75:
            if 4001 < abcs2_f <= 14000:
                return "3,2%", "4,1%", "16,4%", "44,1%", "26,2%", "4,9%", "1,0%"
            elif 3000 < abcs2_f <= 4000:
                return "4,0%", "0,0%", "4,0%", "12,0%", "20,0%", "8,0%", "52,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        elif -0.75 < delta2 <= 0:
            if 4001 < abcs2_f <= 14000:
                return "2,0%", "4,0%", "60,6%", "25,2%", "5,8%", "2,4%", "0,1%"
            elif 3000 < abcs2_f <= 4000:
                return "2,1%", "0,6%", "15,0%", "30,2%", "38,3%", "10,3%", "3,5%"
            elif 2500 < abcs2_f <= 3000:
                return "0,0%", "0,0%", "4,8%", "23,8%", "52,4%", "0,0%", "19,0%"
            elif 2000 < abcs2_f <= 2500:
                return "0,0%", "0,0%", "0,0%", "80,0%", "0,0%", "0,0%", "20,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        elif 0 < delta2 <= 0.75:
            if 4001 < abcs2_f <= 14000:
                return "0,3%", "2,7%", "84,1%", "6,5%", "2,8%", "3,5%", "0,1%"
            elif 3000 < abcs2_f <= 4000:
                return "4,2%", "2,7%", "53,6%", "26,8%", "9,4%", "3,0%", "0,5%"
            elif 2500 < abcs2_f <= 3000:
                return "0,5%", "1,4%", "32,9%", "40,2%", "18,5%", "4,0%", "2,5%"
            elif 2000 < abcs2_f <= 2500:
                return "3,3%", "4,1%", "18,2%", "39,7%", "16,1%", "11,6%", "7,0%"
            elif 1300 < abcs2_f <= 2000:
                return "2,5%", "12,5%", "12,5%", "16,3%", "10,0%", "11,3%", "35,0%"
            elif 0 < abcs2_f <= 1000:
                return "70,8%", "18,5%", "10,7%", "0,0%", "0,0%", "0,0%", "0,0%"
            else:
                return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

        elif delta2 > 0.75:
            if 4001 < abcs2_f <= 14000:
                return "0,0%", "0,0%", "0,0%", "0,0%", "30,4%", "0,0%", "69,6%"
            elif 3000 < abcs2_f <= 4000:
                return "5,7%", "6,7%", "54,2%", "20,0%", "12,5%", "0,9%", "0,0%"
            elif 2500 < abcs2_f <= 3000:
                return "4,2%", "8,0%", "39,1%", "33,0%", "13,0%", "1,4%", "1,3%"
            elif 2000 < abcs2_f <= 2500:
                return "13,0%", "19,5%", "38,0%", "17,7%", "8,9%", "1,3%", "1,7%"
            elif 1300 < abcs2_f <= 2000:
                return "23,9%", "28,0%", "25,2%", "16,7%", "5,5%", "0,6%", "0,2%"
            elif 1000 < abcs2_f <= 1300:
                return "29,6%", "38,1%", "20,8%", "10,2%", "1,1%", "0,0%", "0,1%"
            else:
                return "88,6%", "8,0%", "2,9%", "0,4%", "0,0%", "0,0%", "0,0%"
        else:
            return "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%", "0,0%"

    def calcular():
        if not validar_entradas(entries, limites, nomes_campos):
            return

        try:
            # Coletar valores dos campos
            nam_a = float(entries["nam_a"].get())
            nam_m = float(entries["nam_m"].get())
            aflref = float(entries["aflref"].get())
            tmp_int = float(entries["tmp_int"].get())
            abcs1_i = float(entries["abcs1_i"].get())
            abcs2_i = float(entries["abcs2_i"].get())
            abcs3_i = float(entries["abcs3_i"].get())
            v_vertida_i = float(entries["v_vertida_i"].get())
            ugv = float(entries["ugv"].get())
            potdisp = float(entries["potdisp"].get())

            # Definição das variáveis
            cte_comporta = 1000 / 509
            v_turbinada = potdisp * 6.7
            v_vazio = ugv * 60.0
            v_sanitaria = 52
            v_acum_cap = int((nam_m - nam_a) * 100 / tmp_int * 46.5)
            v_defl_i = v_turbinada + v_vazio
            v_defluente_i = aflref  # Considerando uma operação a fio d'água, pois não há dados para cálculo da Q_defl

            # Lógica de cálculo
            if aflref <= v_acum_cap:
                if v_defl_i >= v_sanitaria:
                    v_acum_hora = int(aflref - v_defl_i)
                    var_hora = v_acum_hora / 46.5
                    v_acumulada = 0
                else:
                    v_acum_hora = int(aflref - v_sanitaria)
                    var_hora = v_acum_hora / 46.5
                    v_acumulada = v_sanitaria

            else:
                if v_sanitaria >= (aflref - v_acum_cap):
                    if v_defl_i >= v_sanitaria:
                        v_acum_hora = int(aflref - v_defl_i)
                        var_hora = v_acum_hora / 46.5
                        v_acumulada = 0
                    else:
                        v_acum_hora = v_acum_cap
                        var_hora = v_acum_hora / 46.5
                        v_acumulada = v_sanitaria

                else:
                    if v_defl_i >= v_sanitaria:
                        v_acum_hora = v_acum_cap
                        var_hora = v_acum_hora / 46.5
                        v_acumulada = int(aflref - v_acum_cap - v_defl_i)
                    else:
                        v_acum_hora = v_acum_cap
                        var_hora = v_acum_hora / 46.5
                        v_acumulada = aflref - v_acum_cap

            v_abcs_1300 = int(1300 * ((-0.2143 * nam_a ** 2 + 22.3 * nam_a + 138.24) / 3) / 1000)
            v_abcs_13mil = int(13000 * ((-0.321 * nam_a ** 2 + 31.691 * nam_a - 14.156) / 3) / 1000)
            soma_vazao = (2 * v_abcs_1300 + v_abcs_13mil)

            abcs1_f1 = v_acumulada * cte_comporta
            if abcs1_f1 < 200 and v_acumulada < v_sanitaria:
                abcs1_f = 0
            elif abcs1_f1 < 200 and v_acumulada == v_sanitaria:
                abcs1_f = 105

            elif abcs1_f1 < 1300 and v_acumulada > v_sanitaria:
                if aflref >= v_acum_hora:
                    abcs1_f = int(abcs1_f1)
                else:
                    abcs1_f = int(abcs1_f1 + 100)

            elif abcs1_f1 > 1300 and v_acumulada > soma_vazao:
                abcs1_f = int(1300 + ((v_acumulada - soma_vazao) * 3))
            else:
                abcs1_f = 1300

            abcs3_f1 = v_acumulada * cte_comporta
            if abcs3_f1 < 200 and v_acumulada < v_sanitaria:
                abcs3_f = 0

            elif abcs3_f1 < 200 and v_acumulada == v_sanitaria:
                abcs3_f = 105

            elif abcs3_f1 < 1300 and v_acumulada > v_sanitaria:
                if aflref >= v_acum_hora:
                    abcs3_f = int(abcs3_f1)
                else:
                    abcs3_f = int(abcs3_f1 + 100)

            elif abcs3_f1 > 1300 and v_acumulada > soma_vazao:
                abcs3_f = int(1300 + ((v_acumulada - soma_vazao) * 3))

            else:
                abcs3_f = 1300

            abcs2_f1 = v_acumulada * cte_comporta
            if abcs2_f1 < 200 and v_acumulada < v_sanitaria:
                abcs2_f = 0
            elif abcs2_f1 < 200 and v_acumulada == v_sanitaria:
                abcs2_f = 105
            elif abcs2_f1 < 1300 and v_acumulada > v_sanitaria:
                if aflref >= v_acum_hora:
                    abcs2_f = int(abcs2_f1)
                else:
                    abcs2_f = int(abcs2_f1 + 100)

            elif abcs2_f1 > 1300 and v_acumulada < soma_vazao:
                abcs2_f = int(abcs2_f1 + (abcs1_f1 - 1300) + (abcs3_f1 - 1300))

            else:
                abcs2_f = 13000

            if v_acumulada < v_sanitaria:
                abcs1_f = 0
                abcs2_f = 0
                abcs2_f = 0
                v_vertida_f1 = 0
                v_vertida_f2 = 0
                v_vertida_f3 = 0

            elif v_acumulada == v_sanitaria:
                abcs1_f = 105
                abcs2_f = 105
                abcs3_f = 105
                v_vertida_f1 = v_sanitaria / 3
                v_vertida_f2 = v_sanitaria / 3
                v_vertida_f3 = v_sanitaria / 3

            else:
                abcs1_f = arredondar_para_multiplo_de_100(abcs1_f)
                abcs2_f = arredondar_para_multiplo_de_100(abcs2_f)
                abcs3_f = arredondar_para_multiplo_de_100(abcs3_f)
                v_vertida_f1 = calcular_vazao_vertida(abcs1_f, nam_a)
                v_vertida_f2 = calcular_vazao_vertida(abcs2_f, nam_a)
                v_vertida_f3 = calcular_vazao_vertida(abcs3_f, nam_a)

            v_vertida_f = int(v_vertida_f1 + v_vertida_f2 + v_vertida_f3)

            v_defluente_f = int(v_vertida_f + v_turbinada + v_vazio)

            if 0 <= aflref <= 51:
                n_jusante_i = 1.59
                n_jusante_f = 1.59
            elif 51 < aflref <= 55:
                n_jusante_i = 1.64
                n_jusante_f = 1.64
            elif 55 < aflref <= 58:
                n_jusante_i = 1.70
                n_jusante_f = 1.70
            else:
                n_jusante_i = round(((1.607 + 0.002402 * v_defluente_i) - (0.0000006697 * v_defluente_i ** 2) + (
                        0.00000000008349 * v_defluente_i ** 3)), 2)

                n_jusante_f = round(((1.607 + 0.002402 * v_defluente_f) - (0.0000006697 * v_defluente_f ** 2) + (
                        0.00000000008349 * v_defluente_f ** 3)), 2)

            delta1 = round(n_jusante_f - 0.74 - round(abcs1_f / 1000, 2), 2)
            delta2 = round(n_jusante_f - 0.74 - round(abcs2_f / 1000, 2), 2)
            delta3 = round(n_jusante_f - 0.74 - round(abcs3_f / 1000, 2), 2)

            v_acum_final = float(aflref - v_defluente_f)
            if nam_m != nam_a:
                v_acum = v_acum_hora
                var_acum = var_hora
            else:
                v_acum = v_acum_final
                var_acum = v_acum / 46.5

            # Lógica de seleção da Sonda
            escolha = opcao_sonda.get()

            if escolha == 1:
                msg_1a, msg_1b, msg_1c, msg_1d, msg_1e, msg_1f, msg_1g = calcular_impactos_s1(delta2, abcs2_f)
                sonda_txt = "Sonda 1"
            elif escolha == 2:
                msg_1a, msg_1b, msg_1c, msg_1d, msg_1e, msg_1f, msg_1g = calcular_impactos_s2(delta2, abcs2_f)
                sonda_txt = "Sonda 2"
            else:
                msg_1a, msg_1b, msg_1c, msg_1d, msg_1e, msg_1f, msg_1g = calcular_impactos_maior_s1_s2(delta2,
                                                                                                       abcs2_f)
                sonda_txt = "Maior S1/S2"

            # Exibir resultados
            result = (
                f" =========( Resultado da simulação baseado nos dados históricos da {sonda_txt} de jun/2018 à fev/2026 )=========\n\n"
                f" Nível de jusante:  Antes da liberação: {n_jusante_i:.2f} m   -   Durante a liberação: {n_jusante_f:.2f} m\n\n"
                f" Q_Vertida:  {v_vertida_f} m³/s +  Q_Turbinada: {v_turbinada:.0f} m³/s  + Q_Vazio: {v_vazio:.0f} m³/s = Q_Defluente: {v_defluente_f} m³/s\n\n"
                f" Vazão a ser acumulada de hora em hora:  {v_acum:.1f} m³/s, correspondente à {var_acum:.1f} cm/h\n\n"
                f" Posição final das Comportas do Vertedouro:\n\n"
                f" Comporta-1:  {abcs1_f} mm       Comporta-2:  {abcs2_f} mm          Comporta-3:  {abcs3_f} mm\n\n"
                f" Valor do Delta das Comportas - 1, 2 e 3:\n\n"
                f" Delta CS-1:  {delta1} m           Delta CS-2:  {delta2} m             Delta CS-3:  {delta3} m\n\n"
                f" Comportamento da Saturação de Oxigênio em virtude da Liberação:\n\n"
                f" => Probabilidade do índice de saturação ficar entre    0 e 95%:  {msg_1a}\n\n"
                f" => Probabilidade do índice de saturação ficar entre  95 e 100%:  {msg_1b}\n\n"
                f" => Probabilidade do índice de saturação ficar entre 100 e 105%:  {msg_1c}\n\n"
                f" => Probabilidade do índice de saturação ficar entre 105 e 110%:  {msg_1d}\n\n"
                f" => Probabilidade do índice de saturação ficar entre 110 e 115%:  {msg_1e}\n\n"
                f" => Probabilidade do índice de saturação ficar entre 115 e 120%:  {msg_1f}\n\n"
                f" => Probabilidade do índice de saturação ficar acima de    120%:  {msg_1g}\n"
            )
            result_label.config(text=result, wraplength=800, justify="left", font=("arial", 11))

        except ValueError:
            result_label.config(text="Erro: Por favor, insira valores válidos: ponto e não vírgula.")

    def novo_calculo():
        for entry in entries.values():
            entry.delete(0, 'end')
        result_label.config(text="Entre com os novos dados!")

    def mostrar_dicas2():
        dicas = (
            "Atenção:\n\n"
            "- Os valores de níveis e o tempo da intervenção,\n"
            "  deverão ser inseridos com duas casas decimais,\n"
            "  separadas por ponto, demais dados deverão ser\n"
            "  inseridos como sendo números inteiros.\n\n"
            "- O tempo de manobras não está incluído nos cálculos\n"
            "  de aumento do nível montante durante a intervenção.\n\n"
            "- O Nível de Montante no início da intervenção será\n"
            "  o mesmo que o Nível de Montante no término da \n"
            "  intervenção, caso não seja previsto (desejado) nenhum\n"
            "  aumento do nível do reservatório durante a intervenção.\n\n"
            "- Se precisar lançar frações de horas, lançar como o\n"
            "  o exemplo: Ao invés de digitar 08:30, digitar 8.5.\n\n"
            "- Ficar atento pois os valores a serem inseridos, possuem\n"
            "  limites máximos e mínimos.\n\n"
        )
        messagebox.showinfo("Orientações de Preenchimento", dicas, parent=sim_saturacao_fgo)

    # Configuração da janela de simulação da saturação
    sim_saturacao_fgo = Toplevel(root)
    sim_saturacao_fgo.title(
        'COG-ALUPAR - SIMULAR COMPORTAMENTO DA SATURAÇÃO DE OXIGÊNIO EM RAZÃO DE LIBERAÇÕES DE UGs NA UHE FGO')
    sim_saturacao_fgo.geometry('1200x667')
    sim_saturacao_fgo.resizable(False, False)
    sim_saturacao_fgo['bg'] = "#a4bad2"
    # Frames
    left_frame = Frame(sim_saturacao_fgo, borderwidth=1, relief="solid", bg="#a4bad2")
    left_frame.place(x=5, y=85, width=400, height=570)

    right_frame = Frame(sim_saturacao_fgo, borderwidth=1, relief="solid", bg="white")
    right_frame.place(x=400, y=85, width=790, height=570)

    right_frame_Image = PhotoImage(file="grafico1.png")
    right_frame_Image_Label = Label(right_frame, image=right_frame_Image)
    right_frame_Image_Label.image = right_frame_Image
    right_frame_Image_Label.place(x=0, y=40)

    # Títulos
    Label(sim_saturacao_fgo,
          text='Simulador para prever os índices de saturação de oxigênio durante a liberação de UGs na UHE FGO',
          font=('Arial', 14, 'bold'), bg="#024593", fg="white").place(relx=0.00, rely=0.00, width=1200, height=60)

    (Label(sim_saturacao_fgo, text="Digite os valores no quadro abaixo", bg="#a4bad2", font=("Arial", 10, "bold")).place
     (x=80, y=62))

    Label(sim_saturacao_fgo, text="Comportamento previsto dos índices de Saturação de Oxigênio em virtude da liberação",
          bg="#a4bad2", font=("Arial", 10, "bold")).place(x=550, y=62)

    # Label para exibir os resultados
    result_label = Label(right_frame, text="", justify="left", wraplength=800, anchor="w", bg='white')
    result_label.place(x=9, y=10)
    result_label.lift()

    # Campos de entrada
    campos = {
        "nam_a": "Nível Montante Início Liberação (m):",
        "nam_m": "Nível Montante Término Liberação (m):",
        "aflref": "Vazão Afluente de Referência (m³/s):",
        "tmp_int": "Tempo de intervenção em horas (h):",
        "abcs1_i": "Abertura da Comporta-1 (mm):",
        "abcs2_i": "Abertura da Comporta-2 (mm):",
        "abcs3_i": "Abertura da Comporta-3 (mm):",
        "v_vertida_i": "Vazão Vertida inicial (m³/s):",
        "ugv": "Número de UGs rodando à vazio (un):",
        "potdisp": "Potência disponível nas UGs Sincronizadas:"
    }
    entries = criar_campos(left_frame, campos, x_entry=270, y_inicial=20, y_incremento=30)

    configurar_entries_numericos()

    # Variável para armazenar a opção selecionada (1=Sonda1, 2=Sonda2, 3=Média)
    opcao_sonda = IntVar(value=1)

    Label(left_frame, text="Selecione a Sonda para Cálculo:", bg="#a4bad2", font=("Arial", 10, "bold")).place(x=10,
                                                                                                              y=330)

    # Adicionado o comando 'atualizar_imagem' em cada um
    Radiobutton(left_frame, text="Resultados com a Sonda 1", variable=opcao_sonda,
                value=1, command=atualizar_imagem, bg="#a4bad2", font=("Arial", 9)).place(x=10, y=355)

    Radiobutton(left_frame, text="Resultados com a Sonda 2", variable=opcao_sonda,
                value=2, command=atualizar_imagem, bg="#a4bad2", font=("Arial", 9)).place(x=10, y=380)

    Radiobutton(left_frame, text="Maior entre as Sondas 1 e 2", variable=opcao_sonda,
                value=3, command=atualizar_imagem, bg="#a4bad2", font=("Arial", 9)).place(x=10, y=405)

    # Botões
    Button(left_frame, text="Orientações de Preenchimento", command=mostrar_dicas2, bg="#a4bad2", fg="black",
           font=("Arial", 9)).place(relx=0.22, rely=0.78, width=200, height=25)

    Button(left_frame, text="Calcular", command=calcular, bg="#024593", fg="white",
           font=("Arial", 12, "bold")).place(relx=0.35, rely=0.85, width=120, height=30)

    Button(left_frame, text="Novo Cálculo", command=novo_calculo, bg="#FF0000", fg="white",
           font=("Arial", 12, "bold")).place(relx=0.35, rely=0.92, width=120, height=30)

    # Limites e nomes dos campos
    limites = {
        "nam_a": (19.80, 21.30),
        "nam_m": (19.80, 21.30),
        "aflref": (50, 6500),
        "tmp_int": (0.5, 60),
        "abcs1_i": (0, 13000),
        "abcs2_i": (0, 13000),
        "abcs3_i": (0, 13000),
        "v_vertida_i": (0, 7500),
        "ugv": (0, 3),
        "potdisp": (0, 252)
    }
    nomes_campos = {
        "nam_a": "Nível Montante Início Liberação",
        "nam_m": "Nível Montante Término Liberação",
        "aflref": "Vazão Afluente de Referência",
        "tmp_int": "Tempo intervenção (horas)",
        "abcs1_i": "Abertura da CS-1 inicial (mm)",
        "abcs2_i": "Abertura da CS-2 inicial (mm)",
        "abcs3_i": "Abertura da CS-3 inicial (mm)",
        "v_vertida_i": "Vazão vertida inicial",
        "ugv": "Número de UGs rodando à vazio",
        "potdisp": "Potência disponível nas UGs Sincronizadas"
    }

def cmd_click20():
    global current_user, entries, manobras

    # Criar a janela principal diretamente como a janela de simulação
    sim_nivel_fgo = Tk()
    sim_nivel_fgo.title('COG-SIMULAR CONTROLE HIDRÁULCIO DA UHE FERREIRA GOMES')
    sim_nivel_fgo.geometry('1540x820')
    sim_nivel_fgo.resizable(False, False)
    sim_nivel_fgo['bg'] = "#a4bad2"

    # Frame a esquerda para a inserção dos dados iniciais
    left_frame = Frame(sim_nivel_fgo, borderwidth=1, relief="solid", bg="#a4bad2")
    left_frame.place(x=5, y=85, width=270, height=729)

    # Frame a esquerda para a inserção das manobras e alterações
    left_frame_menor = Frame(left_frame, borderwidth=1, relief="ridge", bg="#41719C")
    left_frame_menor.place(x=5, y=320, width=258, height=325)

    # Janela da direita (text)
    right_text = Text(sim_nivel_fgo, borderwidth=1, relief="solid", bg="#F0F0F0", font=("Courier New", 10))
    right_text.place(x=280, y=115, width=1255, height=700)

    # Título
    lf1 = Label(sim_nivel_fgo, text='Simulador Hidráulico da UHE Ferreira Gomes', font=('Arial', '14', 'bold'),
                bg="#024593", fg="white")
    lf1.place(relx=0.00, rely=0.00, width=1536, height=60)

    lf = Label(sim_nivel_fgo, text="Entre com os dados iniciais", bg="#a4bad2", font=("Arial", 10, "bold"))
    lf.place(x=40, y=62)

    lf2 = Label(sim_nivel_fgo, text="Resultado da Simulação ou Manobras Realizadas", bg="#a4bad2",
                font=("Arial", 10, "bold"))
    lf2.place(x=650, y=62)

    # LABEL DO CABEÇALHO - Vamos armazenar em uma variável para poder controlar sua visibilidade
    lf3 = _tk.Label(sim_nivel_fgo,
                text="Data/Hora       |    Mont.    |  Jus.   |    HB    |  MW_U1  |  MW_U2  |  MW_U3  | UGV |    Aflu.   |    Turb.    |   Vert.    |    Defl.    |  Ab_CS1 | Ab_CS2 | Ab_CS3 |    Delta1   |   Delta2   |   Delta3   |    Var(m)",
                bg=UI_FUNDO, font=("Arial", 10))
    lf3.place(x=320, y=95)

    # INÍCIO dos Campos para inserção dos dados preliminares

    Label(left_frame, text='Data/Hora Início:', bg="#a4bad2").place(x=5, y=20, anchor=W)
    entry_data_hora = Entry(left_frame, width=30)
    entry_data_hora.place(x=140, y=20, width=110, height=20, anchor=W)

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entry_data_hora.insert(0, data_hora_atual)

    Button(left_frame, text="Sel", command=lambda: selecionar_data(entry_data_hora, "inicio")).place(x=110,
                                                                                                     y=20, height=20,
                                                                                                     anchor=W)
    Label(left_frame, text="Nível Montante Inicial (m):", bg="#a4bad2").place(x=10, y=37)
    entries["nam_1"] = Entry(left_frame, justify='center')
    entries["nam_1"].place(x=175, y=37, width=75, height=20)

    Label(left_frame, text="Nível Jusante Inicial (m):", bg="#a4bad2").place(x=10, y=60)
    entries["naj_1"] = Entry(left_frame, justify='center')
    entries["naj_1"].place(x=175, y=60, width=75, height=20)

    Label(left_frame, text="Vazão Afluente Ref (m³/s):", bg="#a4bad2").place(x=10, y=83)
    entries["aflref_1"] = Entry(left_frame, justify='center')
    entries["aflref_1"].place(x=175, y=83, width=75, height=20)

    Label(left_frame, text="Tempo Manobras (min.):", bg="#a4bad2").place(x=10, y=106)
    entries["tmp_man_1"] = Entry(left_frame, justify='center')
    entries["tmp_man_1"].place(x=175, y=106, width=75, height=20)

    Label(left_frame, text="Número UGs em MV (un):", bg="#a4bad2").place(x=10, y=129)
    entries["ugv_1"] = Entry(left_frame, justify='center')
    entries["ugv_1"].place(x=175, y=129, width=75, height=20)

    Label(left_frame, text="Vazão Vertida Inicial (m³/s):", bg="#a4bad2").place(x=10, y=152)
    entries["q_vert_1"] = Entry(left_frame, justify='center')
    entries["q_vert_1"].place(x=175, y=152, width=75, height=20)

    Label(left_frame, text="Geração UG-1 (MW):", bg="#a4bad2").place(x=10, y=175)
    entries["ger_ug1_1"] = Entry(left_frame, justify='center')
    entries["ger_ug1_1"].place(x=175, y=175, width=75, height=20)

    Label(left_frame, text="Geração UG-2 (MW):", bg="#a4bad2").place(x=10, y=198)
    entries["ger_ug2_1"] = Entry(left_frame, justify='center')
    entries["ger_ug2_1"].place(x=175, y=198, width=75, height=20)

    Label(left_frame, text="Geração UG-3 (MW):", bg="#a4bad2").place(x=10, y=221)
    entries["ger_ug3_1"] = Entry(left_frame, justify='center')
    entries["ger_ug3_1"].place(x=175, y=221, width=75, height=20)

    Label(left_frame, text="Abertura CS-1 (mm):", bg="#a4bad2").place(x=10, y=244)
    entries["abcs1_1"] = Entry(left_frame, justify='center')
    entries["abcs1_1"].place(x=175, y=244, width=75, height=20)

    Label(left_frame, text="Abertura CS-2 (mm):", bg="#a4bad2").place(x=10, y=267)
    entries["abcs2_1"] = Entry(left_frame, justify='center')
    entries["abcs2_1"].place(x=175, y=267, width=75, height=20)

    Label(left_frame, text="Abertura CS-3 (mm):", bg="#a4bad2").place(x=10, y=290)
    entries["abcs3_1"] = Entry(left_frame, justify='center')
    entries["abcs3_1"].place(x=175, y=290, width=75, height=20)

    # FIM dos Campos para inserção dos dados preliminares

    # INÍCIO da inserção de dados de Manobras e Alteração dos dados complementares

    Label(left_frame, text="Efetuar Manobras/Alterar Dados:", bg="#41719C", fg='white',
          font=('arial', '10', 'bold')).place(x=30, y=328)

    Label(left_frame, text='Hora Manobra:', bg="#41719C", fg='white').place(x=10, y=370, anchor=W)
    entries["hora_manobra"] = Entry(left_frame, width=30)
    entries["hora_manobra"].place(x=140, y=370, width=110, height=20, anchor=W)

    # Label para exibir os resultados
    result_label = Label(right_text, text="", justify="left", wraplength=800, anchor="w")
    result_label.pack(pady=10)

    # PREENCHENDO AUTOMATICAMENTE COM DATA/HORA ATUAL
    data_hora_atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")
    entries["hora_manobra"].insert(0, data_hora_atual)

    Button(left_frame, text="Sel", command=lambda: selecionar_data(entries["hora_manobra"], "manobra")).place(x=110,
                                                                                                              y=370,
                                                                                                              height=20,
                                                                                                              anchor=W)
    Label(left_frame, text="Q_Afluente      UG em MV         Temp_Man:", bg="#41719C", fg='white').place(x=20, y=390)
    entries["aflref_adc"] = Entry(left_frame, justify='center')
    entries["aflref_adc"].place(x=10, y=407, width=75, height=20)
    entries["ugv_adc"] = Entry(left_frame, justify='center')
    entries["ugv_adc"].place(x=95, y=407, width=75, height=20)
    entries["tmp_man_adc"] = Entry(left_frame, justify='center')
    entries["tmp_man_adc"].place(x=180, y=407, width=75, height=20)

    Label(left_frame, text="Geração das UGs:", bg="#41719C", fg='white').place(x=75, y=439)
    Label(left_frame, text="UG-1:", bg="#41719C", fg='white').place(x=30, y=456)
    Label(left_frame, text="UG-2:", bg="#41719C", fg='white').place(x=115, y=456)
    Label(left_frame, text="UG-3:", bg="#41719C", fg='white').place(x=205, y=456)

    entries["ger_ug1_adc"] = Entry(left_frame, justify='center')
    entries["ger_ug1_adc"].place(x=10, y=473, width=75, height=20)
    entries["ger_ug2_adc"] = Entry(left_frame, justify='center')
    entries["ger_ug2_adc"].place(x=95, y=473, width=75, height=20)
    entries["ger_ug3_adc"] = Entry(left_frame, justify='center')
    entries["ger_ug3_adc"].place(x=180, y=473, width=75, height=20)

    Label(left_frame, text="Abertura Comportas:", bg="#41719C", fg='white').place(x=75, y=508)
    Label(left_frame, text="CS-1:", bg="#41719C", fg='white').place(x=30, y=525)
    Label(left_frame, text="CS-2:", bg="#41719C", fg='white').place(x=115, y=525)
    Label(left_frame, text="CS-3:", bg="#41719C", fg='white').place(x=205, y=525)
    entries["abcs1_adc"] = Entry(left_frame, justify='center')
    entries["abcs1_adc"].place(x=10, y=542, width=75, height=20)
    entries["abcs2_adc"] = Entry(left_frame, justify='center')
    entries["abcs2_adc"].place(x=95, y=542, width=75, height=20)
    entries["abcs3_adc"] = Entry(left_frame, justify='center')
    entries["abcs3_adc"].place(x=180, y=542, width=75, height=20)

    # Variável para controlar se estamos editando uma manobra
    editando_manobra = False
    indice_edicao = None

    nomes_campos = {
        "nam_1": "Nível Montante Inicial",
        "naj_1": "Nível Jusante Inicial",
        "aflref_1": "Vazão Afluente de Referência",
        "tmp_man_1": "Tempo entre manobras (minutos)",
        "ugv_1": "Número de UGs rodando à vazio",
        "q_vert_1": "Vazão Vertida Inicial",
        "ger_ug1_1": "Geração da UG-1",
        "ger_ug2_1": "Geração da UG-2",
        "ger_ug3_1": "Geração da UG-3",
        "abcs1_1": "Abertura da Comporta 1 (mm)",
        "abcs2_1": "Abertura da Comporta 2 (mm)",
        "abcs3_1": "Abertura da Comporta 3 (mm)",
        # Campos de manobra/alteracao
        "aflref_adc": "Vazão Afluente (Manobra)",
        "ugv_adc": "UGs em MV (Manobra)",
        "tmp_man_adc": "Tempo entre manobras (Manobra)",
        "ger_ug1_adc": "Geração UG-1 (Manobra)",
        "ger_ug2_adc": "Geração UG-2 (Manobra)",
        "ger_ug3_adc": "Geração UG-3 (Manobra)",
        "abcs1_adc": "Abertura CS-1 (Manobra)",
        "abcs2_adc": "Abertura CS-2 (Manobra)",
        "abcs3_adc": "Abertura CS-3 (Manobra)"
    }

    def configurar_entries_numericos():
        """Configura todos os entries numéricos para converter vírgula em ponto automaticamente"""
        campos_numericos = [
            "nam_1", "naj_1", "aflref_1", "tmp_man_1", "ugv_1", "q_vert_1",
            "ger_ug1_1", "ger_ug2_1", "ger_ug3_1", "abcs1_1", "abcs2_1", "abcs3_1",
            "aflref_adc", "ugv_adc", "tmp_man_adc",
            "ger_ug1_adc", "ger_ug2_adc", "ger_ug3_adc",
            "abcs1_adc", "abcs2_adc", "abcs3_adc"
        ]

        for campo in campos_numericos:
            if campo in entries:
                entries[campo].bind("<KeyRelease>",
                                    lambda e, entry=entries[campo]: formatar_numero(e, entry))


    # Função para formatar número substituindo vírgula por ponto
    def formatar_numero(event, entry):
        """Substitui vírgula por ponto enquanto o usuário digita"""
        if ',' in entry.get():
            valor = entry.get().replace(',', '.')
            entry.delete(0, END)
            entry.insert(0, valor)

    def validar_entradas():
        # Definir os limites mínimos e máximos para cada campo
        limites = {
            "nam_1": (19.80, 21.30),
            "naj_1": (1.45, 7.00),
            "aflref_1": (0, 10000),
            "tmp_man_1": (3, 60),
            "ugv_1": (0, 3),
            "tmp_man_adc": (3, 60),
            "q_vert_1": (0, 8000),
            "ger_ug1_1": (0, 84),
            "ger_ug2_1": (0, 84),
            "ger_ug3_1": (0, 84),
            "abcs1_1": (0, 13001),
            "abcs2_1": (0, 13001),
            "abcs3_1": (0, 13001),
            # Campos de manobra/alteracao
            "aflref_adc": (0, 10000),
            "ugv_adc": (0, 3),
            "ger_ug1_adc": (0, 84),
            "ger_ug2_adc": (0, 84),
            "ger_ug3_adc": (0, 84),
            "abcs1_adc": (0, 13001),
            "abcs2_adc": (0, 13001),
            "abcs3_adc": (0, 13001)
        }
        # Campos que não devem ser validados (porque não são numéricos)
        campos_nao_validar = ["hora_manobra"]

        campo_com_erro = None

        for key, entry in entries.items():
            # Pular campos que não devem ser validados
            if key in campos_nao_validar:
                continue

            # Validar apenas campos que estão nos limites e não estão vazios
            if key in limites and entry.get().strip():
                try:
                    # Substituir vírgula por ponto antes da conversão
                    valor_str = entry.get().strip().replace(',', '.')
                    valor = float(valor_str)
                    minimo, maximo = limites[key]
                    if not (minimo <= valor <= maximo):
                        campo_com_erro = key
                        messagebox.showerror("Erro",
                                             f"Valor fora do intervalo permitido para {nomes_campos.get(key, key)}: {minimo} a {maximo}",
                                             parent=sim_nivel_fgo)
                        # Focar no campo com erro
                        entry.focus_set()
                        entry.select_range(0, END)
                        return False
                    # Se chegou aqui, o valor é válido, então atualiza o campo com o valor corrigido
                    # (substituindo vírgula por ponto se necessário)
                    if ',' in entry.get():
                        entry.delete(0, END)
                        entry.insert(0, valor_str)
                except ValueError:
                    campo_com_erro = key
                    messagebox.showerror("Erro",
                                         f"Valor inválido para {nomes_campos.get(key, key)}. Use ponto ao invés de vírgula.",
                                         parent=sim_nivel_fgo)
                    # Focar no campo com erro e selecionar o texto para facilitar a correção
                    entry.focus_set()
                    entry.select_range(0, END)
                    return False
        return True

    def limpar_campos_manobra():
        """Limpa apenas os campos de valores das manobras, mantendo a data/hora"""
        entries["aflref_adc"].delete(0, END)
        entries["ugv_adc"].delete(0, END)
        entries["tmp_man_adc"].delete(0, END)
        entries["ger_ug1_adc"].delete(0, END)
        entries["ger_ug2_adc"].delete(0, END)
        entries["ger_ug3_adc"].delete(0, END)
        entries["abcs1_adc"].delete(0, END)
        entries["abcs2_adc"].delete(0, END)
        entries["abcs3_adc"].delete(0, END)

    def preencher_campos_para_edicao(manobra):
        """Preenche os campos com os dados da manobra selecionada para edição com formatação específica"""
        entries["hora_manobra"].delete(0, END)
        entries["hora_manobra"].insert(0, manobra["hora"].strftime("%d/%m/%Y - %H:%Mh"))

        # Função auxiliar para formatar valores conforme o campo
        def formatar_para_entry(valor, nome_campo):
            """
            Formata o valor para exibição no entry conforme o tipo de campo:
            - UG-1, UG-2, UG-3: 2 casas decimais
            - Demais campos numéricos (aflref_adc, ugv_adc, tmp_man_adc, CS): sem casas decimais (inteiros)
            """
            if valor is None:
                return ""

            # Para campos das UGs (deve ter 2 casas decimais)
            if nome_campo in ['ger_ug1_adc', 'ger_ug2_adc', 'ger_ug3_adc']:
                if isinstance(valor, (int, float)):
                    return f"{valor:.2f}"
                return str(valor)

            # Para os demais campos numéricos (aflref, ugv, tmp_man, CS) - SEM casas decimais
            if isinstance(valor, (int, float)):
                # Arredonda para inteiro mais próximo
                return f"{int(round(valor))}"

            return str(valor)

        # Preencher cada campo com a formatação adequada
        # Q_Afluente - SEM casas decimais
        if manobra.get("aflref") is not None:
            entries["aflref_adc"].delete(0, END)
            entries["aflref_adc"].insert(0, formatar_para_entry(manobra["aflref"], "aflref_adc"))

        # UGs em MV - SEM casas decimais
        if manobra.get("ugv") is not None:
            entries["ugv_adc"].delete(0, END)
            entries["ugv_adc"].insert(0, formatar_para_entry(manobra["ugv"], "ugv_adc"))

        # Tempo de Manobra - SEM casas decimais
        if manobra.get("tmp_man") is not None:
            entries["tmp_man_adc"].delete(0, END)
            entries["tmp_man_adc"].insert(0, formatar_para_entry(manobra["tmp_man"], "tmp_man_adc"))

        # Campos UG - COM 2 casas decimais
        if manobra.get("ger_ug1") is not None:
            entries["ger_ug1_adc"].delete(0, END)
            entries["ger_ug1_adc"].insert(0, formatar_para_entry(manobra["ger_ug1"], "ger_ug1_adc"))

        if manobra.get("ger_ug2") is not None:
            entries["ger_ug2_adc"].delete(0, END)
            entries["ger_ug2_adc"].insert(0, formatar_para_entry(manobra["ger_ug2"], "ger_ug2_adc"))

        if manobra.get("ger_ug3") is not None:
            entries["ger_ug3_adc"].delete(0, END)
            entries["ger_ug3_adc"].insert(0, formatar_para_entry(manobra["ger_ug3"], "ger_ug3_adc"))

        # Campos CS - SEM casas decimais
        if manobra.get("abcs1") is not None:
            entries["abcs1_adc"].delete(0, END)
            entries["abcs1_adc"].insert(0, formatar_para_entry(manobra["abcs1"], "abcs1_adc"))

        if manobra.get("abcs2") is not None:
            entries["abcs2_adc"].delete(0, END)
            entries["abcs2_adc"].insert(0, formatar_para_entry(manobra["abcs2"], "abcs2_adc"))

        if manobra.get("abcs3") is not None:
            entries["abcs3_adc"].delete(0, END)
            entries["abcs3_adc"].insert(0, formatar_para_entry(manobra["abcs3"], "abcs3_adc"))

    def adicionar_ou_atualizar_manobra():
        """Adiciona uma nova manobra ou atualiza uma existente com validação"""
        nonlocal editando_manobra, indice_edicao

        try:
            # Verificar se pelo menos um campo de alteração foi preenchido
            campos_alteracao = [
                entries["aflref_adc"].get(),
                entries["ugv_adc"].get(),
                entries["tmp_man_adc"].get(),
                entries["ger_ug1_adc"].get(),
                entries["ger_ug2_adc"].get(),
                entries["ger_ug3_adc"].get(),
                entries["abcs1_adc"].get(),
                entries["abcs2_adc"].get(),
                entries["abcs3_adc"].get()
            ]

            if not any(campos_alteracao):
                messagebox.showwarning("Aviso", "Nenhum dado de alteração foi preenchido!", parent=sim_nivel_fgo)
                return

            # Obter a hora da manobra
            hora_manobra_str = entries["hora_manobra"].get().strip()
            try:
                hora_manobra = datetime.strptime(hora_manobra_str, "%d/%m/%Y - %H:%Mh")
            except ValueError:
                messagebox.showerror("Erro", "Formato de data/hora inválido. Use DD/MM/AAAA - HH:MMh",
                                     parent=sim_nivel_fgo)
                return

            # Criar dicionário com as alterações e validar cada campo
            alteracao = {
                "hora": hora_manobra,
                "aflref": None,
                "ugv": None,
                "tmp_man": None,
                "ger_ug1": None,
                "ger_ug2": None,
                "ger_ug3": None,
                "abcs1": None,
                "abcs2": None,
                "abcs3": None
            }

            # Validar e preencher cada campo com seus limites específicos
            # Campo: Q_Afluente - ARMazenar como inteiro
            if entries["aflref_adc"].get():
                try:
                    valor = float(entries["aflref_adc"].get().replace(',', '.'))
                    if valor < 0 or valor > 8000:
                        messagebox.showerror("Erro",
                                             f"Q_Afluente fora do intervalo permitido: 0 a 8000 m³/s\nValor informado: {valor}",
                                             parent=sim_nivel_fgo)
                        entries["aflref_adc"].focus_set()
                        entries["aflref_adc"].select_range(0, END)
                        return
                    # Converte para inteiro (SEM casas decimais)
                    alteracao["aflref"] = int(round(valor))
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para Q_Afluente. Use números!", parent=sim_nivel_fgo)
                    entries["aflref_adc"].focus_set()
                    return

            # Campo: UGs em MV - ARMAZENAR como inteiro
            if entries["ugv_adc"].get():
                try:
                    valor = float(entries["ugv_adc"].get().replace(',', '.'))
                    if valor < 0 or valor > 3:
                        messagebox.showerror("Erro",
                                             f"UGs em MV fora do intervalo permitido: 0 a 3 unidades\nValor informado: {valor}",
                                             parent=sim_nivel_fgo)
                        entries["ugv_adc"].focus_set()
                        entries["ugv_adc"].select_range(0, END)
                        return
                    # Converte para inteiro (SEM casas decimais)
                    alteracao["ugv"] = int(round(valor))
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para UGs em MV. Use números!", parent=sim_nivel_fgo)
                    entries["ugv_adc"].focus_set()
                    return

            # Campo: Tempo de Manobra - ARMAZENAR como inteiro
            if entries["tmp_man_adc"].get():
                try:
                    valor = float(entries["tmp_man_adc"].get().replace(',', '.'))
                    if valor < 3 or valor > 60:
                        messagebox.showerror("Erro",
                                             f"Tempo de Manobra fora do intervalo permitido: 3 a 60 minutos\nValor informado: {valor}",
                                             parent=sim_nivel_fgo)
                        entries["tmp_man_adc"].focus_set()
                        entries["tmp_man_adc"].select_range(0, END)
                        return
                    # Converte para inteiro (SEM casas decimais)
                    alteracao["tmp_man"] = int(round(valor))
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para Tempo de Manobra. Use números!",
                                         parent=sim_nivel_fgo)
                    entries["tmp_man_adc"].focus_set()
                    return

            # Campo: Geração UG-1 (COM 2 casas decimais)
            if entries["ger_ug1_adc"].get():
                try:
                    valor = float(entries["ger_ug1_adc"].get().replace(',', '.'))
                    if valor < 0 or valor > 84:
                        messagebox.showerror("Erro",
                                             f"Geração UG-1 fora do intervalo permitido: 0 a 84 MW\nValor informado: {valor}",
                                             parent=sim_nivel_fgo)
                        entries["ger_ug1_adc"].focus_set()
                        entries["ger_ug1_adc"].select_range(0, END)
                        return
                    # Mantém o valor com 2 casas decimais
                    alteracao["ger_ug1"] = round(valor, 2)
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para Geração UG-1. Use números!", parent=sim_nivel_fgo)
                    entries["ger_ug1_adc"].focus_set()
                    return

            # Campo: Geração UG-2 (COM 2 casas decimais)
            if entries["ger_ug2_adc"].get():
                try:
                    valor = float(entries["ger_ug2_adc"].get().replace(',', '.'))
                    if valor < 0 or valor > 84:
                        messagebox.showerror("Erro",
                                             f"Geração UG-2 fora do intervalo permitido: 0 a 84 MW\nValor informado: {valor}",
                                             parent=sim_nivel_fgo)
                        entries["ger_ug2_adc"].focus_set()
                        entries["ger_ug2_adc"].select_range(0, END)
                        return
                    # Mantém o valor com 2 casas decimais
                    alteracao["ger_ug2"] = round(valor, 2)
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para Geração UG-2. Use números!", parent=sim_nivel_fgo)
                    entries["ger_ug2_adc"].focus_set()
                    return

            # Campo: Geração UG-3 (COM 2 casas decimais)
            if entries["ger_ug3_adc"].get():
                try:
                    valor = float(entries["ger_ug3_adc"].get().replace(',', '.'))
                    if valor < 0 or valor > 84:
                        messagebox.showerror("Erro",
                                             f"Geração UG-3 fora do intervalo permitido: 0 a 84 MW\nValor informado: {valor}",
                                             parent=sim_nivel_fgo)
                        entries["ger_ug3_adc"].focus_set()
                        entries["ger_ug3_adc"].select_range(0, END)
                        return
                    # Mantém o valor com 2 casas decimais
                    alteracao["ger_ug3"] = round(valor, 2)
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para Geração UG-3. Use números!", parent=sim_nivel_fgo)
                    entries["ger_ug3_adc"].focus_set()
                    return

            # Campo: Abertura CS-1
            if entries["abcs1_adc"].get():
                try:
                    valor = float(entries["abcs1_adc"].get().replace(',', '.'))
                    if valor < 0 or valor > 15000:
                        messagebox.showerror("Erro",
                                             f"Abertura CS-1 fora do intervalo permitido: 0 a 15000 mm\nValor informado: {valor}",
                                             parent=sim_nivel_fgo)
                        entries["abcs1_adc"].focus_set()
                        entries["abcs1_adc"].select_range(0, END)
                        return
                    # Converte para inteiro (sem casas decimais)
                    alteracao["abcs1"] = int(round(valor))
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para Abertura CS-1. Use números!",
                                         parent=sim_nivel_fgo)
                    entries["abcs1_adc"].focus_set()
                    return

            # Campo: Abertura CS-2
            if entries["abcs2_adc"].get():
                try:
                    valor = float(entries["abcs2_adc"].get().replace(',', '.'))
                    if valor < 0 or valor > 15000:
                        messagebox.showerror("Erro",
                                             f"Abertura CS-2 fora do intervalo permitido: 0 a 15000 mm\nValor informado: {valor}",
                                             parent=sim_nivel_fgo)
                        entries["abcs2_adc"].focus_set()
                        entries["abcs2_adc"].select_range(0, END)
                        return
                    # Converte para inteiro (sem casas decimais)
                    alteracao["abcs2"] = int(round(valor))
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para Abertura CS-2. Use números!",
                                         parent=sim_nivel_fgo)
                    entries["abcs2_adc"].focus_set()
                    return

            # Campo: Abertura CS-3
            if entries["abcs3_adc"].get():
                try:
                    valor = float(entries["abcs3_adc"].get().replace(',', '.'))
                    if valor < 0 or valor > 15000:
                        messagebox.showerror("Erro",
                                             f"Abertura CS-3 fora do intervalo permitido: 0 a 15000 mm\nValor informado: {valor}",
                                             parent=sim_nivel_fgo)
                        entries["abcs3_adc"].focus_set()
                        entries["abcs3_adc"].select_range(0, END)
                        return
                    # Converte para inteiro (sem casas decimais)
                    alteracao["abcs3"] = int(round(valor))
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para Abertura CS-3. Use números!",
                                         parent=sim_nivel_fgo)
                    entries["abcs3_adc"].focus_set()
                    return

            # Se chegou aqui, todos os campos estão válidos
            if editando_manobra and indice_edicao is not None:
                # Atualizar manobra existente
                manobras[indice_edicao] = alteracao
                manobras.sort(key=lambda x: x["hora"])
                messagebox.showinfo("Sucesso", "Manobra atualizada com sucesso!", parent=sim_nivel_fgo)
                # Resetar modo de edição
                editando_manobra = False
                indice_edicao = None
                # Mudar texto do botão de volta para "Salvar"
                btn_salvar.config(text="Salvar")
                # Remover botão cancelar se existir
                if hasattr(ver_dados, 'btn_cancelar'):
                    ver_dados.btn_cancelar.destroy()
                    delattr(ver_dados, 'btn_cancelar')
            else:
                # Verificar duplicata
                chave_unica = (
                    hora_manobra,
                    alteracao.get("aflref"),
                    alteracao.get("ugv"),
                    alteracao.get("tmp_man"),
                    alteracao.get("ger_ug1"),
                    alteracao.get("ger_ug2"),
                    alteracao.get("ger_ug3"),
                    alteracao.get("abcs1"),
                    alteracao.get("abcs2"),
                    alteracao.get("abcs3")
                )

                ja_existe = any(
                    (m["hora"] == chave_unica[0] and
                     m.get("aflref") == chave_unica[1] and
                     m.get("ugv") == chave_unica[2] and
                     m.get("tmp_man") == chave_unica[3] and
                     m.get("ger_ug1") == chave_unica[4] and
                     m.get("ger_ug2") == chave_unica[5] and
                     m.get("ger_ug3") == chave_unica[6] and
                     m.get("abcs1") == chave_unica[7] and
                     m.get("abcs2") == chave_unica[8] and
                     m.get("abcs3") == chave_unica[9])
                    for m in manobras
                )

                if not ja_existe:
                    manobras.append(alteracao)
                    manobras.sort(key=lambda x: x["hora"])
                    messagebox.showinfo("Sucesso", "Manobra/alteracao salva com sucesso!", parent=sim_nivel_fgo)
                else:
                    messagebox.showwarning("Aviso", "Esta manobra já foi registrada anteriormente!",
                                           parent=sim_nivel_fgo)

            # Limpar apenas os campos de VALORES, manter a DATA/HORA
            entries["aflref_adc"].delete(0, END)
            entries["ugv_adc"].delete(0, END)
            entries["tmp_man_adc"].delete(0, END)
            entries["ger_ug1_adc"].delete(0, END)
            entries["ger_ug2_adc"].delete(0, END)
            entries["ger_ug3_adc"].delete(0, END)
            entries["abcs1_adc"].delete(0, END)
            entries["abcs2_adc"].delete(0, END)
            entries["abcs3_adc"].delete(0, END)

        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {e}", parent=sim_nivel_fgo)

    def cancelar_edicao():
        """Cancela a edição atual e limpa os campos, mas mantém a data/hora"""
        nonlocal editando_manobra, indice_edicao
        editando_manobra = False
        indice_edicao = None

        # Limpa apenas os campos de valores, mantém a data/hora
        entries["aflref_adc"].delete(0, END)
        entries["ugv_adc"].delete(0, END)
        entries["tmp_man_adc"].delete(0, END)
        entries["ger_ug1_adc"].delete(0, END)
        entries["ger_ug2_adc"].delete(0, END)
        entries["ger_ug3_adc"].delete(0, END)
        entries["abcs1_adc"].delete(0, END)
        entries["abcs2_adc"].delete(0, END)
        entries["abcs3_adc"].delete(0, END)

        # NÃO alterar a data/hora

        btn_salvar.config(text="Salvar")
        if hasattr(ver_dados, 'btn_cancelar'):
            ver_dados.btn_cancelar.destroy()
            delattr(ver_dados, 'btn_cancelar')
        messagebox.showinfo("Info", "Edição cancelada!", parent=sim_nivel_fgo)

    # FUNÇÃO PARA SELECIONAR DATA E HORA
    # ---------------------------------------------------
    def selecionar_data(entry, tipo):
        def salvar_data():
            data_selecionada = cal.selection_get().strftime('%d/%m/%Y')
            hora_atual = datetime.now().strftime('%H:%M')
            if tipo == "inicio":
                entry.delete(0, END)
                entry.insert(0, f"{data_selecionada} - {hora_atual}h")
            else:
                entry.delete(0, END)
                entry.insert(0, f"{data_selecionada} - {hora_atual}h")

            janela_cal.destroy()

        janela_cal = Toplevel(sim_nivel_fgo)
        janela_cal.title("Selecione a Data")
        cal = Calendar(janela_cal, selectmode='day', date_pattern='dd-mm-yyyy')
        cal.pack(pady=20)

        Button(janela_cal, text="Salvar", command=salvar_data).pack(pady=10)

    def gerenciar_manobras():
        """Abre uma janela com Treeview para gerenciar todas as manobras"""
        if not manobras:
            messagebox.showinfo("Info", "Nenhuma manobra cadastrada ainda!", parent=sim_nivel_fgo)
            return

        # Criar janela de gerenciamento
        janela_gerenciar = Toplevel(sim_nivel_fgo)
        janela_gerenciar.title("Gerenciar Manobras - UHE Ferreira Gomes")
        janela_gerenciar.geometry("1200x500")
        janela_gerenciar.resizable(True, True)

        # Frame principal
        main_frame = Frame(janela_gerenciar)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Treeview com scrollbars
        tree_frame = Frame(main_frame)
        tree_frame.pack(fill=BOTH, expand=True)

        scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
        scroll_x = Scrollbar(tree_frame, orient=HORIZONTAL)

        # Definir colunas
        colunas = ("#", "Data/Hora", "Q_Afluente", "UGs_MV", "Tmp_Man",
                   "UG-1", "UG-2", "UG-3", "CS-1", "CS-2", "CS-3")

        tree = ttk.Treeview(tree_frame, columns=colunas, show="headings",
                            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        tree.pack(fill=BOTH, expand=True)

        # Configurar cabeçalhos
        larguras = {"#": 40, "Data/Hora": 150, "Q_Afluente": 100, "UGs_MV": 80,
                    "Tmp_Man": 80, "UG-1": 80, "UG-2": 80, "UG-3": 80,
                    "CS-1": 80, "CS-2": 80, "CS-3": 80}

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=larguras.get(col, 100), anchor="center")

        # Função auxiliar para formatar valores com regras específicas
        def formatar_valor(valor, nome_campo):
            """
            Formata o valor conforme o tipo de campo:
            - UG-1, UG-2, UG-3: 2 casas decimais
            - Demais campos numéricos: sem casas decimais (inteiros)
            """
            if valor is None:
                return "-"

            # Verifica se é um campo das UGs (deve ter 2 casas decimais)
            if nome_campo in ['UG-1', 'UG-2', 'UG-3']:
                if isinstance(valor, (int, float)):
                    return f"{valor:.2f}"
                return str(valor)

            # Para os demais campos numéricos (sem casas decimais)
            if isinstance(valor, (int, float)):
                # Arredonda para inteiro mais próximo
                return f"{int(round(valor))}"

            return str(valor)

        # Preencher dados
        for idx, manobra in enumerate(manobras, 1):
            valores = [
                idx,
                manobra['hora'].strftime('%d/%m/%Y %H:%M'),
                formatar_valor(manobra.get('aflref'), 'Q_Afluente'),
                formatar_valor(manobra.get('ugv'), 'UGs_MV'),
                formatar_valor(manobra.get('tmp_man'), 'Tmp_Man'),
                formatar_valor(manobra.get('ger_ug1'), 'UG-1'),
                formatar_valor(manobra.get('ger_ug2'), 'UG-2'),
                formatar_valor(manobra.get('ger_ug3'), 'UG-3'),
                formatar_valor(manobra.get('abcs1'), 'CS-1'),
                formatar_valor(manobra.get('abcs2'), 'CS-2'),
                formatar_valor(manobra.get('abcs3'), 'CS-3')
            ]
            tree.insert("", END, values=valores, iid=idx - 1)

        # Frame de botões (CORRIGIDO: agora é criado corretamente)
        botoes_frame = Frame(main_frame)
        botoes_frame.pack(fill=X, pady=10)

        def editar_selecionado():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione uma manobra para editar!", parent=janela_gerenciar)
                return

            nonlocal editando_manobra, indice_edicao
            indice = int(selecionado[0])
            manobra = manobras[indice]

            # Preencher campos para edição
            preencher_campos_para_edicao(manobra)
            editando_manobra = True
            indice_edicao = indice
            btn_salvar.config(text="Atualizar")

            # Criar botão cancelar se não existir
            if not hasattr(ver_dados, 'btn_cancelar'):
                btn_cancelar = Button(left_frame, text="Cancelar", command=cancelar_edicao,
                                      bg="#024593", fg="white", font=("Arial", 9))
                btn_cancelar.place(relx=0.28, rely=0.80, width=55, height=22)
                ver_dados.btn_cancelar = btn_cancelar

            janela_gerenciar.destroy()
            messagebox.showinfo("Edição", "Dados carregados! Corrija os campos e clique em 'Atualizar'",
                                parent=sim_nivel_fgo)

        def excluir_selecionado():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione uma manobra para excluir!", parent=janela_gerenciar)
                return

            indice = int(selecionado[0])
            manobra = manobras[indice]

            if messagebox.askyesno("Confirmar",
                                   f"Deseja realmente excluir a manobra do dia:\n{manobra['hora'].strftime('%d/%m/%Y %H:%M')}?",
                                   parent=janela_gerenciar):
                del manobras[indice]
                messagebox.showinfo("Sucesso", "Manobra excluída com sucesso!", parent=janela_gerenciar)
                janela_gerenciar.destroy()

        def excluir_todas():
            if messagebox.askyesno("Confirmar",
                                   "Deseja realmente EXCLUIR TODAS as manobras?\n\nEsta ação não pode ser desfeita!",
                                   parent=janela_gerenciar):
                global manobras
                manobras = []
                messagebox.showinfo("Sucesso", "Todas as manobras foram excluídas!", parent=janela_gerenciar)
                janela_gerenciar.destroy()

        # Botões de ação (CORRIGIDO: usando botoes_frame em vez de btn_frame)
        btn_editar = Button(botoes_frame, text="✏️ Editar Selecionada", command=editar_selecionado,
                            bg="#024593", fg="white", font=("Arial", 10), padx=20)
        btn_editar.pack(side=LEFT, padx=5)

        btn_excluir = Button(botoes_frame, text="🗑️ Excluir Selecionada", command=excluir_selecionado,
                             bg="#FF0000", fg="white", font=("Arial", 10), padx=20)
        btn_excluir.pack(side=LEFT, padx=5)

        btn_excluir_todas = Button(botoes_frame, text="⚠️ Excluir Todas", command=excluir_todas,
                                   bg="#8B0000", fg="white", font=("Arial", 10), padx=20)
        btn_excluir_todas.pack(side=LEFT, padx=5)

        btn_fechar = Button(botoes_frame, text="Fechar", command=janela_gerenciar.destroy,
                            bg="#808080", fg="white", font=("Arial", 10), padx=20)
        btn_fechar.pack(side=RIGHT, padx=5)

        # Label com informações
        lbl_info = Label(main_frame, text=f"Total de manobras cadastradas: {len(manobras)}",
                         font=("Arial", 10, "bold"), fg="blue")
        lbl_info.pack(pady=5)

    def aplicar_manobras(resultados):
        if not resultados:
            return resultados

        vaz_acumul = 46.5
        produtibi = 0.008979
        foi_pro_brejo = False

        # 1. ESTADO INICIAL (Baseado na primeira linha do grid)
        est = {
            "ug1": (resultados[0].get("ger_ug1") or 0.0),
            "ug2": (resultados[0].get("ger_ug2") or 0.0),
            "ug3": (resultados[0].get("ger_ug3") or 0.0),
            "aflu": (resultados[0].get("aflref") or 0.0),
            "c1": (resultados[0].get("abcs1") or 0.0),
            "c2": (resultados[0].get("abcs2") or 0.0),
            "c3": (resultados[0].get("abcs3") or 0.0),
            "ugv": (resultados[0].get("ugv") or 0.0)
        }

        # Ordenamos as manobras pela data e hora completa para evitar confusão na virada do dia
        manobras_ordenadas = sorted(manobras, key=lambda x: x["hora"])

        for i in range(len(resultados)):
            res = resultados[i]
            # 'res_hora' aqui é um objeto datetime completo (Ex: 2024-05-02 02:05:00)
            res_hora = datetime.strptime(res['hora'], "%d/%m/%Y %H:%M")

            if foi_pro_brejo:
                for k in res:
                    if k != "hora": res[k] = 0.0
                continue

            # 2. ATUALIZAÇÃO DINÂMICA DO ESTADO
            # Varremos as manobras. Se a data/hora da manobra já passou ou é agora, o estado muda.
            for m in manobras_ordenadas:
                # m["hora"] já deve ser um objeto datetime.
                # A comparação abaixo considera Dia, Mês, Ano, Hora e Minuto.
                if res_hora >= m["hora"]:
                    if m.get("ger_ug1") is not None: est["ug1"] = m["ger_ug1"]
                    if m.get("ger_ug2") is not None: est["ug2"] = m["ger_ug2"]
                    if m.get("ger_ug3") is not None: est["ug3"] = m["ger_ug3"]
                    if m.get("aflref") is not None: est["aflu"] = m["aflref"]
                    if m.get("abcs1") is not None: est["c1"] = m["abcs1"]
                    if m.get("abcs2") is not None: est["c2"] = m["abcs2"]
                    if m.get("abcs3") is not None: est["c3"] = m["abcs3"]
                    if m.get("ugv") is not None: est["ugv"] = m["ugv"]
                else:
                    # Como estão ordenadas, se esta manobra é no futuro, as próximas também são.
                    break

            # 3. CÁLCULO HIDRÁULICO (Com os valores vigentes no 'est')
            ger_total = float(est["ug1"] + est["ug2"] + est["ug3"])
            nam_atual = float(res.get("nam") or 0.0)

            # Referência de NAJ anterior para o cálculo do HB inicial
            naj_ant = resultados[i - 1]["naj"] if i > 0 else (res.get("naj") or 1.61)
            hb_est = nam_atual - naj_ant

            # Se o HB cair abaixo de 5, a usina para (independente do dia/hora)
            if hb_est < 9.0 and i > 0:
                foi_pro_brejo = True
                for k in res:
                    if k != "hora": res[k] = 0.0
                continue

            # Vazões calculadas com a abertura de comportas e geração do 'est'
            qv = calcular_vazao_vertida_simplificada(est["c1"], est["c2"], est["c3"], nam_atual)
            qt = (ger_total / hb_est / produtibi) + (est["ugv"] * 60) if hb_est > 0 else 0.0
            qd = qv + qt

            # Níveis resultantes
            naj_real = round((1.607 + 0.002402 * qd -
                              0.0000006697 * qd ** 2 +
                              0.00000000008349 * qd ** 3), 2)

            hb_real = round(nam_atual - naj_real, 2)

            # Validação de segurança final
            if hb_real < 9.0:
                foi_pro_brejo = True
                for k in res:
                    if k != "hora": res[k] = 0.0
                continue

            # 4. ATUALIZAÇÃO DA LINHA E PROPAGAÇÃO DO NÍVEL
            res.update({
                "ger_ug1": est["ug1"], "ger_ug2": est["ug2"], "ger_ug3": est["ug3"],
                "geracao_total": ger_total,
                "abcs1": est["c1"], "abcs2": est["c2"], "abcs3": est["c3"],
                "aflref": est["aflu"], "ugv": est["ugv"],
                "q_vert": qv, "q_turb": qt, "q_defl": qd,
                "naj": naj_real, "hb": hb_real
            })

            # Variação do NAM baseada na Afluência do 'est' e Defluência calculada
            res["var_nivel"] = (est["aflu"] - qd) / vaz_acumul / 100

            # Propaga o novo NAM para a próxima linha do tempo
            if i + 1 < len(resultados):
                resultados[i + 1]["nam"] = round(nam_atual + res["var_nivel"], 4)

        return resultados

    def calcular_linhas_por_hora(tmp_man):
        """Calcula quantas linhas correspondem a 1 hora com base no tmp_man"""
        if tmp_man <= 0:
            return 0  # Evita divisão por zero
        return int(60 / tmp_man)

    def calcular_vazao_vertida_simplificada(abertura_cs1, abertura_cs2, abertura_cs3, nam):

        def calcular_termo(abertura, nam):
            """Função auxiliar para evitar repetição de código"""
            if 0 <= abertura <= 1000:
                coeficiente = (-0.2857 * nam ** 2 + 24.6 * nam + 114.53) / 3
            elif 1000 < abertura <= 2000:
                coeficiente = (-0.2143 * nam ** 2 + 22.3 * nam + 138.24) / 3
            elif 2000 < abertura <= 3000:
                coeficiente = (-0.1667 * nam ** 2 + 20.933 * nam + 150.4) / 3
            elif 3000 < abertura <= 4000:
                coeficiente = (-0.1964 * nam ** 2 + 22.7 * nam + 129.43) / 3
            elif 4000 < abertura <= 5000:
                coeficiente = (-0.2286 * nam ** 2 + 24.44 * nam + 108.8) / 3
            elif 5000 < abertura <= 6000:
                coeficiente = (-0.2381 * nam ** 2 + 25.3 * nam + 94.236) / 3
            elif 6000 < abertura <= 7000:
                coeficiente = (-0.2551 * nam ** 2 + 26.429 * nam + 77.364) / 3
            elif 7000 < abertura <= 8000:
                coeficiente = (-0.2589 * nam ** 2 + 27.1 * nam + 63.665) / 3
            elif 8000 < abertura <= 9000:
                coeficiente = (-0.2937 * nam ** 2 + 29.0 * nam + 37.32) / 3
            elif 9000 < abertura <= 10000:
                coeficiente = (-0.3071 * nam ** 2 + 30.06 * nam + 18.887) / 3
            elif 10000 < abertura <= 11000:
                coeficiente = (-0.3247 * nam ** 2 + 31.309 * nam - 1.8388) / 3
            elif 11000 < abertura <= 12000:
                coeficiente = (-0.3333 * nam ** 2 + 32.2 * nam - 19.38) / 3
            else:
                coeficiente = (-0.321 * nam ** 2 + 31.691 * nam - 14.156) / 3

            return (abertura * coeficiente) / 1000

        try:
            # Calcula termos individualmente
            termo1 = calcular_termo(abertura_cs1, nam)
            termo2 = calcular_termo(abertura_cs2, nam)
            termo3 = calcular_termo(abertura_cs3, nam)

            q_vert = termo1 + termo2 + termo3
            return max(0, q_vert)

        except Exception as e:
            print(f"Erro no cálculo: {e}")
            return 0

    def verificar_nivel(nam):
        """Retorna True se o nível estiver fora dos limites operacionais"""
        return nam > 21.30 or nam < 19.80

    def atualizar_texto_resultados():
        """Lê a lista global de resultados e renderiza no widget de texto"""
        global resultados, manobras

        # 1. Limpa o campo de texto antes de escrever
        right_text.delete(1.0, END)

        # 2. Configura as cores (Tags)
        right_text.tag_config("alerta", foreground="red", font=("Courier New", 10, "bold"))
        right_text.tag_config("delta_baixo", foreground="red")

        # 3. Recupera o tmp_man inicial para as divisórias
        try:
            tmp_man_atual = float(entries["tmp_man_1"].get())
        except:
            tmp_man_atual = 30  # Valor padrão caso erro

        contador_linhas = 0

        # Mapeamento de mudanças de tempo para divisórias
        tempos_manobras = {m["hora"]: m["tmp_man"] for m in manobras if m.get("tmp_man") is not None}

        for i, res in enumerate(resultados):
            # Verifica se nesta hora houve mudança de tmp_man por manobra
            res_hora_dt = datetime.strptime(res['hora'], "%d/%m/%Y %H:%M")
            if res_hora_dt in tempos_manobras:
                tmp_man_atual = tempos_manobras[res_hora_dt]
                right_text.insert(END, "-" * 155 + " MANOBRA DE TEMPO\n")
                contador_linhas = 0  # Reinicia contador para a nova frequência de divisórias

            # Formatação da linha (Strings com largura fixa)
            # :<15 (esquerda), :>6.2f (direita, 2 decimais), :^8 (centro)
            linha = (
                f"{res['hora']:<16} "
                f"{res['nam']:>6.2f} {res['naj']:>5.2f} {res['hb']:>6.2f} "
                f"{res['ger_ug1']:>6.2f} {res['ger_ug2']:>8.2f} {res['ger_ug3']:>7.2f} "
                f"{res['ugv']:>4.0f} "
                f"{res['aflref']:>6.0f} {res['q_turb']:>7.0f} {res['q_vert']:>6.0f} {res['q_defl']:>7.0f} "
                f"{res['abcs1']:>7.0f} {res['abcs2']:>7.0f} {res['abcs3']:>6.0f} "
                f"{res['delta_cs1_real']:>7.2f} {res['delta_cs2_real']:>7.2f} {res['delta_cs3_real']:>7.2f} "
                f"{res['var_nivel']:>+9.3f}\n"
            )

            # 4. Lógica de aplicação de Cores
            tags_aplicar = []

            # Alerta de Nível Operacional (NAM fora de 19.80 - 21.30)
            # Note: ignoramos se for 0.0 (estado crítico já desligado)
            if res['nam'] > 0 and (res['nam'] < 19.80 or res['nam'] > 21.30):
                tags_aplicar.append("alerta")

            # Alerta de Delta (Distância da soleira/composta)
            if 0 < res['delta_cs1_real'] < 0.75 or 0 < res['delta_cs2_real'] < 0.75 or 0 < res[
                'delta_cs3_real'] < 0.75:
                tags_aplicar.append("delta_baixo")

            # Insere no widget
            right_text.insert(END, linha, tuple(tags_aplicar))

            # 5. Inserção de divisórias automáticas (de hora em hora)
            contador_linhas += 1
            linhas_por_hora = int(60 / tmp_man_atual) if tmp_man_atual > 0 else 1

            if contador_linhas % linhas_por_hora == 0:
                right_text.insert(END, "-" * 155 + "\n")

        # Garante que a fonte seja monoespaçada para o alinhamento não quebrar
        right_text.config(font=("Courier New", 10), wrap="none")

    def calcular():
        global resultados

        result_label.config(text="")
        lf3.place(x=320, y=95)

        if not validar_entradas():
            return

        try:
            # 1. Captura de dados iniciais
            data_hora_str = entry_data_hora.get().strip()
            data_hora = datetime.strptime(data_hora_str, "%d/%m/%Y - %H:%Mh")
            tmp_man_inicial = float(entries["tmp_man_1"].get())

            # Valores de partida
            nam = float(entries["nam_1"].get())
            naj = float(entries["naj_1"].get())
            aflref = float(entries["aflref_1"].get())
            ugv = float(entries["ugv_1"].get())
            q_vert = float(entries["q_vert_1"].get())
            ger_ug1 = float(entries["ger_ug1_1"].get())
            ger_ug2 = float(entries["ger_ug2_1"].get())
            ger_ug3 = float(entries["ger_ug3_1"].get())
            abcs1 = float(entries["abcs1_1"].get())
            abcs2 = float(entries["abcs2_1"].get())
            abcs3 = float(entries["abcs3_1"].get())

            vaz_acumul = 46.5
            produtibi = 0.008979
            resultados = []
            hb_critico_atingido = False

            # --- CÁLCULO DA PRIMEIRA LINHA ---
            hb = nam - naj
            if hb < 9: hb_critico_atingido = True

            geracao_total = ger_ug1 + ger_ug2 + ger_ug3
            q_turb = ((geracao_total / hb / produtibi) + (ugv * 60)) if hb >= 5 else 0
            q_defl = q_turb + q_vert
            var_nivel = (aflref - q_vert - q_turb) / vaz_acumul / (60 / tmp_man_inicial) / 100

            resultados.append({
                "hora": data_hora.strftime("%d/%m/%Y %H:%M"),
                "nam": nam, "naj": naj, "hb": hb,
                "ger_ug1": ger_ug1, "ger_ug2": ger_ug2, "ger_ug3": ger_ug3,
                "geracao_total": geracao_total, "ugv": ugv, "aflref": aflref,
                "q_turb": q_turb, "q_vert": q_vert, "q_defl": q_defl,
                "abcs1": abcs1, "abcs2": abcs2, "abcs3": abcs3,
                "delta_cs1_real": naj - (abcs1 / 1000) - 0.742,
                "delta_cs2_real": naj - (abcs2 / 1000) - 0.742,
                "delta_cs3_real": naj - (abcs3 / 1000) - 0.742,
                "var_nivel": var_nivel
            })

            # --- LOOP PARA AS LINHAS 2 A 96 ---
            for i in range(2, 97):
                prev = resultados[-1]

                # Determinar tmp_man para este passo de tempo
                tmp_man_atual = tmp_man_inicial
                for manobra in manobras:
                    if data_hora + timedelta(minutes=tmp_man_atual) >= manobra["hora"]:
                        if manobra.get("tmp_man") is not None:
                            tmp_man_atual = manobra["tmp_man"]

                data_hora = data_hora + timedelta(minutes=tmp_man_atual)

                if not hb_critico_atingido:
                    # Evolução dos níveis baseada na linha anterior
                    nam_atual = prev["nam"] + prev["var_nivel"]
                    # NAJ baseado na defluência anterior
                    naj_atual = round((1.607 + 0.002402 * prev["q_defl"] -
                                       0.0000006697 * prev["q_defl"] ** 2 +
                                       0.00000000008349 * prev["q_defl"] ** 3), 2)
                    hb_atual = nam_atual - naj_atual

                    if hb_atual < 9:
                        hb_critico_atingido = True
                        # Se atingiu o crítico agora, zeramos os dados técnicos desta linha em diante
                        res_linha = criar_linha_vazia(data_hora)
                    else:
                        # Cálculos normais mantendo os parâmetros operativos da anterior
                        q_v = calcular_vazao_vertida_simplificada(prev["abcs1"], prev["abcs2"], prev["abcs3"],
                                                                  nam_atual)
                        q_t = ((prev["geracao_total"] / hb_atual / produtibi) + (prev["ugv"] * 60))
                        q_d = q_t + q_v
                        v_n = (prev["aflref"] - q_v - q_t) / vaz_acumul / (60 / tmp_man_atual) / 100

                        res_linha = {
                            "hora": data_hora.strftime("%d/%m/%Y %H:%M"),
                            "nam": nam_atual, "naj": naj_atual, "hb": hb_atual,
                            "ger_ug1": prev["ger_ug1"], "ger_ug2": prev["ger_ug2"], "ger_ug3": prev["ger_ug3"],
                            "geracao_total": prev["geracao_total"], "ugv": prev["ugv"], "aflref": prev["aflref"],
                            "q_turb": q_t, "q_vert": q_v, "q_defl": q_d,
                            "abcs1": prev["abcs1"], "abcs2": prev["abcs2"], "abcs3": prev["abcs3"],
                            "delta_cs1_real": naj_atual - (prev["abcs1"] / 1000) - 0.742,
                            "delta_cs2_real": naj_atual - (prev["abcs2"] / 1000) - 0.742,
                            "delta_cs3_real": naj_atual - (prev["abcs3"] / 1000) - 0.742,
                            "var_nivel": v_n
                        }
                else:
                    # Já está em estado crítico
                    res_linha = criar_linha_vazia(data_hora)

                resultados.append(res_linha)

            # Aplicar manobras e atualizar a tela
            resultados = aplicar_manobras(resultados)
            atualizar_texto_resultados()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro no cálculo: {e}")

    def criar_linha_vazia(dt):
        """Retorna um dicionário com valores zerados para HB crítico"""
        return {
            "hora": dt.strftime("%d/%m/%Y %H:%M"),
            "nam": 0.0, "naj": 0.0, "hb": 0.0, "ger_ug1": 0.0, "ger_ug2": 0.0, "ger_ug3": 0.0,
            "geracao_total": 0.0, "ugv": 0.0, "aflref": 0.0, "q_turb": 0.0, "q_vert": 0.0, "q_defl": 0.0,
            "abcs1": 0.0, "abcs2": 0.0, "abcs3": 0.0, "delta_cs1_real": 0.0, "delta_cs2_real": 0.0,
            "delta_cs3_real": 0.0, "var_nivel": 0.0
        }

    def novo_calculo_e_reset():
        novo_calculo()
        resetar_dados_combinado()

    def novo_calculo():
        # Limpa todos os campos de entrada
        for entry in entries.values():
            entry.delete(0, 'end')
        result_label.config(text="Entre com os novos dados!")

        # Mostrar novamente o cabeçalho da tabela de resultados
        lf3.place(x=320, y=95)

        # Limpa o text area
        right_text.delete(1.0, END)

    def resetar_dados():
        global manobras
        if messagebox.askyesno("Confirmar", "Deseja realmente resetar todas as manobras/alteracoes?",
                               parent=sim_nivel_fgo):
            manobras = []
            messagebox.showinfo("Sucesso", "Todas as manobras/alteracoes foram removidas.", parent=sim_nivel_fgo)

    def resetar_dados_combinado():
        global manobras
        if messagebox.askyesno("Confirmar", "Deseja resetar as manobras e alterações também?",
                               parent=sim_nivel_fgo):
            manobras = []

    def ver_dados():
        """Chama a função de gerenciamento de manobras"""
        gerenciar_manobras()

    def menu_exportacao():
        """Interface de escolha entre PDF, Excel ou Cancelar"""
        # Personalizamos a pergunta para as duas opções
        escolha = messagebox.askyesnocancel(
            "Exportar Relatório",
            "Como deseja exportar os resultados?\n\n"
            "• Clique em 'SIM' para gerar PLANILHA EXCEL (.xlsx)\n "
            "• Clique em 'NÃO' para gerar RELATÓRIO PDF (.pdf)\n"
            "• Clique em 'CANCELAR' para sair",
            parent=sim_nivel_fgo
        )

        if escolha is True:
            gerar_planilha()  # Chama sua função de Excel
        elif escolha is False:
            gerar_pdf()  # Chama sua função de PDF
        else:
            return  # Usuário cancelou

    def gerar_planilha():
        """Gera relatório em Excel com duas abas: Resultados e Manobras"""
        global resultados, manobras

        try:
            if not resultados:
                messagebox.showwarning("Aviso", "Execute o cálculo primeiro!", parent=sim_nivel_fgo)
                return

            nome_arquivo = "Relatorio_Simulacao_Hidraulica.xlsx"

            # 1. Preparar o DataFrame de Resultados
            df_res = pd.DataFrame(resultados)

            # 2. Aplicar arredondamentos específicos solicitados

            # Três casas decimais
            cols_3_casas = ['var_nivel']
            df_res[cols_3_casas] = df_res[cols_3_casas].round(3)

            # Duas casas decimais
            cols_2_casas = ['nam', 'naj', 'hb', 'delta_cs1_real', 'delta_cs2_real', 'delta_cs3_real']
            df_res[cols_2_casas] = df_res[cols_2_casas].round(2)

            # Duas casas decimais para UGs
            cols_ug = ['ger_ug1', 'ger_ug2', 'ger_ug3']
            df_res[cols_ug] = df_res[cols_ug].round(2)

            # Uma casa decimal para geração total
            df_res['geracao_total'] = df_res['geracao_total'].round(1)

            # Sem casas decimais (Inteiros) - para as vazões e aberturas
            cols_0_casas = ['ugv', 'aflref', 'q_turb', 'q_vert', 'q_defl', 'abcs1', 'abcs2', 'abcs3']
            df_res[cols_0_casas] = df_res[cols_0_casas].fillna(0).astype(int)

            # 3. Renomear Colunas de Resultados para o Excel
            df_res = df_res.rename(columns={
                "hora": "Data/Hora", "nam": "NAM (m)", "naj": "NAJ (m)", "hb": "HB (m)",
                "ger_ug1": "UG1 (MW)", "ger_ug2": "UG2 (MW)", "ger_ug3": "UG3 (MW)",
                "geracao_total": "Total (MW)", "ugv": "UGV", "aflref": "Aflu. (m³/s)",
                "q_turb": "Turb. (m³/s)", "q_vert": "Vert. (m³/s)", "q_defl": "Defl. (m³/s)",
                "abcs1": "CS1 (mm)", "abcs2": "CS2 (mm)", "abcs3": "CS3 (mm)",
                "delta_cs1_real": "Delta 1", "delta_cs2_real": "Delta 2", "delta_cs3_real": "Delta 3",
                "var_nivel": "Var. Nível"
            })

            # 4. Preparar o DataFrame de Manobras
            if manobras:
                df_man = pd.DataFrame(manobras)
                # Converter objetos datetime para string
                if 'hora' in df_man.columns:
                    df_man['hora'] = df_man['hora'].dt.strftime('%d/%m/%Y %H:%M')

                # Substituir None por "-" em todas as colunas
                df_man = df_man.fillna("-")

                # Aplicar formatação correta para UGs no DataFrame de manobras
                for col in ['ger_ug1', 'ger_ug2', 'ger_ug3']:
                    if col in df_man.columns:
                        df_man[col] = df_man[col].apply(
                            lambda x: f"{float(x):.2f}" if x != "-" and x is not None else "-"
                        )

                # Para campos que devem ser inteiros
                for col in ['aflref', 'ugv', 'tmp_man', 'abcs1', 'abcs2', 'abcs3']:
                    if col in df_man.columns:
                        df_man[col] = df_man[col].apply(
                            lambda x: f"{int(round(float(x)))}" if x != "-" and x is not None else "-"
                        )

                # Renomear colunas das Manobras
                df_man = df_man.rename(columns={
                    "hora": "Data/Hora", "aflref": "Q Afluente", "ugv": "UGs MV",
                    "tmp_man": "Temp. Manobra", "ger_ug1": "Ger UG1", "ger_ug2": "Ger UG2",
                    "ger_ug3": "Ger UG3", "abcs1": "CS 1", "abcs2": "CS 2", "abcs3": "CS 3"
                })
            else:
                df_man = pd.DataFrame([{"Aviso": "Nenhuma manobra registrada"}])

            # 5. Gravar no Excel com duas abas (Sheets)
            with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
                df_res.to_excel(writer, sheet_name='Resultados da Simulação', index=False)
                df_man.to_excel(writer, sheet_name='Manobras e Alterações', index=False)

            # 6. Abrir o arquivo
            os.startfile(nome_arquivo)
            messagebox.showinfo("Sucesso", f"Planilha com 2 abas gerada!\nArquivo: {nome_arquivo}",
                                parent=sim_nivel_fgo)

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar planilha Excel:\n{str(e)}", parent=sim_nivel_fgo)

    def gerar_pdf():
        # Gera PDF com manobras (retrato) ou resultados (paisagem)
        global resultados, manobras
        if not resultados:
            messagebox.showwarning("Aviso", "Execute o cálculo primeiro!")
            return

        try:
            # Diálogo com três opções: Sim (Manobras), Não (Resultados), Cancelar (Sair)
            escolha = messagebox.askyesnocancel(
                "Tipo de Relatório",
                "Selecione o tipo de relatório:\n\n"
                "• Clique em 'SIM' para gerar relatório de MANOBRAS\n"
                "• Clique em 'NÃO' para gerar relatório de RESULTADOS\n"
                "• Clique em 'CANCELAR' para sair sem gerar relatório",
                parent=sim_nivel_fgo
            )

            # Usuário cancelou ou fechou a janela
            if escolha is None:
                return

            # Obter data e hora atual para o relatório
            data_hora_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
            data_atual = datetime.now().strftime("%d/%m/%Y")
            hora_atual = datetime.now().strftime("%H:%M")

            # Lógica para Manobras e Alterações dos dados preliminares
            if escolha == True:  # Sim - Gerar relatório de Manobras
                if not manobras:
                    messagebox.showwarning("Aviso", "Nenhuma manobra cadastrada!", parent=sim_nivel_fgo)
                    return

                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)

                # Cabeçalho - Ajustado Arial -> helvetica e ln=1 -> new_x/new_y
                pdf.set_font("helvetica", 'B', 14)
                pdf.cell(0, 10, "Relatório das Manobras/Alterações efetuadas", 0,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

                # Data e hora - Ajustado Arial -> helvetica e ln=1 -> new_x/new_y
                pdf.set_font("helvetica", 'I', 10)
                pdf.cell(0, 6, f"Gerado em: {data_hora_atual}", 0,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                pdf.ln(8)

                # Configuração das colunas
                colunas = ["Data/Hora", "Q_Afluente", "UGs MV", "Tmp_Man", "UG-1", "UG-2", "UG-3", "CS-1", "CS-2",
                           "CS-3"]
                larguras = [29, 22, 18, 20, 17, 17, 17, 17, 17, 17]

                # Cabeçalho da tabela - Ajustado Arial -> helvetica
                pdf.set_font("helvetica", 'B', 10)
                for col, larg in zip(colunas, larguras):
                    pdf.cell(larg, 10, col, border=1, align='C')
                pdf.ln()

                # Dados das manobras
                pdf.set_font("helvetica", size=9)
                for manobra in manobras:
                    pdf.cell(larguras[0], 8, manobra['hora'].strftime('%d/%m/%Y %H:%M'), border=1)
                    # Lista ordenada dos campos com regras de formatação
                    campos = [
                        ('aflref', 'int'),      # Q_Afluente - SEM decimais
                        ('ugv', 'int'),         # UGs MV - SEM decimais
                        ('tmp_man', 'int'),     # Temp_Man - SEM decimais
                        ('ger_ug1', 'float'),   # UG-1 - COM 2 decimais
                        ('ger_ug2', 'float'),   # UG-2 - COM 2 decimais
                        ('ger_ug3', 'float'),   # UG-3 - COM 2 decimais
                        ('abcs1', 'int'),       # CS-1 - SEM decimais
                        ('abcs2', 'int'),       # CS-2 - SEM decimais
                        ('abcs3', 'int')        # CS-3 - SEM decimais
                    ]

                    for i, (campo, tipo) in enumerate(campos, 1):
                        valor = manobra.get(campo)

                        # Formatação condicional - None vira "-"
                        if valor is None:
                            texto = "-"
                        elif isinstance(valor, (int, float)):
                            if tipo == 'float':
                                texto = f"{valor:.2f}"  # 2 casas decimais para UGs
                            else:
                                texto = f"{int(valor)}"  # Inteiro para demais campos
                        else:
                            texto = str(valor)

                        pdf.cell(larguras[i], 8, texto, border=1, align='C')
                    pdf.ln()

                nome_arquivo = "manobras_uhe.pdf"
                mensagem = f"Relatório de MANOBRAS gerado com sucesso!\n\nArquivo: {nome_arquivo}\n\nGerado em: {data_hora_atual}"

            else:  # Não - Gerar relatório de Resultados
                if not resultados:
                    messagebox.showwarning("Aviso", "Execute o cálculo primeiro!", parent=sim_nivel_fgo)
                    return

                    # --- DEFINA AS LISTAS AQUI (FORA DA CLASSE) PARA QUE AMBOS ACESSEM ---
                colunas_header = [
                    "Data/Hora", "Mont.", "Jus.", "HB", "UG-1", "UG-2", "UG-3", "UGV",
                    "Aflu.", "Turb.", "Vert.", "Defl.", "CS-1", "CS-2", "CS-3",
                    "Delta1", "Delta2", "Delta3", "Var.Nív"
                ]
                larguras_header = [25, 14, 14, 14, 14, 14, 14, 13, 13, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14]

                class PDFWithHeader(FPDF):
                    def __init__(self, data_hora, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.data_hora = data_hora

                    def header(self):
                        self.set_font("helvetica", 'B', 13)
                        self.cell(0, 10, "Resultado da Simulação Hidráulica", 0,
                                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

                        self.set_font("helvetica", 'I', 10)
                        self.cell(0, 6, f"Gerado em: {self.data_hora}", 0,
                                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                        self.ln(5)

                        self.set_font("helvetica", size=8)
                        # Agora o header consegue acessar as listas porque elas estão no escopo acima
                        for col, larg in zip(colunas_header, larguras_header):
                            self.cell(larg, 8, col, border=1, align='C')
                        self.ln()

                pdf = PDFWithHeader(data_hora_atual, orientation='L', unit='mm', format='A4')
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()

                # Dados dos resultados
                pdf.set_font("helvetica", size=8)
                for res in resultados:
                    if pdf.get_y() > 180:  # Ajuste para orientação Paisagem (A4 tem ~210mm de altura)
                        pdf.add_page()

                    # Loop de preenchimento das células usando a mesma lista de larguras
                    # IMPORTANTE: usei larguras_header aqui para manter a consistência
                    pdf.cell(larguras_header[0], 6, res['hora'], border=1)

                    campos = [
                        ('nam', res['nam']), ('naj', res['naj']), ('hb', res['hb']),
                        ('ger_ug1', res['ger_ug1']), ('ger_ug2', res['ger_ug2']),
                        ('ger_ug3', res['ger_ug3']), ('ugv', res['ugv']),
                        ('aflref', res['aflref']), ('q_turb', res['q_turb']),
                        ('q_vert', res['q_vert']), ('q_defl', res['q_defl']),
                        ('abcs1', res['abcs1']), ('abcs2', res['abcs2']),
                        ('abcs3', res['abcs3']), ('delta1', res['delta_cs1_real']),
                        ('delta2', res['delta_cs2_real']), ('delta3', res['delta_cs3_real']),
                        ('var_nivel', res['var_nivel'])
                    ]

                    # Começamos do índice 1 porque a hora (índice 0) já foi impressa acima
                    for i, (campo, valor) in enumerate(campos, 1):
                        if campo in ['nam', 'naj', 'hb', 'delta1', 'delta2', 'delta3']:
                            texto = f"{valor:.2f}"
                        elif campo in ['ger_ug1', 'ger_ug2', 'ger_ug3']:
                            texto = f"{valor:.2f}"  # 2 casas decimais para UGs
                        elif campo in ['var_nivel']:
                            texto = f"{valor:.3f}"
                        else:
                            texto = f"{int(valor)}" if isinstance(valor, (int, float)) else str(valor)

                        pdf.cell(larguras_header[i], 6, texto, border=1, align='R')
                    pdf.ln()

                nome_arquivo = "resultados_simulacao.pdf"
                mensagem = f"Relatório de RESULTADOS gerado com sucesso!\nArquivo: {nome_arquivo}\nGerado em: {data_hora_atual}"

            # Salvar e abrir o arquivo
            nome_arquivo = "Relatorio_Simulacao.pdf"
            pdf.output(nome_arquivo)
            os.startfile(nome_arquivo)
            messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no PDF: {e}")

    def mostrar_dicas1():
        # Criar janela personalizada
        dicas_window = Toplevel(sim_nivel_fgo)
        dicas_window.title("Orientações de Preenchimento")
        dicas_window.geometry("1000x650")  # Define largura e altura

        # Adicionar título
        titulo = Label(dicas_window, text="Orientações de Preenchimento",
                          font=("Arial", 14, "bold"))
        titulo.pack(pady=10)

        # Criar frame para texto com scrollbar
        frame_texto = Frame(dicas_window)
        frame_texto.pack(fill="both", expand=True, padx=20, pady=10)

        # Text widget com scrollbar
        scrollbar = Scrollbar(frame_texto)
        scrollbar.pack(side="right", fill="y")

        texto = Text(frame_texto, wrap=WORD, yscrollcommand=scrollbar.set,
                     font=("Arial", 10))
        texto.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=texto.yview)

        dicas = (
            "Considerar como dados preliminares, os dados inseridos na parte superior com fundo claro.\n\n"
            "Considerar como dados complementares, os dados inseridos na parte inferior, denominada 'Efetuar Manobras/Alterar\n"
            "Dados' com fundo escuro, para alterar os dados preliminares.\n\n"
            "Caso sejam inseridos vírgulas, elas serão automaticamente alterada para ponto.\n\n"
            "Usar números decimais somente para Geração, demais dados usar números inteiros.\n\n"
            "Os botões 'Salvar', 'Reset', 'Ver' e 'Relatório' se refere somente aos dados inseridos como dados complementares.\n\n"
            "O botão denominado 'Salvar' efetua o salvamento dos dados complementares.\n\n"
            "O botão denominado 'Reset' apaga todos os dados inseridos como dados complementares.\n\n"
            "O botão denominado 'Ver' apresenta uma janela de gerenciamento para editar/excluir manobras individualmente.\n\n"
            "O botão denominado 'Relatório' gera um arquivo em pdf ou excel apresentando a simulação ou os dados complementares inseridos.\n\n"
            "O botão denominado 'Lançamento simultâneo de Manobras' permite lançar todas as manobras e salvá-las de uma só vez\n\n"
            "O botão denominado 'Calcular' deverá ser pressionado após a inclusão dos dados preliminares para que o resultado seja\n"
            "apresentado na janela à direita.\n\n"
            "Esse botão será pressionado também quando houver inserção de dados complementares e após o salvamento dos dados.\n\n"
            "O botão denominado 'Novo Cálculo' ao ser pressionado apaga todos os dados, tanto preliminares quanto complementares.\n\n"
            "GERENCIAMENTO DE MANOBRAS:\n"
            "- Clique em 'Ver' para abrir a janela de gerenciamento\n"
            "- Selecione qualquer manobra na tabela\n"
            "- Use os botões para Editar ou Excluir a manobra selecionada\n"
            "- É possível excluir todas as manobras de uma vez\n"
            "- As manobras são automaticamente ordenadas por data/hora\n"
        )

        texto.insert("1.0", dicas)
        texto.config(state="disabled")  # Torna o texto apenas leitura

        # Botão fechar
        btn_fechar = Button(dicas_window, text="Fechar", bg="#CDCDCD", fg="black",
                               command=dicas_window.destroy, width=15)
        btn_fechar.pack(pady=10)

        # Centralizar janela
        dicas_window.transient(sim_nivel_fgo)
        dicas_window.grab_set()
        sim_nivel_fgo.wait_window(dicas_window)
    # ============================================================
    # FUNÇÃO DE LANÇAMENTO RÁPIDO EM MASSA (inserir AQUI, antes dos botões)
    # ============================================================
    def lancamento_rapido_massa():
        """Abre uma janela com tabela para lançamento rápido de múltiplas manobras"""

        # Criar janela de lançamento rápido
        janela_massa = Toplevel(sim_nivel_fgo)
        janela_massa.title("Lançamento Rápido de Múltiplas Manobras - UHE Ferreira Gomes")
        janela_massa.geometry("1300x630")
        janela_massa.resizable(True, True)

        # Frame principal
        main_frame = Frame(janela_massa)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Instruções
        lbl_instrucoes = Label(main_frame,
                               text="Preencha os dados das manobras nas linhas abaixo. Deixe em branco os campos que não deseja alterar.\n"
                                    "Data/Hora padrão: será usada a data/hora do campo principal, podendo ser sobrescrita linha a linha.\n"
                                    "Clique em 'Salvar Todas' para adicionar todas as manobras de uma vez.\n"
                                    "As manobras já existentes são mostradas abaixo (linhas em AZUL).",
                               font=("Arial", 9), fg="blue", justify=LEFT)
        lbl_instrucoes.pack(fill=X, pady=5)

        # Frame para a tabela com scroll
        table_frame = Frame(main_frame)
        table_frame.pack(fill=BOTH, expand=True)

        # Scrollbars
        scroll_y = Scrollbar(table_frame, orient=VERTICAL)
        scroll_x = Scrollbar(table_frame, orient=HORIZONTAL)

        # Treeview editável
        colunas = ("Data/Hora", "Q_Afluente", "UGs_MV", "Tmp_Man",
                   "UG-1", "UG-2", "UG-3", "CS-1", "CS-2", "CS-3")

        tree = ttk.Treeview(table_frame, columns=colunas, show="headings",
                            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                            height=15)

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        tree.pack(fill=BOTH, expand=True)

        # Configurar colunas
        larguras = {"Data/Hora": 150, "Q_Afluente": 100, "UGs_MV": 80, "Tmp_Man": 80,
                    "UG-1": 80, "UG-2": 80, "UG-3": 80, "CS-1": 80, "CS-2": 80, "CS-3": 80}

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=larguras.get(col, 100), anchor="center")

        # Configurar tags para cores diferentes
        tree.tag_configure("existente", background="#E8F4FD")  # Azul claro para manobras existentes
        tree.tag_configure("nova", background="#FFFFFF")  # Branco para novas manobras

        # ============================================================
        # FUNÇÃO DE FORMATAÇÃO CORRIGIDA
        # ============================================================
        def formatar_valor_tabela(valor, nome_campo=None):
            """
            Formata valores para exibição na tabela conforme o tipo de campo:
            - UG-1, UG-2, UG-3: 2 casas decimais
            - Demais campos: sem casas decimais (inteiros)
            """
            if valor is None:
                return ""

            # Para campos das UGs (deve ter 2 casas decimais)
            if nome_campo in ['UG-1', 'UG-2', 'UG-3', 'ger_ug1', 'ger_ug2', 'ger_ug3']:
                if isinstance(valor, (int, float)):
                    return f"{valor:.2f}"
                return str(valor)

            # Para os demais campos numéricos (sem casas decimais)
            if isinstance(valor, (int, float)):
                return f"{int(round(valor))}"

            return str(valor)

        # ============================================================
        # FUNÇÃO DE VALIDAÇÃO
        # ============================================================
        def validar_valor_manobra(valor, campo, minimo, maximo):
            """Valida um valor de manobra dentro dos limites"""
            if valor is None or str(valor).strip() == "":
                return True, None
            try:
                num = float(str(valor).replace(',', '.'))
                if num < minimo or num > maximo:
                    return False, f"{campo}: {num} (permitido: {minimo} a {maximo})"
                return True, num
            except:
                return False, f"{campo}: valor inválido"

        # ============================================================
        # FUNÇÃO PARA CARREGAR MANOBRAS EXISTENTES (CORRIGIDA)
        # ============================================================
        def carregar_manobras_existentes():
            """Carrega as manobras já cadastradas na tabela"""
            for manobra in manobras:
                valores = [
                    manobra['hora'].strftime('%d/%m/%Y %H:%M'),
                    formatar_valor_tabela(manobra.get('aflref'), 'Q_Afluente'),
                    formatar_valor_tabela(manobra.get('ugv'), 'UGs_MV'),
                    formatar_valor_tabela(manobra.get('tmp_man'), 'Tmp_Man'),
                    formatar_valor_tabela(manobra.get('ger_ug1'), 'UG-1'),
                    formatar_valor_tabela(manobra.get('ger_ug2'), 'UG-2'),
                    formatar_valor_tabela(manobra.get('ger_ug3'), 'UG-3'),
                    formatar_valor_tabela(manobra.get('abcs1'), 'CS-1'),
                    formatar_valor_tabela(manobra.get('abcs2'), 'CS-2'),
                    formatar_valor_tabela(manobra.get('abcs3'), 'CS-3')
                ]
                tree.insert("", END, values=valores, tags=("existente",))

        # ============================================================
        # LINHA DE BOTÕES SUPERIORES
        # ============================================================
        controle_frame = Frame(main_frame)
        controle_frame.pack(fill=X, pady=10)

        # Informação de quantas manobras existentes
        lbl_info_existentes = Label(controle_frame, text=f"Manobras existentes: {len(manobras)}",
                                    font=("Arial", 9), fg="blue")
        lbl_info_existentes.pack(side=LEFT, padx=10)

        # Separador
        separador = Frame(controle_frame, width=2, bg="gray")
        separador.pack(side=LEFT, fill=Y, padx=10)

        # 1. Label e Spinbox
        Label(controle_frame, text="Nº de novas manobras:", font=("Arial", 10)).pack(side=LEFT, padx=5)

        spin_num_linhas = Spinbox(controle_frame, from_=1, to=50, width=5, font=("Arial", 10))
        spin_num_linhas.pack(side=LEFT, padx=5)
        spin_num_linhas.delete(0, END)
        spin_num_linhas.insert(0, "2")

        # 2. Botão Adicionar Linhas
        def adicionar_linhas():
            try:
                num_linhas = int(spin_num_linhas.get())
            except:
                num_linhas = 5

            if num_linhas < 1:
                num_linhas = 1
            if num_linhas > 50:
                num_linhas = 50
                spin_num_linhas.delete(0, END)
                spin_num_linhas.insert(0, "50")

            data_hora_padrao = entries["hora_manobra"].get().strip()

            for i in range(num_linhas):
                tree.insert("", END, values=(data_hora_padrao, "", "", "", "", "", "", "", "", ""),
                            tags=("nova",))

            atualizar_contador()
            messagebox.showinfo("Info", f"{num_linhas} nova(s) linha(s) adicionada(s)!", parent=janela_massa)

        btn_adicionar = Button(controle_frame, text="Adicionar Linhas", command=adicionar_linhas,
                               bg="#024593", fg="white", font=("Arial", 10), padx=15)
        btn_adicionar.pack(side=LEFT, padx=5)

        # 3. Botão Duplicar Linha
        def duplicar_linha():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione uma linha para duplicar!", parent=janela_massa)
                return

            valores = tree.item(selecionado[0])['values']
            tree.insert("", END, values=valores, tags=("nova",))
            messagebox.showinfo("Sucesso", "Linha duplicada!", parent=janela_massa)
            atualizar_contador()

        btn_duplicar = Button(controle_frame, text="Duplicar Linha", command=duplicar_linha,
                              bg="#FF0000", fg="white", font=("Arial", 10), padx=15)
        btn_duplicar.pack(side=LEFT, padx=5)

        # 4. Botão Excluir Linha
        def excluir_linha():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione uma linha para excluir!", parent=janela_massa)
                return

            item_tags = tree.item(selecionado[0], 'tags')
            if "existente" in item_tags:
                if not messagebox.askyesno("Atenção",
                                           "Esta é uma manobra já salva!\n\n"
                                           "Excluí-la aqui NÃO irá removê-la do sistema.\n"
                                           "Use o 'Gerenciar Manobras' para excluir manobras permanentemente.\n\n"
                                           "Deseja remover apenas desta visualização?",
                                           parent=janela_massa):
                    return

            if messagebox.askyesno("Confirmar", "Deseja excluir a linha selecionada?", parent=janela_massa):
                tree.delete(selecionado[0])
                atualizar_contador()

        btn_excluir = Button(controle_frame, text="Excluir Linha", command=excluir_linha,
                             bg="#FF8C00", fg="white", font=("Arial", 10), padx=15)
        btn_excluir.pack(side=LEFT, padx=5)

        # 5. Botão Limpar Novas Linhas
        def limpar_linhas_novas():
            if messagebox.askyesno("Confirmar", "Deseja remover TODAS as linhas NOVAS (não salvas)?",
                                   parent=janela_massa):
                itens = tree.get_children()
                for item in itens:
                    tags = tree.item(item, 'tags')
                    if "existente" not in tags:
                        tree.delete(item)
                atualizar_contador()
                messagebox.showinfo("Info", "Linhas novas removidas!", parent=janela_massa)

        btn_limpar_novas = Button(controle_frame, text="Limpar Novas", command=limpar_linhas_novas,
                                  bg="#8B0000", fg="white", font=("Arial", 10), padx=15)
        btn_limpar_novas.pack(side=LEFT, padx=5)

        # 6. Botão Recarregar
        def recarregar_manobras():
            if messagebox.askyesno("Confirmar",
                                   "Recarregar irá atualizar a lista com as manobras salvas.\n"
                                   "As linhas novas não salvas serão perdidas.\n\n"
                                   "Deseja continuar?", parent=janela_massa):
                for item in tree.get_children():
                    tree.delete(item)
                carregar_manobras_existentes()
                atualizar_contador()
                messagebox.showinfo("Info", "Lista recarregada!", parent=janela_massa)

        btn_recarregar = Button(controle_frame, text="Recarregar", command=recarregar_manobras,
                                bg="#1D9BFF", fg="white", font=("Arial", 10), padx=15)
        btn_recarregar.pack(side=LEFT, padx=5)

        # ============================================================
        # BOTÕES PRINCIPAIS (Salvar e Fechar)
        # ============================================================
        botoes_frame = Frame(main_frame)
        botoes_frame.pack(fill=X, pady=10)

        def salvar_novas_manobras():
            """Salva apenas as novas manobras (não as existentes) com validação"""
            linhas = tree.get_children()
            if not linhas:
                messagebox.showwarning("Aviso", "Nenhuma manobra para salvar!", parent=janela_massa)
                return

            manobras_adicionadas = 0
            manobras_duplicadas = 0
            erros = 0

            for linha in linhas:
                # Verificar se é uma linha nova (não existente)
                tags = tree.item(linha, 'tags')
                if "existente" in tags:
                    continue

                valores = tree.item(linha)['values']

                # Verificar se pelo menos um campo foi preenchido
                campos_preenchidos = [v for v in valores[1:] if v and str(v).strip()]
                if not campos_preenchidos:
                    continue

                try:
                    # Processar data/hora
                    hora_manobra_str = valores[0].strip() if valores[0] else entries["hora_manobra"].get().strip()

                    try:
                        hora_manobra = datetime.strptime(hora_manobra_str, "%d/%m/%Y - %H:%Mh")
                    except ValueError:
                        try:
                            hora_manobra = datetime.strptime(hora_manobra_str, "%d/%m/%Y - %H:%M")
                        except:
                            messagebox.showerror("Erro",
                                                 f"Data/Hora inválida: {hora_manobra_str}\nUse: DD/MM/AAAA - HH:MMh",
                                                 parent=janela_massa)
                            erros += 1
                            continue

                    # Criar dicionário da manobra
                    alteracao = {
                        "hora": hora_manobra,
                        "aflref": None, "ugv": None, "tmp_man": None,
                        "ger_ug1": None, "ger_ug2": None, "ger_ug3": None,
                        "abcs1": None, "abcs2": None, "abcs3": None
                    }

                    # Validar e preencher cada campo
                    erros_validacao = []

                    # Q_Afluente (0 a 8000) - será armazenado como inteiro
                    if valores[1] and str(valores[1]).strip():
                        valido, resultado = validar_valor_manobra(valores[1], "Q_Afluente", 0, 8000)
                        if not valido:
                            erros_validacao.append(resultado)
                        else:
                            alteracao["aflref"] = int(round(resultado))  # Converte para inteiro

                    # UGs em MV (0 a 3) - será armazenado como inteiro
                    if valores[2] and str(valores[2]).strip():
                        valido, resultado = validar_valor_manobra(valores[2], "UGs_MV", 0, 3)
                        if not valido:
                            erros_validacao.append(resultado)
                        else:
                            alteracao["ugv"] = int(round(resultado))  # Converte para inteiro

                    # Tempo de Manobra (3 a 60) - será armazenado como inteiro
                    if valores[3] and str(valores[3]).strip():
                        valido, resultado = validar_valor_manobra(valores[3], "Tmp_Man", 3, 60)
                        if not valido:
                            erros_validacao.append(resultado)
                        else:
                            alteracao["tmp_man"] = int(round(resultado))  # Converte para inteiro

                    # UG-1 (0 a 84) - mantém 2 casas decimais
                    if valores[4] and str(valores[4]).strip():
                        valido, resultado = validar_valor_manobra(valores[4], "UG-1", 0, 84)
                        if not valido:
                            erros_validacao.append(resultado)
                        else:
                            alteracao["ger_ug1"] = round(resultado, 2)  # Mantém 2 casas decimais

                    # UG-2 (0 a 84) - mantém 2 casas decimais
                    if valores[5] and str(valores[5]).strip():
                        valido, resultado = validar_valor_manobra(valores[5], "UG-2", 0, 84)
                        if not valido:
                            erros_validacao.append(resultado)
                        else:
                            alteracao["ger_ug2"] = round(resultado, 2)  # Mantém 2 casas decimais

                    # UG-3 (0 a 84) - mantém 2 casas decimais
                    if valores[6] and str(valores[6]).strip():
                        valido, resultado = validar_valor_manobra(valores[6], "UG-3", 0, 84)
                        if not valido:
                            erros_validacao.append(resultado)
                        else:
                            alteracao["ger_ug3"] = round(resultado, 2)  # Mantém 2 casas decimais

                    # CS-1 (0 a 15000) - será armazenado como inteiro
                    if valores[7] and str(valores[7]).strip():
                        valido, resultado = validar_valor_manobra(valores[7], "CS-1", 0, 15000)
                        if not valido:
                            erros_validacao.append(resultado)
                        else:
                            alteracao["abcs1"] = int(round(resultado))  # Converte para inteiro

                    # CS-2 (0 a 15000) - será armazenado como inteiro
                    if valores[8] and str(valores[8]).strip():
                        valido, resultado = validar_valor_manobra(valores[8], "CS-2", 0, 15000)
                        if not valido:
                            erros_validacao.append(resultado)
                        else:
                            alteracao["abcs2"] = int(round(resultado))  # Converte para inteiro

                    # CS-3 (0 a 15000) - será armazenado como inteiro
                    if valores[9] and str(valores[9]).strip():
                        valido, resultado = validar_valor_manobra(valores[9], "CS-3", 0, 15000)
                        if not valido:
                            erros_validacao.append(resultado)
                        else:
                            alteracao["abcs3"] = int(round(resultado))  # Converte para inteiro

                    # Se houver erros de validação, mostrar e pular esta linha
                    if erros_validacao:
                        messagebox.showerror("Erro de Validação",
                                             f"Erros na linha:\n" + "\n".join(erros_validacao),
                                             parent=janela_massa)
                        erros += 1
                        continue

                    # Verificar duplicata
                    chave_unica = (
                        hora_manobra, alteracao.get("aflref"), alteracao.get("ugv"),
                        alteracao.get("tmp_man"), alteracao.get("ger_ug1"),
                        alteracao.get("ger_ug2"), alteracao.get("ger_ug3"),
                        alteracao.get("abcs1"), alteracao.get("abcs2"), alteracao.get("abcs3")
                    )

                    ja_existe = any(
                        (m["hora"] == chave_unica[0] and
                         m.get("aflref") == chave_unica[1] and
                         m.get("ugv") == chave_unica[2] and
                         m.get("tmp_man") == chave_unica[3] and
                         m.get("ger_ug1") == chave_unica[4] and
                         m.get("ger_ug2") == chave_unica[5] and
                         m.get("ger_ug3") == chave_unica[6] and
                         m.get("abcs1") == chave_unica[7] and
                         m.get("abcs2") == chave_unica[8] and
                         m.get("abcs3") == chave_unica[9])
                        for m in manobras
                    )

                    if not ja_existe:
                        manobras.append(alteracao)
                        manobras_adicionadas += 1
                        tree.item(linha, tags=("existente",))
                        # Atualiza a exibição da linha com a formatação correta
                        valores_atualizados = [
                            valores[0],
                            formatar_valor_tabela(alteracao.get("aflref"), 'Q_Afluente'),
                            formatar_valor_tabela(alteracao.get("ugv"), 'UGs_MV'),
                            formatar_valor_tabela(alteracao.get("tmp_man"), 'Tmp_Man'),
                            formatar_valor_tabela(alteracao.get("ger_ug1"), 'UG-1'),
                            formatar_valor_tabela(alteracao.get("ger_ug2"), 'UG-2'),
                            formatar_valor_tabela(alteracao.get("ger_ug3"), 'UG-3'),
                            formatar_valor_tabela(alteracao.get("abcs1"), 'CS-1'),
                            formatar_valor_tabela(alteracao.get("abcs2"), 'CS-2'),
                            formatar_valor_tabela(alteracao.get("abcs3"), 'CS-3')
                        ]
                        tree.item(linha, values=valores_atualizados)
                    else:
                        manobras_duplicadas += 1

                except Exception as e:
                    messagebox.showerror("Erro", f"Erro: {str(e)}", parent=janela_massa)
                    erros += 1

            if manobras_adicionadas > 0:
                manobras.sort(key=lambda x: x["hora"])

            lbl_info_existentes.config(text=f"Manobras existentes: {len(manobras)}")

            msg = f"✅ Operação concluída!\n\n"
            msg += f"📝 Manobras adicionadas: {manobras_adicionadas}\n"
            if manobras_duplicadas > 0:
                msg += f"⚠️ Duplicadas ignoradas: {manobras_duplicadas}\n"
            if erros > 0:
                msg += f"❌ Erros: {erros}\n"

            messagebox.showinfo("Resultado", msg, parent=janela_massa)

            if manobras_adicionadas > 0 and messagebox.askyesno("Sucesso",
                                                                f"{manobras_adicionadas} manobra(s) adicionada(s)!\n\n"
                                                                "Deseja fechar esta janela?", parent=janela_massa):
                janela_massa.destroy()

        # Botão Salvar Novas Manobras
        btn_salvar_novas = Button(botoes_frame, text="💾 Salvar Novas Manobras", command=salvar_novas_manobras,
                                  bg="#009F4D", fg="white", font=("Arial", 11, "bold"), padx=30, pady=5)
        btn_salvar_novas.pack(side=LEFT, padx=10)

        # Botão Fechar
        btn_fechar_massa = Button(botoes_frame, text="Fechar", command=janela_massa.destroy,
                                  bg="#808080", fg="white", font=("Arial", 10), padx=20)
        btn_fechar_massa.pack(side=RIGHT, padx=10)

        # Label com contador
        lbl_contador = Label(main_frame, text="", font=("Arial", 9), fg="green")
        lbl_contador.pack(pady=5)

        # Variável de controle para o loop do contador
        contador_ativo = True

        def atualizar_contador():
            """Atualiza o contador de linhas"""
            if not contador_ativo:
                return
            try:
                total_novas = 0
                total_existentes = 0
                for item in tree.get_children():
                    if "existente" in tree.item(item, 'tags'):
                        total_existentes += 1
                    else:
                        total_novas += 1
                lbl_contador.config(
                    text=f"📊 Linhas existentes: {total_existentes} | Novas: {total_novas} | Total: {total_existentes + total_novas}")
                if janela_massa.winfo_exists():
                    janela_massa.after(1000, atualizar_contador)
            except:
                pass

        def on_closing():
            nonlocal contador_ativo
            contador_ativo = False
            janela_massa.destroy()

        janela_massa.protocol("WM_DELETE_WINDOW", on_closing)

        # CARREGAR MANOBRAS EXISTENTES AO ABRIR A JANELA
        carregar_manobras_existentes()
        atualizar_contador()

        # Instruções de edição
        lbl_edicao = Label(main_frame,
                           text="💡 DICA: Linhas com fundo em AZUL são manobras já salvas. Linhas com fundo em BRANCO são novas.\n"
                                "Para editar uma célula, clique duas vezes nela.\n"
                                "Altere o N° de novas manobras, se necessário e use 'Adicionar Linhas' para incluir novas manobras.",
                           font=("Arial", 8), fg="gray", justify=LEFT)
        lbl_edicao.pack(fill=X, pady=5)

        # Configurar edição inline na Treeview
        def on_double_click(event):
            selecionado = tree.selection()
            if not selecionado:
                return

            item = selecionado[0]
            col = tree.identify_column(event.x)
            col_num = int(col[1:]) - 1

            valores = list(tree.item(item, 'values'))
            if not valores:
                valores = [""] * len(colunas)

            try:
                x, y, width, height = tree.bbox(item, column=col)

                entry_edit = Entry(tree, font=("Arial", 10))
                entry_edit.place(x=x, y=y, width=width, height=height)
                entry_edit.insert(0, valores[col_num] if col_num < len(valores) else "")
                entry_edit.focus()

                def save_edit():
                    novo_valor = entry_edit.get()
                    valores[col_num] = novo_valor
                    tree.item(item, values=valores)
                    entry_edit.destroy()
                    atualizar_contador()

                def cancel_edit(event=None):
                    entry_edit.destroy()

                entry_edit.bind("<Return>", lambda e: save_edit())
                entry_edit.bind("<FocusOut>", lambda e: save_edit())
                entry_edit.bind("<Escape>", cancel_edit)
            except:
                pass

        tree.bind("<Double-1>", on_double_click)

    # ============================================================
    # BOTÕES DA INTERFACE (aqui ficam todos os botões existentes)
    # ============================================================

    btn_salvar = Button(left_frame, text="Salvar", command=adicionar_ou_atualizar_manobra, bg="#024593", fg="white",
           font=("Arial", 9))
    btn_salvar.place(relx=0.05, rely=0.80, width=55, height=22)

    Button(left_frame, text="Reset", command=resetar_dados, bg="#024593", fg="white",
           font=("Arial", 9)).place(relx=0.28, rely=0.80, width=55, height=22)

    Button(left_frame, text="Ver", command=ver_dados, bg="#024593", fg="white",
           font=("Arial", 9)).place(relx=0.51, rely=0.80, width=55, height=22)

    Button(left_frame, text="Relatório", command=menu_exportacao, bg="#024593", fg="white",
           font=("Arial", 9)).place(relx=0.74, rely=0.80, width=60, height=22)

    # Botão LANÇAMENTO RÁPIDO (novo botão)
    Button(left_frame, text="Lançamento Simultaneo de Manobras", command=lancamento_rapido_massa,
           bg="#024593", fg="white", font=("Arial", 9)).place(relx=0.05, rely=0.845, width=245, height=22)

    Button(left_frame, text="Orientações Preenchimento", command=mostrar_dicas1, bg="#a4bad2", fg="black",
           font=("Arial", 9)).place(relx=0.12, rely=0.90, width=200, height=22)

    Button(left_frame, text="Calcular", command=calcular, bg="#024593", fg="white",
           font=("Arial", 10, "bold")).place(relx=0.05, rely=0.94, width=100, height=25)

    Button(left_frame, text="Novo Cálculo", command=novo_calculo_e_reset, bg="#FF0000", fg="white",
           font=("Arial", 10, "bold")).place(relx=0.56, rely=0.94, width=100, height=25)


    # Inicializar a configuração dos entries numéricos
    configurar_entries_numericos()


def cmd_click21():
    """Função para pesquisa e abertura de arquivos PDF - Versão Simplificada"""

    # ===== CONFIGURAÇÃO INICIAL =====
    DIRETORIO_BASE = r"C:\Users\nival\PycharmProjects\TTurno\Click_21"
    ARQUIVO_CONFIG = os.path.join(DIRETORIO_BASE, "config_localidades.json")

    # ===== FUNÇÃO PARA CARREGAR CONFIGURAÇÃO DAS LOCALIDADES =====
    def carregar_config_localidades():
        """
        Carrega o arquivo de configuração que mapeia palavras-chave para localidades.
        Se o arquivo não existir, cria um padrão.
        """
        config_padrao = {
            "localidades": [
                "UHE Müller de Godoy Pereira",
                "UHE São José",
                "UHE Ferreira Gomes",
                "PCH Queluz",
                "PCH Lavrinhas",
                "PCH Verde 8",
                "CGE Pitombeira",
                "CGE Jandaíra-III",
                "UFV Pitombeira",
                "SE Macapá",
                "SE Itaguaçu",
                "SE Russas-II",
                "COG-Alupar",
                "UHEs - TODAS",
                "PCHs - TODAS",
                "CGEs - TODAS",
                "OUTROS AGENTES"
            ],
            "mapeamento": {
                "UHE Müller de Godoy Pereira": ["MGP", "FOZ", "Muller"],
                "UHE São José": ["SJO", "Ijuí"],
                "UHE Ferreira Gomes": ["FGO", "FGE", "Ferreira"],
                "PCH Queluz": ["QUE", "Queluz"],
                "PCH Lavrinhas": ["LAV", "Lavrinhas"],
                "PCH Verde 8": ["VIE", "VOE"],
                "CGE Pitombeira": ["PTEM", "EDV"],
                "CGE Jandaíra-III": ["JDT", "EAP"],
                "UFV Pitombeira": ["UPTM", "Solar"],
                "SE Macapá": ["MCP", "Macapá"],
                "SE Itaguaçu": ["ITG", "Itaguaçu"],
                "SE Russas-II": ["RSD", "Russas"],
                "COG-Alupar": ["COG", "Cruzeiro"],
                "UHEs - TODAS": ["UHE", "Usinas"],
                "PCHs - TODAS": ["PCH", "PCHs"],
                "CGEs - TODAS": ["CGE", "CGEs"],
                "OUTROS AGENTES": ["ENGIE", "LMTE", "AXIA"]
            }
        }

        # Função para comparar se duas configurações são diferentes
        def configuracao_diferente(config1, config2):
            """Compara duas configurações e retorna True se forem diferentes"""
            # Compara localidades
            if set(config1.get("localidades", [])) != set(config2.get("localidades", [])):
                return True

            # Compara mapeamento (chaves e valores)
            mapeamento1 = config1.get("mapeamento", {})
            mapeamento2 = config2.get("mapeamento", {})

            if set(mapeamento1.keys()) != set(mapeamento2.keys()):
                return True

            for chave in mapeamento1.keys():
                if set(mapeamento1.get(chave, [])) != set(mapeamento2.get(chave, [])):
                    return True

            return False

        # Se o arquivo de configuração já existe
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
                    config_existente = json.load(f)

                # Verifica se a configuração existente é diferente da padrão
                if configuracao_diferente(config_existente, config_padrao):
                    # Mostra as diferenças para o usuário
                    localidades_antigas = config_existente.get("localidades", [])
                    localidades_novas = config_padrao.get("localidades", [])

                    diferencas = []
                    if set(localidades_antigas) != set(localidades_novas):
                        adicionadas = set(localidades_novas) - set(localidades_antigas)
                        removidas = set(localidades_antigas) - set(localidades_novas)
                        if adicionadas:
                            diferencas.append(f"• Localidades adicionadas: {', '.join(adicionadas)}")
                        if removidas:
                            diferencas.append(f"• Localidades removidas: {', '.join(removidas)}")

                    mensagem = "Foi detectada uma configuração de localidades diferente da atual!\n\n"
                    if diferencas:
                        mensagem += "Diferenças encontradas:\n" + "\n".join(diferencas) + "\n\n"
                    mensagem += "Deseja atualizar para a nova configuração?\n\n"
                    mensagem += "SIM - Atualizar para as novas localidades\n"
                    mensagem += "NÃO - Manter a configuração atual"

                    resposta = messagebox.askyesno(
                        "Configuração Desatualizada",
                        mensagem
                    )

                    if resposta:
                        # Recria o arquivo com a nova configuração
                        with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
                            json.dump(config_padrao, f, indent=4, ensure_ascii=False)
                        messagebox.showinfo("Sucesso",
                                            "Configuração atualizada com sucesso!\nClique em 'Recarregar Arquivos' para ver as mudanças.")
                        return config_padrao
                    else:
                        return config_existente
                else:
                    # Configuração está igual, usa a existente
                    return config_existente

            except Exception as e:
                messagebox.showerror("Erro",
                                     f"Erro ao ler arquivo de configuração: {str(e)}\n\nUsando configuração padrão.")
                return config_padrao
        else:
            # Arquivo não existe, cria pela primeira vez
            try:
                os.makedirs(DIRETORIO_BASE, exist_ok=True)
                with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
                    json.dump(config_padrao, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Configuração Criada",
                                    f"Arquivo de configuração criado em:\n{ARQUIVO_CONFIG}")
                return config_padrao
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar arquivo de configuração: {str(e)}")
                return config_padrao

    # ===== FUNÇÃO PARA ESCANEAR ARQUIVOS PDF DA PASTA =====
    def escanear_arquivos_pdf():
        """
        Escaneia a pasta em busca de todos os arquivos PDF e retorna uma lista
        com as informações de cada arquivo.
        """
        arquivos_encontrados = []

        if not os.path.exists(DIRETORIO_BASE):
            messagebox.showerror("Erro", f"Diretório não encontrado:\n{DIRETORIO_BASE}\n\n"
                                         "Verifique se o caminho está correto.")
            return arquivos_encontrados

        try:
            for arquivo in os.listdir(DIRETORIO_BASE):
                if arquivo.lower().endswith('.pdf') and not arquivo.startswith('~'):
                    caminho_completo = os.path.join(DIRETORIO_BASE, arquivo)
                    # Pega informações do arquivo
                    stats = os.stat(caminho_completo)
                    tamanho_kb = stats.st_size / 1024
                    data_modificacao = datetime.fromtimestamp(stats.st_mtime)

                    arquivos_encontrados.append({
                        'nome': arquivo,
                        'caminho': caminho_completo,
                        'tamanho_kb': tamanho_kb,
                        'data_modificacao': data_modificacao,
                        'localidade': determinar_localidade(arquivo)
                    })

            # Ordena por nome do arquivo
            arquivos_encontrados.sort(key=lambda x: x['nome'])
            return arquivos_encontrados

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao escanear arquivos: {str(e)}")
            return []

    # ===== FUNÇÃO PARA DETERMINAR A LOCALIDADE BASEADO NO NOME DO ARQUIVO =====
    def determinar_localidade(nome_arquivo):
        """
        Determina a localidade de um arquivo baseado nas palavras-chave do nome
        """
        nome_lower = nome_arquivo.lower()
        config = carregar_config_localidades()
        mapeamento = config.get("mapeamento", {})

        for localidade, palavras_chave in mapeamento.items():
            for palavra in palavras_chave:
                if palavra.lower() in nome_lower:
                    return localidade

        return "Não Classificado"

    # ===== FUNÇÃO PARA RECARREGAR ARQUIVOS (ATUALIZAR LISTA) =====
    def recarregar_arquivos():
        """Recarrega a lista de arquivos da pasta"""
        nonlocal todos_arquivos, arquivos_por_localidade
        todos_arquivos = escanear_arquivos_pdf()

        # Reorganiza os arquivos por localidade
        arquivos_por_localidade = {}
        config = carregar_config_localidades()
        for localidade in config.get("localidades", []):
            arquivos_por_localidade[localidade] = []

        # Adiciona categoria "Não Classificado" se necessário
        arquivos_por_localidade["Não Classificado"] = []

        for arquivo in todos_arquivos:
            localidade = arquivo['localidade']
            if localidade in arquivos_por_localidade:
                arquivos_por_localidade[localidade].append(arquivo)
            else:
                arquivos_por_localidade["Não Classificado"].append(arquivo)

        # Atualiza o label de total
        lbl_total.config(text=f"Total de Documentos: {len(todos_arquivos)}")

        return len(todos_arquivos)

    # ===== FUNÇÃO PARA ABRIR PDF =====
    def abrir_pdf(caminho):
        """Abre o arquivo PDF com o programa padrão do sistema"""
        if not os.path.exists(caminho):
            messagebox.showerror("Erro", f"Arquivo não encontrado:\n{caminho}")
            return

        try:
            os.startfile(caminho)  # Windows
        except AttributeError:
            try:
                import subprocess
                subprocess.run(['open', caminho])  # macOS
            except:
                webbrowser.open(caminho)  # Linux

    # ===== FUNÇÃO PARA EXIBIR ÍNDICE COMPLETO =====
    def exibir_indice_completo():
        """Exibe o índice completo de todos os arquivos PDF encontrados"""
        if not todos_arquivos:
            messagebox.showwarning("Atenção", "Nenhum arquivo PDF encontrado no diretório.")
            return

        janela_indice = Toplevel(frame_pesquisa)
        janela_indice.title("Índice de Arquivos PDF - Diretrizes")
        janela_indice.geometry("1150x600")
        janela_indice['bg'] = "#a4bad2"

        frame_indice = Frame(janela_indice, bg="#a4bad2")
        frame_indice.pack(fill=BOTH, expand=True, padx=10, pady=10)

        Label(frame_indice, text="ÍNDICE COMPLETO DE DIRETRIZES",
              bg="#024593", fg="white", font=("Arial", 14, "bold")).pack(fill=X, pady=5)

        Label(frame_indice, text=f"Total de arquivos: {len(todos_arquivos)} | Diretório: {DIRETORIO_BASE}",
              bg="#a4bad2", font=("Arial", 9)).pack(pady=5)

        # Treeview para exibir os arquivos
        colunas = ("Nome do Arquivo", "Localidade", "Tamanho (KB)", "Data Modificação")
        tree = ttk.Treeview(frame_indice, columns=colunas, show="headings", height=20)

        for col in colunas:
            tree.heading(col, text=col)
            if col == "Nome do Arquivo":
                tree.column(col, width=450)
            elif col == "Localidade":
                tree.column(col, width=200)
            elif col == "Tamanho (KB)":
                tree.column(col, width=100)
            else:
                tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(frame_indice, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Preencher com dados atualizados
        for arquivo in todos_arquivos:
            tree.insert("", END, values=(
                arquivo['nome'],
                arquivo['localidade'],
                f"{arquivo['tamanho_kb']:.2f} KB",
                arquivo['data_modificacao'].strftime("%d/%m/%Y %H:%M")
            ), tags=(arquivo['caminho'],))

        def on_double_click(event):
            item = tree.selection()[0]
            caminho = tree.item(item, "tags")[0]
            abrir_pdf(caminho)

        tree.bind("<Double-Button-1>", on_double_click)
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Botões
        frame_botoes = Frame(frame_indice, bg="#a4bad2")
        frame_botoes.pack(fill=X, pady=10)

        Button(frame_botoes, text="Abrir Selecionado",
               command=lambda: abrir_selecionado(tree),
               bg="#024593", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)

        Button(frame_botoes, text="Fechar", command=janela_indice.destroy,
               bg="#FF0000", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)

    def abrir_selecionado(tree):
        """Abre arquivo selecionado na treeview"""
        selecao = tree.selection()
        if selecao:
            caminho = tree.item(selecao[0], "tags")[0]
            abrir_pdf(caminho)
        else:
            messagebox.showwarning("Atenção", "Selecione um arquivo para abrir")

    # ===== FUNÇÃO PARA BUSCAR POR PALAVRA =====
    def buscar_por_palavra():
        """Busca arquivos por palavra-chave no nome"""
        palavra = entry_busca.get().strip().lower()
        if not palavra:
            messagebox.showwarning("Atenção", "Digite uma palavra para buscar")
            return  # ✅ Este return só sai da função, NÃO fecha a janela

        # Continua com a busca...
        resultados = [pdf for pdf in todos_arquivos if palavra in pdf['nome'].lower()]

        if resultados:
            exibir_resultados_busca(resultados, f"Resultados da busca por: '{palavra}'")
        else:
            messagebox.showinfo("Resultado", f"Nenhum arquivo encontrado com a palavra '{palavra}'")

    # ===== FUNÇÃO PARA BUSCAR POR LOCALIDADE =====
    def buscar_por_localidade():
        """Busca arquivos por localidade selecionada"""
        localidade_selecionada = combo_localidades.get()
        if not localidade_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma localidade")
            return

        resultados = arquivos_por_localidade.get(localidade_selecionada, [])

        if resultados:
            exibir_resultados_busca(resultados, f"Arquivos da localidade: {localidade_selecionada}")
        else:
            messagebox.showinfo("Resultado", f"Nenhum arquivo encontrado para a localidade {localidade_selecionada}")

    # ===== FUNÇÃO PARA EXIBIR RESULTADOS =====
    def exibir_resultados_busca(resultados, titulo):
        """Exibe os resultados da busca"""
        janela_resultados = Toplevel(frame_pesquisa)
        janela_resultados.title("Resultados da Busca - Diretrizes")
        janela_resultados.geometry("800x500")
        janela_resultados['bg'] = "#a4bad2"

        frame_resultados = Frame(janela_resultados, bg="#a4bad2")
        frame_resultados.pack(fill=BOTH, expand=True, padx=10, pady=10)

        Label(frame_resultados, text=titulo, bg="#024593", fg="white",
              font=("Arial", 12, "bold")).pack(fill=X, pady=5)

        Label(frame_resultados, text=f"Encontrados {len(resultados)} arquivo(s)",
              bg="#a4bad2", font=("Arial", 10)).pack(pady=5)

        frame_lista = Frame(frame_resultados, bg="#a4bad2")
        frame_lista.pack(fill=BOTH, expand=True)

        scrollbar = Scrollbar(frame_lista)
        scrollbar.pack(side=RIGHT, fill=Y)

        lista_resultados = Listbox(frame_lista, yscrollcommand=scrollbar.set,
                                   font=("Arial", 11), height=15)
        lista_resultados.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=lista_resultados.yview)

        caminhos_resultados = []
        for pdf in resultados:
            lista_resultados.insert(END, f"{pdf['nome']} - {pdf['localidade']} ({pdf['tamanho_kb']:.1f} KB)")
            caminhos_resultados.append(pdf['caminho'])

        def on_listbox_double_click(event):
            selecao = lista_resultados.curselection()
            if selecao:
                indice = selecao[0]
                abrir_pdf(caminhos_resultados[indice])

        lista_resultados.bind("<Double-Button-1>", on_listbox_double_click)

        frame_botoes = Frame(frame_resultados, bg="#a4bad2")
        frame_botoes.pack(fill=X, pady=10)

        Button(frame_botoes, text="Abrir Selecionado",
               command=lambda: abrir_selecionado_listbox(lista_resultados, caminhos_resultados),
               bg="#024593", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)

        Button(frame_botoes, text="Fechar", command=janela_resultados.destroy,
               bg="#FF0000", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)

    def abrir_selecionado_listbox(listbox, caminhos):
        """Abre arquivo selecionado na listbox"""
        selecao = listbox.curselection()
        if selecao:
            indice = selecao[0]
            abrir_pdf(caminhos[indice])
        else:
            messagebox.showwarning("Atenção", "Selecione um arquivo para abrir")

    # ===== INICIALIZAÇÃO =====
    # Carregar configuração e escanear arquivos
    config = carregar_config_localidades()
    todos_arquivos = escanear_arquivos_pdf()

    # Organizar por localidade
    arquivos_por_localidade = {}
    for localidade in config.get("localidades", []):
        arquivos_por_localidade[localidade] = []
    arquivos_por_localidade["Não Classificado"] = []

    for arquivo in todos_arquivos:
        localidade = arquivo['localidade']
        if localidade in arquivos_por_localidade:
            arquivos_por_localidade[localidade].append(arquivo)
        else:
            arquivos_por_localidade["Não Classificado"].append(arquivo)

    # Lista de localidades para o combo
    lista_localidades = config.get("localidades", []) + ["Não Classificado"]

    # ===== CRIAÇÃO DA JANELA PRINCIPAL =====
    frame_pesquisa = Toplevel(root)
    frame_pesquisa.title('DIRETRIZES - Pesquisa de Documentos PDF')
    frame_pesquisa.geometry('850x650')
    frame_pesquisa.resizable(False, False)
    frame_pesquisa['bg'] = "#a4bad2"

    # Título
    titulo = Label(frame_pesquisa, text='DIRETRIZES', font=('Arial', '18', 'bold'),
                   bg="#024593", fg="white", height=2)
    titulo.pack(fill=X)

    # Frame principal
    main_frame = Frame(frame_pesquisa, bg="#a4bad2")
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=15)

    # ===== LINHA SUPERIOR COM BOTÃO DE RECARREGAR E INFORMAÇÕES =====
    frame_superior = Frame(main_frame, bg="#a4bad2")
    frame_superior.pack(fill=X, pady=(0, 10))
    """
    # Botão Recarregar em destaque no topo
    btn_recarregar = Button(frame_superior, text="🔄 RECARREGAR ARQUIVOS",
                            command=lambda: [recarregar_arquivos(),
                                             messagebox.showinfo("Atualizado",
                                                                 f"Lista recarregada!\nTotal de arquivos: {len(todos_arquivos)}")],
                            bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                            padx=20, pady=8)
    btn_recarregar.pack(side=LEFT, padx=(0, 20))
    """
    # Informações do diretório
    frame_info_top = Frame(frame_superior, bg="#a4bad2", relief="groove", bd=1)
    frame_info_top.pack(side=LEFT, fill=X, expand=True)
    """
    Label(frame_info_top, text=f"📁 {DIRETORIO_BASE}",
          bg="#a4bad2", font=("Arial", 9), fg="blue", anchor="w").pack(fill=X, padx=5, pady=2)
    """
    lbl_total = Label(frame_info_top, text=f"📄 Total de Documentos para consulta: {len(todos_arquivos)}",
                      bg="#a4bad2", font=("Arial", 9, "bold"), anchor="w")
    lbl_total.pack(fill=X, padx=5, pady=2)

    # ===== OPÇÃO 1: ACESSO DIRETO PELO ÍNDICE =====
    frame_indice = LabelFrame(main_frame, text="1. Busca Direto pelo Índice",
                              bg="#a4bad2", font=("Arial", 12, "bold"),
                              fg="#024593", relief="groove", bd=2)
    frame_indice.pack(fill=X, pady=(0, 15))

    Label(frame_indice,
          text="Exibe todos os arquivos PDF encontrados no diretório.\nClique duas vezes sobre qualquer arquivo para abri-lo.",
          bg="#a4bad2", font=("Arial", 9), justify=LEFT).pack(pady=(8, 5))

    Button(frame_indice, text="📑 Exibir Índice Completo", command=exibir_indice_completo,
           bg="#024593", fg="white", font=("Arial", 11, "bold"), height=1).pack(pady=10)

    # ===== OPÇÃO 2: BUSCA POR PALAVRA-CHAVE =====
    frame_palavra = LabelFrame(main_frame, text="2. Busca por Palavra-Chave",
                               bg="#a4bad2", font=("Arial", 12, "bold"),
                               fg="#024593", relief="groove", bd=2)
    frame_palavra.pack(fill=X, pady=(0, 15))

    Label(frame_palavra, text="Digite a palavra desejada para buscar nos nomes dos documentos:",
          bg="#a4bad2", font=("Arial", 10)).pack(pady=5)

    entry_busca = Entry(frame_palavra, font=("Arial", 11), width=50)
    entry_busca.pack(pady=5)

    Button(frame_palavra, text="🔍 Buscar por Palavra", command=buscar_por_palavra,
           bg="#024593", fg="white", font=("Arial", 11, "bold"), width=20).pack(pady=10)

    # ===== OPÇÃO 3: BUSCA POR LOCALIDADE =====
    frame_localidade = LabelFrame(main_frame, text="3. Busca por Localidade",
                                  bg="#a4bad2", font=("Arial", 12, "bold"),
                                  fg="#024593", relief="groove", bd=2)
    frame_localidade.pack(fill=X, pady=(0, 15))

    Label(frame_localidade, text="Selecione uma das localidades disponíveis:",
          bg="#a4bad2", font=("Arial", 10)).pack(pady=5)

    combo_localidades = ttk.Combobox(frame_localidade, values=lista_localidades,
                                     font=("Arial", 11), state="readonly", width=40)
    combo_localidades.pack(pady=5)

    Button(frame_localidade, text="🔍 Buscar por Localidade", command=buscar_por_localidade,
           bg="#024593", fg="white", font=("Arial", 11, "bold"), width=20).pack(pady=10)

    # Botão Fechar
    Button(main_frame, text="Fechar", command=frame_pesquisa.destroy,
           bg="#FF0000", fg="white", font=("Arial", 11, "bold"), width=15).pack(pady=10)


# =============================================================================================
# CLICK_22 - DESTAQUE DA INSTALAÇÃO NOS PROCEDIMENTOS ONS
# Ao abrir um cadastro/instrução, o PDF atualizado é baixado, as ocorrências da Usina/Subestação
# selecionada são destacadas no próprio arquivo e uma janela permite navegar entre elas.
# Requer PyMuPDF (pip install pymupdf). Sem ele, o Click_22 funciona como antes (navegador).
# =============================================================================================

# Termos procurados no PDF para cada localidade do Click_22.
# A busca ignora acentos, maiúsculas/minúsculas, hífens e quebras de linha.
# Para incluir siglas ou nomes alternativos (ex.: "FGO"), basta acrescentar na lista.
TERMOS_BUSCA_INSTALACAO = {
    "UHE Müller de Godoy Pereira": ["Müller de Godoy Pereira", "Muller de Godoy", "Godoy Pereira", "J.L.M.G.PEREIRA" , "JLM G. PEREIRA", "Eng.José Luiz","Foz do Rio Claro", "ALUPAR", "AF ENERGIA"],
    "UHE São José": ["São José", "ALUPAR", "AF ENERGIA"],
    "UHE Ferreira Gomes": ["Ferreira Gomes", "ALUPAR", "AF ENERGIA"],
    "SE Macapá": ["F.Gomes", "F. Gomes", "Ferreira Gomes", "ALUPAR", "AF ENERGIA"],
    "SE Itaguaçu": ["J.L.M.G.PEREIRA" , "JLM G. PEREIRA", "Eng.José Luiz", "Müller de Godoy Pereira", "Muller de Godoy", "Godoy Pereira","Foz do Rio Claro", "ALUPAR", "AF ENERGIA"],
    "SE Russas-II": ["Russas II", "Russas 2", "Pitombeira", "ALUPAR", "AF ENERGIA"],
    "CGE Pitombeira": ["Pitombeira", "Ubatuba", "Santa Catarina", "Ventos de horizonte", "Goiabeira", "ALUPAR", "AF ENERGIA"],
    "CGE Jandaíra-III": ["Jandaíra III", "Jandaíra 3", "ALUPAR", "AF ENERGIA"],
    "UFV Pitombeira": ["Pitombeira", "ALUPAR", "AF ENERGIA"],
}

COR_DESTAQUE_PDF = (1.0, 0.92, 0.23)  # amarelo marca-texto
REGEX_NUMERO_SECAO = re.compile(r"^(\d{1,2}\.(?:\d{1,2}\.?)*)\s+(\S.{1,150})$")


def normalizar_texto_busca(texto):
    """Remove acentos e padroniza maiúsculas/minúsculas para comparação."""
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.casefold()


def tokenizar_busca(texto):
    """Quebra o texto em palavras normalizadas (letras e números)."""
    return re.findall(r"[a-z0-9]+", normalizar_texto_busca(texto))


def termos_busca_padrao(localidade):
    """Termos de busca sugeridos para a localidade (configuração ou nome sem o prefixo)."""
    if localidade in TERMOS_BUSCA_INSTALACAO:
        return list(TERMOS_BUSCA_INSTALACAO[localidade])
    nome = re.sub(r"^(UHE|UTE|PCH|CGH|SE|CGE|EOL|UFV|LT)\s+", "", localidade.strip(), flags=re.IGNORECASE)
    return [nome.replace("-", " ")]


def _titulos_secao_da_pagina(pagina, textpage):
    """Identifica títulos numerados (ex.: '6.2. RECOMPOSIÇÃO') em negrito ou caixa alta."""
    titulos = []
    for bloco in pagina.get_text("dict", textpage=textpage).get("blocks", []):
        for linha in bloco.get("lines", []):
            spans = [s for s in linha.get("spans", []) if s.get("text", "").strip()]
            if not spans:
                continue
            texto = " ".join("".join(s["text"] for s in spans).split())
            achado = REGEX_NUMERO_SECAO.match(texto)
            if not achado:
                continue
            negrito = all((s.get("flags", 0) & 16) or "bold" in s.get("font", "").lower() for s in spans)
            letras = [c for c in achado.group(2) if c.isalpha()]
            caixa_alta = len(letras) >= 3 and all(c.isupper() for c in letras)
            if negrito or caixa_alta:
                titulos.append((linha["bbox"][1], texto[:120]))
    return sorted(titulos)


def localizar_ocorrencias_pdf(doc, termos):
    """
    Procura os termos em todas as páginas do PDF.
    Retorna (ocorrencias, paginas_com_texto). Cada ocorrência é um dict com:
    pagina (base 0), rects (retângulos das palavras), termo, trecho (parágrafo/célula),
    secao (último título numerado anterior) e repetida (cabeçalho/rodapé repetido).
    """
    termos_tokens = []
    for termo in termos:
        tokens = tokenizar_busca(termo)
        if tokens and (termo, tokens) not in termos_tokens:
            termos_tokens.append((termo, tokens))
    termos_tokens.sort(key=lambda t: len(t[1]), reverse=True)  # o termo mais longo tem prioridade

    ocorrencias = []
    paginas_com_texto = 0
    secao_atual = ""

    for num_pagina, pagina in enumerate(doc):
        textpage = pagina.get_textpage()
        palavras = pagina.get_text("words", textpage=textpage, sort=True)
        if palavras:
            paginas_com_texto += 1
        blocos = {b[5]: " ".join(b[4].split()) for b in pagina.get_text("blocks", textpage=textpage)}
        titulos = _titulos_secao_da_pagina(pagina, textpage)

        # Cada palavra do PDF pode gerar mais de um token (ex.: "Russas-II" → russas, ii)
        tokens = []
        for indice, palavra in enumerate(palavras):
            for token in tokenizar_busca(palavra[4]):
                tokens.append((token, indice))
        sequencia = [t[0] for t in tokens]

        achados = []
        i = 0
        while i < len(sequencia):
            casou = None
            for termo, alvo in termos_tokens:
                if sequencia[i:i + len(alvo)] == alvo:
                    casou = (termo, alvo)
                    break
            if not casou:
                i += 1
                continue
            termo, alvo = casou
            indices = sorted({tokens[k][1] for k in range(i, i + len(alvo))})
            rects = []
            for k in indices:  # une palavras da mesma linha em um único retângulo
                r = fitz.Rect(palavras[k][:4])
                if rects and abs(rects[-1].y0 - r.y0) < 2 and 0 <= r.x0 - rects[-1].x1 < 15:
                    rects[-1] |= r
                else:
                    rects.append(r)
            achados.append((rects[0].y0, termo, rects, palavras[indices[0]][5]))
            i += len(alvo)

        for y, termo, rects, bloco in achados:
            for y_titulo, titulo in titulos:
                if y_titulo <= y + 1:
                    secao_atual = titulo
            ocorrencias.append({
                "pagina": num_pagina,
                "rects": rects,
                "termo": termo,
                "trecho": blocos.get(bloco, ""),
                "secao": secao_atual,
                "repetida": False,
            })
        if titulos:
            secao_atual = titulos[-1][1]

    # Marca como repetidas as ocorrências de cabeçalho/rodapé (mesmo texto em muitas páginas)
    paginas_por_texto = {}
    for oc in ocorrencias:
        chave = re.sub(r"\d+", "#", normalizar_texto_busca(oc["trecho"]))
        paginas_por_texto.setdefault(chave, set()).add(oc["pagina"])
    limite = max(3, 0.5 * len(doc))
    for oc in ocorrencias:
        chave = re.sub(r"\d+", "#", normalizar_texto_busca(oc["trecho"]))
        oc["repetida"] = len(paginas_por_texto[chave]) >= limite

    return ocorrencias, paginas_com_texto


def aplicar_destaques_pdf(doc, ocorrencias, localidade):
    """Grava os destaques no PDF e acrescenta marcadores (bookmarks) para navegação."""
    paginas = {}  # mantém a referência da página enquanto a anotação é editada
    for oc in ocorrencias:
        pagina = paginas.setdefault(oc["pagina"], doc[oc["pagina"]])
        annot = pagina.add_highlight_annot(oc["rects"])
        annot.set_colors(stroke=COR_DESTAQUE_PDF)
        annot.set_info(title="COG - Click_22", content=f"Ocorrência: {localidade} ({oc['termo']})")
        annot.update()

    relevantes = [oc for oc in ocorrencias if not oc["repetida"]] or ocorrencias
    if not relevantes:
        return
    marcadores = [[1, f"★ OCORRÊNCIAS - {localidade} ({len(relevantes)})", relevantes[0]["pagina"] + 1]]
    for oc in relevantes[:300]:
        trecho = oc["trecho"] if len(oc["trecho"]) <= 70 else oc["trecho"][:67] + "..."
        marcadores.append([2, f"Pág. {oc['pagina'] + 1} - {trecho}", oc["pagina"] + 1])
    try:
        existentes = [m[:3] for m in doc.get_toc(simple=True) if 1 <= m[2] <= len(doc)]
        doc.set_toc(marcadores + existentes)
    except Exception:
        try:
            doc.set_toc(marcadores)
        except Exception:
            pass  # marcadores são um complemento; os destaques já foram aplicados


def montar_resumo_ocorrencias(ocorrencias, localidade):
    """Resumo textual agrupado por seção do procedimento, sem trechos duplicados."""
    relevantes = [oc for oc in ocorrencias if not oc["repetida"]] or ocorrencias
    secoes = {}
    for oc in relevantes:
        secao = oc["secao"] or "(Início do documento)"
        grupo = secoes.setdefault(secao, {"paginas": [], "trechos": []})
        if oc["pagina"] + 1 not in grupo["paginas"]:
            grupo["paginas"].append(oc["pagina"] + 1)
        if oc["trecho"] and oc["trecho"] not in grupo["trechos"]:
            grupo["trechos"].append(oc["trecho"])

    linhas = [f"RESUMO - Trechos do procedimento relacionados a {localidade}",
              f"{len(relevantes)} ocorrência(s) em {len(secoes)} seção(ões)", ""]
    for secao, grupo in secoes.items():
        paginas = ", ".join(str(p) for p in grupo["paginas"])
        linhas.append(f"■ {secao}   [pág. {paginas}]")
        for trecho in grupo["trechos"]:
            linhas.append(f"   • {trecho if len(trecho) <= 600 else trecho[:597] + '...'}")
        linhas.append("")
    return "\n".join(linhas)


def gerar_pdf_destacado(url_pdf, termos, localidade, pasta_destino=None):
    """
    Baixa o PDF atualizado, destaca as ocorrências e salva uma cópia local.
    Retorna (doc, ocorrencias, caminho_salvo). Lança ValueError com mensagem
    amigável quando o destaque não é possível (PDF digitalizado, sem ocorrências...).
    """
    resposta = requests.get(url_pdf, timeout=(5, 60))
    resposta.raise_for_status()

    doc = fitz.open(stream=resposta.content, filetype="pdf")
    if doc.needs_pass:
        doc.close()
        raise ValueError("O PDF está protegido por senha.")

    ocorrencias, paginas_com_texto = localizar_ocorrencias_pdf(doc, termos)
    if paginas_com_texto == 0:
        doc.close()
        raise ValueError("O PDF não possui camada de texto (documento digitalizado).")
    if not ocorrencias:
        doc.close()
        raise ValueError(f"Nenhuma ocorrência de {' / '.join(termos)} foi encontrada no documento.")

    aplicar_destaques_pdf(doc, ocorrencias, localidade)

    pasta_destino = pasta_destino or os.path.join(tempfile.gettempdir(), "COG_Procedimentos_ONS")
    os.makedirs(pasta_destino, exist_ok=True)
    nome_original = os.path.splitext(os.path.basename(requests.utils.unquote(url_pdf)))[0]
    sufixo = re.sub(r"[^A-Za-z0-9]+", "_", normalizar_texto_busca(localidade)).strip("_")
    caminho = os.path.join(pasta_destino,
                           f"{nome_original}_{sufixo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    doc.save(caminho)
    return doc, ocorrencias, caminho


# ---------------------------------------------------------------------------------------------
# CLICK_22 - ÚLTIMA REVISÃO JÁ ENCONTRADA DE CADA DOCUMENTO
# A busca começa por ela (e pelas JANELA_REVISAO_NOVA revisões acima, caso o ONS tenha publicado uma
# nova) e só varre todas as revisões quando não achar. O arquivo fica na pasta temporária do
# Click_22 (fora da pasta do projeto, para não ir para o Git); se for apagado, a busca completa refaz.
# ---------------------------------------------------------------------------------------------
ARQUIVO_REVISOES_CONHECIDAS = os.path.join(tempfile.gettempdir(), "COG_Procedimentos_ONS", "ultimas_revisoes.json")
JANELA_REVISAO_NOVA = 30
_REVISOES_CONHECIDAS = {}   # url_base -> última revisão encontrada
_REVISOES_CARREGADAS = False
_TRAVA_REVISOES = threading.Lock()


def _carregar_revisoes_conhecidas():
    """Lê o arquivo uma única vez por execução (chamar com _TRAVA_REVISOES adquirida)."""
    global _REVISOES_CARREGADAS
    if _REVISOES_CARREGADAS:
        return
    _REVISOES_CARREGADAS = True
    try:
        with open(ARQUIVO_REVISOES_CONHECIDAS, encoding="utf-8") as arquivo:
            for url_base, revisao in json.load(arquivo).items():
                if isinstance(revisao, int):
                    _REVISOES_CONHECIDAS[url_base] = revisao
    except (OSError, ValueError, AttributeError):
        pass  # primeiro uso ou arquivo ilegível: a busca completa refaz


def obter_revisao_conhecida(url_base):
    with _TRAVA_REVISOES:
        _carregar_revisoes_conhecidas()
        return _REVISOES_CONHECIDAS.get(url_base)


def registrar_revisao_conhecida(url_base, revisao):
    with _TRAVA_REVISOES:
        _carregar_revisoes_conhecidas()
        if _REVISOES_CONHECIDAS.get(url_base) == revisao:
            return
        _REVISOES_CONHECIDAS[url_base] = revisao
        try:
            os.makedirs(os.path.dirname(ARQUIVO_REVISOES_CONHECIDAS), exist_ok=True)
            temporario = ARQUIVO_REVISOES_CONHECIDAS + ".tmp"
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(_REVISOES_CONHECIDAS, arquivo, ensure_ascii=False, indent=1)
            os.replace(temporario, ARQUIVO_REVISOES_CONHECIDAS)
        except OSError:
            pass  # o cache é só um atalho; sem ele a busca funciona normalmente


# ---------------------------------------------------------------------------------------------
# CLICK_22 - BOTÃO COM TEXTO DE APOIO DENTRO (ex.: "Clique para acessar")
# ---------------------------------------------------------------------------------------------
class BotaoComRotulo(Frame):
    """Botão com título e uma linha de apoio dentro da própria área clicável.

    Antes o texto "Clique para acessar" era um Label solto abaixo do botão e as pessoas clicavam
    nele em vez de no botão. Agora o título, o texto de apoio e o fundo fazem parte do mesmo botão:
    qualquer clique em qualquer parte dele aciona o comando (também responde a Enter/Espaço
    quando recebe o foco pelo teclado). A cor do texto de apoio é escolhida por fg_rotulo."""

    def __init__(self, master, texto, rotulo, comando, bg, fg="white", fg_rotulo=None,
                 largura=250, altura=64, fonte=("Arial", 10, "bold"), fonte_rotulo=("Arial", 8)):
        cor = _ui_cor("bg", bg)  # mesma conversão de cores que o Button do tema aplica
        Frame.__init__(self, master, bg=cor, width=largura, height=altura, cursor="hand2",
                       highlightthickness=2, highlightbackground=cor, highlightcolor="white", takefocus=1)
        self._cor = cor
        self._cor_hover = _ui_escurecer(cor)
        self._cor_pressionado = _ui_escurecer(cor, 0.7)
        self._comando = comando

        # O Frame mantém o tamanho pedido (só tem filhos posicionados com place)
        miolo = Frame(self, bg=cor, cursor="hand2")
        miolo.place(relx=0.5, rely=0.5, anchor="center")
        lbl_titulo = Label(miolo, text=texto, bg=cor, fg=fg, font=fonte, justify="center",
                           wraplength=largura - 24, cursor="hand2")
        lbl_titulo.pack()
        lbl_rotulo = Label(miolo, text=rotulo, bg=cor, fg=fg_rotulo or fg, font=fonte_rotulo,
                           cursor="hand2")
        lbl_rotulo.pack(pady=(2, 0))

        self._partes = (self, miolo, lbl_titulo, lbl_rotulo)
        for parte in self._partes:
            parte.bind("<Enter>", lambda e: self._pintar(self._cor_hover))
            parte.bind("<Leave>", self._ao_sair)
            parte.bind("<ButtonPress-1>", lambda e: self._pintar(self._cor_pressionado))
            parte.bind("<ButtonRelease-1>", self._ao_soltar)
        self.bind("<Return>", lambda e: self.invocar())
        self.bind("<space>", lambda e: self.invocar())

    def _pintar(self, cor):
        self.configure(bg=cor, highlightbackground=cor)
        for parte in self._partes[1:]:
            parte.configure(bg=cor)

    def _mouse_dentro(self, x_tela, y_tela):
        try:
            return self.winfo_containing(x_tela, y_tela) in self._partes
        except Exception:
            return False

    def _ao_sair(self, _evento=None):
        # Ao passar do fundo para o texto (ou vice-versa) o mouse continua dentro do botão
        try:
            if not self._mouse_dentro(*self.winfo_pointerxy()):
                self._pintar(self._cor)
        except Exception:
            pass  # janela já fechada

    def _ao_soltar(self, evento):
        if self._mouse_dentro(evento.x_root, evento.y_root):
            self._pintar(self._cor_hover)
            self.invocar()
        else:
            self._pintar(self._cor)

    def invocar(self):
        if self._comando:
            self._comando()


# ---------------------------------------------------------------------------------------------
# CLICK_22 - RESUMO DO PROCEDIMENTO (seção "1. OBJETIVO" lida direto do PDF no site do ONS)
# ---------------------------------------------------------------------------------------------
# O título "1. OBJETIVO" aparece sozinho na linha no corpo do documento; no índice ele vem seguido
# de pontilhado e número de página, por isso não confunde. A seção termina no título "2. XXXX".
REGEX_OBJETIVO_INICIO = re.compile(r"^[ \t]*1\.?[ \t]*\n?[ \t]*OBJETIVOS?[ \t]*$", re.IGNORECASE | re.MULTILINE)
REGEX_OBJETIVO_FIM = re.compile(r"^[ \t]*2\.[ \t]*\n?[ \t]*[A-ZÀ-Ý]{3}", re.MULTILINE)
# Início de item dentro do objetivo: marcador, "1.1." (sozinho ou seguido de maiúscula), "a)" ou "1)".
# "5.5 dos Procedimentos de Rede" (minúscula) é continuação da frase, não um item novo.
REGEX_NOVO_PARAGRAFO = re.compile(r"^(?:[-•–·▪]\s|\d+(?:\.\d+)+\.?(?:\s+[A-ZÀ-Ý]|$)|\d+\)\s|[A-Za-z]\)\s)")
LIMITE_OBJETIVO_SEM_FIM = 2500   # caracteres lidos se o título da seção seguinte não for encontrado
PAGINAS_LIDAS_RESUMO = 40        # o objetivo vem após a capa e o índice (que chega a 10 páginas nos PDFs maiores)
PAGINAS_JANELA_OBJETIVO = 6      # páginas lidas a partir do título (o objetivo pode passar de página)
VALIDADE_CACHE_RESUMO = timedelta(hours=6)
_CACHE_RESUMO_ONS = {}           # url_base -> (data_hora, resumo)


def _remover_cabecalho_rodape(textos_paginas):
    """Tira de cada página as linhas que se repetem na maioria delas (cabeçalho, rodapé, nº da página)."""
    chaves_por_pagina = [{re.sub(r"\d+", "#", l.strip()) for l in t.splitlines() if l.strip()}
                         for t in textos_paginas]
    contagem = {}
    for chaves in chaves_por_pagina:
        for chave in chaves:
            contagem[chave] = contagem.get(chave, 0) + 1
    limite = max(3, 0.5 * len(textos_paginas))
    return ["\n".join(l for l in t.splitlines() if contagem.get(re.sub(r"\d+", "#", l.strip()), 0) < limite)
            for t in textos_paginas]


def _reformatar_paragrafos(texto):
    """Junta as quebras de linha do PDF em parágrafos corridos, preservando itens numerados e marcadores."""
    paragrafos, atual = [], []
    for linha in texto.splitlines():
        linha = " ".join(linha.split())
        if not re.search(r"\w", linha):
            continue
        if atual and REGEX_NOVO_PARAGRAFO.match(linha):
            paragrafos.append(" ".join(atual))
            atual = []
        atual.append(linha)
    if atual:
        paragrafos.append(" ".join(atual))
    return "\n\n".join(paragrafos)


def extrair_objetivo_pdf(doc, max_paginas=PAGINAS_LIDAS_RESUMO):
    """Devolve (texto_do_objetivo, pagina_base_1) lido da seção '1. OBJETIVO' do procedimento.
    Lança ValueError com mensagem amigável quando a seção não puder ser lida."""
    pagina_inicio, paginas_com_texto = None, 0
    for numero in range(min(len(doc), max_paginas)):
        texto = doc[numero].get_text("text")
        paginas_com_texto += bool(texto.strip())
        if REGEX_OBJETIVO_INICIO.search(texto):
            pagina_inicio = numero
            break
    if paginas_com_texto == 0:
        raise ValueError("O PDF não possui camada de texto (documento digitalizado).")
    if pagina_inicio is None:
        raise ValueError("Não foi possível localizar a seção '1. OBJETIVO' neste documento.")

    ultima = min(len(doc), pagina_inicio + PAGINAS_JANELA_OBJETIVO)
    paginas = _remover_cabecalho_rodape([doc[i].get_text("text") for i in range(pagina_inicio, ultima)])
    inicio = REGEX_OBJETIVO_INICIO.search(paginas[0])
    resto = paginas[0][inicio.end():] + "\n" + "\n".join(paginas[1:])  # o objetivo pode passar de página
    fim = REGEX_OBJETIVO_FIM.search(resto)
    objetivo = _reformatar_paragrafos(resto[:fim.start()] if fim else resto[:LIMITE_OBJETIVO_SEM_FIM])
    if not objetivo:
        raise ValueError("A seção '1. OBJETIVO' deste documento está vazia.")
    return objetivo, pagina_inicio + 1


def extrair_identificacao_pdf(doc):
    """Título, código, revisão e vigência lidos da capa do procedimento (melhor esforço: pode vir vazio)."""
    info = {"titulo": "", "codigo": "", "revisao": "", "vigencia": ""}
    try:
        texto = doc[0].get_text("text")
        achado = re.search(r"C[óo]digo\s+Revis[ãa]o\s+Item\s+Vig[êe]ncia\s+(\S+)\s+(\d+)\s+\S+\s+(\d{2}/\d{2}/\d{4})",
                           texto)
        if achado:
            info.update(codigo=achado.group(1), revisao=achado.group(2), vigencia=achado.group(3))
        capa = re.search(r"Subm[óo]dulo\s+[\d.]+[^\n]*\n(.*?)(?=\n\s*C[óo]digo\b|\n[\s.]*MOTIVO DA)", texto, re.DOTALL)
        if capa:
            linhas = [" ".join(l.split()) for l in capa.group(1).splitlines() if l.strip(" .\t")]
            info["titulo"] = (f"{linhas[0].rstrip(' .')} - {' '.join(linhas[1:])}" if len(linhas) > 1
                              else " ".join(linhas))
    except Exception:
        pass  # a identificação é um complemento; o objetivo continua sendo exibido
    return info


def obter_resumo_objetivo(url_pdf):
    """Baixa o PDF no site do ONS e devolve o resumo (objetivo + identificação do documento)."""
    resposta = requests.get(url_pdf, timeout=(5, 60))
    resposta.raise_for_status()
    doc = fitz.open(stream=resposta.content, filetype="pdf")
    try:
        if doc.needs_pass:
            raise ValueError("O PDF está protegido por senha.")
        objetivo, pagina = extrair_objetivo_pdf(doc)
        resumo = extrair_identificacao_pdf(doc)
    finally:
        doc.close()
    resumo.update(objetivo=objetivo, pagina=pagina)
    return resumo


def abrir_visualizador_destaque(doc, ocorrencias, localidade, subtipo, caminho_pdf, url_original):
    """Janela com a lista de ocorrências, resumo por seção e a página com os destaques."""

    janela = Toplevel(root)
    janela.title(f"Procedimento ONS - {localidade} - {subtipo}")
    janela.geometry("1250x820")
    janela['bg'] = "#a4bad2"

    estado = {"lista": [], "atual": -1, "zoom": 1.5, "imagem": None, "pagina_render": None}
    var_repetidas = BooleanVar(value=False)

    Label(janela, text=f"🖍 {localidade} - {subtipo}", font=('Arial', '14', 'bold'),
          bg="#024593", fg="white", height=2).pack(fill='x')

    # ----- Barra de navegação -----
    barra = Frame(janela, bg="#a4bad2")
    barra.pack(fill='x', padx=10, pady=6)

    lbl_contador = Label(barra, text="", bg="#a4bad2", font=("Arial", 11, "bold"), fg="#024593", width=22)

    Button(barra, text="◀ Anterior", command=lambda: navegar(-1), bg="#024593", fg="white",
           font=("Arial", 10, "bold"), width=11).pack(side=LEFT, padx=3)
    lbl_contador.pack(side=LEFT, padx=3)
    Button(barra, text="Próxima ▶", command=lambda: navegar(1), bg="#024593", fg="white",
           font=("Arial", 10, "bold"), width=11).pack(side=LEFT, padx=3)
    Button(barra, text="🔍 −", command=lambda: alterar_zoom(-0.25), font=("Arial", 10), width=4).pack(side=LEFT, padx=(15, 2))
    Button(barra, text="🔍 +", command=lambda: alterar_zoom(0.25), font=("Arial", 10), width=4).pack(side=LEFT, padx=2)
    Checkbutton(barra, text="Incluir cabeçalhos/rodapés", variable=var_repetidas,
                command=lambda: preencher_lista(), bg="#a4bad2", font=("Arial", 9)).pack(side=LEFT, padx=8)

    Button(barra, text="Fechar", command=lambda: fechar(), bg="#FF0000", fg="white",
           font=("Arial", 10, "bold"), width=10).pack(side=RIGHT, padx=3)
    Button(barra, text="🌐 Original (navegador)", command=lambda: webbrowser.open(url_original),
           bg="#34495E", fg="white", font=("Arial", 9, "bold")).pack(side=RIGHT, padx=3)
    Button(barra, text="📄 Abrir PDF destacado", command=lambda: abrir_pdf(caminho_pdf),
           bg="#2ECC71", fg="white", font=("Arial", 9, "bold")).pack(side=RIGHT, padx=3)

    corpo = PanedWindow(janela, orient=HORIZONTAL, bg="#a4bad2", sashwidth=6)
    corpo.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

    # ----- Painel esquerdo: ocorrências e resumo -----
    abas = ttk.Notebook(corpo)
    frame_lista = Frame(abas)
    lista = Listbox(frame_lista, font=("Consolas", 9), activestyle="none", selectbackground="#00ffff", exportselection=False)
    scroll_lista = Scrollbar(frame_lista, orient=VERTICAL, command=lista.yview)
    lista.configure(yscrollcommand=scroll_lista.set)
    scroll_lista.pack(side=RIGHT, fill=Y)
    lista.pack(side=LEFT, fill=BOTH, expand=True)
    abas.add(frame_lista, text="Ocorrências")

    frame_resumo = Frame(abas)
    texto_resumo = Text(frame_resumo, wrap="word", font=("Arial", 9), bg="#FFFDF0")
    scroll_resumo = Scrollbar(frame_resumo, orient=VERTICAL, command=texto_resumo.yview)
    texto_resumo.configure(yscrollcommand=scroll_resumo.set)
    scroll_resumo.pack(side=RIGHT, fill=Y)
    texto_resumo.pack(side=LEFT, fill=BOTH, expand=True)
    resumo = montar_resumo_ocorrencias(ocorrencias, localidade)
    texto_resumo.insert("1.0", resumo)
    texto_resumo.configure(state="disabled")

    def copiar_resumo():
        janela.clipboard_clear()
        janela.clipboard_append(resumo)
        messagebox.showinfo("Resumo", "Resumo copiado para a área de transferência.", parent=janela)

    Button(frame_resumo, text="📋 Copiar", command=copiar_resumo, font=("Arial", 8)).place(relx=1.0, x=-22, y=2, anchor="ne")
    abas.add(frame_resumo, text="Resumo por seção")
    corpo.add(abas, width=420)

    # ----- Painel direito: página renderizada -----
    frame_pagina = Frame(corpo, bg="#555")
    canvas = Canvas(frame_pagina, bg="#777", highlightthickness=0)
    scroll_v = Scrollbar(frame_pagina, orient=VERTICAL, command=canvas.yview)
    scroll_h = Scrollbar(frame_pagina, orient=HORIZONTAL, command=canvas.xview)
    canvas.configure(yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)
    scroll_v.pack(side=RIGHT, fill=Y)
    scroll_h.pack(side=BOTTOM, fill=X)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    corpo.add(frame_pagina)

    lbl_rodape = Label(janela, text="", bg="#a4bad2", font=("Arial", 8), fg="#333", anchor="w")
    lbl_rodape.pack(fill='x', padx=10, pady=(0, 6))

    def preencher_lista():
        estado["lista"] = [oc for oc in ocorrencias if var_repetidas.get() or not oc["repetida"]] or ocorrencias
        lista.delete(0, END)
        for oc in estado["lista"]:
            trecho = oc["trecho"] if len(oc["trecho"]) <= 90 else oc["trecho"][:87] + "..."
            lista.insert(END, f"Pág. {oc['pagina'] + 1:>3} │ {trecho}")
        estado["atual"] = -1
        mostrar(0)

    def mostrar(indice):
        if not estado["lista"]:
            return
        indice = max(0, min(indice, len(estado["lista"]) - 1))
        estado["atual"] = indice
        oc = estado["lista"][indice]
        pagina = doc[oc["pagina"]]
        zoom = estado["zoom"]

        if estado["pagina_render"] != (oc["pagina"], zoom):
            pix = pagina.get_pixmap(matrix=fitz.Matrix(zoom, zoom), annots=True)
            estado["imagem"] = PhotoImage(data=base64.b64encode(pix.tobytes("png")).decode("ascii"))
            estado["pagina_render"] = (oc["pagina"], zoom)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=estado["imagem"])
            canvas.configure(scrollregion=(0, 0, pix.width, pix.height))
        canvas.delete("marcador")

        transformacao = pagina.rotation_matrix * fitz.Matrix(zoom, zoom)
        topo = None
        for r in oc["rects"]:
            rr = fitz.Rect(r) * transformacao
            canvas.create_rectangle(rr.x0 - 3, rr.y0 - 3, rr.x1 + 3, rr.y1 + 3,
                                    outline="#E00000", width=3, tags="marcador")
            topo = rr.y0 if topo is None else min(topo, rr.y0)

        altura = max(1, estado["imagem"].height())
        canvas.update_idletasks()
        visivel = canvas.winfo_height()
        canvas.yview_moveto(max(0.0, (topo - visivel / 3) / altura))

        lista.selection_clear(0, END)
        lista.selection_set(indice)
        lista.see(indice)
        lbl_contador.configure(text=f"{indice + 1} / {len(estado['lista'])}  (pág. {oc['pagina'] + 1})")
        lbl_rodape.configure(text=f"Seção: {oc['secao'] or '-'}   │   Termo: {oc['termo']}   │   "
                                  f"Arquivo destacado: {caminho_pdf}")

    def navegar(passo):
        if estado["lista"]:
            mostrar((estado["atual"] + passo) % len(estado["lista"]))

    def alterar_zoom(delta):
        estado["zoom"] = max(0.75, min(3.0, estado["zoom"] + delta))
        mostrar(estado["atual"])

    def ao_selecionar(_evento=None):
        selecao = lista.curselection()
        if selecao and selecao[0] != estado["atual"]:
            mostrar(selecao[0])

    def rolar(evento):
        canvas.yview_scroll(-1 if (evento.delta > 0 or evento.num == 4) else 1, "units")

    def fechar():
        try:
            doc.close()
        finally:
            janela.destroy()

    lista.bind("<<ListboxSelect>>", ao_selecionar)
    canvas.bind("<MouseWheel>", rolar)
    canvas.bind("<Button-4>", rolar)
    canvas.bind("<Button-5>", rolar)
    janela.bind("<F3>", lambda e: navegar(1))
    janela.bind("<Shift-F3>", lambda e: navegar(-1))
    janela.bind("<Next>", lambda e: navegar(1))
    janela.bind("<Prior>", lambda e: navegar(-1))
    janela.protocol("WM_DELETE_WINDOW", fechar)

    janela.after(100, preencher_lista)


def cmd_click22():
    """Função para acesso rápido a procedimentos ONS - URLs específicas por instalação"""

    global root

    procedimentos = {

        # ===== UHE MÜLLER DE GODOY PEREIRA =====
        "UHE Müller de Godoy Pereira": {
            "CADASTRO": {
                "DADOS EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.1.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Dados%20de%20Equipamentos%2F2.1.6.%20Regi%C3%A3o%20Centro-Oeste%2FCD-CT.CO.5GB.01_Rev.{rev}.pdf",
                "LIMITES EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Limites%20de%20Equipamentos%2F2.2.6.%20Regi%C3%A3o%20Centro-Oeste%2FCD-CT.CO.5GB.02_Rev.{rev}.pdf",
                "HIDRÁULICO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.3.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20Hidr%C3%A1ulicas%2FCD-OR.PR.PAR_Rev.{rev}.pdf",
                "FAIXA DE CONTROLE DE TENSÃO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.6.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Faixas%20para%20Controle%20de%20Tens%C3%A3o%2F2.6.6.%20Regi%C3%A3o%20Centro-Oeste%2FCD-CT.CO.5GB.03_Rev.{rev}.pdf"
            },
            "INSTRUÇÕES": {
                # "AJUSTAMENTO OPERATIVO": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - MGP ⚠️",
                "OPERAÇÃO NORMAL": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.1.%20Opera%C3%A7%C3%A3o%20Normal%2F3.1.1.6.%20Centro-Oeste%2FIO-ON.CO.5GB_Rev.{rev}.pdf",
                # "ESQUEMAS ESPECIAIS": "⚠️ INSERIR URL para ESQUEMAS ESPECIAIS - MGP ⚠️",
                "PREPARAÇÃO DE MANOBRAS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.3.%20Prepara%C3%A7%C3%A3o%20para%20Manobras%2F3.1.3.6.%20Centro-Oeste%2FIO-PM.CO.5GB_Rev.{rev}.pdf",
                "OPERAÇÃO EM CONTINGÊNCIA": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.3.%20Opera%C3%A7%C3%A3o%20em%20Conting%C3%AAncia%2F3.3.6.%20Centro-Oeste%2FIO-OC.CO.5GB_Rev.{rev}.pdf",
                # "RECOMPOSIÇÃO DA REDE": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - MGP ⚠️",
                "OPERAÇÃO DE RESERVATÓRIOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.6.%20Opera%C3%A7%C3%A3o%20de%20Reservat%C3%B3rios%2FIO-OR.PR.PAR_Rev.{rev}.pdf",
                "OPERAÇÃO DE INSTALAÇÕES": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.7.%20Opera%C3%A7%C3%A3o%20de%20Instala%C3%A7%C3%B5es%2F3.7.6.%20Centro-Oeste%2F3.7.6.1.%20%C3%81rea%20500345%20kV%20de%20Goi%C3%A1sBras%C3%ADlia%2FIO-OI.CO.UFRC_Rev.{rev}.pdf"
            }
        },

        # ===== UHE SÃO JOSÉ =====
        "UHE São José": {
            "CADASTRO": {
                "DADOS EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.1.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Dados%20de%20Equipamentos%2F2.1.5.%20Regi%C3%A3o%20Sul%2FCD-CT.S.2RS.01_Rev.{rev}.pdf",
                # "LIMITES EQUIPAMENTOS": "⚠️ INSERIR URL para LIMITES EQUIPAMENTOS - SJO ⚠️",
                "HIDRÁULICO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.3.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20Hidr%C3%A1ulicas%2FCD-OR.UR.URU_Rev.{rev}.pdf",
                "FAIXA DE CONTROLE DE TENSÃO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.6.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Faixas%20para%20Controle%20de%20Tens%C3%A3o%2F2.6.5.%20Regi%C3%A3o%20Sul%2FCD-CT.S.2RS.03_Rev.{rev}.pdf"
            },
            "INSTRUÇÕES": {
                # "AJUSTAMENTO OPERATIVO": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - SJO ⚠️",
                "OPERAÇÃO NORMAL": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.1.%20Opera%C3%A7%C3%A3o%20Normal%2F3.1.1.5.%20Sul%2FIO-ON.S.2RS_Rev.{rev}.pdf",
                # "ESQUEMAS ESPECIAIS": "⚠️ INSERIR URL para ESQUEMAS ESPECIAIS - SJO ⚠️",
                "PREPARAÇÃO DE MANOBRAS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.3.%20Prepara%C3%A7%C3%A3o%20para%20Manobras%2F3.1.3.5.%20Sul%2FIO-PM.S.2RS_Rev.{rev}.pdf",
                "OPERAÇÃO EM CONTINGÊNCIA": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.3.%20Opera%C3%A7%C3%A3o%20em%20Conting%C3%AAncia%2F3.3.5.%20Sul%2FIO-OC.S.2RS_Rev.{rev}.pdf",
                # "RECOMPOSIÇÃO DA REDE": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - SJO ⚠️",
                "OPERAÇÃO DE RESERVATÓRIOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.6.%20Opera%C3%A7%C3%A3o%20de%20Reservat%C3%B3rios%2FIO-OR.UR.URU_Rev.{rev}.pdf",
                "OPERAÇÃO DE INSTALAÇÕES": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.7.%20Opera%C3%A7%C3%A3o%20de%20Instala%C3%A7%C3%B5es%2F3.7.5.%20Sul%2F3.7.5.2.%20%C3%81rea%20230%20kV%20do%20Rio%20Grande%20do%20Sul%2FIO-OI.S.USJO_Rev.{rev}.pdf"
            }
        },

        # ===== UHE FERREIRA GOMES =====
        "UHE Ferreira Gomes": {
            "CADASTRO": {
                "DADOS EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.1.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Dados%20de%20Equipamentos%2F2.1.4.%20Regi%C3%A3o%20Norte%2FCD-CT.N.5MM.01_Rev.{rev}.pdf",
                "LIMITES EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Limites%20de%20Equipamentos%2F2.2.4.%20Regi%C3%A3o%20Norte%2FCD-CT.N.5MM.02_Rev.{rev}.pdf",
                "HIDRÁULICO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.3.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20Hidr%C3%A1ulicas%2FCD-OR.AM.ARA_Rev.{rev}.pdf",
                "FAIXA DE CONTROLE DE TENSÃO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.6.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Faixas%20para%20Controle%20de%20Tens%C3%A3o%2F2.6.4.%20Regi%C3%A3o%20Norte%2FCD-CT.N.5MM.03_Rev.{rev}.pdf"
            },
            "INSTRUÇÕES": {
                # "AJUSTAMENTO OPERATIVO": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - FGO ⚠️",
                "OPERAÇÃO NORMAL": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.1.%20Opera%C3%A7%C3%A3o%20Normal%2F3.1.1.4.%20Norte%2FIO-ON.N.5MM_Rev.{rev}.pdf",
                "ESQUEMAS ESPECIAIS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.2.%20Esquemas%20Especiais%2F3.1.2.4.%20Norte%2FIO-EE.N.5MM_Rev.{rev}.pdf",
                "PREPARAÇÃO DE MANOBRAS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.3.%20Prepara%C3%A7%C3%A3o%20para%20Manobras%2F3.1.3.4.%20Norte%2FIO-PM.N.5MM_Rev.{rev}.pdf",
                "OPERAÇÃO EM CONTINGÊNCIA": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.3.%20Opera%C3%A7%C3%A3o%20em%20Conting%C3%AAncia%2F3.3.4.%20Norte%2FIO-OC.N.5MM_Rev.{rev}.pdf",
                # "RECOMPOSIÇÃO DA REDE": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - FGO ⚠️",
                "OPERAÇÃO DE RESERVATÓRIOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.6.%20Opera%C3%A7%C3%A3o%20de%20Reservat%C3%B3rios%2FIO-OR.AM.ARA_Rev.{rev}.pdf",
                "OPERAÇÃO DE INSTALAÇÕES": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.7.%20Opera%C3%A7%C3%A3o%20de%20Instala%C3%A7%C3%B5es%2F3.7.4.%20Norte%2F3.7.4.5.%20%C3%81rea%20500230%20kV%20Manaus%20-%20Macap%C3%A1%2FIO-OI.N.FGO_Rev.{rev}.pdf"
            }
        },

        # ===== SE MACAPÁ =====
        "SE Macapá": {
            "CADASTRO": {
                "DADOS EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.1.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Dados%20de%20Equipamentos%2F2.1.4.%20Regi%C3%A3o%20Norte%2FCD-CT.N.5MM.01_Rev.{rev}.pdf",
                "LIMITES EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Limites%20de%20Equipamentos%2F2.2.4.%20Regi%C3%A3o%20Norte%2FCD-CT.N.5MM.02_Rev.{rev}.pdf",
                # "HIDRÁULICO": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - FGO ⚠️",
                "FAIXA DE CONTROLE DE TENSÃO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.6.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Faixas%20para%20Controle%20de%20Tens%C3%A3o%2F2.6.4.%20Regi%C3%A3o%20Norte%2FCD-CT.N.5MM.03_Rev.{rev}.pdf"
            },
            "INSTRUÇÕES": {
                # "AJUSTAMENTO OPERATIVO": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - FGO ⚠️",
                "OPERAÇÃO NORMAL": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.1.%20Opera%C3%A7%C3%A3o%20Normal%2F3.1.1.4.%20Norte%2FIO-ON.N.5MM_Rev.{rev}.pdf",
                "ESQUEMAS ESPECIAIS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.2.%20Esquemas%20Especiais%2F3.1.2.4.%20Norte%2FIO-EE.N.5MM_Rev.{rev}.pdf",
                "PREPARAÇÃO DE MANOBRAS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.3.%20Prepara%C3%A7%C3%A3o%20para%20Manobras%2F3.1.3.4.%20Norte%2FIO-PM.N.5MM_Rev.{rev}.pdf",
                "OPERAÇÃO EM CONTINGÊNCIA": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.3.%20Opera%C3%A7%C3%A3o%20em%20Conting%C3%AAncia%2F3.3.4.%20Norte%2FIO-OC.N.5MM_Rev.{rev}.pdf",
                # "RECOMPOSIÇÃO DA REDE": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - FGO ⚠️",
                # "OPERAÇÃO DE RESERVATÓRIOS": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - FGO ⚠️",
                "OPERAÇÃO DE INSTALAÇÕES": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.7.%20Opera%C3%A7%C3%A3o%20de%20Instala%C3%A7%C3%B5es%2F3.7.4.%20Norte%2F3.7.4.5.%20%C3%81rea%20500230%20kV%20Manaus%20-%20Macap%C3%A1%2FIO-OI.N.MCP_Rev.{rev}.pdf"
            }
        },

        # ===== SE ITAGUAÇU =====
        "SE Itaguaçu": {
            "CADASTRO": {
                "DADOS EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.1.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Dados%20de%20Equipamentos%2F2.1.6.%20Regi%C3%A3o%20Centro-Oeste%2FCD-CT.CO.5GB.01_Rev.{rev}.pdf",
                "LIMITES EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Limites%20de%20Equipamentos%2F2.2.6.%20Regi%C3%A3o%20Centro-Oeste%2FCD-CT.CO.5GB.02_Rev.{rev}.pdf",
                # "HIDRÁULICO": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - FGO ⚠️",
                "FAIXA DE CONTROLE DE TENSÃO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.6.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Faixas%20para%20Controle%20de%20Tens%C3%A3o%2F2.6.6.%20Regi%C3%A3o%20Centro-Oeste%2FCD-CT.CO.5GB.03_Rev.{rev}.pdf"
            },
            "INSTRUÇÕES": {
                # "AJUSTAMENTO OPERATIVO": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - MGP ⚠️",
                "OPERAÇÃO NORMAL": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.1.%20Opera%C3%A7%C3%A3o%20Normal%2F3.1.1.6.%20Centro-Oeste%2FIO-ON.CO.5GB_Rev.{rev}.pdf",
                # "ESQUEMAS ESPECIAIS": "⚠️ INSERIR URL para ESQUEMAS ESPECIAIS - MGP ⚠️",
                "PREPARAÇÃO DE MANOBRAS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.3.%20Prepara%C3%A7%C3%A3o%20para%20Manobras%2F3.1.3.6.%20Centro-Oeste%2FIO-PM.CO.5GB_Rev.{rev}.pdf",
                "OPERAÇÃO EM CONTINGÊNCIA": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.3.%20Opera%C3%A7%C3%A3o%20em%20Conting%C3%AAncia%2F3.3.6.%20Centro-Oeste%2FIO-OC.CO.5GB_Rev.{rev}.pdf",
                # "RECOMPOSIÇÃO DA REDE": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - MGP ⚠️",
                # "OPERAÇÃO DE RESERVATÓRIOS": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - MGP ⚠️",
                "OPERAÇÃO DE INSTALAÇÕES": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.7.%20Opera%C3%A7%C3%A3o%20de%20Instala%C3%A7%C3%B5es%2F3.7.6.%20Centro-Oeste%2F3.7.6.1.%20%C3%81rea%20500345%20kV%20de%20Goi%C3%A1sBras%C3%ADlia%2FIO-OI.CO.IGU_Rev.{rev}.pdf"
            }
        },

        # ===== SE RUSSAS-II =====
        "SE Russas-II": {
            "CADASTRO": {
                "DADOS EQUIPAMENTOS": "⚠️ INSERIR URL para DADOS EQUIPAMENTOS - PTIM ⚠️",
                "LIMITES EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Limites%20de%20Equipamentos%2F2.2.3.%20Regi%C3%A3o%20Nordeste%2FCD-CT.NE.2NO.02_Rev.{rev}.pdf",
                # "HIDRÁULICO": "⚠️ INSERIR URL para HIDRÁULICO - PTIM ⚠️",
                "FAIXA DE CONTROLE DE TENSÃO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.6.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Faixas%20para%20Controle%20de%20Tens%C3%A3o%2F2.6.3.%20Regi%C3%A3o%20Nordeste%2FCD-CT.NE.2NO.03_Rev.{rev}.pdf"
            },
            "INSTRUÇÕES": {
                # "AJUSTAMENTO OPERATIVO": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - PTIM ⚠️",
                "OPERAÇÃO NORMAL": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.1.%20Opera%C3%A7%C3%A3o%20Normal%2F3.1.1.3.%20Nordeste%2FIO-ON.NE.2NO_Rev.{rev}.pdf",
                "ESQUEMAS ESPECIAIS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.2.%20Esquemas%20Especiais%2F3.1.2.3.%20Nordeste%2FIO-EE.NE.2NO_Rev.{rev}.pdf",
                "PREPARAÇÃO DE MANOBRAS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.3.%20Prepara%C3%A7%C3%A3o%20para%20Manobras%2F3.1.3.3.%20Nordeste%2FIO-PM.NE.2NO_Rev.{rev}.pdf",
                "OPERAÇÃO EM CONTINGÊNCIA": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.3.%20Opera%C3%A7%C3%A3o%20em%20Conting%C3%AAncia%2F3.3.3.%20Nordeste%2FIO-OC.NE.2NO_Rev.{rev}.pdf",
                # "RECOMPOSIÇÃO DA REDE": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - PTIM ⚠️",
                # "OPERAÇÃO DE RESERVATÓRIOS": "⚠️ INSERIR URL para OPERAÇÃO DE RESERVATÓRIOS - PTIM ⚠️",
                "OPERAÇÃO DE INSTALAÇÕES": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.7.%20Opera%C3%A7%C3%A3o%20de%20Instala%C3%A7%C3%B5es%2F3.7.3.%20Nordeste%2F3.7.3.4.%20%C3%81rea%20230%20kV%20Norte%2FIO-OI.NE.RSD_Rev.{rev}.pdf"
            }
        },

        # ===== CGE PITOMBEIRA =====
        "CGE Pitombeira": {
            "CADASTRO": {
                # "DADOS EQUIPAMENTOS": "⚠️ INSERIR URL para DADOS EQUIPAMENTOS - PTIM ⚠️",
                "LIMITES EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Limites%20de%20Equipamentos%2F2.2.3.%20Regi%C3%A3o%20Nordeste%2FCD-CT.NE.2NO.02_Rev.{rev}.pdf",
                # "HIDRÁULICO": "⚠️ INSERIR URL para HIDRÁULICO - PTIM ⚠️",
                "FAIXA DE CONTROLE DE TENSÃO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.6.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Faixas%20para%20Controle%20de%20Tens%C3%A3o%2F2.6.3.%20Regi%C3%A3o%20Nordeste%2FCD-CT.NE.2NO.03_Rev.{rev}.pdf"
            },
            "INSTRUÇÕES": {
                "AJUSTAMENTO OPERATIVO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F5.%20Ajustamentos%20Operativos%20-%20SM%205.14%2F5.2.%20Regi%C3%A3o%20Nordeste%2F5.2.4.%20%C3%81rea%20230%20kV%20Norte%2FAO-CE.NE.2NO_Rev.{rev}.pdf",
                "OPERAÇÃO NORMAL": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.1.%20Opera%C3%A7%C3%A3o%20Normal%2F3.1.1.3.%20Nordeste%2FIO-ON.NE.2NO_Rev.{rev}.pdf",
                "ESQUEMAS ESPECIAIS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.2.%20Esquemas%20Especiais%2F3.1.2.3.%20Nordeste%2FIO-EE.NE.2NO_Rev.{rev}.pdf",
                "PREPARAÇÃO DE MANOBRAS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.3.%20Prepara%C3%A7%C3%A3o%20para%20Manobras%2F3.1.3.3.%20Nordeste%2FIO-PM.NE.2NO_Rev.{rev}.pdf",
                "OPERAÇÃO EM CONTINGÊNCIA": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.3.%20Opera%C3%A7%C3%A3o%20em%20Conting%C3%AAncia%2F3.3.3.%20Nordeste%2FIO-OC.NE.2NO_Rev.{rev}.pdf",
                # "RECOMPOSIÇÃO DA REDE": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - PTIM ⚠️",
                # "OPERAÇÃO DE RESERVATÓRIOS": "⚠️ INSERIR URL para OPERAÇÃO DE RESERVATÓRIOS - PTIM ⚠️",
                "OPERAÇÃO DE INSTALAÇÕES": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.7.%20Opera%C3%A7%C3%A3o%20de%20Instala%C3%A7%C3%B5es%2F3.7.3.%20Nordeste%2F3.7.3.4.%20%C3%81rea%20230%20kV%20Norte%2FIO-OI.NE.PTM_Rev.{rev}.pdf"
            }
        },

        # ===== CGE JANDAÍRA-III =====
        "CGE Jandaíra-III": {
            "CADASTRO": {
                # "DADOS EQUIPAMENTOS": "⚠️ INSERIR URL para DADOS EQUIPAMENTOS - JDT ⚠️",
                # "LIMITES EQUIPAMENTOS": "⚠️ INSERIR URL para LIMITES EQUIPAMENTOS - JDT ⚠️",
                # "HIDRÁULICO": "⚠️ INSERIR URL para HIDRÁULICO - JDT ⚠️",
                "FAIXA DE CONTROLE DE TENSÃO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.6.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Faixas%20para%20Controle%20de%20Tens%C3%A3o%2F2.6.3.%20Regi%C3%A3o%20Nordeste%2FCD-CT.NE.5NE.03_Rev.{rev}.pdf"
            },
            "INSTRUÇÕES": {
                # "AJUSTAMENTO OPERATIVO": "⚠️ INSERIR URL para AJUSTAMENTO OPERATIVO - JDT ⚠️",
                "OPERAÇÃO NORMAL": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.1.%20Opera%C3%A7%C3%A3o%20Normal%2F3.1.1.3.%20Nordeste%2FIO-ON.NE.2NO_Rev.{rev}.pdf",
                "ESQUEMAS ESPECIAIS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.2.%20Esquemas%20Especiais%2F3.1.2.3.%20Nordeste%2FIO-EE.NE.5NE_Rev.{rev}.pdf",
                "PREPARAÇÃO DE MANOBRAS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.3.%20Prepara%C3%A7%C3%A3o%20para%20Manobras%2F3.1.3.3.%20Nordeste%2FIO-PM.NE.5NE_Rev.{rev}.pdf",
                "OPERAÇÃO EM CONTINGÊNCIA": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.3.%20Opera%C3%A7%C3%A3o%20em%20Conting%C3%AAncia%2F3.3.3.%20Nordeste%2FIO-OC.NE.5NE_Rev.{rev}.pdf",
                # "RECOMPOSIÇÃO DA REDE": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - JDT ⚠️",
                # "OPERAÇÃO DE RESERVATÓRIOS": "⚠️ INSERIR URL para OPERAÇÃO DE RESERVATÓRIOS - JDT ⚠️",
                "OPERAÇÃO DE INSTALAÇÕES": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.7.%20Opera%C3%A7%C3%A3o%20de%20Instala%C3%A7%C3%B5es%2F3.7.3.%20Nordeste%2F3.7.3.8.%20%C3%81rea%20500%20kV%20da%20Regi%C3%A3o%20Nordeste%2FIO-OI.NE.JDD_Rev.{rev}.pdf"
            }
        },

        # ===== UFV PITOMBEIRA =====
        "UFV Pitombeira": {
            "CADASTRO": {
                # "DADOS EQUIPAMENTOS": "⚠️ INSERIR URL para DADOS EQUIPAMENTOS - PTIM ⚠️",
                "LIMITES EQUIPAMENTOS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Limites%20de%20Equipamentos%2F2.2.3.%20Regi%C3%A3o%20Nordeste%2FCD-CT.NE.2NO.02_Rev.{rev}.pdf",
                # "HIDRÁULICO": "⚠️ INSERIR URL para HIDRÁULICO - PTIM ⚠️",
                "FAIXA DE CONTROLE DE TENSÃO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F2.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20-%20SM%205.11%2F2.6.%20Cadastros%20de%20Informa%C3%A7%C3%B5es%20Operacionais%20de%20Faixas%20para%20Controle%20de%20Tens%C3%A3o%2F2.6.3.%20Regi%C3%A3o%20Nordeste%2FCD-CT.NE.2NO.03_Rev.{rev}.pdf"
            },
            "INSTRUÇÕES": {
                "AJUSTAMENTO OPERATIVO": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F5.%20Ajustamentos%20Operativos%20-%20SM%205.14%2F5.2.%20Regi%C3%A3o%20Nordeste%2F5.2.4.%20%C3%81rea%20230%20kV%20Norte%2FAO-AJ.NE.UPTM_Rev.{rev}.pdf",
                "OPERAÇÃO NORMAL": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.1.%20Opera%C3%A7%C3%A3o%20Normal%2F3.1.1.3.%20Nordeste%2FIO-ON.NE.2NO_Rev.{rev}.pdf",
                "ESQUEMAS ESPECIAIS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.2.%20Esquemas%20Especiais%2F3.1.2.3.%20Nordeste%2FIO-EE.NE.2NO_Rev.{rev}.pdf",
                "PREPARAÇÃO DE MANOBRAS": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.1.%20Controle%20da%20Transmiss%C3%A3o%2F3.1.3.%20Prepara%C3%A7%C3%A3o%20para%20Manobras%2F3.1.3.3.%20Nordeste%2FIO-PM.NE.2NO_Rev.{rev}.pdf",
                "OPERAÇÃO EM CONTINGÊNCIA": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.3.%20Opera%C3%A7%C3%A3o%20em%20Conting%C3%AAncia%2F3.3.3.%20Nordeste%2FIO-OC.NE.2NO_Rev.{rev}.pdf",
                # "RECOMPOSIÇÃO DA REDE": "⚠️ INSERIR URL para RECOMPOSIÇÃO DA REDE - PTIM ⚠️",
                # "OPERAÇÃO DE RESERVATÓRIOS": "⚠️ INSERIR URL para OPERAÇÃO DE RESERVATÓRIOS - PTIM ⚠️",
                "OPERAÇÃO DE INSTALAÇÕES": "https://www.ons.org.br/%2FMPO%2FDocumento%20Normativo%2F3.%20Instru%C3%A7%C3%B5es%20de%20Opera%C3%A7%C3%A3o%20-%20SM%205.12%2F3.7.%20Opera%C3%A7%C3%A3o%20de%20Instala%C3%A7%C3%B5es%2F3.7.3.%20Nordeste%2F3.7.3.4.%20%C3%81rea%20230%20kV%20Norte%2FIO-OI.NE.PTM_Rev.{rev}.pdf"
            }
        },
    }
    # ===== CONFIGURAÇÕES GLOBAIS PARA BUSCA =====
    MAX_REVISAO = 500
    TIMEOUT_REQUISICAO = 2
    MAX_THREADS = 20  # quantidade de buscas simultâneas

    def testar_revisao(session, url_base, revisao):
        """Testa uma única revisão."""
        url_teste = url_base.replace("{rev}", str(revisao).zfill(2))

        try:
            resposta = session.head(
                url_teste,
                timeout=TIMEOUT_REQUISICAO,
                allow_redirects=True
            )

            if resposta.status_code == 200:
                return revisao, url_teste

        except requests.RequestException:
            pass

        return revisao, None

    def encontrar_ultima_revisao(url_base, callback_progresso=None):

        if "INSERIR URL" in url_base:
            return None

        with requests.Session() as session:

            # 1) Atalho: última revisão já encontrada deste documento e as logo acima dela
            #    (normalmente basta uma rodada curta de consultas, em vez de varrer até MAX_REVISAO)
            conhecida = obter_revisao_conhecida(url_base)
            if conhecida is not None:
                proximas = range(min(conhecida + JANELA_REVISAO_NOVA, MAX_REVISAO), conhecida - 1, -1)
                with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                    achadas = [(rev, url) for rev, url in
                               executor.map(lambda rev: testar_revisao(session, url_base, rev), proximas) if url]
                if achadas:
                    revisao, url_encontrada = max(achadas)  # a mais alta encontrada
                    registrar_revisao_conhecida(url_base, revisao)
                    if callback_progresso:
                        callback_progresso(100, revisao)
                    return url_encontrada

            # 2) Varredura completa (primeira busca do documento ou revisão fora da janela do atalho)
            # Começa da maior revisão para a menor
            revisoes = range(MAX_REVISAO, -1, -1)

            total = MAX_REVISAO + 1
            concluidas = 0

            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:

                futures = {
                    executor.submit(
                        testar_revisao,
                        session,
                        url_base,
                        revisao
                    ): revisao
                    for revisao in revisoes
                }

                for future in as_completed(futures):

                    concluidas += 1

                    if callback_progresso:
                        progresso = int((concluidas / total) * 100)
                        callback_progresso(progresso, futures[future])

                    revisao, resultado = future.result()

                    # Encontrou → encerra imediatamente
                    if resultado:
                        executor.shutdown(wait=False, cancel_futures=True)
                        registrar_revisao_conhecida(url_base, revisao)

                        if callback_progresso:
                            callback_progresso(100, revisao)

                        return resultado

        return None


    # ===== FUNÇÃO QUE EXECUTA A BUSCA EM THREAD =====
    def executar_busca_em_thread(localidade, categoria, subtipo, url_base,
                                 janela_progresso, progress_bar, lbl_status, lbl_revisao,
                                 opcoes_destaque=None, busca_cancelada=None, somente_resumo=False):

        if "INSERIR URL" in url_base:
            janela_progresso.after(0, janela_progresso.destroy)
            janela_progresso.after(0, lambda: messagebox.showerror("Erro",
                                                                   f"❌ URL não configurada!\n\n"
                                                                   f"Localidade: {localidade}\n"
                                                                   f"Categoria: {categoria}\n"
                                                                   f"Documento: {subtipo}\n\n"
                                                                   f"Por favor, configure a URL no código."))
            return

        def callback_progresso(progresso, revisao_atual):
            janela_progresso.after(0, lambda: progress_bar.configure(value=progresso))
            janela_progresso.after(0, lambda: lbl_revisao.configure(text=f"Testando revisão: {revisao_atual}"))

            if progresso < 30:
                msg = f"Buscando revisões... testando {revisao_atual} (0 → {MAX_REVISAO})"
            elif progresso < 100:
                msg = f"Continuando busca... testando revisão {revisao_atual}"
            elif somente_resumo:
                msg = "✅ Revisão encontrada! Lendo o objetivo do procedimento..."
            else:
                msg = "✅ Busca concluída! Abrindo navegador..."

            janela_progresso.after(0, lambda: lbl_status.configure(text=msg))

        url_final = encontrar_ultima_revisao(url_base, callback_progresso)

        if url_final and somente_resumo:
            if busca_cancelada is not None and busca_cancelada.is_set():
                return
            try:
                resumo = obter_resumo_objetivo(url_final)
            except Exception as erro:
                if busca_cancelada is not None and busca_cancelada.is_set():
                    return
                mensagem = (f"❌ Não foi possível obter o resumo!\n\n"
                            f"Localidade: {localidade}\n"
                            f"Documento: {subtipo}\n\n"
                            f"{erro}")
                janela_progresso.after(0, janela_progresso.destroy)
                janela_progresso.after(0, lambda: messagebox.showerror("Resumo indisponível", mensagem))
                return
            if busca_cancelada is not None and busca_cancelada.is_set():
                return
            _CACHE_RESUMO_ONS[url_base] = (datetime.now(), resumo)
            janela_progresso.after(0, janela_progresso.destroy)
            root.after(0, lambda: abrir_janela_resumo(localidade, categoria, subtipo, resumo))
            return

        aviso_destaque = ""
        if url_final and opcoes_destaque and PYMUPDF_DISPONIVEL:
            if busca_cancelada is not None and busca_cancelada.is_set():
                return
            try:
                janela_progresso.after(0, lambda: lbl_status.configure(
                    text="📥 Baixando o PDF atualizado e destacando a instalação..."))
                doc, ocorrencias, caminho = gerar_pdf_destacado(url_final, opcoes_destaque["termos"], localidade)
                if busca_cancelada is not None and busca_cancelada.is_set():
                    doc.close()
                    return
                janela_progresso.after(0, janela_progresso.destroy)
                root.after(0, lambda: abrir_visualizador_destaque(doc, ocorrencias, localidade, subtipo,
                                                                  caminho, url_final))
                return
            except ValueError as erro:
                aviso_destaque = f"\n\n🖍 Destaque não aplicado: {erro}"
            except Exception as erro:
                aviso_destaque = f"\n\n🖍 Destaque não aplicado (falha ao processar o PDF): {erro}"

        if url_final:
            janela_progresso.after(1000, janela_progresso.destroy)
            webbrowser.open(url_final)
            janela_progresso.after(0, lambda: messagebox.showinfo("Sucesso",
                                                                  f"✅ Procedimento aberto com sucesso!\n\n"
                                                                  f"Localidade: {localidade}\n"
                                                                  f"Documento: {subtipo}\n\n"
                                                                  f"O arquivo foi aberto no seu navegador."
                                                                  f"{aviso_destaque}"))
        else:
            janela_progresso.after(0, janela_progresso.destroy)
            janela_progresso.after(0, lambda: messagebox.showerror("Erro",
                                                                   f"❌ Não foi possível encontrar o procedimento!\n\n"
                                                                   f"Localidade: {localidade}\n"
                                                                   f"Documento: {subtipo}\n\n"
                                                                   f"Verifique se a URL está correta ou se o\n"
                                                                   f"documento está disponível no site."))

    # ===== FUNÇÃO PARA ABRIR PROCEDIMENTO =====
    def abrir_procedimento(localidade, categoria, subtipo, url_base, opcoes_destaque=None, somente_resumo=False):

        janela_progresso = Toplevel()
        janela_progresso.title("Buscando resumo..." if somente_resumo else "Buscando procedimento...")
        janela_progresso.geometry("500x410")
        janela_progresso.resizable(False, False)
        janela_progresso['bg'] = "#a4bad2"
        janela_progresso.transient()
        janela_progresso.grab_set()

        lbl_titulo = Label(janela_progresso,
                           text="📝 BUSCANDO RESUMO" if somente_resumo else "🔍 BUSCANDO PROCEDIMENTO",
                           font=('Arial', '14', 'bold'),
                           bg="#024593", fg="white", height=2)
        lbl_titulo.pack(fill='x')

        lbl_info = Label(janela_progresso, text=f"{localidade}\n{categoria} - {subtipo}",
                         bg="#a4bad2", font=("Arial", 11, "bold"), fg="#024593")
        lbl_info.pack(pady=15)

        lbl_status = Label(janela_progresso, text="Iniciando busca pela última revisão...",
                           bg="#a4bad2", font=("Arial", 10))
        lbl_status.pack(pady=5)

        lbl_revisao = Label(janela_progresso, text="Revisão atual: --",
                            bg="#a4bad2", font=("Arial", 9), fg="#666")
        lbl_revisao.pack(pady=5)

        progress_bar = ttk.Progressbar(janela_progresso, length=400, mode='determinate', maximum=100)
        progress_bar.pack(pady=20)

        lbl_instrucao = Label(janela_progresso,
                              text=f"⏳ Buscando revisões de 00 até {MAX_REVISAO}...\nIsso pode levar alguns segundos.",
                              bg="#a4bad2", font=("Arial", 8), fg="#555")
        lbl_instrucao.pack(pady=10)

        busca_cancelada = threading.Event()

        def cancelar_busca():
            busca_cancelada.set()
            janela_progresso.destroy()
            messagebox.showinfo("Busca cancelada", "A busca foi cancelada pelo usuário.")

        btn_cancelar = Button(janela_progresso, text="Cancelar", command=cancelar_busca,
                              bg="#FF8C00", fg="white", font=("Arial", 9))
        btn_cancelar.pack(pady=5)

        thread_busca = threading.Thread(
            target=executar_busca_em_thread,
            args=(localidade, categoria, subtipo, url_base,
                  janela_progresso, progress_bar, lbl_status, lbl_revisao,
                  opcoes_destaque, busca_cancelada, somente_resumo),
            daemon=True
        )
        thread_busca.start()

    # ===== RESUMO DO PROCEDIMENTO (OBJETIVO LIDO NO SITE DO ONS) =====
    def abrir_resumo(localidade, categoria, subtipo, url_base):
        """Botão 'Resumo': mostra o objetivo do procedimento. Reaproveita o resumo já lido
        (por algumas horas) para não buscar a revisão e baixar o PDF a cada clique."""
        em_cache = _CACHE_RESUMO_ONS.get(url_base)
        if em_cache and datetime.now() - em_cache[0] < VALIDADE_CACHE_RESUMO:
            abrir_janela_resumo(localidade, categoria, subtipo, em_cache[1])
            return
        abrir_procedimento(localidade, categoria, subtipo, url_base, somente_resumo=True)

    def abrir_janela_resumo(localidade, categoria, subtipo, resumo):
        janela = Toplevel(root)
        janela.title(f"Resumo - {subtipo} - {localidade}")
        janela.geometry("760x520")
        janela.minsize(560, 380)
        janela['bg'] = "#a4bad2"

        Label(janela, text=f"📝 RESUMO - {subtipo}\n{localidade} ({categoria})",
              font=('Arial', '14', 'bold'), bg="#024593", fg="white", height=2).pack(fill='x')

        identificacao = " │ ".join(parte for parte in (
            f"Código: {resumo['codigo']}" if resumo["codigo"] else "",
            f"Revisão: {resumo['revisao']}" if resumo["revisao"] else "",
            f"Vigência: {resumo['vigencia']}" if resumo["vigencia"] else "",
            f"Objetivo na pág. {resumo['pagina']} do PDF") if parte)
        if resumo["titulo"]:
            Label(janela, text=resumo["titulo"], bg="#a4bad2", fg="#024593", font=("Arial", 10, "bold"),
                  wraplength=700, justify="left", anchor="w").pack(fill='x', padx=20, pady=(12, 0))
        Label(janela, text=identificacao, bg="#a4bad2", font=("Arial", 9), fg="#555",
              anchor="w").pack(fill='x', padx=20, pady=(2, 8))

        # Botões primeiro (lado inferior) para nunca serem cortados quando a janela for reduzida
        barra = Frame(janela, bg="#a4bad2")
        barra.pack(side="bottom", fill='x', padx=20, pady=12)

        quadro = LabelFrame(janela, text="🎯 Objetivo do procedimento", bg="#a4bad2",
                            font=("Arial", 10, "bold"), fg="#024593")
        quadro.pack(side="top", fill=BOTH, expand=True, padx=20, pady=(0, 0))
        rolagem = Scrollbar(quadro, orient=VERTICAL)
        texto = Text(quadro, wrap="word", font=("Arial", 11), bg="white", yscrollcommand=rolagem.set,
                     spacing2=3, spacing3=8)
        rolagem.configure(command=texto.yview)
        rolagem.pack(side=RIGHT, fill=Y, padx=(0, 4), pady=4)
        texto.pack(side=LEFT, fill=BOTH, expand=True, padx=(4, 0), pady=4)
        texto.insert("1.0", resumo["objetivo"])
        texto.configure(state="disabled")

        def copiar():
            janela.clipboard_clear()
            janela.clipboard_append(resumo["objetivo"])
            messagebox.showinfo("Resumo", "Objetivo copiado para a área de transferência.", parent=janela)

        Button(barra, text="Fechar", command=janela.destroy, bg="#FF0000", fg="white",
               font=("Arial", 10, "bold"), width=12).pack(side=RIGHT, padx=3)
        Button(barra, text="📋 Copiar", command=copiar, bg="#2ECC71", fg="white",
               font=("Arial", 9, "bold")).pack(side=RIGHT, padx=3)

        janela.bind("<Escape>", lambda e: janela.destroy())
        janela.lift()
        janela.focus_force()

    # ===== JANELA DE SUBTIPOS =====
    def abrir_subtipos(localidade, categoria):
        """Abre a janela com os subtipos (4 para CADASTRO, 8 para INSTRUÇÕES)"""

        dados = procedimentos[localidade][categoria]
        subtipos = list(dados.keys())

        cores = ["#3498DB", "#2ECC71", "#E74C3C", "#F39C12", "#9B59B6", "#1ABC9C", "#E67E22", "#34495E"]

        colunas = 2
        # Altura acompanha a quantidade de documentos (cada linha tem botão + "Resumo")
        linhas_botoes = (len(subtipos) + colunas - 1) // colunas

        janela_subtipos = Toplevel(frame_principal)
        janela_subtipos.title(f"{categoria} - {localidade}")
        janela_subtipos.geometry(f"620x{min(330 + linhas_botoes * 118, janela_subtipos.winfo_screenheight() - 80)}")
        janela_subtipos.resizable(False, False)
        janela_subtipos['bg'] = "#a4bad2"

        titulo = Label(janela_subtipos, text=f"{localidade}\n{categoria}",
                       font=('Arial', '14', 'bold'),
                       bg="#024593", fg="white", height=2)
        titulo.pack(fill='x')

        subtitulo = Label(janela_subtipos, text=f"Selecione o documento desejado:",
                          bg="#a4bad2", font=("Arial", 11))
        subtitulo.pack(pady=15)

        # ----- Destaque da instalação no PDF (opcional) -----
        frame_destaque = LabelFrame(janela_subtipos, text="🖍 Destaque da instalação no PDF",
                                    bg="#a4bad2", font=("Arial", 10, "bold"), fg="#024593")
        frame_destaque.pack(fill='x', padx=30, pady=(0, 5))

        var_destacar = BooleanVar(value=PYMUPDF_DISPONIVEL)
        Checkbutton(frame_destaque,
                    text=f"Destacar as ocorrências de {localidade} e navegar entre elas",
                    variable=var_destacar, bg="#a4bad2", font=("Arial", 9),
                    state="normal" if PYMUPDF_DISPONIVEL else "disabled").pack(anchor="w", padx=5)

        frame_termos = Frame(frame_destaque, bg="#a4bad2")
        frame_termos.pack(fill='x', padx=5, pady=(0, 5))
        Label(frame_termos, text="Termos (separe por ;):", bg="#a4bad2", font=("Arial", 9)).pack(side=LEFT)
        entry_termos = Entry(frame_termos, font=("Arial", 9))
        entry_termos.insert(0, "; ".join(termos_busca_padrao(localidade)))
        entry_termos.pack(side=LEFT, fill='x', expand=True, padx=5)

        if not PYMUPDF_DISPONIVEL:
            entry_termos.configure(state="disabled")
            Label(frame_destaque, text="Recurso indisponível: instale o PyMuPDF (pip install pymupdf)",
                  bg="#a4bad2", font=("Arial", 8), fg="#B00000").pack(anchor="w", padx=5, pady=(0, 3))

        def obter_opcoes_destaque():
            termos = [t.strip() for t in entry_termos.get().split(";") if t.strip()]
            if not (PYMUPDF_DISPONIVEL and var_destacar.get() and termos):
                return None
            return {"termos": termos}

        frame_botoes = Frame(janela_subtipos, bg="#a4bad2")
        frame_botoes.pack(fill='both', expand=True, padx=30, pady=10)

        for idx, subtipo in enumerate(subtipos):
            linha = idx // colunas
            coluna = idx % colunas
            cor = cores[idx % len(cores)]

            url_base = dados[subtipo]

            btn_frame = Frame(frame_botoes, bg="#a4bad2")
            btn_frame.grid(row=linha, column=coluna, padx=10, pady=6, sticky="nsew")

            if "INSERIR URL" in url_base:
                # Documento ainda sem URL: botão desabilitado, sem "Resumo"
                Button(btn_frame, text=f"⚠️ {subtipo}\n(URL não configurada)", bg=cor, fg="white",
                       font=("Arial", 10, "bold"), height=3, wraplength=236,
                       state="disabled").pack(fill='x')
                Label(btn_frame, text="⚠️ Configurar URL", bg="#a4bad2", font=("Arial", 8),
                      fg="#555").pack(pady=(5, 0))
                continue

            # "Clique para abrir" fica DENTRO do botão (com a cor de fundo da janela), para ninguém
            # clicar no texto achando que é o botão
            BotaoComRotulo(btn_frame, texto=subtipo, rotulo="Clique para abrir",
                           comando=lambda s=subtipo, u=url_base: abrir_procedimento(localidade, categoria, s, u,
                                                                                    obter_opcoes_destaque()),
                           bg=cor, fg_rotulo=janela_subtipos.cget("bg"), largura=260, altura=72).pack()

            # "Resumo" com a mesma cor do botão do procedimento ao qual está associado
            Button(btn_frame, text="📝 Resumo",
                   command=lambda s=subtipo, u=url_base: abrir_resumo(localidade, categoria, s, u),
                   bg=cor, fg="white", font=("Arial", 9, "bold"),
                   state="normal" if PYMUPDF_DISPONIVEL else "disabled").pack(fill='x', pady=(4, 0))

        for i in range(colunas):
            frame_botoes.grid_columnconfigure(i, weight=1)

        Button(janela_subtipos, text="Fechar", command=janela_subtipos.destroy,
               bg="#FF0000", fg="white", font=("Arial", 10, "bold"), width=15).pack(pady=15)

    # ===== JANELA DE OPÇÕES (CADASTRO ou INSTRUÇÕES) =====
    def abrir_opcoes_localidade(localidade):

        janela_opcoes = Toplevel(frame_principal)
        janela_opcoes.title(f"Opções - {localidade}")
        janela_opcoes.geometry("500x510")
        janela_opcoes.resizable(False, False)
        janela_opcoes['bg'] = "#a4bad2"

        titulo = Label(janela_opcoes, text=localidade, font=('Arial', '16', 'bold'),
                       bg="#024593", fg="white", height=2)
        titulo.pack(fill='x')

        subtitulo = Label(janela_opcoes, text="Selecione o tipo de documento:",
                          bg="#a4bad2", font=("Arial", 12))
        subtitulo.pack(pady=20)

        btn_cadastro = Button(janela_opcoes, text="📋 CADASTRO",
                              command=lambda: abrir_subtipos(localidade, "CADASTRO"),
                              bg="#3498DB", fg="white",
                              font=("Arial", 12, "bold"), height=2)
        btn_cadastro.pack(fill='x', padx=50, pady=10)

        Label(janela_opcoes, text="Documentos cadastrais da instalação",
              bg="#a4bad2", font=("Arial", 9), fg="#555").pack(pady=(0, 20))

        btn_instrucoes = Button(janela_opcoes, text="📖 INSTRUÇÕES",
                                command=lambda: abrir_subtipos(localidade, "INSTRUÇÕES"),
                                bg="#2ECC71", fg="white",
                                font=("Arial", 12, "bold"), height=2)
        btn_instrucoes.pack(fill='x', padx=50, pady=10)

        Label(janela_opcoes, text="Instruções operacionais da instalação",
              bg="#a4bad2", font=("Arial", 9), fg="#555").pack(pady=(0, 20))

        Button(janela_opcoes, text="Fechar", command=janela_opcoes.destroy,
               bg="#FF0000", fg="white", font=("Arial", 10, "bold"), width=15).pack(pady=10)

    # ===== CRIAÇÃO DA JANELA PRINCIPAL =====
    frame_principal = Toplevel(root)
    frame_principal.title('Acesso a Procedimentos ONS - Localidades')
    frame_principal.geometry('960x600')
    frame_principal.resizable(True, True)
    frame_principal['bg'] = "#a4bad2"

    titulo = Label(frame_principal, text='ACESSO A PROCEDIMENTOS ONS',
                   font=('Arial', '18', 'bold'),
                   bg="#024593", fg="white", height=2)
    titulo.pack(fill='x')

    subtitulo = Label(frame_principal,
                      text='Selecione uma localidade para acessar os procedimentos',
                      bg="#a4bad2", font=("Arial", 11))
    subtitulo.pack(pady=10)

    frame_dica = Frame(frame_principal, bg="#a4bad2")
    frame_dica.pack(fill='x', padx=20, pady=5)

    Label(frame_dica, text="💡 Clique na localidade → Escolha CADASTRO ou INSTRUÇÕES → Selecione o documento",
          bg="#a4bad2", font=("Arial", 9), fg="#024593").pack()
    """
    frame_aviso = Frame(frame_principal, bg="#FFF3CD", highlightbackground="#FFEAA7", highlightthickness=1)
    frame_aviso.pack(fill='x', padx=20, pady=5)

    Label(frame_aviso, text="⚠️ ATENÇÃO: Configure as URLs no código fonte antes de usar!",
          bg="#FFF3CD", font=("Arial", 9, "bold"), fg="#856404").pack(pady=5)
    """
    frame_botoes_localidades = Frame(frame_principal, bg="#a4bad2")
    frame_botoes_localidades.pack(fill='both', expand=True, padx=20, pady=20)

    localidades = list(procedimentos.keys())
    colunas = 3

    for indice, localidade in enumerate(localidades):
        linha = indice // colunas
        coluna = indice % colunas

        btn_frame = Frame(frame_botoes_localidades, bg="#a4bad2")
        btn_frame.grid(row=linha, column=coluna, padx=15, pady=15, sticky="nsew")

        # "Clique para acessar" fica DENTRO do botão (com a cor de fundo da janela), para ninguém
        # clicar no texto achando que é o botão
        BotaoComRotulo(btn_frame, texto=localidade, rotulo="Clique para acessar",
                       comando=lambda l=localidade: abrir_opcoes_localidade(l),
                       bg="#024593", fg_rotulo=frame_principal.cget("bg"),
                       largura=270, altura=80).pack()

    for i in range(colunas):
        frame_botoes_localidades.grid_columnconfigure(i, weight=1)

    Button(frame_principal, text="Fechar", command=frame_principal.destroy,
           bg="#FF0000", fg="white", font=("Arial", 11, "bold"), width=15).pack(pady=10)

#inicio do click-23

# ==========cascate PRIMEIRA PARTE inicia aqui ===================================
    # ---------------------------------------------------
    # QUESTIONÁRIO CLICK_23 - QUIZ COM BANCO DE QUESTÕES EM CSV
    # ---------------------------------------------------

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
QUESTOES_CSV = os.path.join(PASTA_BASE, "banco_questoes_click23.csv")
RESULTADOS_CSV = os.path.join(PASTA_BASE, "resultados_click23.csv")

SEPARADOR_CSV_QUESTOES = ";"

COLUNAS_QUESTOES = ["assunto", "localidade", "pergunta", "opcao_a", "opcao_b", "opcao_c", "opcao_d",
                     "resposta_correta"]
COLUNAS_RESULTADOS = ["nome", "data_hora_inicio", "data_hora_fim", "tempo_execucao",
                       "assunto_selecionado", "acertos", "total", "percentual"]

# Quantidades de questões que o treinando pode escolher para responder
OPCOES_QUANTIDADE_QUESTOES = [10, 20, 30, 40]

# Localidades aceitas na coluna "localidade" do banco de questões e no filtro da tela.
# Uma questão marcada como "TODAS" é considerada válida para qualquer localidade selecionada.
OPCOES_LOCALIDADE = ["TODAS", "MGP", "SJO", "QUE", "LAV", "FGO", "VIE", "PTM", "JDT"]

# Usuários autorizados a ver o botão "Relatório dos treinandos"
USUARIOS_RELATORIO = ["nmaganha", "jbarros"]


def obter_nome_usuario_logado():
    """Extrai o nome puro do usuário a partir do current_user da sessão de login
    (formato 'usuario em dd/mm/aaaa - HH:Mmh'), para identificar o treinando
    sem precisar de seleção manual."""
    if not current_user:
        return None
    return current_user.split(" em ")[0].strip()


def garantir_banco_questoes():
    """Verifica se o arquivo CSV do banco de questões existe.

    As questões não ficam no código: elas vêm de um arquivo CSV externo
    (banco_questoes_click23.csv, separado por ';'), que pode ser mantido com
    centenas de linhas (ex.: 400 questões) sem qualquer alteração neste programa.
    """
    if not os.path.exists(QUESTOES_CSV):
        raise FileNotFoundError(
            f"Banco de questões não encontrado: {QUESTOES_CSV}\n"
            f"Crie o arquivo CSV (separado por ';') com as colunas: {', '.join(COLUNAS_QUESTOES)}"
        )


def carregar_questoes():
    """Lê o banco de questões do CSV (separado por ';') e retorna uma lista de dicionários."""
    df = pd.read_csv(QUESTOES_CSV, sep=SEPARADOR_CSV_QUESTOES, encoding="utf-8-sig")
    return df.to_dict(orient="records")


def opcao_preenchida(valor):
    """Indica se uma célula de alternativa (opcao_a..d) tem conteúdo real.

    Permite questões de Verdadeiro/Falso (só A e B) ou de 3 alternativas (A, B e C),
    deixando opcao_c e/ou opcao_d em branco (ou só com espaço) no CSV."""
    if valor is None:
        return False
    texto = str(valor).strip()
    return texto != "" and texto.lower() != "nan"


def filtrar_questoes(banco, localidade_selecionada, assunto_selecionado):
    """Filtra as questões pela localidade e pelo assunto escolhidos.

    'TODAS' em qualquer um dos filtros significa ausência de filtro naquele campo.
    Uma questão cadastrada como localidade 'TODAS' atende a qualquer localidade
    específica selecionada (funciona como curinga)."""
    resultado = []
    for questao in banco:
        localidade_questao = str(questao.get("localidade", "")).strip().upper()
        assunto_questao = str(questao.get("assunto", "")).strip()

        loc_ok = (localidade_selecionada == "TODAS" or localidade_questao == localidade_selecionada
                  or localidade_questao == "TODAS")
        assunto_ok = (assunto_selecionado == "TODAS" or assunto_questao == assunto_selecionado)

        if loc_ok and assunto_ok:
            resultado.append(questao)
    return resultado


def migrar_resultados_se_necessario():
    """Se o arquivo de resultados existir com um esquema de colunas antigo (de uma versão
    anterior do Click_23), faz backup dele e inicia um novo arquivo com o esquema atual,
    evitando misturar linhas com layouts diferentes."""
    if not os.path.exists(RESULTADOS_CSV):
        return
    try:
        colunas_atuais = pd.read_csv(RESULTADOS_CSV, encoding="utf-8-sig", nrows=0).columns.tolist()
    except Exception:
        colunas_atuais = []

    if colunas_atuais != COLUNAS_RESULTADOS:
        selo = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = os.path.join(PASTA_BASE, f"resultados_click23_backup_{selo}.csv")
        os.replace(RESULTADOS_CSV, backup)


def salvar_resultado(nome, data_hora_inicio, data_hora_fim, tempo_execucao, assunto_selecionado,
                      acertos, total, percentual):
    """Grava o resultado do treinando no histórico em CSV."""
    novo = pd.DataFrame([{
        "nome": nome,
        "data_hora_inicio": data_hora_inicio,
        "data_hora_fim": data_hora_fim,
        "tempo_execucao": tempo_execucao,
        "assunto_selecionado": assunto_selecionado,
        "acertos": acertos,
        "total": total,
        "percentual": round(percentual, 1)
    }], columns=COLUNAS_RESULTADOS)

    if os.path.exists(RESULTADOS_CSV):
        novo.to_csv(RESULTADOS_CSV, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        novo.to_csv(RESULTADOS_CSV, index=False, encoding="utf-8-sig")


def calcular_media_geral():
    """Calcula a média (%) de todos os resultados já registrados no histórico."""
    df = pd.read_csv(RESULTADOS_CSV, encoding="utf-8-sig")
    return df["percentual"].mean()


# ---------------------------------------------------
# IDENTIDADE VISUAL DA AUTO-AVALIAÇÃO (cores, fonte e componentes)
# ---------------------------------------------------
AV_FONTE = "Segoe UI"
AV_AZUL = "#024593"
AV_FUNDO = "#EEF2F7"
AV_CARD = "#FFFFFF"
AV_BORDA = "#D5DDE8"
AV_TEXTO = "#1F2937"
AV_TEXTO_SUAVE = "#6B7280"
AV_VERDE = "#0A7A2E"
AV_VERMELHO = "#B00000"
AV_AMBAR = "#CC8400"

# (fundo, fundo ao passar o mouse, cor do texto)
AV_ESTILOS_BOTAO = {
    "primario": ("#024593", "#013573", "white"),
    "sucesso": ("#079541", "#057A34", "white"),
    "aviso": ("#CC8400", "#A86D00", "white"),
    "neutro": ("#E3E8EF", "#D0D7E2", AV_TEXTO),
}


def criar_botao_av(parent, texto, comando, estilo="primario", fonte=None, **opcoes):
    """Botão plano com efeito ao passar o mouse (substitui o botão 3D padrão do Tk)."""
    fundo, fundo_hover, cor_texto = AV_ESTILOS_BOTAO[estilo]
    botao = Button(parent, text=texto, command=comando, bg=fundo, fg=cor_texto,
                   activebackground=fundo_hover, activeforeground=cor_texto,
                   font=fonte or (AV_FONTE, 10, "bold"), relief="flat", bd=0,
                   cursor="hand2", **opcoes)
    botao.bind("<Enter>", lambda e: botao.config(bg=fundo_hover))
    botao.bind("<Leave>", lambda e: botao.config(bg=fundo))
    return botao


def criar_cabecalho_av(janela, texto, altura=56):
    """Faixa azul do topo da janela, com o título alinhado à esquerda."""
    cabecalho = Frame(janela, bg=AV_AZUL)
    cabecalho.place(x=0, y=0, relwidth=1.0, height=altura)
    Label(cabecalho, text=texto, bg=AV_AZUL, fg="white",
          font=(AV_FONTE, 15, "bold")).place(x=24, rely=0.5, anchor="w")
    return cabecalho


# Áreas com rolagem da Auto-avaliação que respondem à roda do mouse
_AREAS_ROLAVEIS_AV = []


def _rolar_area_av(evento):
    """Roda do mouse: rola a área rolável que estiver sob o ponteiro, mesmo quando o
    ponteiro está sobre uma alternativa ou texto que fica dentro dela."""
    try:
        widget = evento.widget.winfo_containing(evento.x_root, evento.y_root)
    except (TclError, KeyError):
        return
    while widget is not None:
        if widget in _AREAS_ROLAVEIS_AV:
            widget.yview_scroll(int(-1 * (evento.delta / 120)), "units")
            return
        widget = widget.master


def criar_area_rolavel_av(parent, bg=AV_CARD):
    """Área com rolagem vertical que preenche o 'parent'. A barra de rolagem só aparece
    quando o conteúdo não cabe (perguntas muito longas continuam totalmente acessíveis)."""
    canvas = Canvas(parent, bg=bg, highlightthickness=0)
    scrollbar = Scrollbar(parent, orient=VERTICAL, command=canvas.yview)
    inner_frame = Frame(canvas, bg=bg)
    largura_scroll = 18

    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    janela_interna = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(janela_interna, width=e.width))

    def atualizar_barra(primeiro, ultimo):
        scrollbar.set(primeiro, ultimo)
        if float(primeiro) <= 0.0 and float(ultimo) >= 1.0:
            scrollbar.place_forget()
        else:
            scrollbar.place(relx=1.0, x=0, y=0, anchor="ne", width=largura_scroll, relheight=1.0)

    canvas.configure(yscrollcommand=atualizar_barra)
    canvas.place(x=0, y=0, relwidth=1.0, width=-largura_scroll, relheight=1.0)

    _AREAS_ROLAVEIS_AV.append(canvas)
    canvas.bind("<Destroy>", lambda e: _AREAS_ROLAVEIS_AV.remove(canvas)
                if e.widget is canvas and canvas in _AREAS_ROLAVEIS_AV else None)
    janela_topo = parent.winfo_toplevel()
    if not getattr(janela_topo, "_roda_av_ligada", False):
        janela_topo._roda_av_ligada = True
        janela_topo.bind("<MouseWheel>", _rolar_area_av, add="+")

    return inner_frame


def criar_grafico_resultado(parent, percentual_usuario, percentual_media, meta=70):
    """Cria o gráfico comparativo (nota do treinando x média geral x meta) embutido no Tkinter."""
    usa_layout_automatico = True
    try:
        fig = Figure(figsize=(6.5, 3.3), dpi=100, facecolor="white", layout="constrained")
    except TypeError:  # versões antigas do matplotlib
        fig = Figure(figsize=(6.5, 3.3), dpi=100, facecolor="white")
        usa_layout_automatico = False
    ax = fig.add_subplot(111)
    ax.set_facecolor("white")

    categorias = ["Sua Nota", "Média Geral"]
    valores = [percentual_usuario, percentual_media]
    cores = [AV_AZUL, "#9DB4D3"]

    barras = ax.bar(categorias, valores, color=cores, width=0.5, zorder=3)
    ax.axhline(y=meta, color=AV_VERMELHO, linestyle="--", linewidth=1.5, zorder=4,
               label=f"Avaliação Meta ({meta:.0f}%)")

    for barra, valor in zip(barras, valores):
        ax.text(barra.get_x() + barra.get_width() / 2, valor + 2, f"{valor:.1f}%",
                ha="center", fontsize=11, fontweight="bold", color=AV_TEXTO)

    ax.set_ylim(0, 110)
    ax.set_ylabel("Percentual de Acerto (%)", color=AV_TEXTO_SUAVE, fontsize=9)
    ax.set_title("Comparativo de Desempenho", loc="left", fontsize=12, fontweight="bold", color=AV_TEXTO)
    ax.yaxis.grid(True, color="#E5EAF1", linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#C9D3E0")
    ax.tick_params(colors=AV_TEXTO_SUAVE, length=0)
    ax.tick_params(axis="x", labelsize=10, colors=AV_TEXTO)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), frameon=False, fontsize=9,
              labelcolor=AV_VERMELHO)
    if not usa_layout_automatico:
        fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().config(highlightthickness=0)
    canvas.draw()
    return canvas


# Dicionário global para eventual integração futura (mesmo padrão do click_18)
entries = {}


def cmd_click23():
    global entries, current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    nome_logado = obter_nome_usuario_logado()
    if not nome_logado:
        messagebox.showwarning("Atenção", "Não foi possível identificar o usuário logado.")
        return

    try:
        garantir_banco_questoes()
    except FileNotFoundError as erro:
        messagebox.showerror("Banco de questões ausente", str(erro))
        return

    migrar_resultados_se_necessario()

    pode_ver_relatorio = nome_logado.strip().lower() in [u.lower() for u in USUARIOS_RELATORIO]

    quiz_win = Toplevel(root)
    quiz_win.title('COG - AUTO-AVALIAÇÃO')
    quiz_win.geometry('900x600')
    quiz_win.minsize(900, 600)
    quiz_win.resizable(True, True)
    quiz_win['bg'] = AV_FUNDO

    criar_cabecalho_av(quiz_win, 'Auto-avaliação - Teste seus Conhecimentos')

    conteudo_frame = Frame(quiz_win, bg=AV_CARD, highlightthickness=1, highlightbackground=AV_BORDA,
                          highlightcolor=AV_BORDA)
    conteudo_frame.place(x=24, y=72, relwidth=1.0, width=-48, relheight=1.0, height=-132)

    rodape = Frame(quiz_win, bg=AV_CARD)
    rodape.place(x=0, rely=1.0, anchor="sw", relwidth=1.0, height=44)
    Frame(rodape, bg=AV_BORDA).place(x=0, y=0, relwidth=1.0, height=1)
    rodape_label = Label(rodape, text="", bg=AV_CARD, fg=AV_TEXTO_SUAVE, font=(AV_FONTE, 10))
    rodape_label.place(x=24, rely=0.5, anchor="w")

    estado = {
        "nome": nome_logado,
        "perguntas": [],
        "indice": 0,
        "acertos": 0,
        "total_perguntas": 10,
        "assunto_selecionado": "TODAS",
        "inicio": None,
        "resposta_var": None
    }

    def limpar_conteudo():
        conteudo_frame.unbind("<Configure>")
        for widget in conteudo_frame.winfo_children():
            widget.destroy()

    def gerar_relatorio_treinandos():
        if not os.path.exists(RESULTADOS_CSV):
            messagebox.showwarning("Aviso", "Ainda não há resultados registrados.", parent=quiz_win)
            return

        df = pd.read_csv(RESULTADOS_CSV, encoding="utf-8-sig")
        if df.empty:
            messagebox.showwarning("Aviso", "Ainda não há resultados registrados.", parent=quiz_win)
            return

        try:
            data_hora_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")

            colunas_header = ["Usuário", "Início", "Término", "Tempo", "Assunto", "Qtd.", "Acertos", "%"]
            larguras_header = [35, 32, 32, 24, 54, 15, 20, 18]

            class PDFTreinandos(FPDF):
                def header(self):
                    self.set_font("helvetica", 'B', 14)
                    self.cell(0, 10, "Relatório dos Treinandos - Auto-Avaliação (Click_23)", 0,
                              new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                    self.set_font("helvetica", 'I', 10)
                    self.cell(0, 6, f"Gerado em: {data_hora_atual}", 0,
                              new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                    self.ln(5)
                    self.set_font("helvetica", 'B', 9)
                    for col, larg in zip(colunas_header, larguras_header):
                        self.cell(larg, 8, col, border=1, align='C')
                    self.ln()

            pdf = PDFTreinandos(orientation='L', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            pdf.set_font("helvetica", size=8)
            for _, linha in df.iterrows():
                if pdf.get_y() > 180:
                    pdf.add_page()

                valores = [
                    str(linha.get("nome", "-")),
                    str(linha.get("data_hora_inicio", "-")),
                    str(linha.get("data_hora_fim", "-")),
                    str(linha.get("tempo_execucao", "-")),
                    str(linha.get("assunto_selecionado", "-")),
                    str(linha.get("total", "-")),
                    str(linha.get("acertos", "-")),
                    f"{float(linha.get('percentual', 0)):.1f}%"
                ]
                for valor, larg in zip(valores, larguras_header):
                    pdf.cell(larg, 7, valor, border=1, align='C')
                pdf.ln()

            nome_arquivo = os.path.join(PASTA_BASE, "relatorio_treinandos_click23.pdf")
            pdf.output(nome_arquivo)
            os.startfile(nome_arquivo)
            messagebox.showinfo("Sucesso", "Relatório dos treinandos gerado com sucesso!", parent=quiz_win)
        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao gerar o relatório: {erro}", parent=quiz_win)

    def tela_configuracao():
        limpar_conteudo()
        rodape_label.config(text=f"Treinando: {estado['nome']}")

        saudacao_label = Label(
            conteudo_frame, text=f"Olá, {estado['nome']}! Escolha o formato das questões que deseja responder:",
            bg=AV_CARD, fg=AV_TEXTO, font=(AV_FONTE, 14, "bold"), justify="left", anchor="w", wraplength=780)
        saudacao_label.place(x=28, y=28)
        conteudo_frame.bind("<Configure>", lambda e: saudacao_label.config(wraplength=max(300, e.width - 56)))

        banco_atual = carregar_questoes()
        opcoes_assunto = ["TODAS"] + sorted({str(q["assunto"]).strip() for q in banco_atual})

        quantidade_var = IntVar(value=OPCOES_QUANTIDADE_QUESTOES[0])
        localidade_var = StringVar(value="TODAS")
        assunto_var = StringVar(value="TODAS")

        form = Frame(conteudo_frame, bg=AV_CARD)
        form.place(x=28, y=100, relwidth=1.0, width=-56)
        for coluna in range(3):
            form.columnconfigure(coluna, weight=1, uniform="colunas")

        def campo(coluna, titulo, variavel, valores, padx):
            Label(form, text=titulo, bg=AV_CARD, fg=AV_TEXTO_SUAVE, font=(AV_FONTE, 9, "bold")
                  ).grid(row=0, column=coluna, sticky="w", padx=padx)
            ttk.Combobox(form, textvariable=variavel, values=valores, state="readonly",
                         justify='center', font=(AV_FONTE, 11)
                         ).grid(row=1, column=coluna, sticky="ew", padx=padx, pady=(6, 0), ipady=4)

        campo(0, "Número de questões", quantidade_var, OPCOES_QUANTIDADE_QUESTOES, (0, 12))
        campo(1, "Localidade", localidade_var, OPCOES_LOCALIDADE, (6, 6))
        campo(2, "Assunto", assunto_var, opcoes_assunto, (12, 0))

        disponiveis_label = Label(conteudo_frame, text="", bg=AV_CARD, fg=AV_TEXTO_SUAVE,
                                  font=(AV_FONTE, 10))
        disponiveis_label.place(x=28, y=190)

        def atualizar_disponiveis(*args):
            try:
                quantidade = int(quantidade_var.get())
            except (ValueError, TclError):
                return
            disponiveis = len(filtrar_questoes(banco_atual, localidade_var.get(), assunto_var.get()))
            suficiente = disponiveis >= quantidade
            texto = f"Questões disponíveis para esta combinação: {disponiveis}"
            if not suficiente:
                texto += "  (insuficiente para o número escolhido)"
            disponiveis_label.config(text=texto, fg=AV_TEXTO_SUAVE if suficiente else AV_VERMELHO)

        for variavel in (quantidade_var, localidade_var, assunto_var):
            variavel.trace_add("write", atualizar_disponiveis)
        atualizar_disponiveis()

        def iniciar():
            quantidade = int(quantidade_var.get())
            localidade_sel = localidade_var.get()
            assunto_sel = assunto_var.get()

            banco = carregar_questoes()
            disponiveis = filtrar_questoes(banco, localidade_sel, assunto_sel)

            if len(disponiveis) < quantidade:
                messagebox.showerror(
                    "Questões insuficientes",
                    f"Não existem questões suficientes para montar o questionário no formato selecionado:\n\n"
                    f"Questões: {quantidade}  |  Localidade: {localidade_sel}  |  Assunto: {assunto_sel}\n\n"
                    f"Há apenas {len(disponiveis)} questão(ões) disponível(is) para essa combinação.\n\n"
                    f"Tente reduzir o número de questões, alterar a localidade ou o assunto, "
                    f"ou selecionar TODAS em uma ou ambas as opções.",
                    parent=quiz_win)
                return

            estado["total_perguntas"] = quantidade
            estado["assunto_selecionado"] = assunto_sel
            estado["perguntas"] = random.sample(disponiveis, quantidade)
            estado["indice"] = 0
            estado["acertos"] = 0
            estado["inicio"] = datetime.now()
            mostrar_pergunta()

        if pode_ver_relatorio:
            criar_botao_av(conteudo_frame, "Iniciar Questionário", iniciar, "primario"
                           ).place(relx=0.5, x=-230, rely=1.0, y=-28, anchor="sw", width=220, height=42)
            criar_botao_av(conteudo_frame, "Relatório dos treinandos", gerar_relatorio_treinandos, "neutro"
                           ).place(relx=0.5, x=10, rely=1.0, y=-28, anchor="sw", width=220, height=42)
        else:
            criar_botao_av(conteudo_frame, "Iniciar Questionário", iniciar, "primario"
                           ).place(relx=0.5, x=-110, rely=1.0, y=-28, anchor="sw", width=220, height=42)

    def mostrar_pergunta():
        limpar_conteudo()
        idx = estado["indice"]
        pergunta = estado["perguntas"][idx]

        total = estado["total_perguntas"]
        rodape_label.config(
            text=f"Treinando: {estado['nome']}    |    Pergunta {idx + 1} de {total}    |    Assunto: {pergunta['assunto']}")

        # Botão de avançar fixo na base do quadro (reservado antes do resto do conteúdo)
        barra_botao = Frame(conteudo_frame, bg=AV_CARD)
        barra_botao.pack(side=BOTTOM, fill=X, padx=28, pady=(0, 20))

        # Barra de progresso
        progresso = Frame(conteudo_frame, bg=AV_CARD)
        progresso.pack(fill=X, padx=28, pady=(22, 0))
        Label(progresso, text=f"{idx + 1} / {total}", bg=AV_CARD, fg=AV_TEXTO_SUAVE,
              font=(AV_FONTE, 9, "bold")).pack(side=RIGHT, padx=(12, 0))
        trilho = Frame(progresso, bg="#E5EAF1", height=8)
        trilho.pack(side=LEFT, fill=X, expand=True)
        trilho.pack_propagate(False)
        Frame(trilho, bg=AV_AZUL).place(x=0, y=0, relheight=1.0, relwidth=(idx + 1) / total)

        # Pergunta e alternativas ficam numa área com rolagem (perguntas longas continuam acessíveis)
        area = Frame(conteudo_frame, bg=AV_CARD)
        area.pack(fill=BOTH, expand=True, padx=(28, 10), pady=(6, 8))
        corpo = criar_area_rolavel_av(area, bg=AV_CARD)

        pergunta_label = Label(corpo, text=f"Questão {idx + 1}: {pergunta['pergunta']}",
                               bg=AV_CARD, fg=AV_TEXTO, font=(AV_FONTE, 13, "bold"),
                               justify="left", anchor="w", wraplength=780)
        pergunta_label.pack(fill=X, pady=(14, 14))

        estado["resposta_var"] = StringVar(value="")
        opcoes = [("A", pergunta["opcao_a"]), ("B", pergunta["opcao_b"]),
                  ("C", pergunta["opcao_c"]), ("D", pergunta["opcao_d"])]
        opcoes_validas = [(letra, texto) for letra, texto in opcoes if opcao_preenchida(texto)]

        opcoes_frame = Frame(corpo, bg=AV_CARD)
        opcoes_frame.pack(fill=X)

        botoes_opcao = {}
        for letra, texto in opcoes_validas:
            botao_opcao = Radiobutton(
                opcoes_frame, text=f"{letra})   {texto}", variable=estado["resposta_var"], value=letra,
                indicatoron=0, relief="flat", offrelief="flat", overrelief="flat", bd=0,
                bg="#F6F8FB", activebackground="#E9F0FB", selectcolor="#CFE0F7",
                fg=AV_TEXTO, activeforeground=AV_TEXTO, font=(AV_FONTE, 11), anchor="w",
                justify="left", padx=16, pady=9, wraplength=740, cursor="hand2",
                highlightthickness=1, highlightbackground=AV_BORDA, highlightcolor=AV_AZUL)
            botao_opcao.pack(fill=X, pady=(0, 7))
            botoes_opcao[letra] = botao_opcao

        def marcar_selecao(*args):
            escolhida = estado["resposta_var"].get()
            for letra, botao_opcao in botoes_opcao.items():
                botao_opcao.config(highlightbackground=AV_AZUL if letra == escolhida else AV_BORDA)

        estado["resposta_var"].trace_add("write", marcar_selecao)

        def ajustar_quebra(evento):
            largura = max(300, evento.width - 76)
            pergunta_label.config(wraplength=largura)
            for botao_opcao in botoes_opcao.values():
                botao_opcao.config(wraplength=largura - 40)

        conteudo_frame.bind("<Configure>", ajustar_quebra)

        def confirmar():
            resposta = estado["resposta_var"].get()
            if not resposta:
                messagebox.showwarning("Atenção", "Selecione uma alternativa.", parent=quiz_win)
                return

            correta = str(pergunta["resposta_correta"]).strip().upper()
            texto_correta = pergunta[f"opcao_{correta.lower()}"]

            if resposta == correta:
                estado["acertos"] += 1
                messagebox.showinfo("Resposta", "Você acertou esta questão!", parent=quiz_win)
            else:
                messagebox.showwarning(
                    "Resposta",
                    f"Você errou esta questão.\nA resposta correta era: {correta}) {texto_correta}",
                    parent=quiz_win
                )

            if estado["indice"] + 1 < total:
                estado["indice"] += 1
                mostrar_pergunta()
            else:
                finalizar_questionario()

        texto_botao = "Próxima Pergunta" if idx + 1 < total else "Finalizar Questionário"
        criar_botao_av(barra_botao, texto_botao, confirmar, "primario"
                       ).pack(side=RIGHT, ipadx=14, ipady=10)

    def finalizar_questionario():
        acertos = estado["acertos"]
        total = estado["total_perguntas"]
        percentual = (acertos / total) * 100

        inicio = estado["inicio"]
        fim = datetime.now()
        duracao_seg = int((fim - inicio).total_seconds())
        horas, resto_seg = divmod(duracao_seg, 3600)
        minutos, segundos = divmod(resto_seg, 60)
        tempo_execucao = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

        salvar_resultado(
            estado["nome"],
            inicio.strftime("%d/%m/%Y %H:%M:%S"),
            fim.strftime("%d/%m/%Y %H:%M:%S"),
            tempo_execucao,
            estado["assunto_selecionado"],
            acertos, total, percentual
        )
        percentual_media = calcular_media_geral()

        limpar_conteudo()
        rodape_label.config(text="")

        if percentual >= 50:
            saudacao = f"Parabéns, {estado['nome']}!"
        else:
            saudacao = f"Olá, {estado['nome']}! Não desanime. Confiamos que você é capaz de superar isso."

        if percentual >= 70:
            cor_nota = AV_VERDE
        elif percentual >= 50:
            cor_nota = AV_AMBAR
        else:
            cor_nota = AV_VERMELHO

        # Painel da esquerda: mensagem e nota
        painel = Frame(conteudo_frame, bg=AV_CARD)
        painel.place(x=28, y=24, width=290, relheight=1.0, height=-100)

        Label(painel, text=saudacao, bg=AV_CARD, fg=AV_TEXTO, font=(AV_FONTE, 14, "bold"),
              justify="left", anchor="w", wraplength=280).pack(fill=X)
        Label(painel, text=f"{percentual:.1f}%", bg=AV_CARD, fg=cor_nota,
              font=(AV_FONTE, 40, "bold"), anchor="w").pack(fill=X, pady=(14, 0))
        Label(painel, text=f"Você acertou {acertos} de {total} perguntas ({percentual:.1f}%).",
              bg=AV_CARD, fg=AV_TEXTO_SUAVE, font=(AV_FONTE, 10), justify="left", anchor="w",
              wraplength=280).pack(fill=X, pady=(0, 12))
        Label(painel, text="Meta de 70% atingida" if percentual >= 70 else "Abaixo da meta de 70%",
              bg=cor_nota, fg="white", font=(AV_FONTE, 9, "bold"), padx=12, pady=4).pack(anchor="w")

        # Gráfico comparativo à direita
        grafico = criar_grafico_resultado(conteudo_frame, percentual, percentual_media)
        grafico.get_tk_widget().place(x=340, y=16, relwidth=1.0, width=-368, relheight=1.0, height=-94)

        criar_botao_av(conteudo_frame, "Responder Novamente", tela_configuracao, "primario"
                       ).place(relx=0.5, x=-165, rely=1.0, y=-24, anchor="sw", width=200, height=42)
        criar_botao_av(conteudo_frame, "Fechar", quiz_win.destroy, "neutro"
                       ).place(relx=0.5, x=45, rely=1.0, y=-24, anchor="sw", width=120, height=42)

    tela_configuracao()

# =======cascate PRIMEIRA PARTE termina aqui
#Click_24
# ==========cascate PRIMEIRA PARTE inicia aqui ===================================
    # ---------------------------------------------------
    # SGA - SISTEMA DE GESTÃO DE ATIVIDADES (CLICK_24)
    # ---------------------------------------------------

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
# Mesmo banco de dados já usado no restante do aplicativo (login, demais módulos).
BANCO_SGA = "dados_turno.db"
PASTA_ANEXOS_SGA = os.path.join(PASTA_BASE, "sga_anexos")

OPCOES_LOCALIDADE_SGA = ["UHE MGP", "UHE SJO", "PCH QUE", "PCH LAV", "UHE FGO", "CGE PTM", "UFV PTM", "CGE JDT", "COG"]

STATUS_ABERTO = "ABERTO"
STATUS_CANCELADO = "CANCELADO"
STATUS_REABERTO = "REABERTO"
STATUS_CONCLUIDO = "CONCLUÍDO"
# Processos cancelados ou concluídos não aceitam alterações até serem reabertos
STATUS_FINALIZADOS = (STATUS_CANCELADO, STATUS_CONCLUIDO)

STATUS_LANCAMENTO_ATIVO = "ATIVO"
STATUS_LANCAMENTO_CANCELADO = "CANCELADO"
# Texto que abre a descrição do lançamento automático gerado ao concluir um processo.
# Esse lançamento não pode ser cancelado nem excluído (não recebe os botões na tela).
PREFIXO_DESCRICAO_CONCLUSAO = "Processo concluído pelo usuário:"

LIMITE_PAGINAS_AVISO = 40
# Usuários autorizados a excluir definitivamente um lançamento já cancelado
USUARIOS_EXCLUSAO_LANCAMENTO = ["nmaganha", "fjunqueira"]

# Lembretes do botão "Agendar": exibidos no login dos usuários escolhidos, após a data/hora programada
STATUS_LEMBRETE_ATIVO = "ATIVO"
STATUS_LEMBRETE_CANCELADO = "CANCELADO"
QTDE_LINHAS_USUARIO_LEMBRETE = 10

# Identidade visual do SGA (cores e fonte usadas em todas as janelas do módulo)
SGA_FONTE = "Segoe UI"
SGA_AZUL = "#024593"
SGA_FUNDO = "#EEF2F7"
SGA_CARD = "#FFFFFF"
SGA_BORDA = "#D5DDE8"
SGA_TEXTO = "#1F2937"
SGA_TEXTO_SUAVE = "#6B7280"
SGA_VERDE = "#0A7A2E"
SGA_VERMELHO = "#B00000"

def obter_nome_usuario_logado():
    """Extrai o nome puro do usuário a partir do current_user da sessão de login
    (formato 'usuario em dd/mm/aaaa - HH:Mmh')."""
    if not current_user:
        return None
    return current_user.split(" em ")[0].strip()


def _adicionar_coluna_se_necessario(cursor, tabela, coluna, definicao):
    """Adiciona uma coluna a uma tabela já existente, caso ainda não exista
    (permite evoluir o esquema do SGA sem perder os dados já gravados)."""
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas_existentes = [linha[1] for linha in cursor.fetchall()]
    if coluna not in colunas_existentes:
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")


def garantir_banco_sga():
    """Cria as tabelas do SGA (se não existirem) no mesmo banco já usado pelo aplicativo,
    aplica migrações de colunas novas em bancos já existentes, e garante a pasta onde os
    documentos anexados ficam armazenados permanentemente."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS sga_processos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT UNIQUE NOT NULL,
                        localidade TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'ABERTO',
                        cancelado_por TEXT,
                        data_cancelamento TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS sga_lancamentos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        processo_id INTEGER NOT NULL,
                        data_hora TEXT NOT NULL,
                        usuario TEXT,
                        descricao TEXT,
                        FOREIGN KEY(processo_id) REFERENCES sga_processos(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS sga_documentos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        lancamento_id INTEGER NOT NULL,
                        nome_original TEXT NOT NULL,
                        caminho_armazenado TEXT NOT NULL,
                        FOREIGN KEY(lancamento_id) REFERENCES sga_lancamentos(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS sga_agendamentos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        processo_id INTEGER NOT NULL,
                        data_hora_exibicao TEXT NOT NULL,
                        mensagem TEXT,
                        criado_por TEXT,
                        data_criacao TEXT,
                        status TEXT NOT NULL DEFAULT 'ATIVO',
                        FOREIGN KEY(processo_id) REFERENCES sga_processos(id))''')

    # Um registro por usuário lembrado; data_ciencia preenchida quando ele clica em "Ciente"
    cursor.execute('''CREATE TABLE IF NOT EXISTS sga_agendamentos_usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        lembrete_id INTEGER NOT NULL,
                        usuario TEXT NOT NULL,
                        data_ciencia TEXT,
                        FOREIGN KEY(lembrete_id) REFERENCES sga_agendamentos(id))''')

    _adicionar_coluna_se_necessario(cursor, "sga_lancamentos", "status", "TEXT DEFAULT 'ATIVO'")
    _adicionar_coluna_se_necessario(cursor, "sga_lancamentos", "cancelado_por", "TEXT")
    _adicionar_coluna_se_necessario(cursor, "sga_lancamentos", "data_cancelamento", "TEXT")

    conexao.commit()
    conexao.close()
    os.makedirs(PASTA_ANEXOS_SGA, exist_ok=True)


def listar_processos():
    """Retorna todos os processos cadastrados, ordenados alfabeticamente pelo título."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, localidade, status, cancelado_por FROM sga_processos ORDER BY titulo ASC")
    linhas = cursor.fetchall()
    conexao.close()
    return linhas


def buscar_processo(processo_id):
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, localidade, status, cancelado_por FROM sga_processos WHERE id = ?",
                   (processo_id,))
    linha = cursor.fetchone()
    conexao.close()
    return linha


def titulo_ja_existe(titulo):
    """Retorna o id do processo se já existir um com esse título (comparação sem diferenciar maiúsculas), senão None."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("SELECT id FROM sga_processos WHERE UPPER(titulo) = ?", (titulo.strip().upper(),))
    linha = cursor.fetchone()
    conexao.close()
    return linha[0] if linha else None


def criar_processo(titulo, localidade):
    """Cria um novo processo (sempre com o título em maiúsculas) e retorna seu id."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO sga_processos (titulo, localidade, status) VALUES (?, ?, ?)",
                   (titulo.strip().upper(), localidade, STATUS_ABERTO))
    processo_id = cursor.lastrowid
    conexao.commit()
    conexao.close()
    return processo_id


def inserir_lancamento(processo_id, data_hora, usuario, descricao):
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO sga_lancamentos (processo_id, data_hora, usuario, descricao) VALUES (?, ?, ?, ?)",
                   (processo_id, data_hora, usuario, descricao))
    lancamento_id = cursor.lastrowid
    conexao.commit()
    conexao.close()
    return lancamento_id


def anexar_documento(processo_id, lancamento_id, caminho_original):
    """Copia o arquivo selecionado (qualquer extensão) para a pasta de anexos do SGA,
    mantendo-o vinculado permanentemente ao lançamento (independente do arquivo original
    ser movido/apagado depois)."""
    pasta_processo = os.path.join(PASTA_ANEXOS_SGA, str(processo_id))
    os.makedirs(pasta_processo, exist_ok=True)

    nome_original = os.path.basename(caminho_original)
    nome_armazenado = f"{lancamento_id}_{nome_original}"
    caminho_destino = os.path.join(pasta_processo, nome_armazenado)
    shutil.copyfile(caminho_original, caminho_destino)

    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO sga_documentos (lancamento_id, nome_original, caminho_armazenado) VALUES (?, ?, ?)",
                   (lancamento_id, nome_original, caminho_destino))
    conexao.commit()
    conexao.close()


def _parse_data_hora(texto):
    """Converte o texto de Data-Hora digitado/selecionado pelo usuário em um datetime,
    para permitir ordenação cronológica real (e não apenas pela ordem de lançamento).
    Se o formato não for reconhecido, retorna a menor data possível (vai para o início)."""
    texto = (texto or "").strip()
    formatos = ["%d/%m/%Y - %H:%Mh", "%d/%m/%Y - %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]
    for formato in formatos:
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    return datetime.min


def listar_lancamentos(processo_id):
    """Retorna todos os lançamentos do processo, em ordem CRONOLÓGICA (pela Data-Hora
    informada, não pela ordem em que foram digitados), cada um já com seu status de
    cancelamento e a lista de documentos anexados (lançamentos cancelados não têm mais
    documentos, pois eles são excluídos do banco ao cancelar o lançamento)."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, data_hora, usuario, descricao, status, cancelado_por, data_cancelamento "
        "FROM sga_lancamentos WHERE processo_id = ? ORDER BY id ASC",
        (processo_id,))
    lancamentos = cursor.fetchall()

    resultado = []
    for lanc_id, data_hora, usuario, descricao, status, cancelado_por, data_cancelamento in lancamentos:
        cursor.execute("SELECT nome_original, caminho_armazenado FROM sga_documentos WHERE lancamento_id = ?",
                       (lanc_id,))
        documentos = cursor.fetchall()
        resultado.append({
            "id": lanc_id, "data_hora": data_hora, "usuario": usuario,
            "descricao": descricao, "status": status or STATUS_LANCAMENTO_ATIVO,
            "cancelado_por": cancelado_por, "data_cancelamento": data_cancelamento,
            "documentos": documentos
        })
    conexao.close()

    resultado.sort(key=lambda lanc: _parse_data_hora(lanc["data_hora"]))
    return resultado


def cancelar_processo(processo_id, usuario):
    """Marca o processo como CANCELADO, preservando todo o histórico e documentos."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute("UPDATE sga_processos SET status = ?, cancelado_por = ?, data_cancelamento = ? WHERE id = ?",
                   (STATUS_CANCELADO, usuario, agora, processo_id))
    conexao.commit()
    conexao.close()


def reabrir_processo(processo_id):
    """Reabre um processo cancelado, retornando seu status para REABERTO."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("UPDATE sga_processos SET status = ? WHERE id = ?", (STATUS_REABERTO, processo_id))
    conexao.commit()
    conexao.close()


def concluir_processo(processo_id):
    """Marca o processo como CONCLUÍDO."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("UPDATE sga_processos SET status = ? WHERE id = ?", (STATUS_CONCLUIDO, processo_id))
    conexao.commit()
    conexao.close()


def cancelar_lancamento(lancamento_id, usuario):
    """Cancela um lançamento específico (permanece no histórico, tachado), apaga do disco
    os arquivos anexados a ele e remove as respectivas linhas do banco de dados, tornando-os
    definitivamente inacessíveis."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute(
        "UPDATE sga_lancamentos SET status = ?, cancelado_por = ?, data_cancelamento = ? WHERE id = ?",
        (STATUS_LANCAMENTO_CANCELADO, usuario, agora, lancamento_id))

    cursor.execute("SELECT caminho_armazenado FROM sga_documentos WHERE lancamento_id = ?", (lancamento_id,))
    caminhos = [linha[0] for linha in cursor.fetchall()]

    cursor.execute("DELETE FROM sga_documentos WHERE lancamento_id = ?", (lancamento_id,))
    conexao.commit()
    conexao.close()

    for caminho in caminhos:
        try:
            if os.path.exists(caminho):
                os.remove(caminho)
        except OSError:
            pass


def excluir_lancamento(lancamento_id):
    """Exclui definitivamente um lançamento que já esteja CANCELADO (linha do histórico,
    documentos remanescentes no banco e arquivos físicos). Retorna True se excluiu, ou
    False se o lançamento não existe ou não está cancelado (nesse caso nada é alterado)."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("SELECT status FROM sga_lancamentos WHERE id = ?", (lancamento_id,))
    linha = cursor.fetchone()
    if not linha or linha[0] != STATUS_LANCAMENTO_CANCELADO:
        conexao.close()
        return False

    cursor.execute("SELECT caminho_armazenado FROM sga_documentos WHERE lancamento_id = ?", (lancamento_id,))
    caminhos = [doc[0] for doc in cursor.fetchall()]

    cursor.execute("DELETE FROM sga_documentos WHERE lancamento_id = ?", (lancamento_id,))
    cursor.execute("DELETE FROM sga_lancamentos WHERE id = ?", (lancamento_id,))
    conexao.commit()
    conexao.close()

    for caminho in caminhos:
        try:
            if os.path.exists(caminho):
                os.remove(caminho)
        except OSError:
            pass
    return True


def gerar_pdf_processo(titulo, localidade, lancamentos, status, cancelado_por):
    """Gera o PDF completo do processo (título, localidade, todos os lançamentos com
    data/hora, descrição e relação de documentos anexados) e abre o arquivo gerado."""
    try:
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, f"Processo - {titulo}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        pdf.set_font("helvetica", '', 10)
        status_texto = f"Status: {status}"
        if status == STATUS_CANCELADO:
            status_texto += f"  (Cancelado por: {cancelado_por})"
        pdf.cell(0, 6, f"Localidade: {localidade}    |    {status_texto}", 0,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(6)

        for lanc in lancamentos:
            cancelado = lanc.get("status") == STATUS_LANCAMENTO_CANCELADO

            pdf.set_font("helvetica", 'B', 10)
            texto_cabecalho = f"{lanc['data_hora']}    -    {localidade}"
            if cancelado:
                texto_cabecalho += f"    [CANCELADO por: {lanc.get('cancelado_por')}]"
            pdf.cell(0, 6, texto_cabecalho, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_font("helvetica", '', 10)
            pdf.multi_cell(0, 6, lanc["descricao"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            if lanc["documentos"]:
                nomes = ", ".join(nome for nome, _ in lanc["documentos"])
                pdf.set_font("helvetica", 'I', 9)
                pdf.multi_cell(0, 5, f"Documento(s) anexado(s): {nomes}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            if lanc.get("usuario"):
                pdf.set_font("helvetica", 'I', 9)
                pdf.cell(0, 5, f"Lançado: {lanc['usuario']}", 0,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')

            pdf.ln(2)
            y = pdf.get_y()
            pdf.set_draw_color(2, 69, 147)
            pdf.line(10, y, 200, y)
            pdf.ln(4)

        nome_base = "".join(c if c.isalnum() else "_" for c in titulo)[:50]
        nome_arquivo = os.path.join(PASTA_BASE, f"processo_{nome_base}.pdf")
        pdf.output(nome_arquivo)

        total_paginas = pdf.page_no()
        os.startfile(nome_arquivo)
        messagebox.showinfo("Sucesso", "PDF do processo gerado com sucesso!")

        if total_paginas > LIMITE_PAGINAS_AVISO:
            messagebox.showinfo(
                "Aviso",
                f"Este processo já gerou um PDF com {total_paginas} páginas.\n\n"
                f"Considere abrir um novo processo com o título '{titulo} PARTE2' "
                f"para os próximos lançamentos."
            )
    except Exception as erro:
        messagebox.showerror("Erro", f"Falha ao gerar o PDF do processo: {erro}")


class ToolTipSGA:
    """Tooltip simples (texto flutuante) exibido ao passar o mouse sobre um widget."""

    def __init__(self, widget, texto):
        self.widget = widget
        self.texto = texto
        self.tipwindow = None
        widget.bind("<Enter>", self.mostrar)
        widget.bind("<Leave>", self.esconder)

    def mostrar(self, event=None):
        if self.tipwindow or not self.texto:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        Label(tw, text=self.texto, background=SGA_TEXTO, foreground="white",
              borderwidth=0, font=(SGA_FONTE, 9), padx=8, pady=3).pack()

    def esconder(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


# ---------------------------------------------------
# COMPONENTES VISUAIS REUTILIZÁVEIS DO SGA
# ---------------------------------------------------
# (fundo, fundo ao passar o mouse, cor do texto)
SGA_ESTILOS_BOTAO = {
    "primario": ("#024593", "#013573", "white"),
    "sucesso": ("#079541", "#057A34", "white"),
    "perigo": ("#C62828", "#A11F1F", "white"),
    "aviso": ("#CC8400", "#A86D00", "white"),
    "neutro": ("#E3E8EF", "#D0D7E2", SGA_TEXTO),
    "agendar": ("#5E35B1", "#4A2A8C", "white"),
}


def criar_botao_sga(parent, texto, comando, estilo="primario", fonte=None, **opcoes):
    """Botão plano com efeito ao passar o mouse (substitui o botão 3D padrão do Tk)."""
    fundo, fundo_hover, cor_texto = SGA_ESTILOS_BOTAO[estilo]
    botao = Button(parent, text=texto, command=comando, bg=fundo, fg=cor_texto,
                   activebackground=fundo_hover, activeforeground=cor_texto,
                   font=fonte or (SGA_FONTE, 10, "bold"), relief="flat", bd=0,
                   cursor="hand2", **opcoes)
    botao.bind("<Enter>", lambda e: botao.config(bg=fundo_hover))
    botao.bind("<Leave>", lambda e: botao.config(bg=fundo))
    return botao


def criar_entrada_sga(parent, **opcoes):
    """Campo de texto de uma linha, plano, com contorno que muda de cor ao receber o foco."""
    return Entry(parent, relief="flat", bd=5, font=(SGA_FONTE, 10), bg="white", fg=SGA_TEXTO,
                 disabledbackground="#EEF1F6", disabledforeground=SGA_TEXTO_SUAVE,
                 insertbackground=SGA_TEXTO, highlightthickness=1,
                 highlightbackground=SGA_BORDA, highlightcolor=SGA_AZUL, **opcoes)


def criar_area_texto_sga(parent, **opcoes):
    """Área de texto de várias linhas, plana, com margem interna e contorno com foco."""
    return Text(parent, relief="flat", bd=0, padx=10, pady=8, font=(SGA_FONTE, 10), bg="white",
                fg=SGA_TEXTO, insertbackground=SGA_TEXTO, highlightthickness=1,
                highlightbackground=SGA_BORDA, highlightcolor=SGA_AZUL, **opcoes)


def criar_cabecalho_sga(janela, texto, altura=56):
    """Faixa azul do topo da janela, com o título alinhado à esquerda."""
    cabecalho = Frame(janela, bg=SGA_AZUL)
    cabecalho.place(x=0, y=0, relwidth=1.0, height=altura)
    Label(cabecalho, text=texto, bg=SGA_AZUL, fg="white",
          font=(SGA_FONTE, 15, "bold")).place(x=24, rely=0.5, anchor="w")
    return cabecalho


def criar_rodape_sga(janela, altura=76):
    """Barra branca fixa na base da janela, onde ficam os botões principais."""
    rodape = Frame(janela, bg=SGA_CARD)
    rodape.place(x=0, rely=1.0, anchor="sw", relwidth=1.0, height=altura)
    Frame(rodape, bg=SGA_BORDA).place(x=0, y=0, relwidth=1.0, height=1)
    return rodape


def criar_selo_sga(parent, texto, fundo, cor_texto="white", fonte=None):
    """Etiqueta colorida (usada para status e localidade)."""
    return Label(parent, text=texto, bg=fundo, fg=cor_texto,
                 font=fonte or (SGA_FONTE, 9, "bold"), padx=10, pady=3)


def criar_icone_lupa(parent, bg="white", cor=SGA_TEXTO_SUAVE):
    """Ícone de lupa desenhado (não depende de fonte/emoji do Windows)."""
    icone = Canvas(parent, width=22, height=22, bg=bg, highlightthickness=0)
    icone.create_oval(4, 4, 15, 15, outline=cor, width=2)
    icone.create_line(13, 13, 19, 19, fill=cor, width=2)
    return icone


# Áreas com rolagem do SGA que respondem à roda do mouse
_AREAS_ROLAVEIS_SGA = []


def _rolar_area_sga(evento):
    """Roda do mouse: rola a área rolável que estiver sob o ponteiro, mesmo quando o
    ponteiro está sobre um botão, texto ou card que fica dentro dela."""
    try:
        widget = evento.widget.winfo_containing(evento.x_root, evento.y_root)
    except (TclError, KeyError):
        return
    while widget is not None:
        if widget in _AREAS_ROLAVEIS_SGA:
            widget.yview_scroll(int(-1 * (evento.delta / 120)), "units")
            return
        widget = widget.master


def criar_area_rolavel(parent, bg=SGA_FUNDO):
    """Cria uma área com barra de rolagem vertical (Canvas + Scrollbar + Frame interno),
    usada tanto no índice de processos quanto no histórico de cada processo.
    A área preenche todo o 'parent' e acompanha o redimensionamento da janela."""
    canvas = Canvas(parent, bg=bg, highlightthickness=0)
    scrollbar = Scrollbar(parent, orient=VERTICAL, command=canvas.yview)
    inner_frame = Frame(canvas, bg=bg)

    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    janela_interna = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(janela_interna, width=e.width))

    largura_scroll = 18
    canvas.place(x=0, y=0, relwidth=1.0, width=-largura_scroll, relheight=1.0)
    scrollbar.place(relx=1.0, x=0, y=0, anchor="ne", width=largura_scroll, relheight=1.0)

    # Roda do mouse: registra a área e liga o tratamento uma única vez na janela que a contém
    _AREAS_ROLAVEIS_SGA.append(canvas)
    canvas.bind("<Destroy>", lambda e: _AREAS_ROLAVEIS_SGA.remove(canvas)
                if e.widget is canvas and canvas in _AREAS_ROLAVEIS_SGA else None)
    janela_topo = parent.winfo_toplevel()
    if not getattr(janela_topo, "_roda_sga_ligada", False):
        janela_topo._roda_sga_ligada = True
        janela_topo.bind("<MouseWheel>", _rolar_area_sga, add="+")

    return inner_frame


def solicitar_justificativa(parent, titulo_processo, rotulo="Processo"):
    """Abre um quadro (janela modal) para o usuário digitar a justificativa do cancelamento
    do processo. Retorna o texto informado, ou None se o usuário voltar/fechar sem confirmar
    (nesse caso o cancelamento não deve ser efetivado)."""
    resultado = {"texto": None}

    janela = Toplevel(parent)
    janela.title("Justificativa do Cancelamento")
    janela.geometry('600x390')
    janela.resizable(False, False)
    janela['bg'] = SGA_FUNDO
    janela.transient(parent)

    criar_cabecalho_sga(janela, 'Justificativa do Cancelamento', altura=52)

    card = Frame(janela, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
    card.place(x=20, y=68, relwidth=1.0, width=-40, height=230)

    Label(card, text=f"{rotulo}: {titulo_processo}", bg=SGA_CARD, fg=SGA_TEXTO,
          font=(SGA_FONTE, 10, "bold"), wraplength=530, justify="left", anchor="w"
          ).place(x=16, y=12, relwidth=1.0, width=-32)

    Label(card, text="Informe o motivo do cancelamento:", bg=SGA_CARD, fg=SGA_TEXTO_SUAVE,
          font=(SGA_FONTE, 9, "bold")).place(x=16, y=46)

    frame_texto = Frame(card, bg=SGA_CARD)
    frame_texto.place(x=16, y=70, relwidth=1.0, width=-32, height=144)
    scroll = Scrollbar(frame_texto)
    scroll.pack(side=RIGHT, fill=Y)
    texto = criar_area_texto_sga(frame_texto, wrap=WORD, yscrollcommand=scroll.set)
    texto.pack(side=LEFT, fill=BOTH, expand=True)
    scroll.config(command=texto.yview)
    texto.focus_set()

    def confirmar():
        justificativa = texto.get("1.0", END).strip()
        if not justificativa:
            messagebox.showwarning("Atenção", "Informe a justificativa do cancelamento.", parent=janela)
            return
        resultado["texto"] = justificativa
        janela.destroy()

    criar_botao_sga(janela, "Confirmar", confirmar, "primario"
                    ).place(relx=0.5, x=-130, y=318, width=120, height=38)
    criar_botao_sga(janela, "Voltar", janela.destroy, "neutro"
                    ).place(relx=0.5, x=10, y=318, width=120, height=38)

    janela.grab_set()
    janela.wait_window()
    return resultado["texto"]


def tela_atualizar_novo_lancamento(parent, processo_id, callback_atualizar):
    """Janela 'Atualizar/Novo Lançamento'. Se processo_id for informado, é uma
    atualização de processo existente (título e localidade travados). Caso contrário,
    é a abertura de um novo processo."""
    processo_existente = buscar_processo(processo_id) if processo_id else None

    janela = Toplevel(parent)
    janela.title("Atualizar/Novo Lançamento")
    janela.geometry('1100x750')
    janela.minsize(1100, 750)
    janela.resizable(True, True)
    janela['bg'] = SGA_FUNDO

    criar_cabecalho_sga(janela, 'Atualizar/Novo Lançamento')

    card = Frame(janela, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
    card.place(x=24, y=72, relwidth=1.0, width=-48, relheight=1.0, height=-156)

    def rotulo(texto, x, **posicao):
        etiqueta = Label(card, text=texto, bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9, "bold"))
        etiqueta.place(x=x, **posicao)
        return etiqueta

    # Data-Hora
    rotulo('Data-Hora', 20, y=10)
    entry_data_hora = criar_entrada_sga(card)
    entry_data_hora.place(x=20, y=36, width=190, height=30)
    entry_data_hora.insert(0, datetime.now().strftime("%d/%m/%Y - %H:%Mh"))

    def selecionar_data():
        def salvar_data():
            data_selecionada = cal.selection_get().strftime('%d/%m/%Y')
            hora_atual = datetime.now().strftime('%H:%M')
            entry_data_hora.delete(0, END)
            entry_data_hora.insert(0, f"{data_selecionada} - {hora_atual}h")
            janela_cal.destroy()

        janela_cal = Toplevel(janela)
        janela_cal.title("Selecione a Data")
        cal = Calendar(janela_cal, selectmode='day', date_pattern='dd-mm-yyyy')
        cal.pack(pady=20)
        Button(janela_cal, text="Salvar", command=salvar_data).pack(pady=10)

    criar_botao_sga(card, "Selecionar", selecionar_data, "neutro", fonte=(SGA_FONTE, 9, "bold")
                    ).place(x=218, y=36, width=100, height=30)

    # Localidade
    rotulo('Localidade', 344, y=10)
    combo_localidade = ttk.Combobox(card, values=OPCOES_LOCALIDADE_SGA, state="readonly",
                                    font=(SGA_FONTE, 10))
    combo_localidade.place(x=344, y=36, width=170, height=30)

    # Título
    rotulo('Título', 20, y=78)
    entry_titulo = criar_entrada_sga(card)
    entry_titulo.place(x=20, y=104, relwidth=1.0, width=-40, height=30)

    if processo_existente:
        _, titulo_atual, localidade_atual, status_atual, _ = processo_existente
        entry_titulo.insert(0, titulo_atual)
        entry_titulo.config(state="disabled")
        combo_localidade.set(localidade_atual)
        combo_localidade.config(state="disabled")

    # Descrição
    rotulo('Descrição do Lançamento', 20, y=146)
    frame_desc = Frame(card, bg=SGA_CARD)
    frame_desc.place(x=20, y=172, relwidth=1.0, width=-40, relheight=1.0, height=-312)
    scroll_desc = Scrollbar(frame_desc)
    scroll_desc.pack(side=RIGHT, fill=Y)
    texto_descricao = criar_area_texto_sga(frame_desc, wrap=WORD, yscrollcommand=scroll_desc.set)
    texto_descricao.pack(side=LEFT, fill=BOTH, expand=True)
    scroll_desc.config(command=texto_descricao.yview)

    # Documentos anexados
    rotulo('Documentos Anexados', 20, rely=1.0, y=-130, anchor="nw")
    lista_anexos = Listbox(card, font=(SGA_FONTE, 9), relief="flat", bd=0, activestyle="none",
                           bg="white", fg=SGA_TEXTO, selectbackground="#DCE8F8",
                           selectforeground=SGA_TEXTO, highlightthickness=1,
                           highlightbackground=SGA_BORDA, highlightcolor=SGA_AZUL)
    lista_anexos.place(x=20, rely=1.0, y=-102, anchor="nw", relwidth=1.0, width=-176, height=82)

    anexos_selecionados = []

    def anexar_arquivo():
        caminhos = filedialog.askopenfilenames(title="Selecionar Arquivo(s)", parent=janela,
                                                filetypes=[("Todos os arquivos", "*.*")])
        for caminho in caminhos:
            anexos_selecionados.append(caminho)
            lista_anexos.insert(END, os.path.basename(caminho))

    def remover_anexo():
        selecao = lista_anexos.curselection()
        if selecao:
            idx = selecao[0]
            lista_anexos.delete(idx)
            anexos_selecionados.pop(idx)

    criar_botao_sga(card, "Anexar Arquivo", anexar_arquivo, "primario", fonte=(SGA_FONTE, 9, "bold")
                    ).place(relx=1.0, x=-20, rely=1.0, y=-102, anchor="ne", width=130, height=36)
    criar_botao_sga(card, "Remover", remover_anexo, "sucesso", fonte=(SGA_FONTE, 9, "bold")
                    ).place(relx=1.0, x=-20, rely=1.0, y=-58, anchor="ne", width=130, height=36)

    def salvar():
        data_hora = entry_data_hora.get().strip()
        localidade = combo_localidade.get().strip()
        titulo = entry_titulo.get().strip().upper()
        descricao = texto_descricao.get("1.0", END).strip()

        if not data_hora or not localidade or not titulo or not descricao:
            messagebox.showwarning("Atenção",
                                    "Preencha Data-Hora, Localidade, Título e Descrição antes de salvar.",
                                    parent=janela)
            return

        if processo_existente:
            processo_id_final = processo_existente[0]
        else:
            existente_id = titulo_ja_existe(titulo)
            if existente_id:
                messagebox.showerror(
                    "Título já existe",
                    f"Já existe um processo com o título '{titulo}'.\n\n"
                    f"Para acrescentar um novo lançamento a esse processo já existente, "
                    f"feche esta janela e use o botão 'A' (Atualizar) na lista de processos.",
                    parent=janela)
                return
            processo_id_final = criar_processo(titulo, localidade)

        usuario = obter_nome_usuario_logado()
        lancamento_id = inserir_lancamento(processo_id_final, data_hora, usuario, descricao)

        for caminho in anexos_selecionados:
            anexar_documento(processo_id_final, lancamento_id, caminho)

        messagebox.showinfo("Sucesso", "Lançamento salvo com sucesso!", parent=janela)
        janela.destroy()
        callback_atualizar()

    rodape = criar_rodape_sga(janela)
    criar_botao_sga(rodape, "SALVAR", salvar, "primario"
                    ).place(relx=0.5, x=-150, rely=0.5, anchor="w", width=140, height=40)
    criar_botao_sga(rodape, "VOLTAR", janela.destroy, "sucesso"
                    ).place(relx=0.5, x=10, rely=0.5, anchor="w", width=140, height=40)
    Label(rodape, text=f"Lançado: {obter_nome_usuario_logado()}", bg=SGA_CARD, fg=SGA_TEXTO_SUAVE,
          font=(SGA_FONTE, 10, "italic")).place(relx=1.0, x=-24, rely=0.5, anchor="e")


# ---------------------------------------------------
# LEMBRETES AGENDADOS (BOTÃO "AGENDAR" DA JANELA PROCESSO)
# ---------------------------------------------------
# Data-hora de exibição gravada no formato "AAAA-MM-DD HH:MM", que permite comparar como texto.
FORMATO_DATA_HORA_LEMBRETE = "%Y-%m-%d %H:%M"


def listar_usuarios_sistema():
    """Retorna os nomes de usuário cadastrados no sistema (tabela de login), em ordem alfabética."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("SELECT usuario FROM Usuarios ORDER BY LOWER(usuario) ASC")
    usuarios = [linha[0] for linha in cursor.fetchall()]
    conexao.close()
    return usuarios


def criar_lembrete(processo_id, data_hora_exibicao, usuarios, mensagem, criado_por):
    """Grava um lembrete vinculado ao processo e os usuários que deverão recebê-lo.
    'data_hora_exibicao' é um datetime; retorna o id do lembrete."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO sga_agendamentos (processo_id, data_hora_exibicao, mensagem, criado_por, data_criacao, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (processo_id, data_hora_exibicao.strftime(FORMATO_DATA_HORA_LEMBRETE), mensagem, criado_por,
         datetime.now().strftime("%d/%m/%Y %H:%M:%S"), STATUS_LEMBRETE_ATIVO))
    lembrete_id = cursor.lastrowid
    cursor.executemany("INSERT INTO sga_agendamentos_usuarios (lembrete_id, usuario) VALUES (?, ?)",
                       [(lembrete_id, usuario) for usuario in usuarios])
    conexao.commit()
    conexao.close()
    return lembrete_id


def listar_lembretes(processo_id):
    """Retorna os lembretes ativos do processo, do mais próximo ao mais distante, cada um com
    a lista de (usuário, data_ciencia) dos destinatários."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, data_hora_exibicao, mensagem, criado_por FROM sga_agendamentos "
        "WHERE processo_id = ? AND status = ? ORDER BY data_hora_exibicao ASC",
        (processo_id, STATUS_LEMBRETE_ATIVO))
    resultado = []
    for lembrete_id, data_hora_exibicao, mensagem, criado_por in cursor.fetchall():
        cursor.execute("SELECT usuario, data_ciencia FROM sga_agendamentos_usuarios WHERE lembrete_id = ? "
                       "ORDER BY id ASC", (lembrete_id,))
        resultado.append({"id": lembrete_id, "data_hora_exibicao": data_hora_exibicao, "mensagem": mensagem,
                          "criado_por": criado_por, "usuarios": cursor.fetchall()})
    conexao.close()
    return resultado


def cancelar_lembrete(lembrete_id):
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("UPDATE sga_agendamentos SET status = ? WHERE id = ?", (STATUS_LEMBRETE_CANCELADO, lembrete_id))
    conexao.commit()
    conexao.close()


def listar_lembretes_pendentes_usuario(usuario):
    """Lembretes ativos, com data/hora já alcançada, destinados ao usuário e dos quais ele
    ainda não deu ciência."""
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT lu.id, p.titulo, l.mensagem, l.criado_por, l.data_hora_exibicao "
        "FROM sga_agendamentos_usuarios lu "
        "JOIN sga_agendamentos l ON l.id = lu.lembrete_id "
        "JOIN sga_processos p ON p.id = l.processo_id "
        "WHERE LOWER(lu.usuario) = ? AND lu.data_ciencia IS NULL AND l.status = ? "
        "AND l.data_hora_exibicao <= ? ORDER BY l.data_hora_exibicao ASC",
        (usuario.strip().lower(), STATUS_LEMBRETE_ATIVO, datetime.now().strftime(FORMATO_DATA_HORA_LEMBRETE)))
    linhas = cursor.fetchall()
    conexao.close()
    return linhas


def registrar_ciencia_lembrete(lembrete_usuario_id):
    conexao = sqlite3.connect(BANCO_SGA)
    cursor = conexao.cursor()
    cursor.execute("UPDATE sga_agendamentos_usuarios SET data_ciencia = ? WHERE id = ?",
                   (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), lembrete_usuario_id))
    conexao.commit()
    conexao.close()


def _formatar_data_hora_lembrete(texto):
    try:
        return datetime.strptime(texto, FORMATO_DATA_HORA_LEMBRETE).strftime("%d/%m/%Y - %H:%Mh")
    except (TypeError, ValueError):
        return texto or ""


def janela_lembrete_sga(titulo_processo, mensagem, criado_por, data_hora_exibicao):
    """Janela 'Lembrete do SGA' exibida no login. Retorna True se o usuário clicar em 'Ciente'
    (o lembrete não aparece mais para ele) ou False em 'Lembrar depois' / fechar a janela
    (o lembrete volta a aparecer no próximo login)."""
    resultado = {"ciente": False}

    janela = Toplevel(root)
    janela.title("Lembrete do SGA")
    janela.geometry('600x440')
    janela.resizable(False, False)
    janela['bg'] = SGA_FUNDO
    janela.attributes('-topmost', True)

    criar_cabecalho_sga(janela, 'Lembrete do SGA', altura=52)

    card = Frame(janela, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
    card.place(x=20, y=68, relwidth=1.0, width=-40, height=290)

    Label(card, text=f"O processo {titulo_processo} necessita de sua atenção.", bg=SGA_CARD, fg=SGA_AZUL,
          font=(SGA_FONTE, 12, "bold"), wraplength=520, justify="left", anchor="w"
          ).place(x=16, y=12, relwidth=1.0, width=-32)

    Label(card, text="Mensagem:", bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9, "bold")).place(x=16, y=68)

    frame_texto = Frame(card, bg=SGA_CARD)
    frame_texto.place(x=16, y=90, relwidth=1.0, width=-32, height=120)
    scroll = Scrollbar(frame_texto)
    scroll.pack(side=RIGHT, fill=Y)
    texto = criar_area_texto_sga(frame_texto, wrap=WORD, yscrollcommand=scroll.set)
    texto.pack(side=LEFT, fill=BOTH, expand=True)
    scroll.config(command=texto.yview)
    texto.insert("1.0", mensagem or "")
    texto.config(state=DISABLED)

    Label(card, text="Favor acessar o SGA – Sistema de Gestão de Atividades para verificar.", bg=SGA_CARD,
          fg=SGA_TEXTO, font=(SGA_FONTE, 10), anchor="w").place(x=16, y=222)
    Label(card, text=f"Agendado por {criado_por or '-'} para {_formatar_data_hora_lembrete(data_hora_exibicao)}",
          bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9, "italic"), anchor="w").place(x=16, y=252)

    def ciente():
        resultado["ciente"] = True
        janela.destroy()

    criar_botao_sga(janela, "Ciente", ciente, "sucesso"
                    ).place(relx=0.5, x=-160, y=378, width=150, height=38)
    criar_botao_sga(janela, "Lembrar depois", janela.destroy, "neutro"
                    ).place(relx=0.5, x=10, y=378, width=150, height=38)

    janela.grab_set()
    janela.focus_force()
    janela.wait_window()
    return resultado["ciente"]


def exibir_lembretes_sga_do_usuario(usuario):
    """Chamado logo após o login: mostra, um de cada vez, os lembretes do SGA já vencidos
    destinados ao usuário que acabou de entrar no sistema."""
    try:
        garantir_banco_sga()
        pendentes = listar_lembretes_pendentes_usuario(usuario)
    except sqlite3.Error:
        return
    for lembrete_usuario_id, titulo, mensagem, criado_por, data_hora_exibicao in pendentes:
        if janela_lembrete_sga(titulo, mensagem, criado_por, data_hora_exibicao):
            registrar_ciencia_lembrete(lembrete_usuario_id)


def tela_agendar_lembrete(parent, processo_id, titulo_processo):
    """Janela 'Agendar Lembrete': data, horário, até QTDE_LINHAS_USUARIO_LEMBRETE usuários e a
    mensagem que eles verão ao entrar no sistema a partir da data/hora programada. Também lista
    os lembretes já agendados para o processo, permitindo cancelá-los."""
    garantir_banco_sga()

    janela = Toplevel(parent)
    janela.title("Agendar Lembrete")
    janela.geometry('760x740')
    janela.minsize(760, 740)
    janela.resizable(False, True)
    janela['bg'] = SGA_FUNDO
    janela.transient(parent)

    criar_cabecalho_sga(janela, 'Agendar Lembrete', altura=52)

    card = Frame(janela, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
    card.place(x=20, y=68, relwidth=1.0, width=-40, relheight=1.0, height=-160)

    def rotulo(texto, x, y):
        Label(card, text=texto, bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9, "bold")).place(x=x, y=y)

    Label(card, text=f"Processo: {titulo_processo}", bg=SGA_CARD, fg=SGA_TEXTO,
          font=(SGA_FONTE, 10, "bold"), wraplength=680, justify="left", anchor="w"
          ).place(x=16, y=10, relwidth=1.0, width=-32)

    # Data e horário a partir dos quais o lembrete fica visível (padrão: próxima hora cheia)
    sugestao = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    rotulo("Data do lembrete", 16, 48)
    entry_data = criar_entrada_sga(card)
    entry_data.place(x=16, y=72, width=120, height=30)
    entry_data.insert(0, sugestao.strftime("%d/%m/%Y"))

    def selecionar_data():
        def salvar_data():
            entry_data.delete(0, END)
            entry_data.insert(0, cal.selection_get().strftime('%d/%m/%Y'))
            janela_cal.destroy()

        janela_cal = Toplevel(janela)
        janela_cal.title("Selecione a Data")
        janela_cal.transient(janela)
        cal = Calendar(janela_cal, selectmode='day', date_pattern='dd-mm-yyyy', mindate=datetime.now().date())
        cal.pack(pady=20)
        Button(janela_cal, text="Salvar", command=salvar_data).pack(pady=10)
        janela_cal.grab_set()

    criar_botao_sga(card, "Selecionar", selecionar_data, "neutro", fonte=(SGA_FONTE, 9, "bold")
                    ).place(x=142, y=72, width=100, height=30)

    rotulo("Horário do lembrete", 280, 48)
    combo_hora = ttk.Combobox(card, values=[f"{h:02d}" for h in range(24)], state="readonly",
                              font=(SGA_FONTE, 10))
    combo_hora.place(x=280, y=72, width=60, height=30)
    combo_hora.set(sugestao.strftime("%H"))
    Label(card, text=":", bg=SGA_CARD, fg=SGA_TEXTO, font=(SGA_FONTE, 11, "bold")).place(x=344, y=74)
    combo_minuto = ttk.Combobox(card, values=[f"{m:02d}" for m in range(60)], state="readonly",
                                font=(SGA_FONTE, 10))
    combo_minuto.place(x=356, y=72, width=60, height=30)
    combo_minuto.set(sugestao.strftime("%M"))
    Label(card, text="h", bg=SGA_CARD, fg=SGA_TEXTO, font=(SGA_FONTE, 10)).place(x=420, y=76)

    # Usuários que receberão o lembrete (lista dos usuários cadastrados no sistema)
    rotulo("Usuários que receberão o lembrete", 16, 116)
    opcoes_usuarios = [""] + listar_usuarios_sistema()
    combos_usuario = []
    for indice in range(QTDE_LINHAS_USUARIO_LEMBRETE):
        y = 140 + indice * 30
        Label(card, text=f"{indice + 1:02d}", bg=SGA_CARD, fg=SGA_TEXTO_SUAVE,
              font=(SGA_FONTE, 9)).place(x=16, y=y + 4)
        combo = ttk.Combobox(card, values=opcoes_usuarios, state="readonly", font=(SGA_FONTE, 10))
        combo.place(x=44, y=y, width=230, height=26)
        combos_usuario.append(combo)

    # Mensagem que será exibida aos usuários
    rotulo("Mensagem para os usuários", 300, 116)
    frame_mensagem = Frame(card, bg=SGA_CARD)
    frame_mensagem.place(x=300, y=140, relwidth=1.0, width=-316, height=296)
    scroll_mensagem = Scrollbar(frame_mensagem)
    scroll_mensagem.pack(side=RIGHT, fill=Y)
    texto_mensagem = criar_area_texto_sga(frame_mensagem, wrap=WORD, yscrollcommand=scroll_mensagem.set)
    texto_mensagem.pack(side=LEFT, fill=BOTH, expand=True)
    scroll_mensagem.config(command=texto_mensagem.yview)

    # Lembretes já agendados para este processo
    y_lista = 140 + QTDE_LINHAS_USUARIO_LEMBRETE * 30 + 10
    rotulo("Lembretes agendados para este processo", 16, y_lista)
    frame_lista = Frame(card, bg=SGA_CARD)
    frame_lista.place(x=16, y=y_lista + 24, relwidth=1.0, width=-150, relheight=1.0, height=-(y_lista + 36))
    scroll_lista = Scrollbar(frame_lista)
    scroll_lista.pack(side=RIGHT, fill=Y)
    lista_lembretes = Listbox(frame_lista, font=(SGA_FONTE, 9), relief="flat", bd=0, highlightthickness=1,
                              highlightbackground=SGA_BORDA, activestyle="none",
                              yscrollcommand=scroll_lista.set)
    lista_lembretes.pack(side=LEFT, fill=BOTH, expand=True)
    scroll_lista.config(command=lista_lembretes.yview)
    lembretes_exibidos = []

    detalhe_lista = Label(janela, text="Selecione um lembrete na lista para ver os usuários e a mensagem.",
                          bg=SGA_FUNDO, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 8), anchor="w", justify="left",
                          wraplength=710)
    detalhe_lista.place(x=20, rely=1.0, y=-66, anchor="sw", relwidth=1.0, width=-40)

    def montar_lista():
        lista_lembretes.delete(0, END)
        lembretes_exibidos.clear()
        for lembrete in listar_lembretes(processo_id):
            cientes = len([u for u, data_ciencia in lembrete["usuarios"] if data_ciencia])
            lista_lembretes.insert(END, f"{_formatar_data_hora_lembrete(lembrete['data_hora_exibicao'])}  |  "
                                        f"{len(lembrete['usuarios'])} usuário(s), {cientes} ciente(s)  |  "
                                        f"por {lembrete['criado_por'] or '-'}")
            lembretes_exibidos.append(lembrete)

    def ao_selecionar(event=None):
        selecao = lista_lembretes.curselection()
        if not selecao:
            return
        lembrete = lembretes_exibidos[selecao[0]]
        usuarios = ", ".join(f"{u} (ciente)" if data_ciencia else u for u, data_ciencia in lembrete["usuarios"])
        mensagem = " ".join((lembrete["mensagem"] or "").split())
        if len(mensagem) > 160:
            mensagem = mensagem[:160] + "..."
        detalhe_lista.config(text=f"Usuários: {usuarios}\nMensagem: {mensagem}")

    lista_lembretes.bind("<<ListboxSelect>>", ao_selecionar)

    def cancelar_selecionado():
        selecao = lista_lembretes.curselection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um lembrete na lista.", parent=janela)
            return
        if messagebox.askyesno("Cancelar Lembrete", "Deseja cancelar o lembrete selecionado?", parent=janela):
            cancelar_lembrete(lembretes_exibidos[selecao[0]]["id"])
            detalhe_lista.config(text="")
            montar_lista()

    criar_botao_sga(card, "Cancelar\nlembrete", cancelar_selecionado, "perigo", fonte=(SGA_FONTE, 9, "bold")
                    ).place(relx=1.0, x=-16, y=y_lista + 24, anchor="ne", width=100, height=44)

    montar_lista()

    def salvar():
        try:
            data = datetime.strptime(entry_data.get().strip(), "%d/%m/%Y")
        except ValueError:
            messagebox.showwarning("Atenção", "Informe a data no formato DD/MM/AAAA.", parent=janela)
            return
        data_hora_exibicao = data.replace(hour=int(combo_hora.get()), minute=int(combo_minuto.get()))
        if data_hora_exibicao <= datetime.now():
            messagebox.showwarning("Atenção", "A data e o horário do lembrete devem ser posteriores ao "
                                              "momento atual.", parent=janela)
            return

        usuarios = []
        for combo in combos_usuario:
            usuario = combo.get().strip()
            if usuario and usuario not in usuarios:
                usuarios.append(usuario)
        if not usuarios:
            messagebox.showwarning("Atenção", "Selecione ao menos um usuário.", parent=janela)
            return

        mensagem = texto_mensagem.get("1.0", END).strip()
        if not mensagem:
            messagebox.showwarning("Atenção", "Informe a mensagem do lembrete.", parent=janela)
            texto_mensagem.focus_set()
            return

        criar_lembrete(processo_id, data_hora_exibicao, usuarios, mensagem, obter_nome_usuario_logado())
        messagebox.showinfo("Sucesso",
                            f"Lembrete agendado para {data_hora_exibicao.strftime('%d/%m/%Y - %H:%Mh')}.\n\n"
                            f"Ele será exibido para {len(usuarios)} usuário(s) no login, a partir dessa "
                            f"data e horário.", parent=janela)
        for combo in combos_usuario:
            combo.set("")
        texto_mensagem.delete("1.0", END)
        montar_lista()

    criar_botao_sga(janela, "Salvar", salvar, "primario"
                    ).place(relx=0.5, x=-130, rely=1.0, y=-24, anchor="sw", width=120, height=38)
    criar_botao_sga(janela, "Voltar", janela.destroy, "neutro"
                    ).place(relx=0.5, x=10, rely=1.0, y=-24, anchor="sw", width=120, height=38)

    janela.grab_set()


def tela_ver_processo(parent, processo_id, callback_atualizar):
    """Janela 'Processo - {Título}': histórico completo, em ordem CRONOLÓGICA, com
    documentos anexados, cancelamento individual de cada lançamento, e os botões
    IMPRIMIR / VOLTAR / CONCLUIR / AGENDAR. (O cancelamento do processo inteiro é feito pelo
    botão 'C' na tela do índice, não mais aqui.)"""
    processo = buscar_processo(processo_id)
    if not processo:
        messagebox.showerror("Erro", "Processo não encontrado.", parent=parent)
        return
    _, titulo, localidade, status_processo, cancelado_por = processo

    janela = Toplevel(parent)
    janela.title(f"Processo - {titulo}")
    janela.geometry('1100x750')
    janela.minsize(1100, 750)
    janela.resizable(True, True)
    janela['bg'] = SGA_FUNDO

    criar_cabecalho_sga(janela, 'Processo')

    # Resumo: título do processo à esquerda e status à direita
    resumo = Frame(janela, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
    resumo.place(x=24, y=72, relwidth=1.0, width=-48, height=64)

    titulo_label = Label(resumo, text=titulo, font=(SGA_FONTE, 13, "bold"), bg=SGA_CARD,
                         fg=SGA_TEXTO, anchor="w", justify="left", wraplength=700)
    titulo_label.place(x=18, rely=0.5, anchor="w")
    resumo.bind("<Configure>", lambda e: titulo_label.config(wraplength=max(200, e.width - 280)))

    grupo_status = Frame(resumo, bg=SGA_CARD)
    grupo_status.place(relx=1.0, x=-18, rely=0.5, anchor="e")
    Label(grupo_status, text="Status:", bg=SGA_CARD, fg=SGA_TEXTO_SUAVE,
          font=(SGA_FONTE, 10, "bold")).pack(side=LEFT, padx=(0, 8))
    status_label = criar_selo_sga(grupo_status, "", SGA_AZUL, fonte=(SGA_FONTE, 10, "bold"))
    status_label.config(padx=14, pady=4)
    status_label.pack(side=LEFT)

    historico_frame = Frame(janela, bg=SGA_FUNDO)
    historico_frame.place(x=24, y=148, relwidth=1.0, width=-48, relheight=1.0, height=-236)

    inner_historico = criar_area_rolavel(historico_frame, bg=SGA_FUNDO)

    estado = {"lancamentos": [], "status_processo": status_processo, "cancelado_por": cancelado_por}
    processo_finalizado = status_processo in STATUS_FINALIZADOS

    def avisar_se_finalizado():
        """Confere o status atual no banco (a janela pode estar aberta há algum tempo).
        Retorna True, após avisar o usuário, se o processo estiver cancelado ou concluído."""
        atual = buscar_processo(processo_id)
        status_atual = atual[3] if atual else None
        if status_atual in STATUS_FINALIZADOS:
            messagebox.showwarning(
                "Processo " + status_atual,
                f"O processo está {status_atual} e não permite alterações.\n\n"
                f"Para alterá-lo, reabra-o primeiro pelo botão 'A' (Atualizar) do índice.",
                parent=janela)
            return True
        return False

    # As descrições acompanham a largura da janela: quando ela é maximizada, o texto
    # passa a quebrar linha mais à direita (a partir do valor original de 880).
    labels_descricao = []
    LARGURA_BASE_JANELA = 1100

    def ajustar_quebra_de_linha(event=None):
        largura = janela.winfo_width()
        if largura <= 1:
            return
        wrap = max(300, 880 + (largura - LARGURA_BASE_JANELA))
        for lbl in labels_descricao:
            lbl.config(wraplength=wrap)

    inner_historico.bind("<Configure>", ajustar_quebra_de_linha, add="+")

    CORES_STATUS_PROCESSO = {
        STATUS_CANCELADO: SGA_VERMELHO,
        STATUS_CONCLUIDO: SGA_VERDE,
        STATUS_REABERTO: "#CC8400",
        STATUS_ABERTO: SGA_AZUL,
    }

    def atualizar_cabecalho():
        estado_atual = str(estado["status_processo"])
        status_label.config(text=estado_atual,
                            bg=CORES_STATUS_PROCESSO.get(estado_atual, SGA_AZUL))

    def cancelar_este_lancamento(lancamento_id):
        confirmar = messagebox.askyesno(
            "Cancelar Lançamento",
            "Deseja cancelar este lançamento específico?\n\n"
            "Os documentos anexados a ele ficarão inacessíveis (serão removidos do banco "
            "de dados). O texto do lançamento permanece no histórico, tachado.",
            parent=janela)
        if confirmar and not avisar_se_finalizado():
            cancelar_lancamento(lancamento_id, obter_nome_usuario_logado())
            montar_historico()

    pode_excluir = (obter_nome_usuario_logado() or "").strip().lower() in \
        [u.lower() for u in USUARIOS_EXCLUSAO_LANCAMENTO]

    def excluir_este_lancamento(lancamento_id):
        if not pode_excluir:
            return
        confirmar = messagebox.askyesno(
            "Excluir Lançamento",
            "Deseja excluir DEFINITIVAMENTE este lançamento cancelado?\n\n"
            "Ele será removido do histórico do processo e essa ação não poderá ser desfeita.",
            parent=janela)
        if confirmar and not avisar_se_finalizado():
            excluir_lancamento(lancamento_id)
            montar_historico()

    def montar_historico():
        for widget in inner_historico.winfo_children():
            widget.destroy()
        labels_descricao.clear()

        estado["lancamentos"] = listar_lancamentos(processo_id)

        for lanc in estado["lancamentos"]:
            cancelado = lanc["status"] == STATUS_LANCAMENTO_CANCELADO
            lancamento_conclusao = str(lanc["descricao"] or "").startswith(PREFIXO_DESCRICAO_CONCLUSAO)

            fundo_card = "#FBF1F1" if cancelado else SGA_CARD
            borda_card = "#E8C9C9" if cancelado else SGA_BORDA
            if cancelado:
                cor_faixa = SGA_VERMELHO
            elif lancamento_conclusao:
                cor_faixa = SGA_VERDE  # barra lateral verde no lançamento da conclusão do processo
            else:
                cor_faixa = SGA_AZUL
            cor_lanc = SGA_VERMELHO if cancelado else SGA_TEXTO

            card_lanc = Frame(inner_historico, bg=fundo_card, highlightthickness=1,
                              highlightbackground=borda_card)
            card_lanc.pack(fill=X, padx=(0, 8), pady=(0, 10))
            Frame(card_lanc, bg=cor_faixa, width=5).pack(side=LEFT, fill=Y)

            corpo = Frame(card_lanc, bg=fundo_card)
            corpo.pack(side=LEFT, fill=BOTH, expand=True, padx=16, pady=12)

            topo = Frame(corpo, bg=fundo_card)
            topo.pack(fill=X)

            fonte_data = (SGA_FONTE, 10, "overstrike") if cancelado else (SGA_FONTE, 10, "bold")
            Label(topo, text=lanc["data_hora"], bg=fundo_card, font=fonte_data,
                  fg=cor_lanc).pack(side=LEFT)

            if not cancelado:
                lancamento_conclusao = str(lanc["descricao"] or "").startswith(PREFIXO_DESCRICAO_CONCLUSAO)

            if lancamento_conclusao or processo_finalizado:
                pass  # conclusão do processo, ou processo cancelado/concluído: sem "Cancelar" e "Excluir"
            elif not cancelado:
                criar_botao_sga(topo, "Cancelar", lambda lid=lanc["id"]: cancelar_este_lancamento(lid),
                                "neutro", fonte=(SGA_FONTE, 8), padx=8, pady=1
                                ).pack(side=LEFT, padx=12)
            elif pode_excluir:
                criar_botao_sga(topo, "Excluir", lambda lid=lanc["id"]: excluir_este_lancamento(lid),
                                "perigo", fonte=(SGA_FONTE, 8), padx=8, pady=1
                                ).pack(side=LEFT, padx=12)

            criar_selo_sga(topo, localidade, "#E3ECF8", cor_texto=SGA_AZUL).pack(side=RIGHT)

            fonte_desc = (SGA_FONTE, 10, "overstrike") if cancelado else (SGA_FONTE, 10)
            lbl_desc = Label(corpo, text=lanc["descricao"], bg=fundo_card, font=fonte_desc, fg=cor_lanc,
                             justify="left", anchor="w", wraplength=880)
            lbl_desc.pack(fill=X, pady=(10, 6))
            labels_descricao.append(lbl_desc)

            if not cancelado and lanc["documentos"]:
                docs_frame = Frame(corpo, bg=fundo_card)
                docs_frame.pack(fill=X, pady=(2, 6))
                for nome_original, caminho_armazenado in lanc["documentos"]:
                    criar_botao_sga(docs_frame, f"Documento: {nome_original}",
                                    lambda c=caminho_armazenado: os.startfile(c), "neutro",
                                    fonte=(SGA_FONTE, 9), padx=10, pady=3
                                    ).pack(side=LEFT, padx=(0, 8))

            if lanc["usuario"]:
                Label(corpo, text=f"Lançado: {lanc['usuario']}", bg=fundo_card,
                      font=(SGA_FONTE, 9, "italic"), fg=SGA_TEXTO_SUAVE).pack(anchor="e")

            if cancelado:
                Label(corpo, text=f"Cancelado – {lanc['cancelado_por']}", bg=fundo_card,
                      font=(SGA_FONTE, 9, "italic"), fg=SGA_VERMELHO).pack(anchor="e")

        ajustar_quebra_de_linha()

    atualizar_cabecalho()
    montar_historico()

    def imprimir():
        resposta = messagebox.askquestion(
            "Imprimir Processo",
            "Deseja excluir os lançamentos cancelados da impressão?",
            parent=janela)
        lancamentos_imprimir = estado["lancamentos"]
        if resposta == "yes":
            lancamentos_imprimir = [l for l in lancamentos_imprimir
                                     if l["status"] != STATUS_LANCAMENTO_CANCELADO]
        gerar_pdf_processo(titulo, localidade, lancamentos_imprimir,
                            estado["status_processo"], estado["cancelado_por"])

    def concluir():
        if avisar_se_finalizado():
            return
        confirmar = messagebox.askyesno(
            "Confirmar Conclusão",
            f"Deseja concluir o processo '{titulo}'?",
            parent=janela)
        if confirmar:
            usuario = obter_nome_usuario_logado()
            concluir_processo(processo_id)
            agora = datetime.now().strftime("%d/%m/%Y - %H:%Mh")
            inserir_lancamento(processo_id, agora, usuario, f"Processo concluído pelo usuário: {usuario}")
            messagebox.showinfo("Sucesso", "Processo concluído.", parent=janela)
            janela.destroy()
            callback_atualizar()

    def voltar():
        janela.destroy()
        callback_atualizar()

    def agendar():
        tela_agendar_lembrete(janela, processo_id, titulo)

    # Processo cancelado ou concluído não exibe o CONCLUIR (só volta após ser reaberto)
    botoes_rodape = [("IMPRIMIR", imprimir, "primario"), ("VOLTAR", voltar, "aviso")]
    if not processo_finalizado:
        botoes_rodape.append(("CONCLUIR", concluir, "sucesso"))
    botoes_rodape.append(("AGENDAR", agendar, "agendar"))

    rodape = criar_rodape_sga(janela)
    largura_botao, espaco_botoes = 140, 30
    x_inicial = -(len(botoes_rodape) * largura_botao + (len(botoes_rodape) - 1) * espaco_botoes) // 2
    for posicao, (texto_botao, comando_botao, estilo_botao) in enumerate(botoes_rodape):
        criar_botao_sga(rodape, texto_botao, comando_botao, estilo_botao
                        ).place(relx=0.5, x=x_inicial + posicao * (largura_botao + espaco_botoes),
                                rely=0.5, anchor="w", width=largura_botao, height=40)


def cmd_click24():
    """Tela principal do SGA: índice de processos, em ordem alfabética, com rolagem,
    botões C (Cancelar) / A (Atualizar) / V (Ver) por processo, busca por título e o
    botão Novo Lançamento."""
    global current_user
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return

    nome_logado = obter_nome_usuario_logado()
    if not nome_logado:
        messagebox.showwarning("Atenção", "Não foi possível identificar o usuário logado.")
        return

    garantir_banco_sga()

    indice_win = Toplevel(root)
    indice_win.title('COG - SGA')
    indice_win.geometry('1000x700')
    indice_win.minsize(1000, 700)
    indice_win.resizable(True, True)
    indice_win['bg'] = SGA_FUNDO

    cabecalho = criar_cabecalho_sga(indice_win, 'Sistema de Gestão de Atividades - Índice de Processos',
                                    altura=64)

    # Campo de busca (lupa desenhada + texto de ajuda que some ao digitar)
    busca_var = StringVar()
    TEXTO_AJUDA_BUSCA = "Buscar por título..."
    estado_busca = {"ajuda": True}

    caixa_busca = Frame(cabecalho, bg="white")
    caixa_busca.place(relx=1.0, x=-24, rely=0.5, anchor="e", width=250, height=34)
    criar_icone_lupa(caixa_busca).pack(side=LEFT, padx=(8, 0))
    entry_busca = Entry(caixa_busca, textvariable=busca_var, relief="flat", bd=0, bg="white",
                        fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 10), insertbackground=SGA_TEXTO)
    entry_busca.pack(side=LEFT, fill=BOTH, expand=True, padx=(4, 8), pady=6)
    entry_busca.insert(0, TEXTO_AJUDA_BUSCA)

    def ao_focar_busca(event=None):
        if estado_busca["ajuda"]:
            estado_busca["ajuda"] = False
            entry_busca.delete(0, END)
            entry_busca.config(fg=SGA_TEXTO)

    def ao_sair_busca(event=None):
        if not busca_var.get().strip():
            estado_busca["ajuda"] = True
            entry_busca.delete(0, END)
            entry_busca.insert(0, TEXTO_AJUDA_BUSCA)
            entry_busca.config(fg=SGA_TEXTO_SUAVE)

    entry_busca.bind("<FocusIn>", ao_focar_busca)
    entry_busca.bind("<FocusOut>", ao_sair_busca)

    lista_frame = Frame(indice_win, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
    lista_frame.place(x=24, y=84, relwidth=1.0, width=-48, relheight=1.0, height=-160)

    inner_indice = criar_area_rolavel(lista_frame, bg=SGA_CARD)

    # Rodapé: contador de processos, botão principal e legenda das cores
    contador_label = Label(indice_win, text="", bg=SGA_FUNDO, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9))
    contador_label.place(x=24, rely=1.0, y=-30, anchor="sw")

    legenda = Frame(indice_win, bg=SGA_FUNDO)
    legenda.place(relx=1.0, x=-24, rely=1.0, y=-30, anchor="se")
    for cor_legenda, texto_legenda in (("black", "Aberto / Reaberto"), (SGA_VERDE, "Concluído"),
                                        (SGA_VERMELHO, "Cancelado")):
        Label(legenda, text="■", bg=SGA_FUNDO, fg=cor_legenda, font=(SGA_FONTE, 9)
              ).pack(side=LEFT, padx=(12, 2))
        Label(legenda, text=texto_legenda, bg=SGA_FUNDO, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9)
              ).pack(side=LEFT)

    def montar_indice():
        for widget in inner_indice.winfo_children():
            widget.destroy()

        termo_busca = "" if estado_busca["ajuda"] else busca_var.get().strip().lower()

        exibidos = [p for p in listar_processos() if not termo_busca or termo_busca in p[1].lower()]
        contador_label.config(text=f"{len(exibidos)} processo(s)")

        if not exibidos:
            Label(inner_indice, text="Nenhum processo encontrado.", bg=SGA_CARD,
                  fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 11)).pack(pady=60)
            return

        for posicao, (processo_id, titulo, localidade, status, cancelado_por) in enumerate(exibidos):
            fundo_linha = SGA_CARD if posicao % 2 == 0 else "#F6F8FB"

            linha = Frame(inner_indice, bg=fundo_linha)
            linha.pack(fill=X)

            texto_titulo = f"{titulo} - {localidade}"

            if status == STATUS_CANCELADO:
                fonte_titulo = (SGA_FONTE, 10, "overstrike")
                cor_titulo = SGA_VERMELHO
                cor_faixa = SGA_VERMELHO
            elif status == STATUS_CONCLUIDO:
                fonte_titulo = (SGA_FONTE, 10)
                cor_titulo = SGA_VERDE
                cor_faixa = SGA_VERDE
            else:  # ABERTO ou REABERTO
                fonte_titulo = (SGA_FONTE, 10)
                cor_titulo = "black"
                cor_faixa = "black"

            Frame(linha, bg=cor_faixa, width=5).pack(side=LEFT, fill=Y)

            Label(linha, text=texto_titulo, bg=fundo_linha, fg=cor_titulo, font=fonte_titulo,
                  anchor="w", justify="left", wraplength=780
                  ).pack(side=LEFT, fill=X, expand=True, padx=(14, 0), pady=9)

            if status not in STATUS_FINALIZADOS:  # cancelado ou concluído: sem o botão "C"
                btn_c = criar_botao_sga(linha, "C", lambda pid=processo_id, tit=titulo: cancelar_este_processo(pid, tit),
                                        "perigo", fonte=(SGA_FONTE, 9, "bold"), width=3, pady=2)
                btn_c.pack(side=LEFT, padx=3, pady=6)
                ToolTipSGA(btn_c, "Cancelar")

            btn_a = criar_botao_sga(linha, "A", lambda pid=processo_id: abrir_atualizar(pid),
                                    "primario", fonte=(SGA_FONTE, 9, "bold"), width=3, pady=2)
            btn_a.pack(side=LEFT, padx=3, pady=6)
            ToolTipSGA(btn_a, "Atualizar")

            btn_v = criar_botao_sga(linha, "V", lambda pid=processo_id: abrir_ver(pid),
                                    "sucesso", fonte=(SGA_FONTE, 9, "bold"), width=3, pady=2)
            btn_v.pack(side=LEFT, padx=(3, 14), pady=6)
            ToolTipSGA(btn_v, "Ver")

            Frame(inner_indice, bg="#E5EAF1", height=1).pack(fill=X)

    def cancelar_este_processo(processo_id, titulo_processo):
        processo = buscar_processo(processo_id)
        if processo and processo[3] in STATUS_FINALIZADOS:
            messagebox.showwarning(
                "Processo " + processo[3],
                f"O processo '{titulo_processo}' está {processo[3]} e não pode ser cancelado.\n\n"
                f"Para alterá-lo, reabra-o primeiro pelo botão 'A' (Atualizar).",
                parent=indice_win)
            montar_indice()
            return
        confirmar = messagebox.askyesno(
            "Confirmar Cancelamento",
            f"Deseja realmente cancelar o processo '{titulo_processo}'?\n\n"
            f"Todo o histórico e os documentos serão mantidos; apenas o status "
            f"passará a CANCELADO.",
            parent=indice_win)
        if confirmar:
            justificativa = solicitar_justificativa(indice_win, titulo_processo)
            if justificativa is None:
                return
            usuario = obter_nome_usuario_logado()
            cancelar_processo(processo_id, usuario)
            agora = datetime.now().strftime("%d/%m/%Y - %H:%Mh")
            descricao = (f"Processo cancelado pelo usuário: {usuario}\n"
                         f"Justificativa: {justificativa}")
            inserir_lancamento(processo_id, agora, usuario, descricao)
            montar_indice()

    def abrir_atualizar(processo_id=None):
        if processo_id:
            processo = buscar_processo(processo_id)
            if processo and processo[3] in (STATUS_CANCELADO, STATUS_CONCLUIDO):
                status_atual = processo[3]
                acao_texto = "cancelado" if status_atual == STATUS_CANCELADO else "concluído"
                resposta = messagebox.askquestion(
                    f"Processo {status_atual}",
                    f"O processo '{processo[1]}' está {acao_texto} e não permite novos "
                    f"lançamentos.\n\nDeseja reabri-lo para incluir um novo lançamento?",
                    parent=indice_win)
                if resposta != "yes":
                    return
                reabrir_processo(processo_id)
                usuario = obter_nome_usuario_logado()
                agora = datetime.now().strftime("%d/%m/%Y - %H:%Mh")
                inserir_lancamento(processo_id, agora, usuario, f"Processo reaberto pelo usuário: {usuario}")
                montar_indice()
        tela_atualizar_novo_lancamento(indice_win, processo_id, montar_indice)

    def abrir_ver(processo_id):
        tela_ver_processo(indice_win, processo_id, montar_indice)

    busca_var.trace_add("write", lambda *args: montar_indice())

    montar_indice()

    criar_botao_sga(indice_win, "Novo Lançamento", lambda: abrir_atualizar(None), "primario"
                    ).place(relx=0.5, rely=1.0, y=-18, anchor="s", width=210, height=40)

# =======cascate PRIMEIRA PARTE termina aqui

#Click_25
# ==========cascate PRIMEIRA PARTE inicia aqui ===================================
# ---------------------------------------------------
# Doc_Lib. - BIBLIOTECA DE DOCUMENTOS (CLICK_25)
# ATEIE - Autorização para Trabalhos em Equipamentos de Interligação Energizados
# (AI, MO e SM_Avulso: "Página em Construção" - estrutura preparada para o futuro)
# ---------------------------------------------------

# Mesmo banco de dados já usado no restante do aplicativo (login, SGA, demais módulos).
BANCO_DOC_LIB = "dados_turno.db"

# Pasta onde os documentos gerados pelo Doc_Lib. ficam arquivados por tempo indeterminado
# (uma subpasta por tipo de documento e por ano; nenhum arquivo é apagado ou sobrescrito).
# Para arquivar numa pasta da rede, troque o caminho abaixo pelo caminho UNC, por exemplo:
#     PASTA_ARQUIVO_DOC_LIB = r"\\servidor\cog\Doc_Lib"
# Se a pasta configurada estiver indisponível, o documento é arquivado na pasta local
# (PASTA_ARQUIVO_DOC_LIB_LOCAL) e o usuário é avisado.
PASTA_ARQUIVO_DOC_LIB_LOCAL = os.path.join(PASTA_BASE, "doc_lib_arquivo")
PASTA_ARQUIVO_DOC_LIB = PASTA_ARQUIVO_DOC_LIB_LOCAL

LOGO_ATEIE = os.path.join(PASTA_BASE, "logo_ateie.png")

# Empresas do ATEIE: duas listas independentes (hoje com os mesmos nomes), porque as empresas que solicitam o ATEIE
# são diferentes das empresas que recebem a notificação. Para alterar uma lista basta editá-la aqui, sem mexer na
# outra; "OUTRA" deve continuar como última opção (ela libera o campo para digitar o nome da empresa).
DOC_LIB_EMPRESAS_SOLICITANTES_ATEIE = ["AXIA", "EDP", "ENGIE", "CELEO_REDES", "ENERGISA", "CTEEP", "CBA", "EQUATORIAL",
                                       "OUTRA"]        # combobox "Empresa Solicitante"
DOC_LIB_EMPRESAS_NOTIFICADAS_ATEIE = ["AXIA", "EDP", "ENGIE", "CELEO_REDES", "ENERGISA", "CTEEP", "CBA", "EQUATORIAL",
                                      "OUTRA"]         # combobox "Empresa" de "Pessoal Notificado"
DOC_LIB_CLASSIFICACOES_ATEIE = ["Programado", "Urgência"]
# Texto padrão do campo "Observações": obrigatório em todos os documentos (entra já preenchido no formulário)
DOC_LIB_TEXTO_PADRAO_OBSERVACOES = (
    "Bloquear ou manter bloqueado o religamento automático de todos os disjuntores que alimentam os "
    "equipamentos de interligação sob intervenção, condicionando qualquer religamento manual ao prévio contato "
    "e à autorização deste COG.")
# campos do formulário sempre apresentados em caixa alta (tela, lista e PDF), qualquer que seja a digitação
DOC_LIB_CAMPOS_CAIXA_ALTA = ("equipamento", "empresa", "empresa_outra", "local")
DOC_LIB_LIMITE_NOTIFICACOES = 3        # linhas de "De acordo" (Pessoas/Áreas notificadas)
DOC_LIB_LIMITE_PESSOAL = 3             # linhas de "Pessoal Notificado"
DOC_LIB_LINHAS_INTERVENCOES = 10       # intervenções por documento ATEIE

# Situação de cada ATEIE. Cada linha da tabela de intervenções é um ATEIE com número próprio e com status
# próprio, calculado automaticamente por doc_lib_calcular_status e gravado na intervenção.
STATUS_ATEIE_EM_ANALISE = "Em análise"
# documento gerado, mas ainda sem o "De acordo" (antes da versão atual este status se chamava "Aprovada")
STATUS_ATEIE_AGUARDA_DE_ACORDO = "Aguarda De Acordo"
STATUS_ATEIE_APROVADA_ANTIGO = "Aprovada"
STATUS_ATEIE_APROVADO_EXECUCAO = "Aprovado para Execução"
STATUS_ATEIE_EM_EXECUCAO = "Em Execução"
STATUS_ATEIE_CONCLUIDO = "Concluído"
# ATEIE cancelado mantém o número (nunca reaproveitado) e fica registrado no documento
STATUS_ATEIE_CANCELADO = "Cancelado"
DOC_LIB_STATUS_ATEIE = [STATUS_ATEIE_EM_ANALISE, STATUS_ATEIE_AGUARDA_DE_ACORDO, STATUS_ATEIE_APROVADO_EXECUCAO,
                        STATUS_ATEIE_EM_EXECUCAO, STATUS_ATEIE_CONCLUIDO, STATUS_ATEIE_CANCELADO]
# Só é possível cancelar um ATEIE antes de entrar em execução ("Em análise", "Aguarda De Acordo" ou "Aprovado para
# Execução"): em execução o ATEIE somente pode ser concluído (procedimento); concluído e cancelado também não
# podem ser cancelados
DOC_LIB_STATUS_CANCELAVEIS = (STATUS_ATEIE_EM_ANALISE, STATUS_ATEIE_AGUARDA_DE_ACORDO, STATUS_ATEIE_APROVADO_EXECUCAO)

# Colunas 2 a 13 da tabela de intervenções: (campo no banco, cabeçalho, descrição, tipo)
DOC_LIB_COLUNAS_INTERVENCAO = [
    ("prev_data_inicio", "Data", "Data de início programado", "data"),
    ("prev_hora_inicio", "Hora", "Hora de início programado", "hora"),
    ("prev_data_termino", "Data", "Data de término programado", "data"),
    ("prev_hora_termino", "Hora", "Hora de término programado", "hora"),
    ("real_data_inicio", "Data", "Data de início efetivo - Realizado", "data"),
    ("real_hora_inicio", "Hora", "Hora de início efetivo - Realizado", "hora"),
    ("real_os_r_inicio", "OS-R",
     "OS-R: operador da empresa responsável (que originou o ATEIE) que autorizou o início das atividades", "texto"),
    ("real_os_oe_inicio", "OS-OE",
     "OS-OE: operador da outra empresa que concordou com o início das atividades", "texto"),
    ("real_data_termino", "Data", "Data de término efetivo - Realizado", "data"),
    ("real_hora_termino", "Hora", "Hora de término efetivo - Realizado", "hora"),
    ("real_os_r_termino", "OS-R",
     "OS-R: operador da empresa responsável que informou o término das atividades", "texto"),
    ("real_os_oe_termino", "OS-OE",
     "OS-OE: operador da outra empresa que foi comunicado sobre o término das atividades", "texto"),
]
# Os 4 campos que "consomem" o número da intervenção quando preenchidos (colunas 2 a 5)
DOC_LIB_CAMPOS_PROGRAMADOS = ("prev_data_inicio", "prev_hora_inicio", "prev_data_termino", "prev_hora_termino")
# Colunas 6 a 9: quando as quatro estão preenchidas o ATEIE passa a "Em Execução"
DOC_LIB_CAMPOS_INICIO = ("real_data_inicio", "real_hora_inicio", "real_os_r_inicio", "real_os_oe_inicio")
# Colunas 10 a 13: quando as quatro estão preenchidas o ATEIE passa a "Concluído"
DOC_LIB_CAMPOS_TERMINO = ("real_data_termino", "real_hora_termino", "real_os_r_termino", "real_os_oe_termino")
# Colunas 6 a 13: as únicas que continuam editáveis depois que o ATEIE é emitido (documento gerado)
DOC_LIB_CAMPOS_EXECUCAO = DOC_LIB_CAMPOS_INICIO + DOC_LIB_CAMPOS_TERMINO
_DOC_LIB_DESCRICAO_CAMPO = {chave: descricao for chave, _, descricao, _ in DOC_LIB_COLUNAS_INTERVENCAO}

# Colunas dos blocos "De acordo" e "Pessoal Notificado": (campo, rótulo, tipo)
DOC_LIB_COLUNAS_NOTIFICACAO = [("nome", "Nome", "texto"), ("data", "Data", "data"), ("hora", "Hora", "hora")]
# tipo "empresa": Combobox com DOC_LIB_EMPRESAS_NOTIFICADAS_ATEIE e, na opção OUTRA, campo para digitar o nome
DOC_LIB_COLUNAS_PESSOAL = [("nome", "Nome", "texto"), ("empresa", "Empresa", "empresa"), ("setor", "Setor", "texto"),
                           ("data", "Data", "data"), ("hora", "Hora", "hora")]


class DocLibConflito(Exception):
    """O documento foi alterado (ou removido) por outro usuário depois de aberto nesta janela."""


class DocLibBloqueado(Exception):
    """Tentativa de alterar dados protegidos (ATEIE já emitido, execução já salva ou ainda não permitida)."""


class DocLibRegra(Exception):
    """Dado de execução que contraria uma regra de data do ATEIE (colunas 6 e 10)."""


# ---------------------------------------------------
# DATAS E HORAS (padrão brasileiro)
# ---------------------------------------------------
def doc_lib_normalizar_data(texto, ano_curto=False):
    """Converte o que o usuário digitou (06/10/26, 06102026, 6-10-2026...) para dd/mm/aa
    (ano_curto=True) ou dd/mm/aaaa. Retorna None se o texto não for uma data válida."""
    texto = (texto or "").strip()
    if not texto:
        return None
    partes = re.split(r"[/\-.\s]+", texto)
    if len(partes) == 1 and partes[0].isdigit() and len(partes[0]) in (6, 8):
        numeros = partes[0]
        partes = [numeros[:2], numeros[2:4], numeros[4:]]
    if len(partes) != 3 or not all(parte.isdigit() for parte in partes) or len(partes[2]) not in (2, 4):
        return None
    dia, mes, ano = int(partes[0]), int(partes[1]), int(partes[2])
    if len(partes[2]) == 2:
        ano += 2000
    if not 2000 <= ano <= 2099:
        return None
    try:
        data = datetime(ano, mes, dia)
    except ValueError:
        return None
    return data.strftime("%d/%m/%y" if ano_curto else "%d/%m/%Y")


def doc_lib_normalizar_hora(texto):
    """Converte 1530, 15:30, 15h30 ou 9:05 para HH:MM. Retorna None se a hora for inválida."""
    texto = (texto or "").strip().lower()
    if not texto:
        return None
    achado = re.fullmatch(r"(\d{1,2})\s*[:h.]\s*(\d{2})", texto) or re.fullmatch(r"(\d{1,2})(\d{2})", texto)
    if not achado:
        return None
    hora, minuto = int(achado.group(1)), int(achado.group(2))
    if hora > 23 or minuto > 59:
        return None
    return f"{hora:02d}:{minuto:02d}"


def _doc_lib_data_hora(data_texto, hora_texto):
    """datetime a partir de data e hora já informadas (qualquer formato aceito); None se inválidas."""
    data = doc_lib_normalizar_data(data_texto)
    hora = doc_lib_normalizar_hora(hora_texto)
    if not data or not hora:
        return None
    return datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M")


def doc_lib_formatar_numero(sequencia, ano):
    """Número da intervenção no formato 0001/26 (quatro dígitos, barra e dois dígitos do ano)."""
    return f"{sequencia:04d}/{ano % 100:02d}"


# ---------------------------------------------------
# BANCO DE DADOS DO DOC_LIB.
# ---------------------------------------------------
def doc_lib_conectar(manual=False):
    """Conexão com o banco. Com manual=True as transações são controladas pelo código
    (BEGIN IMMEDIATE ... COMMIT), necessário para consumir o número da intervenção sem
    risco de duas pessoas receberem o mesmo número ao salvar ao mesmo tempo."""
    conexao = sqlite3.connect(BANCO_DOC_LIB, timeout=15, isolation_level=None if manual else "")
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def garantir_banco_doc_lib():
    """Cria as tabelas do Doc_Lib. (se não existirem) no mesmo banco do aplicativo.

    Modelo de dados do ATEIE:
      doclib_ateie                 - dados gerais do documento (emitido = 1 depois de "Gerar Documento")
      doclib_ateie_notificacoes    - "De acordo" (Pessoas/Áreas notificadas)
      doclib_ateie_pessoal         - "Pessoal Notificado"
      doclib_ateie_intervencoes    - UMA linha por ATEIE (intervenção), cada uma com número, status,
                                     dados de programação, execução/normalização e cancelamento
                                     próprios (cancelar ou mudar o status de um ATEIE não afeta o
                                     documento nem os demais ATEIE)
      doclib_ateie_pdfs            - cada PDF gerado e arquivado
      doclib_numeracao             - último número emitido por tipo de documento e por ano
    """
    conexao = doc_lib_conectar()
    cursor = conexao.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS doclib_ateie (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        classificacao TEXT NOT NULL,
                        equipamento TEXT NOT NULL,
                        empresa TEXT NOT NULL,
                        empresa_outra TEXT,
                        local_servico TEXT NOT NULL,
                        servicos TEXT NOT NULL,
                        observacoes TEXT,
                        documentos_vinculados TEXT,
                        nota TEXT,
                        solicitado_por TEXT NOT NULL,
                        solicitado_por_usuario TEXT,
                        data_preenchimento TEXT NOT NULL,
                        hora_preenchimento TEXT NOT NULL,
                        revisao INTEGER NOT NULL DEFAULT 1,
                        emitido INTEGER NOT NULL DEFAULT 0,
                        emitido_em TEXT,
                        emitido_por TEXT,
                        criado_em TEXT,
                        atualizado_por TEXT,
                        atualizado_em TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS doclib_ateie_notificacoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ateie_id INTEGER NOT NULL,
                        ordem INTEGER NOT NULL,
                        nome TEXT,
                        data TEXT,
                        hora TEXT,
                        FOREIGN KEY(ateie_id) REFERENCES doclib_ateie(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS doclib_ateie_pessoal (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ateie_id INTEGER NOT NULL,
                        ordem INTEGER NOT NULL,
                        nome TEXT,
                        empresa TEXT,
                        empresa_outra TEXT,
                        setor TEXT,
                        data TEXT,
                        hora TEXT,
                        FOREIGN KEY(ateie_id) REFERENCES doclib_ateie(id))''')

    colunas_intervencao = ",\n                        ".join(
        f"{chave} TEXT" for chave, _, _, _ in DOC_LIB_COLUNAS_INTERVENCAO)
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS doclib_ateie_intervencoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ateie_id INTEGER NOT NULL,
                        ordem INTEGER NOT NULL,
                        numero TEXT UNIQUE NOT NULL,
                        ano INTEGER NOT NULL,
                        sequencia INTEGER NOT NULL,
                        {colunas_intervencao},
                        status TEXT NOT NULL DEFAULT 'Em análise',
                        cancelada_por TEXT,
                        data_cancelamento TEXT,
                        justificativa_cancelamento TEXT,
                        UNIQUE(ateie_id, ordem),
                        FOREIGN KEY(ateie_id) REFERENCES doclib_ateie(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS doclib_ateie_pdfs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ateie_id INTEGER NOT NULL,
                        revisao INTEGER,
                        caminho TEXT NOT NULL,
                        gerado_por TEXT,
                        gerado_em TEXT,
                        FOREIGN KEY(ateie_id) REFERENCES doclib_ateie(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS doclib_numeracao (
                        tipo TEXT NOT NULL,
                        ano INTEGER NOT NULL,
                        ultimo INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY (tipo, ano))''')

    # bancos criados por versões anteriores do Click_25: colunas novas
    _adicionar_coluna_se_necessario(cursor, "doclib_ateie", "solicitado_por_usuario", "TEXT")
    _adicionar_coluna_se_necessario(cursor, "doclib_ateie", "emitido", "INTEGER NOT NULL DEFAULT 0")
    _adicionar_coluna_se_necessario(cursor, "doclib_ateie", "emitido_em", "TEXT")
    _adicionar_coluna_se_necessario(cursor, "doclib_ateie", "emitido_por", "TEXT")
    _adicionar_coluna_se_necessario(cursor, "doclib_ateie_pessoal", "empresa_outra", "TEXT")

    conexao.commit()
    conexao.close()
    _doc_lib_migrar_dados()


def _doc_lib_migrar_dados():
    """Ajusta ao modelo atual os registros gravados por versões anteriores do Click_25 (pode ser
    executada várias vezes: só mexe no que ainda está no formato antigo)."""
    garantir_nome_completo_usuarios()
    nomes = {usuario.lower(): nome for usuario, nome in listar_nomes_completos_usuarios()}

    # verificação só de leitura: na grande maioria das aberturas não há nada a migrar e nada é gravado
    leitura = doc_lib_conectar()
    try:
        cur = leitura.cursor()
        precisa = (
            cur.execute("SELECT 1 FROM doclib_ateie WHERE solicitado_por_usuario IS NULL "
                        "OR TRIM(solicitado_por_usuario) = '' LIMIT 1").fetchone()
            or cur.execute("SELECT 1 FROM doclib_ateie_intervencoes WHERE status IN ('ATIVA', 'CANCELADA') "
                           "LIMIT 1").fetchone()
            or cur.execute("SELECT 1 FROM doclib_ateie WHERE emitido = 0 AND id IN "
                           "(SELECT ateie_id FROM doclib_ateie_pdfs) LIMIT 1").fetchone()
            or any((empresa or "").strip() and empresa not in DOC_LIB_EMPRESAS_NOTIFICADAS_ATEIE
                   for (empresa,) in cur.execute("SELECT empresa FROM doclib_ateie_pessoal").fetchall())
            or cur.execute("SELECT 1 FROM doclib_ateie_intervencoes WHERE status = ? LIMIT 1",
                           (STATUS_ATEIE_APROVADA_ANTIGO,)).fetchone()
            or cur.execute("SELECT 1 FROM doclib_ateie WHERE observacoes IS NULL OR TRIM(observacoes) = '' "
                           "LIMIT 1").fetchone()
            or any(solicitado_por == login and nomes.get((login or "").lower())
                   for solicitado_por, login in cur.execute(
                       "SELECT solicitado_por, solicitado_por_usuario FROM doclib_ateie").fetchall()))
    finally:
        leitura.close()
    if not precisa:
        return

    conexao = doc_lib_conectar(manual=True)
    cursor = conexao.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        # login e nome completo do solicitante (antes o campo guardava o login)
        cursor.execute("UPDATE doclib_ateie SET solicitado_por_usuario = solicitado_por "
                       "WHERE solicitado_por_usuario IS NULL OR TRIM(solicitado_por_usuario) = ''")
        cursor.execute("SELECT id, solicitado_por, solicitado_por_usuario FROM doclib_ateie")
        for ateie_id, solicitado_por, login in cursor.fetchall():
            nome = nomes.get((login or "").lower())
            if nome and solicitado_por == login:
                cursor.execute("UPDATE doclib_ateie SET solicitado_por = ? WHERE id = ?", (nome, ateie_id))
        # Observações passou a ser obrigatória, com o texto padrão: documentos antigos sem texto recebem o padrão
        cursor.execute("UPDATE doclib_ateie SET observacoes = ? WHERE observacoes IS NULL OR TRIM(observacoes) = ''",
                       (DOC_LIB_TEXTO_PADRAO_OBSERVACOES,))
        # documento que já teve PDF gerado é considerado emitido
        cursor.execute("UPDATE doclib_ateie SET emitido = 1 WHERE emitido = 0 AND id IN "
                       "(SELECT ateie_id FROM doclib_ateie_pdfs)")
        # empresa do pessoal notificado: antes texto livre, agora lista (o que não for da lista vira OUTRA)
        cursor.execute("SELECT id, empresa FROM doclib_ateie_pessoal")
        for pessoal_id, empresa in cursor.fetchall():
            empresa = (empresa or "").strip()
            if not empresa or empresa in DOC_LIB_EMPRESAS_NOTIFICADAS_ATEIE:
                continue
            igual = next((e for e in DOC_LIB_EMPRESAS_NOTIFICADAS_ATEIE[:-1] if e.lower() == empresa.lower()), None)
            if igual:
                cursor.execute("UPDATE doclib_ateie_pessoal SET empresa = ? WHERE id = ?", (igual, pessoal_id))
            else:
                cursor.execute("UPDATE doclib_ateie_pessoal SET empresa = 'OUTRA', empresa_outra = ? WHERE id = ?",
                               (empresa, pessoal_id))
        # status antigos (ATIVA/CANCELADA) para o fluxo atual
        colunas = ", ".join(f"i.{chave}" for chave in DOC_LIB_CAMPOS_EXECUCAO)
        cursor.execute(f"SELECT i.id, i.status, a.emitido, {colunas} FROM doclib_ateie_intervencoes i "
                       f"JOIN doclib_ateie a ON a.id = i.ateie_id WHERE i.status IN ('ATIVA', 'CANCELADA')")
        for linha in cursor.fetchall():
            item = dict(zip(["id", "status", "emitido"] + list(DOC_LIB_CAMPOS_EXECUCAO), linha))
            item["status"] = STATUS_ATEIE_CANCELADO if item["status"] == "CANCELADA" else ""
            cursor.execute("UPDATE doclib_ateie_intervencoes SET status = ? WHERE id = ?",
                           (doc_lib_calcular_status(item, bool(item["emitido"])), item["id"]))
        # o status "Aprovada" passou a se chamar "Aguarda De Acordo" (ou "Aprovado para Execução", se o "De acordo"
        # do documento emitido já estiver preenchido)
        cursor.execute("UPDATE doclib_ateie_intervencoes SET status = ? WHERE status = ?",
                       (STATUS_ATEIE_AGUARDA_DE_ACORDO, STATUS_ATEIE_APROVADA_ANTIGO))
        cursor.execute("SELECT id FROM doclib_ateie WHERE emitido = 1")
        for (ateie_id,) in cursor.fetchall():
            _doc_lib_recalcular_status(cursor, ateie_id, True)
        cursor.execute("COMMIT")
    except Exception:
        if conexao.in_transaction:
            cursor.execute("ROLLBACK")
        raise
    finally:
        conexao.close()


def doc_lib_de_acordo_completo(notificacoes):
    """"De acordo" preenchido na totalidade: pelo menos uma linha e toda linha com conteúdo tem nome, data e hora."""
    chaves = ("nome", "data", "hora")
    linhas = [linha for linha in notificacoes or [] if any(str(linha.get(c) or "").strip() for c in chaves)]
    return bool(linhas) and all(all(str(linha.get(c) or "").strip() for c in chaves) for linha in linhas)


def doc_lib_calcular_status(item, emitido, de_acordo=False):
    """Status automático de um ATEIE (uma intervenção), em função do que já aconteceu com ele:
      Cancelado ................ foi cancelado (nunca volta atrás)
      Em análise ............... salvo, mas o documento ainda não foi gerado
      Concluído ................ documento gerado e colunas 10 a 13 (término efetivo) todas preenchidas
      Em Execução .............. documento gerado e colunas 6 a 9 (início efetivo) todas preenchidas
      Aprovado para Execução ... documento gerado e "De acordo" preenchido (nome, data e hora)
      Aguarda De Acordo ........ documento gerado, ainda sem o "De acordo"
    Preenchimento parcial das colunas 6 a 9 ou 10 a 13 não muda o status."""
    if item.get("status") == STATUS_ATEIE_CANCELADO:
        return STATUS_ATEIE_CANCELADO
    if not emitido:
        return STATUS_ATEIE_EM_ANALISE

    def completo(chaves):
        return all(str(item.get(chave) or "").strip() for chave in chaves)

    if completo(DOC_LIB_CAMPOS_TERMINO):
        return STATUS_ATEIE_CONCLUIDO
    if completo(DOC_LIB_CAMPOS_INICIO):
        return STATUS_ATEIE_EM_EXECUCAO
    return STATUS_ATEIE_APROVADO_EXECUCAO if de_acordo else STATUS_ATEIE_AGUARDA_DE_ACORDO


def _doc_lib_recalcular_status(cursor, ateie_id, emitido):
    """Recalcula e grava o status de cada ATEIE (intervenção) do documento, um a um."""
    cursor.execute("SELECT nome, data, hora FROM doclib_ateie_notificacoes WHERE ateie_id = ?", (ateie_id,))
    de_acordo = doc_lib_de_acordo_completo([{"nome": n, "data": d, "hora": h} for n, d, h in cursor.fetchall()])
    cursor.execute(f"SELECT id, status, {', '.join(DOC_LIB_CAMPOS_EXECUCAO)} FROM doclib_ateie_intervencoes "
                   f"WHERE ateie_id = ?", (ateie_id,))
    for linha in cursor.fetchall():
        item = dict(zip(["id", "status"] + list(DOC_LIB_CAMPOS_EXECUCAO), linha))
        novo = doc_lib_calcular_status(item, emitido, de_acordo)
        if novo != item["status"]:
            cursor.execute("UPDATE doclib_ateie_intervencoes SET status = ? WHERE id = ?", (novo, item["id"]))


def _doc_lib_ultimo_numero(cursor, tipo, ano):
    """Último número já emitido no ano (0 se ainda não houve). Considera também o maior número
    gravado nas intervenções, como segurança caso o contador tenha ficado para trás."""
    cursor.execute("SELECT ultimo FROM doclib_numeracao WHERE tipo = ? AND ano = ?", (tipo, ano))
    linha = cursor.fetchone()
    ultimo = linha[0] if linha else 0
    if tipo == "ATEIE":
        cursor.execute("SELECT MAX(sequencia) FROM doclib_ateie_intervencoes WHERE ano = ?", (ano,))
        ultimo = max(ultimo, cursor.fetchone()[0] or 0)
    return ultimo


def _doc_lib_consumir_numero(cursor, tipo, ano):
    """Consome o próximo número do ano (sequencial, crescente, reiniciado a cada ano).
    Deve ser chamado dentro de uma transação aberta (BEGIN IMMEDIATE)."""
    proximo = _doc_lib_ultimo_numero(cursor, tipo, ano) + 1
    cursor.execute("INSERT OR REPLACE INTO doclib_numeracao (tipo, ano, ultimo) VALUES (?, ?, ?)",
                   (tipo, ano, proximo))
    return proximo


def doc_lib_numeros_previstos(quantidade, tipo="ATEIE"):
    """Próximos números do ano corrente SEM consumi-los (apenas para exibir na tela enquanto
    o documento ainda não foi salvo)."""
    ano = datetime.now().year
    conexao = doc_lib_conectar()
    try:
        ultimo = _doc_lib_ultimo_numero(conexao.cursor(), tipo, ano)
    finally:
        conexao.close()
    return [doc_lib_formatar_numero(ultimo + posicao, ano) for posicao in range(1, quantidade + 1)]


def doc_lib_erros_datas_execucao(item, gravado=None):
    """Regras de data da execução de um ATEIE (item = linha da tabela):
      - coluna 6 (data de início efetivo) tem de ser IGUAL à coluna 2 (data de início programado);
      - coluna 10 (data de término efetivo) não pode ser ANTERIOR à coluna 4 (data de término programado);
        posterior pode.
    Um grupo que já está gravado e não foi alterado não é revalidado ('gravado' = linha como está no banco).
    Retorna [(campo, mensagem)]."""
    def valor(chave):
        return str(item.get(chave) or "").strip()

    def inalterado(chaves):
        return gravado is not None and all(str(gravado.get(c) or "").strip() == valor(c) for c in chaves)

    def dia(texto):
        normal = doc_lib_normalizar_data(texto)
        return datetime.strptime(normal, "%d/%m/%Y") if normal else None

    erros = []
    prog, real = dia(valor("prev_data_inicio")), dia(valor("real_data_inicio"))
    if prog and real and real != prog and not inalterado(DOC_LIB_CAMPOS_INICIO):
        erros.append(("real_data_inicio",
                      f"a data de início efetivo (coluna 6) deve ser igual à data de início programado "
                      f"(coluna 2: {valor('prev_data_inicio')})."))
    prog, real = dia(valor("prev_data_termino")), dia(valor("real_data_termino"))
    if prog and real and real < prog and not inalterado(DOC_LIB_CAMPOS_TERMINO):
        erros.append(("real_data_termino",
                      f"a data de término efetivo (coluna 10) não pode ser anterior à data de término programado "
                      f"(coluna 4: {valor('prev_data_termino')}); posterior pode."))
    return erros


def doc_lib_diferencas_bloqueadas(atual, dados, emitido=True):
    """Lista o que, nos dados recebidos, difere do gravado e NÃO pode ser alterado.

    ATEIE já EMITIDO (documento gerado): dados gerais, Pessoal Notificado e colunas 1 a 5 de cada ATEIE ficam
    protegidos. O "De acordo" só recebe linhas novas (as já registradas não mudam). As colunas 6 a 13 só podem ser
    alteradas depois que o "De acordo" já estiver preenchido e salvo e, quando as quatro colunas de início efetivo
    (6 a 9) ou as quatro de término efetivo (10 a 13) já estão preenchidas e salvas, esse grupo não muda mais.
    ATEIE ainda NÃO emitido: as colunas 6 a 13 (execução) não podem ser informadas antes da geração do documento.
    Lista vazia = nada protegido foi alterado."""
    def texto(valor):
        return str(valor or "").strip()

    gravadas = {item["ordem"]: item for item in atual.get("intervencoes") or []}
    diferencas = []

    if not emitido:
        for item in sorted(dados.get("intervencoes") or [], key=lambda i: i["ordem"]):
            gravada = gravadas.get(item["ordem"], {})
            if any(texto(gravada.get(chave)) != texto(item.get(chave)) for chave in DOC_LIB_CAMPOS_EXECUCAO):
                diferencas.append(f"Linha {item['ordem']}: as colunas 6 a 13 só podem ser informadas depois que o "
                                  f"documento for gerado")
        return diferencas

    for chave, nome in (("classificacao", "Classificação dos Trabalhos"), ("equipamento", "Equipamento de Interligação"),
                        ("empresa", "Empresa Solicitante"), ("empresa_outra", "Empresa Solicitante (OUTRA)"),
                        ("local", "Local"), ("servicos", "Serviços a Executar"), ("observacoes", "Observações"),
                        ("documentos_vinculados", "Documentos Internos Vinculados"), ("nota", "Nota")):
        # Equipamento, Empresa e Local são sempre apresentados em caixa alta: documentos gravados antes dessa regra
        # podem estar em maiúsculas e minúsculas, e mudar só a caixa não conta como alteração
        comparar = str.upper if chave in DOC_LIB_CAMPOS_CAIXA_ALTA else str
        if comparar(texto(atual.get(chave))) != comparar(texto(dados.get(chave))):
            diferencas.append(nome)

    def linhas_nao_vazias(linhas, chaves):
        return [{chave: texto(linha.get(chave)) for chave in chaves} for linha in linhas
                if any(texto(linha.get(chave)) for chave in chaves)]

    fixas = linhas_nao_vazias(atual.get("notificacoes") or [], ("nome", "data", "hora"))
    novas = linhas_nao_vazias(dados.get("notificacoes") or [], ("nome", "data", "hora"))
    if novas[:len(fixas)] != fixas:
        diferencas.append("De acordo (as linhas já registradas não podem ser alteradas)")
    elif len(novas) > DOC_LIB_LIMITE_NOTIFICACOES or not all(all(linha.values()) for linha in novas[len(fixas):]):
        diferencas.append(f"De acordo (cada linha nova precisa de nome, data e hora, no máximo "
                          f"{DOC_LIB_LIMITE_NOTIFICACOES} linhas)")
    de_acordo_gravado = doc_lib_de_acordo_completo(atual.get("notificacoes"))
    chaves_pessoal = ("nome", "empresa", "empresa_outra", "setor", "data", "hora")
    if linhas_nao_vazias(atual.get("pessoal") or [], chaves_pessoal) \
            != linhas_nao_vazias(dados.get("pessoal") or [], chaves_pessoal):
        diferencas.append("Pessoal Notificado")

    for item in sorted(dados.get("intervencoes") or [], key=lambda i: i["ordem"]):
        ordem = item["ordem"]
        gravada = gravadas.get(ordem)
        if gravada is None:
            if any(texto(item.get(chave)) for chave, _, _, _ in DOC_LIB_COLUNAS_INTERVENCAO):
                diferencas.append(f"Linha {ordem}: não é possível incluir novos ATEIE depois da emissão")
            continue
        if any(texto(gravada.get(chave)) != texto(item.get(chave)) for chave in DOC_LIB_CAMPOS_PROGRAMADOS):
            diferencas.append(f"Linha {ordem} ({gravada['numero']}): colunas 1 a 5 (número e programação)")
        if gravada.get("status") == STATUS_ATEIE_CANCELADO:
            continue
        if not de_acordo_gravado and any(texto(gravada.get(chave)) != texto(item.get(chave))
                                         for chave in DOC_LIB_CAMPOS_EXECUCAO):
            diferencas.append(f"Linha {ordem} ({gravada['numero']}): as colunas 6 a 13 só podem ser informadas "
                              f"depois que o De acordo estiver preenchido e salvo")
        for chaves, colunas, nome in ((DOC_LIB_CAMPOS_INICIO, "6 a 9", "início efetivo"),
                                      (DOC_LIB_CAMPOS_TERMINO, "10 a 13", "término efetivo")):
            if all(texto(gravada.get(chave)) for chave in chaves) \
                    and any(texto(gravada.get(chave)) != texto(item.get(chave)) for chave in chaves):
                diferencas.append(f"Linha {ordem} ({gravada['numero']}): colunas {colunas} ({nome} já salvo)")
    return diferencas


def doc_lib_salvar_ateie(dados, usuario):
    """Grava o ATEIE (novo ou já existente) em uma única transação e devolve o id.

    - ATEIE novo com os 4 campos programados preenchidos: recebe aqui o próximo número do ano
      (linhas incompletas ou vazias NÃO consomem número) e entra com o status "Em análise".
    - ATEIE já numerado: mantém o número; só os dados são atualizados.
    - ATEIE cancelado: não é alterado.
    - Documento já EMITIDO (gerado): dados gerais, De acordo, Pessoal Notificado e colunas 1 a 5 ficam
      protegidos, e o grupo de início (6 a 9) ou de término (10 a 13) já preenchido e salvo não muda mais
      (DocLibBloqueado se houver tentativa); só o restante das colunas 6 a 13 é gravado.
    - Depois da emissão o "De acordo" só recebe linhas novas, e as colunas 6 a 13 só são aceitas depois que o
      "De acordo" estiver preenchido e salvo (DocLibBloqueado).
    - Antes da emissão as colunas 6 a 13 não podem ser informadas (DocLibBloqueado).
    - Datas da execução: coluna 6 igual à coluna 2; coluna 10 não anterior à coluna 4 (DocLibRegra).
    - O status de cada ATEIE é recalculado a cada gravação (doc_lib_calcular_status).
    - Lança DocLibConflito se outra pessoa salvou o documento depois que ele foi aberto."""
    dados = doc_lib_normalizar_ateie(dados)
    agora = datetime.now()
    agora_texto = agora.strftime("%d/%m/%Y - %H:%Mh")
    conexao = doc_lib_conectar(manual=True)
    cursor = conexao.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        ateie_id = dados.get("id")
        emitido = False
        atual = None
        campos_gerais = (dados["classificacao"], dados["equipamento"], dados["empresa"], dados["empresa_outra"],
                         dados["local"], dados["servicos"], dados["observacoes"], dados["documentos_vinculados"],
                         dados["nota"])

        if ateie_id is not None:
            atual = _doc_lib_ler_ateie(conexao, ateie_id)
            if atual is None or atual["revisao"] != dados.get("revisao"):
                raise DocLibConflito("Este ATEIE foi alterado por outro usuário depois de aberto nesta janela.\n\n"
                                     "Feche-o e abra-o novamente (Abrir ATEIE salvo) para ver a versão atual.")
            emitido = bool(atual["emitido"])
        bloqueadas = doc_lib_diferencas_bloqueadas(atual or {}, dados, emitido)
        if bloqueadas:
            if emitido:
                cabecalho = ("Este ATEIE já foi emitido (documento gerado). Só podem ser alterados: o De acordo "
                             "(novas linhas) e as colunas 6 a 13 da tabela de intervenções (depois que o De acordo "
                             "estiver preenchido e salvo); o início efetivo (6 a 9) ou o término efetivo (10 a 13) "
                             "já salvo não muda mais.")
            else:
                cabecalho = "Dados de execução não são aceitos antes da geração do documento."
            raise DocLibBloqueado(cabecalho + "\n\nAlterações recusadas: " + "; ".join(bloqueadas) + ".")
        gravadas = {item["ordem"]: item for item in (atual or {}).get("intervencoes") or []}
        violacoes = [f"Linha {item['ordem']}: {mensagem}" for item in dados["intervencoes"]
                     if gravadas.get(item["ordem"], {}).get("status") != STATUS_ATEIE_CANCELADO
                     for _, mensagem in doc_lib_erros_datas_execucao(item, gravadas.get(item["ordem"]))]
        if violacoes:
            raise DocLibRegra("Dados de execução recusados:\n\n" + "\n".join(violacoes))

        if ateie_id is None:
            cursor.execute(
                "INSERT INTO doclib_ateie (classificacao, equipamento, empresa, empresa_outra, local_servico, "
                "servicos, observacoes, documentos_vinculados, nota, solicitado_por, solicitado_por_usuario, "
                "data_preenchimento, hora_preenchimento, revisao, emitido, criado_em, atualizado_por, "
                "atualizado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, ?, ?, ?)",
                campos_gerais + (dados["solicitado_por"], dados.get("solicitado_por_usuario") or dados["solicitado_por"],
                                 dados["data_preenchimento"], dados["hora_preenchimento"], agora_texto, usuario,
                                 agora_texto))
            ateie_id = cursor.lastrowid
        else:
            if emitido:
                cursor.execute("UPDATE doclib_ateie SET revisao = revisao + 1, atualizado_por = ?, "
                               "atualizado_em = ? WHERE id = ?", (usuario, agora_texto, ateie_id))
            else:
                cursor.execute(
                    "UPDATE doclib_ateie SET classificacao = ?, equipamento = ?, empresa = ?, empresa_outra = ?, "
                    "local_servico = ?, servicos = ?, observacoes = ?, documentos_vinculados = ?, nota = ?, "
                    "revisao = revisao + 1, atualizado_por = ?, atualizado_em = ? WHERE id = ?",
                    campos_gerais + (usuario, agora_texto, ateie_id))
                cursor.execute("DELETE FROM doclib_ateie_notificacoes WHERE ateie_id = ?", (ateie_id,))
                cursor.execute("DELETE FROM doclib_ateie_pessoal WHERE ateie_id = ?", (ateie_id,))

        if emitido:
            # depois da emissão o "De acordo" só ganha linhas novas (as já gravadas foram verificadas acima)
            gravadas_de_acordo = len(atual["notificacoes"])
            novas = [linha for linha in dados["notificacoes"]
                     if any(str(linha.get(chave) or "").strip() for chave in ("nome", "data", "hora"))]
            for ordem, linha in enumerate(novas[gravadas_de_acordo:], start=gravadas_de_acordo + 1):
                cursor.execute("INSERT INTO doclib_ateie_notificacoes (ateie_id, ordem, nome, data, hora) "
                               "VALUES (?, ?, ?, ?, ?)", (ateie_id, ordem, linha["nome"], linha["data"], linha["hora"]))
        else:
            # "De acordo" é opcional: só são gravadas as linhas com algum conteúdo
            ordem = 0
            for linha in dados["notificacoes"]:
                if not any(str(linha.get(chave) or "").strip() for chave in ("nome", "data", "hora")):
                    continue
                ordem += 1
                cursor.execute("INSERT INTO doclib_ateie_notificacoes (ateie_id, ordem, nome, data, hora) "
                               "VALUES (?, ?, ?, ?, ?)", (ateie_id, ordem, linha["nome"], linha["data"], linha["hora"]))
            for ordem, linha in enumerate(dados["pessoal"], start=1):
                cursor.execute("INSERT INTO doclib_ateie_pessoal (ateie_id, ordem, nome, empresa, empresa_outra, "
                               "setor, data, hora) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                               (ateie_id, ordem, linha["nome"], linha["empresa"], linha.get("empresa_outra") or "",
                                linha["setor"], linha["data"], linha["hora"]))

        cursor.execute("SELECT ordem, status FROM doclib_ateie_intervencoes WHERE ateie_id = ?", (ateie_id,))
        existentes = dict(cursor.fetchall())
        nomes_colunas = [chave for chave, _, _, _ in DOC_LIB_COLUNAS_INTERVENCAO]

        for item in sorted(dados["intervencoes"], key=lambda i: i["ordem"]):
            ordem = item["ordem"]
            if ordem in existentes:
                if existentes[ordem] == STATUS_ATEIE_CANCELADO:
                    continue
                gravar = list(DOC_LIB_CAMPOS_EXECUCAO) if emitido else nomes_colunas   # depois de emitido: só 6 a 13
                cursor.execute(f"UPDATE doclib_ateie_intervencoes SET {', '.join(f'{chave} = ?' for chave in gravar)} "
                               f"WHERE ateie_id = ? AND ordem = ?",
                               [item.get(chave, "") for chave in gravar] + [ateie_id, ordem])
            elif not emitido and all(item.get(chave) for chave in DOC_LIB_CAMPOS_PROGRAMADOS):
                sequencia = _doc_lib_consumir_numero(cursor, "ATEIE", agora.year)
                cursor.execute(
                    f"INSERT INTO doclib_ateie_intervencoes (ateie_id, ordem, numero, ano, sequencia, "
                    f"{', '.join(nomes_colunas)}, status) VALUES (?, ?, ?, ?, ?, {', '.join('?' * len(nomes_colunas))}, ?)",
                    [ateie_id, ordem, doc_lib_formatar_numero(sequencia, agora.year), agora.year, sequencia]
                    + [item.get(chave, "") for chave in nomes_colunas] + [STATUS_ATEIE_EM_ANALISE])

        _doc_lib_recalcular_status(cursor, ateie_id, emitido)
        cursor.execute("COMMIT")
        return ateie_id
    except Exception:
        if conexao.in_transaction:
            cursor.execute("ROLLBACK")
        raise
    finally:
        conexao.close()


def _doc_lib_ler_ateie(conexao, ateie_id):
    """Lê o ATEIE completo (dados gerais, notificações, pessoal e intervenções) usando a conexão informada."""
    cursor = conexao.cursor()
    cursor.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM doclib_ateie WHERE id = ?", (ateie_id,))
    cabecalho = cursor.fetchone()
    if cabecalho is None:
        return None
    doc = dict(cabecalho)
    doc["local"] = doc.pop("local_servico")
    cursor.execute("SELECT nome, data, hora FROM doclib_ateie_notificacoes WHERE ateie_id = ? ORDER BY ordem",
                   (ateie_id,))
    doc["notificacoes"] = [dict(linha) for linha in cursor.fetchall()]
    cursor.execute("SELECT nome, empresa, empresa_outra, setor, data, hora FROM doclib_ateie_pessoal "
                   "WHERE ateie_id = ? ORDER BY ordem", (ateie_id,))
    doc["pessoal"] = [dict(linha) for linha in cursor.fetchall()]
    cursor.execute("SELECT * FROM doclib_ateie_intervencoes WHERE ateie_id = ? ORDER BY ordem", (ateie_id,))
    doc["intervencoes"] = [dict(linha) for linha in cursor.fetchall()]
    return doc


def doc_lib_carregar_ateie(ateie_id):
    """Devolve o ATEIE completo (dados gerais, notificações, pessoal e intervenções) ou None."""
    conexao = doc_lib_conectar()
    try:
        return _doc_lib_ler_ateie(conexao, ateie_id)
    finally:
        conexao.close()


def doc_lib_listar_ateie():
    """Um registro por ATEIE (cada intervenção numerada), do mais recente para o mais antigo. Mesmo que
    vários ATEIE tenham empresa, equipamento, local e serviços iguais, cada um aparece individualmente."""
    conexao = doc_lib_conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "SELECT i.ateie_id, i.ordem, i.numero, i.ano, i.sequencia, i.status, a.equipamento, a.empresa, "
            "a.empresa_outra, a.local_servico, a.servicos, a.solicitado_por, i.prev_data_inicio, "
            "i.prev_hora_inicio, i.prev_data_termino, i.prev_hora_termino FROM doclib_ateie_intervencoes i "
            "JOIN doclib_ateie a ON a.id = i.ateie_id ORDER BY i.ano DESC, i.sequencia DESC")
        resultado = []
        for (ateie_id, ordem, numero, ano, sequencia, status, equipamento, empresa, empresa_outra, local,
             servicos, solicitado_por, data_inicio, hora_inicio, data_termino, hora_termino) in cursor.fetchall():
            resultado.append({
                "ateie_id": ateie_id, "ordem": ordem, "numero": numero, "ano": ano, "sequencia": sequencia,
                "status": status, "equipamento": equipamento or "",
                "empresa": empresa_outra if empresa == "OUTRA" and empresa_outra else empresa,
                "solicitante": solicitado_por, "prog_inicio": f"{data_inicio} {hora_inicio}",
                "prog_termino": f"{data_termino} {hora_termino}", "local": local or "", "servicos": servicos or "",
            })
        return resultado
    finally:
        conexao.close()


def doc_lib_cancelar_intervencao(ateie_id, ordem, usuario, justificativa, revisao_esperada):
    """Cancela SOMENTE o ATEIE (intervenção) indicado: os demais ATEIE do mesmo documento continuam com o
    status que tinham. O número cancelado fica registrado e nunca é reaproveitado. Só é possível cancelar um
    ATEIE "Em análise", "Aguarda De Acordo" ou "Aprovado para Execução": em execução ele somente pode ser concluído, e concluído ou já cancelado
    não cancela (ValueError). Devolve a nova revisão do documento."""
    agora_texto = datetime.now().strftime("%d/%m/%Y - %H:%Mh")
    conexao = doc_lib_conectar(manual=True)
    cursor = conexao.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT revisao FROM doclib_ateie WHERE id = ?", (ateie_id,))
        linha = cursor.fetchone()
        if linha is None or linha[0] != revisao_esperada:
            raise DocLibConflito("Este ATEIE foi alterado por outro usuário depois de aberto nesta janela.\n\n"
                                 "Feche-o e abra-o novamente (Abrir ATEIE salvo) para ver a versão atual.")
        cursor.execute("SELECT status FROM doclib_ateie_intervencoes WHERE ateie_id = ? AND ordem = ?",
                       (ateie_id, ordem))
        linha = cursor.fetchone()
        if linha is None:
            raise ValueError("ATEIE não encontrado.")
        if linha[0] == STATUS_ATEIE_CANCELADO:
            raise ValueError("Este ATEIE já está cancelado.")
        if linha[0] not in DOC_LIB_STATUS_CANCELAVEIS:
            raise ValueError(f"Um ATEIE com status '{linha[0]}' não pode ser cancelado.")
        cursor.execute("UPDATE doclib_ateie_intervencoes SET status = ?, cancelada_por = ?, data_cancelamento = ?, "
                       "justificativa_cancelamento = ? WHERE ateie_id = ? AND ordem = ?",
                       (STATUS_ATEIE_CANCELADO, usuario, agora_texto, justificativa, ateie_id, ordem))
        cursor.execute("UPDATE doclib_ateie SET revisao = revisao + 1, atualizado_por = ?, atualizado_em = ? "
                       "WHERE id = ?", (usuario, agora_texto, ateie_id))
        cursor.execute("SELECT revisao FROM doclib_ateie WHERE id = ?", (ateie_id,))
        nova_revisao = cursor.fetchone()[0]
        cursor.execute("COMMIT")
        return nova_revisao
    except Exception:
        if conexao.in_transaction:
            cursor.execute("ROLLBACK")
        raise
    finally:
        conexao.close()


# ---------------------------------------------------
# NORMALIZAÇÃO E VALIDAÇÃO DO ATEIE
# ---------------------------------------------------
def doc_lib_normalizar_ateie(dados):
    """Devolve uma cópia dos dados com datas e horas válidas já no padrão de cada campo
    (tabela: dd/mm/aa; demais campos: dd/mm/aaaa; horas: HH:MM). Valores inválidos ficam
    como foram digitados (a validação os aponta)."""
    def data_hora(linha, ano_curto):
        linha = dict(linha)
        if "data" in linha:
            linha["data"] = doc_lib_normalizar_data(linha["data"], ano_curto) or linha["data"]
        if "hora" in linha:
            linha["hora"] = doc_lib_normalizar_hora(linha["hora"]) or linha["hora"]
        return linha

    novo = dict(dados)
    novo["notificacoes"] = [data_hora(linha, False) for linha in dados.get("notificacoes", [])]
    novo["pessoal"] = []
    for linha in dados.get("pessoal", []):
        linha = data_hora(linha, False)
        if linha.get("empresa") != "OUTRA":
            linha["empresa_outra"] = ""
        novo["pessoal"].append(linha)
    intervencoes = []
    for item in dados.get("intervencoes", []):
        item = dict(item)
        for chave, _, _, tipo in DOC_LIB_COLUNAS_INTERVENCAO:
            valor = item.get(chave) or ""
            if tipo == "data":
                valor = doc_lib_normalizar_data(valor, True) or valor
            elif tipo == "hora":
                valor = doc_lib_normalizar_hora(valor) or valor
            item[chave] = valor
        intervencoes.append(item)
    novo["intervencoes"] = intervencoes
    return novo


def doc_lib_validar_ateie(dados, atual=None):
    """Valida o ATEIE (antes de salvar e antes de gerar o documento). 'atual' é o documento como está gravado
    (quando já existe): execução já gravada e inalterada não é revalidada nas regras de data.

    Retorna uma lista de (chaves_dos_campos, mensagem); lista vazia = documento válido.
    Opcionais: De acordo, Documentos Internos Vinculados e Nota. Observações é obrigatório (documento ainda não
    emitido). Na tabela de intervenções são
    obrigatórios os 4 campos programados de cada intervenção usada (pelo menos uma); as colunas
    de execução (Verificado) são preenchidas à medida que o serviço acontece e, se informadas,
    precisam estar corretas."""
    erros = []

    def vazio(valor):
        return not str(valor or "").strip()

    if vazio(dados.get("classificacao")):
        erros.append((("classificacao",), "Classificação dos Trabalhos: selecione Programado ou Urgência."))
    if vazio(dados.get("equipamento")):
        erros.append((("equipamento",), "Equipamento de Interligação: preencha o campo."))
    if vazio(dados.get("empresa")):
        erros.append((("empresa",), "Empresa Solicitante: selecione a empresa."))
    elif dados.get("empresa") == "OUTRA" and vazio(dados.get("empresa_outra")):
        erros.append((("empresa_outra",), "Empresa Solicitante (OUTRA): informe o nome da empresa."))
    if vazio(dados.get("local")):
        erros.append((("local",), "Local: preencha o campo."))
    if vazio(dados.get("servicos")):
        erros.append((("servicos",), "Serviços a Executar: preencha o campo."))
    if vazio(dados.get("observacoes")) and not (atual or {}).get("emitido"):     # documento emitido não muda mais
        erros.append((("observacoes",), "Observações: preencha o campo."))
    if vazio(dados.get("solicitado_por")) or vazio(dados.get("data_preenchimento")) \
            or vazio(dados.get("hora_preenchimento")):
        erros.append((("solicitado_por",), "Solicitado por: usuário, data ou hora não identificados "
                                           "(faça login novamente)."))

    def validar_linhas(linhas, colunas, prefixo, titulo, opcional=False):
        """opcional=True: linha totalmente em branco é ignorada; linha parcialmente preenchida precisa ser
        completada (ou removida)."""
        if not linhas and not opcional:
            erros.append(((f"{prefixo}:1:nome",), f"{titulo}: informe ao menos uma linha."))
        for numero_linha, linha in enumerate(linhas, start=1):
            if opcional and all(vazio(linha.get(chave)) for chave, _, _ in colunas):
                continue
            faltando = [(chave, rotulo) for chave, rotulo, _ in colunas if vazio(linha.get(chave))]
            if faltando:
                erros.append((tuple(f"{prefixo}:{numero_linha}:{chave}" for chave, _ in faltando),
                              f"{titulo}, linha {numero_linha}: preencha "
                              + ", ".join(rotulo for _, rotulo in faltando) + "."))
            for chave, rotulo, tipo in colunas:
                valor = linha.get(chave)
                if vazio(valor):
                    continue
                if tipo == "data" and not doc_lib_normalizar_data(valor):
                    erros.append(((f"{prefixo}:{numero_linha}:{chave}",),
                                  f"{titulo}, linha {numero_linha}: Data inválida (use DD/MM/AAAA)."))
                if tipo == "hora" and not doc_lib_normalizar_hora(valor):
                    erros.append(((f"{prefixo}:{numero_linha}:{chave}",),
                                  f"{titulo}, linha {numero_linha}: Hora inválida (use HH:MM)."))
                if tipo == "empresa" and valor == "OUTRA" and vazio(linha.get(chave + "_outra")):
                    erros.append(((f"{prefixo}:{numero_linha}:{chave}_outra",),
                                  f"{titulo}, linha {numero_linha}: informe o nome da empresa (OUTRA)."))

    validar_linhas(dados.get("notificacoes") or [], DOC_LIB_COLUNAS_NOTIFICACAO, "notif",
                   "De acordo (Pessoas/Áreas notificadas)", opcional=True)
    validar_linhas(dados.get("pessoal") or [], DOC_LIB_COLUNAS_PESSOAL, "pessoal", "Pessoal Notificado")

    # Tabela de intervenções
    gravadas = {item["ordem"]: item for item in (atual or {}).get("intervencoes") or []}
    intervencoes_usadas = 0
    for item in dados.get("intervencoes") or []:
        if item.get("status") == STATUS_ATEIE_CANCELADO:
            intervencoes_usadas += 1
            continue
        ordem = item["ordem"]
        valores = {chave: str(item.get(chave) or "").strip() for chave, _, _, _ in DOC_LIB_COLUNAS_INTERVENCAO}
        numero = item.get("numero")
        if not numero and not any(valores.values()):
            continue                                         # linha não utilizada
        intervencoes_usadas += 1
        titulo = f"Intervenção da linha {ordem}" + (f" (Nº {numero})" if numero else "")

        faltando = [chave for chave in DOC_LIB_CAMPOS_PROGRAMADOS if not valores[chave]]
        if faltando:
            dica = ("; para retirar a intervenção use o botão Cancelar" if numero else "")
            erros.append((tuple(f"interv:{ordem}:{chave}" for chave in faltando),
                          f"{titulo}: preencha " + ", ".join(_DOC_LIB_DESCRICAO_CAMPO[c] for c in faltando)
                          + dica + "."))

        for chave, _, descricao, tipo in DOC_LIB_COLUNAS_INTERVENCAO:
            valor = valores[chave]
            if not valor:
                continue
            if tipo == "data" and not doc_lib_normalizar_data(valor):
                erros.append(((f"interv:{ordem}:{chave}",), f"{titulo}: {descricao} inválida (use DD/MM/AA)."))
            if tipo == "hora" and not doc_lib_normalizar_hora(valor):
                erros.append(((f"interv:{ordem}:{chave}",), f"{titulo}: {descricao} inválida (use HH:MM)."))

        inicio = _doc_lib_data_hora(valores["prev_data_inicio"], valores["prev_hora_inicio"])
        termino = _doc_lib_data_hora(valores["prev_data_termino"], valores["prev_hora_termino"])
        if inicio and termino and termino < inicio:
            erros.append(((f"interv:{ordem}:prev_data_termino", f"interv:{ordem}:prev_hora_termino"),
                          f"{titulo}: o término programado não pode ser anterior ao início programado."))

        for chave_data, chave_hora, nome in (("real_data_inicio", "real_hora_inicio", "início efetivo"),
                                             ("real_data_termino", "real_hora_termino", "término efetivo")):
            if bool(valores[chave_data]) != bool(valores[chave_hora]):
                ausente = chave_hora if valores[chave_data] else chave_data
                erros.append(((f"interv:{ordem}:{ausente}",),
                              f"{titulo}: preencha também {_DOC_LIB_DESCRICAO_CAMPO[ausente]} "
                              f"(data e hora do {nome} andam juntas)."))
        for campo, mensagem in doc_lib_erros_datas_execucao(valores, gravadas.get(ordem)):
            erros.append(((f"interv:{ordem}:{campo}",), f"{titulo}: {mensagem}"))

        inicio_real = _doc_lib_data_hora(valores["real_data_inicio"], valores["real_hora_inicio"])
        termino_real = _doc_lib_data_hora(valores["real_data_termino"], valores["real_hora_termino"])
        if inicio_real and termino_real and termino_real < inicio_real:
            erros.append(((f"interv:{ordem}:real_data_termino", f"interv:{ordem}:real_hora_termino"),
                          f"{titulo}: o término efetivo não pode ser anterior ao início efetivo."))

    if intervencoes_usadas == 0:
        erros.append((tuple(f"interv:1:{chave}" for chave in DOC_LIB_CAMPOS_PROGRAMADOS),
                      "Tabela de intervenções: informe ao menos uma intervenção (data e hora de início e "
                      "de término programados)."))
    return erros


# ---------------------------------------------------
# GERAÇÃO DO DOCUMENTO ATEIE EM PDF
# ---------------------------------------------------
def doc_lib_quebrar_linhas(pdf, largura, altura_linha, texto):
    """Linhas em que o texto será quebrado na largura dada (sem desenhar nada). Funciona nas versões
    novas do fpdf2 (dry_run/output) e nas anteriores (split_only)."""
    try:
        return pdf.multi_cell(largura, altura_linha, texto, dry_run=True, output="LINES")
    except TypeError:
        return pdf.multi_cell(largura, altura_linha, texto, split_only=True)


class PDFAteie(FPDF):
    """Folha A4 do ATEIE (cabeçalho com logotipo e título, réguas superior e inferior e rodapé)."""
    X0 = 20.0                  # margem esquerda do formulário (igual ao documento de referência)
    X1 = 200.0
    Y_REGUA_TOPO = 12.2
    Y_REGUA_TITULO = 29.3
    Y_CONTEUDO = 30.0
    Y_REGUA_BASE = 282.0
    Y_MAXIMO = 280.0           # limite inferior do conteúdo

    def __init__(self, rodape_texto=""):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.rodape_texto = rodape_texto
        self.set_auto_page_break(False)
        self.alias_nb_pages()
        for estilo, arquivo in (("", "DejaVuSansCondensed.ttf"), ("B", "DejaVuSansCondensed-Bold.ttf"),
                                ("I", "DejaVuSansCondensed-Oblique.ttf"),
                                ("BI", "DejaVuSansCondensed-BoldOblique.ttf")):
            self.add_font("DejaVuC", estilo, os.path.join(PASTA_BASE, arquivo))

    def header(self):
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.8)
        self.line(self.X0, self.Y_REGUA_TOPO, self.X1, self.Y_REGUA_TOPO)
        if os.path.exists(LOGO_ATEIE):
            self.image(LOGO_ATEIE, x=27.0, y=13.4, w=30.5)
        self.set_font("DejaVuC", "B", 11)
        self.set_text_color(0, 0, 0)
        self.set_xy(48.0, 16.8)
        self.multi_cell(152.0, 5.2, "AUTORIZAÇÃO PARA TRABALHOS EM EQUIPAMENTOS DE\n"
                                    "INTERLIGAÇÃO ENERGIZADOS – ATEIE", align="C")
        self.line(self.X0, self.Y_REGUA_TITULO, self.X1, self.Y_REGUA_TITULO)
        self.set_line_width(0.2)

    def footer(self):
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.8)
        self.line(self.X0, self.Y_REGUA_BASE, self.X1, self.Y_REGUA_BASE)
        self.set_line_width(0.2)
        self.set_font("DejaVuC", "", 6.5)
        self.set_text_color(110, 110, 110)
        self.set_xy(self.X0, self.Y_REGUA_BASE + 1.2)
        self.cell(self.X1 - self.X0, 3.5, f"{self.rodape_texto}   |   Página {self.page_no()}/{{nb}}", align="R")
        self.set_text_color(0, 0, 0)


def doc_lib_gerar_pdf_ateie(doc, caminho, gerado_por=""):
    """Gera o PDF do ATEIE (layout do documento de referência) em 'caminho'."""
    agora = datetime.now()
    pdf = PDFAteie(f"Gerado pelo sistema COG-Alupar em {agora.strftime('%d/%m/%Y às %H:%M')} por {gerado_por}")
    pdf.add_page()
    X0, X1 = PDFAteie.X0, PDFAteie.X1
    LARGURA = X1 - X0
    estado = {"y": PDFAteie.Y_CONTEUDO}

    def nova_pagina():
        pdf.add_page()
        estado["y"] = PDFAteie.Y_CONTEUDO

    def garantir(altura):
        """Abre nova página se não houver 'altura' mm livres na atual."""
        if estado["y"] + altura > PDFAteie.Y_MAXIMO:
            nova_pagina()

    def regua(y, x_ini=X0, x_fim=X1, espessura=0.2):
        pdf.set_line_width(espessura)
        pdf.line(x_ini, y, x_fim, y)

    def largura_texto(texto, estilo, tamanho):
        pdf.set_font("DejaVuC", estilo, tamanho)
        return pdf.get_string_width(texto)

    def rotulo(x, y_base, numero, texto, tamanho=9.0):
        """Rótulo do campo: número pequeno e rebaixado (subescrito) + texto em itálico. Devolve o x final."""
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVuC", "I", tamanho * 0.62)
        pdf.text(x, y_base + 0.8, f"{numero}.")
        x += pdf.get_string_width(f"{numero}.") + 0.1
        pdf.set_font("DejaVuC", "I", tamanho)
        pdf.text(x, y_base, texto)
        return x + pdf.get_string_width(texto)

    def valor_ajustado(x, y_base, texto, largura, tamanho=9.5, minimo=6.0, estilo=""):
        """Valor em uma linha: reduz a fonte até caber e, no limite, abrevia com reticências."""
        texto = " ".join(str(texto or "").split())
        tam = tamanho
        pdf.set_font("DejaVuC", estilo, tam)
        while tam > minimo and pdf.get_string_width(texto) > largura:
            tam -= 0.5
            pdf.set_font("DejaVuC", estilo, tam)
        while len(texto) > 1 and pdf.get_string_width(texto) > largura:
            texto = texto[:-2] + "…"
        pdf.set_text_color(0, 0, 0)
        pdf.text(x, y_base, texto)

    def ajustar_celula(texto, largura):
        """Maior fonte (de 7 a 5,5) em que o texto cabe em uma linha da célula; se nem assim couber,
        usa 5,5 e quebra em várias linhas. Retorna (tamanho, linhas)."""
        texto = " ".join(str(texto).split())
        for tamanho in (7.0, 6.5, 6.0, 5.5):
            pdf.set_font("DejaVuC", "", tamanho)
            if pdf.get_string_width(texto) <= largura:
                return tamanho, [texto]
        return 5.5, doc_lib_quebrar_linhas(pdf, largura, 2.5, texto)

    def campo_texto(numero, nome, valor):
        """Linha do formulário com rótulo à esquerda e o valor ao lado (quebrando em várias linhas,
        inclusive entre páginas, se necessário), terminada por uma régua."""
        valor = (valor or "").strip()
        x_rotulo_fim = X0 + 1.0 + largura_texto(f"{numero}.", "I", 9.0 * 0.62) + largura_texto(nome, "I", 9.0) + 0.1
        x_valor = x_rotulo_fim + 2.0
        pdf.set_font("DejaVuC", "", 9.5)
        linhas = doc_lib_quebrar_linhas(pdf, X1 - x_valor - 1.5, 4.3, valor) if valor else [""]
        altura_total = max(10.3, 4.4 + (len(linhas) - 1) * 4.3 + 5.6)
        # mantém rótulo e texto juntos; só divide entre páginas se o campo não couber em uma página inteira
        garantir(altura_total if altura_total <= PDFAteie.Y_MAXIMO - PDFAteie.Y_CONTEUDO else 10.3)
        y_topo = estado["y"]
        rotulo(X0 + 1.0, y_topo + 4.4, numero, nome)
        pdf.set_font("DejaVuC", "", 9.5)
        pdf.set_text_color(0, 0, 0)
        y_base = y_topo + 4.4
        for linha in linhas:
            if y_base + 3.6 > PDFAteie.Y_MAXIMO:        # texto maior que o espaço restante: continua na página seguinte
                nova_pagina()
                y_topo = estado["y"]
                y_base = y_topo + 4.4
                pdf.set_font("DejaVuC", "", 9.5)
                pdf.set_text_color(0, 0, 0)
            pdf.text(x_valor, y_base, linha)
            y_base += 4.3
        estado["y"] = max(y_topo + 10.3, y_base - 4.3 + 5.6)
        regua(estado["y"])

    # ---- 1. Classificação dos Trabalhos --------------------------------------------------------
    y_topo = estado["y"]
    rotulo(X0 + 1.0, y_topo + 4.4, "1", "Classificação dos Trabalhos:")
    for texto, x_texto in (("Programado", 125.8), ("Urgência", 168.6)):
        marcado = doc.get("classificacao") == texto
        pdf.set_font("DejaVuC", "", 9.5)
        pdf.set_text_color(0, 0, 0)
        pdf.text(x_texto, y_topo + 4.4, texto)
        x_caixa = x_texto + pdf.get_string_width(texto) + 3.0
        pdf.set_font("DejaVuC", "B" if marcado else "", 9.5)
        pdf.text(x_caixa, y_topo + 4.4, "[X]" if marcado else "[ ]")
    estado["y"] = y_topo + 10.3
    regua(estado["y"])

    empresa = doc.get("empresa_outra") if doc.get("empresa") == "OUTRA" and doc.get("empresa_outra") \
        else doc.get("empresa")
    # Equipamento de Interligação, Empresa Solicitante e Local saem sempre em caixa alta, como quer que tenham
    # sido digitados
    campo_texto("2", "Equipamento de Interligação:", (doc.get("equipamento") or "").upper())
    campo_texto("3", "Empresa Solicitante:", (empresa or "").upper())
    campo_texto("4", "Local:", (doc.get("local") or "").upper())
    campo_texto("5", "Serviços a Executar:", doc.get("servicos"))
    campo_texto("6", "Observação:", doc.get("observacoes") or DOC_LIB_TEXTO_PADRAO_OBSERVACOES)
    campo_texto("7", "Documentos Internos Vinculados:", doc.get("documentos_vinculados"))

    # ---- 8 a 12: Solicitado por / Data / Hora / Visto Responsável / De Acordo --------------------
    notificacoes = (doc.get("notificacoes") or [])[:DOC_LIB_LIMITE_NOTIFICACOES]
    altura_bloco = 8.3 + 24.3
    garantir(altura_bloco)
    y0 = estado["y"]
    X_VISTO = 167.4
    rotulo(X0 + 1.0, y0 + 5.4, "8", "Solicitado por:")
    valor_ajustado(X0 + 28.0, y0 + 5.4, doc.get("solicitado_por"), 58.0)
    rotulo(88.4, y0 + 5.4, "9", "Data:")
    valor_ajustado(88.4 + 14.0, y0 + 5.4, doc.get("data_preenchimento"), 24.0)
    rotulo(128.6, y0 + 5.4, "10", "Hora:")
    valor_ajustado(128.6 + 14.5, y0 + 5.4, doc.get("hora_preenchimento"), 22.0)
    regua(y0 + 8.3, X0, X_VISTO)
    rotulo(X0 + 1.0, y0 + 12.4, "12", "De Acordo:")
    sequencia_rotulos = [("12.1", "12.2", "12.3"), ("12.4", "12.5", "12.6"), ("12.7", "12.8", "12.9")]
    for indice, (r_nome, r_data, r_hora) in enumerate(sequencia_rotulos):
        y_base = y0 + 18.4 + indice * 6.0
        linha = notificacoes[indice] if indice < len(notificacoes) else {}
        x_fim = rotulo(X0 + 1.0, y_base, r_nome, "Nome:")
        valor_ajustado(x_fim + 1.5, y_base, linha.get("nome"), 88.4 - (x_fim + 1.5) - 1.5)
        x_fim = rotulo(88.4, y_base + 0.6, r_data, "Data:")
        valor_ajustado(x_fim + 1.5, y_base + 0.6, linha.get("data"), 128.6 - (x_fim + 1.5) - 1.5)
        x_fim = rotulo(128.6, y_base + 0.6, r_hora, "Hora:")
        valor_ajustado(x_fim + 1.5, y_base + 0.6, linha.get("hora"), X_VISTO - (x_fim + 1.5) - 1.0)
    # 11. Visto Responsável (espaço para o visto manual)
    pdf.set_line_width(0.2)
    pdf.line(X_VISTO, y0, X_VISTO, y0 + altura_bloco)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("DejaVuC", "I", 9.0 * 0.62)
    pdf.text(X_VISTO + 14.0, y0 + 4.3, "11.")
    pdf.set_font("DejaVuC", "I", 9.0)
    pdf.set_xy(X_VISTO, y0 + 1.5)
    pdf.set_x(X_VISTO + 17.2)
    pdf.cell(10, 4.0, "Visto")
    pdf.set_xy(X_VISTO, y0 + 5.6)
    pdf.cell(X1 - X_VISTO, 4.0, "Responsável:", align="C")
    # user.name (login) do profissional, ao contrário de "Solicitado por", que mostra o nome completo
    visto = " ".join(str(doc.get("solicitado_por_usuario") or "").split())
    if visto:
        tamanho = 9.5
        pdf.set_font("DejaVuC", "B", tamanho)
        while tamanho > 6.0 and pdf.get_string_width(visto) > X1 - X_VISTO - 3.0:
            tamanho -= 0.5
            pdf.set_font("DejaVuC", "B", tamanho)
        pdf.set_xy(X_VISTO, y0 + 14.0)
        pdf.cell(X1 - X_VISTO, 4.5, visto, align="C")
    estado["y"] = y0 + altura_bloco
    regua(estado["y"])

    # ---- 13. Pessoal Notificado --------------------------------------------------------------
    pessoal = (doc.get("pessoal") or [])[:DOC_LIB_LIMITE_PESSOAL]
    garantir(7.2 + 4.4 + 3 * 5.0)
    y0 = estado["y"]
    rotulo(X0 + 1.0, y0 + 4.4, "13", "Pessoal Notificado")
    y_cab = y0 + 7.2
    larguras = [47.6, 36.2, 36.5, 30.0, 29.7]
    xs = [X0]
    for largura in larguras:
        xs.append(xs[-1] + largura)
    regua(y_cab)
    for coluna, (numero, nome) in enumerate((("13.1", "Nome:"), ("13.2", "Empresa:"), ("13.3", "Setor:"),
                                              ("13.4", "Data:"), ("13.5", "Hora:"))):
        rotulo(xs[coluna] + 1.0, y_cab + 3.2, numero, nome)
    altura_linha = 5.0
    y_linha = y_cab + 4.4
    regua(y_linha)
    chaves_pessoal = ("nome", "empresa", "setor", "data", "hora")
    for indice in range(DOC_LIB_LIMITE_PESSOAL):
        linha = pessoal[indice] if indice < len(pessoal) else {}
        for coluna, chave in enumerate(chaves_pessoal):
            valor = linha.get(chave)
            if chave == "empresa" and valor == "OUTRA" and linha.get("empresa_outra"):
                valor = linha["empresa_outra"]
            valor_ajustado(xs[coluna] + 1.0, y_linha + 3.5, valor, larguras[coluna] - 2.0, 9.0, 6.0)
        y_linha += altura_linha
        regua(y_linha)
    for x_vertical in xs[1:-1]:
        pdf.set_line_width(0.2)
        pdf.line(x_vertical, y_cab, x_vertical, y_linha)
    estado["y"] = y_linha

    # ---- 14 a 16. Período dos Serviços ---------------------------------------------------------
    intervencoes = sorted(doc.get("intervencoes") or [], key=lambda item: item["ordem"])
    por_ordem = {item["ordem"]: item for item in intervencoes}
    larg_col = [15.0, 17.5, 12.5, 17.5, 12.5, 12.5, 12.5, 12.5, 15.0, 12.5, 12.5, 12.5, 15.0]
    # larguras (mm): col. 1 (nº), 15.1 a 15.4 e 16.1 a 16.8 - mesmas proporções do documento de referência
    xc = [X0]
    for largura in larg_col:
        xc.append(xc[-1] + largura)

    chaves_dados = [chave for chave, _, _, _ in DOC_LIB_COLUNAS_INTERVENCAO]
    alturas_linhas = []
    for ordem in range(1, DOC_LIB_LINHAS_INTERVENCOES + 1):
        item = por_ordem.get(ordem, {})
        n_linhas = 1
        for posicao, chave in enumerate(chaves_dados):
            texto = str(item.get(chave) or "")
            if texto and DOC_LIB_COLUNAS_INTERVENCAO[posicao][3] == "texto":
                n_linhas = max(n_linhas, len(ajustar_celula(texto, larg_col[posicao + 1] - 1.2)[1]))
        alturas_linhas.append(max(4.73, n_linhas * 2.5 + 1.6))
    ALTURA_CABECALHO = 5.5 + 4.6 + 4.2 + 5.0
    altura_tabela = ALTURA_CABECALHO + sum(alturas_linhas)
    estado["y"] += 5.0
    garantir(altura_tabela + 6.0)
    yt = estado["y"]
    y_prev, y_grupo, y_sub, y_dados = yt + 5.5, yt + 5.5 + 4.6, yt + 5.5 + 4.6 + 4.2, yt + ALTURA_CABECALHO
    y_fim_t = yt + altura_tabela
    pdf.set_line_width(0.2)
    # molduras
    pdf.rect(X0, yt, LARGURA, altura_tabela)
    pdf.line(xc[1], yt, xc[1], y_fim_t)
    regua(y_prev, xc[1], X1)
    regua(y_grupo, xc[1], X1)
    regua(y_sub, xc[1], X1)
    regua(y_dados, X0, X1)
    pdf.line(xc[5], y_prev, xc[5], y_fim_t)                                  # Previsto | Verificado
    for indice_x in (3, 9):                                                  # Início | Término
        pdf.line(xc[indice_x], y_grupo, xc[indice_x], y_fim_t)
    for indice_x in (2, 4, 6, 7, 8, 10, 11, 12):                             # colunas simples
        pdf.line(xc[indice_x], y_sub, xc[indice_x], y_fim_t)
    # títulos
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("DejaVuC", "", 10.5)
    pdf.set_xy(X0, yt + 7.0)
    pdf.cell(larg_col[0], 5.0, "ATEIE", align="C")
    pdf.set_xy(X0, yt + 12.0)
    pdf.cell(larg_col[0], 5.0, "Nº", align="C")

    def titulo_centralizado(x_ini, x_fim, y_base, numero, texto, tamanho):
        largura = (largura_texto(f"{numero}.", "I", tamanho * 0.62) if numero else 0) + largura_texto(texto, "I", tamanho)
        x_texto = x_ini + ((x_fim - x_ini) - largura) / 2
        if numero:
            rotulo(x_texto, y_base, numero, texto, tamanho)
        else:
            pdf.set_font("DejaVuC", "I", tamanho)
            pdf.text(x_texto, y_base, texto)

    titulo_centralizado(xc[1], X1, yt + 4.0, "14", "Período dos Serviços", 9.0)
    titulo_centralizado(xc[1], xc[5], y_prev + 3.4, "15", "Previsto", 9.0)
    titulo_centralizado(xc[5], X1, y_prev + 3.4, "16", "Verificado", 9.0)
    titulo_centralizado(xc[1], xc[3], y_grupo + 3.1, "", "Início", 9.5)
    titulo_centralizado(xc[3], xc[5], y_grupo + 3.1, "", "Término", 9.5)
    titulo_centralizado(xc[5], xc[9], y_grupo + 3.1, "", "Início do Serviço", 9.5)
    titulo_centralizado(xc[9], X1, y_grupo + 3.1, "", "Término do Serviço", 9.5)
    sub_rotulos = [("15.1", "Data"), ("15.2", "Hora"), ("15.3", "Data"), ("15.4", "Hora"),
                   ("16.1", "Data"), ("16.2", "Hora"), ("16.3", "OS-R."), ("16.4", "OS-OE"),
                   ("16.5", "Data"), ("16.6", "Hora"), ("16.7", "OS-R."), ("16.8", "OS-OE")]
    for posicao, (numero, texto) in enumerate(sub_rotulos):
        titulo_centralizado(xc[posicao + 1], xc[posicao + 2], y_sub + 3.6, numero, texto, 7.0)

    # ATEIE gerado ainda sem o "De acordo" preenchido (e salvo): linha vermelha sobre as colunas 6 a 13 e o aviso
    # abaixo da Nota. Ao gerar o documento de novo, com o "De acordo" já salvo, a marca deixa de aparecer.
    de_acordo_pdf = doc_lib_de_acordo_completo(doc.get("notificacoes"))

    def aguarda_de_acordo(item):
        return bool(item.get("numero")) and \
            doc_lib_calcular_status(item, True, de_acordo_pdf) == STATUS_ATEIE_AGUARDA_DE_ACORDO

    # linhas de dados
    y_linha = y_dados
    for indice, ordem in enumerate(range(1, DOC_LIB_LINHAS_INTERVENCOES + 1)):
        altura = alturas_linhas[indice]
        item = por_ordem.get(ordem)
        if indice:
            regua(y_linha, X0, X1)
        if item:
            cancelada = item.get("status") == STATUS_ATEIE_CANCELADO
            cor = (176, 0, 0) if cancelada else (0, 0, 0)
            pdf.set_text_color(*cor)
            pdf.set_font("DejaVuC", "B", 8.0)
            pdf.set_xy(xc[0], y_linha + (altura - 3.2) / 2)
            pdf.cell(larg_col[0], 3.2, item.get("numero") or "", align="C")
            for posicao, chave in enumerate(chaves_dados):
                texto = str(item.get(chave) or "")
                if not texto:
                    continue
                if DOC_LIB_COLUNAS_INTERVENCAO[posicao][3] == "texto":
                    tamanho, linhas_texto = ajustar_celula(texto, larg_col[posicao + 1] - 1.2)
                    pdf.set_font("DejaVuC", "", tamanho)
                    y_texto = y_linha + (altura - len(linhas_texto) * 2.5) / 2
                    for linha_texto in linhas_texto:
                        pdf.set_xy(xc[posicao + 1], y_texto)
                        pdf.cell(larg_col[posicao + 1], 2.5, linha_texto, align="C")
                        y_texto += 2.5
                else:
                    pdf.set_font("DejaVuC", "", 7.5)
                    pdf.set_xy(xc[posicao + 1], y_linha + (altura - 3.2) / 2)
                    pdf.cell(larg_col[posicao + 1], 3.2, texto, align="C")
            if cancelada:                                       # risco sobre toda a linha cancelada
                pdf.set_draw_color(176, 0, 0)
                pdf.set_line_width(0.35)
                pdf.line(xc[0] + 1, y_linha + altura / 2, X1 - 1, y_linha + altura / 2)
                pdf.set_draw_color(0, 0, 0)
                pdf.set_line_width(0.2)
            elif aguarda_de_acordo(item):                       # linha vermelha nas colunas 6 a 13
                pdf.set_draw_color(176, 0, 0)
                pdf.set_line_width(0.35)
                pdf.line(xc[5] + 1, y_linha + altura / 2, X1 - 1, y_linha + altura / 2)
                pdf.set_draw_color(0, 0, 0)
                pdf.set_line_width(0.2)
            pdf.set_text_color(0, 0, 0)
        y_linha += altura
    estado["y"] = y_fim_t

    # ---- 17. Nota ----------------------------------------------------------------------------------
    pdf.set_text_color(0, 0, 0)
    canceladas = [item for item in intervencoes if item.get("status") == STATUS_ATEIE_CANCELADO]
    texto_nota = (doc.get("nota") or "").strip()
    estado["y"] += 1.0
    garantir(10.0)
    y_nota = estado["y"]
    x_fim_rotulo = rotulo(X0 + 1.0, y_nota + 3.6, "17", "Nota:")
    pdf.set_font("DejaVuC", "", 9.0)
    linhas_nota = doc_lib_quebrar_linhas(pdf, X1 - x_fim_rotulo - 3.5, 4.0, texto_nota) \
        if texto_nota else []
    x_nota = x_fim_rotulo + 2.0
    y_atual = y_nota + 3.6
    for indice, linha in enumerate(linhas_nota):
        if y_atual + 3.0 > PDFAteie.Y_MAXIMO:
            nova_pagina()
            y_atual = estado["y"] + 3.6
            pdf.set_font("DejaVuC", "", 9.0)
        pdf.text(x_nota, y_atual, linha)
        y_atual += 4.0
    aguardando = any(aguarda_de_acordo(item) for item in intervencoes)
    if aguardando:
        y_atual += 1.5 if linhas_nota else 5.0
        if y_atual + 3.0 > PDFAteie.Y_MAXIMO:
            nova_pagina()
            y_atual = estado["y"] + 3.6
        pdf.set_font("DejaVuC", "B", 8.5)
        pdf.set_text_color(176, 0, 0)
        pdf.text(X0 + 1.0, y_atual, "Aguardando o De Acordo do documento")
        y_atual += 4.0
        pdf.set_text_color(0, 0, 0)
    if canceladas:
        y_atual += 1.5 if (linhas_nota or aguardando) else 5.0
        if y_atual + 3.0 > PDFAteie.Y_MAXIMO:
            nova_pagina()
            y_atual = estado["y"] + 3.6
        pdf.set_font("DejaVuC", "B", 8.5)
        pdf.set_text_color(176, 0, 0)
        pdf.text(X0 + 1.0, y_atual, "Intervenções canceladas:")
        y_atual += 4.0
        pdf.set_font("DejaVuC", "", 8.5)
        for item in canceladas:
            descricao = (f"{item.get('numero')} - cancelada em {item.get('data_cancelamento')} por "
                         f"{item.get('cancelada_por')}. Justificativa: {item.get('justificativa_cancelamento')}")
            for linha in doc_lib_quebrar_linhas(pdf, LARGURA - 5.0, 3.8, descricao):
                if y_atual + 3.0 > PDFAteie.Y_MAXIMO:
                    nova_pagina()
                    y_atual = estado["y"] + 3.6
                    pdf.set_font("DejaVuC", "", 8.5)
                    pdf.set_text_color(176, 0, 0)
                pdf.text(X0 + 3.0, y_atual, linha)
                y_atual += 3.8
        pdf.set_text_color(0, 0, 0)

    pdf.output(caminho)


def doc_lib_pasta_destino(tipo, ano):
    """Pasta onde o documento será arquivado: PASTA_ARQUIVO_DOC_LIB/<tipo>/<ano>. Se ela estiver
    indisponível (por exemplo, rede fora do ar), usa a pasta local. Retorna (pasta, aviso)."""
    candidatas = [(PASTA_ARQUIVO_DOC_LIB, None)]
    if os.path.normpath(PASTA_ARQUIVO_DOC_LIB) != os.path.normpath(PASTA_ARQUIVO_DOC_LIB_LOCAL):
        candidatas.append((PASTA_ARQUIVO_DOC_LIB_LOCAL,
                           f"A pasta de arquivamento configurada não está acessível:\n{PASTA_ARQUIVO_DOC_LIB}\n\n"
                           f"O documento foi arquivado na pasta local. Copie-o para a pasta da rede quando "
                           f"ela estiver disponível."))
    ultimo_erro = None
    for base, aviso in candidatas:
        pasta = os.path.join(base, tipo, str(ano))
        try:
            os.makedirs(pasta, exist_ok=True)
            arquivo_teste = os.path.join(pasta, f".teste_escrita_{os.getpid()}")
            with open(arquivo_teste, "w"):
                pass
            os.remove(arquivo_teste)
            return pasta, aviso
        except OSError as erro:
            ultimo_erro = erro
    raise OSError(f"Nenhuma pasta de arquivamento disponível: {ultimo_erro}")


def doc_lib_registrar_geracao(doc, caminho, usuario):
    """Registra o PDF gerado e, na PRIMEIRA geração, EMITE o ATEIE: o documento passa a ser protegido (somente as
    colunas 6 a 13 continuam editáveis) e cada ATEIE não cancelado passa a "Aguarda De Acordo" (ou "Aprovado para Execução", se o "De acordo" já
    estiver preenchido). Lança DocLibConflito se o
    documento mudou desde que foi lido. Devolve a revisão atual do documento."""
    agora_texto = datetime.now().strftime("%d/%m/%Y - %H:%Mh")
    conexao = doc_lib_conectar(manual=True)
    cursor = conexao.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT revisao, emitido FROM doclib_ateie WHERE id = ?", (doc["id"],))
        linha = cursor.fetchone()
        if linha is None or linha[0] != doc["revisao"]:
            raise DocLibConflito("Este ATEIE foi alterado por outro usuário enquanto o documento era gerado.\n\n"
                                 "Feche-o e abra-o novamente (Abrir ATEIE salvo) antes de gerar o documento.")
        emitido = bool(linha[1])
        cursor.execute("INSERT INTO doclib_ateie_pdfs (ateie_id, revisao, caminho, gerado_por, gerado_em) "
                       "VALUES (?, ?, ?, ?, ?)", (doc["id"], doc["revisao"], caminho, usuario, agora_texto))
        if not emitido:
            cursor.execute("UPDATE doclib_ateie SET emitido = 1, emitido_em = ?, emitido_por = ?, "
                           "revisao = revisao + 1, atualizado_por = ?, atualizado_em = ? WHERE id = ?",
                           (agora_texto, usuario, usuario, agora_texto, doc["id"]))
            _doc_lib_recalcular_status(cursor, doc["id"], True)
        cursor.execute("SELECT revisao FROM doclib_ateie WHERE id = ?", (doc["id"],))
        revisao = cursor.fetchone()[0]
        cursor.execute("COMMIT")
        return revisao
    except Exception:
        if conexao.in_transaction:
            cursor.execute("ROLLBACK")
        raise
    finally:
        conexao.close()


def doc_lib_arquivar_pdf_ateie(doc, usuario):
    """Gera o PDF do ATEIE, arquiva na pasta do Doc_Lib. (nunca sobrescreve um arquivo anterior), registra o
    arquivo no banco e, na primeira geração, emite o ATEIE. Retorna (caminho, aviso)."""
    agora = datetime.now()
    numeros = [item["numero"] for item in doc["intervencoes"] if item.get("numero")]
    ano = next((item["ano"] for item in doc["intervencoes"] if item.get("ano")), agora.year)
    pasta, aviso = doc_lib_pasta_destino("ATEIE", ano)

    base = numeros[0] + (f"_a_{numeros[-1]}" if len(numeros) > 1 else "") if numeros else f"id{doc['id']}"
    nome_arquivo = f"ATEIE_{base.replace('/', '-')}_{agora.strftime('%Y%m%d-%H%M%S')}.pdf"
    caminho = os.path.join(pasta, nome_arquivo)
    caminho_temporario = caminho + ".tmp"
    try:
        doc_lib_gerar_pdf_ateie(doc, caminho_temporario, usuario)
        os.replace(caminho_temporario, caminho)
    finally:
        if os.path.exists(caminho_temporario):
            os.remove(caminho_temporario)

    try:
        doc_lib_registrar_geracao(doc, caminho, usuario)
    except Exception:
        if os.path.exists(caminho):            # documento não registrado/emitido: não deixa arquivo órfão
            os.remove(caminho)
        raise
    return caminho, aviso


def doc_lib_imprimir_pdf(caminho):
    """Envia o PDF para a impressora padrão (Windows) ou para o sistema de impressão (lp)."""
    so = platform.system()
    if so == "Windows":
        os.startfile(caminho, "print")
    else:
        subprocess.run(["lp", caminho], check=True)



# ---------------------------------------------------
# COMPONENTES VISUAIS DO DOC_LIB. (reaproveitam os componentes do SGA: mesmas cores e fonte)
# ---------------------------------------------------
# Cor do texto de cada status do ATEIE (mesma paleta do SGA)
DOC_LIB_COR_STATUS = {STATUS_ATEIE_EM_ANALISE: "#CC8400", STATUS_ATEIE_AGUARDA_DE_ACORDO: SGA_AZUL,
                      STATUS_ATEIE_APROVADO_EXECUCAO: "#0E7490", STATUS_ATEIE_EM_EXECUCAO: "#5E35B1", STATUS_ATEIE_CONCLUIDO: SGA_VERDE,
                      STATUS_ATEIE_CANCELADO: SGA_VERMELHO}
DOC_LIB_COR_BLOQUEADO = "#EEF1F6"
DOC_LIB_COR_DESABILITADO = "#E3E8EF"
DOC_LIB_TEXTO_DESABILITADO = "#9AA3AF"


def doc_lib_criar_botao(parent, texto, comando, estilo="primario", fonte=None, **opcoes):
    """Botão do SGA (criar_botao_sga) que também sabe ficar desabilitado: o efeito ao passar o
    mouse só vale quando o botão está habilitado."""
    botao = criar_botao_sga(parent, texto, comando, estilo, fonte=fonte, disabledforeground=DOC_LIB_TEXTO_DESABILITADO,
                            **opcoes)
    fundo, fundo_hover, _ = SGA_ESTILOS_BOTAO[estilo]
    botao.bind("<Enter>", lambda e: botao.config(bg=fundo_hover) if str(botao.cget("state")) != "disabled" else None)
    botao.bind("<Leave>", lambda e: botao.config(
        bg=fundo if str(botao.cget("state")) != "disabled" else DOC_LIB_COR_DESABILITADO))
    botao._doclib_estilo = estilo
    return botao


def doc_lib_estado_botao(botao, habilitado):
    """Habilita/desabilita o botão, com aparência clara de cada estado."""
    fundo, _, cor_texto = SGA_ESTILOS_BOTAO[botao._doclib_estilo]
    if habilitado:
        botao.config(state=NORMAL, bg=fundo, fg=cor_texto, cursor="hand2")
    else:
        botao.config(state=DISABLED, bg=DOC_LIB_COR_DESABILITADO, fg=DOC_LIB_TEXTO_DESABILITADO, cursor="arrow")


class IconeCalendarioDocLib(Canvas):
    """Ícone de calendário desenhado (não depende de fonte/emoji do Windows) que abre o calendário
    do campo de data ao lado dele."""

    def __init__(self, parent, comando, bg=SGA_CARD):
        Canvas.__init__(self, parent, width=26, height=24, bg=bg, highlightthickness=0, cursor="hand2")
        self.comando = comando
        self.habilitado = True
        self._desenhar(SGA_AZUL)
        self.bind("<Button-1>", self._clicar)

    def _desenhar(self, cor):
        self.delete("all")
        self.create_rectangle(4, 6, 22, 21, outline=cor, width=2)
        self.create_line(4, 11, 22, 11, fill=cor, width=2)
        self.create_line(8, 3, 8, 8, fill=cor, width=2)
        self.create_line(18, 3, 18, 8, fill=cor, width=2)
        for x in (8, 12, 16):
            for y in (14, 17):
                self.create_rectangle(x, y, x + 1, y + 1, fill=cor, outline=cor)

    def definir_habilitado(self, habilitado):
        self.habilitado = habilitado
        self._desenhar(SGA_AZUL if habilitado else DOC_LIB_TEXTO_DESABILITADO)
        self.configure(cursor="hand2" if habilitado else "arrow")

    def _clicar(self, evento=None):
        if self.habilitado:
            self.comando()


def doc_lib_bloquear_widget(widget, bloquear):
    """Trava (somente leitura) ou libera um campo, conforme o tipo de componente."""
    try:
        classe = widget.winfo_class()
        if classe == "Entry":
            widget.configure(state="readonly" if bloquear else "normal")
        elif classe == "Text":
            widget.configure(state=DISABLED if bloquear else NORMAL,
                             bg=DOC_LIB_COR_BLOQUEADO if bloquear else "white")
        elif classe == "TCombobox":
            widget.configure(state="disabled" if bloquear else "readonly")
        elif classe in ("Radiobutton", "Button"):
            widget.configure(state=DISABLED if bloquear else NORMAL)
        elif hasattr(widget, "definir_habilitado"):
            widget.definir_habilitado(not bloquear)
    except TclError:
        pass


def doc_lib_definir_entrada(entrada, texto):
    """Grava texto em um Entry mesmo que ele esteja travado (somente leitura)."""
    estado = str(entrada.cget("state"))
    entrada.configure(state="normal")
    entrada.delete(0, END)
    entrada.insert(0, texto)
    entrada.configure(state=estado)


def doc_lib_selecionar_data(parent, entrada, ano_curto=False, ao_selecionar=None):
    """Abre o calendário do sistema (tkcalendar, em português) e grava a data escolhida no campo,
    no formato dd/mm/aaaa (ou dd/mm/aa quando ano_curto=True)."""
    if str(entrada.cget("state")) != "normal":
        return
    janela_cal = Toplevel(parent)
    janela_cal.title("Selecione a Data")
    janela_cal.resizable(False, False)
    janela_cal.transient(parent.winfo_toplevel())

    atual = doc_lib_normalizar_data(entrada.get())
    data_inicial = datetime.strptime(atual, "%d/%m/%Y") if atual else datetime.now()
    cal = Calendar(janela_cal, selectmode='day', date_pattern='dd/mm/yyyy',
                   year=data_inicial.year, month=data_inicial.month, day=data_inicial.day)
    cal.pack(padx=20, pady=(20, 10))

    def confirmar(evento=None):
        texto = cal.selection_get().strftime("%d/%m/%y" if ano_curto else "%d/%m/%Y")
        doc_lib_definir_entrada(entrada, texto)
        janela_cal.destroy()
        if ao_selecionar:
            ao_selecionar()

    criar_botao_sga(janela_cal, "Selecionar", confirmar, "primario").pack(pady=(0, 18), ipadx=18, ipady=4)
    janela_cal.bind("<Return>", confirmar)

    janela_cal.update_idletasks()
    x = entrada.winfo_rootx()
    y = entrada.winfo_rooty() + entrada.winfo_height() + 4
    x = max(0, min(x, janela_cal.winfo_screenwidth() - janela_cal.winfo_reqwidth() - 10))
    y = max(0, min(y, janela_cal.winfo_screenheight() - janela_cal.winfo_reqheight() - 50))
    janela_cal.geometry(f"+{x}+{y}")
    try:
        janela_cal.grab_set()
    except TclError:
        pass


# Colunas da janela "Abrir ATEIE salvo": (campo, título, largura em pixels, exibir sempre em caixa alta)
DOC_LIB_COLUNAS_LISTA = [
    ("numero", "N° ATEIE", 105, False),
    ("equipamento", "Equipamento de Interligação", 185, True),
    ("empresa", "Empresa", 115, True),
    ("solicitante", "Solicitado por", 150, False),
    ("prog_inicio", "Programação Início", 135, False),
    ("prog_termino", "Programação Término", 135, False),
    ("local", "Local", 140, True),
    ("servicos", "Serviços a Executar", 205, False),
    ("status", "Status", 160, False),
]


def _doc_lib_uma_linha(texto):
    return " ".join(str(texto or "").split())


class TabelaQuebraDocLib(Frame):
    """Tabela em que o texto de cada célula QUEBRA em várias linhas quando é maior que a largura da coluna (a
    altura da linha acompanha a célula mais alta). Cabeçalho clicável (usado nos filtros), barras de rolagem
    vertical e horizontal, seleção por clique e duplo clique para abrir."""

    ALTURA_CABECALHO = 40
    ALTURA_MINIMA = 28
    MARGEM = 8
    COR_SELECAO = "#DCE8F8"

    def __init__(self, pai, colunas, ao_clicar_titulo=None, ao_abrir=None):
        Frame.__init__(self, pai, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
        self.colunas = [(chave, titulo, largura) for chave, titulo, largura in colunas]
        self.ao_clicar_titulo = ao_clicar_titulo
        self.ao_abrir = ao_abrir
        self.titulos = {chave: titulo for chave, titulo, _ in self.colunas}
        self.x0, total = [], 0
        for _, _, largura in self.colunas:
            self.x0.append(total)
            total += largura
        self.largura_total = total
        self.registros = []
        self.faixas = []                 # (y_inicial, y_final, retângulo de fundo, cor de fundo) de cada linha
        self.selecionado = None

        self.cabecalho = Canvas(self, height=self.ALTURA_CABECALHO, bg=SGA_AZUL, highlightthickness=0,
                                cursor="hand2")
        self.corpo = Canvas(self, bg="white", highlightthickness=0, yscrollincrement=28, xscrollincrement=40,
                            takefocus=1)
        self.barra_v = Scrollbar(self, orient=VERTICAL, command=self.corpo.yview)
        self.barra_h = Scrollbar(self, orient=HORIZONTAL, command=self._rolar_x)
        self.cabecalho.grid(row=0, column=0, sticky="ew")
        self.corpo.grid(row=1, column=0, sticky="nsew")
        self.barra_v.grid(row=1, column=1, sticky="ns")
        self.barra_h.grid(row=2, column=0, sticky="ew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.corpo.configure(yscrollcommand=self.barra_v.set, xscrollcommand=self._ao_rolar_x)
        self.cabecalho.configure(scrollregion=(0, 0, self.largura_total, self.ALTURA_CABECALHO))
        self.itens_titulo = {}
        self._desenhar_cabecalho()

        self.cabecalho.bind("<Button-1>", self._clicar_cabecalho)
        self.corpo.bind("<Button-1>", self._clicar)
        self.corpo.bind("<Double-Button-1>", self._duplo)
        self.corpo.bind("<Up>", lambda e: self.selecionar((self.selecionado or 0) - 1 if self.selecionado else 0))
        self.corpo.bind("<Down>", lambda e: self.selecionar(0 if self.selecionado is None else self.selecionado + 1))
        self.corpo.bind("<Return>", lambda e: self._abrir_selecionado())
        for widget in (self.corpo, self.cabecalho):
            widget.bind("<MouseWheel>", self._roda)
            widget.bind("<Shift-MouseWheel>", self._roda_horizontal)

    # ---- cabeçalho -------------------------------------------------------------------------------------------
    def _desenhar_cabecalho(self):
        self.cabecalho.delete("all")
        for (chave, _, largura), x in zip(self.colunas, self.x0):
            self.cabecalho.create_rectangle(x, 0, x + largura, self.ALTURA_CABECALHO, fill=SGA_AZUL, outline="#2F5F9E")
            self.itens_titulo[chave] = self.cabecalho.create_text(
                x + self.MARGEM, self.ALTURA_CABECALHO / 2, text=self.titulos[chave], anchor="w",
                width=largura - 2 * self.MARGEM, fill="white", font=(SGA_FONTE, 10, "bold"))

    def titulo(self, chave):
        return self.titulos[chave]

    def definir_titulo(self, chave, texto):
        self.titulos[chave] = texto
        self.cabecalho.itemconfigure(self.itens_titulo[chave], text=texto)

    def x_coluna(self, chave):
        return self.x0[[c[0] for c in self.colunas].index(chave)]

    def deslocamento_x(self):
        return int(self.corpo.canvasx(0))

    def _clicar_cabecalho(self, evento):
        x = self.cabecalho.canvasx(evento.x)
        for (chave, _, largura), x0 in zip(self.colunas, self.x0):
            if x0 <= x < x0 + largura:
                if self.ao_clicar_titulo:
                    self.ao_clicar_titulo(chave)
                return

    # ---- conteúdo --------------------------------------------------------------------------------------------
    def preencher(self, registros):
        """registros: [{'valores': [textos na ordem das colunas], 'cor': cor do texto, 'dados': qualquer objeto}]."""
        self.registros = list(registros)
        self.selecionado = None
        corpo = self.corpo
        corpo.delete("all")
        self.faixas = []
        y = 0
        for indice, registro in enumerate(self.registros):
            altura = self.ALTURA_MINIMA
            for (chave, _, largura), x, texto in zip(self.colunas, self.x0, registro["valores"]):
                item = corpo.create_text(x + self.MARGEM, y + 6, text=texto, anchor="nw",
                                         width=max(largura - 2 * self.MARGEM, 20), font=(SGA_FONTE, 10),
                                         fill=registro.get("cor", SGA_TEXTO))
                caixa = corpo.bbox(item)
                if caixa:
                    altura = max(altura, caixa[3] - y + 6)
            fundo = "#FFFFFF" if indice % 2 == 0 else "#F6F8FB"
            retangulo = corpo.create_rectangle(0, y, self.largura_total, y + altura, fill=fundo, outline="")
            corpo.tag_lower(retangulo)
            corpo.create_line(0, y + altura, self.largura_total, y + altura, fill="#E5EAF1")
            self.faixas.append((y, y + altura, retangulo, fundo))
            y += altura
        for x in self.x0[1:]:
            corpo.create_line(x, 0, x, y, fill="#E5EAF1")
        corpo.configure(scrollregion=(0, 0, self.largura_total, max(y, 1)))
        corpo.yview_moveto(0)

    def linhas(self):
        """Textos exibidos em cada linha (na ordem das colunas)."""
        return [registro["valores"] for registro in self.registros]

    def alturas_linhas(self):
        return [fim - inicio for inicio, fim, _, _ in self.faixas]

    # ---- seleção e rolagem -----------------------------------------------------------------------------------
    def selecionar(self, indice):
        if self.selecionado is not None and self.selecionado < len(self.faixas):
            self.corpo.itemconfigure(self.faixas[self.selecionado][2], fill=self.faixas[self.selecionado][3])
        self.selecionado = indice if indice is not None and 0 <= indice < len(self.faixas) else None
        if self.selecionado is not None:
            inicio, fim, retangulo, _ = self.faixas[self.selecionado]
            self.corpo.itemconfigure(retangulo, fill=self.COR_SELECAO)
            self._mostrar(inicio, fim)

    def _mostrar(self, inicio, fim):
        total = max(self.faixas[-1][1], 1)
        topo = self.corpo.canvasy(0)
        visivel = max(self.corpo.winfo_height(), 1)
        if inicio < topo:
            self.corpo.yview_moveto(inicio / total)
        elif fim > topo + visivel:
            self.corpo.yview_moveto((fim - visivel) / total)

    def dados_selecionado(self):
        if self.selecionado is None:
            return None
        return self.registros[self.selecionado].get("dados")

    def _clicar(self, evento):
        self.corpo.focus_set()
        y = self.corpo.canvasy(evento.y)
        self.selecionar(next((i for i, (inicio, fim, _, _) in enumerate(self.faixas) if inicio <= y < fim), None))

    def _duplo(self, evento):
        self._clicar(evento)
        self._abrir_selecionado()

    def _abrir_selecionado(self):
        if self.selecionado is not None and self.ao_abrir:
            self.ao_abrir()

    def _ao_rolar_x(self, inicio, fim):
        self.barra_h.set(inicio, fim)
        self.cabecalho.xview_moveto(inicio)

    def _rolar_x(self, *args):
        self.corpo.xview(*args)
        self.cabecalho.xview(*args)

    def _roda(self, evento):
        self.corpo.yview_scroll(int(-1 * (evento.delta / 120)), "units")

    def _roda_horizontal(self, evento):
        self._rolar_x("scroll", int(-1 * (evento.delta / 120)), "units")


class JanelaListaAteie:
    """Janela "Abrir ATEIE salvo": UMA linha por ATEIE (número), com busca livre e filtros por coluna que
    podem ser combinados (clique no título da coluna para ver os valores existentes, sem repetição). O texto de
    cada coluna quebra em mais de uma linha quando é maior que a largura; Equipamento de Interligação, Empresa e
    Local aparecem sempre em caixa alta."""

    SEM_FILTRO = "(Todos)"

    def __init__(self, parent):
        self.parent = parent
        self.resultado = None            # (id do documento, linha da tabela) do ATEIE escolhido
        self.filtros = {}                # campo -> valor selecionado
        self.popup = None
        self.registros = doc_lib_listar_ateie()
        for registro in self.registros:
            textos = {}
            for chave, _, _, maiuscula in DOC_LIB_COLUNAS_LISTA:
                texto = _doc_lib_uma_linha(registro[chave])
                textos[chave] = texto.upper() if maiuscula else texto
            registro["_texto"] = textos

        janela = self.janela = Toplevel(parent)
        janela.title("Abrir ATEIE salvo")
        janela.geometry("1400x700")
        janela.minsize(900, 500)
        janela.transient(parent)
        ui_dialogo(janela, "Abrir ATEIE salvo", "Selecione o ATEIE e clique em Abrir (ou dê duplo clique). "
                                                 "Clique no título de uma coluna para filtrar.")

        barra_busca = Frame(janela, bg=SGA_FUNDO)
        barra_busca.place(x=24, y=78, relwidth=1.0, width=-48, height=34)
        Label(barra_busca, text="Buscar:", bg=SGA_FUNDO, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 10, "bold")
              ).pack(side=LEFT)
        self.busca_var = StringVar()
        self.entrada_busca = criar_entrada_sga(barra_busca, textvariable=self.busca_var)
        self.entrada_busca.pack(side=LEFT, fill=X, expand=True, padx=(8, 0))
        doc_lib_criar_botao(barra_busca, "Limpar filtros", self.limpar_filtros, "neutro"
                            ).pack(side=RIGHT, padx=(10, 0), ipadx=10, fill=Y)

        self.tabela = TabelaQuebraDocLib(janela, [(c[0], self.titulo_coluna(c[0], c[1]), c[2])
                                                  for c in DOC_LIB_COLUNAS_LISTA],
                                         ao_clicar_titulo=self.abrir_filtro, ao_abrir=self.abrir)
        self.tabela.place(x=24, y=122, relwidth=1.0, width=-48, relheight=1.0, height=-122 - 78)

        self.contador = Label(janela, text="", bg=SGA_FUNDO, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9), anchor="w")
        self.contador.place(x=24, rely=1.0, y=-30, anchor="sw")

        self.busca_var.trace_add("write", lambda *args: self.aplicar())
        doc_lib_criar_botao(janela, "Abrir", self.abrir, "primario"
                            ).place(relx=0.5, x=-130, rely=1.0, y=-20, anchor="sw", width=120, height=40)
        doc_lib_criar_botao(janela, "Voltar", janela.destroy, "neutro"
                            ).place(relx=0.5, x=10, rely=1.0, y=-20, anchor="sw", width=120, height=40)
        self.aplicar()
        self.entrada_busca.focus_set()

    # ---- dados e filtros -------------------------------------------------------------------------------------
    @staticmethod
    def valor_filtro(registro, chave):
        """Valor do registro usado no filtro da coluna (nas colunas de programação filtra-se pela data)."""
        texto = registro["_texto"][chave]
        return texto.split(" ")[0] if chave in ("prog_inicio", "prog_termino") else texto

    def valores_distintos(self, chave):
        """Todos os valores existentes na coluna, sem repetição, em ordem útil para escolher."""
        valores = {self.valor_filtro(registro, chave) for registro in self.registros}
        valores.discard("")
        if chave == "status":
            return [status for status in DOC_LIB_STATUS_ATEIE if status in valores]
        if chave == "numero":
            return sorted(valores, key=lambda n: (n.split("/")[-1], n), reverse=True)
        if chave in ("prog_inicio", "prog_termino"):
            return sorted(valores, key=lambda d: d.split("/")[::-1], reverse=True)
        return sorted(valores, key=lambda v: v.lower())

    def linhas_visiveis(self):
        """Registros que atendem a todos os filtros ativos (combinados) e à busca livre."""
        termo = self.busca_var.get().strip().lower()
        visiveis = []
        for registro in self.registros:
            if any(self.valor_filtro(registro, chave) != valor for chave, valor in self.filtros.items()):
                continue
            if termo and termo not in " ".join(registro["_texto"].values()).lower():
                continue
            visiveis.append(registro)
        return visiveis

    def titulo_coluna(self, chave, titulo=None):
        titulo = titulo or next(c[1] for c in DOC_LIB_COLUNAS_LISTA if c[0] == chave)
        return f"● {titulo} ▼" if chave in self.filtros else f"{titulo} ▼"

    def aplicar(self):
        """Redesenha a lista conforme os filtros e a busca."""
        visiveis = self.linhas_visiveis()
        self.tabela.preencher([{
            "valores": [registro["_texto"][c[0]] for c in DOC_LIB_COLUNAS_LISTA],
            "cor": DOC_LIB_COR_STATUS.get(registro["status"], SGA_TEXTO),
            "dados": (registro["ateie_id"], registro["ordem"])} for registro in visiveis])
        for chave, _, _, _ in DOC_LIB_COLUNAS_LISTA:
            self.tabela.definir_titulo(chave, self.titulo_coluna(chave))
        titulos = {c[0]: c[1] for c in DOC_LIB_COLUNAS_LISTA}
        ativos = "; ".join(f"{titulos[chave]} = {valor}" for chave, valor in self.filtros.items())
        self.contador.config(text=f"{len(visiveis)} de {len(self.registros)} ATEIE(s)"
                                  + (f"   |   Filtros ativos: {ativos}" if ativos else ""))

    def definir_filtro(self, chave, valor):
        """Filtra a coluna pelo valor (None remove o filtro dessa coluna). Os filtros das colunas se combinam."""
        if valor is None:
            self.filtros.pop(chave, None)
        else:
            self.filtros[chave] = valor
        self.aplicar()

    def limpar_filtros(self):
        """Remove todos os filtros e a busca: volta a mostrar todos os ATEIE."""
        self.fechar_filtro()
        self.filtros.clear()
        self.busca_var.set("")
        self.aplicar()

    # ---- menu de valores da coluna (seta no título) --------------------------------------------------------------
    def abrir_filtro(self, chave):
        self.fechar_filtro()
        valores = self.valores_distintos(chave)
        x = self.tabela.corpo.winfo_rootx() + self.tabela.x_coluna(chave) - self.tabela.deslocamento_x()
        x = max(self.tabela.corpo.winfo_rootx(), x)
        y = self.tabela.cabecalho.winfo_rooty() + self.tabela.ALTURA_CABECALHO

        popup = self.popup = Toplevel(self.janela)
        popup.overrideredirect(True)
        popup.geometry(f"+{x}+{y}")
        quadro = Frame(popup, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_AZUL)
        quadro.pack(fill=BOTH, expand=True)
        busca = StringVar()
        entrada = criar_entrada_sga(quadro, textvariable=busca)
        entrada.pack(fill=X, padx=6, pady=(6, 4))
        corpo = Frame(quadro, bg=SGA_CARD)
        corpo.pack(fill=BOTH, expand=True, padx=6, pady=(0, 6))
        largura = max([len(self.SEM_FILTRO)] + [min(len(v), 70) for v in valores]) + 2
        lista = Listbox(corpo, height=min(12, len(valores) + 1), width=max(largura, 24), exportselection=False,
                        font=(SGA_FONTE, 10))
        rolagem = Scrollbar(corpo, orient=VERTICAL, command=lista.yview)
        lista.configure(yscrollcommand=rolagem.set)
        rolagem.pack(side=RIGHT, fill=Y)
        lista.pack(side=LEFT, fill=BOTH, expand=True)
        self.lista_popup, self.itens_popup = lista, []

        def preencher(*args):
            termo = busca.get().strip().lower()
            self.itens_popup = [self.SEM_FILTRO] + [v for v in valores if not termo or termo in v.lower()]
            lista.delete(0, END)
            for valor in self.itens_popup:
                lista.insert(END, valor if len(valor) <= 80 else valor[:77] + "…")
            atual = self.filtros.get(chave)
            if atual in self.itens_popup:
                lista.selection_set(self.itens_popup.index(atual))

        def escolher(evento=None):
            selecao = lista.curselection()
            if not selecao:
                return
            valor = self.itens_popup[selecao[0]]
            self.fechar_filtro()
            self.definir_filtro(chave, None if valor == self.SEM_FILTRO else valor)

        def clique(evento):
            """Com o foco preso ao menu, um clique fora dele fecha o menu."""
            dentro = (popup.winfo_rootx() <= evento.x_root < popup.winfo_rootx() + popup.winfo_width()
                      and popup.winfo_rooty() <= evento.y_root < popup.winfo_rooty() + popup.winfo_height())
            if not dentro:
                self.fechar_filtro()

        busca.trace_add("write", preencher)
        lista.bind("<ButtonRelease-1>", escolher)
        lista.bind("<Return>", escolher)
        entrada.bind("<Return>", lambda e: (lista.selection_clear(0, END),
                                           lista.selection_set(1 if len(self.itens_popup) > 1 else 0), escolher()))
        entrada.bind("<Down>", lambda e: lista.focus_set())
        popup.bind("<Escape>", lambda e: self.fechar_filtro())
        popup.bind("<Button-1>", clique, add="+")
        preencher()
        try:
            popup.update_idletasks()
            popup.grab_set()
            entrada.focus_force()
        except TclError:
            pass

    def fechar_filtro(self):
        if self.popup is not None:
            try:
                self.popup.destroy()
            except TclError:
                pass
            self.popup = None
            try:
                self.janela.grab_set()
            except TclError:
                pass

    def abrir(self, evento=None):
        escolha = self.tabela.dados_selecionado()
        if escolha is None:
            messagebox.showwarning("Atenção", "Selecione um ATEIE na lista.", parent=self.janela)
            return
        self.resultado = escolha
        self.janela.destroy()


def doc_lib_escolher_ateie(parent):
    """Abre a janela "Abrir ATEIE salvo" e devolve (id do documento, linha da tabela) do ATEIE escolhido,
    ou None se o usuário voltar sem escolher."""
    janela = JanelaListaAteie(parent)
    try:
        janela.janela.grab_set()
    except TclError:
        pass
    janela.janela.wait_window()
    return janela.resultado


def doc_lib_dialogo_documento_gerado(parent, caminho, aviso=None, lembrete=None):
    """Janela exibida logo após gerar o documento: mostra onde ele foi arquivado e já oferece
    abrir o PDF e imprimir. aviso: problema com a pasta de arquivamento; lembrete: orientação sobre o documento."""
    extra = (90 if aviso else 0) + (80 if lembrete else 0)
    altura = 300 + extra
    janela = Toplevel(parent)
    janela.title("Documento gerado")
    janela.geometry(f"660x{altura}")
    janela.resizable(False, False)
    janela.transient(parent)
    ui_dialogo(janela, "Documento gerado e arquivado", "O PDF permanece arquivado por tempo indeterminado")

    cartao = ui_cartao(janela, 84, 96 + extra)
    Label(cartao, text="Arquivo:", bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9, "bold")
          ).place(x=20, y=14)
    Label(cartao, text=caminho, bg=SGA_CARD, fg=SGA_TEXTO, font=(SGA_FONTE, 10), wraplength=580,
          justify="left", anchor="w").place(x=20, y=36)
    if aviso:
        Label(cartao, text=aviso, bg=SGA_CARD, fg=SGA_VERMELHO, font=(SGA_FONTE, 9), wraplength=580,
              justify="left", anchor="w").place(x=20, y=96)
    if lembrete:
        Label(cartao, text=lembrete, bg=SGA_CARD, fg=SGA_TEXTO, font=(SGA_FONTE, 9, "bold"), wraplength=580,
              justify="left", anchor="w").place(x=20, y=96 + (90 if aviso else 0))

    def abrir():
        try:
            abrir_pdf(caminho)
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível abrir o PDF: {erro}", parent=janela)

    def imprimir():
        try:
            doc_lib_imprimir_pdf(caminho)
            messagebox.showinfo("Impressão", "Documento enviado para a impressora padrão.", parent=janela)
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível enviar o documento para a impressora: {erro}\n\n"
                                         f"Abra o PDF e imprima por ele (Ctrl+P).", parent=janela)

    doc_lib_criar_botao(janela, "Abrir PDF", abrir, "primario"
                        ).place(relx=0.5, x=-225, rely=1.0, y=-22, anchor="sw", width=140, height=42)
    doc_lib_criar_botao(janela, "Imprimir", imprimir, "sucesso"
                        ).place(relx=0.5, x=-70, rely=1.0, y=-22, anchor="sw", width=140, height=42)
    doc_lib_criar_botao(janela, "Fechar", janela.destroy, "neutro"
                        ).place(relx=0.5, x=85, rely=1.0, y=-22, anchor="sw", width=140, height=42)
    try:
        janela.grab_set()
    except TclError:
        pass
    janela.wait_window()


class LinhasDinamicasDocLib:
    """Bloco de linhas horizontais com botão 'Adicionar' e limite de linhas. Usado em 'De acordo'
    (Pessoas/Áreas notificadas) e em 'Pessoal Notificado'. O botão Adicionar fica na última linha e
    deixa de permitir novas inclusões quando o limite é atingido.

    Colunas do tipo "empresa" são um Combobox com a lista de empresas do ATEIE; em OUTRA aparece um campo para
    digitar o nome (o mesmo mecanismo de "Empresa Solicitante")."""

    def __init__(self, ateie, pai, colunas, limite, empresas=None):
        self.ateie = ateie
        self.pai = pai
        self.colunas = colunas
        self.limite = limite
        self.empresas = empresas or DOC_LIB_EMPRESAS_NOTIFICADAS_ATEIE    # opções das colunas do tipo "empresa"
        self.linhas = []
        self.bloqueado = False        # todas as linhas travadas
        self.fixas = 0                # quantidade de primeiras linhas travadas (já registradas) com o restante livre

        for indice, (chave, rotulo, tipo) in enumerate(colunas):
            if tipo == "data":
                minimo, peso = 150, 0
            elif tipo == "hora":
                minimo, peso = 86, 0
            elif tipo == "empresa":
                minimo, peso = 170, 2
            else:
                minimo, peso = 110, 3 if chave == "nome" else 2
            pai.grid_columnconfigure(indice, weight=peso, minsize=minimo)
            Label(pai, text=rotulo, bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9, "bold"), anchor="w"
                  ).grid(row=0, column=indice, sticky="w", padx=4)
        self.coluna_adicionar = len(colunas)
        pai.grid_columnconfigure(self.coluna_adicionar, minsize=96)
        pai.grid_columnconfigure(self.coluna_adicionar + 1, minsize=90)
        self.adicionar_linha()

    def adicionar_linha(self, valores=None):
        if len(self.linhas) >= self.limite:
            return None
        grade = len(self.linhas) + 1
        linha = {"campos": {}, "outras": {}, "widgets": [], "icones": []}
        for coluna, (chave, rotulo, tipo) in enumerate(self.colunas):
            if tipo == "data":
                quadro = Frame(self.pai, bg=SGA_CARD)
                entrada = criar_entrada_sga(quadro, width=11)
                entrada.pack(side=LEFT, fill=X, expand=True)
                icone = IconeCalendarioDocLib(quadro, lambda e=entrada: self.ateie.abrir_calendario(e, False))
                icone.pack(side=LEFT, padx=(4, 0))
                linha["icones"].append(icone)
                celula = quadro
            elif tipo == "empresa":
                celula = Frame(self.pai, bg=SGA_CARD)
                entrada = ttk.Combobox(celula, values=self.empresas, state="readonly", width=14,
                                       font=(SGA_FONTE, 10))
                entrada.pack(fill=X)
                entrada.bind("<MouseWheel>", lambda e: (_rolar_area_sga(e), "break")[1])
                rotulo_outra = Label(celula, text="Nome da empresa:", bg=SGA_CARD, fg=SGA_TEXTO_SUAVE,
                                     font=(SGA_FONTE, 8, "bold"), anchor="w")
                outra = criar_entrada_sga(celula, width=14)
                self.ateie.configurar_entrada(outra, "texto")
                linha["outras"][chave] = (rotulo_outra, outra)
                entrada.bind("<<ComboboxSelected>>", lambda e, l=linha, c=chave: self._ao_mudar_empresa(l, c, True))
            else:
                entrada = criar_entrada_sga(self.pai, width=8 if tipo == "hora" else 18)
                celula = entrada
            celula.grid(row=grade, column=coluna, sticky="new", padx=4, pady=3)
            linha["widgets"].append((celula, coluna))
            linha["campos"][chave] = entrada
            if tipo != "empresa":
                self.ateie.configurar_entrada(entrada, tipo, ano_curto=False)
            if valores:
                if tipo == "empresa":
                    entrada.set(valores.get(chave) or "")
                    doc_lib_definir_entrada(linha["outras"][chave][1], valores.get(chave + "_outra") or "")
                    self._ao_mudar_empresa(linha, chave, False)
                else:
                    doc_lib_definir_entrada(entrada, valores.get(chave) or "")
            if self.bloqueado:
                doc_lib_bloquear_widget(entrada, True)
                if tipo == "empresa":
                    doc_lib_bloquear_widget(linha["outras"][chave][1], True)

        linha["btn_add"] = doc_lib_criar_botao(self.pai, "Adicionar", self._ao_adicionar, "primario",
                                               fonte=(SGA_FONTE, 9, "bold"))
        linha["btn_rem"] = doc_lib_criar_botao(self.pai, "Remover", lambda l=linha: self.remover_linha(l), "neutro",
                                               fonte=(SGA_FONTE, 9, "bold"))
        self.linhas.append(linha)
        self._reorganizar()
        return linha

    def _ao_mudar_empresa(self, linha, chave, foco):
        """Em OUTRA mostra o campo para o nome da empresa; nas demais opções, esconde e limpa o campo."""
        combo = linha["campos"][chave]
        rotulo_outra, outra = linha["outras"][chave]
        self.ateie._limpar_marca(combo)
        if combo.get() == "OUTRA":
            rotulo_outra.pack(fill=X, pady=(4, 0))
            outra.pack(fill=X)
            if foco:
                outra.focus_set()
        else:
            rotulo_outra.pack_forget()
            outra.pack_forget()
            doc_lib_definir_entrada(outra, "")
            self.ateie._limpar_marca(outra)

    def _ao_adicionar(self):
        linha = self.adicionar_linha()
        if linha:
            primeira = next(iter(linha["campos"].values()))
            primeira.focus_set()
            self.ateie.rolar_ate(primeira)

    def remover_linha(self, linha):
        if self.bloqueado or len(self.linhas) <= 1 or linha not in self.linhas \
                or self.linhas.index(linha) < self.fixas:
            return
        for celula, _ in linha["widgets"]:
            self.ateie.esquecer_marcas(celula)
            celula.destroy()
        linha["btn_add"].destroy()
        linha["btn_rem"].destroy()
        self.linhas.remove(linha)
        self._reorganizar()

    def _reorganizar(self):
        """Reposiciona as linhas e mostra o botão Adicionar só na última (desabilitado no limite)."""
        total = len(self.linhas)
        for posicao, linha in enumerate(self.linhas):
            grade = posicao + 1
            for celula, coluna in linha["widgets"]:
                celula.grid_configure(row=grade)
            ultima = posicao == total - 1
            if ultima:
                linha["btn_add"].grid(row=grade, column=self.coluna_adicionar, sticky="new", padx=4, pady=3)
                doc_lib_estado_botao(linha["btn_add"], total < self.limite and not self.bloqueado)
            else:
                linha["btn_add"].grid_remove()
            if posicao > 0:
                linha["btn_rem"].grid(row=grade, column=self.coluna_adicionar + 1, sticky="new", padx=4, pady=3)
                doc_lib_estado_botao(linha["btn_rem"], not self.bloqueado and posicao >= self.fixas)
            else:
                linha["btn_rem"].grid_remove()

    def coletar(self):
        resultado = []
        for linha in self.linhas:
            item = {chave: entrada.get().strip() for chave, entrada in linha["campos"].items()}
            for chave, (_, outra) in linha["outras"].items():
                item[chave + "_outra"] = outra.get().strip() if item[chave] == "OUTRA" else ""
            resultado.append(item)
        return resultado

    def preencher(self, lista):
        """Recria as linhas com os valores informados (pelo menos uma linha, no máximo o limite)."""
        for linha in list(self.linhas):
            for celula, _ in linha["widgets"]:
                self.ateie.esquecer_marcas(celula)
                celula.destroy()
            linha["btn_add"].destroy()
            linha["btn_rem"].destroy()
        self.linhas = []
        for valores in (lista or [{}])[:self.limite]:
            self.adicionar_linha(valores)
        if not self.linhas:
            self.adicionar_linha()

    def entrada(self, numero_linha, chave):
        """Campo da linha (1, 2, 3) indicada ("empresa_outra" = nome digitado em OUTRA), ou None."""
        if 1 <= numero_linha <= len(self.linhas):
            linha = self.linhas[numero_linha - 1]
            if chave in linha["campos"]:
                return linha["campos"][chave]
            if chave.endswith("_outra") and chave[:-6] in linha["outras"]:
                return linha["outras"][chave[:-6]][1]
        return None

    def travar(self, bloquear, fixas=0):
        """bloquear=True trava todas as linhas. Com bloquear=False, as 'fixas' primeiras linhas (já registradas)
        ficam travadas e as demais continuam livres, inclusive para novas linhas."""
        self.bloqueado = bloquear
        self.fixas = 0 if bloquear else fixas
        for posicao, linha in enumerate(self.linhas):
            travada = bloquear or posicao < self.fixas
            for entrada in linha["campos"].values():
                doc_lib_bloquear_widget(entrada, travada)
            for _, outra in linha["outras"].values():
                doc_lib_bloquear_widget(outra, travada)
            for icone in linha["icones"]:
                icone.definir_habilitado(not travada)
        self._reorganizar()


class JanelaAteie:
    """Janela do ATEIE (Doc_Lib. - Click_25): cadastro, edição, salvamento e geração do documento.

    Estados dos botões:
      - janela nova ........ Voltar e Salvar habilitados; Editar e Gerar Documento desabilitados
      - depois de Salvar ... campos travados; Editar e Gerar Documento habilitados; Salvar desabilitado
      - depois de Editar ... campos liberados; Gerar Documento desabilitado até um novo Salvar
    """

    def __init__(self):
        self.ateie_id = None
        self.revisao = None
        self.salvo = False            # versão atual gravada e campos travados (documento ainda não emitido)
        self.emitido = False          # documento já gerado: só as colunas 6 a 13 continuam editáveis
        agora = datetime.now()
        # "Solicitado por" mostra o nome completo do profissional; o user.name (login) vai para o campo
        # "Visto Responsável" do documento
        self.solicitado_por_usuario = obter_nome_usuario_logado()
        self.solicitado_por = obter_nome_completo_usuario(self.solicitado_por_usuario)
        self.data_preenchimento = agora.strftime("%d/%m/%Y")
        self.hora_preenchimento = agora.strftime("%H:%M")
        # por linha: número, status e se os grupos de execução (6 a 9 e 10 a 13) já estão salvos completos (travados)
        self.estado_intervencoes = [{"numero": "", "status": "", "provisorio": False,
                                     "inicio_travado": False, "termino_travado": False}
                                    for _ in range(DOC_LIB_LINHAS_INTERVENCOES)]
        self._doc_gravado = None      # o ATEIE como está gravado no banco (None enquanto for novo)
        self._controles = []          # campos travados/liberados em bloco
        self._alvos = {}              # chave de campo -> (widget com contorno ou None, rótulo)
        self._marcados = {}           # widget -> cores originais do contorno
        self._rotulos_marcados = {}   # rótulo -> cor original
        self.celulas = []
        self.lbl_numero = []
        self.btn_cancelar = []
        self.lbl_status_linha = []
        self.indice_coluna = {chave: posicao for posicao, (chave, _, _, _) in enumerate(DOC_LIB_COLUNAS_INTERVENCAO)}

        self.janela = Toplevel(root)
        self.janela.title('COG - Doc_Lib. - ATEIE')
        self.janela.geometry('1240x820')
        self.janela.minsize(1100, 640)
        self.janela.resizable(True, True)
        self.janela['bg'] = SGA_FUNDO
        self.janela.protocol("WM_DELETE_WINDOW", self.voltar)
        estilo = ttk.Style(self.janela)       # contorno vermelho do Combobox com pendência
        estilo.configure("DocLibErro.TCombobox", bordercolor=SGA_VERMELHO, lightcolor=SGA_VERMELHO,
                         darkcolor=SGA_VERMELHO)
        estilo.map("DocLibErro.TCombobox", bordercolor=[("focus", SGA_VERMELHO), ("active", SGA_VERMELHO)])

        self._montar_cabecalho()
        self._montar_formulario()
        self._montar_rodape()
        self._aplicar_bloqueios()     # documento novo: tudo editável, exceto as colunas 6 a 13 (só depois de gerar)
        self._atualizar_estado()
        self._assinatura_ref = self._assinatura()
        self.janela.after(300, self._avisar_sem_nome_completo)

    def _avisar_sem_nome_completo(self):
        """Usuário sem nome completo cadastrado: "Solicitado por" usará o login até o administrador cadastrar."""
        if self.ateie_id is None and not buscar_nome_completo(self.solicitado_por_usuario):
            messagebox.showwarning(
                "Nome completo não cadastrado",
                f"O usuário '{self.solicitado_por_usuario}' não tem nome completo cadastrado, por isso o campo "
                f"'Solicitado por' mostrará o próprio login.\n\nPeça ao administrador para cadastrar o nome "
                f"(menu ADMIN > Nomes dos Usuários).", parent=self.janela)

    # ------------------------------------------------------------------ montagem da janela
    def _montar_cabecalho(self):
        faixa = ui_dialogo(self.janela, "ATEIE - Doc_Lib.",
                           "Autorização para Trabalhos em Equipamentos de Interligação Energizados")
        doc_lib_criar_botao(faixa, "Abrir ATEIE salvo", self.abrir_salvo, "neutro"
                            ).place(relx=1.0, x=-24, rely=0.5, anchor="e", width=170, height=34)
        self.lbl_status = Label(faixa, text="", bg=SGA_AZUL, fg="#B8CCE8", font=(SGA_FONTE, 9, "bold"))
        self.lbl_status.place(relx=1.0, x=-208, rely=0.5, anchor="e")

    def _montar_formulario(self):
        area = Frame(self.janela, bg=SGA_FUNDO)
        area.place(x=0, y=64, relwidth=1.0, relheight=1.0, height=-(64 + 76))
        self.inner = criar_area_rolavel(area, bg=SGA_FUNDO)
        self.canvas = self.inner.master

        card = Frame(self.inner, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
        card.pack(fill=X, padx=24, pady=(16, 8))
        card.grid_columnconfigure(0, minsize=250)
        card.grid_columnconfigure(1, weight=1)
        self.card = card
        self._linha = 0

        # 1. Classificação dos Trabalhos
        rot = self._rotulo("Classificação dos Trabalhos")
        quadro = Frame(card, bg=SGA_CARD)
        self.var_classificacao = StringVar(value="")
        for texto in DOC_LIB_CLASSIFICACOES_ATEIE:
            # tristatevalue: sem ele o Tk desenha os dois botões "indefinidos" enquanto nada está selecionado
            radio = Radiobutton(quadro, text=texto, variable=self.var_classificacao, value=texto,
                                tristatevalue="-", font=(SGA_FONTE, 10), bg=SGA_CARD)
            radio.pack(side=LEFT, padx=(0, 28))
            self._controles.append(radio)
        self._nova_linha(rot, quadro)
        self._alvos["classificacao"] = (None, rot)

        # 2. Equipamento de Interligação / 4. Local / 5. Serviços / 6. Observações / 7. Documentos
        self.txt_equipamento = self._campo_texto("equipamento", "Equipamento de Interligação", 3, maiusculas=True,
                                                 dica="(não usar siglas)")

        # 3. Empresa Solicitante (+ nome manual quando OUTRA)
        rot = self._rotulo("Empresa Solicitante")
        quadro = Frame(card, bg=SGA_CARD)
        self.cmb_empresa = ttk.Combobox(quadro, values=DOC_LIB_EMPRESAS_SOLICITANTES_ATEIE, state="readonly", width=24,
                                        font=(SGA_FONTE, 10))
        self.cmb_empresa.pack(side=LEFT)
        self.cmb_empresa.bind("<<ComboboxSelected>>", self._ao_mudar_empresa)
        self.cmb_empresa.bind("<MouseWheel>", lambda e: (_rolar_area_sga(e), "break")[1])
        self.lbl_empresa_outra = Label(quadro, text="Nome da empresa:", bg=SGA_CARD, fg=SGA_TEXTO_SUAVE,
                                       font=(SGA_FONTE, 10, "bold"))
        self.ent_empresa_outra = criar_entrada_sga(quadro, width=34)
        self.configurar_entrada(self.ent_empresa_outra, "texto")
        self.forcar_maiusculas(self.ent_empresa_outra)
        self._controles += [self.cmb_empresa, self.ent_empresa_outra]
        self._nova_linha(rot, quadro)
        self._alvos["empresa"] = (self.cmb_empresa, rot)
        self._alvos["empresa_outra"] = (self.ent_empresa_outra, rot)

        self.txt_local = self._campo_texto("local", "Local", 3, maiusculas=True)
        self.txt_servicos = self._campo_texto("servicos", "Serviços a Executar", 6, barra=True)
        self.txt_observacoes = self._campo_texto("observacoes", "Observações", 4, barra=True)
        self._definir_texto(self.txt_observacoes, DOC_LIB_TEXTO_PADRAO_OBSERVACOES)     # obrigatório, já preenchido
        self.txt_documentos = self._campo_texto("documentos_vinculados", "Documentos Internos Vinculados", 2,
                                                opcional=True)

        # 8 a 10. Solicitado por / Data / Hora (preenchidos automaticamente)
        quadro = Frame(card, bg=SGA_CARD)
        self.lbl_solicitante = self._par_automatico(quadro, "Solicitado por:", self.solicitado_por or "-", 26)
        self.lbl_data = self._par_automatico(quadro, "Data:", self.data_preenchimento, 18)
        self.lbl_hora = self._par_automatico(quadro, "Hora:", self.hora_preenchimento, 0)
        quadro.grid(row=self._linha, column=0, columnspan=2, sticky="w", padx=16, pady=10)
        self._alvos["solicitado_por"] = (None, None)
        self._linha += 1
        self._separador()

        # 11/12. De acordo: Pessoas/Áreas notificadas
        Label(card, text="De acordo:", bg=SGA_CARD, fg=SGA_AZUL, font=(SGA_FONTE, 11, "bold"), anchor="w"
              ).grid(row=self._linha, column=0, columnspan=2, sticky="w", padx=16, pady=(10, 0))
        self._linha += 1
        Label(card, text="Pessoas/Áreas notificadas", bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9),
              anchor="w").grid(row=self._linha, column=0, columnspan=2, sticky="w", padx=16)
        self._linha += 1
        bloco = Frame(card, bg=SGA_CARD)
        bloco.grid(row=self._linha, column=0, columnspan=2, sticky="ew", padx=12, pady=(2, 10))
        self.lista_notificacoes = LinhasDinamicasDocLib(self, bloco, DOC_LIB_COLUNAS_NOTIFICACAO,
                                                        DOC_LIB_LIMITE_NOTIFICACOES)
        self._linha += 1
        self._separador()

        # 13. Pessoal Notificado
        Label(card, text="Pessoal Notificado:", bg=SGA_CARD, fg=SGA_AZUL, font=(SGA_FONTE, 11, "bold"),
              anchor="w").grid(row=self._linha, column=0, columnspan=2, sticky="w", padx=16, pady=(10, 0))
        self._linha += 1
        bloco = Frame(card, bg=SGA_CARD)
        bloco.grid(row=self._linha, column=0, columnspan=2, sticky="ew", padx=12, pady=(2, 10))
        self.lista_pessoal = LinhasDinamicasDocLib(self, bloco, DOC_LIB_COLUNAS_PESSOAL, DOC_LIB_LIMITE_PESSOAL,
                                                   DOC_LIB_EMPRESAS_NOTIFICADAS_ATEIE)
        self._linha += 1

        self._montar_tabela()

        # 17. Nota (opcional)
        card_nota = Frame(self.inner, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
        card_nota.pack(fill=X, padx=24, pady=(0, 24))
        card_nota.grid_columnconfigure(0, minsize=250)
        card_nota.grid_columnconfigure(1, weight=1)
        self.card, self._linha = card_nota, 0
        self.txt_nota = self._campo_texto("nota", "Nota", 3, opcional=True, separador=False)

    def _montar_rodape(self):
        rodape = criar_rodape_sga(self.janela)
        self.btn_voltar = doc_lib_criar_botao(rodape, "Voltar", self.voltar, "neutro")
        self.btn_salvar = doc_lib_criar_botao(rodape, "Salvar", self.salvar, "sucesso")
        self.btn_editar = doc_lib_criar_botao(rodape, "Editar", self.editar, "aviso")
        self.btn_gerar = doc_lib_criar_botao(rodape, "Gerar Documento", self.gerar, "primario")
        for posicao, botao in enumerate((self.btn_voltar, self.btn_salvar, self.btn_editar, self.btn_gerar)):
            botao.place(relx=0.5, x=-321 + posicao * 164, rely=0.5, anchor="w", width=150, height=42)

    def _montar_tabela(self):
        """Tabela de intervenções: 13 colunas x 10 linhas. Cada linha é um ATEIE com número, status e
        cancelamento próprios (além das 13 colunas: Status e o botão Cancelar da linha)."""
        quadro = Frame(self.inner, bg=SGA_CARD, highlightthickness=1, highlightbackground=SGA_BORDA)
        quadro.pack(fill=X, padx=24, pady=(0, 8))
        Label(quadro, text="Período dos Serviços - Intervenções (até 10 por documento)", bg=SGA_CARD, fg=SGA_AZUL,
              font=(SGA_FONTE, 11, "bold"), anchor="w").pack(fill=X, padx=16, pady=(12, 0))
        Label(quadro, text="Cada linha uma ATEIE e no máximo 10 ATEIEs por documento.",
              bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9), anchor="w", justify="left", wraplength=1100
              ).pack(fill=X, padx=16, pady=(2, 8))

        tabela = Frame(quadro, bg=SGA_CARD)
        tabela.pack(fill=X, padx=12, pady=(0, 14))
        tabela.grid_columnconfigure(0, minsize=86)
        for coluna in range(1, 13):
            tabela.grid_columnconfigure(coluna, weight=1, uniform="dados")
        tabela.grid_columnconfigure(13, minsize=130)
        tabela.grid_columnconfigure(14, minsize=84)

        cabecalho = dict(bg=SGA_AZUL, fg="white", font=(SGA_FONTE, 9, "bold"))
        subcabecalho = dict(bg="#2F5F9E", fg="white", font=(SGA_FONTE, 9, "bold"))
        rotulo_coluna = dict(bg="#DCE8F8", fg=SGA_TEXTO, font=(SGA_FONTE, 9, "bold"))
        Label(tabela, text="ATEIE\nNº", **cabecalho).grid(row=0, column=0, rowspan=4, sticky="nsew", padx=1, pady=1)
        Label(tabela, text="Período dos Serviços", **cabecalho).grid(row=0, column=1, columnspan=12, sticky="nsew",
                                                                    padx=1, pady=1)
        Label(tabela, text="Previsto", **cabecalho).grid(row=1, column=1, columnspan=4, sticky="nsew", padx=1, pady=1)
        Label(tabela, text="Verificado", **cabecalho).grid(row=1, column=5, columnspan=8, sticky="nsew", padx=1,
                                                          pady=1)
        for texto, coluna, extensao in (("Início", 1, 2), ("Término", 3, 2), ("Início do Serviço", 5, 4),
                                        ("Término do Serviço", 9, 4)):
            Label(tabela, text=texto, **subcabecalho).grid(row=2, column=coluna, columnspan=extensao,
                                                           sticky="nsew", padx=1, pady=1)
        for posicao, (chave, curto, descricao, tipo) in enumerate(DOC_LIB_COLUNAS_INTERVENCAO):
            rotulo = Label(tabela, text=curto, **rotulo_coluna)
            rotulo.grid(row=3, column=posicao + 1, sticky="nsew", padx=1, pady=1)
            ToolTipSGA(rotulo, descricao)
        for coluna, texto in ((13, "Status"), (14, "Cancelar")):
            Label(tabela, text=texto, bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 8, "bold")
                  ).grid(row=3, column=coluna, sticky="nsew")

        for indice in range(DOC_LIB_LINHAS_INTERVENCOES):
            grade = 4 + indice
            numero = Label(tabela, text="", bg=SGA_CARD, fg=SGA_TEXTO, font=(SGA_FONTE, 9, "bold"), width=9)
            numero.grid(row=grade, column=0, sticky="nsew", padx=1, pady=1)
            self.lbl_numero.append(numero)
            entradas = []
            for posicao, (chave, curto, descricao, tipo) in enumerate(DOC_LIB_COLUNAS_INTERVENCAO):
                entrada = Entry(tabela, font=(SGA_FONTE, 9), justify="center", width=1)
                entrada.configure(readonlybackground=DOC_LIB_COR_BLOQUEADO)
                entrada.grid(row=grade, column=posicao + 1, sticky="ew", padx=1, pady=1, ipady=2)
                self.configurar_entrada(entrada, tipo, ano_curto=True,
                                        atualiza_numeracao=chave in DOC_LIB_CAMPOS_PROGRAMADOS,
                                        atualiza_estado=chave in DOC_LIB_CAMPOS_EXECUCAO)
                if tipo == "data":
                    entrada.bind("<Double-Button-1>", lambda e, w=entrada: self.abrir_calendario(w, True))
                    ToolTipSGA(entrada, "Dê duplo clique para abrir o calendário")
                entradas.append(entrada)
            self.celulas.append(entradas)
            situacao = Label(tabela, text="", bg=SGA_CARD, fg=SGA_TEXTO, font=(SGA_FONTE, 8, "bold"),
                             wraplength=124, justify="center")
            situacao.grid(row=grade, column=13, sticky="nsew")
            self.lbl_status_linha.append(situacao)
            botao = doc_lib_criar_botao(tabela, "Cancelar", lambda i=indice: self.cancelar_intervencao(i), "perigo",
                                        fonte=(SGA_FONTE, 8, "bold"))
            botao.grid(row=grade, column=14, sticky="ew", padx=(4, 1), pady=1)
            self.btn_cancelar.append(botao)
            doc_lib_estado_botao(botao, False)

    # ------------------------------------------------------------------ construção de linhas do formulário
    def _rotulo(self, texto, opcional=False, pai=None):
        return Label(pai or self.card, text=texto + (" (opcional)" if opcional else ""), bg=SGA_CARD,
                     fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 10, "bold"), anchor="nw", justify="left", wraplength=225)

    def _nova_linha(self, rotulo, conteudo, separador=True):
        rotulo.grid(row=self._linha, column=0, sticky="nw", padx=(16, 8), pady=(12, 8))
        conteudo.grid(row=self._linha, column=1, sticky="ew", padx=(0, 16), pady=(8, 8))
        self._linha += 1
        if separador:
            self._separador()

    def _separador(self):
        Frame(self.card, bg="#E5EAF1", height=1).grid(row=self._linha, column=0, columnspan=2, sticky="ew")
        self._linha += 1

    @staticmethod
    def forcar_maiusculas(widget):
        """O que for digitado ou colado no campo passa para caixa alta na hora (o cursor não sai do lugar)."""
        def converter(evento=None):
            try:
                if str(widget.cget("state")) != "normal":
                    return
                texto = widget.winfo_class() == "Text"
                atual = widget.get("1.0", "end-1c") if texto else widget.get()
                novo = atual.upper()
                if novo == atual:
                    return
                posicao = widget.index(INSERT)
                if texto:
                    widget.delete("1.0", END)
                    widget.insert("1.0", novo)
                    widget.mark_set(INSERT, posicao)
                else:
                    widget.delete(0, END)
                    widget.insert(0, novo)
                    widget.icursor(posicao)
            except TclError:
                pass
        widget.bind("<KeyRelease>", converter, add="+")
        widget.bind("<<Paste>>", lambda e: widget.after_idle(converter), add="+")

    def _campo_texto(self, chave, nome, linhas, barra=False, opcional=False, separador=True, maiusculas=False,
                     dica=None):
        """Linha com rótulo + campo de texto livre de várias linhas (maiusculas: converte a digitação para caixa
        alta; dica: orientação em fonte 9, sob o nome do campo)."""
        bloco = None
        if dica:
            bloco = Frame(self.card, bg=SGA_CARD)
            rotulo = self._rotulo(nome, opcional, pai=bloco)
            rotulo.pack(anchor="nw")
            Label(bloco, text=dica, bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9), anchor="w",
                  justify="left").pack(anchor="nw", pady=(2, 0))
        else:
            rotulo = self._rotulo(nome, opcional)
        quadro = Frame(self.card, bg=SGA_CARD)
        texto = criar_area_texto_sga(quadro, wrap=WORD, height=linhas)
        if barra:
            rolagem = Scrollbar(quadro, orient=VERTICAL, command=texto.yview)
            texto.configure(yscrollcommand=rolagem.set)
            rolagem.pack(side=RIGHT, fill=Y)
        texto.pack(side=LEFT, fill=BOTH, expand=True)
        texto.bind("<Tab>", lambda e: (e.widget.tk_focusNext().focus_set(), "break")[1])
        try:
            texto.bind("<Shift-Tab>", lambda e: (e.widget.tk_focusPrev().focus_set(), "break")[1])
            texto.bind("<ISO_Left_Tab>", lambda e: (e.widget.tk_focusPrev().focus_set(), "break")[1])
        except TclError:
            pass
        texto.bind("<MouseWheel>", self._roda_texto)
        texto.bind("<Key>", lambda e, w=texto: self._limpar_marca(w), add="+")
        texto.bind("<FocusOut>", lambda e, w=texto: self._limpar_marca(w) if self._texto(w) else None, add="+")
        if maiusculas:
            self.forcar_maiusculas(texto)
        self._controles.append(texto)
        self._alvos[chave] = (texto, rotulo)
        self._nova_linha(bloco or rotulo, quadro, separador)
        return texto

    def _par_automatico(self, pai, titulo, valor, espaco):
        Label(pai, text=titulo, bg=SGA_CARD, fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 10, "bold")).pack(side=LEFT)
        valor_label = Label(pai, text=valor, bg=SGA_CARD, fg=SGA_TEXTO, font=(SGA_FONTE, 10, "bold"))
        valor_label.pack(side=LEFT, padx=(6, espaco))
        return valor_label

    def _roda_texto(self, evento):
        """Roda do mouse sobre um texto: rola o próprio texto só se ele tiver o que rolar; senão,
        quem rola é a janela."""
        inicio, fim = evento.widget.yview()
        if inicio <= 0.0 and fim >= 1.0:
            return None
        evento.widget.yview_scroll(int(-1 * (evento.delta / 120)), "units")
        return "break"

    # ------------------------------------------------------------------ campos de data/hora e marcação de erros
    def configurar_entrada(self, entrada, tipo, ano_curto=False, atualiza_numeracao=False, atualiza_estado=False):
        """Liga ao campo a formatação automática (data dd/mm/aa(aa), hora HH:MM) e a limpeza da marca de erro.
        atualiza_estado: depois da emissão, alterar o campo deixa o documento com alterações a salvar."""
        entrada.configure(readonlybackground=DOC_LIB_COR_BLOQUEADO)
        if tipo in ("data", "hora"):
            entrada.bind("<FocusOut>", lambda e, w=entrada: self._ao_sair_campo(w, tipo, ano_curto, atualiza_numeracao),
                         add="+")
        entrada.bind("<Key>", lambda e, w=entrada: self._limpar_marca(w), add="+")
        if tipo not in ("data", "hora"):
            entrada.bind("<FocusOut>", lambda e, w=entrada: self._limpar_marca(w) if w.get().strip() else None,
                         add="+")
        if atualiza_estado:
            entrada.bind("<KeyRelease>", lambda e: self._ao_alterar_execucao(), add="+")
            entrada.bind("<FocusOut>", lambda e: self._ao_alterar_execucao(), add="+")

    def _ao_sair_campo(self, entrada, tipo, ano_curto, atualiza_numeracao):
        try:
            if str(entrada.cget("state")) != "normal":
                return
            texto = entrada.get().strip()
            if texto:
                novo = doc_lib_normalizar_data(texto, ano_curto) if tipo == "data" else doc_lib_normalizar_hora(texto)
                if novo:
                    self._limpar_marca(entrada)
                    if novo != entrada.get():
                        entrada.delete(0, END)
                        entrada.insert(0, novo)
                else:
                    self._marcar(entrada)         # formato inválido: destaca já, sem esperar o Salvar
        except TclError:
            return
        if atualiza_numeracao:
            self._atualizar_numeracao_provisoria()

    def abrir_calendario(self, entrada, ano_curto):
        self._limpar_marca(entrada)
        doc_lib_selecionar_data(self.janela, entrada, ano_curto, lambda: self._apos_escolher_data(entrada))

    def _apos_escolher_data(self, entrada):
        if entrada in self._celulas_programadas():
            self._atualizar_numeracao_provisoria()
        self._ao_alterar_execucao()

    def _ao_alterar_execucao(self):
        """Depois da emissão, alterar as colunas 6 a 13 deixa o documento com alterações ainda não salvas
        (Salvar habilita e Gerar Documento desabilita até salvar)."""
        if self.emitido:
            try:
                self._atualizar_estado()
            except TclError:
                pass

    def _celulas_programadas(self):
        indices = [self.indice_coluna[chave] for chave in DOC_LIB_CAMPOS_PROGRAMADOS]
        return [linha[indice] for linha in self.celulas for indice in indices]

    def _marcar(self, widget, rotulo=None):
        """Destaca em vermelho um campo (contorno) e/ou seu rótulo."""
        if widget is not None and widget not in self._marcados:
            classe = widget.winfo_class()
            if classe in ("Entry", "Text"):
                self._marcados[widget] = {"highlightbackground": str(widget.cget("highlightbackground")),
                                          "highlightcolor": str(widget.cget("highlightcolor"))}
            elif classe == "TCombobox":
                self._marcados[widget] = {"style": str(widget.cget("style"))}
        if widget is not None and widget in self._marcados:
            if widget.winfo_class() == "TCombobox":
                widget.configure(style="DocLibErro.TCombobox")
            else:
                widget.configure(highlightbackground=SGA_VERMELHO, highlightcolor=SGA_VERMELHO)
        if rotulo is not None and rotulo not in self._rotulos_marcados:
            self._rotulos_marcados[rotulo] = str(rotulo.cget("fg"))
            rotulo.configure(fg=SGA_VERMELHO)

    def _limpar_marca(self, widget):
        original = self._marcados.pop(widget, None)
        if original:
            try:
                widget.configure(**original)
            except TclError:
                pass

    def esquecer_marcas(self, widget):
        """Chamado antes de destruir um campo que pode estar marcado."""
        self._marcados.pop(widget, None)
        for filho in widget.winfo_children():
            self._marcados.pop(filho, None)

    def _limpar_erros(self):
        for widget in list(self._marcados):
            self._limpar_marca(widget)
        for rotulo, cor in list(self._rotulos_marcados.items()):
            try:
                rotulo.configure(fg=cor)
            except TclError:
                pass
        self._rotulos_marcados.clear()

    def _alvo_da_chave(self, chave):
        """(widget, rótulo) do campo identificado pela chave devolvida pela validação."""
        partes = chave.split(":")
        if partes[0] in ("notif", "pessoal"):
            lista = self.lista_notificacoes if partes[0] == "notif" else self.lista_pessoal
            return lista.entrada(int(partes[1]), partes[2]), None
        if partes[0] == "interv":
            return self.celulas[int(partes[1]) - 1][self.indice_coluna[partes[2]]], None
        return self._alvos.get(chave, (None, None))

    def rolar_ate(self, widget):
        """Rola a janela até deixar o campo visível."""
        try:
            self.janela.update_idletasks()
            y = 0
            atual = widget
            while atual is not None and atual is not self.inner:
                y += atual.winfo_y()
                atual = atual.master
            total = max(self.inner.winfo_height(), 1)
            self.canvas.yview_moveto(max(0.0, (y - 120) / total))
        except TclError:
            pass

    def _mostrar_erros(self, erros):
        """Informa os campos pendentes (mensagem objetiva), destaca-os em vermelho e leva o usuário ao primeiro."""
        primeiro = None
        for chaves, _ in erros:
            for chave in chaves:
                widget, rotulo = self._alvo_da_chave(chave)
                self._marcar(widget, rotulo)
                if primeiro is None:
                    primeiro = widget if widget is not None else rotulo
        linhas = ["Existem campos obrigatórios não preenchidos ou incorretos.",
                  "Os campos marcados em vermelho precisam ser corrigidos:", ""]
        linhas += [f"• {mensagem}" for _, mensagem in erros[:14]]
        if len(erros) > 14:
            linhas.append(f"... e mais {len(erros) - 14} pendência(s).")
        messagebox.showwarning("Campos obrigatórios", "\n".join(linhas), parent=self.janela)
        if primeiro is not None:
            self.rolar_ate(primeiro)
            if primeiro.winfo_class() in ("Entry", "Text", "TCombobox"):
                primeiro.focus_set()

    # ------------------------------------------------------------------ empresa / numeração
    def _ao_mudar_empresa(self, evento=None):
        self._limpar_marca(self.cmb_empresa)
        if self.cmb_empresa.get() == "OUTRA":
            self.lbl_empresa_outra.pack(side=LEFT, padx=(18, 6))
            self.ent_empresa_outra.pack(side=LEFT)
            if evento is not None:
                self.ent_empresa_outra.focus_set()
        else:
            self.lbl_empresa_outra.pack_forget()
            self.ent_empresa_outra.pack_forget()
            doc_lib_definir_entrada(self.ent_empresa_outra, "")
            self._limpar_marca(self.ent_empresa_outra)

    def _linha_programada_valida(self, indice):
        valores = {chave: self.celulas[indice][self.indice_coluna[chave]].get().strip()
                   for chave in DOC_LIB_CAMPOS_PROGRAMADOS}
        return bool(doc_lib_normalizar_data(valores["prev_data_inicio"]) and doc_lib_normalizar_hora(
            valores["prev_hora_inicio"]) and doc_lib_normalizar_data(valores["prev_data_termino"])
                    and doc_lib_normalizar_hora(valores["prev_hora_termino"]))

    def _atualizar_numeracao_provisoria(self):
        """Mostra em cada linha com os 4 campos programados preenchidos o número que ela vai receber.
        O número só é de fato consumido ao salvar; linhas incompletas não recebem número."""
        pendentes = []
        for indice, estado in enumerate(self.estado_intervencoes):
            if estado["status"] == STATUS_ATEIE_CANCELADO or (estado["numero"] and not estado["provisorio"]):
                continue
            if self._linha_programada_valida(indice):
                pendentes.append(indice)
            else:
                estado["numero"], estado["provisorio"] = "", False
        try:
            previstos = doc_lib_numeros_previstos(len(pendentes)) if pendentes else []
        except sqlite3.Error:
            previstos = [""] * len(pendentes)
        for indice, numero in zip(pendentes, previstos):
            self.estado_intervencoes[indice]["numero"] = numero
            self.estado_intervencoes[indice]["provisorio"] = bool(numero)
        self._desenhar_numeros()

    def _desenhar_numeros(self):
        """Mostra, em cada linha, o número do ATEIE (cinza e itálico = ainda não consumido) e o seu status."""
        for indice, estado in enumerate(self.estado_intervencoes):
            rotulo = self.lbl_numero[indice]
            if estado["status"] == STATUS_ATEIE_CANCELADO:
                rotulo.configure(text=estado["numero"], fg=SGA_VERMELHO, font=(SGA_FONTE, 9, "bold overstrike"))
            elif estado["provisorio"]:
                rotulo.configure(text=estado["numero"], fg=SGA_TEXTO_SUAVE, font=(SGA_FONTE, 9, "italic"))
            else:
                rotulo.configure(text=estado["numero"], fg=SGA_TEXTO, font=(SGA_FONTE, 9, "bold"))
            situacao = estado["status"] if estado["numero"] and not estado["provisorio"] else ""
            self.lbl_status_linha[indice].configure(text=situacao, fg=DOC_LIB_COR_STATUS.get(situacao, SGA_TEXTO))
        self._atualizar_botoes_cancelar()

    def _atualizar_botoes_cancelar(self):
        """Cancelar só vale para ATEIE já numerado e ainda cancelável (Em análise, Aguarda De Acordo ou Aprovado para Execução), com
        o documento sem alterações pendentes."""
        permitido = self.ateie_id is not None and not self._pendente()
        for indice, estado in enumerate(self.estado_intervencoes):
            botao = self.btn_cancelar[indice]
            if estado["status"] == STATUS_ATEIE_CANCELADO:
                botao.grid_remove()
                continue
            botao.grid()
            numerada = bool(estado["numero"]) and not estado["provisorio"]
            doc_lib_estado_botao(botao, permitido and numerada and estado["status"] in DOC_LIB_STATUS_CANCELAVEIS)

    # ------------------------------------------------------------------ leitura e gravação dos campos
    @staticmethod
    def _texto(widget):
        return widget.get("1.0", "end-1c").strip()

    @staticmethod
    def _definir_texto(widget, valor):
        estado = str(widget.cget("state"))
        widget.configure(state=NORMAL)
        widget.delete("1.0", END)
        widget.insert("1.0", valor or "")
        widget.configure(state=estado)

    def _coletar(self):
        """Todos os dados da tela (como digitados, sem normalizar)."""
        intervencoes = []
        for indice in range(DOC_LIB_LINHAS_INTERVENCOES):
            estado = self.estado_intervencoes[indice]
            item = {"ordem": indice + 1,
                    "numero": "" if estado["provisorio"] else estado["numero"],
                    "status": estado["status"]}
            for posicao, (chave, _, _, _) in enumerate(DOC_LIB_COLUNAS_INTERVENCAO):
                item[chave] = self.celulas[indice][posicao].get().strip()
            intervencoes.append(item)
        empresa = self.cmb_empresa.get().strip()
        return {
            "id": self.ateie_id, "revisao": self.revisao,
            "classificacao": self.var_classificacao.get(),
            "equipamento": self._texto(self.txt_equipamento),
            "empresa": empresa,
            "empresa_outra": self.ent_empresa_outra.get().strip() if empresa == "OUTRA" else "",
            "local": self._texto(self.txt_local),
            "servicos": self._texto(self.txt_servicos),
            "observacoes": self._texto(self.txt_observacoes),
            "documentos_vinculados": self._texto(self.txt_documentos),
            "nota": self._texto(self.txt_nota),
            "solicitado_por": self.solicitado_por or "",
            "solicitado_por_usuario": self.solicitado_por_usuario or "",
            "data_preenchimento": self.data_preenchimento,
            "hora_preenchimento": self.hora_preenchimento,
            "notificacoes": self.lista_notificacoes.coletar(),
            "pessoal": self.lista_pessoal.coletar(),
            "intervencoes": intervencoes,
        }

    def _assinatura(self):
        return json.dumps(self._coletar(), sort_keys=True, ensure_ascii=False)

    def _preencher(self, doc):
        """Mostra na tela um ATEIE gravado no banco."""
        self._limpar_erros()
        self.ateie_id, self.revisao = doc["id"], doc["revisao"]
        self.solicitado_por = doc["solicitado_por"]
        self.solicitado_por_usuario = doc.get("solicitado_por_usuario") or doc["solicitado_por"]
        self.data_preenchimento, self.hora_preenchimento = doc["data_preenchimento"], doc["hora_preenchimento"]
        self.lbl_solicitante.configure(text=self.solicitado_por)
        self.lbl_data.configure(text=self.data_preenchimento)
        self.lbl_hora.configure(text=self.hora_preenchimento)
        self.var_classificacao.set(doc["classificacao"])
        for widget, chave in ((self.txt_equipamento, "equipamento"), (self.txt_local, "local"),
                              (self.txt_servicos, "servicos"), (self.txt_observacoes, "observacoes"),
                              (self.txt_documentos, "documentos_vinculados"), (self.txt_nota, "nota")):
            valor = doc.get(chave)
            self._definir_texto(widget, (valor or "").upper() if chave in DOC_LIB_CAMPOS_CAIXA_ALTA else valor)
        estado_combo = str(self.cmb_empresa.cget("state"))
        self.cmb_empresa.configure(state="readonly")
        self.cmb_empresa.set(doc["empresa"])
        self.cmb_empresa.configure(state=estado_combo)
        doc_lib_definir_entrada(self.ent_empresa_outra, (doc.get("empresa_outra") or "").upper())
        self._ao_mudar_empresa()
        self.lista_notificacoes.preencher(doc["notificacoes"])
        self.lista_pessoal.preencher(doc["pessoal"])
        por_ordem = {item["ordem"]: item for item in doc["intervencoes"]}
        for indice in range(DOC_LIB_LINHAS_INTERVENCOES):
            item = por_ordem.get(indice + 1)
            for posicao, (chave, _, _, _) in enumerate(DOC_LIB_COLUNAS_INTERVENCAO):
                doc_lib_definir_entrada(self.celulas[indice][posicao], (item or {}).get(chave) or "")
            self.estado_intervencoes[indice] = {
                "numero": item["numero"] if item else "", "status": item["status"] if item else "",
                "provisorio": False,
                "inicio_travado": bool(item) and all(str(item.get(c) or "").strip() for c in DOC_LIB_CAMPOS_INICIO),
                "termino_travado": bool(item) and all(str(item.get(c) or "").strip() for c in DOC_LIB_CAMPOS_TERMINO)}
        self._desenhar_numeros()

    def _carregar_documento(self, doc):
        """Mostra o ATEIE gravado: travado (versão salva) e, se já foi gerado, no estado EMITIDO (somente as colunas
        6 a 13 editáveis)."""
        self._preencher(doc)
        self._doc_gravado = doc
        self.emitido = bool(doc.get("emitido"))
        self.salvo = True
        self._aplicar_bloqueios()
        self._assinatura_ref = self._assinatura()
        self._atualizar_estado()

    # ------------------------------------------------------------------ estados
    def _aplicar_bloqueios(self):
        """Libera/trava cada campo conforme o estado do documento:
          - novo ou em edição ........ tudo editável (menos as colunas 6 a 13)
          - salvo (travado) .......... nada editável (Editar libera)
          - EMITIDO (já gerado) ...... dados gerais e colunas 1 a 5 travados para sempre. O "De acordo" continua
                                       aberto para novas linhas (as já registradas não mudam). As colunas 6 a 13
                                       só são liberadas depois que o "De acordo" está preenchido e SALVO; a partir
                                       daí ficam editáveis nos ATEIE numerados e não cancelados, até que o grupo
                                       de início (6 a 9) ou de término (10 a 13) esteja preenchido E salvo (esse
                                       grupo deixa de mudar)
        As colunas 6 a 13 só existem depois da emissão (antes dela ficam travadas).
        Linha de ATEIE cancelado nunca é editada."""
        geral = self.emitido or self.salvo
        gravado = self._doc_gravado or {}
        de_acordo_ok = doc_lib_de_acordo_completo(gravado.get("notificacoes"))
        for widget in self._controles:
            doc_lib_bloquear_widget(widget, geral)
        if self.emitido:
            self.lista_notificacoes.travar(False, fixas=len(gravado.get("notificacoes") or []))
        else:
            self.lista_notificacoes.travar(self.salvo)
        self.lista_pessoal.travar(geral)
        quantidade_programadas = len(DOC_LIB_CAMPOS_PROGRAMADOS)
        for indice, entradas in enumerate(self.celulas):
            estado = self.estado_intervencoes[indice]
            cancelada = estado["status"] == STATUS_ATEIE_CANCELADO
            numerada = bool(estado["numero"]) and not estado["provisorio"]
            for posicao, entrada in enumerate(entradas):
                if posicao < quantidade_programadas:                 # colunas 2 a 5
                    bloquear = geral or cancelada
                elif not self.emitido:                               # colunas 6 a 13: só depois de emitido
                    bloquear = True
                else:
                    grupo_salvo = estado["inicio_travado"] if posicao < quantidade_programadas + 4 \
                        else estado["termino_travado"]
                    bloquear = cancelada or not numerada or not de_acordo_ok or grupo_salvo
                doc_lib_bloquear_widget(entrada, bloquear)

    def _pendente(self):
        """True se existem dados ainda não salvos (documento novo, em edição ou, depois de emitido, com alteração
        nas colunas 6 a 13)."""
        if self.ateie_id is None:
            return True
        if self.emitido:
            return self._assinatura() != self._assinatura_ref
        return not self.salvo

    def _atualizar_estado(self):
        pendente = self._pendente()
        doc_lib_estado_botao(self.btn_voltar, True)
        doc_lib_estado_botao(self.btn_salvar, pendente)
        doc_lib_estado_botao(self.btn_editar, self.ateie_id is not None and not self.emitido and self.salvo)
        doc_lib_estado_botao(self.btn_gerar, self.ateie_id is not None and not pendente)
        if self.ateie_id is None:
            texto = "Novo documento (não salvo)"
        elif self.emitido:
            texto = f"ATEIE ID {self.ateie_id} - emitido (rev. {self.revisao})" \
                    + (" - alterações não salvas" if pendente else "")
        elif self.salvo:
            texto = f"ATEIE ID {self.ateie_id} - salvo (rev. {self.revisao})"
        else:
            texto = f"ATEIE ID {self.ateie_id} - em edição"
        self.lbl_status.configure(text=texto)
        self._atualizar_botoes_cancelar()

    # ------------------------------------------------------------------ ações dos botões
    def salvar(self):
        self._limpar_erros()
        dados = doc_lib_normalizar_ateie(self._coletar())
        erros = doc_lib_validar_ateie(dados, self._doc_gravado)
        if erros:
            self._mostrar_erros(erros)
            return
        usuario = obter_nome_usuario_logado()
        de_acordo_antes = doc_lib_de_acordo_completo((self._doc_gravado or {}).get("notificacoes"))
        travas_antes = {i: (e["inicio_travado"], e["termino_travado"]) for i, e in enumerate(self.estado_intervencoes)}
        provisorios = {i: e["numero"] for i, e in enumerate(self.estado_intervencoes) if e["provisorio"]}
        status_antes = {i: e["status"] for i, e in enumerate(self.estado_intervencoes) if e["numero"]}
        ja_emitido = self.emitido
        try:
            ateie_id = doc_lib_salvar_ateie(dados, usuario)
        except DocLibConflito as erro:
            messagebox.showwarning("Documento alterado", str(erro), parent=self.janela)
            return
        except DocLibBloqueado as erro:
            messagebox.showwarning("Alteração não permitida", str(erro), parent=self.janela)
            return
        except DocLibRegra as erro:
            messagebox.showwarning("Regra do ATEIE", str(erro), parent=self.janela)
            return
        except (sqlite3.Error, OSError) as erro:
            messagebox.showerror("Erro", f"Não foi possível salvar o ATEIE: {erro}", parent=self.janela)
            return
        doc = doc_lib_carregar_ateie(ateie_id)
        self._carregar_documento(doc)

        if ja_emitido:
            mensagem = "ATEIE atualizado com sucesso!"
            if not de_acordo_antes and doc_lib_de_acordo_completo(doc["notificacoes"]):
                mensagem += ("\n\n'De acordo' registrado: as colunas 6 a 13 foram liberadas para digitação "
                             "(execução).\n\nGere o documento novamente: o novo PDF não traz mais a linha vermelha "
                             "nem o aviso 'Aguardando o De Acordo do documento'.")
            mudancas = [f"{self.estado_intervencoes[i]['numero']}: {status_antes[i]} passou a "
                        f"{self.estado_intervencoes[i]['status']}" for i in status_antes
                        if self.estado_intervencoes[i]["status"] != status_antes[i]]
            if mudancas:
                mensagem += "\n\nStatus atualizado:\n" + "\n".join(mudancas)
            travados = []
            for i, estado in enumerate(self.estado_intervencoes):
                if estado["inicio_travado"] and not travas_antes[i][0]:
                    travados.append(f"{estado['numero']}: início efetivo (colunas 6 a 9)")
                if estado["termino_travado"] and not travas_antes[i][1]:
                    travados.append(f"{estado['numero']}: término efetivo (colunas 10 a 13)")
            if travados:
                mensagem += "\n\nRegistrados e bloqueados (não podem mais ser alterados):\n" + "\n".join(travados)
        else:
            numeros = ", ".join(item["numero"] for item in doc["intervencoes"] if item.get("numero"))
            mensagem = f"ATEIE salvo com sucesso!\n\nIntervenção(ões): {numeros}\nStatus: {STATUS_ATEIE_EM_ANALISE}"
            trocados = [f"{provisorios[i]} passou a {self.estado_intervencoes[i]['numero']}" for i in provisorios
                        if self.estado_intervencoes[i]["numero"] != provisorios[i]]
            if trocados:
                mensagem += ("\n\nA numeração foi atualizada porque outro usuário emitiu números enquanto este "
                             "documento era preenchido: " + "; ".join(trocados) + ".")
            mensagem += "\n\nUse 'Gerar Documento' para emitir o PDF."
        messagebox.showinfo("Sucesso", mensagem, parent=self.janela)

    def editar(self):
        if not self.salvo or self.emitido:
            return
        self.salvo = False
        self._aplicar_bloqueios()
        self._atualizar_numeracao_provisoria()
        self._assinatura_ref = self._assinatura()
        self._atualizar_estado()

    def gerar(self):
        """Gera o PDF a partir da versão salva (revalida antes), arquiva e oferece abrir/imprimir. A primeira
        geração EMITE o ATEIE: status "Aguarda De Acordo" e proteção dos dados (só as colunas 6 a 13 seguem editáveis)."""
        if self.ateie_id is None or self._pendente():
            messagebox.showwarning("Atenção", "Salve o ATEIE antes de gerar o documento.", parent=self.janela)
            return
        try:
            doc = doc_lib_carregar_ateie(self.ateie_id)
        except sqlite3.Error as erro:
            messagebox.showerror("Erro", f"Não foi possível ler o ATEIE salvo: {erro}", parent=self.janela)
            return
        if doc is None or doc["revisao"] != self.revisao:
            messagebox.showwarning("Documento alterado",
                                   "Este ATEIE foi alterado por outro usuário depois de aberto nesta janela.\n\n"
                                   "Feche-o e abra-o novamente (Abrir ATEIE salvo) antes de gerar o documento.",
                                   parent=self.janela)
            return
        erros = doc_lib_validar_ateie(doc, doc)
        if erros:
            messagebox.showwarning("Campos obrigatórios",
                                   "O documento salvo possui pendências e não pode ser gerado:\n\n"
                                   + "\n".join(f"• {mensagem}" for _, mensagem in erros[:14]), parent=self.janela)
            return
        if not self.emitido and not messagebox.askyesno(
                "Emitir ATEIE",
                "Ao gerar o documento o ATEIE será considerado EMITIDO (status 'Aguarda De Acordo').\n\n"
                "A partir daí os dados gerais e as colunas 1 a 5 da tabela não poderão mais ser alterados; "
                "somente as colunas 6 a 13 (execução e normalização) continuarão editáveis.\n\n"
                "Deseja gerar o documento?", parent=self.janela):
            return
        try:
            caminho, aviso = doc_lib_arquivar_pdf_ateie(doc, obter_nome_usuario_logado())
        except DocLibConflito as erro:
            messagebox.showwarning("Documento alterado", str(erro), parent=self.janela)
            return
        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao gerar/arquivar o documento ATEIE: {erro}", parent=self.janela)
            return
        doc = doc_lib_carregar_ateie(self.ateie_id)
        self._carregar_documento(doc)
        lembrete = None
        if any(item.get("status") == STATUS_ATEIE_AGUARDA_DE_ACORDO for item in doc["intervencoes"]):
            lembrete = ("Status: Aguarda De Acordo. O PDF traz uma linha vermelha nas colunas 6 a 13 e o aviso "
                        "'Aguardando o De Acordo do documento'. Preencha e salve o 'De acordo' e gere o documento "
                        "novamente: a marca sai e as colunas 6 a 13 são liberadas para a execução.")
        doc_lib_dialogo_documento_gerado(self.janela, caminho, aviso, lembrete)

    def cancelar_intervencao(self, indice):
        """Cancela somente o ATEIE da linha; os demais ATEIE do documento mantêm o seu status."""
        estado = self.estado_intervencoes[indice]
        if self._pendente() or not estado["numero"] or estado["provisorio"] \
                or estado["status"] not in DOC_LIB_STATUS_CANCELAVEIS:
            return
        numero = estado["numero"]
        if not messagebox.askyesno(
                "Confirmar cancelamento",
                f"Deseja realmente cancelar somente o ATEIE {numero}?\n\n"
                f"Os demais ATEIE deste documento não são afetados. O número {numero} fica registrado "
                f"como cancelado e não será reaproveitado.", parent=self.janela):
            return
        justificativa = solicitar_justificativa(self.janela, numero, rotulo="ATEIE")
        if justificativa is None:
            return
        try:
            doc_lib_cancelar_intervencao(self.ateie_id, indice + 1, obter_nome_usuario_logado(), justificativa,
                                         self.revisao)
        except DocLibConflito as erro:
            messagebox.showwarning("Documento alterado", str(erro), parent=self.janela)
            return
        except (ValueError, sqlite3.Error) as erro:
            messagebox.showerror("Erro", f"Não foi possível cancelar o ATEIE: {erro}", parent=self.janela)
            return
        self._carregar_documento(doc_lib_carregar_ateie(self.ateie_id))
        messagebox.showinfo("ATEIE cancelado",
                            f"O ATEIE {numero} foi cancelado. Os demais continuam com o status que tinham.\n\n"
                            f"Gere o documento novamente para que o PDF mostre o cancelamento.", parent=self.janela)

    def _tem_alteracoes_pendentes(self):
        return self._assinatura() != self._assinatura_ref

    def abrir_salvo(self):
        if self._tem_alteracoes_pendentes() and not messagebox.askyesno(
                "Dados não salvos", "Existem dados não salvos neste ATEIE. Abrir outro documento descarta essas "
                                    "alterações.\n\nDeseja continuar?", parent=self.janela):
            return
        try:
            escolha = doc_lib_escolher_ateie(self.janela)
            doc = doc_lib_carregar_ateie(escolha[0]) if escolha else None
        except sqlite3.Error as erro:
            messagebox.showerror("Erro", f"Não foi possível ler os ATEIE salvos: {erro}", parent=self.janela)
            return
        if escolha is None:
            return
        if doc is None:
            messagebox.showerror("Erro", "O ATEIE selecionado não foi encontrado.", parent=self.janela)
            return
        self._carregar_documento(doc)
        self.rolar_ate(self.lbl_numero[escolha[1] - 1])

    def voltar(self):
        if self._tem_alteracoes_pendentes() and not messagebox.askyesno(
                "Dados não salvos", "Existem dados não salvos neste ATEIE.\n\nDeseja sair mesmo assim?",
                parent=self.janela):
            return
        self.janela.destroy()


# ---------------------------------------------------
# JANELAS DO MENU Doc_Lib. (CLICK_25)
# ---------------------------------------------------
def cmd_click25_ateie():
    """Doc_Lib. > ATEIE: cadastro, edição, salvamento e geração do documento ATEIE."""
    if not current_user:
        messagebox.showwarning("Atenção", "Nenhum usuário está logado. Faça login primeiro.")
        return
    if not obter_nome_usuario_logado():
        messagebox.showwarning("Atenção", "Não foi possível identificar o usuário logado.")
        return
    try:
        garantir_banco_doc_lib()
    except sqlite3.Error as erro:
        messagebox.showerror("Erro", f"Não foi possível preparar o banco de dados do Doc_Lib.: {erro}")
        return
    JanelaAteie()


def doc_lib_pagina_em_construcao(nome_modulo):
    messagebox.showinfo(f"Doc_Lib. - {nome_modulo}", "Página em Construção")


def cmd_click25_ai():
    doc_lib_pagina_em_construcao("AI")


def cmd_click25_mo():
    doc_lib_pagina_em_construcao("MO")


def cmd_click25_sm_avulso():
    doc_lib_pagina_em_construcao("SM_Avulso")

# =======cascate PRIMEIRA PARTE termina aqui


# ---------------------------------------------------
# FUNÇÕES RELACIONADAS AO LOGIN
# ---------------------------------------------------
def realizar_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    atual = datetime.now().strftime(f" %d/%m/%Y - %H:%Mh")

    conexao = sqlite3.connect('dados_turno.db')
    cursor = conexao.cursor()

    # Certifique-se de que a consulta retorna todos os campos
    cursor.execute("SELECT id, usuario, senha, admin, primeiro_acesso FROM Usuarios WHERE usuario = ? AND senha = ?",
                   (usuario, senha))
    resultado = cursor.fetchone()

    if resultado:
        global logged_in, current_user
        logged_in = True
        current_user = f"{usuario} em {atual}"  # Armazena o nome de quem logou

        # Verifica se é o primeiro acesso
        if resultado[4] == 1:  # primeiro_acesso = 1
            messagebox.showinfo("Primeiro Acesso", "Você precisa alterar sua senha.")
            trocar_senha(usuario)  # Abre a janela para trocar a senha
        else:
            messagebox.showinfo("Login", "Login realizado com sucesso!")
            login_window.destroy()
            root.deiconify()  # Mostra a janela principal
            root.after(300, lambda: exibir_lembretes_sga_do_usuario(usuario))  # lembretes do SGA (Click_24)
    else:
        messagebox.showerror("Erro", "Usuário ou senha inválidos.")
        entry_senha.delete(0, END)

    conexao.close()


def trocar_senha(usuario):
    def salvar_nova_senha():
        nova_senha = entry_nova_senha.get()
        confirmar_senha = entry_confirmar_senha.get()

        if not nova_senha or not confirmar_senha:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")
            return
        if nova_senha != confirmar_senha:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return

        conexao = sqlite3.connect('dados_turno.db')
        cursor = conexao.cursor()

        cursor.execute("UPDATE Usuarios SET senha = ?, primeiro_acesso = 0 WHERE usuario = ?",
                       (nova_senha, usuario))
        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
        janela_troca_senha.destroy()
        login_window.destroy()
        root.deiconify()  # Mostra a janela principal
        root.after(300, lambda: exibir_lembretes_sga_do_usuario(usuario))  # lembretes do SGA (Click_24)

    janela_troca_senha = Toplevel(root)
    janela_troca_senha.title("Trocar Senha")
    janela_troca_senha.geometry("380x360")
    janela_troca_senha.resizable(False, False)
    janela_troca_senha['bg'] = UI_FUNDO

    ui_dialogo(janela_troca_senha, "Trocar Senha", "Defina uma nova senha para continuar")
    cartao_troca = ui_cartao(janela_troca_senha, 84, 250)
    entry_nova_senha = ui_campo(cartao_troca, "Nova senha", 18, show="*")
    entry_confirmar_senha = ui_campo(cartao_troca, "Confirmar senha", 88, show="*")
    Button(cartao_troca, text="Salvar", bg=UI_AZUL, fg="white", font=(UI_FONTE, 11, "bold"),
           command=salvar_nova_senha).place(x=20, y=184, relwidth=1.0, width=-40, height=42)
    entry_nova_senha.focus_set()
    janela_troca_senha.bind('<Return>', lambda event: salvar_nova_senha())


def resetar_senha():
    def confirmar_reset():
        usuario_reset = entry_usuario_reset.get()
        nova_senha = "123456"  # Senha padrão após o reset

        if not usuario_reset:
            messagebox.showwarning("Atenção", "Por favor, insira o nome do usuário.")
            return

        conexao = sqlite3.connect('dados_turno.db')
        cursor = conexao.cursor()

        cursor.execute("UPDATE Usuarios SET senha = ?, primeiro_acesso = 1 WHERE usuario = ?",
                       (nova_senha, usuario_reset))
        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", f"Senha do usuário {usuario_reset} resetada para '123456'.")
        janela_reset_senha.destroy()

    janela_reset_senha = Toplevel(root)
    janela_reset_senha.title("Resetar Senha")
    janela_reset_senha.geometry("380x330")
    janela_reset_senha.resizable(False, False)
    janela_reset_senha['bg'] = UI_FUNDO

    ui_dialogo(janela_reset_senha, "Resetar Senha", "Somente para administradores")
    cartao_reset = ui_cartao(janela_reset_senha, 84, 220)
    entry_usuario_reset = ui_campo(cartao_reset, "Usuário", 18)
    Label(cartao_reset, text="A senha volta ao padrão e será trocada no próximo acesso.", bg=UI_CARD,
          fg=UI_TEXTO_SUAVE, font=(UI_FONTE, 9), wraplength=290, justify="left").place(x=20, y=88)
    Button(cartao_reset, text="Resetar", bg=UI_AZUL, fg="white", font=(UI_FONTE, 11, "bold"),
           command=confirmar_reset).place(x=20, y=150, relwidth=1.0, width=-40, height=42)
    entry_usuario_reset.focus_set()
    janela_reset_senha.bind('<Return>', lambda event: confirmar_reset())


def cmd_click_resetar_senha():
    if verificar_admin():
        resetar_senha()
    else:
        messagebox.showwarning("Atenção", "Apenas o admin pode resetar senhas.")


def criar_tela_login():
    global login_window, entry_usuario, entry_senha

    login_window = Toplevel(root)
    login_window.title("Login - Troca de Turno")
    login_window.geometry("380x420")
    login_window.resizable(False, False)
    login_window['bg'] = UI_FUNDO

    ui_dialogo(login_window, "Troca de Turno", "COG - Centro de Operação da Geração", altura_faixa=96)
    cartao_login = ui_cartao(login_window, 120, 264)
    entry_usuario = ui_campo(cartao_login, "Usuário", 20)
    entry_senha = ui_campo(cartao_login, "Senha", 92, show="*")
    Button(cartao_login, text="Entrar", bg=UI_AZUL, fg="white", font=(UI_FONTE, 11, "bold"),
           command=realizar_login).place(x=20, y=186, relwidth=1.0, width=-40, height=42)
    entry_usuario.focus_set()
    login_window.bind('<Return>', lambda event: realizar_login())  # login pela tecla enter.


# ___________________________________________________
# NOME COMPLETO DOS USUÁRIOS (usado no Click_25: campo "Solicitado por")
# ___________________________________________________
# O login (user.name) continua sendo a identificação interna do sistema; o nome completo serve apenas para
# apresentar a pessoa nos formulários e documentos. Quando um usuário não tem nome completo cadastrado, o
# sistema usa o próprio user.name.
BANCO_USUARIOS = "dados_turno.db"

# user.name -> nome completo. Carga inicial: só preenche cadastros que ainda não têm nome completo
# (o que o administrador digitar depois nunca é sobrescrito).
# O usuário "admin" fica sem nome completo de propósito.
NOMES_COMPLETOS_PADRAO = {
    "jfmjunior": "José Flavio Medeiros Jr",
    "lcampos": "Leonardo S. S. Campos",
    "evmorais": "Evandro Vicente Morais",
    "gsantiago": "Gilson Santiago",
    "gpalves": "Gabriel P. Alves",
    "garaujo": "Giovanni Araújo",
    "ltheodoro": "Luiz G. Theodoro",
    "pbiondi": "Pedro H. G. Biondi",
    "rdavid": "Rafael David de Paula",
    "bfribeiro": "Brendon F. Ribeiro",
    "rcrangel": "Ramon Cesar Rangel",
    "acaldeira": "Ademir Caldeira",
    "fsilva": "Fabiano Silva",
    "fjunqueira": "Fernando M. Junqueira",
    "ebenati": "Everton Benati",
    "nmaganha": "Nivaldo Maganha",
    "jbarros": "Jefferson Barros",
}


def garantir_nome_completo_usuarios():
    """Cria a coluna nome_completo na tabela Usuarios (se ainda não existir) e faz a carga inicial dos nomes.
    Não altera login, senha nem permissões."""
    conexao = sqlite3.connect(BANCO_USUARIOS, timeout=15)
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'Usuarios'")
        if cursor.fetchone() is None:
            return
        _adicionar_coluna_se_necessario(cursor, "Usuarios", "nome_completo", "TEXT")
        cursor.execute("SELECT LOWER(usuario) FROM Usuarios WHERE nome_completo IS NULL OR TRIM(nome_completo) = ''")
        sem_nome = {linha[0] for linha in cursor.fetchall()}
        for usuario, nome in NOMES_COMPLETOS_PADRAO.items():
            if usuario.lower() in sem_nome:                  # só grava onde ainda falta o nome
                cursor.execute("UPDATE Usuarios SET nome_completo = ? WHERE LOWER(usuario) = ? "
                               "AND (nome_completo IS NULL OR TRIM(nome_completo) = '')", (nome, usuario.lower()))
        conexao.commit()
    finally:
        conexao.close()


def listar_nomes_completos_usuarios():
    """[(usuario, nome_completo)] de todos os usuários, em ordem alfabética do login ('' se não houver nome)."""
    conexao = sqlite3.connect(BANCO_USUARIOS, timeout=15)
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT usuario, nome_completo FROM Usuarios ORDER BY usuario COLLATE NOCASE")
        return [(usuario, (nome or "").strip()) for usuario, nome in cursor.fetchall()]
    except sqlite3.OperationalError:          # tabela ainda sem a coluna nome_completo
        return []
    finally:
        conexao.close()


def buscar_nome_completo(usuario):
    """Nome completo cadastrado para o login informado ('' se não houver)."""
    if not usuario:
        return ""
    conexao = sqlite3.connect(BANCO_USUARIOS, timeout=15)
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT nome_completo FROM Usuarios WHERE LOWER(usuario) = ?", (usuario.strip().lower(),))
        linha = cursor.fetchone()
        return (linha[0] or "").strip() if linha else ""
    except sqlite3.OperationalError:
        return ""
    finally:
        conexao.close()


def obter_nome_completo_usuario(usuario):
    """Nome completo do profissional para exibir em formulários e documentos; se não houver, o próprio user.name."""
    return buscar_nome_completo(usuario) or (usuario or "")


def salvar_nome_completo_usuario(usuario, nome_completo):
    """Grava (ou altera) o nome completo de um usuário existente. Retorna True se o usuário foi encontrado."""
    conexao = sqlite3.connect(BANCO_USUARIOS, timeout=15)
    try:
        cursor = conexao.cursor()
        cursor.execute("UPDATE Usuarios SET nome_completo = ? WHERE usuario = ?", (nome_completo.strip(), usuario))
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()


def tela_nomes_usuarios():
    """Janela do administrador para conferir e alterar o nome completo de cada usuário."""
    garantir_nome_completo_usuarios()
    janela = Toplevel(root)
    janela.title("Nomes dos Usuários")
    janela.geometry("640x600")
    janela.minsize(560, 520)
    janela['bg'] = UI_FUNDO
    ui_dialogo(janela, "Nomes dos Usuários", "Nome completo que aparece nos formulários (o login não muda)")

    quadro = Frame(janela, bg=UI_CARD, highlightthickness=1, highlightbackground=UI_BORDA)
    quadro.place(x=24, y=84, relwidth=1.0, width=-48, relheight=1.0, height=-84 - 150)
    arvore = ttk.Treeview(quadro, columns=("usuario", "nome"), show="headings", selectmode="browse")
    arvore.heading("usuario", text="Usuário (login)", anchor="w")
    arvore.heading("nome", text="Nome completo", anchor="w")
    arvore.column("usuario", width=170, anchor="w", stretch=False)
    arvore.column("nome", width=380, anchor="w")
    arvore.tag_configure("pendente", foreground=UI_VERMELHO)
    rolagem = Scrollbar(quadro, orient=VERTICAL, command=arvore.yview)
    arvore.configure(yscrollcommand=rolagem.set)
    rolagem.pack(side=RIGHT, fill=Y)
    arvore.pack(side=LEFT, fill=BOTH, expand=True)

    cartao = Frame(janela, bg=UI_CARD, highlightthickness=1, highlightbackground=UI_BORDA)
    cartao.place(x=24, rely=1.0, y=-136, relwidth=1.0, width=-48, height=118)
    Label(cartao, text="Nome completo do usuário selecionado", bg=UI_CARD, fg=UI_TEXTO_SUAVE,
          font=(UI_FONTE, 9, "bold")).place(x=16, y=10)
    entrada = Entry(cartao, font=(UI_FONTE, 11))
    entrada.place(x=16, y=34, relwidth=1.0, width=-32, height=34)
    selecionado = {"usuario": None}

    def carregar(manter=None):
        arvore.delete(*arvore.get_children())
        for usuario, nome in listar_nomes_completos_usuarios():
            item = arvore.insert("", END, iid=usuario, values=(usuario, nome or "(sem nome completo)"),
                                 tags=() if nome else ("pendente",))
            if usuario == manter:
                arvore.selection_set(item)
                arvore.see(item)

    def ao_selecionar(evento=None):
        escolhido = arvore.selection()
        if not escolhido:
            return
        selecionado["usuario"] = escolhido[0]
        entrada.delete(0, END)
        entrada.insert(0, buscar_nome_completo(escolhido[0]))
        entrada.focus_set()

    def salvar():
        if not selecionado["usuario"]:
            messagebox.showwarning("Atenção", "Selecione um usuário na lista.", parent=janela)
            return
        nome = entrada.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Informe o nome completo.", parent=janela)
            return
        salvar_nome_completo_usuario(selecionado["usuario"], nome)
        carregar(selecionado["usuario"])
        messagebox.showinfo("Sucesso", "Nome completo salvo.", parent=janela)

    arvore.bind("<<TreeviewSelect>>", ao_selecionar)
    Button(cartao, text="Salvar nome", bg=UI_AZUL, fg="white", font=(UI_FONTE, 10, "bold"),
           command=salvar).place(x=16, y=76, width=160, height=32)
    entrada.bind("<Return>", lambda e: salvar())
    carregar()


def cmd_click_nomes_usuarios():
    if verificar_admin():
        tela_nomes_usuarios()
    else:
        messagebox.showwarning("Atenção", "Apenas o admin pode alterar os nomes dos usuários.")


# ___________________________________________________
# CADASTRO DE NOVOS USUÁRIOS
# ___________________________________________________
def cadastrar_usuario():
    garantir_nome_completo_usuarios()

    def salvar_usuario():
        novo_usuario = entry_novo_usuario.get()
        nome_completo = entry_nome_completo.get().strip()
        nova_senha = entry_nova_senha.get()
        eh_admin = var_admin.get()

        if not novo_usuario or not nome_completo or not nova_senha:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")
            return

        conexao = sqlite3.connect('dados_turno.db')
        cursor = conexao.cursor()

        try:
            cursor.execute("INSERT INTO Usuarios (usuario, senha, admin, nome_completo) VALUES (?, ?, ?, ?)",
                           (novo_usuario, nova_senha, eh_admin, nome_completo))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            janela_cadastro.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário já existe.")
        finally:
            conexao.close()

    # Janela de cadastro dos usuários
    janela_cadastro = Toplevel(root)
    janela_cadastro.title("Cadastrar Novo Usuário")
    janela_cadastro.geometry("380x490")
    janela_cadastro.resizable(False, False)
    janela_cadastro['bg'] = UI_FUNDO

    ui_dialogo(janela_cadastro, "Cadastrar Novo Usuário", "Somente para administradores")
    cartao_cadastro = ui_cartao(janela_cadastro, 84, 380)
    entry_novo_usuario = ui_campo(cartao_cadastro, "Novo usuário (login)", 18)
    entry_nome_completo = ui_campo(cartao_cadastro, "Nome completo", 88)
    entry_nova_senha = ui_campo(cartao_cadastro, "Nova senha", 158, show="*")

    var_admin = IntVar()  # 0 (não administrador)
    Checkbutton(cartao_cadastro, text="Usuário administrador", variable=var_admin, onvalue=1, offvalue=0,
                font=(UI_FONTE, 10)).place(x=16, y=230)
    Button(cartao_cadastro, text="Salvar", bg=UI_AZUL, fg="white", font=(UI_FONTE, 11, "bold"),
           command=salvar_usuario).place(x=20, y=284, relwidth=1.0, width=-40, height=42)
    entry_novo_usuario.focus_set()


def verificar_admin():
    if not current_user:
        return False
    conexao = sqlite3.connect('dados_turno.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT admin FROM Usuarios WHERE usuario = ?", (current_user.split(" em ")[0],))
    resultado = cursor.fetchone()
    conexao.close()
    return resultado and resultado[0] == 1


def cmd_click_cadastrar_usuario():
    if verificar_admin():
        cadastrar_usuario()
    else:
        messagebox.showwarning("Atenção", "Apenas o admin pode cadastrar novos usuários.")


# ---------------------------------------------------
# CONFIGURAÇÃO DA JANELA PRINCIPAL
# ---------------------------------------------------
root = Tk()
root.title('COG-ALUPAR - TROCA DE TURNO')
root.geometry('1539x780')
root.resizable(True, True)
root['bg'] = '#024593'
img = PhotoImage(file='cog3.png')
Label_imagem = Label(root, image=img).pack()

root.withdraw()  # Oculta a janela principal até que o login seja realizado

meuMenu = Menu(root)
LANCAMENTOMenu = Menu(meuMenu, tearoff=0)
LANCAMENTOMenu.add_command(label="Informações Relevantes", command=cmd_click1)
LANCAMENTOMenu.add_command(label="Alarmes e Sinalizações", command=cmd_click2)
LANCAMENTOMenu.add_command(label="Anormalidades Estações Telemétricas", command=cmd_click3)
LANCAMENTOMenu.add_command(label="Comprovação de Disponibilidade", command=cmd_click4)
LANCAMENTOMenu.add_command(label="Comutação de Malha de Controle", command=cmd_click5)
LANCAMENTOMenu.add_command(label="Contato com Balseiro da UHE SJO", command=cmd_click6)
LANCAMENTOMenu.add_command(label="Testes de Descargas Parciais", command=cmd_click7)
LANCAMENTOMenu.add_command(label="Falha de Comunicação", command=cmd_click8)
LANCAMENTOMenu.add_command(label="Falha de Supervisão", command=cmd_click9)
LANCAMENTOMenu.add_command(label="Perturbações", command=cmd_click10)
LANCAMENTOMenu.add_command(label="Falha Fonte externa Serviço Auxiliar CA", command=cmd_click11)
LANCAMENTOMenu.add_command(label="Informações do ONS", command=cmd_click12)
LANCAMENTOMenu.add_command(label="Transbordo Plantas Aquáticas", command=cmd_click13)
LANCAMENTOMenu.add_command(label="Habilitação-Desabilitação do SEP-ECE", command=cmd_click14)
LANCAMENTOMenu.add_command(label="Alimentação do SACA por outro Agente", command=cmd_click15)

LANCAMENTOMenu.add_separator()
LANCAMENTOMenu.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="TROCA DE TURNO", menu=LANCAMENTOMenu)

fileRELATORIO = Menu(meuMenu, tearoff=0)
fileRELATORIO.add_command(label="Gerar Relatório PDF (Completo)", command=gerar_pdf_completo)
fileRELATORIO.add_command(label="Gerar Relatório PDF (Filtrado)", command=abrir_janela_filtros)
fileRELATORIO.add_command(label="Gerar Relatório TAG AVATO", command=abrir_janela_avato_filtro)
fileRELATORIO.add_command(label="Gerar Relatório PROTOCOLO", command=abrir_janela_protocolo_filtro)

fileRELATORIO.add_separator()
# fileRELATORIO.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="RELATORIO", menu=fileRELATORIO)

fileTAG_AVATO = Menu(meuMenu, tearoff=0)
fileTAG_AVATO.add_command(label="TAG-Ávato", command=cmd_click16)
fileTAG_AVATO.add_separator()
fileTAG_AVATO.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="TAG-ÁVATO", menu=fileTAG_AVATO)

filePROTOCOL = Menu(meuMenu, tearoff=0)
filePROTOCOL.add_command(label="Protocolo", command=cmd_click17)
filePROTOCOL.add_separator()
filePROTOCOL.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="PROTOCOLO", menu=filePROTOCOL)

fileTRIP_FGO = Menu(meuMenu, tearoff=0)
fileTRIP_FGO.add_command(label="Simulador Trip UHE FGO", command=cmd_click18)
fileTRIP_FGO.add_separator()
fileTRIP_FGO.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="SIM_TRIP_UHE_FGO", menu=fileTRIP_FGO)

fileSATURACAO_FGO = Menu(meuMenu, tearoff=0)
fileSATURACAO_FGO.add_command(label="Simulador Saturação UHE FGO", command=cmd_click19)
fileSATURACAO_FGO.add_separator()
fileSATURACAO_FGO.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="SIM_SATUR_UHE_FGO", menu=fileSATURACAO_FGO)

fileSIM_NIVEL_FGO = Menu(meuMenu, tearoff=0)
fileSIM_NIVEL_FGO.add_command(label="Simulador Hidráulico UHE FGO", command=cmd_click20)
fileSIM_NIVEL_FGO.add_separator()
fileSIM_NIVEL_FGO.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="SIM_HIDRO_UHE_FGO", menu=fileSIM_NIVEL_FGO)

fileDIRETRIZES = Menu(meuMenu, tearoff=0)
fileDIRETRIZES.add_command(label="Pesquisar e Abrir PDF - Diretrizes", command=cmd_click21)
fileDIRETRIZES.add_separator()
fileDIRETRIZES.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="DIRETRIZES", menu=fileDIRETRIZES)

fileIO_ONS = Menu(meuMenu, tearoff=0)
fileIO_ONS.add_command(label="Abrir procedimentos do ONS", command=cmd_click22)
fileIO_ONS.add_separator()
fileIO_ONS.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="IO-ONS", menu=fileIO_ONS)

fileAUTO_AVALIACAO = Menu(meuMenu, tearoff=0)
fileAUTO_AVALIACAO.add_command(label="Responder Auto-Avaliação", command=cmd_click23)
fileAUTO_AVALIACAO.add_separator()
fileAUTO_AVALIACAO.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="AUTO-AVALIAÇÃO", menu=fileAUTO_AVALIACAO)
# ========cascate SEGUNDA PARTE termina aqui
# ========cascate Click_24 - SEGUNDA PARTE inicia aqui
fileSGA = Menu(meuMenu, tearoff=0)
fileSGA.add_command(label="Sistema de Gestão de Atividades", command=cmd_click24)
fileSGA.add_separator()
fileSGA.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="SGA", menu=fileSGA)
# ========cascate SEGUNDA PARTE termina aqui

# ========cascate Click_25 - SEGUNDA PARTE inicia aqui
fileDOC_LIB = Menu(meuMenu, tearoff=0)
fileDOC_LIB.add_command(label="ATEIE", command=cmd_click25_ateie)
fileDOC_LIB.add_command(label="AI", command=cmd_click25_ai)
fileDOC_LIB.add_command(label="MO", command=cmd_click25_mo)
fileDOC_LIB.add_command(label="SM_Avulso", command=cmd_click25_sm_avulso)
fileDOC_LIB.add_separator()
fileDOC_LIB.add_command(label='Sair', command=root.quit)
meuMenu.add_cascade(label="DOC_LIB.", menu=fileDOC_LIB)
# ========cascate SEGUNDA PARTE termina aqui

ADMINMenu = Menu(meuMenu, tearoff=0)
ADMINMenu.add_command(label="Cadastrar Usuário", command=cmd_click_cadastrar_usuario)
ADMINMenu.add_command(label="Resetar Senha", command=cmd_click_resetar_senha)
ADMINMenu.add_command(label="Nomes dos Usuários", command=cmd_click_nomes_usuarios)
meuMenu.add_cascade(label="ADMIN", menu=ADMINMenu)

root.config(menu=meuMenu)

criar_banco()
garantir_nome_completo_usuarios()   # coluna nome_completo (Click_25)
criar_tela_login()
root.mainloop()