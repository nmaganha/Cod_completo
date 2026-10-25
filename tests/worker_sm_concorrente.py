"""Um processo do teste de concorrência: carrega o sistema, espera o sinal de largada e salva N SMs / reserva números no
banco compartilhado. Imprime as linhas "NUMERO <numero>" (uma por documento criado)."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carregar_main import carregar_main  # noqa: E402
from conftest import FluxoSM  # noqa: E402

pasta, quantidade, modo = sys.argv[1], int(sys.argv[2]), sys.argv[3]
app = carregar_main(pasta)
app.PASTA_ARQUIVO_DOC_LIB = app.PASTA_ARQUIVO_DOC_LIB_LOCAL = os.path.join(pasta, "arquivo")
fluxo = FluxoSM(app)
print("PRONTO", flush=True)
while not os.path.exists(os.path.join(pasta, "largada")):
    time.sleep(0.01)
for _ in range(quantidade):
    if modo == "salvar":
        print("NUMERO", app.doc_lib_carregar_sm(fluxo.salvar())["numero"], flush=True)
    else:
        for item in app.doc_lib_reservar_sm(2, "operador1"):
            print("NUMERO", item["numero"], flush=True)
