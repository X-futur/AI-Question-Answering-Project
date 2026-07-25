let switch_voice = false;   // 全局变量，记录朗读状态（false: 未朗读，true: 正在朗读）
const synth = window.speechSynthesis;  // 调用浏览器原生 Web Speech API 的语音合成接口

// 执行朗读核心函数
function speak(content) {
    let utterance = new SpeechSynthesisUtterance(content); // 创建语音实例
    utterance.lang = 'zh-CN';     // 设置语言为中文
    utterance.volume = 1;         // 音量 (0 ~ 1)
    utterance.rate = 1;            // 语速 (0.1 ~ 10)
    synth.cancel();                // 强制清空之前尚未朗读完的语音队列（停止前一段朗读）
    synth.speak(utterance);       // 开始朗读
}

// 朗读/停止状态切换函数
function readText(obj) {
    let chatbox = document.getElementById('chatbox');
    if (switch_voice) {    // 如果正在播放，点击后切换为关闭
        obj.innerText = '朗读';
        switch_voice = false;
        synth.cancel();   // 停止朗读
    } else {               // 如果未播放，点击后切换为开始
        obj.innerText = '停止';
        switch_voice = true;
        synth.cancel();

        // 核心技巧：从父容器（answer-box）中提取文本
        // 因为“朗读”按钮本身在 answer-box 内部，通过 split("<button")[0] 把按钮本身的标签剥离掉，只保留 AI 回复的纯文本
        let content = obj.parentNode.innerHTML.split("<button")[0];
        if (content) {
            speak(content);
        }
    }
}

// 监听键盘按键：按下 Ctrl + Enter 快速提交提问
function doEnter(e) {
    if (e.key == "Enter" && e.ctrlKey) {
        doAsk();
    }
}

// 保持聊天框滚动条一直在最底部
function scrollToBottom() {
    var chatbox = document.getElementById('chatbox');
    // 距离顶部的高度等于滚动条高度
    chatbox.scrollTop = chatbox.scrollHeight;
}

// 创建提问的DIV并将问题内容添加进来
function doAsk() {
    let ask = document.createElement('div');
    ask.setAttribute("class", "ask-box"); // 赋予用户气泡框样式
    ask.innerHTML = document.getElementById("question").value; // 填入输入框的内容

    document.getElementById("chatbox").append(ask); // 插入到聊天主界面中
    scrollToBottom();   // 滚动到底部展示新气泡
    doAnswer();         // 触发 AI 回复逻辑
}

function doAnswer() {
    // 1. 先在聊天框里预创建一个空的 AI 答复气泡
    let answer = document.createElement('div');
    answer.setAttribute("class", "answer-box");
    document.getElementById("chatbox").append(answer);

    let content = document.getElementById("question").value;
    params = { "content": content, "search": false };

    // 2. 发送 POST 请求连接后端的 /stream 接口
    fetch("/stream", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    }).then(async result => {
        // 3. 获取 ReadableStream 流式读取器与解码器
        const reader = result.body.getReader();
        const textDecoder = new TextDecoder("utf-8");

        // 4. 开启无限循环持续从流中读取数据包（chunk）
        while (true) {
            const { done, value } = await reader.read();

            // 如果后端流数据传输完毕（EOF）
            if (done) {
                // 在气泡结尾追加“朗读”按钮，并滚动到底部后结束函数
                answer.innerHTML += "<button onclick='readText(this)' class='read-button' id='speak'>朗读</button>";
                scrollToBottom();
                return;
            }

            // 5. 将二进制数据解码并按 \n 拆分成单独的 JSON 字符串数组
            let jsonList = textDecoder.decode(value).split("\n");

            // 6. 遍历拆分出的 JSON 数据并追加到页面中（打字机效果）
            for (let i = 0; i < jsonList.length - 1; i++) {
                jsonObj = JSON.parse(jsonList[i]);
                // 将 \n 转换为 <br/> 以便在 HTML 中正确实现换行
                answer.innerHTML += jsonObj['content'].replaceAll("\n", "<br/>");
            }
        }
    });
}