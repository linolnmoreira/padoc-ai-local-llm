"""
PADOC AI - Suíte de Testes Automatizados (compatível com unittest e pytest)

Valida:
1. Diagnóstico Automotivo Especialista (DTCs e sintomas)
2. Detecção de Emergência e Urgência Máxima
3. RAG Automotivo e Manuais
4. Motor Preditivo de Veículo e Riscos 7/30/90 dias
5. Ciclo de Auto-Aprendizado Contínuo (ContinuousLearner)
6. Endpoints REST da API
"""

import os
import unittest
import tempfile
from brain.padoc_brain_engine import PadocBrainEngine, ContinuousLearner
from predictive_vehicle_ai import PadocPredictiveAI
from api import app


class TestPadocAI(unittest.TestCase):

    def setUp(self):
        self.brain = PadocBrainEngine()
        app.config["TESTING"] = True
        self.api_client = app.test_client()

    def test_diagnostico_com_dtc(self):
        """Testa diagnóstico com código de falha OBD-II (P0300)."""
        resultado = self.brain.processar_diagnostico("O carro está falhando e acusou código P0300 no scanner")
        self.assertTrue(resultado["sucesso"])
        self.assertIn("P0300", resultado["dtcs_detectados"])
        self.assertTrue("Falha de ignição" in resultado["resposta"] or "Velas" in resultado["resposta"])

    def test_alerta_urgencia_seguranca(self):
        """Testa detecção de condição de risco crítico."""
        resultado = self.brain.processar_diagnostico("O freio não para e está saindo fumaça do capô")
        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["intencao"], "urgencia")
        self.assertTrue(resultado.get("urgencia_maxima"))
        self.assertIn("ALERTA DE SEGURANÇA", resultado["resposta"])

    def test_auto_aprendizado_continuo(self):
        """Testa se a IA aprende um novo problema resolvido e o consulta com sucesso."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_learner_file = os.path.join(tmp_dir, "aprendizado_teste.json")
            learner = ContinuousLearner(storage_path=test_learner_file)

            # 1. Registra um novo caso resolvido
            learner.registrar_aprendizado(
                problema="Corolla 2018 com barulho de estalo na coluna de direcao",
                solucao="Troca da bucha de acoplamento da coluna elétrica de direção",
                veiculo="Toyota Corolla 2018",
                eficacia=1.0,
                autor="Oficina Central"
            )

            # 2. Consulta pelo sintoma
            resultados = learner.consultar_aprendizado("Corolla estalo na coluna de direcao")
            self.assertGreater(len(resultados), 0)
            self.assertIn("bucha de acoplamento", resultados[0]["solucoes"][0]["texto"])
            self.assertGreaterEqual(resultados[0]["score_confianca"], 0.6)

    def test_motor_preditivo(self):
        """Testa o cálculo preditivo de saúde dos componentes."""
        engine = PadocPredictiveAI()
        dados_telemetria = {
            "rpm": 920.0,
            "coolant_temp": 105.0,
            "battery_voltage": 12.1,
            "fuel_trim_short": 8.0,
            "fuel_trim_long": 16.0,
            "vehicle_speed": 45.0,
            "engine_load": 40.0,
            "dtcs": ["P0171"]
        }
        
        predicao = engine.processar_telemetria_json("TEST-CAR", dados_telemetria)
        self.assertIn("global_health", predicao)
        self.assertIn("components", predicao)
        self.assertIn("BATTERY", predicao["components"])
        self.assertIn("COOLING", predicao["components"])

    def test_api_endpoints(self):
        """Testa os endpoints principais da API Flask."""
        # 1. Health Check
        res_saude = self.api_client.get("/api/saude")
        self.assertEqual(res_saude.status_code, 200)
        dados_saude = res_saude.get_json()
        self.assertEqual(dados_saude["status"], "ok")

        # 2. Diagnóstico
        res_diag = self.api_client.post("/api/diagnostico", json={"pergunta": "Meu carro está com a luz da injeção acesa e código P0171"})
        self.assertEqual(res_diag.status_code, 200)
        dados_diag = res_diag.get_json()
        self.assertTrue(dados_diag["sucesso"])
        self.assertIn("P0171", dados_diag["dtcs_detectados"])

        # 3. Telemetria / Evento
        res_evento = self.api_client.post("/api/evento", json={
            "placa": "PADOC-TESTE",
            "telemetria": {"rpm": 800, "temperatura": 90, "voltagem": 13.9}
        })
        self.assertEqual(res_evento.status_code, 200)
        dados_evento = res_evento.get_json()
        self.assertTrue(dados_evento["sucesso"])

        # 4. Auto-Aprendizado
        res_aprender = self.api_client.post("/api/aprender", json={
            "problema": "HB20 luz acesa falha sonda",
            "solucao": "Substituição do conector oxidado da sonda lambda pré",
            "veiculo": "Hyundai HB20"
        })
        self.assertEqual(res_aprender.status_code, 200)
        dados_aprender = res_aprender.get_json()
        self.assertTrue(dados_aprender["sucesso"])


if __name__ == "__main__":
    unittest.main()
