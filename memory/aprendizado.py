"""
PADOC AI - Sistema de evolução e aprendizado incremental
"""

import json
import os
from datetime import datetime


BASE = os.path.dirname(os.path.abspath(__file__))


CONHECIMENTO = os.path.join(
    BASE,
    "conhecimento.json"
)


FEEDBACK = os.path.join(
    BASE,
    "feedback.json"
)


def carregar_base():
    """Carrega a base de conhecimento a partir de um arquivo JSON."""
    if not os.path.exists(CONHECIMENTO):
        return {}

    try:
        with open(
            CONHECIMENTO,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def salvar_base(base):
    """Salva a base de conhecimento em um arquivo JSON."""
    os.makedirs(os.path.dirname(CONHECIMENTO), exist_ok=True)
    with open(
        CONHECIMENTO,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            base,
            f,
            indent=4,
            ensure_ascii=False
        )


def aprender(pergunta, resposta):
    """
    PADOC aprende uma nova informação ou reforça um conhecimento existente.
    """
    base = carregar_base()
    chave = pergunta.lower().strip()

    if chave not in base:
        base[chave] = {
            "pergunta": pergunta,
            "resposta": resposta,
            "vezes_usado": 1,
            "criado": datetime.now().isoformat()
        }
    else:
        base[chave]["vezes_usado"] += 1

    salvar_base(base)
    return True


def buscar_conhecimento(pergunta):
    """Busca o conhecimento mais relevante para uma dada pergunta."""
    base = carregar_base()
    pergunta_lower = pergunta.lower().strip()

    melhores = []

    for chave, dado in base.items():
        if chave in pergunta_lower:
            melhores.append(dado)

    if melhores:
        # Ordena por relevância (quantas vezes foi usado)
        melhores.sort(
            key=lambda x: x["vezes_usado"],
            reverse=True
        )
        return melhores[0]

    return None


def registrar_feedback(pergunta, resposta_correta):
    """
    Registra um feedback (correção) de um especialista e usa-o para aprender.
    """
    dados = {
        "data": datetime.now().isoformat(),
        "pergunta": pergunta,
        "resposta_correta": resposta_correta
    }

    historico = []
    os.makedirs(os.path.dirname(FEEDBACK), exist_ok=True)

    if os.path.exists(FEEDBACK):
        try:
            with open(FEEDBACK, "r", encoding="utf-8") as f:
                historico = json.load(f)
        except (json.JSONDecodeError, IOError):
            historico = []

    historico.append(dados)

    with open(FEEDBACK, "w", encoding="utf-8") as f:
        json.dump(
            historico,
            f,
            indent=4,
            ensure_ascii=False
        )

    # Transforma o feedback em aprendizado
    aprender(
        pergunta,
        resposta_correta
    )

    return True


if __name__ == '__main__':
    # Exemplo de como o módulo funciona

    pergunta_exemplo = "Meu carro está falhando quando acelero"
    resposta_exemplo = "Pode ser vela, bobina ou combustível adulterado. Verifique primeiro as velas."

    # 1. A IA aprende uma nova associação
    print(f"Aprendendo: '{pergunta_exemplo}' -> '{resposta_exemplo}'")
    aprender(pergunta_exemplo, resposta_exemplo)

    # 2. A IA consulta sua memória para uma pergunta similar
    print("\nConsultando a memória para: 'carro falhando na aceleração'")
    resultado = buscar_conhecimento("carro falhando na aceleração")

    if resultado:
        print("\nConhecimento encontrado:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print("\nNenhum conhecimento encontrado para essa consulta.")