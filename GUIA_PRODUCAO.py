"""
GUIA COMPLETO: TRANSFORMAR PADOC AI EM APLICAÇÃO WEB + MOBILE COM FIREBASE
===========================================================================

SUMÁRIO:
1. FASE 1: Testar a aplicação local
2. FASE 2: Criar API REST
3. FASE 3: Integrar Firebase
4. FASE 4: Deploy em servidor
5. FASE 5: Conectar site + app mobile
"""

# =============================================================================
# FASE 1: TESTAR A APLICAÇÃO LOCAL
# =============================================================================

"""
PASSO 1.1: Instalação de dependências
--------------------------------------
"""

# Arquivo: requirements.txt
# Verificar se tem:
# llama-cpp-python==0.2.x
# flask==3.0.0          # Para API REST
# flask-cors==4.0.0     # Para aceitar requisições do front-end
# firebase-admin==6.1.0 # Para integração Firebase
# python-dotenv==1.0.0  # Para variáveis de ambiente
# requests==2.31.0      # Para fazer requisições HTTP

# Instalar:
# pip install -r requirements.txt


"""
PASSO 1.2: Testar o chatbot local
----------------------------------
"""

# Terminal:
# cd c:\Users\User\Downloads\padoc-ai-local-llm\padoc-ai-local-llm
# python app.py

# Resultado esperado:
# ==================================================
#      PADOC AI - Diagnóstico Automotivo
# ==================================================
# Digite 'sair' para encerrar.
# Você: Meu carro não pega
# [Processando...]
# PADOC AI: [resposta com diagnóstico]


"""
PASSO 1.3: Testar carregamento de dados
----------------------------------------
"""

# Terminal:
# python validar_datasets.py

# Resultado: Todos os datasets carregam sem erros


# =============================================================================
# FASE 2: CRIAR API REST COM FLASK
# =============================================================================

"""
PASSO 2.1: Criar arquivo api.py
"""

ARQUIVO_API_PY = '''
"""API REST para PADOC AI usando Flask"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from brain.modelo_ia import PadocAI
from memory.memoria import salvar_memoria
import logging

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar IA uma vez ao start da API
try:
    ia = PadocAI()
    logger.info("✓ PADOC AI inicializado com sucesso")
except Exception as e:
    logger.error(f"✗ Erro ao inicializar PADOC AI: {e}")
    ia = None


@app.route('/api/diagnostico', methods=['POST'])
def diagnostico():
    """Endpoint para obter diagnóstico automotivo.
    
    Request:
        {
            "pergunta": "Meu carro não pega",
            "usuario_id": "user123"  # Opcional, para log
        }
    
    Response:
        {
            "sucesso": true,
            "resposta": "Possíveis causas...",
            "timestamp": "2026-06-17T10:30:00"
        }
    """
    if ia is None:
        return jsonify({
            "sucesso": False,
            "erro": "PADOC AI não inicializado"
        }), 500
    
    try:
        # Validar entrada
        dados = request.get_json()
        if not dados or "pergunta" not in dados:
            return jsonify({
                "sucesso": False,
                "erro": "Campo 'pergunta' obrigatório"
            }), 400
        
        pergunta = dados["pergunta"].strip()
        if not pergunta:
            return jsonify({
                "sucesso": False,
                "erro": "Pergunta não pode ser vazia"
            }), 400
        
        # Gerar diagnóstico
        logger.info(f"Nova pergunta: {pergunta[:50]}...")
        resposta = ia.diagnosticar(pergunta)
        
        # Salvar em histórico
        usuario_id = dados.get("usuario_id", "anonimo")
        salvar_memoria(pergunta, resposta)
        
        return jsonify({
            "sucesso": True,
            "resposta": resposta,
            "usuario_id": usuario_id
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar diagnóstico: {e}")
        return jsonify({
            "sucesso": False,
            "erro": str(e)
        }), 500


@app.route('/api/saude', methods=['GET'])
def saude():
    """Verificar se API está funcionando."""
    return jsonify({
        "status": "ok",
        "ia_pronta": ia is not None
    }), 200


@app.route('/api/historico', methods=['GET'])
def historico():
    """Obter últimos diagnósticos (opcional)."""
    from memory.memoria import carregar_historico
    
    linhas = request.args.get("linhas", 10, type=int)
    historico_list = carregar_historico(linhas_max=linhas)
    
    return jsonify({
        "total": len(historico_list),
        "historico": historico_list
    }), 200


if __name__ == "__main__":
    # Para desenvolvimento:
    app.run(debug=True, host="0.0.0.0", port=5000)
    
    # Para produção, usar Gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:5000 api:app
'''

