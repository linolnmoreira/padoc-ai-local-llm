import json

try:
    with open('knowledge/historico_oficina.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print('✓ JSON válido')
    print(f'Total de registros: {len(data)}')
    print(f'Últimos 3 códigos OBD2: {[r["codigo_obd2"] for r in data[-3:]]}')
    print('\nÚltimo registro (P0420):')
    print(f'  - Componente: {data[-1]["componente"]}')
    print(f'  - Defeito: {data[-1]["defeito"][:60]}...')
    
except json.JSONDecodeError as e:
    print(f'✗ Erro JSON: {e}')
except Exception as e:
    print(f'✗ Erro: {e}')
