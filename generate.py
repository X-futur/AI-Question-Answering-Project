import os
import dashscope
from dotenv import load_dotenv
from fastapi import APIRouter, Body
from dashscope.aigc.image_generation import ImageGeneration
from dashscope.api_entities.dashscope_response import Message


load_dotenv()
generate = APIRouter()

@generate.post("/generate")
def generate_image(data: dict=Body()):
    api_key = os.getenv('Dashscope_API_Key')
    dashscope.base_http_api_url = 'https://llm-fmg6raj85fkh752m.cn-beijing.maas.aliyuncs.com/api/v1'

    text = data['content']

    message = Message(
        role="user",
        content=[
            {"text": text}
        ]
    )

    response = ImageGeneration.async_call(
        model="wan2.7-image-pro",
        api_key=api_key, # type: ignore
        messages=[message],
        enable_sequential=False,
        n=1,
        size="2K"
    )
    
    if response.status_code == 200: # type: ignore
        print(f"任务提交成功，任务ID: {response.output.task_id}") # type: ignore
        
        # 等待任务完成
        status = ImageGeneration.wait(task=response, api_key=api_key) # type: ignore
        
        if status.output.task_status == "SUCCEEDED":
            print("任务完成!")
            print(f"结果:")
            print(status)
        else:
            print(f"任务失败，状态: {status.output.task_status}")
    else:
        print(f"任务创建失败: {response.code} - {response.message}") # type: ignore
        return {"message": "failed"}

    image_url = status["output"]["choices"][0]["message"]["content"][0]["image"]

    return {"message": "success", "image_url": image_url}