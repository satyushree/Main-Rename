import logging
logger = logging.getLogger(__name__)

import traceback
import os

from ..config import Config
from ..screenshotbot import ScreenShotBot
from ..tools.text import TEXT
from ..database.database import *
from pyrogram import Client as RenamerNs, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup 
from pyrogram.emoji import *


################## Help command ##################

@RenamerNs.on_message(filters.command("help") & filters.private & filters.incoming)
async def help(c, m, cb=False):
    button = [[
        InlineKeyboardButton(f'{HOUSE_WITH_GARDEN} Home', callback_data='back'),
        InlineKeyboardButton(f'{MONEY_BAG} Donate', callback_data='donate')
        ],[
        InlineKeyboardButton(f'{NO_ENTRY} 𝙲𝚕𝚘𝚜𝚎', callback_data='close')
    ]]
    reply_markup = InlineKeyboardMarkup(button)
    if cb:
        await m.message.edit(
            text=TEXT.HELP_USER.format(m.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
    else:
        await m.reply_text(
            text=TEXT.HELP_USER.format(m.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True
        )


################## start commamd ##################

@RenamerNs.on_message(filters.command("start") & filters.private & filters.incoming)
async def start(c, m, cb=False):
    
        
    if not await c.is_user_exist(m.chat.id):
        await c.add_user(m.chat.id)
        await c.send_message(
            Config.LOG_CHANNEL,
            f"New User [{m.from_user.first_name}](tg://user?id={m.chat.id}) started."
        )
        
    owner = await c.get_users(Config.OWNER_ID)
    owner_username = owner.username if owner.username else 'Ns_bot_updates'
    button = [[
        InlineKeyboardButton(f'{MAN_TEACHER_LIGHT_SKIN_TONE} My Owner', url=f'https://t.me/{owner_username}'),
        InlineKeyboardButton(f'{ROBOT} About', callback_data='about')
        ],[
        InlineKeyboardButton(f'{INFORMATION} Help', callback_data="help"),
        InlineKeyboardButton(f'{NO_ENTRY} Close', callback_data="close")
    ]]
    reply_markup = InlineKeyboardMarkup(button)
    if cb:
        await m.message.edit(
            text=TEXT.START_TEXT.format(user_mention=m.from_user.mention, bot_owner=owner.mention(style="md")), 
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
    else:
        await m.reply_text(
            text=TEXT.START_TEXT.format(user_mention=m.from_user.mention, bot_owner=owner.mention(style="md")), 
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True
        ) 


################## about command ##################

@RenamerNs.on_message(filters.command("about") & filters.private & filters.incoming)
async def about(c, m, cb=False):
    me = await c.get_me()
    owner = await c.get_users(Config.OWNER_ID)

    button = [[
        InlineKeyboardButton(f'{HOUSE_WITH_GARDEN} Home', callback_data='back'),
        InlineKeyboardButton(f'{MONEY_BAG} Donate', callback_data='donate')
        ],[
        InlineKeyboardButton(f'{NO_ENTRY} Close', callback_data="close")
    ]]
    reply_markup = InlineKeyboardMarkup(button)
    if cb:
        await m.message.edit(
            text=TEXT.ABOUT.format(bot_name=me.mention(style='md'), bot_owner=owner.mention(style="md")),
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
    else:
        await m.reply_text(
            text=TEXT.ABOUT.format(bot_name=me.mention(style='md'), bot_owner=owner.mention(style="md")),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True
        )


################## Mode command ##################

@RenamerNs.on_message(filters.command("mode") & filters.private & filters.incoming)
async def set_mode(c, m):
    upload_mode = (await get_data(m.from_user.id)).upload_mode
    if upload_mode:
        await update_mode(m.from_user.id, False)
        text = f"From Now all files will be **Uploaded as Video** {VIDEO_CAMERA}"
    else:
        await update_mode(m.from_user.id, True)
        text = f"From Now all files will be **Uploaded as Files** {FILE_FOLDER}"
    await m.reply_text(text, quote=True)
    

################## reset command ##################

@RenamerNs.on_message(filters.command("reset") & filters.private & filters.incoming)
async def reset_user(c, m):
    if m.from_user.id in Config.AUTH_USERS:
        if len(m.command) == 2:
            cmd, user_id = m.command
            try:
                status = await del_user(user_id)
            except Exception as e:
                logger.error(e)
                return await m.reply_text(f'__Error while deleting user from Database__\n\n**Error:** `{e}`')
            if status:
                await m.reply_text(f"Sucessfully removed user with id {user_id} from database")
            else:
                await m.reply_text('User not exist in Database')
        else:
            await m.reply_text('Use this command in the format `/reset user_id`')
    else:
        await m.reply_sticker(sticker="CAACAgIAAx0CVjDmEQACS3lgvEO2HpojwIQe8lqa4L66qEnDzQACjAEAAhZCawq6dimcpGB-fx8E", quote=True)
        await m.reply_text(text="You are not admin to use this command.")


################## login command ##################

@RenamerNs.on_message(filters.command('login') & filters.incoming & filters.private)
async def password(c, m):
    if Config.BOT_PASSWORD:
        if m.from_user.id in Config.AUTH_USERS:
            return await m.reply_text(f"__Hey you are auth user of this bot so you don't want to login {DETECTIVE_LIGHT_SKIN_TONE}.__")

        is_logged = (await get_data(m.from_user.id)).is_logged
        if is_logged:
            return await m.reply_text(f"__You are already loggedin {VICTORY_HAND}.__", quote=True)

        if len(m.command) == 1:
            await m.reply_text('Send me the bot password in the format `/login password`')
        else:
            cmd, pwd = m.text.split(' ', 1)
            if pwd == Config.BOT_PASSWORD:
                await update_login(m.from_user.id, True)
                await m.reply_text(text=LOCKED_WITH_KEY, quote=True)
                await m.reply_text(f'Logged Sucessfully to the bot.\nEnjoy the bot now {FACE_SAVORING_FOOD}.', quote=True)
            else:
                await m.reply_sticker(sticker="CAACAgQAAxkBAAIlHWC8WTwz55v_w0laDRuSrwL2oWRTAALtDAACYLUpUtRT8sziJp59HwQ", quote=True)
                return await m.reply_text(f'Incorrect password', quote=True)
    else:
        await m.reply_text(f'**This bot was publicly available to all {SMILING_FACE_WITH_HEARTS}.**\nIf you are the owner of the bot to make bot private add bot password in Config Vars {LOCKED_WITH_KEY}.', quote=True)

        
        
        ################## ban command ##################
        
        
@RenamerNs.on_message(filters.private & filters.command("status") & filters.user(Config.AUTH_USERS))
async def sts(c, m):
    
    total_users = await c.db.total_users_count()
    await m.reply_text(text=f"Total user(s) {total_users}", quote=True)


@RenamerNs.on_message(filters.private & filters.command("ban_user") & filters.user(Config.AUTH_USERS))
async def ban(c, m):
    
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to ban any user from the bot.\n\nUsage:\n\n`/ban_user user_id ban_duration ban_reason`\n\nEg: `/ban_user 1234567 28 You misused me.`\n This will ban user with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True
        )
        return
    
    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} days for the reason {ban_reason}."
        
        try:
            await c.send_message(
                user_id,
                f"You are banned to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n**Message from the admin**"
            )
            ban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            ban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"
        await c.db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(
            ban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


@RenamerNs.on_message(filters.private & filters.command("unban_user") & filters.user(Config.AUTH_USERS))
async def unban(c, m):
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to unban any user.\n\nUsage:\n\n`/unban_user user_id`\n\nEg: `/unban_user 1234567`\n This will unban user with id `1234567`.",
            quote=True
        )
        return
    
    try:
        user_id = int(m.command[1])
        unban_log_text = f"Unbanning user {user_id}"
        
        try:
            await c.send_message(
                user_id,
                f"Your ban was lifted!"
            )
            unban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            unban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"
        await c.db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(
            unban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


@RenamerNs.on_message(filters.private & filters.command("banned_users") & filters.user(Config.AUTH_USERS))
async def _banned_usrs(c, m):
    all_banned_users = await c.db.get_all_banned_users()
    banned_usr_count = 0
    text = ''
    async for banned_user in all_banned_users:
        user_id = banned_user['id']
        ban_duration = banned_user['ban_status']['ban_duration']
        banned_on = banned_user['ban_status']['banned_on']
        ban_reason = banned_user['ban_status']['ban_reason']
        banned_usr_count += 1
        text += f"> **user_id**: `{user_id}`, **Ban Duration**: `{ban_duration}`, **Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
    reply_text = f"Total banned user(s): `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open('banned-users.txt', 'w') as f:
            f.write(reply_text)
        await m.reply_document('banned-users.txt', True)
        os.remove('banned-users.txt')
        return
    await m.reply_text(reply_text, True)
