"""
PADOC AI - Módulo de Memória do Veículo

Usa SQLite para persistir o histórico de cada veículo.
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'memory', 'padoc_memory.db')

class VehicleMemory:
    """
    Gerencia o banco de dados de veículos e seus históricos.
    """
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._criar_tabela()

    def _get_conn(self):
        return sqlite3.connect(DB_PATH)

    def _criar_tabela(self):
        """Cria a tabela de veículos se ela não existir."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            placa TEXT PRIMARY KEY,
            modelo TEXT NOT NULL,
            km INTEGER,
            historico TEXT,
            ultima_atualizacao TEXT
        )
        """)
        conn.commit()
        conn.close()

    def salvar(self, placa: str, modelo: str, km: int, historico: str):
        """Salva ou atualiza os dados de um veículo."""
        conn = self._get_conn()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        # Usamos INSERT OR REPLACE para criar ou atualizar o registro
        cursor.execute("""
        INSERT OR REPLACE INTO veiculos (placa, modelo, km, historico, ultima_atualizacao)
        VALUES (?, ?, ?, ?, ?)
        """, (placa.upper(), modelo, km, historico, now))
        
        conn.commit()
        conn.close()

    def memoria(self, placa: str):
        """Busca um veículo pela placa."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row # Retorna resultados como dicionários
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM veiculos WHERE placa = ?", (placa.upper(),))
        veiculo = cursor.fetchone()
        
        conn.close()
        return veiculo

def carregar_historico_geral(linhas_max: int = 5) -> list:
    """
    Carrega as interações mais recentes da base de aprendizado para fornecer contexto.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    conhecimento_path = os.path.normpath(os.path.join(base_path, '..', 'memory', 'conhecimento.json'))

    if not os.path.exists(conhecimento_path):
        return []

    try:
        with open(conhecimento_path, "r", encoding="utf-8") as f:
            base = json.load(f)
        
        # Converte o dicionário de interações em uma lista
        interacoes = list(base.values())
        
        # Ordena por data de criação, da mais recente para a mais antiga
        interacoes.sort(key=lambda x: x.get("criado", ""), reverse=True)
        
        # Retorna as 'linhas_max' mais recentes
        return interacoes[:linhas_max]

    except (json.JSONDecodeError, IOError):
        return []