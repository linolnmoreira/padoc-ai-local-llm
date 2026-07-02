from brain.llm.model import PadocLLM
from brain.rag.search import OBDKnowledge

class PadocCore:
    def __init__(self):
        self.llm = PadocLLM()
        self.obd = OBDKnowledge()

    def diagnosticar(self, codigo, pergunta):
        # Recupera conhecimento técnico específico do código OBD2
        conhecimento = self.obd.pesquisar(codigo)
        
        # Gera resposta usando o LLM com o contexto injetado
        resposta = self.llm.responder(
            conhecimento,
            pergunta
        )
        
        return resposta