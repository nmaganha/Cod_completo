# Código atualizado em 14-09-26 – 16,03 (Inclusão do Click_23)
import sqlite3
from tkinter import *
# from tkinter import ttk, messagebox
from tkinter import Tk
from tkcalendar import Calendar
from datetime import datetime, timedelta
from fpdf import FPDF, XPos, YPos
import os
import platform
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
from matplotlib.figure import Figure  # exclusivo para o click23
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # exclusivo para o click23

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
    info_relev.resizable(False, False)
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
    alar_sinal.resizable(False, False)
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
    anom_telem.resizable(False, False)
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
    comp_disp.resizable(False, False)
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
    comut_malha.resizable(False, False)
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
    cont_balsa.resizable(False, False)
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
    desc_parc.resizable(False, False)
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
    falh_comm.resizable(False, False)
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
    falh_sdsc.resizable(False, False)
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
                                                                                                   rely=0.15),
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
                   "CGE JDT", "UFV PTM", "SE IGU", "SE MCP", "SE CLA", "SE SCA", "SE IPG", "SE RSD", "SE JDD"],
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
    pert_equip.resizable(False, False)
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
    falh_saca.resizable(False, False)
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
    info_ons.resizable(False, False)
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
    trans_paqu.resizable(False, False)
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
    habil_ece.resizable(False, False)
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
    saca_agente.resizable(False, False)
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
    tag_avato.resizable(False, False)
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
    protocolo.resizable(False, False)
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
    sim_trip_fgo.geometry('1200x667')
    sim_trip_fgo.resizable(False, False)
    sim_trip_fgo['bg'] = "#a4bad2"

    # Frame a esquerda para a inserção dos dados
    left_frame = Frame(sim_trip_fgo, borderwidth=1, relief="solid", bg="#a4bad2")
    left_frame.place(x=5, y=85, width=400, height=570)

    # Frame a direita para exibir os resultados
    right_frame = Frame(sim_trip_fgo, borderwidth=1, relief="solid", bg="#F0F0F0")
    right_frame.place(x=400, y=85, width=790, height=570)

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
    lf3 = Label(sim_nivel_fgo,
                text="Data/Hora       |    Mont.    |  Jus.   |    HB    |  MW_U1  |  MW_U2  |  MW_U3  | UGV |    Aflu.   |    Turb.    |   Vert.    |    Defl.    |  Ab_CS1 | Ab_CS2 | Ab_CS3 |    Delta1   |   Delta2   |   Delta3   |    Var(m)",
                bg="#a4bad2", font=("Arial", 10))
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
    MAX_REVISAO = 400
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

                        if callback_progresso:
                            callback_progresso(100, revisao)

                        return resultado

        return None


    # ===== FUNÇÃO QUE EXECUTA A BUSCA EM THREAD =====
    def executar_busca_em_thread(localidade, categoria, subtipo, url_base,
                                 janela_progresso, progress_bar, lbl_status, lbl_revisao):

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
            else:
                msg = "✅ Busca concluída! Abrindo navegador..."

            janela_progresso.after(0, lambda: lbl_status.configure(text=msg))

        url_final = encontrar_ultima_revisao(url_base, callback_progresso)

        if url_final:
            janela_progresso.after(1000, janela_progresso.destroy)
            webbrowser.open(url_final)
            janela_progresso.after(0, lambda: messagebox.showinfo("Sucesso",
                                                                  f"✅ Procedimento aberto com sucesso!\n\n"
                                                                  f"Localidade: {localidade}\n"
                                                                  f"Documento: {subtipo}\n\n"
                                                                  f"O arquivo foi aberto no seu navegador."))
        else:
            janela_progresso.after(0, janela_progresso.destroy)
            janela_progresso.after(0, lambda: messagebox.showerror("Erro",
                                                                   f"❌ Não foi possível encontrar o procedimento!\n\n"
                                                                   f"Localidade: {localidade}\n"
                                                                   f"Documento: {subtipo}\n\n"
                                                                   f"Verifique se a URL está correta ou se o\n"
                                                                   f"documento está disponível no site."))

    # ===== FUNÇÃO PARA ABRIR PROCEDIMENTO =====
    def abrir_procedimento(localidade, categoria, subtipo, url_base):

        janela_progresso = Toplevel()
        janela_progresso.title("Buscando procedimento...")
        janela_progresso.geometry("500x280")
        janela_progresso.resizable(False, False)
        janela_progresso['bg'] = "#a4bad2"
        janela_progresso.transient()
        janela_progresso.grab_set()

        lbl_titulo = Label(janela_progresso, text="🔍 BUSCANDO PROCEDIMENTO",
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
                              text="⏳ Buscando revisões de 00 até 99...\nIsso pode levar alguns segundos.",
                              bg="#a4bad2", font=("Arial", 8), fg="#555")
        lbl_instrucao.pack(pady=10)

        def cancelar_busca():
            janela_progresso.destroy()
            messagebox.showinfo("Busca cancelada", "A busca foi cancelada pelo usuário.")

        btn_cancelar = Button(janela_progresso, text="Cancelar", command=cancelar_busca,
                              bg="#FF8C00", fg="white", font=("Arial", 9))
        btn_cancelar.pack(pady=5)

        thread_busca = threading.Thread(
            target=executar_busca_em_thread,
            args=(localidade, categoria, subtipo, url_base,
                  janela_progresso, progress_bar, lbl_status, lbl_revisao),
            daemon=True
        )
        thread_busca.start()

    # ===== JANELA DE SUBTIPOS =====
    def abrir_subtipos(localidade, categoria):
        """Abre a janela com os subtipos (4 para CADASTRO, 8 para INSTRUÇÕES)"""

        dados = procedimentos[localidade][categoria]
        subtipos = list(dados.keys())

        cores = ["#3498DB", "#2ECC71", "#E74C3C", "#F39C12", "#9B59B6", "#1ABC9C", "#E67E22", "#34495E"]

        janela_subtipos = Toplevel(frame_principal)
        janela_subtipos.title(f"{categoria} - {localidade}")
        janela_subtipos.geometry("600x500")
        janela_subtipos.resizable(False, False)
        janela_subtipos['bg'] = "#a4bad2"

        titulo = Label(janela_subtipos, text=f"{localidade}\n{categoria}",
                       font=('Arial', '14', 'bold'),
                       bg="#024593", fg="white", height=2)
        titulo.pack(fill='x')

        subtitulo = Label(janela_subtipos, text=f"Selecione o documento desejado:",
                          bg="#a4bad2", font=("Arial", 11))
        subtitulo.pack(pady=15)

        frame_botoes = Frame(janela_subtipos, bg="#a4bad2")
        frame_botoes.pack(fill='both', expand=True, padx=30, pady=10)

        colunas = 2
        for idx, subtipo in enumerate(subtipos):
            linha = idx // colunas
            coluna = idx % colunas
            cor = cores[idx % len(cores)]

            url_base = dados[subtipo]

            btn_frame = Frame(frame_botoes, bg="#a4bad2")
            btn_frame.grid(row=linha, column=coluna, padx=10, pady=10, sticky="nsew")

            if "INSERIR URL" in url_base:
                btn_text = f"⚠️ {subtipo}\n(URL não configurada)"
                btn_state = "disabled"
            else:
                btn_text = subtipo
                btn_state = "normal"

            btn = Button(btn_frame, text=btn_text,
                         command=lambda s=subtipo, u=url_base: abrir_procedimento(localidade, categoria, s, u),
                         bg=cor, fg="white",
                         font=("Arial", 10, "bold"),
                         height=2, width=25,
                         wraplength=200,
                         state=btn_state)
            btn.pack()

            descricao = "Clique para abrir"
            Label(btn_frame, text=descricao if "INSERIR" not in url_base else "⚠️ Configurar URL",
                  bg="#a4bad2", font=("Arial", 8), fg="#555").pack(pady=(5, 0))

        for i in range(colunas):
            frame_botoes.grid_columnconfigure(i, weight=1)

        Button(janela_subtipos, text="Fechar", command=janela_subtipos.destroy,
               bg="#FF0000", fg="white", font=("Arial", 10, "bold"), width=15).pack(pady=15)

    # ===== JANELA DE OPÇÕES (CADASTRO ou INSTRUÇÕES) =====
    def abrir_opcoes_localidade(localidade):

        janela_opcoes = Toplevel(frame_principal)
        janela_opcoes.title(f"Opções - {localidade}")
        janela_opcoes.geometry("500x350")
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
    frame_principal.geometry('800x600')
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

        btn = Button(btn_frame, text=localidade,
                     command=lambda l=localidade: abrir_opcoes_localidade(l),
                     bg="#024593", fg="white",
                     font=("Arial", 10, "bold"),
                     height=3, width=25,
                     wraplength=200)
        btn.pack()

        Label(btn_frame, text="Clique para acessar", bg="#a4bad2",
              font=("Arial", 8), fg="#666").pack(pady=(5, 0))

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


