"""
PADOC AI - Atualizador com Dados Reais da Internet (v3.0)

Baixa da internet:
1. Códigos DTC Reais de Fabricantes (Toyota, Volkswagen, Ford, Chevrolet, BMW, Honda, etc.)
2. Códigos OBD-II Genéricos em Português Brasileiro (fabiovila/OBDIICodes)
3. Lista Real de Fabricantes e Modelos via NHTSA API (National Highway Traffic Safety Administration)
4. Recalls Oficiais de Veículos via NHTSA Recalls API
5. Reclamações Reais de Donos via NHTSA Complaints API
6. Modelos por Fabricante via NHTSA vPIC API
7. Consolidação e indexação vetorial no Cérebro da PADOC AI
"""

import os
import sys
import json
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime

# Garante UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
MULTIMODAL_DIR = os.path.join(BASE_DIR, "dados", "multimodal")
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

HEADERS = {"User-Agent": "PADOC-AI-Updater/3.0"}

# ═══════════════════════════════════════════════════════════════════════════
# 1. Repositórios Reais de DTCs por Fabricante (GitHub - Automotive-9)
# ═══════════════════════════════════════════════════════════════════════════
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
    {"marca": "Volvo", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Volvo.json", "arquivo": "dtc_volvo_real.json"},
    {"marca": "Toyota", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Toyota.json", "arquivo": "dtc_toyota_real.json"},
    {"marca": "Chevrolet", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Chevrolet.json", "arquivo": "dtc_chevrolet_real.json"},
    {"marca": "Chrysler", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Chrysler.json", "arquivo": "dtc_chrysler_real.json"},
    {"marca": "Jeep", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Jeep.json", "arquivo": "dtc_jeep_real.json"},
    {"marca": "Mitsubishi", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Mitsubishi.json", "arquivo": "dtc_mitsubishi_real.json"},
    {"marca": "Subaru", "url": "https://raw.githubusercontent.com/Automotive-9/dtc-codes/main/Subaru.json", "arquivo": "dtc_subaru_real.json"},
]

# ═══════════════════════════════════════════════════════════════════════════
# 2. Códigos OBD-II Genéricos em PT-BR (fabiovila/OBDIICodes)
# ═══════════════════════════════════════════════════════════════════════════
OBDII_GENERICOS = [
    {
        "nome": "Códigos OBD-II Genéricos em Português (PT-BR)",
        "url": "https://raw.githubusercontent.com/fabiovila/OBDIICodes/master/Codigos-ptbr.json",
        "arquivo": "obdii_codigos_genericos_ptbr.json"
    },
    {
        "nome": "Códigos OBD-II Genéricos em Inglês (EN)",
        "url": "https://raw.githubusercontent.com/fabiovila/OBDIICodes/master/codes.json",
        "arquivo": "obdii_codigos_genericos_en.json"
    }
]

# ═══════════════════════════════════════════════════════════════════════════
# 3. APIs Públicas Oficiais do Setor Automotivo
# ═══════════════════════════════════════════════════════════════════════════
APIS_OFICIAIS = [
    {
        "nome": "NHTSA - Lista Oficial de Fabricantes Mundiais de Veículos",
        "url": "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json",
        "arquivo": "nhtsa_fabricantes_mundiais.json"
    }
]

# Marcas mais comuns no mercado brasileiro para buscar recalls e reclamações
MARCAS_BRASIL = [
    {"make": "Toyota", "model": "Corolla", "year": "2023"},
    {"make": "Toyota", "model": "Hilux", "year": "2023"},
    {"make": "Honda", "model": "Civic", "year": "2023"},
    {"make": "Honda", "model": "HR-V", "year": "2023"},
    {"make": "Volkswagen", "model": "Gol", "year": "2023"},
    {"make": "Volkswagen", "model": "T-Cross", "year": "2023"},
    {"make": "Chevrolet", "model": "Onix", "year": "2023"},
    {"make": "Chevrolet", "model": "Tracker", "year": "2023"},
    {"make": "Fiat", "model": "Strada", "year": "2023"},
    {"make": "Fiat", "model": "Argo", "year": "2023"},
    {"make": "Hyundai", "model": "HB20", "year": "2023"},
    {"make": "Hyundai", "model": "Creta", "year": "2023"},
    {"make": "Jeep", "model": "Compass", "year": "2023"},
    {"make": "Jeep", "model": "Renegade", "year": "2023"},
    {"make": "Nissan", "model": "Kicks", "year": "2023"},
    {"make": "Renault", "model": "Kwid", "year": "2023"},
    {"make": "Ford", "model": "Ranger", "year": "2023"},
    {"make": "BMW", "model": "320i", "year": "2023"},
    {"make": "Mercedes-Benz", "model": "C-Class", "year": "2023"},
]

# Fabricantes para buscar modelos disponíveis
FABRICANTES_MODELOS = [
    "Toyota", "Honda", "Volkswagen", "Chevrolet", "Fiat",
    "Hyundai", "Kia", "Nissan", "Renault", "Ford",
    "BMW", "Mercedes-Benz", "Jeep", "Mitsubishi", "Volvo",
    "Audi", "Subaru", "Peugeot", "Citroen"
]


def _baixar_json(url, timeout=15):
    """Faz download de um JSON da internet e retorna o conteúdo parsed."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        conteudo = response.read().decode("utf-8")
        return json.loads(conteudo)


def _salvar_json(destino, dados):
    """Salva dados JSON em arquivo com UTF-8."""
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def _contar_registros(dados):
    """Conta registros de um JSON (lista ou dict)."""
    if isinstance(dados, list):
        return len(dados)
    elif isinstance(dados, dict):
        return len(dados.keys())
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 1: DTCs de Fabricantes
# ═══════════════════════════════════════════════════════════════════════════
def baixar_dtcs_reais():
    print("\n🌐 1. BAIXANDO CÓDIGOS DTC REAIS DE MONTADORAS DA INTERNET...")
    total_baixados = 0

    for item in REPOSITORIOS_DTC_REAIS:
        marca = item["marca"]
        url = item["url"]
        destino = os.path.join(KNOWLEDGE_DIR, item["arquivo"])
        print(f" -> Conectando e baixando dados reais da {marca}...")

        try:
            dados_json = _baixar_json(url)
            _salvar_json(destino, dados_json)

            qtd_codigos = _contar_registros(dados_json)
            print(f"    ✅ {marca}: {qtd_codigos} códigos de falha reais baixados com sucesso!")
            total_baixados += qtd_codigos

        except Exception as e:
            print(f"    ⚠️ Aviso para {marca}: {e}")

    return total_baixados


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 2: Códigos OBD-II Genéricos em PT-BR
# ═══════════════════════════════════════════════════════════════════════════
def baixar_obdii_genericos():
    print("\n🔧 2. BAIXANDO CÓDIGOS OBD-II GENÉRICOS (PT-BR E EN)...")
    total = 0

    for item in OBDII_GENERICOS:
        nome = item["nome"]
        url = item["url"]
        destino = os.path.join(KNOWLEDGE_DIR, item["arquivo"])
        print(f" -> Baixando: {nome}...")

        try:
            dados = _baixar_json(url)
            _salvar_json(destino, dados)

            qtd = _contar_registros(dados)
            print(f"    ✅ {qtd} códigos OBD-II salvos em {item['arquivo']}!")
            total += qtd

        except Exception as e:
            print(f"    ⚠️ Aviso ao baixar {nome}: {e}")

    return total


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 3: API NHTSA - Fabricantes
# ═══════════════════════════════════════════════════════════════════════════
def baixar_dados_nhtsa():
    print("\n🏛️ 3. CONSULTANDO API OFICIAL DE SEGURANÇA E FABRICANTES (NHTSA)...")

    for item in APIS_OFICIAIS:
        nome = item["nome"]
        url = item["url"]
        destino = os.path.join(KNOWLEDGE_DIR, item["arquivo"])
        print(f" -> Baixando: {nome}...")

        try:
            dados = _baixar_json(url, timeout=20)

            # Salva os primeiros fabricantes mais relevantes para manter o dataset limpo e rápido
            resultados = dados.get("Results", [])
            _salvar_json(destino, resultados[:500])

            print(f"    ✅ Salvo {len(resultados[:500])} registros oficiais em {item['arquivo']}!")

        except Exception as e:
            print(f"    ⚠️ Aviso API NHTSA: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 4: NHTSA Recalls por Veículo
# ═══════════════════════════════════════════════════════════════════════════
def baixar_recalls_nhtsa():
    print("\n🚨 4. BAIXANDO RECALLS OFICIAIS DE SEGURANÇA (NHTSA)...")
    todos_recalls = []

    for veiculo in MARCAS_BRASIL:
        make = veiculo["make"]
        model = veiculo["model"]
        year = veiculo["year"]
        url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={urllib.parse.quote(make)}&model={urllib.parse.quote(model)}&modelYear={year}"
        print(f" -> Buscando recalls: {make} {model} {year}...")

        try:
            dados = _baixar_json(url, timeout=20)
            resultados = dados.get("results", [])
            
            for recall in resultados:
                recall["_padoc_veiculo"] = f"{make} {model} {year}"

            if resultados:
                todos_recalls.extend(resultados)
                print(f"    ✅ {len(resultados)} recalls encontrados para {make} {model}!")
            else:
                print(f"    ℹ️ Nenhum recall para {make} {model} {year}")

        except Exception as e:
            print(f"    ⚠️ Aviso Recalls {make} {model}: {e}")

    if todos_recalls:
        destino = os.path.join(KNOWLEDGE_DIR, "nhtsa_recalls_veiculos.json")
        _salvar_json(destino, todos_recalls)
        print(f"\n    📋 Total: {len(todos_recalls)} recalls salvos em nhtsa_recalls_veiculos.json")

    return len(todos_recalls)


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 5: NHTSA Reclamações Reais de Donos
# ═══════════════════════════════════════════════════════════════════════════
def baixar_reclamacoes_nhtsa():
    print("\n📣 5. BAIXANDO RECLAMAÇÕES REAIS DE DONOS DE VEÍCULOS (NHTSA)...")
    todas_reclamacoes = []

    for veiculo in MARCAS_BRASIL[:10]:  # Limita para as 10 primeiras para não sobrecarregar
        make = veiculo["make"]
        model = veiculo["model"]
        year = veiculo["year"]
        url = f"https://api.nhtsa.gov/complaints/complaintsByVehicle?make={urllib.parse.quote(make)}&model={urllib.parse.quote(model)}&modelYear={year}"
        print(f" -> Buscando reclamações: {make} {model} {year}...")

        try:
            dados = _baixar_json(url, timeout=20)
            resultados = dados.get("results", [])

            for rec in resultados:
                rec["_padoc_veiculo"] = f"{make} {model} {year}"

            if resultados:
                todas_reclamacoes.extend(resultados[:50])  # Max 50 por veículo
                print(f"    ✅ {min(len(resultados), 50)} reclamações encontradas para {make} {model}!")
            else:
                print(f"    ℹ️ Nenhuma reclamação para {make} {model} {year}")

        except Exception as e:
            print(f"    ⚠️ Aviso Reclamações {make} {model}: {e}")

    if todas_reclamacoes:
        destino = os.path.join(KNOWLEDGE_DIR, "nhtsa_reclamacoes_donos.json")
        _salvar_json(destino, todas_reclamacoes)
        print(f"\n    📋 Total: {len(todas_reclamacoes)} reclamações salvas em nhtsa_reclamacoes_donos.json")

    return len(todas_reclamacoes)


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 6: Modelos por Fabricante (NHTSA vPIC)
# ═══════════════════════════════════════════════════════════════════════════
def baixar_modelos_por_fabricante():
    print("\n🚗 6. BAIXANDO MODELOS DISPONÍVEIS POR FABRICANTE (NHTSA vPIC)...")
    todos_modelos = {}

    for marca in FABRICANTES_MODELOS:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/{urllib.parse.quote(marca)}?format=json"
        print(f" -> Buscando modelos da {marca}...")

        try:
            dados = _baixar_json(url, timeout=15)
            resultados = dados.get("Results", [])
            
            modelos_lista = [
                {
                    "modelo": r.get("Model_Name", ""),
                    "modelo_id": r.get("Model_ID", ""),
                    "marca": r.get("Make_Name", marca)
                }
                for r in resultados if r.get("Model_Name")
            ]
            
            if modelos_lista:
                todos_modelos[marca] = modelos_lista
                print(f"    ✅ {len(modelos_lista)} modelos encontrados para {marca}")
            else:
                print(f"    ℹ️ Nenhum modelo retornado para {marca}")

        except Exception as e:
            print(f"    ⚠️ Aviso Modelos {marca}: {e}")

    if todos_modelos:
        destino = os.path.join(KNOWLEDGE_DIR, "nhtsa_modelos_por_fabricante.json")
        _salvar_json(destino, todos_modelos)
        total = sum(len(v) for v in todos_modelos.values())
        print(f"\n    📋 Total: {total} modelos de {len(todos_modelos)} fabricantes salvos!")

    return sum(len(v) for v in todos_modelos.values())


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 7: Reindexação no Cérebro
# ═══════════════════════════════════════════════════════════════════════════
def atualizar_rag_com_dados_reais():
    print("\n🧠 7. INTEGRANDO E REINDEXANDO TUDO NO CÉREBRO DA PADOC AI...")
    try:
        from brain.vector_search import SemanticKnowledgeBase
        from brain.padoc_brain_engine import brain_engine
        
        # Recarrega o RAG (agora indexa também dados multimodais)
        kb = SemanticKnowledgeBase()
        # Recarrega as bases do cérebro
        brain_engine.knowledge_base = brain_engine._carregar_base_conhecimento()
        print("    ✅ Cérebro da PADOC AI reindexado com os novos dados reais da internet!")
    except Exception as e:
        print(f"    ⚠️ Erro ao reindexar: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 8: Relatório Final
# ═══════════════════════════════════════════════════════════════════════════
def gerar_relatorio_final():
    """Gera um JSON de auditoria com tudo que foi gravado no cérebro."""
    print("\n📊 8. GERANDO RELATÓRIO DE AUDITORIA DO CÉREBRO...")
    
    relatorio = {
        "versao": "3.0",
        "data_atualizacao": datetime.now().isoformat(),
        "arquivos_knowledge": {},
        "arquivos_multimodal": {},
        "total_bytes_knowledge": 0,
        "total_bytes_multimodal": 0
    }
    
    # Conta arquivos em knowledge/
    if os.path.exists(KNOWLEDGE_DIR):
        for f in sorted(os.listdir(KNOWLEDGE_DIR)):
            if f.endswith(".json"):
                caminho = os.path.join(KNOWLEDGE_DIR, f)
                tamanho = os.path.getsize(caminho)
                relatorio["arquivos_knowledge"][f] = {
                    "tamanho_bytes": tamanho,
                    "tamanho_legivel": f"{tamanho / 1024:.1f} KB"
                }
                relatorio["total_bytes_knowledge"] += tamanho
    
    # Conta arquivos em dados/multimodal/
    if os.path.exists(MULTIMODAL_DIR):
        for root, dirs, files in os.walk(MULTIMODAL_DIR):
            for f in sorted(files):
                caminho = os.path.join(root, f)
                tamanho = os.path.getsize(caminho)
                pasta_rel = os.path.relpath(root, MULTIMODAL_DIR)
                chave = f"{pasta_rel}/{f}" if pasta_rel != "." else f
                relatorio["arquivos_multimodal"][chave] = {
                    "tamanho_bytes": tamanho,
                    "tamanho_legivel": f"{tamanho / 1024:.1f} KB"
                }
                relatorio["total_bytes_multimodal"] += tamanho
    
    relatorio["total_legivel_knowledge"] = f"{relatorio['total_bytes_knowledge'] / 1024:.1f} KB"
    relatorio["total_legivel_multimodal"] = f"{relatorio['total_bytes_multimodal'] / 1024:.1f} KB"
    
    destino = os.path.join(KNOWLEDGE_DIR, "_relatorio_cerebro.json")
    _salvar_json(destino, relatorio)
    
    print(f"    📁 Knowledge: {len(relatorio['arquivos_knowledge'])} arquivos ({relatorio['total_legivel_knowledge']})")
    print(f"    📁 Multimodal: {len(relatorio['arquivos_multimodal'])} arquivos ({relatorio['total_legivel_multimodal']})")
    print(f"    ✅ Relatório salvo em: _relatorio_cerebro.json")
    
    return relatorio


def main():
    print("=" * 70)
    print("🚗 PADOC AI v3.0 - ATUALIZAÇÃO COMPLETA DO CÉREBRO COM DADOS REAIS 🚗")
    print("=" * 70)
    print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    total_dtcs = baixar_dtcs_reais()
    total_obdii = baixar_obdii_genericos()
    baixar_dados_nhtsa()
    total_recalls = baixar_recalls_nhtsa()
    total_reclamacoes = baixar_reclamacoes_nhtsa()
    total_modelos = baixar_modelos_por_fabricante()
    atualizar_rag_com_dados_reais()
    relatorio = gerar_relatorio_final()

    print("\n" + "=" * 70)
    print(f"🎉 ATUALIZAÇÃO COMPLETA DO CÉREBRO DA PADOC AI!")
    print(f"   📦 DTCs de fabricantes:       {total_dtcs}")
    print(f"   🔧 Códigos OBD-II genéricos:  {total_obdii}")
    print(f"   🚨 Recalls oficiais NHTSA:    {total_recalls}")
    print(f"   📣 Reclamações de donos:       {total_reclamacoes}")
    print(f"   🚗 Modelos por fabricante:     {total_modelos}")
    print(f"   📁 Total no cérebro:           {relatorio['total_legivel_knowledge']}")
    print(f"⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
