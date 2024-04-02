import requests
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import tgbot

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DICT_API_URL = "http://dict.youdao.com/suggest"
TRANSLATE_API_URL = "https://api.deeplx.org/translate"

def start(update: Update, context: CallbackContext) -> None:
    """Start the conversation and ask user for input."""
    update.message.reply_text("这里是一个词典(˵¯͒ ¯͒˵)")

def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    Here, a simple heuristic is used: if the text contains any Chinese character, it is considered Chinese.
    This is a basic approach. For more accuracy, consider using a library like langdetect.
    """
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return 'zh'
    return 'en'

def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    with requests.Session() as session:
        payload = {"text": text, "source_lang": from_lang, "target_lang": to_lang}
        response = session.post(TRANSLATE_API_URL, json=payload)
        data = response.json()
        if data.get('code') == 200:
            return data.get('data', "翻译失败(。•́︿•̀。)")
        else:
            return "翻译失败(。•́︿•̀。)"

def lookup_word(word: str) -> str:
    with requests.Session() as session:
        params = {"q": word, "le": "eng", "num": 5, "doctype": "json"}
        response = session.get(DICT_API_URL, params=params)
        data = response.json()
        if data.get("result", {}).get("code") == 200:
            entries = data.get("data", {}).get("entries", [])
            result_list = [f"查询：'{data['data']['query']}'\n\n词典释义:\n"]
            for i, entry in enumerate(entries, 1):
                result_list.append(f"{i}. {entry['entry']}: {entry.get('explain', '')}\n")
            return "".join(result_list)
        else:
            return "只能查单词哦(。•́︿•̀。)"

def echo(update: Update, context: CallbackContext) -> None:
    user_mode = context.user_data.get('mode', 'word')
    text = update.message.text
    if user_mode == 'word':
        result_str = lookup_word(text)
    else:
        source_lang = detect_language(text)
        target_lang = 'en' if source_lang == 'zh' else 'zh'
        result_str = translate_text(text, source_lang, target_lang)
    update.message.reply_text(result_str)

def switch(update: Update, context: CallbackContext) -> None:
    current_mode = context.user_data.get('mode', 'word')
    new_mode = 'sentence' if current_mode == 'word' else 'word'
    context.user_data['mode'] = new_mode
    mode_message = "已切换到句子模式" if new_mode == 'sentence' else "已切换到单词模式"
    update.message.reply_text(mode_message)

def main() -> None:
    """Run the bot."""
    updater = Updater(tgbot['token'],request_kwargs={
        'proxy_url': 'socks5://127.0.0.1:1080/'
    })
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('switch', switch))
    dispatcher.add_handler(MessageHandler(~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
