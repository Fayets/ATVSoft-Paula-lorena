"""Análisis de transcripciones vía Anthropic Messages API (sin Claude CLI)."""

from __future__ import annotations

import json
import re

import httpx

from src.services.anthropic_service import (
    ANTHROPIC_API_URL,
    ANTHROPIC_VERSION,
    normalize_claude_runtime_error,
)

# Haiku: extracción estructurada a ~1/3 del costo de Sonnet.
ANALYSIS_MODEL = "claude-haiku-4-5-20251001"
MAX_TRANSCRIPT_CHARS = 30_000
MAX_OUTPUT_TOKENS = 2500

ANALYSIS_RESULT_KEYS = (
    "nivel_dolor",
    "capacidad_decision",
    "capacidad_economica",
    "fit_real",
    "objecion_diagnostico",
    "cambio_energia",
    "objecion_no_manejada",
    "razon_real_no_cerrar",
    "compromisos_prometidos",
    "patrones_y_mejoras",
)

ANALYSIS_SYSTEM = """Sos un coach de closers de ventas de alto ticket. Analizás transcripciones de llamadas
(formato "Hablante: texto") para calificar al lead y mejorar al closer.

Reglas:
- Respondé SOLO JSON válido (sin markdown, sin backticks, sin prosa fuera del JSON).
- Español claro y concreto. Usá citas textuales del lead entre comillas cuando aporte.
- No inventes: si no hay evidencia, escribí "No se evidencia en la llamada".
- Si la llamada cerró, en razon_real_no_cerrar poné "Cerró" y la razón real del sí.
- Priorizá señales de los primeros ~10 minutos para capacidad_decision.
"""

ANALYSIS_USER_TEMPLATE = """Analizá la transcripción en DOS bloques (todo en un solo JSON).

## BLOQUE 1 — Calificación del lead
1. nivel_dolor: urgencia real del problema (no solo si lo tiene). Sacá el dolor profundo, no la versión superficial. Indicá nivel (bajo/medio/alto) + evidencia.
2. capacidad_decision: ¿puede decidir solo/a o necesita consultar pareja/socio? Detectalo temprano (ideal: primeros 10 min).
3. capacidad_economica: señales de poder de pago (qué invierte hoy, compras previas, herramientas que usa). ¿El precio será objeción real o de percepción de valor?
4. fit_real: ¿el programa puede ayudarlo de verdad? Si está fuera del ICP, decilo: mejor no cerrar (malos resultados / refunds).
5. objecion_diagnostico: objeción de superficie vs objeción real. El precio casi nunca es el problema; suele ser falta de confianza o de creer que funcionará en su caso. Cavá debajo.

## BLOQUE 2 — Coaching de la llamada (complementario)
6. cambio_energia: ¿en qué momento cambió la energía del lead? (timestamp aproximado o cita + qué pasó).
7. objecion_no_manejada: qué objeción no se manejó bien (o se esquivó).
8. razon_real_no_cerrar: razón real diagnosticada de no cerrar (no la que dio el lead). Si cerró: "Cerró" + por qué sí.

## Extra (trazabilidad y mejora)
9. compromisos_prometidos: qué se prometió en la llamada (entregables, fechas, condiciones, follow-ups).
10. patrones_y_mejoras: patrones, objeciones recurrentes y 2-4 puntos de mejora concretos para el closer.

JSON EXACTO (todas las claves, strings):
{{"nivel_dolor":"...","capacidad_decision":"...","capacidad_economica":"...","fit_real":"...","objecion_diagnostico":"...","cambio_energia":"...","objecion_no_manejada":"...","razon_real_no_cerrar":"...","compromisos_prometidos":"...","patrones_y_mejoras":"..."}}

--- TRANSCRIPCIÓN ---

{transcript}
"""


def _truncate_transcript(text: str, max_chars: int = MAX_TRANSCRIPT_CHARS) -> str:
    raw = (text or "").strip()
    if len(raw) <= max_chars:
        return raw
    # Prioriza inicio (calificación temprana) + cierre (objeciones / ask).
    head = max_chars * 2 // 3
    tail = max_chars - head - 80
    return (
        raw[:head]
        + "\n\n[...tramo intermedio omitido por longitud...]\n\n"
        + raw[-tail:]
    )


def _parse_json_lenient(raw: str) -> dict:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0 or end <= start:
        raise ValueError("Claude no devolvió JSON válido.")
    return json.loads(text[start : end + 1])


def _empty_result() -> dict[str, str]:
    return {k: "" for k in ANALYSIS_RESULT_KEYS}


def run_call_analysis(transcript_text: str, api_key: str) -> dict[str, str]:
    """Una sola llamada a Messages API: calificación + coaching + trazabilidad."""
    key = (api_key or "").strip()
    if not key:
        raise RuntimeError(
            "Configurá tu API key de Claude en Conexiones API antes de analizar llamadas."
        )

    transcript = _truncate_transcript(transcript_text)
    if not transcript:
        raise RuntimeError("La transcripción de Fathom vino vacía; no hay nada para analizar.")

    user_content = ANALYSIS_USER_TEMPLATE.format(transcript=transcript)
    try:
        with httpx.Client(timeout=180.0) as client:
            resp = client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": key,
                    "anthropic-version": ANTHROPIC_VERSION,
                    "content-type": "application/json",
                },
                json={
                    "model": ANALYSIS_MODEL,
                    "max_tokens": MAX_OUTPUT_TOKENS,
                    "system": ANALYSIS_SYSTEM,
                    "messages": [{"role": "user", "content": user_content}],
                },
            )
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Error de red al llamar a Anthropic: {exc}") from exc

    if resp.status_code != 200:
        try:
            data = resp.json()
        except ValueError:
            data = {}
        err = data.get("error") if isinstance(data, dict) else None
        msg = ""
        if isinstance(err, dict):
            msg = str(err.get("message") or err.get("type") or "")
        if not msg:
            msg = (resp.text or "")[:800]
        raise RuntimeError(normalize_claude_runtime_error(msg or f"HTTP {resp.status_code}"))

    try:
        payload = resp.json()
    except ValueError as exc:
        raise RuntimeError("Respuesta inválida de Anthropic.") from exc

    blocks = payload.get("content") if isinstance(payload, dict) else None
    text_parts: list[str] = []
    if isinstance(blocks, list):
        for block in blocks:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(str(block.get("text") or ""))
    raw_text = "\n".join(text_parts).strip()
    if not raw_text:
        raise RuntimeError("Claude devolvió una respuesta vacía.")

    try:
        parsed = _parse_json_lenient(raw_text)
    except (ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Claude no devolvió la ficha JSON: {raw_text[:800]}"
        ) from exc

    out = _empty_result()
    for key_name in ANALYSIS_RESULT_KEYS:
        out[key_name] = str(parsed.get(key_name) or "").strip()
    return out
