import os
import logging
logger = logging.getLogger(__name__)


class Config:
    # get a token from https://chatbase.com
    CHAT_BASE_TOKEN = os.environ.get("CHAT_BASE_TOKEN", "")
    API_ID = int(os.environ.get("API_ID", 12345))
    API_HASH = os.environ.get("API_HASH")
    OWNER_ID =  int(os.environ.get("OWNER_ID", ""))
    SESSION_NAME = os.environ.get("SESSION_NAME" , "")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001539615782"))
    AUTH_USERS = list(int(i) for i in os.environ.get("AUTH_USERS", "").split(" ")) if os.environ.get("AUTH_USERS", "") else []
    if OWNER_ID not in AUTH_USERS:
        AUTH_USERS.append(OWNER_ID)
    BANNED_USERS = set(int(x) for x in os.environ.get("BANNED_USERS", "").split())
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    BOT_PASSWORD = os.environ.get("BOT_PASSWORD", "") if os.environ.get("BOT_PASSWORD", "") else None
    CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION") if os.environ.get("CUSTOM_CAPTION", "") else None
    HOST = os.environ.get('HOST', '')
    FORCE_SUB = os.environ.get("FORCE_SUB", "") if os.environ.get("FORCE_SUB", "") else None
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    try:
        TIME_GAP = int(os.environ.get("TIME_GAP", "")) if os.environ.get("TIME_GAP", "") else None
    except:
        TIME_GAP = None
        logger.warning("Give the timegap in seconds. Dont use letters 😑")
    TIME_GAP_STORE = {}
    try:
        TRACE_CHANNEL = int(os.environ.get("TRACE_CHANNEL")) if os.environ.get("TRACE_CHANNEL", "") else None
    except:
        TRACE_CHANNEL = None
        logger.warning("Trace channel id was invalid")
