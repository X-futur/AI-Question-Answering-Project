let switch_voice = false;   // 全局变量，记录朗读状态（false: 未朗读，true: 正在朗读）
const synth = window.speechSynthesis;  // 调用浏览器原生 Web Speech API 的语音合成接口
sessionStorage.clear();   // 每次刷新界面时均将之前的内容清空，以进行全局调用

// 执行朗读核心函数
function speak(content) {
    // 利用浏览器自带的语音合成接口
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

// 此处进行判断，如果用户上传了图像，则说明要使用图像识别功能，否则要使用文本问答功能
function doAsk() {
    let content = document.getElementById("question").value;
    if (!content) {
        alert("提示语不能为空")
        return
    }

    // 创建一个提问的DIV元素，并设置其class属性为ask-box，以匹配CSS
    let ask = document.createElement('div');
    ask.setAttribute("class", "ask-box");

    // 如果sessionStorage的内容不为空，则将图像添加到提问框中
    if (sessionStorage.getItem("image")) {
        ask.innerHTML = '<img src="' + sessionStorage.getItem("image")
            + '" style="width:100%"><br/>' + question.value;
        document.getElementById("chatbox").append(ask);
        scrollToBottom();
        recognizeImage();
    }
    else {
        ask.innerHTML = document.getElementById("question").value;
        // 将该DIV元素添加到chatbox提问框DIV中作为一个子元素
        document.getElementById("chatbox").append(ask);
        scrollToBottom();
        doAnswer();
    }
}

// 文本回复
function doAnswer() {

    let content = document.getElementById("question").value;
    if (!content) {
        alert("提示语不能为空")
        return
    }
    // params = { "content": content, "search": false };

    // 1. 先在聊天框里预创建一个空的 AI 答复气泡
    let answer = document.createElement('div');
    answer.setAttribute("class", "answer-box");
    document.getElementById("chatbox").append(answer);

    // 引入联网搜索功能
    let checkbox = document.getElementById("net-search");
    if (checkbox.checked) {
        params = { "content": content, "search": true }
    }
    else {
        params = { "content": content, "search": false }
    }

    // 2. 发送 POST 请求连接后端的 /stream 接口
    // 后端注册路由之后就可以在这里fetch发送请求使用路由接口了
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

function addImage() {
    // 看似点击button，实则点击input，调用上传框上传图像
    document.getElementById('imageInput').click();
}

// 保存图像到sessionStorage中并进行预览显示
// 把input框显示出来，焦点放在input question框里
function saveAndPreview() {
    // console.log("调用了saveandpreview函数")
    // 获取文件上传框元素
    var input = document.getElementById('imageInput');
    // 判断是否有文件，如果有，则进行以下操作
    // input.files检查是否浏览器支持input，input.files[0]检查是否真的有文件
    // console.log("input.files:", input.files)
    // console.log("input.files[0]:", input.files[0])

    if (input.files && input.files[0]) {
        // 使用FileReader()读取文件流，并响应onload事件
        var reader = new FileReader();
        reader.onload = function (e) {
            console.log(e)

            var img = document.getElementById('preview');
            img.src = e.target.result;   // 获取Base64编码
            img.style.display = 'block';  // 显示预览的DIV元素

            // // 缩小userask文本域的宽度，以显示预览图
            document.getElementById('question').style.width = '450px';
            document.getElementById('imageDiv').style.display = 'block';

            // // 将图像数据存储到sessionStorage中
            sessionStorage.clear();  // 清空之前的内容，确保只有一张图像被保存
            sessionStorage.setItem('image', e.target.result);  // 新加入一条

            // // 将焦点放置到输入框中，并提供默认的提示词
            var question = document.getElementById("question");
            question.focus();
            // // 为了让用户少一些输入，提前预置一段提示词
            question.value = "请识别图像中的内容，覆盖尽可能多的信息，描述尽量简洁明了。";
        }
        reader.readAsDataURL(input.files[0]);
    }
}

// 图像识别的前后端对接
function recognizeImage() {
    let answer = document.createElement('div');
    let question = document.getElementById("question");

    let ask = document.createElement('div');
    ask.setAttribute("class", "ask-box");

    // 直接以Base64编码方式上传图像到后台
    let params = { "base64": sessionStorage.getItem("image"), "content": question.value }
    answer.setAttribute("class", "answer-box");
    document.getElementById("chatbox").append(answer);

    fetch("/recognize", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    }).then(async result => {
        const reader = result.body.getReader();
        const textDecoder = new TextDecoder("utf-8");
        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                answer.innerHTML += "<button  onclick='readText(this)'  class='read-button' id='speak'>朗读</button>";
                scrollToBottom();
                return
            }
            let jsonList = textDecoder.decode(value).split("\n");
            console.log("jsonlist:", jsonList)
            for (let i = 0; i < jsonList.length - 1; i++) {
                jsonObj = JSON.parse(jsonList[i]);
                answer.innerHTML += jsonObj['content'].replaceAll("\n", "<br/>");
            }
        }
    });

    // 删除sessionStorage中的内容，并隐藏预览框，还原到初始状态
    sessionStorage.clear();
    document.getElementById("imageDiv").style.display = "none";
    document.getElementById("question").style.width = "560px";
}


// 图像生成的前端代码对接与渲染
// 生图按钮直接相当于是“智能回答”按钮
function generateImage() {
    let ask = document.createElement('div');
    ask.setAttribute("class", "ask-box");

    let question = document.getElementById("question")
    if (!question.value) {
        alert("提示语不能为空")
        return
    }
    // question.value = "默认提示语：一位年轻女性，自然随性的自拍风格，超高清写实人物生活照。她身着黄色碎花长袖上衣，长发自然垂落且略带波浪卷。画面背景为户外自然景色，近处有绿植，远处可见水域和山峦。自然柔和的阳光洒在人物脸上和身上，形成自然的光影效果，拍摄机位为人物手持设备的中景自拍视角，人物身体自然站立，展现出轻松自在的状态。角度自然，随手一拍的快照风格，不经意间的抓拍。"
    ask.innerHTML = document.getElementById("question").value;

    document.getElementById("chatbox").append(ask);
    scrollToBottom();

    let answer = document.createElement('div');
    answer.setAttribute("class", "answer-box");

    fetch("/generate", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "content": document.getElementById("question").value })
    }).then(result => {
        // 解析响应头，把数据转为json
        return result.json();
    }).then(data => {
        // 拿到上一个then的json数据，取出image的url
        let url = data['image_url'];
        // 将图像渲染到回复框中
        answer.innerHTML = "<img src='" + url + "' style='width: 100%'/>";
        document.getElementById("chatbox").append(answer);
        scrollToBottom();
    });
}