# Rappi Case-Early Warning System

## Descripción

Solución para detectar posibles condiciones de saturación operacional asociadas a eventos de precipitación y generar alertas accionables para Operations.

La solución está compuesta por tres módulos:

1. **Módulo 1 - Diagnóstico histórico**
2. **Módulo 2 - Motor de alertas**
3. **Módulo 3 - Agente AI + Telegram**

---


# Módulo 1 - Diagnóstico histórico

## Objetivo

Analizar el comportamiento histórico de las zonas para identificar patrones de saturación y evaluar la relación entre precipitación, demanda y oferta de repartidores.

## Ejecución

Abrir:

```text
modulo1_diagnostico/modulo1_diagnostico.ipynb
```

El notebook contiene:

- Exploración y preparación de los datos.
- Cálculo del ratio operacional.
- Identificación de ventanas y zonas de mayor riesgo.
- Análisis de precipitación.
- Análisis estadístico.
- Visualizaciones.
- Hallazgos y conclusiones.

El análisis histórico sirve como base para definir las reglas utilizadas posteriormente por el motor de alertas.

---

# Módulo 2 - Motor de alertas

## Objetivo

Convertir los patrones identificados en el Módulo 1 en un sistema de decisión que utiliza información meteorológica para anticipar posibles condiciones de saturación.

## Flujo

```text
Forecast meteorológico
        ↓
Precipitación por zona
        ↓
Ratio proyectado
        ↓
Nivel de riesgo
        ↓
Earnings recomendado
        ↓
Alerta estructurada
```

## Ejecución

Entrar a la carpeta:

```bash
cd modulo2_motor_alertas
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar el motor:

```bash
python motor_alertas.py
```

El motor genera una alerta estructurada con información como:

- Zona.
- Hora del forecast.
- Precipitación esperada.
- Ratio proyectado.
- Nivel de riesgo.
- Earnings recomendado.
- Ventana de acción.
- Zonas secundarias.

La justificación de los principales thresholds y reglas se encuentra en:

```text
modulo2_motor_alertas/justificacion_motor.md
```

---

# Módulo 3 - Agente AI + Telegram

## Objetivo

Transformar la alerta estructurada generada por el motor en un mensaje accionable utilizando Gemini y enviarlo mediante Telegram.

## Flujo

```text
Módulo 2
    ↓
Alerta estructurada
    ↓
Gemini
    ↓
Mensaje contextualizado
    ↓
Telegram
    ↓
Operations
```

## Requisitos

- Python 3.x
- Gemini API Key
- Telegram Bot Token
- Telegram Chat ID

## Instalación

Entrar a:

```bash
cd modulo3_agente_telegram
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Variables de entorno

Crear un archivo:

```text
.env
```

Utilizar `.env.example` como referencia:

```text
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Las credenciales reales no deben incluirse en el repositorio.

## Prueba del agente

Para generar el mensaje sin enviarlo:

```bash
python agent.py --input sample_alert.json --dry-run
```

Para ejecutar el flujo completo y enviar la alerta:

```bash
python agent.py --input sample_alert.json
```

El mensaje generado incluye la información necesaria para que Operations pueda entender rápidamente la situación y tomar acción.

---

# Tecnologías utilizadas

- Python
- Pandas
- NumPy
- Statsmodels
- Shapely
- Open-Meteo
- Google Gemini
- Telegram Bot API
- Jupyter / Google Colab

---

