import os
import dotenv
import telebot
from telebot import types
import re
from datetime import datetime
from src.utils import validate_email

from src.gmail_extractor import get_last_netflix_mail

keywords = {
    "restablecimiento": ['{subject: "restablece" subject: "contraseña"}'],
    "actualizar_hogar": ['{subject: "actualizar tu hogar"}'],
    "codigo_temporal": ['{subject: "acceso temporal"}'],
    "activar_tv": ['{subject: "aprueba" subject: "sesion"}'],
}

# Cargar el archivo .env
dotenv.load_dotenv()

# Obtener la API_KEY desde el archivo .env
API_KEY = os.getenv("API_KEY")

# Verificar si la API_KEY se cargó correctamente
if not API_KEY:
    raise ValueError("API_KEY no se encuentra en el archivo .env")

bot = telebot.TeleBot(API_KEY)

# Diccionario en memoria para simular el almacenamiento de acciones y correos de usuarios
user_data = {}


# Funciones ficticias para obtener datos (reemplaza con la lógica real)
def get_user_id_by_chat_id(chat_id):
    return chat_id  # Suponiendo que el user_id es igual al chat_id


def update_action(user_id, action):
    if user_id not in user_data:
        user_data[user_id] = {"action": None, "emails": []}
    user_data[user_id]["action"] = action


def get_emails_by_user_id(user_id):
    return user_data.get(user_id, {}).get("emails", [])


def store_email(user_id, email):
    if user_id not in user_data:
        user_data[user_id] = {"action": None, "emails": []}
    if email not in user_data[user_id]["emails"]:
        user_data[user_id]["emails"].append(email)


# Comando de inicio
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hola, ¡Un gusto conocerte! ¿En qué puedo ayudarte?")
    bot.send_message(
        message.chat.id,
        "El bot ya funciona. Usa /acciones para ver las opciones disponibles.",
    )


# Comando para mostrar opciones
@bot.message_handler(commands=["acciones"])
def mostrar_acciones(message):
    markup = types.InlineKeyboardMarkup()
    acciones = [
        ("Restablecimiento de Contraseña", "restablecimiento"),
        ("Actualizar Hogar", "actualizar_hogar"),
        ("Código Temporal", "codigo_temporal"),
        ("Activar TV", "activar_tv"),
    ]
    for texto, callback_data in acciones:
        boton = types.InlineKeyboardButton(texto, callback_data=callback_data)
        markup.add(boton)
    bot.send_message(
        message.chat.id,
        "Selecciona la acción que deseas realizar para tu cuenta:",
        reply_markup=markup,
    )


# Función para manejar la acción seleccionada
@bot.callback_query_handler(
    func=lambda call: call.data
    in ["restablecimiento", "actualizar_hogar", "codigo_temporal", "activar_tv"]
)
def manejar_accion_seleccionada(call):
    accion = call.data
    user_id = get_user_id_by_chat_id(call.message.chat.id)
    update_action(user_id, accion)

    bot.send_message(
        call.message.chat.id,
        f"Has elegido la opción: {accion.replace('_', ' ').title()}.",
    )
    ask_for_email(call.message)
    bot.answer_callback_query(call.id)


# Función que muestra los correos electrónicos al usuario
def ask_for_email(message):
    user_id = get_user_id_by_chat_id(message.chat.id)
    emails = get_emails_by_user_id(user_id)
    markup = types.InlineKeyboardMarkup()

    if emails:
        for email in emails:
            markup.add(
                types.InlineKeyboardButton(email, callback_data=f"email:{email}")
            )

    markup.add(types.InlineKeyboardButton("Agregar Nuevo", callback_data="new_email"))
    bot.send_message(
        message.chat.id,
        "¿Con cuál correo electrónico deseas realizar esta operación?",
        reply_markup=markup,
    )


# Manejar selección de correos
@bot.callback_query_handler(func=lambda call: call.data.startswith("email:"))
def manejar_seleccion_email(call):
    email = call.data.split(":", 1)[1]
    user_id = get_user_id_by_chat_id(call.message.chat.id)
    action = user_data.get(user_id, {}).get("action")

    bot.send_message(call.message.chat.id, f"Se utilizará el correo {email}.")
    mostrar_instrucciones(call.message, action, email)
    bot.answer_callback_query(call.id)


# Manejar el correo electrónico del usuario
@bot.callback_query_handler(func=lambda call: call.data == "new_email")
def solicitar_email(call):
    bot.send_message(call.message.chat.id, "Por favor ingresa tu correo.")
    bot.register_next_step_handler(call.message, agregar_correo)


def agregar_correo(message):
    user_id = get_user_id_by_chat_id(message.chat.id)
    email = message.text.strip()

    if not validate_email(email):
        bot.send_message(
            message.chat.id,
            "El correo ingresado no es válido. Por favor, intenta nuevamente.",
        )
        return

    store_email(user_id, email)
    bot.send_message(message.chat.id, f"El correo {email} se ha agregado exitosamente.")

    action = user_data.get(user_id, {}).get("action")
    mostrar_instrucciones(message, action, email)


# Mostrar instrucciones según la acción seleccionada
def mostrar_instrucciones(message, action, email):
    respuestas = {
        "restablecimiento": "Para restablecer tu contraseña, ve a: https://www.netflix.com/LoginHelp.\nSelecciona 'Enviar un email'.",
        "actualizar_hogar": "Para actualizar tu hogar, selecciona 'Actualizar Hogar' en la pantalla.\nSelecciona 'Enviar un email'.",
        "codigo_temporal": "Para obtener un código temporal, selecciona 'Estoy de viaje' en tu cuenta.\nSelecciona 'Enviar un email'.",
        "activar_tv": "Para activar TV, selecciona 'Enviar enlace de inicio de sesión' en tu cuenta.\nSelecciona 'Enviar un email'.",
    }
    if action in respuestas:
        bot.send_message(message.chat.id, respuestas[action])

        # Crear el teclado con las opciones "Si" y "No"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "Si", callback_data=f"enviado_si|{action}|{email}"
            ),  # Usando "Si" sin tilde
            types.InlineKeyboardButton("No", callback_data=f"enviado_no|{action}"),
        )
        bot.send_message(message.chat.id, "¿Enviaste el email?", reply_markup=markup)


# Manejar la respuesta de "Si" o "No"
@bot.callback_query_handler(func=lambda call: call.data.startswith("enviado_"))
def manejar_respuesta_envio(call):
    respuesta, *datos = call.data.split("|")  # Separa correctamente los valores

    # Si la respuesta es "enviado_si", obtenemos la acción y el email
    if respuesta == "enviado_si" and len(datos) == 2:
        accion, email = datos
        get_url, fecha_hora = get_last_netflix_mail(email, keywords.get(accion, []))

        response_message = f"✅ El enlace correspondiente para el email {email} es: {get_url}\nFecha: {fecha_hora}"
        bot.send_message(call.message.chat.id, response_message)

    elif respuesta == "enviado_no":
        bot.send_message(
            call.message.chat.id, "Recuerda enviar el correo para completar la acción."
        )

    bot.answer_callback_query(call.id)  # Asegúrate de responder al callback


if __name__ == "__main__":
    try:
        print("El bot funciona correctamente.")
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"Error al iniciar el bot: {e}")
