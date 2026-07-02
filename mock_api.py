from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/saude':
            resp = {'status': 'ok', 'ia_pronta': True}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        elif self.path == '/api/historico':
            resp = {
                'sucesso': True,
                'historico': [
                    {'pergunta': 'Motor falhando P0300', 'resposta': 'Falha de ignição múltipla detectada. Verifique velas e bobinas.'}
                ]
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path in ['/api/diagnostico', '/api/diagnostico-firebase']:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                pergunta = data.get('pergunta', '')
            except Exception:
                pergunta = ''

            # Diagnóstico inteligente simulado com base no conhecimento técnico
            resposta_texto = 'Diagnóstico simulado: verifique velas, cabos de ignição e compressão.\nDetalhes: ' + (pergunta[:200] if pergunta else 'sem descrição')
            
            if 'P0300' in pergunta.upper():
                resposta_texto = 'Detectada falha de ignição em cilindros múltiplos (P0300). Recomendamos testar a resistência das bobinas, inspecionar o desgaste das velas e verificar a pressão da linha de combustível.'
            elif 'P0171' in pergunta.upper():
                resposta_texto = 'Detectada mistura muito pobre no Banco 1 (P0171). Verifique possíveis entradas de ar falso pelas mangueiras de vácuo ou faça a limpeza preventiva do sensor MAF.'
            elif 'P0420' in pergunta.upper():
                resposta_texto = 'Detectada eficiência do catalisador abaixo do limite (P0420). Analise o gráfico de leitura da sonda lambda pós-catalisador e inspecione a colmeia interna com câmera endoscópica.'

            resp = {
                'sucesso': True,
                'resposta': resposta_texto
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = 5000
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'Mock API rodando em http://0.0.0.0:{port} - POST /api/diagnostico')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Interrompido pelo usuário')
        server.server_close()
