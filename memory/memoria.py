"""Módulo de memória e histórico de conversas PADOC AI"""

import json
import os
from datetime import datetime


def salvar_memoria(pergunta, resposta):
    """Salva pergunta e resposta no histórico de conversas.
    
    Args:
        pergunta: Pergunta do usuário
        resposta: Resposta da IA
        
    Returns:
        True se salvo com sucesso, False caso contrário
    """
    # Validação de entrada
    if not pergunta or not resposta:
        return False

    if not isinstance(pergunta, str) or not isinstance(resposta, str):
        return False

    try:
        dados = {
            "data": datetime.now().isoformat(),
            "pergunta": pergunta.strip(),
            "resposta": resposta.strip()
        }

        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "historico.json")

        # Cria diretório se não existir
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(dados, ensure_ascii=False) + "\n")

        return True

    except (IOError, OSError):
        return False
    except Exception:
        return False


def carregar_historico_geral(linhas_max=10):
    """Carrega os últimos registros do histórico.
    
    Args:
        linhas_max: Número máximo de registros a carregar
        
    Returns:
        Lista com dicionários de histórico
    """
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "historico.json")

        if not os.path.exists(file_path):
            return []

        historico = []
        with open(file_path, "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()
            for linha in linhas[-linhas_max:]:
                try:
                    historico.append(json.loads(linha))
                except json.JSONDecodeError:
                    continue

        return historico

    except Exception:
        return []