def criar_grafico_resultado(parent, percentual_usuario, percentual_media, meta=70):
    """Cria o gráfico comparativo (nota do treinando x média geral x meta) embutido no Tkinter."""
    fig = Figure(figsize=(6.5, 3.3), dpi=100)
    ax = fig.add_subplot(111)

    categorias = ["Sua Nota", "Média Geral"]
    valores = [percentual_usuario, percentual_media]
    cores = ["#024593", "#079541"]

    barras = ax.bar(categorias, valores, color=cores, width=0.5)
    ax.axhline(y=meta, color="red", linestyle="--", linewidth=1.5)
    ax.text(0.55, meta + 2, f"Meta ({meta:.0f}%)", color="red", fontsize=9, ha="right")

    for barra, valor in zip(barras, valores):
        ax.text(barra.get_x() + barra.get_width() / 2, valor + 2, f"{valor:.1f}%",
                ha="center", fontsize=10, fontweight="bold")

    ax.set_ylim(0, 110)
    ax.set_ylabel("Percentual de Acerto (%)")
    ax.set_title("Comparativo de Desempenho")
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
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
    quiz_win.geometry('1200x650')
    quiz_win.resizable(False, False)
    quiz_win['bg'] = "#a4bad2"

    lf1 = Label(quiz_win, text='Auto-avaliação - Teste seus Conhecimentos', font=('Arial', '14', 'bold'),
                bg="#024593", fg="white")
    lf1.place(relx=0.00, rely=0.00, width=1200, height=60)

    conteudo_frame = Frame(quiz_win, borderwidth=1, relief="solid", bg="#F0F0F0")
    conteudo_frame.place(x=20, y=80, width=1160, height=460)

    rodape_label = Label(quiz_win, text="", bg="#a4bad2", font=("Arial", 9))
    rodape_label.place(x=20, y=560)

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

        Label(conteudo_frame, text=f"Olá, {estado['nome']}! Escolha o formato das questões que deseja responder:",
              bg="#F0F0F0", font=("Arial", 12, "bold"), wraplength=1100).place(x=30, y=30)

        banco_atual = carregar_questoes()
        opcoes_assunto = ["TODAS"] + sorted({str(q["assunto"]).strip() for q in banco_atual})

        # Coluna 1 - Número de questões
        Label(conteudo_frame, text="Número de questões", bg="#F0F0F0",
              font=("Arial", 11, "bold")).place(x=40, y=90)
        quantidade_var = IntVar(value=OPCOES_QUANTIDADE_QUESTOES[0])
        ttk.Combobox(conteudo_frame, textvariable=quantidade_var, values=OPCOES_QUANTIDADE_QUESTOES,
                     state="readonly", justify='center', font=("Arial", 11), width=15
                     ).place(x=40, y=120, height=28)

        # Coluna 2 - Localidade
        Label(conteudo_frame, text="Localidade", bg="#F0F0F0",
              font=("Arial", 11, "bold")).place(x=540, y=90)
        localidade_var = StringVar(value="TODAS")
        ttk.Combobox(conteudo_frame, textvariable=localidade_var, values=OPCOES_LOCALIDADE,
                     state="readonly", justify='center', font=("Arial", 11), width=15
                     ).place(x=510, y=120, height=28)

        # Coluna 3 - Assunto
        Label(conteudo_frame, text="Assunto", bg="#F0F0F0",
              font=("Arial", 11, "bold")).place(x=970, y=90)
        assunto_var = StringVar(value="TODAS")
        ttk.Combobox(conteudo_frame, textvariable=assunto_var, values=opcoes_assunto,
                     state="readonly", justify='center', font=("Arial", 11), width=22
                     ).place(x=910, y=120, height=28)

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

        largura_botao = 220
        x_centralizado = 30 + (1100 - largura_botao) // 2

        Button(conteudo_frame, text="Iniciar Questionário", command=iniciar, bg="#024593", fg="white",
               font=("Arial", 11, "bold")).place(x=x_centralizado, y=350, width=largura_botao, height=35)

        if pode_ver_relatorio:
            Button(conteudo_frame, text="Relatório dos treinandos", command=gerar_relatorio_treinandos,
                   bg="#079541", fg="white", font=("Arial", 11, "bold")
                   ).place(x=x_centralizado, y=400, width=largura_botao, height=35)

    def mostrar_pergunta():
        limpar_conteudo()
        idx = estado["indice"]
        pergunta = estado["perguntas"][idx]

        total = estado["total_perguntas"]
        rodape_label.config(
            text=f"Treinando: {estado['nome']}    |    Pergunta {idx + 1} de {total}    |    Assunto: {pergunta['assunto']}")

        Label(conteudo_frame, text=f"Questão {idx + 1}: {pergunta['pergunta']}", bg="#F0F0F0",
              font=("Arial", 12, "bold"), wraplength=1100, justify="left").place(x=30, y=25, width=1100)

        estado["resposta_var"] = StringVar(value="")
        opcoes = [("A", pergunta["opcao_a"]), ("B", pergunta["opcao_b"]),
                  ("C", pergunta["opcao_c"]), ("D", pergunta["opcao_d"])]

        y_pos = 100
        for letra, texto in opcoes:
            Radiobutton(conteudo_frame, text=f"{letra}) {texto}", variable=estado["resposta_var"],
                        value=letra, bg="#F0F0F0", font=("Arial", 11), wraplength=1080,
                        justify="left", anchor="w").place(x=50, y=y_pos, width=1090, height=50)
            y_pos += 50

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
        Button(conteudo_frame, text=texto_botao, command=confirmar, bg="#024593", fg="white",
               font=("Arial", 11, "bold")).place(x=510, y=400, width=200, height=35)

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

        resultado_texto = (
            f"Parabéns, {estado['nome']}!\n\n"
            f"Você acertou {acertos} de {total} perguntas ({percentual:.1f}%)."
        )

        Label(conteudo_frame, text=resultado_texto, bg="#F0F0F0", font=("Arial", 13, "bold"),
              justify="left", wraplength=800).place(x=30, y=20, width=800)

        grafico = criar_grafico_resultado(conteudo_frame, percentual, percentual_media)
        grafico.get_tk_widget().place(x=30, y=90, width=800, height=290)

        Button(conteudo_frame, text="Responder Novamente", command=tela_configuracao,
               bg="#024593", fg="white", font=("Arial", 11, "bold")).place(x=30, y=400, width=200, height=35)
        Button(conteudo_frame, text="Fechar", command=quiz_win.destroy,
               bg="#FF0000", fg="white", font=("Arial", 11, "bold")).place(x=250, y=400, width=120, height=35)

    tela_configuracao()

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

    janela_troca_senha = Toplevel(root)
    janela_troca_senha.title("Trocar Senha")
    janela_troca_senha.geometry("300x260")
    janela_troca_senha.resizable(False, False)
    janela_troca_senha['bg'] = '#024593'

    Label(janela_troca_senha, text="Nova Senha:", font=('arial', 10, 'bold'), fg='white', bg='#024593').place(relx=0.37,
                                                                                                              rely=0.1)
    entry_nova_senha = Entry(janela_troca_senha, show="*")
    entry_nova_senha.place(relx=0.17, rely=0.2, width=200, height=30)

    Label(janela_troca_senha, text="Confirmar Senha:", font=('arial', 10, 'bold'), fg='white', bg='#024593').place(
        relx=0.32, rely=0.4)
    entry_confirmar_senha = Entry(janela_troca_senha, show="*")
    entry_confirmar_senha.place(relx=0.17, rely=0.5, width=200, height=30)

    Button(janela_troca_senha, fg='#024593', text="Salvar", font=('arial', 10, 'bold'),
           command=salvar_nova_senha).place(relx=0.37,
                                            rely=0.83,
                                            width=75)
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
    janela_reset_senha.geometry("300x200")
    janela_reset_senha.resizable(False, False)
    janela_reset_senha['bg'] = '#024593'

    Label(janela_reset_senha, bg='#024593', fg='white', text="Usuário:", font=('arial', 10, 'bold')).place(relx=0.4,
                                                                                                           rely=0.15)
    entry_usuario_reset = Entry(janela_reset_senha)
    entry_usuario_reset.place(relx=0.15, rely=0.30, width=210, height=30)

    Button(janela_reset_senha, fg='#024593', text="Resetar", font=('arial', 10, 'bold'),
           command=confirmar_reset).place(relx=0.35, rely=0.60, width=80)
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
    login_window.geometry("300x260")
    login_window.resizable(False, False)
    login_window['bg'] = "#024593"

    lb6 = Label(login_window, text="Usuário:", fg="white", bg='#024593', font=('arial', 11, 'bold'))
    lb6.place(relx=0.25, rely=0.09, width=150)
    entry_usuario = Entry(login_window)
    entry_usuario.place(relx=0.22, rely=0.20, width=170, height=30)

    lb7 = Label(login_window, text="Senha:", fg="white", bg='#024593', font=('arial', 11, 'bold'))
    lb7.place(relx=0.25, rely=0.39, width=150)
    entry_senha = Entry(login_window, show="*")
    entry_senha.place(relx=0.22, rely=0.50, width=170, height=30)

    bt1 = Button(login_window, text="Entrar", width=12, font=('Arial', 11, 'bold'), fg='#024593',
                 overrelief="sunken", highlightthickness=2, command=realizar_login)
    bt1.place(relx=0.35, rely=0.75, width=100)
    login_window.bind('<Return>', lambda event: realizar_login())  # login pela tecla enter.


