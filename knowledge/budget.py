"""
PADOC AI - Módulo de Orçamento (Simulado)
"""

class BudgetAI:
    """Gera orçamentos simulados para serviços."""
    def __init__(self):
        pass

    def gerar(self, servico: str, pecas: list) -> dict:
        """Simula a geração de um orçamento."""
        custo_pecas = len(pecas) * 150.0  # Custo simulado por peça
        mao_de_obra = 200.0  # Custo simulado
        return {
            "servico": servico,
            "custo_estimado_pecas": f"R$ {custo_pecas:.2f}",
            "custo_mao_de_obra": f"R$ {mao_de_obra:.2f}",
            "total_estimado": f"R$ {custo_pecas + mao_de_obra:.2f}",
            "observacao": "Este é um orçamento simulado e pode variar."
        }