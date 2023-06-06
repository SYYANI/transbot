import json
import requests
import logging

from telegram import  Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext
)
from config import tgbot
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> int:
    """
    Start the conversation and ask user for input.
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="这里是一个词典(˵¯͒¯͒˵)"
    )

def echo(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """
    # Print to console
    # print(f'{update.message.from_user.first_name} wrote {update.message.text}')
    text = update.message.text
    url = "http://dict.youdao.com/suggest?q="+text+"&le=eng&num=5&ver=&doctype=json&keyfrom=&model=&mid=&imei=&vendor=&screen=&ssid=&abtest="
    response = requests.request("GET", url)
    data = json.loads(response.text)

    # 检查返回的结果是否成功
    if data["result"]["code"] == 200:
        entries = data["data"]["entries"]
        result_list = []
        result_list.append(f"查询：'{data['data']['query']}'\n\n")
        result_list.append("词典释义:\n")
        for i, entry in enumerate(entries, 1):
            result_list.append(f"{i}. {entry['entry']}: {entry['explain']}\n")
        result_str = "".join(result_list)
    else:
        result_str = f"查询失败，错误码：{data['result']['code']}"

    context.bot.send_message(chat_id=update.effective_chat.id, text=result_str)

def main(token) -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token, request_kwargs={
        'proxy_url': 'socks5://127.0.0.1:10808/'
    })
    # Set your proxy address here

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add start handler
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    dispatcher.add_handler(MessageHandler(~Filters.command, echo))
    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    token = tgbot['token']
    main(token)
