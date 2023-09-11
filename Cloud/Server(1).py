from flask import Flask, request, jsonify
import csv
import os
import ipaddress
from flask import make_response
from datetime import datetime, timedelta
import requests
import random

app = Flask(__name__)


# 存储按组分的部分密钥和参与人数
groups = {}

@app.route('/send_partial_key', methods=['POST'])
def receive_partial_key():
    client_id = request.cookies.get('user_id')  # 从cookie中获取client_id
    if client_id is None:
        log_behavior(0,"stranger want to get key")
        return jsonify({'status': 'client_id not found in cookies'}), 400
    log_behavior(client_id,"sent partial key")
    partial_key = request.json.get('partial_key')
    group_id = request.json.get('group_id')
    num_members = request.json.get('num_members')
    localurl = request.json.get('localurl')
    if group_id not in groups:
        groups[group_id] = {'members': {}, 'num_members': num_members, 'localurls': {}}
        
    groups[group_id]['members'][client_id] = partial_key
    groups[group_id]['localurls'][client_id] = localurl
    
    if len(groups[group_id]['members']) == groups[group_id]['num_members']:
        for client, url in groups[group_id]['localurls'].items():
            send_information(url, groups[group_id]['members'])
        del groups[group_id]
    
    return jsonify({'status': 'received'})

url1='http://localhost:5001/receive_information'

@app.route('/receive_information', methods=['POST'])
def receive_information():
    # 从POST请求中获取数据
    data = request.get_json()
    print(f"Received data: {data}")
    return 'OK', 200

@app.route('/receive_file', methods=['POST'])
def receive_file():
    # 从POST请求中获取文件
    file_data = request.files.get('file')
    if file_data:
        with open('received_file', 'wb') as file:
            file.write(file_data.read())
        return 'OK', 200
    else:
        return 'No file in request', 400

def add_account(username, password, ip):
    filename = "accounts.csv"
    id = 1

    # 检查文件是否存在，如果存在，获取最后一行的 ID
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            last_line = list(csv.reader(f))[-1]
            id = int(last_line[0]) + 1
    log_behavior(id,"registed")
    # 将账户信息添加到文件中
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([id, username, password, ip])

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if data['action'] == 'register':
        username = data['username']
        password = data['password']
        ip = request.remote_addr
        add_account(username, password, ip)
        return 'OK', 200
    
def is_ip_close(ip1, ip2):
    # 只比较IPv4地址的前两个数字
    return ip1.split('.')[:2] == ip2.split('.')[:2]

def get_account(username):
    # 从文件中获取账户信息
    with open('accounts.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1] == username:
                return row
    return None

def log_behavior(id, behavior):
    # 在日志文件中记录行为
    with open('log.txt', 'a') as f:
        f.write(f"{datetime.now()}: ID {id} {behavior}\n")


def send_information(url1,data):
    
    # 发送POST请求
    
    response = requests.post(url1, json=data)
    
    # 检查请求是否成功
    if response.status_code == 200:
        print(f"Sent data: {data}")
        log_behavior(0,"sent message to"+url1)
        return 'OK', 200
    else:
        print(f"Failed to send data: {response.status_code}")
        log_behavior(0,"failed sent message to"+url1)
        return 'Failed', 400


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if data['action'] == 'login':
        username = data['username']
        password = data['password']

        ip = request.remote_addr

        account = get_account(username)

        if account and account[2] == password:
            if not is_ip_close(ip, account[3]):
                # 将异常登录信息写入文件
                with open('suspicious_logins.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([username, ip])
                    log_behavior(account[0], "failed login attempt")
            # 创建一个带有ID cookie的响应
            resp = make_response('OK')
            expires = datetime.now()
            expires = expires + timedelta(hours=1)
            resp.set_cookie(key='user_id',value=account[0], expires=expires)
            log_behavior(account[0], "logged in")
            data1=('login','sucessfully')
            send_information(url1,data1)
            print(resp.headers.get('Set-Cookie'))
            return resp #之前漏了一行
        

    data1={'type':'login','status':'failed'}
    print(data1)
    
    send_information(url1,data1)
    return 'OK', 200



if __name__ == '__main__':
    app.run(port=5000)  # 运行服务器
