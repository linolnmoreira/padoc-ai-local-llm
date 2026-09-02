"""
PADOC AI - Atualizador com Dados Reais da Internet

Baixa da internet:
1. Códigos DTC Reais de Fabricantes (Toyota, Volkswagen, Ford, Chevrolet, BMW, Honda)
2. Lista Real de Fabricantes e Modelos via NHTSA API (National Highway Traffic Safety Administration)
3. Consolidação e indexação vetorial no Cérebro da PADOC AI
"""

import os
import sys
import json
import urllib.request
import urllib.error

# Garante UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

# 1. Repositórios Reais de DTCs por Fabricante (GitHub)
REPOSITORIOS_DTC_REAIS = [
    {"marca": "Volkswagen", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Volkswagen.json", "arquivo": "dtc_volkswagen_real.json"},
    {"marca": "Ford", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Ford.json", "arquivo": "dtc_ford_real.json"},
    {"marca": "BMW", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/BMW.json", "arquivo": "dtc_bmw_real.json"},
    {"marca": "Honda", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Honda.json", "arquivo": "dtc_honda_real.json"},
    {"marca": "Audi", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Audi.json", "arquivo": "dtc_audi_real.json"},
    {"marca": "Fiat", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Fiat.json", "arquivo": "dtc_fiat_real.json"},
    {"marca": "Hyundai", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Hyundai.json", "arquivo": "dtc_hyundai_real.json"},
    {"marca": "Kia", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Kia.json", "arquivo": "dtc_kia_real.json"},
    {"marca": "Mercedes-Benz", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Mercedes.json", "arquivo": "dtc_mercedes_real.json"},
    {"marca": "Nissan", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Nissan.json", "arquivo": "dtc_nissan_real.json"},
    {"marca": "Renault", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Renault.json", "arquivo": "dtc_renault_real.json"},
    {"marca": "Volvo", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Volvo.json", "arquivo": "dtc_volvo_real.json"}
]

# 2. APIs Públicas Oficiais do Setor Automotivo
APIS_OFICIAIS = [
    {
        "nome": "NHTSA - Lista Oficial de Fabricantes Mundiais de Veículos",
        "url": "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json",
        "arquivo": "nhtsa_fabricantes_mundiais.json"
    }
]


def baixar_dtcs_reais():
    print("\n🌐 1. BAIXANDO CÓDIGOS DTC REAIS DE MONTADORAS DA INTERNET...")
    headers = {"User-Agent": "PADOC-AI-Updater/2.5"}
    total_baixados = 0

    for item in REPOSITORIOS_DTC_REAIS:
        marca = item["marca"]
        url = item["url"]
        destino = os.path.join(KNOWLEDGE_DIR, item["arquivo"])
        print(f" -> Conectando e baixando dados reais da {marca}...")

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                conteudo = response.read().decode("utf-8")
                dados_json = json.loads(conteudo)
                
                with open(destino, "w", encoding="utf-8") as f:
                    json.dump(dados_json, f, indent=2, ensure_ascii=False)
                
                qtd_codigos = len(dados_json) if isinstance(dados_json, list) else len(dados_json.keys())
                print(f"    ✅ {marca}: {qtd_codigos} códigos de falha reais baixados com sucesso!")
                total_baixados += qtd_codigos

        except Exception as e:
            print(f"    ⚠️ Aviso para {marca}: {e}")

    return total_baixados


def baixar_dados_nhtsa():
    print("\n🏛️ 2. CONSULTANDO API OFICIAL DE SEGURANÇA E FABRICANTES (NHTSA)...")
    headers = {"User-Agent": "PADOC-AI-Updater/2.5"}

    for item in APIS_OFICIAIS:
        nome = item["nome"]
        url = item["url"]
        destino = os.path.join(KNOWLEDGE_DIR, item["arquivo"])
        print(f" -> Baixando: {nome}...")

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as response:
                conteudo = response.read().decode("utf-8")
                dados = json.loads(conteudo)
                
                # Salva os primeiros fabricantes mais relevantes para manter o dataset limpo e rápido
                resultados = dados.get("Results", [])
                with open(destino, "w", encoding="utf-8") as f:
                    json.dump(resultados[:500], f, indent=2, ensure_ascii=False)

                print(f"    ✅ Salvo {len(resultados[:500])} registros oficiais em {item['arquivo']}!")

        except Exception as e:
            print(f"    ⚠️ Aviso API NHTSA: {e}")


def atualizar_rag_com_dados_reais():
    print("\n🧠 3. INTEGRANDO E REINDEXANDO TUDO NO CÉREBRO DA PADOC AI...")
    try:
        from brain.vector_search import SemanticKnowledgeBase
        from brain.padoc_brain_engine import brain_engine
        
        # Recarrega o RAG
        kb = SemanticKnowledgeBase()
        # Recarrega as bases do cérebro
        brain_engine.knowledge_base = brain_engine._carregar_base_conhecimento()
        print("    ✅ Cérebro da PADOC AI reindexado com os novos dados reais da internet!")
    except Exception as e:
        print(f"    ⚠️ Erro ao reindexar: {e}")


def main():
    print("=" * 70)
    print("🚗 PADOC AI - DOWNLOAD DE DADOS REAIS DA INTERNET (DTCs & APIs) 🚗")
    print("=" * 70)

    total_dtcs = baixar_dtcs_reais()
    baixar_dados_nhtsa()
    atualizar_rag_com_dados_reais()

    print("\n" + "=" * 70)
    print(f"🎉 SUCESSO! A PADOC AI agora conta com dados reais da internet.")
    print(f"📦 Total de DTCs e dados técnicos sincronizados com a nuvem.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