# ___________________________________________________
# CADASTRO DE NOVOS USUÁRIOS
# ___________________________________________________
def cadastrar_usuario():
    def salvar_usuario():
        novo_usuario = entry_novo_usuario.get()
        nova_senha = entry_nova_senha.get()
        eh_admin = var_admin.get()

        if not novo_usuario or not nova_senha:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")
            return

        conexao = sqlite3.connect('dados_turno.db')
        cursor = conexao.cursor()

        try:
            cursor.execute("INSERT INTO Usuarios (usuario, senha, admin) VALUES (?, ?, ?)",
                           (novo_usuario, nova_senha, eh_admin))
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
    janela_cadastro.geometry("300x260")
    janela_cadastro.resizable(False, False)
    janela_cadastro['bg'] = '#a4bad2'

    Label(janela_cadastro, text="Novo Usuário:", font=('arial', 10, 'bold'), bg='#a4bad2').place(relx=0.37, rely=0.1)
    entry_novo_usuario = Entry(janela_cadastro)
    entry_novo_usuario.place(relx=0.17, rely=0.2, width=200, height=25)

    Label(janela_cadastro, text="Nova Senha:", font=('arial', 10, 'bold'), bg='#a4bad2').place(relx=0.37, rely=0.4)
    entry_nova_senha = Entry(janela_cadastro, show="*")
    entry_nova_senha.place(relx=0.17, rely=0.5, width=200, height=25)

    var_admin = IntVar()  # 0 (não administrador)
    Checkbutton(janela_cadastro, bg='#a4bad2', text="Admin", font=('arial', 10, 'bold'),
                variable=var_admin, onvalue=1, offvalue=0).place(relx=0.15, rely=0.65)
    Button(janela_cadastro, fg='white', bg='#024593', text="Salvar", font=('arial', 10, 'bold'),
           command=salvar_usuario).place(relx=0.4, rely=0.83, width=80)


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
meuMenu.add_cascade(label="LANÇAMENTO", menu=LANCAMENTOMenu)

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

ADMINMenu = Menu(meuMenu, tearoff=0)
ADMINMenu.add_command(label="Cadastrar Usuário", command=cmd_click_cadastrar_usuario)
ADMINMenu.add_command(label="Resetar Senha", command=cmd_click_resetar_senha)
meuMenu.add_cascade(label="ADMIN", menu=ADMINMenu)

root.config(menu=meuMenu)

criar_banco()
criar_tela_login()
root.mainloop()