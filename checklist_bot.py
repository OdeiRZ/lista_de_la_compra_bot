import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# TOKEN desde variable de entorno
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    print("Error: TOKEN no definido")
    exit(1)

STATE_FILE = "state.json"

# Lista inicial de ejemplo
default_checklist = {
    "🥛 Lácteos": ["Leche", "Yogur"],
    "🥕 Verduras": ["Tomates", "Pimientos"],
    "Otros": ["Pan", "Huevos"]
}

# Cargar estado o crear uno nuevo
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

# /add Sección | Item
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "|" not in text:
        await update.message.reply_text("Formato: /add Sección | Item")
        return
    section, item = [x.strip() for x in text.split("|", 1)]
    if section not in checklist:
        checklist[section] = []
    checklist[section].append(item)
    state[item] = False
    save_state()
    await update.message.reply_text(f"Item '{item}' añadido a '{section}'")

# /remove Item
async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = update.message.text.replace("/remove", "").strip()
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

# /list
async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🛒 Lista de la compra:\n"
    for section, items in checklist.items():
        msg += f"\n--- {section} ---\n"
        for item in items:
            prefix = "✅" if state[item] else "⬜"
            msg += f"{prefix} {item}\n"
    await update.message.reply_text(msg)

# MAIN
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(toggle))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("remove", remove_item))
    app.add_handler(CommandHandler("list", show_list))
    print("Bot corriendo...")
    app.run_polling()
