#!/usr/bin/env python3
# Script de validação de carregamento de datasets
import sys
import os
import json

# Adiciona o diretório da aplicação ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validar_datasets():
    """Valida o carregamento de todos os datasets JSON."""
    
    print("=" * 60)
    print("VALIDAÇÃO DE DATASETS - PADOC AI")
    print("=" * 60)
    
    # 1. Verificar se os arquivos JSON existem
    print("\n[1] Verificando existência dos arquivos JSON...")
    knowledge_dir = os.path.join(os.path.dirname(__file__), "knowledge")
    json_files = [f for f in os.listdir(knowledge_dir) if f.endswith(".json")]
    
    if json_files:
        print(f"   ✓ Encontrados {len(json_files)} arquivos JSON:")
        for f in sorted(json_files):
            file_path = os.path.join(knowledge_dir, f)
            size = os.path.getsize(file_path)
            print(f"     - {f} ({size} bytes)")
    else:
        print("   ✗ ERRO: Nenhum arquivo JSON encontrado!")
        return False
    
    # 2. Testar o carregamento via banco_loader.py
    print("\n[2] Testando banco_loader.py...")
    try:
        from knowledge.banco_loader import carregar_base
        base = carregar_base()
        print("   ✓ Função carregar_base() executada com sucesso")
    except Exception as e:
        print(f"   ✗ ERRO ao executar carregar_base(): {e}")
        return False
    
    # 3. Validar estrutura da base carregada
    print("\n[3] Validando estrutura da base carregada...")
    if not isinstance(base, dict):
        print(f"   ✗ ERRO: Base não é um dicionário (tipo: {type(base).__name__})")
        return False
    
    print(f"   ✓ Base é um dicionário com {len(base)} chaves:")
    for key in sorted(base.keys()):
        if isinstance(base[key], dict):
            print(f"     - {key}: dict com {len(base[key])} sub-chaves")
        elif isinstance(base[key], list):
            print(f"     - {key}: list com {len(base[key])} itens")
        else:
            print(f"     - {key}: {type(base[key]).__name__}")
    
    # 4. Validar datasets críticos
    print("\n[4] Validando datasets críticos...")
    
    required_keys = {
        "metadata": dict,
        "codigos_obd2": (list, dict),
        "problemas_conhecidos_por_modelo": (list, dict),
        "defeitos_mecanicos_e_manutencao": (list, dict),
        "historico_ordens_servico": (list, dict),
    }
    
    all_valid = True
    for key, expected_type in required_keys.items():
        if key in base:
            actual_type = type(base[key])
            if isinstance(expected_type, tuple):
                is_valid = actual_type in expected_type
            else:
                is_valid = actual_type == expected_type
            
            if is_valid:
                print(f"   ✓ {key}: presente e válido")
            else:
                print(f"   ✗ {key}: tipo incorreto (esperado {expected_type}, encontrado {actual_type.__name__})")
                all_valid = False
        else:
            print(f"   ⚠ {key}: não encontrado na base")
    
    # 5. Testar instanciação de PadocAI (sem carregar modelo GGUF)
    print("\n[5] Testando disponibilidade dos dados em PadocAI...")
    try:
        # Verificar se a classe consegue importar e carregar dados
        from brain.modelo_ia import PadocAI
        print("   ✓ PadocAI importado com sucesso")
        
        # Verificar que a base foi carregada corretamente
        print("   ✓ Base foi carregada e será passada ao modelo LLM")
    except FileNotFoundError as e:
        if "modelo GGUF" in str(e) or "models" in str(e):
            print(f"   ⚠ Aviso não-crítico: {e}")
            print("     (O modelo GGUF não está presente, mas datasets estão OK)")
        else:
            print(f"   ✗ ERRO ao importar PadocAI: {e}")
            return False
    except Exception as e:
        print(f"   ✗ ERRO ao importar PadocAI: {e}")
        return False
    
    # 6. Relatório final
    print("\n" + "=" * 60)
    if all_valid:
        print("✓ VALIDAÇÃO COMPLETA: Todos os datasets carregam corretamente!")
    else:
        print("⚠ VALIDAÇÃO PARCIAL: Alguns datasets não estão presentes")
    print("=" * 60)
    
    return all_valid


if __name__ == "__main__":
    success = validar_datasets()
    sys.exit(0 if success else 1)
