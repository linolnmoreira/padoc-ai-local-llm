"""
PADOC AI - Módulo de Busca em Base de Conhecimento (RAG) para OBD.
"""
import json
import os

class OBDKnowledge:
    """
    Busca informações sobre códigos OBD em uma base de conhecimento JSON.
    """
    def __init__(self):
        self.base_conhecimento = self._carregar_base()

    def _carregar_base(self):
        """Carrega o arquivo JSON com dados de códigos OBD."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        # O arquivo está em 'knowledge/historico_oficina.json'
        json_path = os.path.normpath(os.path.join(base_path, "..", "..", "knowledge", "historico_oficina.json"))
        
        if not os.path.exists(json_path):
            print(f"Aviso: Arquivo de conhecimento OBD não encontrado em {json_path}")
            return []
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print(f"Aviso: Erro ao carregar ou decodificar {json_path}")
            return []

    def pesquisar(self, codigo_obd: str) -> str:
        """Pesquisa por um código OBD na base de conhecimento."""
        codigo_obd_upper = codigo_obd.upper()
        for item in self.base_conhecimento:
            if item.get("codigo_obd2") == codigo_obd_upper:
                # Retorna uma string formatada com as informações encontradas
                return f"Defeito: {item.get('defeito', 'N/A')}. Causas Prováveis: {', '.join(item.get('causas_provaveis', []))}. Histórico: {item.get('historico_reparacao', 'Nenhum')}"
        
        return f"Nenhuma informação encontrada para o código {codigo_obd}."