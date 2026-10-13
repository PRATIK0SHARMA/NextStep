"""Set NEXTSTEP_MCP_TOKEN before running. Optional NEXTSTEP_MCP_URL.
Uses the official client and a real HTTP MCP handshake; never prints the token.
"""
import asyncio
import os
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    token=os.environ.get('NEXTSTEP_MCP_TOKEN')
    if not token:raise SystemExit('Set NEXTSTEP_MCP_TOKEN using the UI MCP connection panel first.')
    url=os.environ.get('NEXTSTEP_MCP_URL','http://127.0.0.1:8000/mcp/')
    async with httpx.AsyncClient(headers={'Authorization':'Bearer '+token},timeout=30,trust_env=False) as http:
        async with streamable_http_client(url,http_client=http) as (read,write,_):
            async with ClientSession(read,write) as session:
                result=await session.initialize()
                print('Negotiated protocol:',result.protocolVersion)
                tools=await session.list_tools()
                print('Tools:',', '.join(t.name for t in tools.tools))
                listed=await session.call_tool('list_requests',{})
                if listed.isError:raise SystemExit('MCP tool call failed')
                print('list_requests executed successfully.')

if __name__=='__main__':asyncio.run(main())
