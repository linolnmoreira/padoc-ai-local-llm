class PartsAgent:

    def comparar(
        self,
        peca
    ):
        fornecedores = {
            "vela": [
                {
                    "nome": "Fornecedor A",
                    "preco": 90
                },
                {
                    "nome": "Fornecedor B",
                    "preco": 75
                }
            ]
        }

        return fornecedores.get(
            peca.lower().strip(),
            []
        )

    def escolher_melhor(
        self,
        peca
    ):
        lista = self.comparar(
            peca
        )
        if not lista:
            return {"erro": "Nenhum fornecedor encontrado para esta peça"}

        return min(lista, key=lambda x: x["preco"])