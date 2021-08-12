import configparser
import datetime
import logging
import os
import re
from typing import Dict

from facebook_scraper import get_posts
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from message_util import already_registered, help_message, successfully_registered, register_first, \
    watching_no_flavors
from persist_data import write_data_to_file, read_data_from_file
from user import User

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

data: Dict[str, User] = read_data_from_file()
config = configparser.ConfigParser()
if os.path.isfile("/config/config") or os.path.isfile("../config"):
    config.read("/config/config" if os.path.isfile("/config/config") else "../config")
else:
    logging.log(logging.ERROR, "Config is missing")

cache: Dict[str, any] = {
    "cache_text": None,
    "cache_date": None
}


def start(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username in data:
        context.bot.sendMessage(text=already_registered, chat_id=update.effective_user.id)
    else:
        context.bot.sendMessage(text=help_message, chat_id=update.effective_user.id)
        data[username] = User(username=username)
        write_data_to_file(data)
        context.bot.sendMessage(text=successfully_registered, chat_id=update.effective_user.id)


def configure(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text=register_first, chat_id=update.effective_user.id)
        return
    token = update.message.text.replace("/configure", "").lstrip()
    if not token:
        return
    data.get(username).page_url = token
    write_data_to_file(data)
    context.bot.sendMessage(text="Updated subscribed shop.", chat_id=update.effective_user.id)


def add(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text=register_first, chat_id=update.effective_user.id)
        return
    token = update.message.text.replace("/add", "").lstrip()
    if not token:
        return
    if token.lower() not in data.get(username).ice_cream_flavors:
        data.get(username).ice_cream_flavors.append(token.lower())
        write_data_to_file(data)
        message = str("Now watching out for: {}").format(token.capitalize())
        context.bot.sendMessage(text=message, chat_id=update.effective_user.id)


def remove(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text=register_first, chat_id=update.effective_user.id)
        return
    message = update.message.text.replace("/remove", "").lstrip()
    if not message:
        return
    if message.lower() in data.get(username).ice_cream_flavors:
        data.get(username).ice_cream_flavors.remove(message.lower())
        write_data_to_file(data)
        context.bot.sendMessage(text="Removed {}".format(message.capitalize()), chat_id=update.effective_user.id)


def post(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text=register_first, chat_id=update.effective_user.id)
        return
    if get_post() is not None:
        context.bot.sendMessage(text=get_post(), chat_id=update.effective_user.id)


def list_flavors(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text=register_first, chat_id=update.effective_user.id)
        return
    if len(data.get(username).ice_cream_flavors) > 0:
        message: str = ""
        for flavor in data.get(username).ice_cream_flavors:
            message += flavor.capitalize() + "\n"
        context.bot.sendMessage(text=message, chat_id=update.effective_user.id)
    else:
        context.bot.sendMessage(text=watching_no_flavors, chat_id=update.effective_user.id)


def help(update: Update, context: CallbackContext) -> None:
    context.bot.sendMessage(text=help_message, chat_id=update.effective_user.id)


def get_update(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text=register_first, chat_id=update.effective_user.id)
        return
    if get_available_message(username) is not None:
        context.bot.sendMessage(chat_id=update.message.chat_id, text=get_available_message(username))


def start_notify(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text=register_first, chat_id=update.effective_user.id)
        return
    if len(context.job_queue.get_jobs_by_name(username)) != 0:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Already subscribed to notifications.")
        return
    time = datetime.time(10, 20, 00)
    args = {"username": username,
            "chat_id": update.message.chat_id}
    context.job_queue.run_daily(
        callback=notify_job,
        time=time,
        days=tuple(range(7)),
        context=args,
        name=username)
    context.bot.sendMessage(text="You'll get notified at {} UTC.".format(time.isoformat(timespec="minutes")),
                            chat_id=update.effective_user.id)


def stop_notify(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data:
        context.bot.sendMessage(text=register_first, chat_id=update.effective_user.id)
        return
    if len(context.job_queue.get_jobs_by_name(username)) == 0:
        context.bot.sendMessage(text="You are not subscribed to notifications yet.", chat_id=update.effective_user.id)
        return
    context.job_queue.get_jobs_by_name(username)[0].schedule_removal()
    context.bot.sendMessage(text="You'll not get notified any longer.", chat_id=update.effective_user.id)


def notify_job(context):
    if get_available_message(context.job.context.get("username")) is not None:
        context.bot.sendMessage(chat_id=context.job.context.get("chat_id"),
                                text=get_available_message(context.job.context.get("username")))


def get_available_message(username: str) -> str or None:
    if username not in data:
        return None
    post = get_post()
    available_flavors: list[str] = list()
    user: User = data.get(username)
    for flavor in user.ice_cream_flavors:
        if user.page_url.casefold() == "both".casefold():
            if flavor.casefold() in post.casefold():
                available_flavors.append(flavor)
        elif "Lindenhof".casefold() == user.page_url.casefold() \
                and flavor.casefold() in re.search("Lindenhof((?:.|\s)*?)Limburgerhof", post,
                                                   flags=re.IGNORECASE).group(1) \
                or "Limburgerhof".casefold() == user.page_url.casefold() \
                and flavor.casefold() in re.search("Limburgerhof((?:.|\s)*?)$", post, flags=re.IGNORECASE).group(1):
            available_flavors.append(flavor)
    if len(available_flavors) > 0:
        return "The following flavors are available today: {}".format(', '.join(available_flavors))


def get_post() -> str:
    date_today = datetime.date.today()
    cache_date = cache["cache_date"]
    cache_text = cache["cache_text"]
    if cache_date is not None and cache_date == date_today:
        return cache_text.casefold()
    else:
        posts = get_posts("eismanufakturzeitgeist", pages=1, cookies=config['Cookies']['path-to-cookies'])
        for post in posts:
            if post['time'].date() == date_today:
                cache["cache_text"] = post['text']
                cache["cache_date"] = date_today
                return cache["cache_text"].casefold()


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config['Telegram']['bot-token'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("remove", remove))
    dispatcher.add_handler(CommandHandler("list", list_flavors))
    dispatcher.add_handler(CommandHandler("configure", configure))
    dispatcher.add_handler(CommandHandler("update", get_update))
    dispatcher.add_handler(CommandHandler("post", post))
    dispatcher.add_handler(CommandHandler("start_notify", start_notify, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("stop_notify", stop_notify, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("help", help))

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
