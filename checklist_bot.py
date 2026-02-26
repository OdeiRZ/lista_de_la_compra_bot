import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# TOKEN desde variable de entorno
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    print("Error: TOKEN no definido como variable de entorno")
    exit(1)

STATE_FILE = "state.json"

# Lista inicial
default_checklist = {
    "🥛 Lácteos": ["Leche", "Yogur"],
    "🥕 Verduras": ["Tomates", "Pimientos"],
    "Otros": ["Pan", "Huevos"]
}

# Cargar lista y estado
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
        checklist = data["checklist"]
        state = data["state"]
else:
    checklist = default_checklist
    state = {item: False for section in checklist.values() for item in section}

# Construir teclado inline
def build_keyboard():
    buttons = []
    for section, items in checklist.items():
        buttons.append([InlineKeyboardButton(f"--- {section} ---", callback_data="section")])
        for item in items:
            prefix = "✅" if state[item] else "⬜"
            buttons.append([InlineKeyboardButton(f"{prefix} {item}", callback_data=item)])
    return InlineKeyboardMarkup(buttons)

# Guardar estado en JSON
def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump({"checklist": checklist, "state": state}, f)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Lista de la compra",
        reply_markup=build_
