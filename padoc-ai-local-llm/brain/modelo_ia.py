"""Motor LLM local para diagnóstico automotivo PADOC AI

Usa llama-cpp-python para executar modelo local sem API externa.
"""

from knowledge.banco_loader import carregar_base
import os
import json


class SistemaEspecialistaAutomotivo:
    def __init__(self):
        # Base de conhecimento avançada integrada
        self.base_dados = {
            "modelos": {},
            "esquemas_eletricos": {},
            "sintomas_visuais": {}
        }
        self.inicializar_dados_demo()

    def inicializar_dados_demo(self):
        """Alimenta o sistema com os módulos avançados sugeridos"""

        # 1. MÓDULO DE MODELOS + LIVE DATA (PARÂMETROS EM TEMPO REAL)
        self.base_dados["modelos"]["Gol 1.6 G6"] = {
            "marca": "Volkswagen",
            "motores": ["EA111", "MSI"],
            "defeitos_comuns": {
                "luz_epc_acesa": {
                    "causa": "Desgaste nas trilhas do Corpo de Borboleta (TBI) ou chicote oxidado.",
                    "codigos_obd2": ["P0121", "P0221"],
                    "valores_referencia_live": {
                        "posicao_borboleta_marcha_lenta": "3% a 5%",
                        "tensao_sinal_pino": "Estável próximo a 5V"
                    },
                    "teste_recomendado": "Medir resistência nos pinos do TBI movendo a borboleta manualmente buscando saltos bruscos."
                }
            }
        }

        # 2. MÓDULO DE ESQUEMAS ELÉTRICOS E PINOUTS
        self.base_dados["esquemas_eletricos"]["ECU Magneti Marelli 4GV"] = {
            "aplicacao": "Gol/Fox 1.6 EA111",
            "pinout": {
                "pino_15": "Alimentação pós-chave (+15)",
                "pino_30": "Alimentação direta da bateria (+30)",
                "pino_32": "Sinal de referência 5V para Sensor de Fase (CMP)",
                "pino_64": "Sinal de controle do relé da bomba de combustível"
            }
        }

        # 3. MÓDULO DE SINTOMAS VISUAIS E AUDITIVOS
        self.base_dados["sintomas_visuais"] = {
            "fumaça_azulada": "Óleo lubrificante sendo queimado na câmara de combustão (Prováveis anéis de pistão gastos ou retentores de válvula danificados).",
            "fumaça_branca_densa": "Líquido de arrefecimento (água) entrando nos cilindros (Provável junta do cabeçote queimada).",
            "oleo_cafe_com_leite": "Mistura crítica de água no óleo. Verificar trocador de calor do câmbio/óleo ou junta de cabeçote imediatamente."
        }

    # --- FUNÇÃO 1: ANALISADOR DE PARÂMETROS AO VIVO (LIVE DATA) ---
    def analisar_dados_vivos(self, modelo, defeito_chave, valor_atual_sensor):
        """Compara os dados atuais do scanner do usuário com o padrão ideal de fábrica"""
        if modelo in self.base_dados["modelos"]:
            defeitos = self.base_dados["modelos"][modelo]["defeitos_comuns"]
            if defeito_chave in defeitos:
                ref = defeitos[defeito_chave]["valores_referencia_live"]
                return {
                    "Status": "Análise Concluída",
                    "Valores de Referência Esperados": ref,
                    "Valor Fornecido pelo Usuário": valor_atual_sensor,
                    "Ação Recomendada": defeitos[defeito_chave].get("teste_recomendado", "Teste recomendado não disponível")
                }
        return {"Erro": "Modelo ou sintoma não mapeado na base de dados vivos."}

    # --- FUNÇÃO 2: ÁRVORE DE DECISÃO / DIAGNÓSTICO GUIADO ---
    def iniciar_diagnostico_guiado(self):
        """Simula a linha de raciocínio de um mecânico através de perguntas"""
        print("\n--- INICIANDO DIAGNÓSTICO GUIADO ---")
        p1 = input("O ruído/problema é na [1] Dianteira (Suspensão/Motor) ou [2] Traseira? (Digite 1 ou 2): ")

        if p1 == "1":
            p2 = input("O barulho ocorre ao [1] Passar em lombadas/buracos ou [2] Ao esterçar o volante parado? (Digite 1 ou 2): ")
            if p2 == "1":
                return "Diagnóstico: Alta probabilidade de desgaste nas Bieletas ou Buchas da Barra Estabilizadora."
            elif p2 == "2":
                return "Diagnóstico: Verificar Rolamento do Coxim do Amortecedor ou falta de óleo na bomba de direção."
        elif p1 == "2":
            p2 = input("O som é um [1] Estalo seco em ondulações ou [2] Um zumbido constante que aumenta com a velocidade? (Digite 1 ou 2): ")
            if p2 == "1":
                return "Diagnóstico: Verificar buchas dos braços tensores traseiros."
            elif p2 == "2":
                return "Diagnóstico: Forte indício de Rolamento de Roda traseiro danificado."

        return "Sintoma não catalogado na árvore de decisão básica."

    # --- FUNÇÃO 3: CONSULTA DE PINOUT E COMPONENTES ELÉTRICOS ---
    def consultar_pinout(self, central, pino):
        """Retorna a função exata de um fio no chicote elétrico da injeção"""
        if central in self.base_dados["esquemas_eletricos"]:
            mapeamento = self.base_dados["esquemas_eletricos"][central]["pinout"]
            pino_busca = f"pino_{pino}"
            if pino_busca in mapeamento:
                return f"Central {central} -> {pino_busca.upper()}: {mapeamento[pino_busca]}"
            return f"Pino {pino} não encontrado na central {central}."
        return "Central elétrica/ECU não cadastrada."

    # --- FUNÇÃO 4: CONVERSOR DE SINTOMAS SENSORIAIS ---
    def analisar_sintoma_visual(self, termo_chave):
        """Interpreta termos leigos como cores de fumaça e texturas de fluidos"""
        termo_ajustado = termo_chave.lower().replace(" ", "_")
        if termo_ajustado in self.base_dados["sintomas_visuais"]:
            return f"Análise Sensorial: {self.base_dados['sintomas_visuais'][termo_ajustado]}"
        return "Sintoma visual não reconhecido. Tente termos como: 'fumaça azulada', 'fumaça branca densa' ou 'oleo cafe com leite'."


