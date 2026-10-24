"""Carrega o main.py (sem o mainloop final) como módulo, na pasta de trabalho atual (usada pelo conftest e pelos testes de
concorrência, que carregam o sistema em processos separados)."""
import os
import shutil
import sys
import types

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_MAIN = os.path.join(RAIZ, "main.py")


def carregar_main(pasta):
    """Executa o main.py dentro de 'pasta' (o banco dados_turno.db e a imagem da janela principal são relativos a ela)."""
    os.chdir(pasta)
    destino = os.path.join(pasta, "cog3.png")
    if not os.path.exists(destino):
        shutil.copy(os.path.join(RAIZ, "cog3.png"), destino)
    codigo = open(CAMINHO_MAIN, encoding="utf-8").read().rstrip()
    assert codigo.endswith("root.mainloop()"), "main.py deveria terminar com root.mainloop()"
    codigo = codigo[:-len("root.mainloop()")] + "pass\n"
    modulo = types.ModuleType("cog_main")
    modulo.__file__ = CAMINHO_MAIN
    sys.modules["cog_main"] = modulo
    exec(compile(codigo, CAMINHO_MAIN, "exec"), modulo.__dict__)
    return modulo
