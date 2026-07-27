from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from qa import qa
from recognize import recog
from test import generate
import uvicorn
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# 设置静态目录为static，且设置前端的引用路径为 /static，名字就叫做static
app.mount("/static", StaticFiles(directory="static"), name="static")
# 指定 HTML 模板文件存放在本地的 templates 文件夹中
templates = Jinja2Templates(directory="templates")

# 后端路由注册，把qa.py注册进来
app.include_router(qa)
app.include_router(recog)
app.include_router(generate)

# 首页路由渲染
@app.get('/')
def chat(request: Request):
    # 读取模板chat.html，并把request传入模板响应
    return templates.TemplateResponse(request=request, name="chat.html")

if __name__ == '__main__':
    uvicorn.run(app)