import json
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from openai import OpenAI
import uvicorn


load_dotenv()
recog = APIRouter()

@recog.post('/recognize')
def recognize_image(data: dict=Body()):
    b64str = data['base64'].split(',')[1]
    def stream_chat():
        client = OpenAI(api_key=os.getenv('Dashscope_API_Key'), base_url='https://llm-fmg6raj85fkh752m.cn-beijing.maas.aliyuncs.com/compatible-mode/v1')
        completion = client.chat.completions.create(
            model= 'qwen3.7-plus',
            stream= True,
            messages= [
                {'role': 'system', 'content': '你是一名专业的AI助手，可以帮助用户解答任何问题，也能以精准、简洁的语言识别并描述出图像的内容。'},
                {'role': 'user', 'content': [
                    {'type':'image_url', 'image_url': data['base64']},
                    {'type':'text', 'text': data['content']}
                ]}
            ]
        ) # type: ignore

        # 流式输出
        for chunk in completion:
            if chunk and chunk.choices:
                choice = chunk.choices[0].delta.content
                yield json.dumps({'content': choice}) + '\n'
    return StreamingResponse(stream_chat(), media_type='text/event-stream')