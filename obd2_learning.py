"""
PADOC AI
Aprendizado OBD2
"""


import csv
import os



BASE=os.path.dirname(
os.path.abspath(__file__)
)



ARQUIVO=os.path.join(
BASE,
"treinamento",
"codigos_obd2.csv"
)




def consultar_codigo(codigo):


    if not os.path.exists(ARQUIVO):
        return None



    with open(
        ARQUIVO,
        encoding="utf-8"
    ) as arquivo:


        leitor=csv.DictReader(arquivo)



        for linha in leitor:


            if linha["codigo"] == codigo:


                return {


                "descricao":
                linha["descricao"],


                "causa":
                linha["causa"],


                "reparo":
                linha["reparo"]


                }


    return None