print("PASSO 2.1: Criar arquivo api.py")
print("Copiar o código acima em: padoc-ai-local-llm/api.py")


"""
PASSO 2.2: Testar a API
"""

TESTE_API = '''
# Terminal 1: Iniciar API
cd padoc-ai-local-llm
python api.py

# Terminal 2: Testar endpoint
curl -X POST http://localhost:5000/api/diagnostico \\
  -H "Content-Type: application/json" \\
  -d '{"pergunta": "Meu carro está piscando a luz de injeção", "usuario_id": "teste123"}'

# Resposta esperada:
# {
#   "sucesso": true,
#   "resposta": "Possíveis causas...",
#   "usuario_id": "teste123"
# }

# Ou em Python:
import requests

url = "http://localhost:5000/api/diagnostico"
dados = {
    "pergunta": "Carro não pega",
    "usuario_id": "user123"
}

resposta = requests.post(url, json=dados)
print(resposta.json())
'''

print("\nPASSO 2.2: Testar API")
print(TESTE_API)


# =============================================================================
# FASE 3: INTEGRAR COM FIREBASE
# =============================================================================

"""
PASSO 3.1: Configurar Firebase
"""

FIREBASE_CONFIG = '''
PASSO 3.1.1: Criar projeto no Firebase (https://console.firebase.google.com)
  - Ir em "Criar novo projeto"
  - Nome: "padoc-ai"
  - Ativar Google Analytics
  
PASSO 3.1.2: Baixar credenciais
  - Ir em Configurações do Projeto > Contas de Serviço
  - Clicar "Gerar nova chave privada"
  - Salvar o JSON em: padoc-ai-local-llm/firebase-key.json
  
PASSO 3.1.3: Arquivo .env (NUNCA comitar no Git!)
  FIREBASE_CREDENTIALS_PATH=./firebase-key.json
  FIREBASE_DATABASE_URL=https://padoc-ai.firebaseio.com
'''

print("\nPASSO 3.1: Configurar Firebase")
print(FIREBASE_CONFIG)


"""
PASSO 3.2: Integrar Firebase em api.py
"""

FIREBASE_INTEGRATION = '''
# Arquivo: api_firebase.py

import firebase_admin
from firebase_admin import credentials, db, auth
import os
from dotenv import load_dotenv

load_dotenv()

# Inicializar Firebase
firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-key.json")
cred = credentials.Certificate(firebase_cred_path)
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
})


def salvar_diagnostico_firebase(usuario_id, pergunta, resposta):
    """Salvar diagnóstico no Firebase Realtime Database"""
    from datetime import datetime
    
    try:
        ref = db.reference("diagnosticos")
        novo_diagnostico = {
            "usuario_id": usuario_id,
            "pergunta": pergunta,
            "resposta": resposta,
            "timestamp": datetime.now().isoformat()
        }
        
        ref.push(novo_diagnostico)
        return True
    except Exception as e:
        print(f"Erro ao salvar no Firebase: {e}")
        return False


def obter_diagnosticos_usuario(usuario_id, limite=10):
    """Obter diagnósticos de um usuário"""
    try:
        ref = db.reference("diagnosticos")
        diagnosticos = ref.order_by_child("usuario_id").equal_to(usuario_id).get()
        
        if diagnosticos:
            return list(diagnosticos.values())[:limite]
        return []
    except Exception as e:
        print(f"Erro ao obter diagnósticos: {e}")
        return []


# Integrar na API existente
@app.route('/api/diagnostico-firebase', methods=['POST'])
def diagnostico_firebase():
    """Versão da API que salva em Firebase"""
    
    dados = request.get_json()
    pergunta = dados.get("pergunta", "").strip()
    usuario_id = dados.get("usuario_id", "anonimo")
    
    if not pergunta:
        return jsonify({"erro": "Pergunta vazia"}), 400
    
    # Gerar resposta
    resposta = ia.diagnosticar(pergunta)
    
    # Salvar no Firebase
    sucesso = salvar_diagnostico_firebase(usuario_id, pergunta, resposta)
    
    if not sucesso:
        return jsonify({
            "aviso": "Resposta gerada mas não foi salva no Firebase",
            "resposta": resposta
        }), 207  # 207 = Partial Content
    
    return jsonify({
        "sucesso": True,
        "resposta": resposta
    }), 200
'''

print("\nPASSO 3.2: Integração Firebase")
print("Criar arquivo: api_firebase.py com o código acima")


