import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# Token desde variable de entorno
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    print("Error: TOKEN no definido")
    exit(1)

STATE_FILE = "state.json"

# Lista inicial de ejemplo
default_checklist = {
    "Mercadona": ["Leche", "Yogur"],
    "Carrefour": ["Tomates", "Pimientos"],
    "Lidl": ["Pan", "Huevos"]
}

# Cargar estado o crear uno nuevo
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
        checklist = data["checklist"]
        state = data["state"]
else:
    checklist = default_checklist
    state = {item: False
