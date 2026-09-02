import os
from datetime import datetime
import hashlib # Adicionado: Importação do módulo hashlib


class WiringAI:

    def analisar(self, arquivo):

        if not os.path.exists(arquivo):

            return {

                "tipo": "Esquema elétrico",

                "arquivo": arquivo,

                "erro": "Arquivo não encontrado."

            }

        extensao = os.path.splitext(arquivo)[1].lower()

        tamanho = os.path.getsize(arquivo)

        formatos = [

            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".gif",
            ".webp",
            ".tif",
            ".tiff"

        ]

        if extensao not in formatos:

            return {

                "tipo": "Esquema elétrico",

                "arquivo": arquivo,

                "erro": "Formato não suportado."

            }

        sha256 = hashlib.sha256()

        with open(arquivo, "rb") as f:

            while True:

                bloco = f.read(8192)

                if not bloco:
                    break

                sha256.update(bloco)

        componentes = []

        conectores = []

        fusiveis = []

        reles = []

        sensores = []

        atuadores = []

        modulos = []

        fios = []

        diagnostico = []

        diagnostico.append("Esquema carregado com sucesso.")

        return {

            "tipo": "Esquema elétrico",

            "arquivo": arquivo,

            "nome_arquivo": os.path.basename(arquivo),

            "extensao": extensao,

            "tamanho_bytes": tamanho,

            "hash_sha256": sha256.hexdigest(),

            "data_analise": datetime.now().isoformat(),

            "componentes": componentes,

            "conectores": conectores,

            "fusiveis": fusiveis,

            "reles": reles,

            "sensores": sensores,

            "atuadores": atuadores,

            "modulos": modulos,

            "fios": fios,

            "diagnostico": diagnostico,

            "ocr": False,

            "ia": False,

            "status": "Pronto para análise"

        }

    def detectar_componente(self, nome):

        nome = nome.upper()

        if "ECU" in nome or "PCM" in nome or "BCM" in nome:
            return "Módulo"
        if "ABS" in nome:
            return "Módulo ABS"
        if "F" in nome:
            return "Fusível"
        if "R" in nome:
            return "Relé"
        if "SENSOR" in nome:
            return "Sensor"
        if "MOTOR" in nome:
            return "Atuador"

        return "Desconhecido"

    def validar_formato(self, arquivo):

        extensao = os.path.splitext(arquivo)[1].lower()

        return extensao in [

            ".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif",
            ".tiff"

        ]

    def calcular_hash(self, arquivo):

        sha256 = hashlib.sha256()

        with open(arquivo, "rb") as f:

            while True:

                bloco = f.read(8192)

                if not bloco:
                    break

                sha256.update(bloco)

        return sha256.hexdigest()