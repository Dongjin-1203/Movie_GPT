# backend/mcp_servers/tmdb_server.py
import asyncio
import json
import sys
import os
from typing import Any
import httpx

# MCP SDK가 설치되어 있지 않으면 간단한 구현
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    MCP_INSTALLED = True
except ImportError:
    MCP_INSTALLED = False
    print("MCP SDK not installed, using simple stdio implementation", file=sys.stderr)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# 장르 매핑
GENRE_MAP = {
    "스릴러": 53,
    "드라마": 18,
    "코미디": 35,
    "액션": 28,
    "공포": 27,
    "로맨스": 10749,
    "SF": 878,
    "범죄": 80,
    "가족": 10751,
    "애니메이션": 16
}

class SimpleMCPServer:
    """간단한 MCP Server 구현 (stdio 통신)"""
    
    def __init__(self):
        self.tools = self.get_tools()
    
    def get_tools(self):
        """사용 가능한 도구 목록"""
        return [
            {
                "name": "search_movies",
                "description": "TMDB에서 영화 제목으로 검색",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "검색할 영화 제목"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "discover_movies",
                "description": "장르, 년도 등으로 영화 발견",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "genre": {
                            "type": "string",
                            "description": "장르 (스릴러, 드라마, 코미디 등)"
                        },
                        "year": {
                            "type": "integer",
                            "description": "개봉 연도"
                        },
                        "min_rating": {
                            "type": "number",
                            "description": "최소 평점 (0-10)"
                        }
                    }
                }
            },
            {
                "name": "get_movie_details",
                "description": "영화 상세 정보 조회",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "movie_id": {
                            "type": "integer",
                            "description": "TMDB 영화 ID"
                        }
                    },
                    "required": ["movie_id"]
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: dict) -> str:
        """도구 실행"""
        try:
            async with httpx.AsyncClient() as client:
                if name == "search_movies":
                    return await self._search_movies(client, arguments)
                elif name == "discover_movies":
                    return await self._discover_movies(client, arguments)
                elif name == "get_movie_details":
                    return await self._get_movie_details(client, arguments)
                else:
                    return json.dumps({"error": f"Unknown tool: {name}"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _search_movies(self, client: httpx.AsyncClient, args: dict) -> str:
        """영화 검색"""
        response = await client.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": args["query"],
                "language": "ko-KR",
                "page": 1
            }
        )
        data = response.json()
        
        movies = []
        for movie in data.get("results", [])[:5]:
            movies.append({
                "id": movie["id"],
                "title": movie["title"],
                "original_title": movie.get("original_title"),
                "overview": movie.get("overview"),
                "release_date": movie.get("release_date"),
                "vote_average": movie.get("vote_average"),
                "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
            })
        
        return json.dumps({"results": movies, "count": len(movies)})
    
    async def _discover_movies(self, client: httpx.AsyncClient, args: dict) -> str:
        """영화 발견"""
        params = {
            "api_key": TMDB_API_KEY,
            "language": "ko-KR",
            "sort_by": "popularity.desc",
            "page": 1
        }
        
        # 장르 필터
        if args.get("genre"):
            genre_id = GENRE_MAP.get(args["genre"])
            if genre_id:
                params["with_genres"] = genre_id
        
        # 연도 필터
        if args.get("year"):
            params["primary_release_year"] = args["year"]
        
        # 평점 필터
        if args.get("min_rating"):
            params["vote_average.gte"] = args["min_rating"]
        
        response = await client.get(
            f"{TMDB_BASE_URL}/discover/movie",
            params=params
        )
        data = response.json()
        
        movies = []
        for movie in data.get("results", [])[:5]:
            movies.append({
                "id": movie["id"],
                "title": movie["title"],
                "overview": movie.get("overview"),
                "release_date": movie.get("release_date"),
                "vote_average": movie.get("vote_average"),
                "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
            })
        
        return json.dumps({"results": movies, "count": len(movies)})
    
    async def _get_movie_details(self, client: httpx.AsyncClient, args: dict) -> str:
        """영화 상세 정보"""
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/{args['movie_id']}",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR",
                "append_to_response": "credits"
            }
        )
        movie = response.json()
        
        # 감독 추출
        director = None
        if "credits" in movie:
            for crew in movie["credits"].get("crew", []):
                if crew["job"] == "Director":
                    director = crew["name"]
                    break
        
        # 배우 추출
        actors = []
        if "credits" in movie:
            for cast in movie["credits"].get("cast", [])[:5]:
                actors.append(cast["name"])
        
        result = {
            "id": movie["id"],
            "title": movie["title"],
            "overview": movie.get("overview"),
            "release_date": movie.get("release_date"),
            "director": director,
            "actors": actors,
            "genres": [g["name"] for g in movie.get("genres", [])],
            "vote_average": movie.get("vote_average"),
            "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
        }
        
        return json.dumps(result)
    
    async def handle_request(self, request: dict) -> dict:
        """요청 처리 (stdio)"""
        method = request.get("method")
        
        if method == "tools/list":
            return {
                "tools": self.tools
            }
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            result = await self.call_tool(tool_name, arguments)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        else:
            return {"error": f"Unknown method: {method}"}
    
    async def run(self):
        """stdio로 요청 받고 응답"""
        print("MCP Server started (stdio mode)", file=sys.stderr)
        
        while True:
            try:
                # stdin에서 한 줄 읽기 (JSON-RPC 형식)
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                
                # stdout으로 응답
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                error_response = {"error": f"Invalid JSON: {str(e)}"}
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {"error": str(e)}
                print(json.dumps(error_response), flush=True)


async def main():
    """메인 실행"""
    if not TMDB_API_KEY:
        print("ERROR: TMDB_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    server = SimpleMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())