import logging
logger = logging.getLogger(__name__)

import os
import time
import random
from renamer.config import Config
from renamer.tools.text import TEXT
from renamer.tools.progress_bar import progress_bar, take_screen_shot
from renamer.tools.timegap_check import timegap_check
from renamer.tools.thumbnail_fixation import fix_thumb
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from renamer.database.database import *
from pyrogram import Client as RenamerNs, filters
from pyrogram.errors import PeerIdInvalid, ChannelInvalid, FloodWait
from pyrogram.emoji import *


@RenamerNs.on_message((filters.document|filters.video) & filters.private & filters.incoming)
async def media(c, m):
    """Checking and Processing the renaming"""

    if Config.BANNED_USERS:
        if m.from_user.id in Config.BANNED_USERS:
            return await m.reply_text(TEXT.BANNED_USER_TEXT, quote=True)

    if Config.BOT_PASSWORD:
        is_logged = (await get_data(m.from_user.id)).is_logged
        if not is_logged and m.from_user.id not in Config.AUTH_USERS:
            return await m.reply_text(TEXT.NOT_LOGGED_TEXT, quote=True)
        
    if Config.TIME_GAP:
        time_gap = await timegap_check(m)
        if time_gap:
            return

    file_name = await c.ask(chat_id=m.from_user.id, text="Send me the New FileName for this file or send /cancel to stop", filters=filters.text)
    await file_name.delete()
    await file_name.request.delete()
    new_file_name = file_name.text
    if new_file_name.lower() == "/cancel":
        await m.delete()
        return

    if Config.TIME_GAP:
        time_gap = await timegap_check(m)
        if time_gap:
            return
        Config.TIME_GAP_STORE[m.from_user.id] = time.time()
        asyncio.get_event_loop().create_task(notify(m, Config.TIME_GAP))

    send_message = await m.reply_text(TEXT.DOWNLOAD_START)
    trace_msg = None
    if Config.TRACE_CHANNEL:
        try:
            media = await m.copy(chat_id=Config.TRACE_CHANNEL)
            trace_msg = await media.reply_text(f'**User Name:** {m.from_user.mention(style="md")}\n\n**User Id:** `{m.from_user.id}`\n\n**New File Name:** `{new_file_name}`\n\n**Status:** Downloading....')
        except PeerIdInvalid:
            logger.warning("Give the correct Channel or Group ID.")
        except ChannelInvalid:
            logger.warning("Add the bot in the Trace Channel or Group as admin to send details of the users using your bot")
        except Exception as e:
            logger.warning(e)

    download_location = f'{Config.DOWNLOAD_LOCATION}/{m.from_user.id}/'
    if not os.path.isdir(download_location):
        os.makedirs(download_location)

    start_time = time.time()
    try:
        file_location = await m.download(
                            file_name=download_location,
                            progress=progress_bar,
                            progress_args=("Downloading:", start_time, send_message)
                        )
    except Exception as e:
        logger.error(e)
        await send_message.edit(f"**Error:** {e}")
        if trace_msg:
            await trace_msg.edit(f'**User Name:** {m.from_user.mention(style="md")}\n\n**User Id:** `{m.from_user.id}`\n\n**New File Name:** `{new_file_name}`\n\n**Status:** Failed\n\nCheck logs for error')
        return

    new_file_location = f"{download_location}{new_file_name}"
    os.rename(file_location, new_file_location)

    try:
        metadata = extractMetadata(createParser(new_file_location))
        duration = 0
        if metadata.has("duration"):
           duration = metadata.get('duration').seconds
    except:
        duration = 0

    thumbnail_location = f"{Config.DOWNLOAD_LOCATION}/{m.from_user.id}.jpg"
    # if thumbnail not exists checking the database for thumbnail
    if not os.path.exists(thumbnail_location):
        thumb_id = (await get_data(m.from_user.id)).thumb_id

        if thumb_id:
            thumb_msg = await c.get_messages(m.chat.id, thumb_id)
            try:
                thumbnail_location = await thumb_msg.download(file_name=thumbnail_location)
            except:
                thumbnail_location = None
        else:
            try:
                thumbnail_location = await take_screen_shot(new_file_location, os.path.dirname(os.path.abspath(new_file_location)), random.randint(0, duration - 1))
            except Exception as e:
                logger.error(e)
                thumbnail_location = None

    width, height, thumbnail = await fix_thumb(thumbnail_location)

    try:
        await send_message.edit(TEXT.UPLOAD_START)
        if trace_msg:
            await trace_msg.edit(f'**User Name:** {m.from_user.mention(style="md")}\n\n**User Id:** `{m.from_user.id}`\n\n**New File Name:** `{new_file_name}`\n\n**Status:** Uploading')
    except:
        pass

    caption = str(new_file_name)
    if Config.CUSTOM_CAPTION:
        caption += f"\n\n {Config.CUSTOM_CAPTION}"
    as_file = (await get_data(m.from_user.id)).upload_mode
    if as_file:
        try:
            await m.reply_document(
                document=new_file_location,
                caption=caption,
                thumb=thumbnail,
                progress=progress_bar,
                progress_args=("Uploading:", start_time, send_message)
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            logger.warning(f"Got FloodWait for {e.x} Seconds")
        except Exception as e:
            logger.error(e)

    else:
        try:
            await m.reply_video(
                video=new_file_location,
                duration=duration,
                width=width,
                height=height,
                caption=caption,
                thumb=thumbnail,
                progress=progress_bar,
                progress_args=("Uploading:", start_time, send_message)
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            logger.warning(f"Got FloodWait for {e.x} Seconds")
        except Exception as e:
            logger.error(e)

    try:
        await send_message.edit(TEXT.UPLOAD_SUCESS, disable_web_page_preview=True)
        if trace_msg:
            await trace_msg.edit(f'**User Name:** {m.from_user.mention(style="md")}\n\n**User Id:** `{m.from_user.id}`\n\n**New File Name:** `{new_file_name}`\n\n**Status:** Uploaded Sucessfully {CHECK_MARK_BUTTON}')
        os.remove(new_file_location)
    except:
        pass

async def notify(m, time_gap):
    await asyncio.sleep(time_gap)
    await m.reply_text("__You can use me Now__")
    
    
    
    


if bool(os.environ.get("WEBHOOK", False)):
    from renamer.config import Config
else:
    from config import Config

# the Strings used for this "thing"
from renamer.tools.text import TEXT

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import Client, filters

from helper_funcs.chat_base import TRChatBase
from renamer.tools.progress_bar import progress_bar

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image


@pyrogram.Client.on_message(pyrogram.filters.command(["rename_doc"]))
async def rename_doc(bot, update):
    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return
    TRChatBase(update.from_user.id, update.text, "rendoc")
    if (" " in update.text) and (update.reply_to_message is not None):
        cmd, file_name = update.text.split(" ", 1)
        if len(file_name) > 64:
            await update.reply_text(
                TEXT.IFLONG_FILE_NAME.format(
                    alimit="64",
                    num=len(file_name)
                )
            )
            return
        description = TEXT.CUSTOM_CAPTION_UL_FILE
        download_location = Config.DOWNLOAD_LOCATION + "/"
        a = await bot.send_message(
            chat_id=update.chat.id,
            text=TEXT.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        c_time = time.time()
        the_real_download_location = await bot.download_media(
            message=update.reply_to_message,
            file_name=download_location,
            progress=progress_bar,
            progress_args=(
                TEXT.DOWNLOAD_START,
                a,
                c_time
            )
        )
        if the_real_download_location is not None:
            try:
                await bot.edit_message_text(
                    text=TEXT.SAVED_RECVD_DOC_FILE,
                    chat_id=update.chat.id,
                    message_id=a.message_id
                )
            except:
                pass
            new_file_name = download_location + file_name
            os.rename(the_real_download_location, new_file_name)
            await bot.edit_message_text(
                text=TEXT.UPLOAD_START,
                chat_id=update.chat.id,
                message_id=a.message_id
                )
            logger.info(the_real_download_location)
            thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                thumb_image_path = None
            else:
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                # img.thumbnail((90, 90))
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            c_time = time.time()
            await bot.send_document(
                chat_id=update.chat.id,
                document=new_file_name,
                thumb=thumb_image_path,
                caption=description,
                # reply_markup=reply_markup,
                reply_to_message_id=update.reply_to_message.message_id,
                progress=progress_bar,
                progress_args=(
                    TEXT.UPLOAD_START,
                    a, 
                    c_time
                )
            )
            try:
                os.remove(new_file_name)
                #os.remove(thumb_image_path)
            except:
                pass
            await bot.edit_message_text(
                text=TEXT.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.chat.id,
                message_id=a.message_id,
                disable_web_page_preview=True
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=TEXT.REPLY_TO_DOC_FOR_RENAME_FILE,
            reply_to_message_id=update.message_id
        )
