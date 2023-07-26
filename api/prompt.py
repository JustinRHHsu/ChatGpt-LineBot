import os


chat_language = os.getenv("INIT_LANGUAGE", default = "zh")

# Message 最多在 List 中的數量為 20
MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default = 2))
LANGUAGE_TABLE = {
  "zh": "嗨！",
  "en": "Hi!"
}


## Prompt class 的作用是將使用者輸入的訊息加入 prompt 中，並且限制 prompt 的長度
## 其中有三個 method，分別是 __init__、add_msg、remove_msg
## __init__ 是初始化，會設定一個 msg_list，並且將第一個訊息加入 msg_list 中

class Prompt:
    def __init__(self):
        self.msg_list = []
        self.msg_list.append(f"AI:{LANGUAGE_TABLE[chat_language]}")
    
    def add_msg(self, new_msg):
        # 如果 msg_list 的長度超過 MSG_LIST_LIMIT，就移除第一個訊息
        if len(self.msg_list) >= MSG_LIST_LIMIT:
            self.remove_msg()
        self.msg_list.append(new_msg)

    def remove_msg(self):
        ## pop() 是移除 List 中的第一個元素，0 指的是第一個元素
        self.msg_list.pop(0)

    def generate_prompt(self):
        ## join() 是將 List 中的元素組合成一個字串，並且以換行符號分隔
        ## '\n'.的寫法是將換行符號加入字串中，每一個元素都會以換行符號分隔
        return '\n'.join(self.msg_list)
