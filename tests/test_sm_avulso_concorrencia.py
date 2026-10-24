"""SM Avulso: criação e reserva simultâneas por VÁRIOS PROCESSOS (várias estações usando o mesmo banco) sem número duplicado."""
import os
import subprocess
import sys
import time

import pytest

PASTA_TESTES = os.path.dirname(os.path.abspath(__file__))
PROCESSOS = 4


def rodar_em_paralelo(app, pasta, quantidade, modo):
    """Inicia os processos, espera todos ficarem prontos, dá a largada ao mesmo tempo e devolve os números criados."""
    ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")
    processos = [subprocess.Popen([sys.executable, os.path.join(PASTA_TESTES, "worker_sm_concorrente.py"), str(pasta),
                                   str(quantidade), modo], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                  encoding="utf-8", env=ambiente) for _ in range(PROCESSOS)]
    prontos = 0
    inicio = time.time()
    for processo in processos:
        while True:
            linha = processo.stdout.readline()
            if linha.strip() == "PRONTO":
                prontos += 1
                break
            assert linha or processo.poll() is None, processo.stderr.read()
            assert time.time() - inicio < 120, "os processos não ficaram prontos"
    assert prontos == PROCESSOS
    open(os.path.join(pasta, "largada"), "w").close()
    numeros = []
    for processo in processos:
        saida, erro = processo.communicate(timeout=180)
        assert processo.returncode == 0, erro
        numeros += [linha.split()[1] for linha in saida.splitlines() if linha.startswith("NUMERO")]
    os.remove(os.path.join(pasta, "largada"))
    return numeros


@pytest.mark.parametrize("modo,esperados", [("salvar", PROCESSOS * 5), ("reservar", PROCESSOS * 5 * 2)])
def test_processos_simultaneos_nao_duplicam_numeros(app, banco, modo, esperados):
    import shutil
    shutil.copy(os.path.join(PASTA_TESTES, "..", "cog3.png"), banco / "cog3.png")
    numeros = rodar_em_paralelo(app, banco, 5, modo)
    assert len(numeros) == esperados and len(set(numeros)) == esperados, "número duplicado"
    assert sorted(numeros) == [f"{n:04d}/26" for n in range(1, esperados + 1)]       # sequência contínua, sem buracos
    conexao = app.doc_lib_conectar()
    assert conexao.execute("SELECT COUNT(*), COUNT(DISTINCT numero) FROM doclib_sm").fetchone() == (esperados, esperados)
    assert conexao.execute("SELECT ultimo FROM doclib_numeracao WHERE tipo = 'SM' AND ano = 2026").fetchone()[0] == esperados
    conexao.close()
