import os, requests
from dotenv import load_dotenv

load_dotenv()
def aliyun_search(content):

    print(content)
    url = "http://default-0j40.platform-cn-shanghai.opensearch.aliyuncs.com/v3/openapi/workspaces/default/web-search/ops-web-search-001"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('Aliyun_Search_Key')}"
        }
    # way设为full时表示使用大模型对搜索结果进行评判和过滤；默认值为fast，表示不过滤
    # content_type设为summary时表示对网页内容的文本进行摘要；默认值为snippet，表示简短描述
    data = {
            "query": content, 
            "top_k":3, 
            "way":"full", 
            "content_type":"summary"
            }

    resp = requests.post(url, headers=header, json=data)
    list = resp.json()['result']['search_result']
    return list