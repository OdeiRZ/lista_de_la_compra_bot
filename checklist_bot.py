import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token desde variable de entorno (para Railway)
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    print("Error: pon tu TOKEN como variable de entorno 'TOKEN'")
    exit(1)


# Lista de la compra
SHOPPING_LIST = ["Leche", "Huevos", "Pan", "Mantequilla", "Fruta"]

# Estado inicial de la lista
state = {item: False for item in SHOPPING_LIST}


def start(update: Update, context: CallbackContext):
    """Enviar mensaje inicial con botones de la lista de la compra."""
    keyboard = [
        [InlineKeyboardButton(f"{'✅' if state[item] else '⬜'} {item}", callback_data=item)]
        for item in SHOPPING_LIST
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Lista de la compra:", reply_markup=reply_markup)


def button(update: Update, context: CallbackContext):
    """Actualizar estado al pulsar un botón."""
    query = update.callback_query
    query.answer()

    item = query.data
    state[item] = not state[item]  # Alternar estado

    # Reconstruir teclado
    keyboard = [
        [InlineKeyboardButton(f"{'✅' if state[i] else '⬜'} {i}", callback_data=i)]
        for i in SHOPPING_LIST
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Lista de la compra:", reply_markup=reply_markup)


def reset(update: Update, context: CallbackContext):
    """Resetear lista a todos sin marcar."""
    for item in state:
        state[item] = False
    keyboard = [
        [InlineKeyboardButton(f"⬜ {i}", callback_data=i)] for i in SHOPPING_LIST
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Lista reseteada:", reply_markup=reply_markup)


def main():
    """Inicializar bot y polling."""
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
