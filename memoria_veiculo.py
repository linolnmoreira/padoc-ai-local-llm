"""
Histórico inteligente do carro
"""

import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(BASE_DIR, "dados", "veiculos.json")


def salvar_veiculo(placa, dados):
    """Salva ou atualiza os dados de um veículo."""
    os.makedirs(os.path.dirname(ARQUIVO), exist_ok=True)
    banco = {}

    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                banco = json.load(f)
        except (json.JSONDecodeError, IOError):
            banco = {}

    banco[placa] = dados

    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(banco, f, indent=4, ensure_ascii=False)


def consultar_veiculo(placa):
    """Consulta os dados de um veículo pela placa."""
    if not os.path.exists(ARQUIVO):
        return None

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            banco = json.load(f)
        return banco.get(placa)
    except (json.JSONDecodeError, IOError):
        return None


# Exemplo de uso e criação do arquivo de dados se não existir
if __name__ == "__main__":
    if not os.path.exists(ARQUIVO):
        salvar_veiculo(
            "ABC1234",
            {
                "modelo": "Toyota Corolla",
                "km": 85000,
                "historico": [
                    "troca vela",
                    "troca óleo"
                ]
            }
        )
    print(f"Módulo memoria_veiculo.py pronto. Dados em: {ARQUIVO}")