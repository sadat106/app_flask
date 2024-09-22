from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pat_JBOz0Y36yCN3FvmNahMFOPNDWqLTYIBK8vz5J2Is0qEnhYKzEb6Ms5fFTMvv5EhU'
socketio = SocketIO(app)

# 假设的字节扣子API URL
BYTE_BUTTON_API_URL = "https://api.coze.cn/v3/chat"
BOT_ID = "7416706593401651240"  # 你的 bot_id
API_KEY = "pat_JBOz0Y36yCN3FvmNahMFOPNDWqLTYIBK8vz5J2Is0qEnhYKzEb6Ms5fFTMvv5EhU"  # 如果需要授权
USER_ID = "123456789"  # 用户 ID，可以动态生成或从前端传递

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('user_message')
def handle_user_message(message):
    # 构建请求数据，根据用户输入来生成additional_messages
    request_data = {
        "bot_id": BOT_ID,
        "user_id": USER_ID,
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": message,
                "content_type": "text"
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",  # 假设需要API_KEY认证
        "Content-Type": "application/json"
    }

    # 发送请求到字节扣子API并获取流式响应
    try:
        # 发送请求到字节扣子API并获取流式响应
        with requests.post(BYTE_BUTTON_API_URL, json=request_data, headers=headers, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    # 解析事件类型和数据
                    decoded_line = line.decode('utf-8')

                    if decoded_line.startswith("event:conversation.message.completed"):
                        emit('conversation_completed')
                        break

                    # 每行可能以 "event: ..." 开头，找到 "data:" 并解析其后的 JSON
                    if decoded_line.startswith("data:"):
                        event_data = decoded_line[5:].strip()  # 去掉 "data:" 前缀并清理空格

                        try:
                            # 解析为JSON
                            response_data = json.loads(event_data)

                            # 处理特定事件类型
                            if "content" in response_data and response_data["role"] == "assistant":
                                # 获取部分生成内容
                                response_text = response_data["content"]
                                # 发送部分结果到前端
                                emit('model_response', response_text)

                            # 处理完成事件，标志会话结束
                            if response_data.get("status") == "completed":
                                emit('model_response', "[会话已完成]")
                                break
                        except json.JSONDecodeError:
                            print("无法解析的JSON数据:", event_data)
    except requests.RequestException as e:
        print("请求出现错误:", e)

if __name__ == '__main__':
    socketio.run(app, debug=True)

