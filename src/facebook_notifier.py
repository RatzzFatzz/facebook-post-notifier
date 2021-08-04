import logging
from datetime import date
from typing import List, Dict

import configparser
from facebook_scraper import get_posts
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from src.persit_data import write_data_to_file, read_data_from_file
from src.user import User

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

data: Dict[str, User] = read_data_from_file()
config = configparser.ConfigParser()
config.read("../config")


def start(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username in data:
        context.bot.sendMessage(text="You have already been registered. To change facebook page use /configure",
                                chat_id=update.effective_user.id)
    else:
        data[username] = User(username=username)
        write_data_to_file(data)
        context.bot.sendMessage(text="You have been successfully registered.",
                                chat_id=update.effective_user.id)


def configure(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text="Please register first with /start!",
                                chat_id=update.effective_user.id)
        return
    token = update.message.text.replace("/configure ", "")
    data.get(username).page_url = token
    write_data_to_file(data)
    context.bot.sendMessage(text="Updated facebook page.",
                            chat_id=update.effective_user.id)


def add(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text="Please register first with /start!",
                                chat_id=update.effective_user.id)
        return
    token = update.message.text.replace("/add ", "")
    if token not in data.get(username).ice_cream_flavors:
        data.get(username).ice_cream_flavors.append(token)
        write_data_to_file(data)
        message = str("Now watching out for: {}").format(token)
        context.bot.sendMessage(text=message, chat_id=update.effective_user.id)


def get_update(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text="Please register first with /start!",
                                chat_id=update.effective_user.id)
        return
    for post in get_posts(data.get(username).page_url, pages=1, cookies=config['Cookies']['path-to-cookies']):
        if post['time'].date() == date.today():
            for flavor in data.get(username).ice_cream_flavors:
                if flavor in post['text']:
                    message = str("{} verfügbar").format(flavor)
                    context.bot.sendMessage(text=message, chat_id=update.effective_user.id)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config['Telegram']['bot-token'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("configure", configure))
    dispatcher.add_handler(CommandHandler("update", get_update))


    # on non command i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()