"""
GUIA PRÁTICO: TESTES PASSO A PASSO
==================================
"""

# ==============================================================================
# PASSO 1: TESTAR APLICAÇÃO LOCAL
# ==============================================================================

print("""
PASSO 1: TESTAR A APLICAÇÃO LOCAL
==================================

1.1 Abrir Terminal PowerShell
  Pressionar: Win + X > Windows PowerShell (ou cmd)
  
1.2 Navegar para o diretório do projeto
  cd c:\Users\User\Downloads\padoc-ai-local-llm\padoc-ai-local-llm
  
1.3 Testar carregamento de dados
  python validar_datasets.py
  
  Resultado esperado:
  ============================================================
  ✓ Encontrados 5 arquivos JSON
  ✓ Função carregar_base() executada com sucesso
  ✓ Base é um dicionário com 6 chaves
  ============================================================

1.4 Testar chat interativo (opcional)
  python app.py
  
  Digitar uma pergunta:
    "Meu carro não pega"
  
  Resultado: Resposta com diagnóstico
  Digitar: sair
""")


# ==============================================================================
# PASSO 2: TESTAR API REST
# ==============================================================================

print("""
PASSO 2: TESTAR A API REST
==========================

2.1 Instalar Flask (se não estiver instalado)
  pip install flask flask-cors
  
2.2 Iniciar a API (Terminal 1)
  python api.py
  
  Resultado esperado:
  * Running on http://localhost:5000
  
2.3 Testar endpoints (Terminal 2)

  Teste 1: Verificar saúde da API
  ------
  curl http://localhost:5000/api/saude
  
  Resposta esperada:
  {
    "status": "ok",
    "ia_pronta": true,
    "timestamp": "2026-06-17T..."
  }
  
  
  Teste 2: Enviar diagnóstico
  ---------
  curl -X POST http://localhost:5000/api/diagnostico \\
    -H "Content-Type: application/json" \\
    -d '{"pergunta": "Carro não pega", "usuario_id": "teste123"}'
  
  Resposta esperada:
  {
    "sucesso": true,
    "resposta": "Possíveis causas...",
    "usuario_id": "teste123",
    "timestamp": "2026-06-17T..."
  }
  
  
  Teste 3: Ver histórico
  -----
  curl http://localhost:5000/api/historico?linhas=5
  
  Resposta esperada:
  {
    "total": 5,
    "historico": [...]
  }
""")


# ==============================================================================
# PASSO 3: TESTAR COM PYTHON
# ==============================================================================

TESTE_PYTHON = '''
import requests
import json

# URL da API local
API_URL = "http://localhost:5000/api/diagnostico"

# Teste 1: Enviar pergunta
dados = {
    "pergunta": "Motor piscando luz de injeção",
    "usuario_id": "user_python_001"
}

resposta = requests.post(API_URL, json=dados)
resultado = resposta.json()

print("Status:", resposta.status_code)
print("Sucesso:", resultado["sucesso"])
print("Resposta:")
print(resultado["resposta"])

# Teste 2: Verificar histórico
url_historico = "http://localhost:5000/api/historico"
resposta = requests.get(url_historico)
print("\nHistórico (últimos 3):")
for item in resposta.json()["historico"][-3:]:
    print(f"- {item['pergunta'][:50]}...")
'''

print("\nPASSO 3: TESTAR COM PYTHON")
print("==========================")
print(TESTE_PYTHON)


# ==============================================================================
# PASSO 4: TESTAR SITE HTML
# ==============================================================================

print("""
PASSO 4: TESTAR SITE HTML
=========================

4.1 Abrir o arquivo site_padoc.html no navegador
  - Clicar 2x em: site_padoc.html
  - Ou: Arrastar o arquivo para o navegador
  
4.2 Testar funcionamento
  - Descrever um problema (ex: "Motor com barulho estranho")
  - Clicar "Obter Diagnóstico"
  - Resultado deve aparecer em alguns segundos
  
4.3 Verificar em diferentes navegadores
  - Google Chrome
  - Firefox
  - Edge
  - Safari (Mac)

4.4 Testar responsividade (mobile)
  - Pressionar F12 (Developer Tools)
  - Clicar em "Toggle device toolbar" (Ctrl+Shift+M)
  - Testar em diferentes tamanhos: iPhone, iPad, Android
""")


