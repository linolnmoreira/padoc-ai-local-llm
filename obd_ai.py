import json
import os
from datetime import datetime


class OBDAI:

    def __init__(self):
        self.database = {
            "P0100": {
                "descricao": "Falha no circuito do sensor MAF",
                "categoria": "Motor",
                "gravidade": "Média",
                "criticidade": False,
                "causas": [
                    "Sensor MAF defeituoso",
                    "Conector oxidado",
                    "Fiação rompida",
                    "Filtro de ar obstruído"
                ],
                "sintomas": [
                    "Perda de potência",
                    "Consumo elevado",
                    "Marcha lenta irregular"
                ],
                "testes": [
                    "Medir alimentação do MAF",
                    "Verificar sinal do sensor",
                    "Inspecionar chicote"
                ],
                "reparos": [
                    "Limpar sensor",
                    "Trocar sensor",
                    "Reparar chicote"
                ]
            },

            "P0171": {
                "descricao": "Mistura pobre Banco 1",
                "categoria": "Combustível",
                "gravidade": "Alta",
                "criticidade": False,
                "causas": [
                    "Entrada falsa de ar",
                    "Bomba de combustível",
                    "Filtro entupido",
                    "MAF defeituoso"
                ],
                "sintomas": [
                    "Motor falhando",
                    "Consumo elevado",
                    "Luz da injeção"
                ],
                "testes": [
                    "Teste de pressão",
                    "Teste do MAF",
                    "Teste de fumaça"
                ],
                "reparos": [
                    "Eliminar vazamentos",
                    "Trocar filtro",
                    "Trocar bomba"
                ]
            },

            "P0300": {
                "descricao": "Falhas múltiplas de combustão",
                "categoria": "Ignição",
                "gravidade": "Alta",
                "criticidade": True,
                "causas": [
                    "Velas",
                    "Bobinas",
                    "Combustível",
                    "Compressão"
                ],
                "sintomas": [
                    "Motor tremendo",
                    "Perda de potência",
                    "Catalisador superaquecendo"
                ],
                "testes": [
                    "Teste de bobinas",
                    "Teste de compressão",
                    "Scanner em tempo real"
                ],
                "reparos": [
                    "Trocar velas",
                    "Trocar bobinas",
                    "Verificar injetores"
                ]
            },

            "P0420": {
                "descricao": "Eficiência do catalisador abaixo do limite",
                "categoria": "Emissões",
                "gravidade": "Média",
                "criticidade": False,
                "causas": [
                    "Catalisador",
                    "Sonda lambda",
                    "Falhas de combustão"
                ],
                "sintomas": [
                    "Check Engine",
                    "Consumo elevado"
                ],
                "testes": [
                    "Comparar sondas",
                    "Temperatura do catalisador"
                ],
                "reparos": [
                    "Trocar catalisador",
                    "Trocar sonda"
                ]
            }
        }

    def analisar(self, dtcs):

        resultado = []

        score = 100

        critico = False

        for codigo in dtcs:

            codigo = codigo.upper()

            if codigo in self.database:

                item = self.database[codigo]

                if item["gravidade"] == "Alta":
                    score -= 20

                elif item["gravidade"] == "Média":
                    score -= 10

                if item["criticidade"]:
                    critico = True

                resultado.append({

                    "codigo": codigo,

                    "descricao": item["descricao"],

                    "categoria": item["categoria"],

                    "gravidade": item["gravidade"],

                    "criticidade": item["criticidade"],

                    "causas": item["causas"],

                    "sintomas": item["sintomas"],

                    "testes": item["testes"],

                    "reparos": item["reparos"]

                })

            else:

                score -= 5

                resultado.append({

                    "codigo": codigo,

                    "descricao": "Código não encontrado",

                    "categoria": "Desconhecida",

                    "gravidade": "Indefinida",

                    "criticidade": False,

                    "causas": [],

                    "sintomas": [],

                    "testes": [],

                    "reparos": []

                })

        score = max(score, 0)

        if score >= 90:
            estado = "Excelente"

        elif score >= 70:
            estado = "Bom"

        elif score >= 50:
            estado = "Regular"

        elif score >= 30:
            estado = "Ruim"

        else:
            estado = "Crítico"

        return {

            "tipo": "OBD",

            "data": datetime.now().isoformat(),

            "quantidade_codigos": len(dtcs),

            "codigos": resultado,

            "score_motor": score,

            "estado_motor": estado,

            "falha_critica": critico

        }

    def carregar_database(self, arquivo_json):

        if not os.path.exists(arquivo_json):
            return False

        with open(arquivo_json, "r", encoding="utf-8") as f:
            self.database = json.load(f)

        return True

    def salvar_database(self, arquivo_json):

        with open(arquivo_json, "w", encoding="utf-8") as f:
            json.dump(
                self.database,
                f,
                indent=4,
                ensure_ascii=False
            )