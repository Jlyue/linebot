import errno
import os
import sys
import openai
from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    AudioMessage,
    TextMessage
)
from io import BytesIO
from openai import OpenAI

app = Flask(__name__)

openai_api_key = os.getenv('sk-proj-cqvgJtWOFqS7iyduCW3HT3BlbkFJ8i3iAUiQAc2vKBnKjcEL')

# get channel_secret and channel_access_token
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None or channel_access_token is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

configuration = Configuration(
    access_token=channel_access_token
)

# create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

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
        abort(400)

    return 'OK'

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
