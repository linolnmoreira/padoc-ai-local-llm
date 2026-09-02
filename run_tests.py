"""
PADOC AI - Runner de Validacao e Testes do Sistema Completo
"""

import sys
import os

# Forca encoding UTF-8 no stdout do Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    print("=" * 60)
    print("PADOC AI - EXECUCAO DA SUITE DE TESTES AUTOMATIZADOS")
    print("=" * 60)

    try:
        import pytest
        retcode = pytest.main(["-v", "tests/test_padoc_ai.py"])
        if retcode == 0:
            print("\n[OK] TODOS OS TESTES PASSARAM COM SUCESSO!")
        else:
            print(f"\n[AVISO] Codigo de retorno do pytest: {retcode}")
        sys.exit(retcode)
    except ImportError:
        print("pytest nao encontrado. Executando testes via unittest...")
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover("tests", pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
