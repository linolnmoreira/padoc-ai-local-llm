import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class DiagnosisResult:
    classification: str
    possible_causes: List[str]
    confidence: int  # percent
    recommended_data: List[str]


class SymptomClassifier:
    """Rule-based automotive symptom classifier.

    The classifier uses a static mapping of engine-noise categories and a simple
    heuristic to produce a structured diagnosis. It is deliberately lightweight
    so it can be executed locally without any ML dependencies.
    """

    # Static dictionary of noise categories (the ones requested by the user)
    CATEGORY_MAP: Dict[str, List[str]] = {
        "RUÍDOS_INTERNOS_DO_MOTOR": [
            "Batida de biela",
            "Bronzina",
            "Pino de pistão",
            "Tucho hidráulico",
            "Comando de válvulas",
            "Corrente de comando",
            "Tensor da corrente",
            "Correia",
            "Polia",
            "Virabrequim",
            "Pistão",
            "Pré-detonação/detonação",
        ],
        "CARACTERÍSTICAS_DO_RUÍDO": [],
    }

    # Simple heuristic weights for confidence (placeholder values)
    FEATURE_WEIGHTS: Dict[str, int] = {
        "frequency": 10,
        "intensity": 10,
        "rpm": 15,
        "load": 10,
        "temperature": 10,
        "engine_state": 10,
        "operation_mode": 10,
        "location": 5,
        "obd": 10,
    }

    def _aggregate_score(self, audio_features: Dict[str, Any], obd_data: Optional[Dict[str, Any]]) -> int:
        """Aggregate a simple confidence score based on presence of key features.

        The score is capped at 100 (percent). Each feature contributes a fixed
        weight defined in ``FEATURE_WEIGHTS`` when it is present and truthy.
        """
        score = 0
        for key, weight in self.FEATURE_WEIGHTS.items():
            if key in audio_features and audio_features[key]:
                score += weight
            elif key == "obd" and obd_data:
                score += weight
        return min(score, 100)

    def classify(
        self,
        audio_features: Dict[str, Any],
        obd_data: Optional[Dict[str, Any]] = None,
        telemetry: Optional[Dict[str, Any]] = None,
        media: Optional[Dict[str, Any]] = None,
    ) -> DiagnosisResult:
        """Classify a symptom based on supplied data.

        For the prototype we always return the high-level classification
        "RUÍDO MECÂNICO DO MOTOR" and a list of possible causes derived from the
        static ``CATEGORY_MAP``. Confidence is calculated with the simple
        heuristic ``_aggregate_score``.
        """
        classification = "RUÍDO MECÂNICO DO MOTOR"
        # Flatten possible causes from the internal map (excluding empty groups)
        possible_causes = []
        for group in self.CATEGORY_MAP.values():
            possible_causes.extend(group)

        confidence = self._aggregate_score(audio_features, obd_data)

        # Recommended data – based on the original proposal
        recommended = [
            "RPM",
            "temperatura",
            "áudio do ruído",
            "DTCs",
            "pressão de óleo",
        ]

        return DiagnosisResult(
            classification=classification,
            possible_causes=possible_causes,
            confidence=confidence,
            recommended_data=recommended,
        )


def classify_symptom(
    audio_features: Dict[str, Any],
    obd_data: Optional[Dict[str, Any]] = None,
    telemetry: Optional[Dict[str, Any]] = None,
    media: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Convenient functional wrapper used by the orchestrator.

    Returns a JSON-serialisable dictionary that matches the output format
    requested by the user (structured JSON).
    """
    classifier = SymptomClassifier()
    result = classifier.classify(audio_features, obd_data, telemetry, media)
    return {
        "classification": result.classification,
        "possible_causes": result.possible_causes,
        "confidence": result.confidence,
        "recommended_data": result.recommended_data,
    }
