import json, os, asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

server_url = "https://mcp.amap.com/mcp?key=8dfe10cc9bd3c54425d469104f3992f8"

class MCPClient:
    def __init__(self):
        self.sessions = []      # 存储服务器的会话及其上下文对象

    # 初始化SSE服务器的连接，并获取可用工具列表
    async def init_session(self):
        # 创建SSE客户端并进入上下文
        streams_context = sse_client(url=server_url)
        # __aenter__()：手动触发异步上下文的入口方法
        streams = await streams_context.__aenter__()
        # 将上一步获取的读写流注入 MCP 会话对象中
        session_context = ClientSession(*streams)
        session = await session_context.__aenter__()
        await session.initialize()
        # 存储会话及其上下文
        self.sessions = [session, session_context, streams_context]
        # 获取工具列表并建立映射
        response = await session.list_tools()
        for tool in response.tools:
          print(tool)
        # 也可以直接调用某个工具
        response = await session.call_tool("maps_weather", {"city": "成都"})
        print(response)
        response = await session.call_tool("maps_geo", {"address": "环球中心","city": "成都"})
        print(response)

    # 清理所有会话和连接资源，确保无资源泄露
    async def cleanup(self):
        # 清空上下文和会话等对象，并断开与服务器的连接
        session, session_context, streams_context = self.sessions
        try:
          await session_context.__aexit__(None, None, None)
          await streams_context.__aexit__(None, None, None)
          await session.__aexit__(None, None, None)
        except:
            pass
        print("所有会话已清理。")

# 异步调用主函数
async def main():
    client = MCPClient()
    await client.init_session()   # 初始化并输出工具列表
    await client.cleanup()        # 调用函数后必须对其进行清理

if __name__ == '__main__':
    asyncio.run(main())