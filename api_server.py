"""
Servidor API Moderno PADOC AI com FastAPI & WebSockets

Oferece endpoints assíncronos de alta performance para:
- Diagnósticos automotivos em tempo real
- Streaming de telemetria via WebSockets
- Ingestão de eventos e telemetria preditiva
- Auto-Aprendizado contínuo
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from brain.padoc_brain_engine import brain_engine
from predictive_vehicle_ai import predictive_engine

logger = logging.getLogger("padoc_fastapi")

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="PADOC AI - NextGen Automotive Intelligence API",
        version="2.5.0",
        description="API de Diagnóstico Mecânico, RAG Automotivo, IA Preditiva e Auto-Aprendizado."
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class DiagnosticoRequest(BaseModel):
        pergunta: str
        usuario_id: Optional[str] = "anonimo"
        contexto: Optional[Dict[str, Any]] = None

    class EventoRequest(BaseModel):
        placa: Optional[str] = "PADOC-001"
        tipo_evento: Optional[str] = "telemetria"
        telemetria: Optional[Dict[str, Any]] = None

    class AprendizadoRequest(BaseModel):
        problema: str
        solucao: str
        veiculo: Optional[str] = "Geral"
        eficacia: Optional[float] = 1.0
        autor: Optional[str] = "oficina"

    @app.get("/api/saude")
    async def saude():
        return {
            "status": "ok",
            "framework": "FastAPI",
            "cerebro_ia": True,
            "engine_preditivo": True,
            "padroes_aprendidos": len(brain_engine.learner.memoria.get("padroes_aprendidos", {})),
            "timestamp": datetime.now().isoformat()
        }

    @app.post("/api/diagnostico")
    async def diagnostico(req: DiagnosticoRequest):
        try:
            return brain_engine.processar_diagnostico(
                pergunta=req.pergunta,
                usuario_id=req.usuario_id,
                contexto_veiculo=req.contexto
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/evento")
    async def evento(req: EventoRequest):
        try:
            telemetria_dados = req.telemetria or {}
            predicao = predictive_engine.processar_telemetria_json(
                vehicle_id=req.placa,
                dados=telemetria_dados
            )
            return {
                "sucesso": True,
                "veiculo_id": req.placa,
                "analise_preditiva": predicao,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/aprender")
    async def aprender(req: AprendizadoRequest):
        return brain_engine.retroalimentar_aprendizado(
            problema=req.problema,
            solucao=req.solucao,
            veiculo=req.veiculo,
            eficacia=req.eficacia,
            autor=req.autor
        )

    @app.websocket("/ws/telemetria")
    async def websocket_telemetry(websocket: WebSocket):
        await websocket.accept()
        logger.info("📡 Cliente conectado via WebSocket para Telemetria em Tempo Real.")
        try:
            while True:
                texto = await websocket.receive_text()
                dados = json.loads(texto)
                placa = dados.get("placa", "PADOC-REALTIME")
                resultado = predictive_engine.processar_telemetria_json(placa, dados)
                await websocket.send_text(json.dumps({
                    "tipo": "telemetria_preditiva",
                    "dados": resultado,
                    "timestamp": datetime.now().isoformat()
                }))
        except WebSocketDisconnect:
            logger.info("📡 Cliente desconectado do WebSocket de Telemetria.")
        except Exception as e:
            logger.error(f"Erro no WebSocket: {e}")

else:
    app = None
