try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_AVAILABLE = True
except ImportError:
    firebase_admin = None
    credentials = None
    db = None
    FIREBASE_AVAILABLE = False

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from datetime import datetime
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

# Inicializar Firebase
def inicializar_firebase():
    """Inicializar conexão com Firebase"""
    if not FIREBASE_AVAILABLE:
        logger.info("ℹ️ Firebase SDK não instalado. Operando em modo de persistência local.")
        return False
    try:
        # Tenta carregar a partir de uma variável de ambiente (ideal para produção)
        firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if firebase_creds_json:
            cred_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(cred_dict)
            logger.info("✓ Firebase inicializado via variável de ambiente.")
        else:
            # Fallback para arquivo local (bom para desenvolvimento)
            firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-key.json")
            if not os.path.exists(firebase_cred_path):
                logger.warning(f"Arquivo Firebase não encontrado: {firebase_cred_path}")
                return False
            cred = credentials.Certificate(firebase_cred_path)
            logger.info("✓ Firebase inicializado via arquivo local.")

        firebase_admin.initialize_app(cred, {
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "")
        })

        logger.info("✓ Conexão com Firebase estabelecida.")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao inicializar Firebase: {e}")
        return False


def salvar_diagnostico(usuario_id, pergunta, resposta):
    """Salvar diagnóstico no Firebase Realtime Database
    
    Args:
        usuario_id: ID do usuário
        pergunta: Pergunta do usuário
        resposta: Resposta da IA
        
    Returns:
        bool: True se sucesso, False caso contrário
    """
    try:
        ref = db.reference("diagnosticos")
        novo_diagnostico = {
            "usuario_id": usuario_id,
            "pergunta": pergunta,
            "resposta": resposta,
            "timestamp": datetime.now().isoformat(),
            "versao": "1.0"
        }
        
        ref.push(novo_diagnostico)
        logger.info(f"✓ Diagnóstico salvo para usuário {usuario_id}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar no Firebase: {e}")
        return False


def obter_diagnosticos_usuario(usuario_id, limite=10):
    """Obter diagnósticos de um usuário
    
    Args:
        usuario_id: ID do usuário
        limite: Número máximo de registros
        
    Returns:
        list: Lista de diagnósticos
    """
    try:
        ref = db.reference("diagnosticos")
        # Query para usuário específico
        diagnosticos = ref.order_by_child("usuario_id").equal_to(usuario_id).get()
        
        if diagnosticos:
            lista = list(diagnosticos.values())
            return lista[-limite:]  # Retornar os últimos N registros
        return []
    except Exception as e:
        logger.error(f"Erro ao obter diagnósticos: {e}")
        return []


def obter_ultimo_diagnostico(usuario_id):
    """Obter último diagnóstico de um usuário"""
    try:
        diagnosticos = obter_diagnosticos_usuario(usuario_id, limite=1)
        return diagnosticos[0] if diagnosticos else None
    except Exception as e:
        logger.error(f"Erro ao obter último diagnóstico: {e}")
        return None


def deletar_diagnostico(chave_diagnostico):
    """Deletar um diagnóstico específico"""
    try:
        ref = db.reference(f"diagnosticos/{chave_diagnostico}")
        ref.delete()
        logger.info(f"✓ Diagnóstico deletado: {chave_diagnostico}")
        return True
    except Exception as e:
        logger.error(f"Erro ao deletar diagnóstico: {e}")
        return False


def obter_estatisticas_globais():
    """Obter estatísticas de uso global"""
    try:
        ref = db.reference("diagnosticos")
        todos = ref.get()
        
        if not todos:
            return {
                "total_diagnosticos": 0,
                "usuarios_unicos": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        usuarios = set()
        for diag in todos.values():
            usuarios.add(diag.get("usuario_id", ""))
        
        return {
            "total_diagnosticos": len(todos),
            "usuarios_unicos": len(usuarios),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {}


def salvar_aprendizado(pergunta, resposta):
    """Salva uma nova interação na base de conhecimento do Firebase para aprendizado contínuo."""
    try:
        # Usamos um hash da pergunta como chave para evitar duplicatas e caracteres inválidos
        import hashlib
        chave_pergunta = hashlib.sha1(pergunta.encode('utf-8')).hexdigest()

        ref = db.reference(f"conhecimento/{chave_pergunta}")
        
        novo_conhecimento = {
            "pergunta": pergunta,
            "resposta": resposta,
            "criado": datetime.now().isoformat(),
            "fonte": "PADOC AI LLM"
        }
        
        ref.set(novo_conhecimento) # .set() para criar ou sobrescrever se a pergunta for idêntica
        logger.info(f"✓ Novo conhecimento salvo no Firebase para a pergunta: '{pergunta[:30]}...'")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao salvar aprendizado no Firebase: {e}")
        return False


def salvar_evento(placa_veiculo, tipo_evento, dados_evento):
    """
    NOVA FUNÇÃO: Salva um evento de hardware (colisão, geofence, etc.) no Firebase.

    Args:
        placa_veiculo (str): Placa do veículo associado ao evento.
        tipo_evento (str): Tipo do evento (ex: 'colisao', 'geofence_entrada').
        dados_evento (dict): Dicionário com os detalhes do evento analisado pela IA.

    Returns:
        bool: True se o evento foi salvo com sucesso, False caso contrário.
    """
    try:
        # Cria uma referência para um novo nó 'eventos_veiculares' no banco
        ref = db.reference("eventos_veiculares")
        
        novo_evento = {
            "placa": placa_veiculo,
            "tipo_evento": tipo_evento,
            "dados_evento": dados_evento,
            "timestamp": datetime.now().isoformat()
        }
        
        ref.push(novo_evento)
        logger.info(f"✓ Evento '{tipo_evento}' salvo para o veículo {placa_veiculo}")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao salvar evento no Firebase: {e}")
        return False

# Arquivo .env (NUNCA comitar no Git!)
ENV_TEMPLATE = """
# .env - Variáveis de Ambiente PADOC AI
FIREBASE_CREDENTIALS_PATH=./firebase-key.json
FIREBASE_DATABASE_URL=https://seu-projeto-padoc.firebaseio.com
FLASK_ENV=development
DEBUG=True
"""

if __name__ == "__main__":
    # Teste das funções
    if inicializar_firebase():
        print("✓ Firebase pronto")
        
        # Testar salvamento
        salvar_diagnostico(
            "user_teste_123",
            "Meu carro não pega",
            "Possíveis causas: bateria fraca, combustível vencido, velas de ignição..."
        )
        
        # Testar recuperação
        diagnosticos = obter_diagnosticos_usuario("user_teste_123")
        print(f"Diagnosticos recuperados: {len(diagnosticos)}")
        
        # Testar estatísticas
        stats = obter_estatisticas_globais()
        print(f"Estatísticas: {stats}")
