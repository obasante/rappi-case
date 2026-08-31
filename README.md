\# Rappi Case — Early Warning System



\## Descripción



Solución para detectar posibles condiciones de saturación operacional asociadas a eventos de precipitación y generar alertas accionables para Operations.



La solución está compuesta por tres módulos:



1\. \*\*Módulo 1 — Diagnóstico histórico\*\*

2\. \*\*Módulo 2 — Motor de alertas\*\*

3\. \*\*Módulo 3 — Agente AI + Telegram\*\*



\---



\# Módulo 1 — Diagnóstico histórico



\### Objetivo



Analizar el comportamiento histórico de las zonas para identificar patrones de saturación y la relación entre precipitación, demanda y oferta de repartidores.



\### Ejecución



Abrir el notebook ubicado en:



```text

modulo1\_diagnostico/

```



El notebook debe ejecutarse de principio a fin.



El análisis incluye:



\- Exploración de los datos.

\- Cálculo del ratio operacional.

\- Identificación de horas y zonas de mayor riesgo.

\- Análisis de precipitación.

\- Análisis estadístico.

\- Visualizaciones.

\- Principales hallazgos y conclusiones.



La salida del Módulo 1 sirve como base para definir las reglas utilizadas posteriormente por el motor de alertas.



\---



\# Módulo 2 — Motor de alertas



\### Objetivo



Convertir los patrones históricos identificados en el Módulo 1 en un sistema de decisión que utilice un forecast meteorológico para anticipar posibles condiciones de saturación.



\### Flujo



```text

Forecast meteorológico

&#x20;       ↓

Precipitación por zona

&#x20;       ↓

Ratio proyectado

&#x20;       ↓

Nivel de riesgo

&#x20;       ↓

Earnings recomendado

&#x20;       ↓

Alerta estructurada

```



\### Ejecución



Entrar a la carpeta:



```bash

cd modulo2\_motor\_alertas

```



Instalar dependencias:



```bash

pip install -r requirements.txt

```



Ejecutar el motor utilizando el dataset:



```bash

python motor\_alertas.py --input ../rappi\_delivery\_case\_data.xlsx

```



Para ejecutar la demostración:



```bash

python motor\_alertas.py --input ../rappi\_delivery\_case\_data.xlsx --demo

```



El motor utiliza información meteorológica para generar una alerta estructurada que posteriormente puede ser consumida por el Agente AI.



\---



\# Módulo 3 — Agente AI + Telegram



\### Objetivo



Transformar la alerta estructurada del Módulo 2 en un mensaje breve y accionable utilizando Gemini y enviarlo automáticamente mediante Telegram.



\### Flujo



```text

Módulo 2

&#x20;  ↓

JSON de alerta

&#x20;  ↓

Gemini

&#x20;  ↓

Mensaje contextualizado

&#x20;  ↓

Telegram

&#x20;  ↓

Operations Manager

```



\### Requisitos



\- Python 3.x

\- Gemini API Key

\- Telegram Bot Token

\- Telegram Chat ID



\### Instalación



Entrar a:



```bash

cd modulo3\_agente\_telegram

```



Instalar dependencias:



```bash

pip install -r requirements.txt

```



\### Configuración



Crear un archivo:



```text

.env

```



Utilizar `.env.example` como referencia:



```text

GEMINI\_API\_KEY=your\_gemini\_api\_key

TELEGRAM\_BOT\_TOKEN=your\_telegram\_bot\_token

TELEGRAM\_CHAT\_ID=your\_telegram\_chat\_id

```





\### Configuración del bot de Telegram



1\. Crear un bot utilizando \*\*BotFather\*\* en Telegram.

2\. Obtener el `TELEGRAM\_BOT\_TOKEN`.

3\. Iniciar una conversación con el bot.

4\. Obtener el `TELEGRAM\_CHAT\_ID`.

5\. Agregar ambos valores al archivo `.env`.



\### Prueba del agente



Para generar el mensaje sin enviarlo:



```bash

python agent.py --input sample\_alert.json --dry-run

```



Para ejecutar el flujo completo y enviar la alerta a Telegram:



```bash

python agent.py --input sample\_alert.json

```



El sistema genera un mensaje que incluye:



\- Zona afectada.

\- Nivel de riesgo.

\- Condición esperada.

\- Ratio proyectado.

\- Earnings actual.

\- Earnings recomendado.

\- Ventana de acción.

\- Zonas secundarias cuando corresponda.



\---



\# Tecnologías



\- Python

\- Pandas

\- NumPy

\- Statsmodels

\- Shapely

\- Open-Meteo

\- Google Gemini

\- Telegram Bot API

\- Google Colab



\---