# ==============================================================================
# PASSO 5: INTEGRAR COM FIREBASE
# ==============================================================================

print("""
PASSO 5: INTEGRAR COM FIREBASE
=============================

5.1 Criar conta Firebase
  - Ir para: https://console.firebase.google.com
  - Clicar "Criar novo projeto"
  - Nome: "padoc-ai"
  - Clique em "Continuar"
  
5.2 Ativar Realtime Database
  - No menu lateral: "Realtime Database"
  - Clicar "Criar base de dados"
  - Selecionar: Iniciar no modo de teste
  - Região: us-central1 (ou mais próxima)
  
5.3 Obter credenciais
  - Ir para: Configurações do Projeto > Contas de Serviço
  - Aba "Firebase Admin SDK"
  - Clicar "Gerar nova chave privada"
  - Baixar o arquivo JSON
  - Salvar em: padoc-ai-local-llm/firebase-key.json
  
5.4 Criar arquivo .env
  Criar arquivo: padoc-ai-local-llm/.env
  
  Conteúdo:
  ---------
  FIREBASE_CREDENTIALS_PATH=./firebase-key.json
  FIREBASE_DATABASE_URL=https://seu-projeto-padoc.firebaseio.com
  FLASK_ENV=development
  DEBUG=True
  
  (Copiar o URL da base de dados de: Realtime Database > URL no topo)
  
5.5 Instalar firebase-admin
  pip install firebase-admin python-dotenv
  
5.6 Testar integração
  python -c "from firebase_integration import inicializar_firebase; inicializar_firebase()"
  
  Resultado esperado:
  ✓ Firebase inicializado com sucesso
""")


# ==============================================================================
# PASSO 6: DEPLOY
# ==============================================================================

print("""
PASSO 6: DEPLOY EM PRODUÇÃO
===========================

OPÇÃO A: HEROKU (Recomendado para iniciantes)
----------------------------------------------

6A.1 Criar conta em Heroku
  - Ir para: https://heroku.com
  - Sign up
  - Verificar email
  
6A.2 Instalar Heroku CLI
  - Download: https://devcenter.heroku.com/articles/heroku-cli
  - Windows: Executar installer
  - Verificar: heroku --version
  
6A.3 Criar arquivos necessários

  a) Procfile (sem extensão)
  ----
  web: gunicorn api:app
  
  b) runtime.txt
  ----------
  python-3.11.0
  
  c) requirements.txt (atualizar)
  ----------
  llama-cpp-python==0.2.x
  flask==3.0.0
  flask-cors==4.0.0
  firebase-admin==6.1.0
  python-dotenv==1.0.0
  requests==2.31.0
  gunicorn==20.1.0

6A.4 Fazer login no Heroku
  heroku login
  
  Será aberto navegador para autenticação
  
6A.5 Criar aplicação no Heroku
  heroku create padoc-ai-api
  
  Resultado:
  Creating app... done, ⬢ padoc-ai-api
  https://padoc-ai-api.herokuapp.com/ | https://git.heroku.com/padoc-ai-api.git
  
6A.6 Preparar variáveis de ambiente
  heroku config:set FIREBASE_CREDENTIALS_PATH=./firebase-key.json
  heroku config:set FIREBASE_DATABASE_URL=https://seu-firebase.firebaseio.com
  
6A.7 Deploy
  git add .
  git commit -m "Deploy PADOC AI"
  git push heroku main
  
  (Ou: git push heroku master, se usar branch master)
  
6A.8 Verificar logs
  heroku logs --tail
  
  Procurar por:
  ✓ Application running on port 5000
  ✓ PADOC AI inicializado com sucesso
  
6A.9 Testar API em produção
  curl https://padoc-ai-api.herokuapp.com/api/saude
  
  Resultado esperado:
  {"status":"ok","ia_pronta":true}


OPÇÃO B: GOOGLE CLOUD (Profissional)
------------------------------------

Seguir documentação em:
https://cloud.google.com/run/docs/quickstarts/build-and-deploy
""")


# ==============================================================================
# PASSO 7: CONECTAR SITE
# ==============================================================================

