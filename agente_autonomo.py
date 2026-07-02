"""
PADOC AI
Agente Autônomo
"""


from brain.motor_diagnostico import diagnosticar
from brain.obd2_learning import consultar_codigo
from brain.recomendador_pecas import recomendar
from brain.orcamento_ai import gerar_orcamento




class AgenteAutonomo:



    def analisar(self, entrada):


        resultado={}



        if entrada.startswith("P"):


            resultado["OBD2"] = consultar_codigo(
            entrada
            )



        else:


            resultado["diagnostico"] = diagnosticar(
            entrada
            )



            resultado["pecas"] = recomendar(
            entrada
            )



        return resultado


    def criar_orcamento(
        self,
        problema
    ):


        pecas = recomendar(
        problema
        )


        return gerar_orcamento(

        problema,

        pecas,

        250

        )