class PadocAI:
    """Classe principal para diagnóstico automotivo com LLM local."""

    def __init__(self):
        """Inicializa PADOC AI carregando modelo e base de dados."""
        self.base = carregar_base()
        if not self.base:
            raise ValueError("Base de dados vazia. Verifique os arquivos JSON.")
        
        # Resolve o caminho do modelo dinamicamente
        base_path = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_path, "models", "padoc-model.gguf")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo GGUF não encontrado em: {model_path}")

        try:
            from llama_cpp import Llama
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError("llama_cpp não encontrado. Instale com pip install llama-cpp-python") from e

        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_threads=8,
                verbose=False
            )
        except Exception as e:
            raise RuntimeError(f"Erro ao inicializar o motor LLM: {e}") from e

    def _preparar_contexto(self, pergunta):
        """Prepara o contexto com dados relevantes para a pergunta.
        
        Args:
            pergunta: Pergunta do usuário
            
        Returns:
            String formatada com contexto para o LLM
        """
        if not pergunta or not isinstance(pergunta, str):
            raise ValueError("Pergunta inválida")

        # Prioriza seções principais
        secao_base = {
            "metadata": self.base.get("metadata"),
            "codigos_obd2": self.base.get("codigos_obd2"),
            "problemas_conhecidos_por_modelo": self.base.get("problemas_conhecidos_por_modelo"),
            "defeitos_mecanicos_e_manutencao": self.base.get("defeitos_mecanicos_e_manutencao"),
            "historico_ordens_servico": self.base.get("historico_ordens_servico"),
        }
        # Adiciona demais seções
        secao_base.update({
            k: v for k, v in self.base.items() if k not in secao_base
        })

        # Limita tamanho do JSON para não sobrecarregar o prompt
        json_base = json.dumps(secao_base, indent=2, ensure_ascii=False)[:5000]

        contexto = f"""Você é a PADOC AI, especialista em diagnóstico automotivo com 20 anos de experiência.

Use estas seções de base técnica:
- Códigos OBD2 (diagnóstico)
- Problemas conhecidos por marca/modelo
- Defeitos mecânicos e elétricos
- Histórico de reparações

Base técnica:
{json_base}

Pergunta: {pergunta}

Responda como um mecânico especialista:
1. Possíveis defeitos
2. Causas mais prováveis
3. Testes recomendados
4. Solução e custo estimado
5. Nível de urgência
6. Perguntas para confirmar diagnóstico
"""
        return contexto

    def gerar_resposta(self, pergunta):
        """Gera resposta de diagnóstico para a pergunta.
        
        Args:
            pergunta: Pergunta do usuário
            
        Returns:
            Resposta de diagnóstico do LLM
        """
        try:
            contexto = self._preparar_contexto(pergunta)

            resposta = self.llm(
                contexto,
                max_tokens=500,
                temperature=0.6,
                top_p=0.9,
                repeat_penalty=1.1
            )

            if not resposta or "choices" not in resposta:
                return ""

            texto = resposta["choices"][0]["text"].strip()
            return texto if texto else ""

        except ValueError as e:
            raise ValueError(f"Erro de validação: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar resposta: {e}") from e

    def diagnosticar(self, pergunta):
        """Interface pública para diagnóstico.
        
        Args:
            pergunta: Pergunta do usuário
            
        Returns:
            Diagnóstico da IA
        """
        return self.gerar_resposta(pergunta)

    # ------------------ WRAPPERS DO SISTEMA ESPECIALISTA ------------------
    def analisar_dados_vivos(self, modelo, defeito_chave, valor_atual_sensor):
        """Retorna a análise de live data do sistema especialista."""
        especialista = SistemaEspecialistaAutomotivo()
        return especialista.analisar_dados_vivos(modelo, defeito_chave, valor_atual_sensor)

    def iniciar_diagnostico_guiado(self):
        """Inicia a árvore de decisão guiada do sistema especialista."""
        especialista = SistemaEspecialistaAutomotivo()
        return especialista.iniciar_diagnostico_guiado()

    def consultar_pinout(self, central, pino):
        """Consulta o pinout elétrico de uma central."""
        especialista = SistemaEspecialistaAutomotivo()
        return especialista.consultar_pinout(central, pino)

    def analisar_sintoma_visual(self, termo_chave):
        """Analisa sintomas visuais pelo sistema especialista."""
        especialista = SistemaEspecialistaAutomotivo()
        return especialista.analisar_sintoma_visual(termo_chave)
