class BudgetAI:

    def gerar(
        self,
        defeito,
        pecas
    ):
        tabela = {
            "vela": 120,
            "bobina": 450,
            "pastilha": 300
        }

        total = 0
        lista = []

        for p in pecas:
            p_clean = p.lower().strip()
            valor = tabela.get(
                p_clean,
                0
            )
            total += valor
            lista.append(
                {
                    "item": p_clean,
                    "valor": valor
                }
            )

        return {
            "problema":
            defeito,
            "servicos":
            lista,
            "total":
            total
        }