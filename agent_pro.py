import asyncio
import json
import os
import sys
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from ollama import Client as OllamaClient
import requests

# Re-using console from current dashboard/orchestrator style
console = Console()

class AwesomeAICyberProAgent:
    def __init__(self, target: str, model_name="qwen2.5:7b"):
        self.target = target
        self.model_name = model_name
        self.ollama = OllamaClient(host="http://localhost:11434")
        self.memory = [
            {"role": "system", "content": f"""You are a professional security researcher and penetration tester. 
Your target is {target}. You must follow a rigorous methodology:
1. **Knowledge Retrieval**: Query your security knowledge base for information about the target technology or common vulnerabilities.
2. **Action**: Choose and execute the best tool via MCP.
3. **Observation**: Analyze the tool output.
4. **Iterate**: Refine your plan based on findings.

Always provide your 'Thought' before performing an 'Action'.
Action Format: TOOL_NAME({{"param1": "value1"}})
"""}
        ]

    def _think(self, prompt: str) -> str:
        """Get reasoning from the LLM"""
        self.memory.append({"role": "user", "content": prompt})
        response = self.ollama.chat(model=self.model_name, messages=self.memory)
        answer = response['message']['content']
        self.memory.append({"role": "assistant", "content": answer})
        return answer

    def _execute_mcp_tool(self, tool_call_str: str) -> Dict[str, Any]:
        """Parse and execute a tool call string like 'nmap_scan({"target": "..."})'"""
        try:
            # More robust parser to handle extra text after JSON
            name = tool_call_str.split('(')[0]
            start_index = tool_call_str.find('(')
            # Find the matching closing parenthesis for the JSON object
            params_str = ""
            depth = 0
            for i in range(start_index, len(tool_call_str)):
                if tool_call_str[i] == '(': depth += 1
                elif tool_call_str[i] == ')': depth -= 1
                
                if depth == 0 and i > start_index:
                    params_str = tool_call_str[start_index+1:i]
                    break
            
            params = json.loads(params_str)
            
            console.print(f"[bold cyan]Action:[/bold cyan] Executing {name}...")
            
            # Special case for Knowledge tool (Local simulation of MCP bridge)
            if name == "query_security_knowledge":
                 from rag_engine import RAGEngine
                 engine = RAGEngine()
                 return {"success": True, "results": engine.query(params.get("query", ""))}

            # Mapping for standard tools
            # If the tool name contains 'scan' or 'enum', we try to map it to the API endpoint
            tool_path = name.replace('_scan', '').replace('_enum', '').replace('_discovery', '').replace('_test', '')
            
            # Specific mapping for Burp Suite Alternative
            if name == "burpsuite_alternative_scan":
                endpoint = "api/tools/burpsuite-alternative"
            elif "burpsuite" in name:
                endpoint = "api/tools/burpsuite"
            else:
                endpoint = f"api/tools/{tool_path}"
                
            url = f"http://localhost:8888/{endpoint}"
            
            response = requests.post(url, json=params, timeout=300)
            return response.json()
        except Exception as e:
            return {"success": False, "error": f"Failed to execute tool: {str(e)}"}

    async def run(self, goal: str):
        console.print(Panel(f"Target: [bold yellow]{self.target}[/bold yellow]\nGoal: [bold cyan]{goal}[/bold cyan]", title="Awesome-AI-Cyber Pro Agent", border_style="red"))
        
        current_task = goal
        for i in range(5):  # Max 5 iterations for this demo
            console.print(f"\n[bold green]--- Iteration {i+1} ---[/bold green]")
            
            # 1. Thought Phase
            thought = self._think(f"Current Status: {current_task}. What is your thought and next action? Use 'Action: TOOL_NAME(PARAMS)' format.")
            console.print(Panel(Markdown(thought), title="Thought Process", border_style="blue"))
            
            # 2. Action Phase
            if "Action:" in thought:
                action_line = [line for line in thought.split('\n') if "Action:" in line][0]
                tool_call = action_line.split("Action:")[1].strip()
                
                observation = self._execute_mcp_tool(tool_call)
                console.print(Panel(json.dumps(observation, indent=2), title="Observation", border_style="magenta"))
                
                # 3. Update Task with Observation
                current_task = f"Tool {tool_call} returned results. Analyze them and decide next step."
            else:
                console.print("[yellow]No specific action identified. Agent might be done or stuck.[/yellow]")
                break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_pro.py <target>")
        sys.exit(1)
        
    target = sys.argv[1]
    agent = AwesomeAICyberProAgent(target)
    asyncio.run(agent.run("Perform a security assessment focusing on API vulnerabilities."))
