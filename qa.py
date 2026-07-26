from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
import json, os
from openai import OpenAI
from dotenv import load_dotenv
from func_calling import send_email, functions
from model import aliyun_search

load_dotenv()
# 创建路由对象，方便在主应用中挂载
qa = APIRouter()

# 全局消息列表，也可认为是模型的记忆
messages = [{
    "role": "system",
    "content": "你是一名专业的AI助手，可以帮助用户解答任何问题。"
}]


@qa.post("/stream")
def stream(question: dict=Body()):
    # 读取JSON参数的值并构建用户提问的消息体
    content = question['content']
    search = question['search']
    
    # 把搜索结果作为提示词一并传入大模型
    if search == True:
      search_result = aliyun_search(content)
      message = {"role": "user", "content": f"请使用以下内容：\n{search_result}\n，并基于用户的提问：\n{content}\n来进行回答"}
    else:
      message = {"role": "user", "content": content}

    # 增加函数调用的功能，让大模型理解用户的提问后返回函数调用的声明
    def check_func_call(message):
      messages.append(message)
      client = OpenAI(api_key=os.getenv("Dashscope_API_Key"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
      completion = client.chat.completions.create(
          model="qwen-plus",
          messages=messages, # type: ignore
          stream=False,        # 函数调用不能与流式响应同时处理
          tools=functions # type: ignore
      ) # type: ignore
      return completion.choices[0].message
    
    # stream_chat()中不再运行messages.append(message)
    def stream_chat():
      # messages.append(message)
      client = OpenAI(api_key=os.getenv("Dashscope_API_Key"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
      
      reply = ""

      # 调用check_func_call()，确认是否存在函数调用
      # 如果存在，则进行函数调用，并让大模型返回函数调用的结果给用户
      # 如果不存在，则直接将用户的提问交给stream_chat()来完成
      output = check_func_call(message)
      if output.tool_calls:
          func_name = output.tool_calls[0].function.name
          func_args = eval(output.tool_calls[0].function.arguments)
          func = globals()[func_name]
          result = func(**func_args)
          messages.append({"role": "user", "content": f"请将以下内容直接回复给用户：{result}"})
      else:
          messages.append(message) # 因为此处已经添加用户问题，所以stream_chat()中不用再次添加用户问题

      # 调用大模型流式生成
      completion = client.chat.completions.create(
        model="qwen-plus",
        messages=messages, # type: ignore
        stream=True,
        stream_options={"include_usage": False}
      ) # type: ignore

      
      for chunk in completion:
        # 使用生成器迭代输出每一个数据流
        # 获取大模型本次增量返回的文本段落
        choice = chunk.choices[0].delta.content
        # 拼接完整的回复
        reply += choice
        # 使用yield把增量数据打包为JSON格式
        # yield让当前函数成为了一个生成器，每产生一个chunk就通过网络推送给前端，实现流式输出
        yield json.dumps({"content": choice}) + "\n"
          
    return StreamingResponse(stream_chat(), media_type="text/event-stream") # type: ignore
    
# 定义接口，并将生成器输出封装到响应中
# @qa.post("/stream")
# def stream_chat(question: dict=Body()):
#     # 读取JSON参数的值
#     content = question['content']
#     search = question['search']

#     # message = {"role": "user", "content": content}
#     # 把搜索结果作为提示词一并传入大模型
#     if search == True:
#       search_result = aliyun_search(content)
#       message = {"role": "user", "content": f"请使用以下内容：\n{search_result}\n，并基于用户的提问：\n{content}\n来进行回答"}
#     else:
#       message = {"role": "user", "content": content}
    
#     def stream_chat():
#         # 将当前消息加入历史消息队列中
#         messages.append(message)
#         # 初始化客户端
#         client = OpenAI(api_key=os.getenv("Dashscope_API_Key"),
#                       base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
#         # 调用大模型流式生成
#         completion = client.chat.completions.create(
#           model="qwen-plus",
#           messages=messages, # type: ignore
#           stream=True,
#           stream_options={"include_usage": False}
#         ) # type: ignore

#         # 定义变量reply，实现流式生成完整的拼接
#         reply = ""
#         print("completion:", completion)

#         for chunk in completion:
#           # 使用生成器迭代输出每一个数据流
#           # 获取大模型本次增量返回的文本段落
#           choice = chunk.choices[0].delta.content
#           # 拼接完整的回复
#           reply += choice
#           # 使用yield把增量数据打包为JSON格式
#           # yield让当前函数成为了一个生成器，每产生一个chunk就通过网络推送给前端，实现流式输出
#           yield json.dumps({"content": choice}) + "\n"

#         # 循环结束后，将AI回复添加到messages中，保存记忆
#         messages.append({"role": "assistant", "content": reply})

#     # 以流式响应的方式响应给前端
#     # 调用内部的stream_chat函数，通过yield返回一个生成器，再把这个生成器包装为流式响应对象返回
#     return StreamingResponse(stream_chat(), media_type="text/event-stream")