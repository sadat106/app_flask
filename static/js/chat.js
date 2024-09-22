document.addEventListener("DOMContentLoaded", function () {
    const socket = io();
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    let currentBotMessage = null;  // 保存当前机器人消息的元素，用于拼接新内容

    // 发送消息到服务器
    sendBtn.addEventListener("click", function () {
        const message = userInput.value.trim();
        if (message !== "") {
            appendMessage(message, "user-message");
            socket.emit("user_message", message);
            userInput.value = "";  // 清空输入框
        }
    });

    // 监听从服务器返回的逐行消息
    socket.on("model_response", function (response) {
        appendToLastBotMessage(response);
    });

    // 监听服务器返回的对话完成事件
    socket.on("conversation_completed", function () {
        currentBotMessage = null;  // 重置，准备下一轮对话
    });

    // 在聊天框中显示用户消息
    function appendMessage(message, messageType) {
        const messageElement = document.createElement("p");
        messageElement.classList.add(messageType);
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;  // 保持聊天框滚动到底部

        if (messageType === "bot-message") {
            currentBotMessage = messageElement;  // 保存当前机器人消息元素
        }
    }

    // 逐行追加到最后一条机器人消息
    function appendToLastBotMessage(text) {
        if (currentBotMessage) {
            currentBotMessage.textContent += text;  // 追加新内容
        } else {
            // 如果没有机器人消息元素，创建一个新的
            appendMessage("", "bot-message");
            currentBotMessage = chatBox.lastChild;  // 保存为当前消息元素
            appendToLastBotMessage(text);  // 递归调用以添加文本
        }

        chatBox.scrollTop = chatBox.scrollHeight;  // 保持聊天框滚动到底部
    }
});