# =============================================================================
# FASE 4: DEPLOY EM SERVIDOR
# =============================================================================

"""
PASSO 4.1: Deploy no Heroku (Opção 1 - Fácil)
"""

HEROKU_DEPLOY = '''
PASSO 4.1.1: Criar conta em https://heroku.com

PASSO 4.1.2: Instalar Heroku CLI
  - Windows: https://devcenter.heroku.com/articles/heroku-cli
  - Ou: choco install heroku-cli

PASSO 4.1.3: Criar arquivos necessários

Arquivo: Procfile
  web: gunicorn api:app

Arquivo: runtime.txt
  python-3.11.0

PASSO 4.1.4: Deploy
  heroku login
  heroku create padoc-ai-api
  git push heroku main
  
  # Verificar logs:
  heroku logs --tail

PASSO 4.1.5: Testar
  curl https://padoc-ai-api.herokuapp.com/api/saude
'''

print("\nPASSO 4.1: Deploy no Heroku")
print(HEROKU_DEPLOY)


"""
PASSO 4.2: Deploy no Google Cloud (Opção 2 - Profissional)
"""

GCLOUD_DEPLOY = '''
PASSO 4.2.1: Criar app.yaml para Cloud Run

app.yaml:
  runtime: python311
  
  env: flex
  
  runtime_config:
    python_version: 3
  
  env_variables:
    FIREBASE_CREDENTIALS_PATH: /app/firebase-key.json

PASSO 4.2.2: Deploy
  gcloud app deploy

PASSO 4.2.3: URL será: https://padoc-ai-XXXXX.appspot.com
'''

print("\nPASSO 4.2: Deploy no Google Cloud")
print(GCLOUD_DEPLOY)


# =============================================================================
# FASE 5: CONECTAR SITE + APP MOBILE
# =============================================================================

"""
PASSO 5.1: Frontend Web (HTML/JavaScript)
"""

FRONTEND_WEB = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PADOC AI - Diagnóstico Automotivo</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        input, textarea { width: 100%; padding: 10px; margin: 10px 0; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        .resposta { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 PADOC AI - Diagnóstico Automotivo</h1>
        
        <textarea id="pergunta" placeholder="Descreva o problema do seu carro..." rows="4"></textarea>
        <input type="text" id="usuario_id" placeholder="Seu ID (opcional)">
        <button onclick="enviarPergunta()">Obter Diagnóstico</button>
        
        <div id="resposta" class="resposta" style="display:none;"></div>
    </div>

    <script>
        const API_URL = "https://padoc-ai-api.herokuapp.com/api/diagnostico-firebase";
        
        async function enviarPergunta() {
            const pergunta = document.getElementById("pergunta").value;
            const usuario_id = document.getElementById("usuario_id").value || "anonimo";
            
            if (!pergunta.trim()) {
                alert("Digite uma pergunta!");
                return;
            }
            
            document.getElementById("resposta").innerHTML = "⏳ Processando...";
            document.getElementById("resposta").style.display = "block";
            
            try {
                const resposta = await fetch(API_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ pergunta, usuario_id })
                });
                
                const dados = await resposta.json();
                
                if (dados.sucesso) {
                    document.getElementById("resposta").innerHTML = 
                        "<strong>Diagnóstico:</strong><br>" + dados.resposta;
                } else {
                    document.getElementById("resposta").innerHTML = 
                        "Erro: " + dados.erro;
                }
            } catch (erro) {
                document.getElementById("resposta").innerHTML = 
                    "Erro ao conectar com a API: " + erro;
            }
        }
    </script>
</body>
</html>
'''

print("\nPASSO 5.1: Frontend Web")
print("Salvar em: site/index.html")
print(FRONTEND_WEB)


"""
PASSO 5.2: App Mobile (React Native / Flutter)
"""

MOBILE_EXAMPLE = '''
// Exemplo com React Native

import React, { useState } from 'react';
import { View, TextInput, Button, Text, ScrollView } from 'react-native';

