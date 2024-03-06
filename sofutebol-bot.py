import requests
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Configuração do bot
import environs
from telegram.ext import Updater

env = environs.Env()
env.read_env()

TOKEN = env("sofutebol")
url = env("URL")

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

response = requests.get(url, timeout=5)

if response.status_code == 200:
    jogos = response.json()
else:
    jogos = None


def formatar_jogos_para_dia(jogos_para_dia):
    mensagem = f"📅 {jogos_para_dia['diaJogo']}:\n\n"
    for jogo in jogos_para_dia["content"]:
        mensagem += f"⚽ {jogo['jogo']}\n"
        mensagem += f"🏆 {jogo['campeonato']}\n"
        mensagem += f"🕒 {jogo['horario']}\n"
        mensagem += f"📺 {', '.join(jogo['ondePassa'])}\n\n\n"
    mensagem += f"Acesse: <a href='https://sofutebol.live'>sofutebol.live</a>"
    mensagem += f"\n\nComando usado: /jogos"
    return mensagem.strip()


def obter_dias_de_jogo():
    return [jogo["diaJogo"] for jogo in jogos]


def jogos_hoje(update: Update, context: CallbackContext) -> None:
    dias_de_jogo = obter_dias_de_jogo()

    if not dias_de_jogo:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Não há jogos hoje."
        )
        return

    keyboard = [
        [InlineKeyboardButton(dia, callback_data=str(index))]
        for index, dia in enumerate(dias_de_jogo)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Escolha o dia para ver os jogos:",
        reply_markup=reply_markup,
    )


def jogos_por_dia_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    dia_escolhido_index = int(query.data)

    if 0 <= dia_escolhido_index < len(jogos):
        jogos_para_dia_escolhido = jogos[dia_escolhido_index]
        msg_format = formatar_jogos_para_dia(jogos_para_dia_escolhido)
        context.bot.send_message(
            chat_id=query.message.chat_id, text=msg_format, parse_mode="HTML"
        )
    else:
        context.bot.send_message(
            chat_id=query.message.chat_id, text="Dia de jogo inválido."
        )


def help_command(update, context):
    available_commands = [
        "/jogos - Mostra os jogos de hoje\n"
        "/help - Lista de comandos disponíveis",
    ]
    help_message = "Comandos disponíveis:\n" + "\n".join(available_commands)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=help_message)


# Adicione o manipulador de comandos para o comando /jogos
dispatcher.add_handler(CommandHandler("jogos", jogos_hoje))

# Adicione o manipulador de consulta de botões
dispatcher.add_handler(CallbackQueryHandler(jogos_por_dia_callback))

dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(MessageHandler(
    Filters.text & ~Filters.command, help_command))

# Inicie o bot
updater.start_polling()
updater.idle()
