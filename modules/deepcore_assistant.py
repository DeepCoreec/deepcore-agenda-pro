"""
deepcore_assistant.py — Alisson para DeepCore Agenda Pro.
Contexto: citas, turnos, clientes, servicios, profesionales, ocupación.
"""
from __future__ import annotations

import os as _os
import sys as _sys
from datetime import datetime as _dt

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DEEPCORE_ROOT = _os.path.dirname(_HERE)
for _path in (_HERE, _DEEPCORE_ROOT):
    if _path not in _sys.path:
        _sys.path.insert(0, _path)

try:
    from alisson import Alisson as _Alisson
    _ALISSON_OK = True
except ImportError:
    _ALISSON_OK = False


class AlissonAgenda:
    """Asistente IA de DeepCore Agenda Pro — motor híbrido Claude + Ollama + local."""

    _ACCIONES = (
        "ACCIONES QUE PUEDES EJECUTAR:\n"
        "- Consultar citas del día y la semana\n"
        "- Analizar ocupación por profesional y horario\n"
        "- Identificar clientes recurrentes y nuevos\n"
        "- Sugerir horarios para reducir inasistencias\n"
        "- Analizar servicios más solicitados\n"
        "- Calcular ingresos proyectados\n\n"
        "EJEMPLOS:\n"
        "  '¿Cuántas citas tengo hoy?'\n"
        "  '¿Cuál es mi hora pico de atención?'\n"
        "  '¿Qué servicio genera más ingresos?'\n"
        "  'Dame tips para reducir las inasistencias'"
    )

    _AGENDA_INTEL = (
        "\n\nCONOCIMIENTO DE GESTIÓN DE CITAS:\n"
        "Buenas prácticas para reducir inasistencias:\n"
        "  - Recordatorio por WhatsApp 24h antes\n"
        "  - Confirmación el mismo día por la mañana\n"
        "  - Política de cancelación con al menos 2h de anticipación\n"
        "  - Lista de espera para cubrir cancelaciones de última hora\n"
        "Análisis de ocupación:\n"
        "  - Ocupación ideal: 75-85% (deja margen para emergencias)\n"
        "  - Horarios pico en Ecuador: 10:00-12:00 y 15:00-18:00\n"
        "  - Tasa de no-show promedio en salones: 15-20%\n"
        "  - Con recordatorios automáticos baja al 5-8%\n"
        "Estrategias de fidelización:\n"
        "  - Clientes que visitan 3+ veces tienen 70% menos tasa de abandono\n"
        "  - Programa de puntos o descuento por reserva anticipada\n"
        "  - Seguimiento post-servicio mejora recomendaciones boca a boca\n"
    )

    def __init__(self, api_key: str = '', empresa: str = 'Mi Negocio'):
        self.empresa = empresa
        self._activa = False
        if _ALISSON_OK:
            try:
                self._ia = _Alisson(
                    api_key=api_key,
                    programa="Agenda Pro",
                    contexto=self._build_contexto(),
                )
                self._activa = True
            except Exception:
                self._ia = None
        else:
            self._ia = None

    def set_api_key(self, api_key: str):
        if self._ia:
            self._ia.set_api_key(api_key)

    @property
    def activa(self) -> bool:
        return bool(self._ia and self._activa)

    @property
    def modo(self) -> str:
        if not self._ia:
            return 'no_disponible'
        return getattr(self._ia, 'modo', 'local')

    def _get_stats(self) -> dict:
        try:
            import database as _db
            return _db.kpis_hoy()
        except Exception:
            return {}

    def _build_contexto(self) -> str:
        stats = self._get_stats()
        ahora = _dt.now().strftime('%Y-%m-%d %H:%M')
        return (
            f"Eres Alisson, asistente IA de {self.empresa} usando DeepCore Agenda Pro.\n"
            f"Fecha y hora actual: {ahora}\n\n"
            f"ESTADO ACTUAL DE LA AGENDA:\n"
            f"  Citas hoy:        {stats.get('citas_hoy', 0)}\n"
            f"  Completadas hoy:  {stats.get('completadas', 0)}\n"
            f"  Pendientes hoy:   {stats.get('pendientes', 0)}\n"
            f"  Ingreso hoy:      ${stats.get('ingreso_hoy', 0):.2f}\n"
            f"  Total clientes:   {stats.get('total_clientes', 0)}\n"
            f"  Ingreso del mes:  ${stats.get('ingreso_mes', 0):.2f}\n\n"
            + self._ACCIONES + self._AGENDA_INTEL
        )

    def chat(self, mensaje: str) -> str:
        if not self._ia:
            return (
                "Alisson no está disponible.\n"
                "Configura tu API key de Anthropic en Configuración para activar el asistente IA."
            )
        try:
            self._ia._system = (
                f"Eres Alisson, la asistente de inteligencia artificial de DeepCore Agenda Pro. "
                f"Eres amable, profesional y concisa. Respondes siempre en español. "
                f"{self._build_contexto()}"
            )
            resp, _ = self._ia.responder(mensaje)
            return resp
        except Exception as e:
            return f"Error al procesar tu consulta: {e}"

    def respuesta_rapida(self, tipo: str) -> str:
        prompts = {
            'citas_hoy':      "¿Cuántas citas tengo hoy y cuáles son las más próximas?",
            'ocupacion':      "Analiza mi ocupación semanal y dime en qué horarios tengo más disponibilidad.",
            'inasistencias':  "Dame 3 estrategias prácticas para reducir las inasistencias en mi negocio.",
            'analisis':       "Analiza el rendimiento de mi agenda este mes y dame recomendaciones.",
        }
        return self.chat(prompts.get(tipo, "¿En qué puedo ayudarte hoy?"))
