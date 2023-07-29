# 导入必要的模块
from flask import Flask, request
import os

# 创建Flask应用
app = Flask(__name__)

# 定义存储路径
storage_path = "path/to/storage_directory/"

# 云端接收函数框架
@app.route("/receive", methods=["POST"])
def receive():
    # 从请求中获取参数和数据
    ip_address = request.form.get("ip_address")
    port = request.form.get("port")
    request_type = request.form.get("request_type")
    data = request.form.get("data")
    makelog('0001 login')//孔做的日志添加函数
    # 根据请求类型调用相应的处理函数
    if request_type == "registration":
        # 执行注册请求的处理逻辑
        # ...
        return "Registration request processed successfully"
    elif request_type == "login":
        # 执行登录请求的处理逻辑
        # ...
        return "Login request processed successfully"
    elif request_type == "file_upload":
        # 执行文件上传请求的处理逻辑
        # ...
        # 储存文件
        file = request.files.get("file")
        file_save(file)//孔做的文件存储函数
        return "File upload request processed successfully and file stored"

    # 处理未知请求类型的情况
    return "Unknown request type"

#日志存储
def makelog(strr):
    with open("log.txt",'a') as file:
        file.write(strr)
        file.write("\n")
    file.close()

def file_save(file):
    f=open("file")
    s=f.read()
    with open("storage.txt") as filee:
        filee.write(s)
        filee.write("\n")
        filee.close()

# 运行Flask应用
if __name__ == "__main__":
    app.run()