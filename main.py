from core.agent import PadocAgent
from core.llm_padoc import PadocLLM
from business.budget import BudgetAI
from business.parts_agent import PartsAgent

print(
"""
=====================
 PADOC CORE AI ENGINE
=====================
"""
)

agent = PadocAgent()
llm = PadocLLM()
orcamento = BudgetAI()
pecas = PartsAgent()

mensagem = input(
"Motorista: "
)

acao = agent.executar(
mensagem
)

print(
"PADOC executando:",
acao
)

if acao == "orcamento":
    print(
        orcamento.gerar("falha motor", ["vela"])
    )
elif acao == "pecas":
    print(
        pecas.escolher_melhor("vela")
    )
else:
    print(
        llm.responder("Base mecânica PADOC", mensagem)
    )