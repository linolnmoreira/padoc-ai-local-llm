"""
PADOC AI
Agente Autônomo
"""


from motor_diagnostico import diagnosticar # Corrigido: Caminho de importação
from obd2_learning import consultar_codigo # Corrigido: Caminho de importação
from recomendador_pecas import recomendar # Corrigido: Caminho de importação
from orcamento_ai import gerar_orcamento # Corrigido: Caminho de importação




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