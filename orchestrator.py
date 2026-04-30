import asyncio
import json
import os
import sys
import requests
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from ollama import Client as OllamaClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuration
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen2.5:7b"
AWESOME_AI_CYBER_PATH = os.path.join(os.getcwd(), "Awesome-AI-Cyber", "hexstrike_mcp.py")

console = Console()

class AwesomeAICyberOrchestrator:
    def __init__(self, target: str):
        self.target = target
        self.ollama = OllamaClient(host=OLLAMA_HOST)
        self.history = [
            {"role": "system", "content": f"You are a professional penetration tester. Your goal is to perform a security assessment on {target}. Use the available tools to gather information, identify vulnerabilities, and generate a report. Be methodical and follow the Recon -> Enum -> Exploit -> Report flow."}
        ]
        self.mcp_session: Optional[ClientSession] = None
        self.tools_info = []

    async def connect_mcp(self):
        """Connect to Awesome-AI-Cyber MCP server via STDIO"""
        if not os.path.exists(AWESOME_AI_CYBER_PATH):
            console.print("[red]Error: Awesome-AI-Cyber MCP file not found.[/red]")
            return False
            
        console.print("[blue]Connecting to Awesome-AI-Cyber MCP Server...[/blue]")
        # For now, we simulate connection to allow demonstration
        return True

    def get_ollama_response(self, prompt: str):
        """Get response from Ollama with tool-calling support"""
        self.history.append({"role": "user", "content": prompt})
        
        try:
            response = self.ollama.chat(
                model=MODEL_NAME,
                messages=self.history,
            )
            content = response['message']['content']
            self.history.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def print_banner(self):
        banner = """
[bold red]██╗  ██╗███████╗██╗  ██╗███████╗████████╗██████╗ ██╗██╗  ██╗███████╗[/bold red]
[bold red]██║  ██║██╔════╝╚██╗██╔╝██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝██╔════╝[/bold red]
[bold red]███████║█████╗   ╚███╔╝ ███████╗   ██║   ██████╔╝██║█████╔╝ █████╗  [/bold red]
[bold red]██╔══██║██╔══╝   ██╔██╗ ╚════██║   ██║   ██╔══██╗██║██╔═██╗ ██╔══╝  [/bold red]
[bold red]██║  ██║███████╗██╔╝ ██╗███████║   ██║   ██║  ██║██║██║  ██╗███████╗[/bold red]
[bold red]╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝[/bold red]
[cyan]AI Orchestrator v1.0 | Powered by Ollama + Awesome-AI-Cyber MCP[/cyan]
        """
        console.print(banner)

    def execute_tool(self, tool_name: str, params: Dict[str, Any]):
        """Execute a tool via Awesome-AI-Cyber API"""
        console.print(f"[bold cyan]Tool Call:[/bold cyan] {tool_name}({json.dumps(params)})")
        
        # Mapping MCP tool names to API endpoints if necessary, or using the generic command executor
        # The Awesome-AI-Cyber server has specific endpoints like /api/tools/nmap
        endpoint = f"api/tools/{tool_name.replace('_scan', '')}"
        url = f"http://127.0.0.1:8888/{endpoint}"
        
        try:
            response = requests.post(url, json=params, timeout=300)
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def start(self):
        self.print_banner()
        console.print(Panel(f"Starting Penetration Test on: [bold yellow]{self.target}[/bold yellow]", border_style="blue"))
        
        # Phase 1: Reconnaissance
        with console.status("[bold green]AI is reasoning about the target...") as status:
            reasoning = self.get_ollama_response(f"I want to perform a penetration test on {self.target}. What is the first step? Provide your reasoning and specify which tool you want to use (e.g., nmap_scan).")
            console.print(Panel(Markdown(reasoning), title="AI Reasoning", border_style="green"))

            # Simple logic to extract tool and params (in a full version we'd use Ollama's tool-calling API)
            if "nmap" in reasoning.lower():
                tool_name = "nmap_scan"
                params = {"target": self.target, "scan_type": "-sV"}
                
                console.print(f"[bold magenta]AI Decision:[/bold magenta] Execute {tool_name}")
                result = self.execute_tool(tool_name, params)
                
                # Feed back to AI
                follow_up = self.get_ollama_response(f"The result of {tool_name} was: {json.dumps(result)}. Analyze this and tell me the next move.")
                console.print(Panel(Markdown(follow_up), title="AI Reasoning: Next Step", border_style="green"))

        console.print("[bold green]Phase completed.[/bold green]")
        console.print(f"Check [bold cyan]dashboard.html[/bold cyan] for real-time visualization.")

async def main():
    if len(sys.argv) < 2:
        console.print("[red]Usage: python orchestrator.py <target>[/red]")
        return
    
    target = sys.argv[1]
    orchestrator = AwesomeAICyberOrchestrator(target)
    await orchestrator.start()

if __name__ == "__main__":
    asyncio.run(main())
