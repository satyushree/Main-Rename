import logging

# Get logging configurations
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - Line: %(lineno)d - Path: %(name)s - Module: %(module)s.py - %(levelname)s - %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.WARNING)

import os
import platform
from .config import Config
from pyrogram import Client, __version__, idle
from pyromod import listen

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from renamer.config import Config

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)


if __name__ == "__main__" :
    # create download directory, if not exist
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    plugins = dict(
        root="plugins"
    )
    app = pyrogram.Client(
        "[ARM] RENAME",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        plugins=dict(root="renamer/plugins"),
                 workers=100)
    
    app.start()


def main():

    Renamer = Client("[ARM] RENAME",
                 bot_token=Config.BOT_TOKEN,
                 api_id=Config.API_ID,
                 api_hash=Config.API_HASH,
                 plugins=dict(root="renamer/plugins"),
                 workers=100)

    Renamer.start()
    me = Renamer.get_me()

    startup_msg = f"Successfully deployed your Renamer at @{me.username}\n"
    startup_msg += f"Pyrogram Version: V{__version__}\n"
    startup_msg += f"Python Version: V{platform.python_version()}\n\n"
    startup_msg += "Thanks for deploying our bot. Please give a star to my repo and join @All_Movie_Rockers."
    print(startup_msg)

    
    

#import logging
#logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger = logging.getLogger(__name__)

#import os

## the secret configuration specific things
