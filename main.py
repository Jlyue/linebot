from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    MessagingApiBlob,
    AudioMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

import os
from openai import OpenAI
OPENAI_API_KEY = os.getenv('openai_api_key')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
# if channel_secret is None or channel_access_token is None:
#     print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
#     sys.exit(1)
# TODO Use raise error.

app = Flask(__name__)

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# TODO import whisper API module, don't import whisper in this script, make it a module.
# handle received audio messages
@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):
    try:
        if(event.message.type == "audio"):
            audio_content = Configuration.get.message_content(event.message.id)
            path='./temp.mp3'
            with open(path,'wb') as fd:
                for chunk in audio_content.iter_content():
                    fd.writ(chunk)

            with open("temp.mp3", "rb") as audio_file:
                openai.api_key="sk-proj-cqvgJtWOFqS7iyduCW3HT3BlbkFJ8i3iAUiQAc2vKBnKjcEL"
                model_id='whisper-1'
                
                client = OpenAI(api_key=openai_api_key)

                audio_file.seek(0)
                transcript = client.audio.transcriptions.create(
                  model="whisper-1",
                  file=audio_file,
                  response_format="text",
                )
                result_content = f'{transcript}'

    except Exception as e:
        result_content += f'Error\n【{e}】'

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=result_content.strip('\n').strip(' '))
                ]
            )
        )

if __name__ == "__main__":
    app.run()
