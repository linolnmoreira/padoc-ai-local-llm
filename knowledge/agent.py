"""
PADOC AI - Agente de Intenção

Este módulo determina a intenção principal do usuário com base na mensagem.
"""

class PadocAgent:
    """
    Um agente simples baseado em regras para classificar a intenção do usuário.
    """
    def __init__(self):
        self.regras_intencao = {
            "orcamento": ["quanto custa", "orçamento", "preço para", "valor para"],
            "agenda": ["agendar", "marcar", "horário para", "posso levar"],
            "pecas": ["qual peça", "fornecedor", "melhor marca", "onde comprar"]
        }

    def executar(self, mensagem: str) -> str:
        """
        Analisa a mensagem do usuário e retorna a intenção detectada.

        Args:
            mensagem: A mensagem do usuário.

        Returns:
            A intenção ("orcamento", "agenda", "pecas", "diagnostico").
        """
        mensagem_lower = mensagem.lower()
        for intencao, palavras_chave in self.regras_intencao.items():
            if any(palavra in mensagem_lower for palavra in palavras_chave):
                return intencao
        
        # Se nenhuma intenção específica for encontrada, o padrão é diagnóstico.
        return "diagnostico"