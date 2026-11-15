import ollama
import yaml
import os
import re
import json
import platform
import subprocess
import psutil
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

#client = ollama.Client()

history_file = "history.yaml"
preferences_file = "preferences.yaml"
model = "qwen:1.8b"

# ---------- TOOLS ----------
def build_apps():
    folders = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"),
    ]
    apps = {}
    for folder in folders:
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(".lnk"):
                    apps[f[:-4].lower()] = os.path.join(root, f)
    return apps

APPS = build_apps()
# built-in Windows apps that have no Start Menu shortcut
APPS.update({"whatsapp": "whatsapp:", "settings": "ms-settings:", "calculator": "calc", "notepad": "notepad", "paint": "mspaint",
             "explorer": "explorer", "cmd": "cmd"})

def open_app(name: str) -> str:
    """Open an app on the PC by name, e.g. notepad, calculator, chrome, spotify."""
    key = name.strip().removesuffix(".exe")
    if key not in APPS:
        matches = [k for k in APPS if key in k]   # partial match: "code" -> "visual studio code"
        if not matches:
            return f"No app found matching {name}"
        key = matches[0]
    os.startfile(APPS[key])
    return f"Opened {key}"

def open_app(name: str) -> str:
    """Open an app on the PC, e.g. notepad, calculator, chrome, vscode."""
    key = name.strip()
    cmd = APPS.get(key, key)
    r = subprocess.run(f'start "" "{cmd}"', shell=True, capture_output=True, text=True)
    return f"Opened {name}" if r.returncode == 0 else f"FAILED to open {name}"

def sys_info() -> str:
    """Get OS, CPU and RAM info of this PC."""
    return json.dumps({
        "os": platform.system(),
        "cpu": platform.processor(),
        "ram_gb": round(psutil.virtual_memory().total / 1e9, 1),
    })
def read_file(path: str) -> str:
    """Read a text file and return its content."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

TOOLS = {f.__name__: f for f in (open_app, sys_info, read_file)}

# ---------- HELPERS ----------
def now() -> str:
    """Get current date and time."""
    return datetime.now().astimezone().strftime("%A, %d %B %Y, %I:%M %p %Z")

def load_system_prompt():
    with open("sys.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

def load_history(history_file):
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                return data
    return [{"role": "system", "content": load_system_prompt()}]

def save_history(history):
    with open(history_file, "w", encoding="utf-8") as f:
        yaml.dump(history, f, allow_unicode=True, sort_keys=False)

def load_preferences(preferences_file):
    if os.path.exists(preferences_file):
        with open(preferences_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                return data
    return {}

def save_preferences(preferences):
    with open(preferences_file, "w", encoding="utf-8") as f:
        yaml.dump(preferences, f, allow_unicode=True, sort_keys=False)

def extract_preferences(user_input, preferences, bot_reply):
    extraction_prompt = f"""
Extract any user preferences, facts, or personal details from this exchange.
Only include things sensitive and worth remembering long-term (name, likes/dislikes, tone preference, etc).
Return ONLY valid YAML, as a flat key: value mapping.
If nothing worth saving, return an empty mapping: {{}}

User: {user_input}
Assistant: {bot_reply}
"""
    result = ollama.chat(model=model, messages=[{"role": "user", "content": extraction_prompt}])
    raw = result["message"]["content"].strip()
    raw = re.sub(r"^```(?:yaml)?\s*|\s*```$", "", raw).strip()
    try:
        if "---" in raw:
            raw = raw.split("---")[-1].strip()
        new_facts = yaml.safe_load(raw)
        if isinstance(new_facts, dict) and new_facts:
            preferences.update(new_facts)
            save_preferences(preferences)
            print(f"[{Fore.CYAN}++Preferences{Style.RESET_ALL}, ({list(new_facts.keys())}).]")
    except yaml.YAMLError as e:
        print(f"[preference parsing error] {e}:{Fore.RED}{raw}{Style.RESET_ALL}")
    return preferences

# ---------- MAIN ----------
history = load_history(history_file)
preferences = load_preferences(preferences_file)
print(f"{Fore.YELLOW}Loaded {len(history)} messages from history{Style.RESET_ALL}")

while True:
    prompt = input(f"{Fore.MAGENTA}You: {Style.RESET_ALL}").strip()
    if prompt.lower() in ('exit', 'quit', 'bye', 'byee'):
        print("have a great day!")
        break

    history[0]["content"] = f"{load_system_prompt()}\n\nKnown facts about the user: {preferences}\n\nCurrent date and time: {now()}"

    history.append({"role": "user", "content": f"[Current time: {now()}]\n{prompt}"})
    print(f"{Fore.MAGENTA}Jarvis: {Style.RESET_ALL}", end="", flush=True)

    # temp copy: tool messages stay here, so history.yaml stays clean
    turn = list(history)
    botmsgcontent = ""

    while True:
        calls = []
        for chunk in ollama.chat(model=model, messages=turn, tools=list(TOOLS.values()), stream=True):
            if chunk.message.content:
                botmsgcontent += chunk.message.content
                print(chunk.message.content, end="", flush=True)
            if chunk.message.tool_calls:
                calls.extend(chunk.message.tool_calls)

        if not calls:          # no tool needed, answer is done
            break

        turn.append({"role": "assistant", "content": "", "tool_calls": calls})
        for call in calls:
            try:
                result = TOOLS[call.function.name](**call.function.arguments)
            except Exception as e:
                result = f"Error: {e}"
            print(f"\n[{Fore.CYAN}tool{Style.RESET_ALL}: {call.function.name} -> {str(result)[:80]}]")
            turn.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})
    print()

    history.append({"role": "assistant", "content": botmsgcontent})
    save_history(history)
    print(f"[{Fore.CYAN}++History{Style.RESET_ALL}, ({len(history)}) messages saved.]")

    preferences = extract_preferences(prompt, preferences, botmsgcontent)