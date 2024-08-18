from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, Application

# Token y username
token = '7333639265:AAGRbZlVbDRQ6vURGgcw4IMeRaazd2X29t0'
user_name = 'GothamKnightBot'

# Estados de la conversación
CHOICE, IMAGE, NAME, YEAR = range(4)

# Función de inicio del bot
async def start(update: Update, context: CallbackContext):
     # Verificar si el mensaje es en un chat privado
    if update.message.chat.type == 'private':
        user = update.effective_user  # Obtener el usuario efectivo
        if user:  # Asegurarse de que user no sea None
        # Enviar un mensaje en el grupo pidiendo al usuario que inicie una conversación privada con el bot
          await update.message.reply_text(
            f"¡Hola, {user.first_name}! Bienvenido al bot de Bat-Sabiduria v2.\n\n"
            "Para realizar una solicitud, por favor, usa el comando /peticion. \n"
            "despues, por favor, contesta la información que el bot te solicita. \n"
            "Al final, tu mensaje sera reenviado al grupo para el proceso de tu solicitud. \n\n"
            "Gracias por ayudarnos a facilitar tu busqueda. :)"
        )
    else:
        # Guardar el ID del grupo en el contexto del usuario
        context.user_data['group_chat_id'] = update.message.chat.id
        # Enviar un mensaje en el grupo pidiendo al usuario que inicie una conversación privada con el bot
        await update.message.reply_text(
           "Para realizar una solicitud, por favor, inicia una conversación privada con el bot: @GothamKnightBot, y usa el comando /start. "

        )
        

# Función para iniciar el proceso de petición
async def peticion(update: Update, context: CallbackContext):
    if update.message.chat.type == 'private':
        # Continuar con la petición en privado
        reply_keyboard = [
            ['Series', 'Películas', 'Animes'],
            ['Apps', 'Libros', 'Juegos']
        ]

        await update.message.reply_text(
            "¿Qué tipo de contenido deseas solicitar?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return CHOICE
    else:
        # Enviar un mensaje al usuario para iniciar la conversación en privado
        user_id = update.message.from_user.id
        await context.bot.send_message(
            chat_id=user_id,
            text="Has iniciado una solicitud desde un grupo. Por favor, continúa la solicitud en esta conversación privada."
        )
        # Almacenar el ID del grupo en la base de datos de usuario para poder usarlo después
        context.user_data['group_chat_id'] = update.message.chat.id
        return ConversationHandler.END

# Función para manejar la elección del usuario
async def choice(update: Update, context: CallbackContext):
    context.user_data['choice'] = update.message.text
    await update.message.reply_text("Por favor, sube una imagen de la serie, película, anime, app, libro o juego.")
    return IMAGE

# Función para manejar la imagen subida
async def image(update: Update, context: CallbackContext):
    if update.message.photo:
        context.user_data['image'] = update.message.photo[-1].file_id  # Obtiene la mejor resolución de la foto
        await update.message.reply_text("Por favor, ingresa el nombre de la serie, película, anime, app, libro o juego..")
        return NAME
    else:
        await update.message.reply_text("No se detectó una imagen. Por favor, intenta de nuevo.")
        return IMAGE

# Función para manejar el nombre ingresado
async def name(update: Update, context: CallbackContext):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Por favor, ingresa el año de lanzamiento.")
    return YEAR

async def year(update: Update, context: CallbackContext):
    context.user_data['year'] = update.message.text
    choice = context.user_data['choice']
    name = context.user_data['name']
    year = context.user_data['year']
    image_file_id = context.user_data.get('image', '')

    # Definir hashtags basados en la elección del usuario
    hashtags = {
        "series": "#petición #serie",
        "películas": "#petición #película",
        "animes": "#petición #anime",
        "apps": "#petición #app",
        "libros": "#petición #libro",
        "juegos": "#petición #juego"
    }.get(choice.lower(), "#petición")

    if image_file_id:
        # Enviar el mensaje al usuario en privado
        await update.message.reply_photo(
            photo=image_file_id,
            caption=f"Has solicitado:\nNombre: {name}\nAño: {year}\n{hashtags}"
        )
        
        # Enviar el mensaje al grupo si se almacenó el ID del grupo
        group_chat_id = context.user_data.get('group_chat_id')
        if group_chat_id:
            try:
                # Enviar la imagen al grupo
                await context.bot.send_photo(
                    chat_id=group_chat_id,
                    photo=image_file_id,
                    caption=f"{update.effective_user.first_name} ha solicitado:\nNombre: {name}\nAño: {year}\n{hashtags}"
                )
                # Limpiar el ID del grupo después de enviar el mensaje
                context.user_data.pop('group_chat_id', None)
            except Exception as e:
                print(f"Error al enviar el mensaje al grupo: {e}")
        else:
            await update.message.reply_text("No se encontró el ID del grupo.")
    else:
        await update.message.reply_text("Error: No se pudo enviar la imagen.")

    return ConversationHandler.END

# Función para cancelar la petición
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Petición cancelada.")
    return ConversationHandler.END

# Función de ayuda
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Si necesitas ayuda, contacta al administrador del bot.\n"
        "Correo: admin@example.com"
    )

def main() -> None:
    app = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('peticion', peticion)],
        states={
            CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice)],
            IMAGE: [MessageHandler(filters.PHOTO, image)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, year)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('cancel', cancel))

    app.run_polling()

if __name__ == '__main__':
    main()
    
'''
#comandos

async def start(update: Update, context: ContextTypes):
    await update.message.reply_text("Hola, soy un bot. ¿En que puedo ayudarte?")

async def help(update: Update, context: ContextTypes):
    await update.message.reply_text('Ayuda')

async def custom(update: Update, context: ContextTypes):
    await update.message.reply_text(update.message.text)


def handle_response(text: str, context: ContextTypes, update: Update):

    procecesed_text = text.lower()
    print(procecesed_text)
    if 'hola' in procecesed_text:
        return 'Hola, ¿Como estas?'
    else:
        return 'No entiendo'



async def handle_message(update: Update, context: ContextTypes):

    message_type = update.message.chat.type # private, group, supergroup, channel
    text = update.message.text

    if message_type == 'group':
        if text.startswith(user_name):
            new_text = text.replace(user_name, '')
            response = handle_response(new_text,context,update)
        else:
            return
    else:
        response = handle_response(text,context,update)

    await update.message.reply_text(response) 

async def error(update: Update, context: ContextTypes):
    print(context.error)
    await update.message.reply_text('Ha ocurrido un error')

#main

if __name__ == '__main__':

    print('Iniciando bot...')
    app = Application.builder().token(token).build() #creamos la app

    #creamos los comandos
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('echo', custom))

    #crear las respuestas
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #crear los errores
    app.add_error_handler(error)

    #iniciar el bot
    print('Bot iniciado')
    app.run_polling(poll_interval=1, timeout=10)
'''
