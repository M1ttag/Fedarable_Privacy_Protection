import requests
import getpass
import hashlib
from requests.exceptions import Timeout
import json
import random
response = None 
URL = "http://localhost:5000/"

def send_information_to_server(url, data):
    # url是服务器地址，data是要发送的信息
    url=url+'receive_information'
    response = requests.post(url, json=data)
    return response.status_code, response.text

def send_file_to_server(url, file_path):
    # url是服务器地址，file_path是要发送的文件路径
    url=url+'receive_file'
    with open(file_path, 'rb') as file:
        file_data = file.read()
    response = requests.post(url, files={'file': file_data})
    return response.status_code, response.text


def register(url):
    url=url+'register'
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    # 使用 SHA-256 哈希算法对密码进行加密
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    response = requests.post(url, json={'action': 'register', 'username': username, 'password': password_hash})
    response_code = response.status_code
    response_text = response.text

    if response_code == 200 and response_text == 'OK':
        print("Registration successful")
    else:
        print("Registration failed")


def login(url):
    url=url+'login'
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    global response
    response = requests.post(url, json={'action': 'login', 'username': username, 'password': password_hash})
    
    
    print(response)
    


def DH(p,g,localurl,group_id,num_members,cookies):
 

    # 客户端生成自己的密钥对
    
    private_key = random.randint(1, p)
    partial_key = pow(g, private_key, p)

    # 将部分密钥和组信息发送给服务器


    response = requests.post('http://localhost:5000/send_partial_key',cookies=cookies, json={
        'partial_key': partial_key,
        'group_id': group_id,
        'num_members': num_members,
        'localurl':localurl
    })

    print(f"sent partial key: {response.json()}")
    return private_key


def compute_shared_secret(p, local_private_key):
    # 从名为'DH'的文件中读取部分密钥
    with open('DH.json', 'r') as f:
        other_partial_keys = json.load(f)
    
    shared_secret = 1
    for  client_id, partial_key in other_partial_keys.items():
        # 使用每个客户端的部分密钥来计算共享密钥
        partial_shared_secret = pow(int(partial_key), local_private_key, p)
        shared_secret = (shared_secret * partial_shared_secret) % p
    return shared_secret

def main():
    url = "http://localhost:5000/" #服务器端网址
    localurl = "http://localhost:5001/"#本地网址
    while True:
        print("Please choose an action:")
        print("1. Register")
        print("2. Login")
        print("3. DH")
        print("4. Compute DH")
        print("5. Quit")
        choice = input()

        if choice == '1':
            register(url)
        elif choice == '2':
            login(url)
        elif choice == '3':
            p=int(input('p?'))
            private_key=DH(p,int(input('g?')),localurl+'/DH',int(input('groupid')),int(input('groupnum')),cookies=response.cookies)
        elif choice == '4':
            if private_key==0:
                print("NO private_key")
            else:
                shared_secret = compute_shared_secret(p,private_key)
                print(shared_secret)
        elif choice == '5':
            break
        else:
            print("Invalid choice, please choose again.")

if __name__ == "__main__":
    main()
