from typing import Dict

from telegram import Update
from telegram.ext import CallbackContext

from src.user import User

help_message = """
/start - Register yourself\n
/configure <Lindenhof|Limburgerhof|both> - Choose which shop you want to be notified about\n
/add <flavor> - Add a flavor to your watchlist\n
/remove <flavor> - Remove a flavor from your watchlist\n
/list - List your watchlist\n
/update - Manually check if your flavors are available today\n
/start_notify - Activates notifications (should be executed to get daily automated notifications)
/stop_notify - Deactivates notifications
\n
/help - Get a list of all commands
"""

register_first = "Please register first with /start!"
already_registered = "You have already been registered. Use /configure to select affiliate."
successfully_registered = "You have been successfully registered."

watching_no_flavors = "Currently not watching any ice cream flavors"
