"""Login com o banco errado (caso típico do .exe aberto sem o dados_turno.db real ao lado dele).

O programa não cria a tabela Usuarios (ela só existe no banco completo do sistema). Aberto numa pasta sem o banco real, o SQLite
cria um dados_turno.db vazio e o login falhava com a exceção "no such table: Usuarios" no console. Agora o usuário recebe uma
mensagem que diz qual banco foi aberto e o que fazer.
"""
import os
import sqlite3


def test_login_com_banco_sem_a_tabela_usuarios_mostra_mensagem_clara(app, banco, mensagens):
    conexao = sqlite3.connect("dados_turno.db")        # a pasta do teste só tem as tabelas do Doc_Lib., sem Usuarios
    existe = conexao.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'Usuarios'").fetchone()
    conexao.close()
    assert existe is None
    app.entry_usuario.delete(0, "end")
    app.entry_senha.delete(0, "end")
    app.entry_usuario.insert(0, "alguem")
    app.entry_senha.insert(0, "qualquer")
    try:
        app.realizar_login()                           # não pode lançar sqlite3.OperationalError
    finally:
        app.entry_usuario.delete(0, "end")
        app.entry_senha.delete(0, "end")
    titulo, texto = mensagens.erros[-1]
    assert titulo == "Banco de dados não encontrado"
    assert "no such table: Usuarios" in texto
    assert os.path.abspath("dados_turno.db") in texto             # diz qual banco foi aberto
    assert "dados_turno.db completo" in texto


def test_pasta_do_aplicativo_na_versao_em_python_e_a_pasta_do_main(app):
    """Fora do .exe nada muda: os caminhos continuam sendo os da pasta do main.py."""
    assert app.PASTA_APLICATIVO == os.path.dirname(os.path.abspath(app.__file__))
    assert app.PASTA_BASE == app.PASTA_APLICATIVO
