class PadocAgent:

    def analisar_intencao(
        self,
        mensagem
    ):
        texto = mensagem.lower()

        if "preço" in texto or "preco" in texto or "orçamento" in texto or "orcamento" in texto:
            return "orcamento"

        if "marcar" in texto or "agendar" in texto or "agenda" in texto:
            return "agenda"

        if "peça" in texto or "peca" in texto or "fornecedor" in texto:
            return "pecas"

        return "diagnostico"

    def executar(
        self,
        mensagem
    ):
        acao = self.analisar_intencao(
            mensagem
        )

        return acao