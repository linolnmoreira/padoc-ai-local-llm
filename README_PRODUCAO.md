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

### Instalar Flask:
```powershell
pip install flask flask-cors
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

## ☁️ PASSO 5: DEPLOY NO HEROKU (20 min)

### 5.1 Criar Conta
- https://heroku.com → **Sign up**

### 5.2 Instalar CLIhttps://devcenter.heroku.com/articles/heroku-cli
- Download: 
- Verificar: `heroku --version`

### 5.3 Criar Arquivos

**Procfile** (sem extensão):
```
web: gunicorn api:app
```

**runtime.txt**:
```
python-3.11.0
```

**requirements.txt** (adicionar):
```
gunicorn==20.1.0
```

### 5.4 Deploy
```bash
heroku login
heroku create padoc-ai-api
git add .
git commit -m "Deploy PADOC AI"
git push heroku main
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
