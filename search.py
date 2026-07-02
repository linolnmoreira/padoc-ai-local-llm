import json
import os

class OBDKnowledge:
    def __init__(self):
        path = "brain/datasets/obd2/codigos.json"
        if os.path.exists(path):
            with open(path, encoding="utf8") as f:
                self.base = json.load(f)
        else:
            self.base = []

    def pesquisar(self, codigo):
        for item in self.base:
            if item["codigo"].upper() == codigo.upper():
                # Retorna string formatada para o contexto do LLM
                return f"Descrição: {item['descricao']}. Causas: {', '.join(item['causas'])}. Solução: {item['solucao']}"
        return "Código não encontrado na base técnica."