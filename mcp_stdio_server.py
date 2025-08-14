#!/usr/bin/env python3
"""
MCP STDIO Server for Claude Desktop
This server communicates via standard input/output for Claude Desktop integration
"""

import json
import sys
import asyncio
import logging
from typing import Dict, Any
from mcp_server import MCPWebScraperServer

# Configure logging to file (not stdout/stderr which would interfere with MCP)
logging.basicConfig(
    filename='/tmp/mcp_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPStdioServer:
    """STDIO server for MCP protocol"""
    
    def __init__(self):
        self.server = MCPWebScraperServer()
        self.running = True
    
    async def read_request(self) -> Dict:
        """Read a JSON request from stdin"""
        try:
            line = sys.stdin.readline()
            if not line:
                self.running = False
                return None
            
            # Parse JSON-RPC request
            request = json.loads(line.strip())
            logger.info(f"Received request: {request.get('method', 'unknown')}")
            return request
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading request: {e}")
            return None
    
    def send_response(self, response: Dict):
        """Send a JSON response to stdout"""
        try:
            # Add JSON-RPC wrapper
            output = json.dumps(response)
            sys.stdout.write(output + '\n')
            sys.stdout.flush()
            logger.info(f"Sent response: {response.get('result', {}).get('success', 'unknown')}")
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    async def handle_request(self, request: Dict) -> Dict:
        """Handle a JSON-RPC request"""
        
        if not request:
            return None
        
        method = request.get('method', '')
        params = request.get('params', {})
        request_id = request.get('id')
        
        try:
            # Handle different MCP methods
            if method == 'initialize':
                result = {
                    "protocolVersion": "1.0",
                    "serverInfo": self.server.get_server_info(),
                    "capabilities": {
                        "tools": True,
                        "resources": False,
                        "prompts": False
                    }
                }
            
            elif method == 'tools/list':
                tools = []
                for name, info in self.server.tools.items():
                    tools.append({
                        "name": name,
                        "description": info["description"],
                        "inputSchema": {
                            "type": "object",
                            "properties": info["parameters"],
                            "required": [k for k, v in info["parameters"].items() 
                                       if v.get("required", False)]
                        }
                    })
                result = {"tools": tools}
            
            elif method == 'tools/call':
                tool_name = params.get('name')
                tool_params = params.get('arguments', {})
                
                # Call the tool
                tool_result = await self.server.handle_tool_call(tool_name, tool_params)
                
                # Format result for MCP
                if tool_result.get('success'):
                    result = {
                        "toolResult": tool_result.get('content', tool_result)
                    }
                else:
                    result = {
                        "error": {
                            "code": -32603,
                            "message": tool_result.get('error', 'Tool execution failed')
                        }
                    }
            
            elif method == 'shutdown':
                self.running = False
                result = {"success": True}
            
            else:
                # Unknown method
                result = {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            # Create JSON-RPC response
            response = {
                "jsonrpc": "2.0",
                "id": request_id
            }
            
            if "error" in result:
                response["error"] = result["error"]
            else:
                response["result"] = result
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """Main server loop"""
        logger.info("MCP STDIO Server started")
        
        # Send initialization message
        self.send_response({
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {
                "serverInfo": self.server.get_server_info()
            }
        })
        
        while self.running:
            try:
                # Read request
                request = await self.read_request()
                if request is None:
                    break
                
                # Handle request
                response = await self.handle_request(request)
                if response:
                    self.send_response(response)
                
            except KeyboardInterrupt:
                logger.info("Server interrupted")
                break
            except Exception as e:
                logger.error(f"Server error: {e}")
                self.send_response({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {e}"
                    }
                })
        
        logger.info("MCP STDIO Server stopped")

async def main():
    """Main entry point"""
    server = MCPStdioServer()
    await server.run()

if __name__ == "__main__":
    # Run the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)