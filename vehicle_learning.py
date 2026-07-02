import pandas as pd

class FleetLearning:

    def analisar_frota(
        self,
        arquivo
    ):
        dados = pd.read_csv(
            arquivo
        )
        resumo = dados.groupby(
            "defeito"
        ).count()
        return resumo