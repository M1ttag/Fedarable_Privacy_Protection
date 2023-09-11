from flask import Flask, request, jsonify
import json

app = Flask(__name__)

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

@app.route('/DH', methods=['POST'])
def recive_keys():
    received_data = request.json  # 这假设你发送的是一个JSON对象
    with open('DH.json', 'w') as f:
        json.dump(received_data, f)
    return 'OK', 200
    
if __name__ == "__main__":
    app.run(port=5001)
