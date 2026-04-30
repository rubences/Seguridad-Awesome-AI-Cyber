import requests
import json
import sys
import argparse
from typing import Dict, Any

# Configuration
AWESOME_AI_CYBER_API = "http://localhost:8888"

def list_tools():
    """List common Awesome-AI-Cyber tools available via API"""
    tools = [
        "nmap", "gobuster", "sqlmap", "nuclei", "nikto", 
        "burpsuite", "burpsuite-alternative", "httpx", 
        "paramspider", "ffuf", "dirsearch"
    ]
    print("\n[bold]Available Awesome-AI-Cyber Tools (Common):[/bold]")
    for tool in tools:
        print(f" - {tool}")
    print("\n[info]Note: Awesome-AI-Cyber supports 150+ tools via generic command execution.[/info]")

def call_tool(tool_name: str, params: Dict[str, Any]):
    """Execute a tool via Awesome-AI-Cyber API"""
    endpoint = f"api/tools/{tool_name}"
    url = f"{AWESOME_AI_CYBER_API}/{endpoint}"
    
    print(f"[*] Invoking {tool_name} on {AWESOME_AI_CYBER_API}...")
    try:
        response = requests.post(url, json=params, timeout=300)
        result = response.json()
        print("\n[+] Response received:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"[!] Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Manual Awesome-AI-Cyber Tool Invocation")
    parser.add_argument("tool", nargs="?", help="Tool name to invoke")
    parser.add_argument("--params", help="JSON string with tool parameters")
    parser.add_argument("--list", action="store_true", help="List available tools")

    args = parser.parse_args()

    if args.list or not args.tool:
        list_tools()
        return

    params = {}
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError:
            print("[!] Error: Invalid JSON in --params")
            return
    
    call_tool(args.tool, params)

if __name__ == "__main__":
    main()
