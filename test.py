import json

import requests, os
from dotenv import load_dotenv
load_dotenv()

url = "http://default-0j40.platform-cn-shanghai.opensearch.aliyuncs.com/v3/openapi/workspaces/default/web-search/ops-web-search-001"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('Aliyun_Search_Key')}"
    }
data = {"query": "成都明天的天气情况", "top_k":3}   # top_k表示返回的搜索结果数量

resp = requests.post(url, headers=header, json=data)
list = resp.json()['result']['search_result']
# print(list)

contents = [item['content'] for item in list]
result = '\n'.join(contents)
print(result)

# print("HTTP Status Code:", resp.status_code)

# # 2. 尝试将返回结果美化打印 (indent=2 可以让缩进对齐，极方便查看层级结构)
# try:
#     res_json = resp.json()
#     print(res_json)
#     print("========== 接口返回的完整 JSON 数据 ==========")
#     print(json.dumps(res_json, ensure_ascii=False, indent=2))
#     print("============================================")
# except Exception as e:
#     print("返回内容非标准 JSON，原始文本为:", resp.text)