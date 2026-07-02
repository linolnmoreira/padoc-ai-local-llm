import urllib.request, json, sys

data = json.dumps({
    'pergunta': 'Motor com barulho estranho ao acelerar',
    'usuario_id': 'teste_ui'
}).encode('utf-8')

req = urllib.request.Request('http://localhost:5000/api/diagnostico', data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode('utf-8')
        print('STATUS:', resp.status)
        print('BODY:\n', body)
except Exception as e:
    print('ERRO:', e)
    sys.exit(1)
