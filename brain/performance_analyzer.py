"""
Módulo de Análise de Desempenho de Veículos - PADOC AI

Este módulo carrega dados históricos de desempenho de veículos (como o dataset Auto MPG)
e fornece uma interface para consultá-los de forma eficiente usando pandas.
"""

import os
import json
import pandas as pd
from typing import Dict, Optional

class PerformanceAnalyzer:
    """
    Carrega e analisa dados de desempenho de veículos a partir de um arquivo JSON.
    """

    def __init__(self, data_path: Optional[str] = None):
        """
        Inicializa o analisador, carregando os dados para um DataFrame do pandas.

        Args:
            data_path (Optional[str]): Caminho para o arquivo JSON. Se None, busca
                                       em 'knowledge/dados_desempenho_veiculos.json'.
        """
        if data_path is None:
            base_path = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.normpath(
                os.path.join(base_path, "..", "knowledge", "dados_desempenho_veiculos.json")
            )

        self.df = self._load_data(data_path)

    def _load_data(self, path: str) -> pd.DataFrame:
        """Carrega o JSON e o converte para um DataFrame pandas."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data.get("veiculos", []))

            # Limpeza de dados: converte colunas para numérico e trata valores ausentes
            for col in ['mpg', 'horsepower']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Preenche 'horsepower' ausente com a média daquele número de cilindros
            df['horsepower'] = df.groupby('cylinders')['horsepower'].transform(
                lambda x: x.fillna(x.mean())
            )
            df.dropna(inplace=True) # Remove outras linhas com dados ausentes

            # Converte MPG para Km/L (1 MPG = 0.425 Km/L)
            df['kml'] = df['mpg'] * 0.425144

            return df

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Aviso: Falha ao carregar dados de desempenho: {e}")
            return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

    def consultar_desempenho(self, nome_veiculo: str) -> Optional[Dict]:
        """
        Busca os dados de desempenho de um veículo específico pelo nome.

        Args:
            nome_veiculo (str): Parte do nome do veículo a ser buscado (ex: 'maverick').

        Returns:
            Optional[Dict]: Um dicionário com os dados médios do veículo encontrado,
                            ou None se não for encontrado.
        """
        if self.df.empty:
            return None

        # Busca por veículos que contenham o nome (ignorando maiúsculas/minúsculas)
        resultados = self.df[self.df['name'].str.contains(nome_veiculo, case=False, na=False)]

        if resultados.empty:
            return None

        # Calcula a média se houver múltiplos resultados (ex: para vários anos do mesmo modelo)
        dados_medios = resultados.mean(numeric_only=True)

        # Monta uma resposta amigável
        resposta = {
            "veiculo_encontrado": nome_veiculo,
            "modelos_analisados": len(resultados),
            "consumo_medio_kml": round(dados_medios['kml'], 2),
            "potencia_media_hp": round(dados_medios['horsepower'], 1),
            "cilindros_medio": int(round(dados_medios['cylinders'])),
            "peso_medio_kg": int(round(dados_medios['weight'] * 0.453592)), # lbs para kg
            "aceleracao_0_100_s": round(dados_medios['acceleration'], 1),
            "ano_medio": int(round(dados_medios['year']) + 1900)
        }
        return resposta

# --- Padrão Singleton para reutilizar a instância e o DataFrame carregado ---
_performance_analyzer_instance = None

def get_performance_analyzer_instance():
    global _performance_analyzer_instance
    if _performance_analyzer_instance is None:
        _performance_analyzer_instance = PerformanceAnalyzer()
    return _performance_analyzer_instance