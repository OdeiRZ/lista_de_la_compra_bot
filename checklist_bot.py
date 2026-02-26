import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import os

# Token desde variable de entorno (para Railway)
TOKEN = os.environ.get("8268360976:AAHXbvHk16UTcnsZs0XoeQlklrmX1j18674")
if not TOKEN:
    print("Error: pon tu TOKEN como variable de entorno 'TOKEN'")
    exit(1)

# Archivo donde se guardarÃ¡ la lista y estado
STATE_FILE = "state.json"

# Lista inicial (si no existe state.json)
default_checklist = {
    "Lacteos": ["Leche", "Yogur"],
    "Verduras": ["Tomates", "Pimientos"],
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

# Construye teclado inline
def build_keyboard():
    buttons = []
    for section, items in checklist.items():
        buttons.append([InlineKeyboardButton(f"--- {section} ---", callback_data="section")])
        for item in items:
            prefix = "âœ…" if state[item] else "â¬œ"
            buttons.append([InlineKeyboardButton(f"{prefix} {item}", callback_data=item)])
    return InlineKeyboardMarkup(buttons)

# Guardar en JSON
def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump({"checklist": checklist, "state": state}, f)

# /start crea o actualiza el mensaje
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ðŸ›’ Lista de la compra",
        reply_markup=build_keyboard()
    )

# Toggle checkbox
async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item = query.data
    if item != "section":
        state[item] = not state[item]
        save_state()
        await query.edit_message_reply_markup(reply_markup=build_keyboard())

# AÃ±adir nuevo item a una secciÃ³n
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        # Formato: /add SecciÃ³n | Item
        if "|" not in text:
            await update.message.reply_text("Formato: /add SecciÃ³n | Item")
            return
        section, item = [x.strip() for x in text.split("|", 1)]
        if section not in checklist:
            checklist[section] = []
        checklist[section].append(item)
        state[item] = False
        save_state()
        await update.message.reply_text(f"Item '{item}' aÃ±adido a '{section}'")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Quitar item
async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        # Formato: /remove Item
        item = text.replace("/remove", "").strip()
        found = False
        for section, items in checklist.items():
            if item in items:
                items.remove(item)
                found = True
                break
        if found:
            state.pop(item, None)
            save_state()
            await update.message.reply_text(f"Item '{item}' eliminado")
        else:
            await update.message.reply_text(f"Item '{item}' no encontrado")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Mensaje normal para listar la lista
async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "ðŸ›’ Lista de la compra:\n"
    for section, items in checklist.items():
        msg += f"\n--- {section} ---\n"
        for item in items:
            prefix = "âœ…" if state[item] else "â¬œ"
            msg += f"{prefix} {item}\n"
    await update.message.reply_text(msg)

# Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(toggle))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("remove", remove_item))
    app.add_handler(CommandHandler("list", show_list))
    print("Bot corriendo...")
    app.run_polling()
