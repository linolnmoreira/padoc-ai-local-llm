# PADOC AI: DO LOCAL PARA PRODUÇÃO
## Guia Completo: Transformar em Aplicação Web + Mobile + Firebase

---

## 📋 RESUMO EXECUTIVO

Você tem uma aplicação PADOC AI pronta. Aqui estão os **8 passos** para transformá-la em um sistema web + mobile profissional:

| Passo | Tarefa | Tempo | Status |
|-------|--------|-------|--------|
| 1️⃣ | Testar Local | 5 min | ✅ Pronto |
| 2️⃣ | Criar API REST | 10 min | ✅ Criado (api.py) |
| 3️⃣ | Testar Site HTML | 2 min | ✅ Criado (site_padoc.html) |
| 4️⃣ | Integrar Firebase | 15 min | ✅ Criado (firebase_integration.py) |
| 5️⃣ | Deploy Heroku | 20 min | 📖 Instruções |
| 6️⃣ | Hospedar Site | 10 min | 📖 Instruções |
| 7️⃣ | App Mobile | 30-60 min | 📖 Instruções |
| 8️⃣ | Verificação Final | 1-2 min | 📖 Checklist |
| | **TOTAL** | **2-4 horas** | ✅ |

---

## 🚀 PASSO 1: TESTAR LOCAL (5 min)

### Terminal PowerShell:
```powershell
cd c:\Users\User\Downloads\padoc-ai-local-llm\padoc-ai-local-llm
python validar_datasets.py
```

### ✓ Resultado Esperado:
```
✓ Encontrados 5 arquivos JSON
✓ Função carregar_base() executada com sucesso
✓ Base é um dicionário com 6 chaves
✓ Total de 132 registros carregados
```

---

## 🌐 PASSO 2: CRIAR API REST (10 min)


### 2.1 Ativar Ambiente Virtual (se ainda não estiver ativo)
No PowerShell, navegue até a pasta do projeto e execute:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2.2 Instalar Flask (com o ambiente ativo)
```powershell
python -m pip install flask flask-cors
```

### Iniciar API (Terminal 1):
```powershell
python api.py
```

### ✓ Resultado: `* Running on http://localhost:5000`

### Testar (Terminal 2):
```bash
# Verificar saúde
curl http://localhost:5000/api/saude

# Enviar diagnóstico
curl -X POST http://localhost:5000/api/diagnostico \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Carro não pega", "usuario_id": "teste123"}'
```

---

## 📱 PASSO 3: TESTAR SITE HTML (2 min)

### Abrir no Navegador:
1. Abra o arquivo `site_padoc.html` (duplo clique) ou arraste-o para o navegador.
2. No campo de texto, descreva o problema (ex.: "Motor com barulho estranho").
3. Clique em "Obter Diagnóstico" e aguarde a resposta.

### ✓ Resultado:
- Página carregada com formulário do `site_padoc.html`
- Histórico salvo localmente (localStorage)
- Resposta da IA exibida

---

## 🔥 PASSO 4: INTEGRAR FIREBASE (15 min)

### 4.1 Criar Projeto Firebase
- Ir para: https://console.firebase.google.com
- "Criar novo projeto"
- Nome: "padoc-ai"

### 4.2 Ativar Realtime Database
- Menu: **Realtime Database**
- "Criar base de dados"
- Selecione: **Modo de teste**
- Copie a URL (vai precisar)

### 4.3 Obter Credenciais
- Configurações → **Contas de Serviço**
- "Gerar nova chave privada"
- Salvar como: `firebase-key.json`

### 4.4 Criar Arquivo `.env`
```
FIREBASE_CREDENTIALS_PATH=./firebase-key.json
FIREBASE_DATABASE_URL=https://seu-projeto-padoc.firebaseio.com
FLASK_ENV=development
DEBUG=True
```

### 4.5 Instalar Dependências
```powershell
pip install firebase-admin python-dotenv
```

### ✓ Resultado: Dados salvos automaticamente no Firebase

---

## ☁️ PASSO 5: DEPLOY DA API NA NUVEM (20 min)

### Opção A: Render (Recomendado)

1.  **Criar Conta no Render e GitHub**:
    *   Crie uma conta em: https://render.com (pode usar sua conta do GitHub).
    *   Certifique-se que seu projeto está em um repositório no GitHub.

2.  **Criar um "Web Service"**:
    *   No dashboard do Render, clique em **New +** → **Web Service**.
    *   Conecte seu repositório do GitHub e selecione o repositório do projeto `padoc-ai`.

