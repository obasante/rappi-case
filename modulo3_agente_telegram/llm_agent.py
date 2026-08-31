import json
import os

from google import genai


SYSTEM_PROMPT = """
Eres un agente de alertas operacionales para una operación de última milla.

Tu función es transformar resultados analíticos ya calculados
en una alerta corta y accionable para un Operations Manager.

REGLAS IMPORTANTES:

1. NO inventes números.
2. NO recalcules métricas.
3. NO cambies el earnings recomendado.
4. NO cambies el ratio proyectado.
5. NO afirmes causalidad.
6. Utiliza únicamente los datos entregados por el motor analítico.
7. El mensaje debe poder entenderse en aproximadamente 10 segundos.
8. Escribe en español.
9. Máximo aproximadamente 700 caracteres.

El mensaje debe incluir:

- Zona
- Nivel de riesgo
- Lluvia esperada
- Ratio proyectado
- Earnings actual
- Earnings recomendado
- Ventana de acción
- Zonas secundarias, si existen

El LLM es solamente una capa de comunicación.
Las decisiones analíticas vienen del motor de datos.
"""


def build_alert_message(alert: dict) -> str:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY en el archivo .env"
        )

    client = genai.Client(api_key=api_key)

    payload = json.dumps(
        alert,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
{SYSTEM_PROMPT}

Estos son los resultados validados por el motor analítico:

{payload}

Genera únicamente el mensaje final que será enviado
al Operations Manager por WhatsApp.
"""

    response = client.models.generate_content(
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        ),
        contents=prompt
    )

    return response.text.strip()
