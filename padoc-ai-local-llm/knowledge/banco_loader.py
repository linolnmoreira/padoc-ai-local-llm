"""Carregador de base de dados JSON para PADOC AI

Carrega todos os datasets do diretório knowledge/ e os combina em uma
estrutura unificada para uso pelo motor LLM.
"""

import glob
import json
import os


def carregar_base():
    """Carrega todos os datasets JSON do diretório knowledge.

    O arquivo principal `banco_automotivo.json` mantém suas chaves no nível raiz.
    Demais arquivos JSON são adicionados sob uma chave nomeada pelo arquivo.
    
    Returns:
        Dicionário com todos os dados carregados
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_files = sorted(glob.glob(os.path.join(base_path, "*.json")))

    if not json_files:
        return {}

    base = {}

    for file_path in json_files:
        filename = os.path.basename(file_path)
        
        try:
            with open(file_path, "r", encoding="utf-8") as arquivo:
                data = json.load(arquivo)
                
            if not isinstance(data, (dict, list)):
                continue

            if filename == "banco_automotivo.json":
                base.update(data)
            else:
                key = os.path.splitext(filename)[0]
                base[key] = data

        except (FileNotFoundError, json.JSONDecodeError, OSError):
            continue
        except Exception:
            continue

    return base