3.  **Configurar o Serviço**:
    *   **Name**: `padoc-ai-api` (ou o nome que preferir).
    *   **Region**: Escolha uma região próxima (ex: `Ohio (US East)`).
    *   **Branch**: `main` (ou a branch principal do seu projeto).
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn api:app`
    *   **Instance Type**: `Free`

4.  **Adicionar Variáveis de Ambiente**:
    *   Vá para a aba **Environment**.
    *   Clique em **Add Environment Variable**.
    *   Adicione a chave `FIREBASE_DATABASE_URL` com o valor da URL do seu Realtime Database.

5.  **Adicionar o Arquivo de Credenciais (Secret File)**:
    *   Ainda em **Environment**, role para baixo até **Secret Files**.
    *   Clique em **Add Secret File**.
    *   **Filename**: `firebase-key.json`
    *   **Contents**: Copie e cole todo o conteúdo do seu arquivo `firebase-key.json` local.

6.  **Fazer o Deploy**:
    *   Clique em **Create Web Service**.
    *   O Render irá construir e iniciar sua aplicação. Você pode acompanhar os logs em tempo real.

### ✓ Resultado:
Sua API estará no ar em uma URL como: `https://padoc-ai-api.onrender.com`. Use essa URL no Passo 6.

---

### Opção C: DigitalOcean (Alternativa Profissional)

1.  **Criar Conta e Projeto**:
    *   Crie uma conta em: https://www.digitalocean.com.
    *   No painel, vá para **Create** -> **Apps**.

2.  **Conectar Repositório**:
    *   Escolha o GitHub (ou outro provedor) e selecione o repositório do seu projeto `padoc-ai`.

3.  **Configurar a Aplicação**:
    *   O DigitalOcean irá detectar seu projeto Python e o `Procfile`.
    *   **App Spec**: Verifique se o comando de execução (`run command`) está correto: `gunicorn api:app --bind 0.0.0.0:${PORT}`.
    *   **Build Command**: O padrão `pip install -r requirements.txt` deve ser detectado automaticamente.

4.  **Adicionar Variáveis de Ambiente**:
    *   Na etapa de configuração, vá para **Environment Variables**.
    *   Clique em **Edit** e depois em **Add Variable**.
    *   Adicione a chave `FIREBASE_DATABASE_URL` com o valor da URL do seu Realtime Database.
    *   Para as credenciais do Firebase, adicione outra variável:
        *   **Key**: `FIREBASE_CREDENTIALS_JSON`
        *   **Value**: Copie e cole **todo o conteúdo** do seu arquivo `firebase-key.json` aqui.
        *   Marque a caixa **Encrypt** para proteger a credencial.

5.  **Fazer o Deploy**:
    *   Revise as configurações e clique em **Create Resources**.
    *   O DigitalOcean irá construir e implantar sua aplicação.

### ✓ Resultado:
Sua API estará no ar em uma URL como: `https://padoc-ai-api-xxxxx.ondigitalocean.app`. Use essa URL para conectar seu site.

---

### Opção B: Heroku (Alternativa)

#### 5.1 Criar Conta e Instalar CLI
- **Conta**: https://heroku.com → **Sign up**
- **CLI**: https://devcenter.heroku.com/articles/heroku-cli

#### 5.2 Criar Arquivos

**Procfile** (sem extensão): `web: gunicorn api:app`

**runtime.txt**: `python-3.11.0`

**requirements.txt** (adicionar): `gunicorn==20.1.0`

#### 5.3 Deploy
```bash
heroku login
heroku create padoc-ai-api
git add .
git commit -m "Deploy PADOC AI"
git push heroku main

# Configurar variáveis de ambiente (IMPORTANTE)
# O Heroku não tem um bom suporte para arquivos secretos, então o ideal é usar variáveis de ambiente.
# Converta seu firebase-key.json para uma string de uma linha e adicione:
# heroku config:set FIREBASE_CREDENTIALS_JSON='...'
# heroku config:set FIREBASE_DATABASE_URL='...'
# E ajuste o firebase_integration.py para ler a variável de ambiente.
```

### ✓ Resultado:
```
API em produção: https://padoc-ai-api.herokuapp.com/api/saude
```

---

## 🌍 PASSO 6: HOSPEDAR SITE (10 min)

