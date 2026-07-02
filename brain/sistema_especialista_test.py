import json
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from brain.modelo_ia import SistemaEspecialistaAutomotivo


def executar_testes():
    especialista = SistemaEspecialistaAutomotivo()

    print("=== TESTE 1: Analisar dados vivos ===")
    resultado_live = especialista.analisar_dados_vivos(
        modelo="Gol 1.6 G6",
        defeito_chave="luz_epc_acesa",
        valor_atual_sensor="Oscilando em 1.2V no scanner"
    )
    print(json.dumps(resultado_live, indent=2, ensure_ascii=False))

    print("\n=== TESTE 2: Consultar pinout ===")
    resultado_pinout = especialista.consultar_pinout("ECU Magneti Marelli 4GV", 32)
    print(resultado_pinout)

    print("\n=== TESTE 3: Analisar sintoma visual ===")
    resultado_sintoma = especialista.analisar_sintoma_visual("oleo cafe com leite")
    print(resultado_sintoma)


if __name__ == "__main__":
    executar_testes()
