"""
PADOC AI
Recomendador inteligente de peças
"""


pecas = {


"falha motor":[

"vela de ignição",
"bobina",
"bico injetor"

],


"freio":[

"pastilha",
"disco",
"fluido de freio"

],


"suspensão":[

"amortecedor",
"bucha",
"pivô"

]

}


def recomendar(problema):
    problema_lower = problema.lower()
    for chave, item in pecas.items():
        if chave in problema_lower:
            return item
    return ["Necessário diagnóstico avançado"]