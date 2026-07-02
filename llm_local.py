"""
PADOC AI
Modelo de linguagem local baseado em memória JSON.
"""

import json
import os


BASE = os.path.dirname(os.path.abspath(__file__))
MEMORIA = os.path.join(BASE, "memoria_modelo.json")


def carregar_memoria():
    """Carrega a memória do modelo a partir de um arquivo JSON."""
    if not os.path.exists(MEMORIA):
        return {}

    try:
        with open(MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def aprender(pergunta, resposta):
    """Adiciona uma nova pergunta e resposta à memória do modelo."""
    memoria = carregar_memoria()
    chave = pergunta.lower().strip()

    # Incrementa o contador de uso ou inicializa
    vezes = memoria.get(chave, {}).get("vezes", 0) + 1
    memoria[chave] = {
        "resposta": resposta,
        "vezes": vezes
    }

    with open(MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, indent=4, ensure_ascii=False)


def responder(pergunta):
    """Busca uma resposta na memória com base na pergunta."""
    memoria = carregar_memoria()
    pergunta_lower = pergunta.lower().strip()

    for chave, dado in memoria.items():
        if chave in pergunta_lower:
            return dado["resposta"]

    return "Ainda estou aprendendo esse diagnóstico."


# Placeholder para o arquivo de memória
if not os.path.exists(MEMORIA):
    with open(MEMORIA, "w", encoding="utf-8") as f:
        json.dump({}, f)