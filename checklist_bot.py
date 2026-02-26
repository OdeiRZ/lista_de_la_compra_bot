import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import os

# Token desde variable de entorno (para Railway)
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    print("Error: pon tu TOKEN como variable de entorno 'TOKEN'")
    exit(1)

# Archivo donde se guardara la lista y estado
STATE_FILE = "state.json"

# Lista inicial (si no existe state.json)
default_checklist = {
    "MERCADONA": [
		"Arena aglomerante", "Papel higiénico", "Toallitas culo", "Bolsas de basura", "Lavavajillas", "Pato WC", 
		"Nidos de pasta (al huevo)", "Hélices de pasta", 
		"Lágrima artificial", "Bastoncillos", "Enjuague bucal", "Pasta de dientes", 
		"Filetes de pavo", "Jamón extrafino", "Jamón ibérico", "Bacon", "Chorizo de pavo", "Pavo", "Queso mozarella", "Queso mozarella light", "Queso tierno", "Queso cuña",
		"Plátanos", "Manzanas", "Patatas", "Pimiento verde", "Zanahorias", "Guacamole", 
		"Chocolate Nestlé", "Helados de cono grandes", "Helados de cono chicos", 
		"Patatas gajo", "Patatas corte grueso", "Batatas congeladas", "Ñoquis congelados", "Pimiento congelado", "Cebolla congelada", "Ajo congelado",
		"Agua", "Monster", "Coca-cola zero", "Mosto tinto",
		"Salsa barbacoa", "Salsa de soja", "Tomate", "Atún", "Aceitunas",
		"Pollitos crunchy", "Bases de pizza", "Hielo",
		"Yogur natural", "Yogur edulcorado", "Batido +proteinas", "Leche proteica",
		"Pan de sándwich", "Palitos de frutos secos", "Bollitos de leche", 
		"Napolitana", "Pan", "Tila/Infusión", "Sopas",
		"Pipas aquasal", "Cacahuetes", "Cacahuetes desgrasado", "Pistachos", "Nueces",
		"Lasaña", "Tiras de pollo", "Tortilla de patatas", "Piña"
	],
	"ALDI": ["Albóndigas de Soja", "Cereales 0%", "Queso Havarti", "Casera de Limón", "Gyozas de pollo"],
    "CARREFOUR": ["Patatas/Picoteo", "Monsters", "Mosto blanco"]
}

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        checklist = data.get("checklist", default_checklist)
        state = data.get("state", {item: False for sec in checklist.values() for item in sec})
else:
    checklist = default_checklist
    state = {item: False for sec in checklist.values() for item in sec}

def build_keyboard():
    buttons = []
    for section, items in checklist.items():
        buttons.append([InlineKeyboardButton(f"--- {section} ---", callback_data="section")])
        for item in items:
            prefix = "✅" if state.get(item, False) else "⬜"
            buttons.append([InlineKeyboardButton(f"{prefix} {item}", callback_data=item)])
    return InlineKeyboardMarkup(buttons)

def save_state():
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"checklist": checklist, "state": state}, f, ensure_ascii=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛒 Lista de la compra", reply_markup=build_keyboard())

async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item = query.data
    if item != "section":
        state[item] = not state.get(item, False)
        save_state()
        await query.edit_message_reply_markup(reply_markup=build_keyboard())

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

async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🛒 Lista de la compra:\n"
    for section, items in checklist.items():
        msg += f"\n--- {section} ---\n"
        for item in items:
            prefix = "✅" if state.get(item, False) else "⬜"
            msg += f"{prefix} {item}\n"
    await update.message.reply_text(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(toggle))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("remove", remove_item))
    app.add_handler(CommandHandler("list", show_list))
    print("Bot corriendo...")
    app.run_polling()
