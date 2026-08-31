from dotenv import load_dotenv
from telegram import send_telegram_message

load_dotenv()

message = """🚨 PRUEBA DEL AI AGENT

📍 Zona: Santiago
⚠️ Riesgo: CRÍTICO
🌧️ Lluvia esperada: 7.2 mm/hr
📊 Ratio proyectado: 2.01
💰 Earnings actual: 55 MXN
💡 Earnings recomendado: 78 MXN
⏱️ Ventana de acción: 30 minutos
"""

result = send_telegram_message(message)

print("================================")
print("MENSAJE ENVIADO CORRECTAMENTE")
print("================================")
print(result)