print("""
PASSO 7: CONECTAR SITE À API
============================

7.1 Editar site_padoc.html
  Procurar por:
    const API_URL = "http://localhost:5000/api/diagnostico";
  
  Trocar para:
    const API_URL = "https://padoc-ai-api.herokuapp.com/api/diagnostico";
    
  (Se usando Google Cloud, trocar para sua URL)

7.2 Hospedar site (opções)

  a) GitHub Pages (Grátis)
  -
  - Criar repositório
  - Fazer push dos arquivos
  - Ativar GitHub Pages
  - Site será: https://seu-usuario.github.io/padoc-ai
  
  b) Vercel (Grátis, muito fácil)
  -
  - Ir para: https://vercel.com
  - Conectar GitHub
  - Fazer import do repositório
  - Deploy automático
  - URL: https://seu-projeto.vercel.app
  
  c) Seu próprio servidor
  -
  - Upload HTML para servidor Apache/Nginx
  - Configurar SSL (HTTPS)
  
7.3 Configurar CORS (se necessário)
  Na API (api.py), certifique-se de ter:
    from flask_cors import CORS
    CORS(app)
  
  Isso permite requisições de qualquer origem
""")


# ==============================================================================
# PASSO 8: APP MOBILE
# ==============================================================================

print("""
PASSO 8: CRIAR APP MOBILE (React Native/Flutter)
================================================

OPÇÃO A: React Native
--------------------

8A.1 Instalar Node.js
  - Download: https://nodejs.org
  - Instalar versão LTS
  
8A.2 Criar projeto
  npx create-expo-app PadocAI
  cd PadocAI
  
8A.3 Instalar dependências
  npm install firebase @react-navigation/native
  
8A.4 Integrar Firebase Auth (opcional)
  npm install @react-native-firebase/auth @react-native-firebase/app
  
8A.5 Testar
  npx expo start
  
  - Escanear QR code com app Expo no celular
  - App abrirá no seu celular em tempo real

8A.6 Publicar
  - App Store (iOS): https://developer.apple.com
  - Google Play (Android): https://developer.android.com


OPÇÃO B: Flutter
---------------

8B.1 Instalar Flutter SDK
  - Download: https://flutter.dev/docs/get-started/install
  
8B.2 Criar projeto
  flutter create padoc_ai
  cd padoc_ai
  
8B.3 Adicionar dependências em pubspec.yaml
  dependencies:
    flutter:
      sdk: flutter
    http: ^0.13.0
    firebase_core: ^2.0.0
    firebase_auth: ^4.0.0
  
8B.4 Testar
  flutter run
  
8B.5 Publicar
  flutter build apk      # Android
  flutter build ios      # iOS
""")


# ==============================================================================
# CHECKLIST FINAL
# ==============================================================================

print("""
CHECKLIST DE VERIFICAÇÃO FINAL
==============================

Antes de ir para produção, verificar:

TESTES LOCAIS:
  ☐ python validar_datasets.py funciona
  ☐ python app.py funciona
  ☐ python api.py inicia sem erros
  ☐ Endpoints da API respondem corretamente
  ☐ site_padoc.html carrega no navegador
  ☐ Site consegue conectar à API local

API:
  ☐ GET /api/saude retorna 200
  ☐ POST /api/diagnostico funciona
  ☐ GET /api/historico retorna dados
  ☐ CORS está habilitado
  ☐ Rate limiting está configurado (opcional)

FIREBASE:
  ☐ Projeto criado
  ☐ Realtime Database ativado
  ☐ Credenciais baixadas
  ☐ .env configurado
  ☐ Dados sendo salvos no Firebase

DEPLOYMENT:
  ☐ Heroku app criado
  ☐ Environment variables configuradas
  ☐ Deploy bem-sucedido
  ☐ Logs mostram aplicação rodando
  ☐ API em produção responde

SITE:
  ☐ URL da API em produção configurada
  ☐ Site hospedado (GitHub Pages/Vercel)
  ☐ HTTPS ativado
  ☐ Funciona em desktop
  ☐ Funciona em mobile
  ☐ Histórico salva localmente

APP MOBILE:
  ☐ React Native/Flutter instalado
  ☐ Conecta à API em produção
  ☐ Firebase Auth configurado (opcional)
  ☐ Pronto para publicar em lojas
""")

print("\n" + "="*60)
print("✅ GUIA DE TESTES COMPLETO!")
print("="*60)
