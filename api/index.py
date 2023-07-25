from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage   ##FlexSendMessage
from api.chatgpt import ChatGPT

import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

# domain root
@app.route('/')
def home():
    return 'Hello, ChatGpt-LineBot!'

@app.route("/webhook", methods=['POST'])
## 當 LINE 的服務器，呼叫 callback()時
## 會將 request 的 body 轉成文字，並且傳入 callback() 中
## 這個 body 是 LINE 的 webhook，會包含 LINE 的使用者傳送的訊息
## 這個 body 的格式是 JSON，所以我們需要使用 JSON 的格式來解析
## 這個 body 的格式如下
## {
##   "events": [
##     {
##       "type": "message",
##       "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
##       "source": {
##         "userId": "U206d25c2ea6bd87c17655609a1c37cb8",
##         "type": "user"
##       },
##       "timestamp": 1462629479859,
##       "message": {
##         "id": "325708",
##         "type": "text",
##         "text": "Hello, world"
##       }
##     }
##   ]
## }

def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    ## request 是 flask 的物件，get_data() 是一個 request 物件裡的 method，as_text=True 是將 request 的 body 轉成文字
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    ## line_handler.handle() 是呼叫 WebhookHandler 物件的 handle() method, 這個 method 會將 body 和 signature 傳入
    ## 這個 method 會檢查 signature 是否正確，如果正確就會執行 handle() method 中的程式碼
    ## 如果 signature 不正確，就會回傳 400 的錯誤訊息
    ## 所以， LINE Server 會調用 callback() 函數，把 request 的物件傳入給 web app
    ## web app 的程式碼裡有引入 LINE 開發的 module，名字為 linebot，這個 module 裡有一個 WebhookHandler 的 class
    ## 當 web app 收到 event()時，會呼叫 WebhookHandler 的 handle() method，並且將 request 的物件傳入
    ## 並且將 request 的物件傳入，這個 method 會檢查 signature 是否正確，如果正確就會執行 handle() method 中的程式碼
    ## 如果 signature 不正確，就會回傳 400 的錯誤訊息，web app 不會對這個 request 做任何處理
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


## @ 是 flask 的語法，會將函數註冊到 event handler 中
## event handler 是一個 event 的處理器，當 LINE Server 收到 event 時，會呼叫 event handler
## event handler 會根據 event 的類型，來決定要執行哪一個函數
## 在下面的程式碼中，我們註冊了一個 MessageEvent 的 event handler，當 LINE Server 收到 MessageEvent 時，會呼叫 handle_message() 函數
## handle_message() 函數會檢查 event 的類型是否為 TextMessage，如果是的話，就會執行 handle_message() 函數中的程式碼
@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    
    ## 如果不是文字訊息，就不處理，回傳空值
    if event.message.type != "text":
        return
    
    ## event.message.text 是使用者傳送的文 字訊息
    ## 如果使用者傳送的訊息是 「啟動」，就會回傳 「我是時下流行的AI智能，目前可以為您服務囉，歡迎來跟我互動~」
    ## line_bot_api 是 LINE 開發的 module，這個 module 裡有一個 LineBotApi 的 class
    ## line_bot_api 是一個物件，實體化 LineBotApi 這個 class 後，就會產生 line_bot_api 這個物件
    ## reply_message() 是 LineBotApi class 的 method，會回傳一個訊息給使用者
    ## 需要傳入的參數有兩個，第一個是 reply_token，第二個是 TextSendMessage 物件
    ## reply_token 是 LINE Server 產生的，用來識別使用者的，每一個使用者都有一個獨一無二的 reply_token
    ## TextSendMessage 的 class 是由 module linebot.models 中引入的
    ## TextSendMessage()是一個物件，實體化 TextSendMessage 這個 class 後，就會產生 TextSendMessage 這個物件
    ## class 帶的參數是一個字串，這個字串就是要回傳給使用者的訊息
    if event.message.text == "啟動":
        ## working_status 是一個 global 變數，預設為 False，用來管理是否要啟動 chatbot
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我是時下流行的AI智能，目前可以為您服務囉，歡迎來跟我互動~"))
        return

    if event.message.text == "安靜":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="感謝您的使用，若需要我的服務，請跟我說 「啟動」 謝謝~"))
        return
    
    if working_status:
        ## 若 working_status 沒有變更為 false 的情況下，默認都是 true，會開啟 chatgpt 的服務
        ## 此時會將使用者輸入的訊息，傳入 chatgpt 的物件，並呼叫 add_msg() method
        ## 在 chatgpt class 裡，有一個 add_msg() method，會將使用者輸入的訊息加入 prompt 中
        ## prompt 也是一個 class，會將使用者輸入的訊息加入 prompt 的 list 中，並且限制 prompt 的長度
        chatgpt.add_msg(f"Human:{event.message.text}?\n")
        print("用戶輸入了訊息：" + event.message.text)

        ## .replace() 是將字串中的某個字串取代成另一個字串
        ## 這裡是將回應的訊息中的 AI: 取代成空字串，並且限制取代的次數為 1
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        print("ChatGPT API 回應(取代部份字串)：" + reply_msg)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        print("在 Prompt 再加入這一次 AI 回應的消息，完整訊息為：" + chatgpt.prompt.generate_prompt())
        ## 回傳給使用者的訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    app.run()
