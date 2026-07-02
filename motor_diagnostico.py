"""
PADOC AI
Motor de diagnóstico automotivo
"""


import csv
import os


BASE = os.path.dirname(os.path.abspath(__file__))


ARQUIVO = os.path.join(
    BASE,
    "treinamento",
    "defeitos.csv"
)



def carregar_defeitos():

    dados=[]


    if not os.path.exists(ARQUIVO):
        return []


    with open(
        ARQUIVO,
        encoding="utf-8"
    ) as arquivo:


        leitor = csv.DictReader(arquivo)


        for linha in leitor:

            dados.append(linha)



    return dados


def diagnosticar(sintoma):
    banco = carregar_defeitos()
    resultado = []
    sintoma_lower = sintoma.lower()

    for item in banco:
        if item["sintoma"].lower() in sintoma_lower:
            resultado.append({
                "problema": item["defeito"],
                "causa": item["causa"],
                "solucao": item["solucao"]
            })

    return resultado