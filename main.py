# -*- coding: UTF-8 -*-
"""
MyCloak V1.0 | by TG@seo898
"""

from concurrent.futures import ThreadPoolExecutor
import os
from fastapi.responses import FileResponse, RedirectResponse
from func.function import Func
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware
from starlette.templating import Jinja2Templates
from func.middleware import Mid

app = FastAPI()
# gzip流文件处理
app.add_middleware(GZipMiddleware, minimum_size=600)
# 静态文件路径设置
os.makedirs('./static', exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
# 初始化function
app.state.func = Func()
# 线程管理
app.state.executor = ThreadPoolExecutor(32)
# 创建一个templates（模板）对象，以后可以重用。
app.state.templates = Jinja2Templates(directory="page")


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """错误处理"""
    return JSONResponse(
        status_code=500,
        content={"error": f"{Exception}"},
    )


@app.middleware("http")
async def middleware(request: Request, call_next):
    resp = await Mid().middleware(app, request, call_next)
    return resp


@app.get("/robots.txt")
async def robots(request: Request):
    """robots.txt 文件规定了搜索引擎抓取工具可以访问您网站上的哪些网址"""
    result = JSONResponse(status_code=404,
                          content={"error": './robots.txt 不存在'})
    if os.path.exists('./page/robots.txt'):
        datas = {"request": request}
        result = app.state.templates.TemplateResponse('robots.txt',
                                                      datas,
                                                      media_type="text/plain")
    return result


@app.get("/favicon.ico")
async def favicon(request: Request):
    """favicon.ico"""
    result = JSONResponse(status_code=404,
                          content={"error": './favicon.ico 不存在'})
    if os.path.exists('./favicon.ico'):
        result = FileResponse("favicon.ico", media_type="image/x-icon")
    return result


@app.get("{path:path}")
async def route(request: Request, response: Response, path=""):
    """主路由"""
    datas = {"request": request}
    if len(path.strip('/')) > 1 and os.path.exists(
            os.path.join('./page', path.strip('/'))):
        return app.state.templates.TemplateResponse(path.strip('/'),
                                                    datas,
                                                    media_type="text/html")
    mode = request.state.config["【斗篷设置】"]['模式']
    if mode == '正常':
        return app.state.templates.TemplateResponse('index.html',
                                                    datas,
                                                    media_type="text/html")
    elif mode == '广告':
        ad_path = request.state.config["【斗篷设置】"]["广告地址"]
        if ad_path.startswith('http://') or ad_path.startswith('https://'):
            return RedirectResponse(url=ad_path, status_code=301)
        return app.state.templates.TemplateResponse('ad.html',
                                                    datas,
                                                    media_type="text/html")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=11888)
