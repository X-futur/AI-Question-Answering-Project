from fastapi import APIRouter, Body
from http import HTTPStatus
import os, requests
from dashscope import ImageSynthesis  # 引入SDK
from dotenv import load_dotenv

load_dotenv()
generate = APIRouter()

# 此功能使用通义万相v2实现，图像生成不支持OpenAI的SDK，需要使用Dashscope的SDK
# 图像生成不存在流式响应，因为响应的内容是一张生成的图像
@generate.post("/generate")
def generate_image(data: dict=Body()):
    api_key=os.getenv("Dashscope_API_Key")
    rsp = ImageSynthesis.call(api_key=api_key, # type: ignore
            model="wanx2.1-t2i-turbo",    # 模型名称
            prompt=data['content'],        # 提示词
            n=1,                           # 生成图像数量
            size='1024*1024')              # 图像尺寸
    if rsp.status_code == HTTPStatus.OK:
        # 在images目录中保存图像
        for result in rsp.output.results:
          # result.url为生成图像的在线地址
          file_name = result.url.split('/')[-1].split("?")[0]
          with open(f'./static/images/{file_name}', 'wb') as f:
              f.write(requests.get(result.url).content)
    # 将图像的URL响应给前端，以便前端进行渲染
    return {"message":"successful", "image_url": f"/static/images/{file_name}"}