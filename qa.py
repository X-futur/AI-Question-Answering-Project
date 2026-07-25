from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
import json, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# 创建路由对象，方便在主应用中挂载
qa = APIRouter()

# 全局消息列表，也可认为是模型的记忆
messages = [{
    "role": "system",
    "content": "你是一名专业的AI助手，可以帮助用户解答任何问题。"
}]

# 定义接口，并将生成器输出封装到响应中
@qa.post("/stream")
def stream_chat(question: dict=Body()):
    # 读取JSON参数的值
    content = question['content']
    search = question['search']
    message = {"role": "user", "content": content}
    
    def stream_chat():
        # 将当前消息加入历史消息队列中
        messages.append(message)
        # 初始化客户端
        client = OpenAI(api_key=os.getenv("Dashscope_API_Key"),
                      base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        # 调用大模型流式生成
        completion = client.chat.completions.create(
          model="qwen-plus",
          messages=messages, # type: ignore
          stream=True,
          stream_options={"include_usage": False}
        ) # type: ignore

        # 定义变量reply，实现流式生成完整的拼接
        reply = ""
        print("completion:", completion)

        for chunk in completion:
          # 使用生成器迭代输出每一个数据流
          # 获取大模型本次增量返回的文本段落
          choice = chunk.choices[0].delta.content
          # 拼接完整的回复
          reply += choice
          # 使用yield把增量数据打包为JSON格式
          # yield让当前函数成为了一个生成器，每产生一个chunk就通过网络推送给前端，实现流式输出
          yield json.dumps({"content": choice}) + "\n"

        # 循环结束后，将AI回复添加到messages中，保存记忆
        messages.append({"role": "assistant", "content": reply})

    # 以流式响应的方式响应给前端
    # 调用内部的stream_chat函数，通过yield返回一个生成器，再把这个生成器包装为流式响应对象返回
    return StreamingResponse(stream_chat(), media_type="text/event-stream")