# -*- coding: UTF-8 -*-
"""gunicorn后台运行"""

import os
import re
import time
import click
from func.function import Func


def createj_nginx_conf(port, domain):
    "自动创建nginx配置文件"
    if not os.path.exists("logs"):
        os.makedirs("./logs")
    path = f"/www/server/panel/vhost/nginx/{domain}.conf"
    if os.path.exists(path):
        with open(path, "r", encoding='utf8') as f:
            conf = f.read()
        print(f"{conf}\n\n以上为nignx配置信息")
    else:
        conf = """server {
 listen 80;
 server_name 【域名】;
 return 301 https://$host$request_uri;
}

server {
 listen 443 ssl;
 server_name 【域名】;
 index index.html;
 root /www/server/nginx/html;

 ssl_certificate /etc/letsencrypt/live/【域名】/fullchain.pem;
 ssl_certificate_key /etc/letsencrypt/live/【域名】/privkey.pem;

 location / {
 proxy_pass http://127.0.0.1:【端口号】;
 proxy_pass_header Server;
 proxy_redirect off;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header Host $host;
 client_max_body_size 10m;
 client_body_buffer_size 128k;
 proxy_connect_timeout 90;
 proxy_send_timeout 90;
 proxy_read_timeout 90;
 proxy_buffer_size 4k;
 proxy_buffers 4 32k;
 proxy_busy_buffers_size 64k;
 proxy_temp_file_write_size 64k;
 }

 error_page 500 502 503 504 /50x.html;
 location = /50x.html {
 root /www/wwwroot/【域名】/page;
 }
}""".replace("【端口号】", str(port)).replace('【域名】', domain)
        with open(path, "w", encoding='utf8') as f:
            f.write(conf)
        print(f"{conf}\n\nnignx配置文件已生成")
        content = f"service nginx stop && certbot certonly --standalone --email seo888@gmx.com -w /www/wwwroot/ -d {domain} && service nginx start"
        os.popen(content)
        print("nignx服务已重启")


def start():
    "开始"
    config = Func().getYml('config.yml')
    port = config["【斗篷设置】"]['端口']
    domain = config["【斗篷设置】"]['绑定域名'][0]
    createj_nginx_conf(port, domain)
    content = "gunicorn -c conf.py main:app -k uvicorn.workers.UvicornWorker --daemon"
    os.popen(content)
    print('程序已运行')


def close():
    "关闭"
    send = os.popen("pstree -ap|grep gunicorn")
    result = send.read()
    if "|-gunicorn," in result:
        print('程序后台运行中，正在关闭进程...')
        program_name = os.path.basename(os.path.abspath('.'))
        sid = re.findall(r'gunicorn,(\d+).*?/' + program_name, result)
        print(sid)
        for i in sid:
            kill = f"kill -9 {i}"
            print(kill + f" from {program_name}")
            os.system(kill)


def restart():
    "重启"
    close()
    print('现在启动程序')
    time.sleep(1)
    start()


@click.command()
@click.option("--mode", default="start", help="模式：1.重启 2.停止 ")
def run(mode):
    """运行"""
    if mode == "start":
        mode = input('0.启动 1.重启 2.停止 选择模式：')
    if mode == "0":
        start()
    elif mode == "1":
        restart()
    else:
        close()


if __name__ == '__main__':
    run()
