## api.prompt 是
from api.prompt import Prompt

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
## declar a global variable that will store usage of open api, default is 0
usage = 0

# ChatGPT 的 class 有三個 method，分別是 __init__、get_response、add_msg
# __init__ 是初始化，會設定一些參數，例如 model、temperature、frequency_penalty、presence_penalty、max_tokens
# get_response 是取得回應，會呼叫 openai.Completion.create 來取得回應
# add_msg 是新增訊息，會呼叫 prompt.add_msg 來新增訊息，將使用者輸入的訊息加入 prompt 中
class ChatGPT:
    def __init__(self):
        self.prompt = Prompt()
        #self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo")
        self.model = os.getenv("OPENAI_MODEL", default = "text-davinci-003")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0))
        self.frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", default = 0))
        self.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", default = 0.6))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 240))

    ## get_response 函數裡有一個 openai.Completion.create()，會呼叫 OpenAI API 來取得回應
    ## 其中 create() 有幾個參數，分別是 model、prompt、temperature、frequency_penalty、presence_penalty、max_tokens
    ## self.model 會帶入 OPENAI_MODEL 的環境變數，預設為 text-davinci-003
    ## prompt object 會呼叫 generate prompt() method，generate_prompt 會將 list 中的元素組合成一個字串，並且以換行符號分隔
    ## 再回到 get_response()裡，回存到 response 變數中，response 是一個 dictionary 的資料型態
    ## get_response() 會回傳 response['choices'][0]['text'].strip()，這個字串就是回應的訊息
    ## openai api 的回應格式如下
    ## {
    ##   "id": "cmpl-2hQJZKz5jz5n5Z5Z5Z5Z5Z5Z5",
    ##   "object": "text_completion",
    ##   "created": 1619268370,
    ##   "model": "davinci:2020-05-03",
    ##   "choices": [
    ##     {
    ##       "text": "Hello, how are you?",
    ##       "index": 0,
    ##       "logprobs": null,
    ##       "finish_reason": "length"
    ##     }
    ##   ]
    ## }
    ## .strip() 是將字串前後的空白符號去除

    def get_response(self):
        global usage
        response = openai.Completion.create(
            model=self.model,
            prompt=self.prompt.generate_prompt(),
            temperature=self.temperature,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            max_tokens=self.max_tokens
        )
        
        ## print out prompt_tokens, completion_tokens and total_tokens
        print("prompt_tokens: " + str(response['usage']['prompt_tokens']))
        print("completion_tokens: " + str(response['usage']['completion_tokens']))
        print("total_tokens: " + str(response['usage']['total']))
        ## then retrieve total_tokens and store into the global variable usage
        usage = response['usage']['total']
        print("OpenAI API usage: " + str(usage))

        return response['choices'][0]['text'].strip()

    def add_msg(self, text):
        self.prompt.add_msg(text)


    ## write a function that to query the latest usage of openai api
    ## https://beta.openai.com/docs/api-reference/retrieve-engine
    ## https://beta.openai.com/docs/api-reference/retrieve-completion
    def get_usage(self):
        global usage
        return usage
    
