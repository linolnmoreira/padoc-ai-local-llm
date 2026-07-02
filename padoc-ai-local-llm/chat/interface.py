
"""Interface de chat para PADOC AI"""

from brain.modelo_ia import PadocAI
from memory.memoria import salvar_memoria
import sys


def iniciar_chat():
    """Inicia a interface de chat interativo com o PADOC AI."""
    try:
        ia = PadocAI()
    except Exception as e:
        print(f"Erro ao inicializar PADOC AI: {e}")
        sys.exit(1)

    print("="*50)
    print("     PADOC AI - Diagnóstico Automotivo")
    print("="*50)
    print("\nDigite 'sair' para encerrar.\n")

    while True:
        try:
            pergunta = input("\nVocê: ").strip()

            if not pergunta:
                print("Por favor, digite uma pergunta válida.")
                continue

            if pergunta.lower() == "sair":
                print("\nEncerrando PADOC AI. Até logo!")
                break

            print("\n[Processando...]")
            resposta = ia.diagnosticar(pergunta)

            if resposta:
                print("\nPADOC AI:")
                print(resposta)
                salvar_memoria(pergunta, resposta)
            else:
                print("Erro ao gerar resposta. Tente novamente.")

        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário.")
            break
        except Exception as e:
            print(f"Erro ao processar pergunta: {e}")
