# Justificación de reglas — Módulo 2

## API y forecast

Se utiliza Open-Meteo porque es pública, gratuita para el volumen del caso, no requiere API key y entrega precipitación horaria en mm/hr.

## Mapeo de zonas

El dataset proporciona `ZONE_POLYGONS` en WKT. El motor construye un punto representativo dentro de cada polígono para consultar el clima y valida la coordenada devuelta por la API mediante **point-in-polygon**. Si una geometría está truncada o no puede procesarse, utiliza el centro disponible en `ZONE_INFO` como fallback explícito.

## Umbral de precipitación

Se utiliza **1 mm/hr** como gatillo base combinado con el ratio proyectado. En el Módulo 1, los niveles superiores a 1 mm/hr muestran mayor ratio y mayor tasa de saturación, especialmente en la ventana crítica 12–14. El umbral no implica causalidad por sí mismo.

## Ratio proyectado

Se utiliza el modelo histórico `RATIO ~ PRECIPITATION_MM + C(HOUR) + C(ZONE)`. Esto permite estimar el riesgo bajo las condiciones climáticas previstas antes de decidir la intervención económica.

## Anticipación

Se utiliza una ventana de **2 horas** como compromiso entre precisión y tiempo de reacción. En producción debería validarse mediante backtesting de forecast vs. observado.

## Earnings recomendado

El objetivo operacional es `RATIO = 1.8`, definido en el diagnóstico. El valor recomendado se obtiene despejando el coeficiente histórico de `EARNINGS` en `RATIO ~ EARNINGS + PRECIPITATION_MM + HOUR + ZONE`. El motor nunca recomienda pagar menos que el earnings actual.

## Duplicados

Cada alerta recibe un `EVENT_ID` por zona y bloque de 2 horas, evitando repetir la misma alerta durante el mismo evento.

## Limitaciones

El histórico es observacional y cubre 30 días en Monterrey. Las relaciones no deben interpretarse automáticamente como causales. Antes de producción se recomienda backtesting, calibración por zona y monitoreo de falsos positivos.
