# backend/app/services/mcp_client.py
import asyncio
import json
import subprocess
import os
from typing import Any, Dict, List


class MCPClient:
    """MCP Server와 통신하는 클라이언트"""
    
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.process = None
    
    async def start(self):
        """MCP Server 프로세스 시작"""
        env = os.environ.copy()
        
        self.process = await asyncio.create_subprocess_exec(
            "python", self.server_script_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        print("MCP Server started")
    
    async def stop(self):
        """MCP Server 종료"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("MCP Server stopped")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """MCP Tool 호출"""
        if not self.process:
            await self.start()
        
        # JSON-RPC 요청 생성
        request = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # 요청 전송
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # 응답 읽기
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())
        
        # 결과 추출
        if "content" in response:
            return response["content"][0]["text"]
        elif "error" in response:
            raise Exception(response["error"])
        else:
            raise Exception("Invalid response from MCP server")
    
    async def list_tools(self) -> List[Dict]:
        """사용 가능한 도구 목록"""
        if not self.process:
            await self.start()
        
        request = {"method": "tools/list"}
        request_json = json.dumps(request) + "\n"
        
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())
        
        return response.get("tools", [])


# 싱글톤 인스턴스
_mcp_client = None

def get_mcp_client() -> MCPClient:
    """MCP Client 싱글톤"""
    global _mcp_client
    if _mcp_client is None:
        script_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..",
            "mcp_servers", "tmdb_server.py"
        )
        _mcp_client = MCPClient(script_path)
    return _mcp_client