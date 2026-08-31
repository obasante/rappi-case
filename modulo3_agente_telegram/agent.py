import argparse
import os
from dotenv import load_dotenv

from alert_engine_adapter import load_alert
from llm_agent import build_alert_message
from telegram import send_telegram_message


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="sample_alert.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Cargar variables del archivo .env
    load_dotenv()

    # 1. Cargar alerta generada por el Módulo 2
    alert = load_alert(args.input)

    # 2. Generar mensaje utilizando el AI Agent
    message = build_alert_message(alert)

    print("\n===== MENSAJE GENERADO =====\n")
    print(message)

    # 3. Si usamos dry-run, solamente mostramos el mensaje
    if args.dry_run:
        print("\n[DRY RUN] No se envió ningún mensaje.")
        return

    # 4. Validar credenciales de Telegram
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")

    if not os.getenv("TELEGRAM_CHAT_ID"):
        raise RuntimeError("Missing TELEGRAM_CHAT_ID")

    # 5. Enviar mensaje a Telegram
    result = send_telegram_message(message)

    print("\n===== TELEGRAM API RESPONSE =====\n")
    print(result)


if __name__ == "__main__":
    main()