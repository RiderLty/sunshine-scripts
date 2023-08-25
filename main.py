import asyncio
import json
import os
import sys
from time import sleep
from fastapi import FastAPI
from uvicorn import Config, Server
import subprocess
from fastapi.responses import HTMLResponse
from os.path import join as path_join


help_text = '''<h1>快速设置显示器模式</h1>
<p>多显示器模式 </p>
<p>1=仅内置屏幕</p>
<p>2=仅外置屏幕</p>
<p>3=扩展</p>
<p>4=复制</p>
<h2>直接调用</h2>
<h3>使用内置模式</h3>
<p>向 typeMap 内添加模式</p>
<p>格式为</p>
<pre><code class="language-json">名称:[多显示器模式,宽度,高度,刷新率]
</code></pre>
<p>然后可以直接通过单个名称参数来调用设置</p>
<h2>手动设定</h2>
<p>使用 多显示器模式 宽度 高度 刷新率 四个参数 直接设定</p>
<h2>服务器模式</h2>
<p>用于远程调用</p>
<ul>
<li>使用内置模式</li>
</ul>
<pre><code>/set/{type}
</code></pre>
<p>type为内置参数的名称</p>
<p>例如：/set/default</p>
<ul>
<li>手动设定</li>
</ul>
<pre><code>/dwhr/{mode}
</code></pre>
<p>多显示器模式,宽度,高度,刷新率  用.连接</p>
<p>例如：/dwhr/1.1920.1080.120</p>
'''

typeMap = {
    "default": [1, 3440, 1440, 165],
    "ipad": [2, 2388, 1668, 120],
    "1080p60": [2, 1920, 1080, 60],
    "1080p120": [2, 1920, 1080, 120],
}

app = FastAPI()

if getattr(sys, 'frozen', False):  # 判断是否打为包
    ROOT_PATH = os.path.dirname(os.path.abspath(sys.executable))
    SERVER_FILE = path_join(sys._MEIPASS, "static")
elif __file__:
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    SERVER_FILE = path_join(ROOT_PATH, "static")

QRes_path = path_join(SERVER_FILE,"QRes.exe")
DisplaySwitch_path = path_join(SERVER_FILE,"DisplaySwitch.exe")
# print("QRes_path",QRes_path)
# print("DisplaySwitch",DisplaySwitch)

def QRes(width, height, rate):
    cmd = rf"{QRes_path} /X:{width} /Y:{height} /R:{rate}"
    print(cmd)
    result = subprocess.run(cmd,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    return {
        "stdout": result.stdout,
        "returncode": result.returncode,
        "stderr": result.stderr,
    }


def DisplaySwitch(type):
    if int(type) not in [1, 2, 3, 4]:
        return 'type must in [1,2,3,4]'
    typeStr = ["internal", "external", "extend", "clone"][int(type)-1]
    cmd = rf"{DisplaySwitch_path} /{typeStr}"
    print(cmd)
    result = subprocess.run(cmd,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    return {
        "stdout": result.stdout,
        "returncode": result.returncode,
        "stderr": result.stderr,
    }


@app.get("/set/{type}")
def set(type: str = None):
    if type == None:
        return json.dumps(typeMap, indent=4)
    if type not in typeMap.keys():
        return json.dumps(typeMap, indent=4)
    else:
        DisplaySwitch(typeMap[type][0])
        sleep(3)
        QRes(typeMap[type][1], typeMap[type][2], typeMap[type][3])
        return typeMap[type][0],typeMap[type][1], typeMap[type][2], typeMap[type][3]


@app.get("/dwhr/{mode}")
def dwhr(mode: str = None):
    try:
        display, width, height, rate = mode.split(".")
        DisplaySwitch(display)
        sleep(3)
        QRes(width, height, rate)
        return "ok"
    except Exception as e:
        return str(e) + help_text


@app.get("/", response_class=HTMLResponse)
def index():
    return help_text


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        config = Config(
            app=app,
            # host="::",
            host="0.0.0.0",
            port=8106,
            log_level="info",
        )
        asyncio.get_event_loop().run_until_complete(Server(config=config).serve())
    elif len(args) == 4:
        print(dwhr(f"{args[0]}.{args[1]}.{args[2]}.{args[3]}"))
    elif len(args) == 1:
        print(set(args[0]))
    else:
        print("args error : display width height rate")
