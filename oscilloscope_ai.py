import pandas as pd

class OscilloscopeAI:

    def analisar(self,csv):

        dados=pd.read_csv(csv)

        return{

            "tipo":"Osciloscópio",

            "amostras":len(dados),

            "diagnostico":"Sinal importado."

        }