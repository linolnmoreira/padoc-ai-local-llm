from brain.agente_autonomo import AgenteAutonomo
import json

def run_tests():
    """Executa os testes para o novo AgenteAutonomo."""
    
    ia = AgenteAutonomo()

    print("--- Teste 1: Analisando sintoma 'Meu carro está falhando' ---")
    resultado1 = ia.analisar("Meu carro está falhando")
    print(json.dumps(resultado1, indent=2, ensure_ascii=False))
    print("-" * 60)

    print("\n--- Teste 2: Analisando código OBD 'P0300' ---")
    resultado2 = ia.analisar("P0300")
    print(json.dumps(resultado2, indent=2, ensure_ascii=False))
    print("-" * 60)

    print("\n--- Teste 3: Criando orçamento para 'falha motor' ---")
    resultado3 = ia.criar_orcamento("falha motor")
    print(json.dumps(resultado3, indent=2, ensure_ascii=False))
    print("-" * 60)

if __name__ == "__main__":
    # Garante que os diretórios necessários existam antes de rodar
    import os
    os.makedirs("brain/treinamento", exist_ok=True)
    
    run_tests()