const PadocApp = () => {
  const [pergunta, setPergunta] = useState('');
  const [resposta, setResposta] = useState('');
  const [carregando, setCarregando] = useState(false);

  const enviarPergunta = async () => {
    if (!pergunta.trim()) {
      alert('Digite uma pergunta!');
      return;
    }

    setCarregando(true);
    
    try {
      const response = await fetch(
        'https://padoc-ai-api.herokuapp.com/api/diagnostico-firebase',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            pergunta,
            usuario_id: 'mobile_user_123'  // Usar UID do Firebase Auth
          })
        }
      );

      const dados = await response.json();
      
      if (dados.sucesso) {
        setResposta(dados.resposta);
      } else {
        setResposta('Erro: ' + dados.erro);
      }
    } catch (erro) {
      setResposta('Erro ao conectar: ' + erro.message);
    } finally {
      setCarregando(false);
    }
  };

  return (
    <ScrollView style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>
        🚗 PADOC AI
      </Text>
      
      <TextInput
        style={{
          borderWidth: 1,
          padding: 10,
          marginBottom: 10,
          minHeight: 100,
          borderColor: '#ccc'
        }}
        placeholder="Descreva o problema do seu carro..."
        value={pergunta}
        onChangeText={setPergunta}
        multiline
      />
      
      <Button 
        title={carregando ? "Processando..." : "Obter Diagnóstico"}
        onPress={enviarPergunta}
        disabled={carregando}
      />
      
      {resposta && (
        <Text style={{ marginTop: 20, padding: 15, backgroundColor: '#f0f0f0' }}>
          {resposta}
        </Text>
      )}
    </ScrollView>
  );
};

export default PadocApp;
'''

print("\nPASSO 5.2: App Mobile (React Native)")
print(MOBILE_EXAMPLE)


# =============================================================================
# RESUMO DA ARQUITETURA FINAL
# =============================================================================

ARQUITETURA = '''
┌─────────────────────────────────────────────────────────────────┐
│                     ARQUITETURA PADOC AI                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [SITE: padoc.com.br]        [APP: iOS/Android]                 │
│          |                            |                           │
│          └────────────┬───────────────┘                          │
│                       ↓                                            │
│          [API REST: https://api.padoc.com.br]                    │
│          (Flask/Gunicorn)                                         │
│                       ↓                                            │
│  ┌──────────────────────────────────┐                            │
│  │  PADOC AI LLM (llama-cpp-python)  │                           │
│  ├──────────────────────────────────┤                            │
│  │ - Diagnóstico Automotivo          │                           │
│  │ - Base de Conhecimento (5 JSONs)  │                           │
│  │ - 132+ Registros de Histórico     │                           │
│  └──────────────────────────────────┘                            │
│                       ↓                                            │
│  ┌──────────────────────────────────┐                            │
│  │  FIREBASE                         │                            │
│  ├──────────────────────────────────┤                            │
│  │ - Realtime Database               │                            │
│  │ - Armazenar diagnósticos          │                            │
│  │ - Autenticação de usuários        │                            │
│  │ - Analytics                       │                            │
│  └──────────────────────────────────┘                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
'''

print("\n" + ARQUITETURA)


# =============================================================================
# CHECKLIST DE IMPLEMENTAÇÃO
# =============================================================================

CHECKLIST = '''
CHECKLIST COMPLETO
==================

FASE 1: TESTES LOCAIS
  ☐ Instalar dependências (pip install -r requirements.txt)
  ☐ Testar app.py local
  ☐ Executar validar_datasets.py
  ☐ Verificar se todos datasets carregam
  ☐ Testar chat interativo

FASE 2: API REST
  ☐ Criar arquivo api.py
  ☐ Testar endpoints:
    ☐ POST /api/diagnostico
    ☐ GET /api/saude
    ☐ GET /api/historico
  ☐ Testar com curl/Postman
  ☐ Testar com Python requests

FASE 3: FIREBASE
  ☐ Criar projeto Firebase
  ☐ Baixar credenciais (firebase-key.json)
  ☐ Criar arquivo .env
  ☐ Integrar Firebase na API
  ☐ Testar salvar/recuperar dados

FASE 4: DEPLOY
  ☐ Preparar Procfile e runtime.txt
  ☐ Fazer deploy em Heroku/Google Cloud
  ☐ Testar API em produção
  ☐ Configurar domínio customizado

FASE 5: FRONTEND
  ☐ Criar site HTML/JavaScript
  ☐ Criar app React Native/Flutter
  ☐ Integrar com Firebase Auth
  ☐ Testar ambos em produção
  ☐ Publicar em lojas (App Store/Google Play)

FASE 6: OTIMIZAÇÃO
  ☐ Setup SSL/HTTPS
  ☐ Cache de respostas
  ☐ Rate limiting
  ☐ Monitoramento de performance
  ☐ Backup automático do Firebase
'''

print("\n" + CHECKLIST)

print("\n\n✅ DOCUMENTAÇÃO COMPLETA GERADA!")