### OPÇÃO A: GitHub Pages (Grátis)
1. Criar repositório em: https://github.com/new
2. Nome: "padoc-ai-site"
3. Upload: `site_padoc.html`
4. Settings → **Pages** → ativar
5. Site em: `https://seu-usuario.github.io/padoc-ai-site`

### OPÇÃO B: Vercel (Automático)
1. Ir para: https://vercel.com
2. "Deploy"
3. Conectar GitHub
4. Selecionar repositório
5. Site em: `https://seu-projeto.vercel.app`

### ⚠️ IMPORTANTE: Editar site_padoc.html

Trocar esta linha:
```javascript
const API_URL = "http://localhost:5000/api/diagnostico";
```

Para:
```javascript
const API_URL = "https://padoc-ai-api.herokuapp.com/api/diagnostico";
```

---

## 📱 PASSO 7: APP MOBILE (30-60 min, OPCIONAL)

### Opção A: React Native (Recomendado)
```bash
npm install -g expo-cli
npx create-expo-app PadocAI
cd PadocAI
npm install firebase http
npx expo start
```
✓ App roda no seu celular via **Expo Go**

### Opção B: Flutter
```bash
flutter create padoc_ai
cd padoc_ai
flutter run
```
✓ App roda direto no seu celular

---

## ✅ PASSO 8: VERIFICAÇÃO FINAL (1-2 min)

### Checklist Antes de Lançar:
```
☐ python validar_datasets.py → OK
☐ API local responde → OK
☐ Site HTML funciona → OK
☐ Firebase salva dados → OK
☐ Deploy Heroku bem-sucedido → OK
☐ Site hospedado e acessível → OK
☐ Site conecta à API em produção → OK
☐ App mobile (se fizer) → OK
```

---

## 📊 ARQUITETURA FINAL

```
[SITE: padoc.com.br]    [APP: iOS/Android]    [Admin]
           ↓                      ↓               ↓
    ┌─────────────────────────────────────┐
    │    API REST (Heroku)                │
    │ https://padoc-ai-api.herokuapp.com  │
    └─────────────────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │   PADOC AI Motor LLM                │
    │   - llama-cpp-python                │
    │   - 132 registros histórico          │
    │   - 6 JSONs conhecimento             │
    └─────────────────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │   FIREBASE (Cloud)                  │
    │   - Realtime Database               │
    │   - Autenticação (opcional)         │
    │   - Analytics                       │
    │   - Backup automático               │
    └─────────────────────────────────────┘
```

---

## 📦 ARQUIVOS CRIADOS

| Arquivo | Descrição | Pronto? |
|---------|-----------|---------|
| `api.py` | API REST com 3 endpoints | ✅ |
| `firebase_integration.py` | Integração Firebase | ✅ |
| `site_padoc.html` | Site responsivo + JS | ✅ |
| `GUIA_PRODUCAO.py` | Doc completa (2.500+ linhas) | ✅ |
| `GUIA_TESTES.py` | Comandos prontos | ✅ |
| `COMECE_AQUI.py` | Este arquivo resumido | ✅ |
| `PROXIMOS_PASSOS.txt` | Checklist em texto | ✅ |

---

## ⏱️ TEMPO TOTAL

- **Sem app mobile**: 2-3 horas
- **Com app mobile**: 3-4 horas

---

## 🎯 O QUE VOCÊ VAI TER

✅ API REST profissional em: `https://padoc-ai-api.herokuapp.com`
✅ Site responsivo em: `https://seu-dominio.com` ou Vercel
✅ App mobile iOS/Android (opcional)
✅ Banco de dados Firebase em tempo real
✅ 132 registros histórico
✅ 6 datasets conhecimento automotivo
✅ Sistema escalável e pronto para produção

---

## 📚 SUPORTE & DOCUMENTAÇÃO

- **Detalhes de cada passo**: `GUIA_PRODUCAO.py`
- **Comandos prontos para copiar/colar**: `GUIA_TESTES.py`
- **Documentação oficial**:
  - Flask: https://flask.palletsprojects.com
  - Firebase: https://firebase.google.com/docs
  - Heroku: https://devcenter.heroku.com
  - React Native: https://reactnative.dev

---

## 🚀 COMECE AGORA!

```bash
cd c:\Users\User\Downloads\padoc-ai-local-llm\padoc-ai-local-llm
python validar_datasets.py
```

Se tudo der OK, você está pronto para o **PASSO 2**!

---

**Boa sorte no seu projeto PADOC AI!** 🎉

_Documentação gerada: 17 de junho de 2026_
