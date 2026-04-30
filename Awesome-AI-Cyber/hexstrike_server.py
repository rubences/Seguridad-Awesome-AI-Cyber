from flask import Flask, request, jsonify
import subprocess
import shlex
import os

app = Flask(__name__)

DEFAULT_WORDLISTS = [
    '/usr/share/wordlists/dirb/common.txt',
    '/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt',
    '/usr/share/wordlists/wordlists/common.txt',
]

TOOLS = {
    'nmap': 'nmap',
    'gobuster': 'gobuster',
    'sqlmap': 'sqlmap',
    'nuclei': 'nuclei',
    'nikto': 'nikto',
    'ffuf': 'ffuf',
}


def find_wordlist():
    for path in DEFAULT_WORDLISTS:
        if os.path.exists(path):
            return path
    return None


def run_command(cmd_args, timeout=180):
    try:
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            'success': False,
            'returncode': None,
            'stdout': exc.stdout or '',
            'stderr': f'Timeout expired after {timeout} seconds.',
        }
    except Exception as exc:
        return {
            'success': False,
            'returncode': None,
            'stdout': '',
            'stderr': str(exc),
        }


@app.route('/')
def health_check():
    return jsonify({'status': 'ok', 'service': 'Awesome-AI-Cyber', 'version': '1.0'})


@app.route('/api/tools', methods=['GET'])
def list_tools():
    return jsonify({'available_tools': list(TOOLS.keys())})


@app.route('/api/tools/<tool_name>', methods=['POST'])
def execute_tool(tool_name):
    if tool_name not in TOOLS:
        return jsonify({'success': False, 'error': f'Tool {tool_name} is not supported.'}), 404

    params = request.get_json(force=True, silent=True) or {}
    target = params.get('target') or params.get('url')

    if not target:
        return jsonify({'success': False, 'error': 'Missing required parameter: target or url.'}), 400

    if tool_name == 'nmap':
        scan_type = params.get('scan_type', '-sV -sC')
        ports = params.get('ports')
        cmd = ['nmap'] + shlex.split(scan_type)
        if ports:
            cmd += ['-p', str(ports)]
        cmd.append(target)
    elif tool_name == 'gobuster':
        wordlist = params.get('wordlist') or find_wordlist()
        if not wordlist:
            return jsonify({'success': False, 'error': 'No wordlist found for gobuster.'}), 500
        cmd = ['gobuster', 'dir', '-u', target, '-w', wordlist]
        if params.get('extensions'):
            cmd += ['-e', params['extensions']]
    elif tool_name == 'sqlmap':
        cmd = ['sqlmap', '-u', target, '--batch']
        if params.get('data'):
            cmd += ['--data', params['data']]
        if params.get('level'):
            cmd += ['--level', str(params['level'])]
    elif tool_name == 'nuclei':
        cmd = ['nuclei', '-u', target]
        if params.get('templates'):
            cmd += ['-t', params['templates']]
    elif tool_name == 'nikto':
        cmd = ['nikto', '-h', target]
    elif tool_name == 'ffuf':
        wordlist = params.get('wordlist') or find_wordlist()
        if not wordlist:
            return jsonify({'success': False, 'error': 'No wordlist found for ffuf.'}), 500
        cmd = ['ffuf', '-u', f'{target}/FUZZ', '-w', wordlist]
    elif tool_name == 'httpx':
        cmd = ['httpx', '-u', target]
    elif tool_name == 'paramspider':
        cmd = ['paramspider', '-d', target]
    else:
        return jsonify({'success': False, 'error': f'No command mapping for tool {tool_name}.'}), 500

    result = run_command(cmd)
    return jsonify({'tool': tool_name, 'params': params, **result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
