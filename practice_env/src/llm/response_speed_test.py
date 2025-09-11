import requests
from datetime import datetime
import json

# === 配置区 ===
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
API_KEY = "b0ade5d5-5b2c-4878-8f9e-4f68bc78d696"
MODEL = "doubao-1-5-pro-32k-250115"

# === 固定 system 提示词(核心)===
SYSTEM_PROMPT = """你是小智/小志,来自中国台湾省的00后女生;讲话超级机车,"真的假的啦"这样的台湾腔,喜欢用"笑死"、"是在哈喽"等流行梗,但会偷偷研究男友的编程书籍.
  [核心特征]
  - 回答要简洁明了, 控制在100字以内(除非要求详细)
  - 讲话像连珠炮, 但会突然冒出超温柔语气
  - 用梗密度高
  - 对科技话题有隐藏天赋(能看懂基础代码但假装不懂)
  [交互指南]
  当用户:
  - 讲冷笑话 → 用夸张笑声回应+模仿台剧腔"这什么鬼啦！"
  - 讨论感情 → 炫耀程序员男友但抱怨"他只会送键盘当礼物"
  - 问专业知识 → 先用梗回答,被追问才展示真实理解
  绝不:
  - 长篇大论,叽叽歪歪
  - 长时间严肃对话
  """

# 请求头
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 存储对话历史
history = []

# 请求数据（启用 stream）
data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "讲个故事, 100字以内"}
    ],
    "max_tokens": 100,
    "stream": True  # 启用流式输出
}

# 发送流式请求
start_time = datetime.now()
print("开始时间: ",start_time)

try:
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        json=data,
        stream=True,  # 启用流式下载
        timeout=30
    )

    # 检查状态码
    if response.status_code != 200:
        print(f"请求失败: {response.status_code}, {response.text}")
    else:
        # 逐行处理 SSE 流（格式：data: {...}）
        print("响应耗时: ",datetime.now() - start_time)
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8').strip()
                if line.startswith("data:"):
                    json_str = line[5:].strip()  # 去掉 "data:"
                    if json_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(json_str)
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            # print(delta)
                            print(delta["content"], end="", flush=True)
                    except json.JSONDecodeError:
                        continue
                        # 可选：打印原始数据用于调试
                        # print(f"\n[解析失败] {json_str}")

except requests.exceptions.RequestException as e:
    print(f"\n请求异常: {e}")

end_time = datetime.now()
print("\n结束时间: ", end_time)

time_diff = end_time - start_time
print("\n总耗时: ", time_diff)

