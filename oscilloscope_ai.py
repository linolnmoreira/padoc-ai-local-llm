import pandas as pd
import os
from datetime import datetime


class OscilloscopeAI:

    def analisar(self, csv_path):
        """
        Analisa um arquivo CSV de um osciloscópio, extraindo estatísticas básicas do sinal.
        Assume que o CSV tem as colunas 'Time' e 'Voltage'.
        """
        if not os.path.exists(csv_path):
            return {
                "tipo": "Osciloscópio",
                "sucesso": False,
                "erro": f"Arquivo não encontrado: {csv_path}"
            }

        try:
            dados = pd.read_csv(csv_path)

            # Validação das colunas esperadas
            if 'Time' not in dados.columns or 'Voltage' not in dados.columns:
                return {
                    "tipo": "Osciloscópio",
                    "sucesso": False,
                    "erro": "Arquivo CSV deve conter as colunas 'Time' e 'Voltage'."
                }

            # Cálculo das estatísticas do sinal
            v_max = dados['Voltage'].max()
            v_min = dados['Voltage'].min()
            v_avg = dados['Voltage'].mean()
            amostras = len(dados)
            tempo_total = dados['Time'].iloc[-1] - dados['Time'].iloc[0] if amostras > 1 else 0

            diagnostico = f"Sinal com {amostras} amostras analisado. Tensão varia de {v_min:.2f}V a {v_max:.2f}V."

            return {
                "tipo": "Osciloscópio",
                "sucesso": True,
                "data_analise": datetime.now().isoformat(),
                "arquivo": os.path.basename(csv_path),
                "amostras": amostras,
                "diagnostico": diagnostico,
                "estatisticas": {
                    "tensao_max_v": round(v_max, 3),
                    "tensao_min_v": round(v_min, 3),
                    "tensao_media_v": round(v_avg, 3),
                    "tempo_total_s": round(tempo_total, 4)
                }
            }

        except Exception as e:
            return {
                "tipo": "Osciloscópio",
                "sucesso": False,
                "erro": f"Erro ao processar o arquivo CSV: {e}"
            }