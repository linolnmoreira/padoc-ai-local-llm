"""
PADOC AI
Aprendizado de frota a partir de diagnósticos registrados.
"""

import json
import os
from collections import defaultdict


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(BASE_DIR, "dados", "diagnosticos.json")


def registrar_diagnostico(veiculo, problema, solucao):
    """Registra um novo diagnóstico no banco de dados JSON."""
    os.makedirs(os.path.dirname(ARQUIVO), exist_ok=True)
    banco = []

    try:
        if os.path.exists(ARQUIVO) and os.path.getsize(ARQUIVO) > 0:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                banco = json.load(f)
    except (json.JSONDecodeError, IOError):
        banco = []

    banco.append({
        "veiculo": veiculo,
        "problema": problema,
        "solucao": solucao
    })

    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(banco, f, indent=4, ensure_ascii=False)


def aprender_padrao():
    """Analisa todos os diagnósticos e agrupa soluções por problema."""
    if not os.path.exists(ARQUIVO):
        return {"aviso": "Nenhum dado de diagnóstico para aprender."}

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"erro": "Não foi possível ler os dados de diagnóstico."}

    aprendizado = defaultdict(list)

    for item in dados:
        chave = item.get("problema")
        solucao = item.get("solucao")
        if chave and solucao:
            aprendizado[chave].append(solucao)

    return dict(aprendizado)