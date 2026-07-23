import logging

logger = logging.getLogger(__name__)

class PadocAgent:

    def analisar_intencao(self, mensagem):
        """Analisa a mensagem do usuário para determinar sua intenção."""
        texto = mensagem.lower()

        if any(palavra in texto for palavra in ["preço", "preco", "orçamento", "orcamento", "quanto custa"]):
            return "orcamento"

        if any(palavra in texto for palavra in ["marcar", "agendar", "agenda"]):
            return "agenda"

        if any(palavra in texto for palavra in ["peça", "peca", "fornecedor"]):
            return "pecas"

        # Se nenhuma intenção específica for encontrada, o padrão é diagnóstico.
        return "diagnostico"

    def executar_tarefa(self, mensagem, usuario_id, ferramentas, dados_extras=None):
        """
        Orquestra a execução da tarefa com base na intenção do usuário.
        Esta é a função central do agente.
        """
        if dados_extras is None:
            dados_extras = {}

        intencao = self.analisar_intencao(mensagem)
        logger.info(f"Intenção detectada: '{intencao}'")

        # Seleciona e executa a ferramenta apropriada
        if intencao == "diagnostico":
            ferramenta_diagnostico = ferramentas.get("diagnostico")
            if ferramenta_diagnostico:
                codigo_obd = dados_extras.get("codigo_obd")
                telemetria = dados_extras.get("telemetria")

                # Se houver dados de telemetria ou um código OBD, usa o método especializado.
                if codigo_obd or telemetria:
                    logger.info("Executando diagnóstico via telemetria.")
                    return ferramenta_diagnostico.diagnosticar_via_telemetria(
                        dtcs=[codigo_obd] if codigo_obd else [],
                        dados_vivos=telemetria if telemetria else {}
                    )
                # Se não houver dados de telemetria, mas houver uma mensagem, usa o cérebro principal.
                elif mensagem:
                    logger.info("Nenhum dado OBD fornecido. Executando diagnóstico via chat com o cérebro da IA.")
                    return ferramenta_diagnostico.diagnosticar(usuario_id, mensagem)
                else:
                    # Caso de borda: intenção de diagnóstico sem nenhuma informação.
                    return "Para iniciar um diagnóstico, por favor, descreva o problema ou forneça um código de erro (OBD)."
            else:
                return "Desculpe, a ferramenta de diagnóstico não está disponível no momento."

        elif intencao == "orcamento":
            ferramenta_orcamento = ferramentas.get("orcamento")
            if ferramenta_orcamento:
                # Para um orçamento, precisamos identificar as peças.
                # Aqui, uma lógica mais avançada poderia usar o LLM para extrair peças da mensagem.
                # Por simplicidade, vamos assumir que a mensagem contém nomes de peças.
                # Ex: "quanto custa para trocar vela e bobina?"
                pecas_identificadas = [p for p in ["vela", "bobina", "pastilha"] if p in mensagem.lower()]
                if not pecas_identificadas:
                    return "Para gerar um orçamento, por favor, me diga quais peças você precisa."
                
                logger.info(f"Executando orçamento para as peças: {pecas_identificadas}")
                orcamento = ferramenta_orcamento.gerar(defeito=mensagem, pecas=pecas_identificadas)
                return f"O orçamento para '{orcamento['problema']}' é de R$ {orcamento['total']:.2f}. Itens: {', '.join([item['item'] for item in orcamento['servicos']])}."
            else:
                return "Desculpe, a ferramenta de orçamento não está disponível no momento."

        # Resposta padrão se a intenção não tiver uma ferramenta configurada
        return "Entendi sua pergunta, mas ainda não tenho uma ferramenta para processar essa solicitação específica."