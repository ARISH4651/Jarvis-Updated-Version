import time
import psutil
import GPUtil
from flask import Flask, jsonify
from flask_cors import CORS
import threading

from automation import Automator
from research import Researcher
from memory import MemoryCore
from launcher import Launcher

app = Flask(__name__)
CORS(app)
jarvis = Automator()
brain = Researcher()
memory = MemoryCore()
launcher = Launcher()

def get_gpu_stats():
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            return {
                "name": gpu.name,
                "load": gpu.load * 100,
                "memory_used": gpu.memoryUsed,
                "memory_total": gpu.memoryTotal,
                "temperature": gpu.temperature
            }
    except Exception as e:
        return None
    return None

@app.route('/stats')
def stats():
    cpu_percent = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    
    gpu_stats = get_gpu_stats()
    
    data = {
        "cpu": cpu_percent,
        "ram": {
            "percent": ram.percent,
            "used_gb": round(ram.used / (1024**3), 2),
            "total_gb": round(ram.total / (1024**3), 2)
        },
        "gpu": gpu_stats
    }
    return jsonify(data)

@app.route('/command', methods=['POST'])
def command_handler():
    from flask import request
    data = request.json
    cmd = data.get('command', '').lower()
    
    response = {"status": "unknown", "message": "I didn't understand that command."}
    
    # === PERSONALITY MODE ACTIVATION ===
    if "activate full autonomous assistant mode" in cmd or "full intelligent assistant mode" in cmd:
        memory.set_preference("mode_autonomous", "true")
        memory.set_preference("mode_proactive", "true")
        memory.set_preference("mode_voice", "true")
        memory.set_preference("mode_memory", "true")
        memory.set_preference("mode_auto_execute", "true")
        response = {
            "status": "success",
            "message": "Full autonomous mode activated. I am now operating with memory, proactive reasoning, voice-style responses, and task execution. Standing by for directives."
        }
    
    elif "continuous readiness state" in cmd or "remain in continuous" in cmd:
        memory.set_preference("mode_continuous", "true")
        response = {"status": "success", "message": "Continuous monitoring enabled. I will notify you of relevant events."}
    
    elif "think through the task step-by-step" in cmd or "think before responding" in cmd:
        memory.set_preference("mode_reasoning", "true")
        response = {"status": "success", "message": "Step-by-step reasoning mode activated."}
    
    elif "adapt your tone to my mood" in cmd or "interact naturally like a human" in cmd:
        memory.set_preference("mode_human", "true")
        response = {"status": "success", "message": "Human-like interaction mode enabled. I will adapt to your communication style."}
    
    elif "don't wait for instructions" in cmd or "suggest tasks" in cmd:
        memory.set_preference("mode_proactive", "true")
        response = {"status": "success", "message": "Proactive mode engaged. I will suggest optimizations and automations."}
    
    elif "execute it without asking" in cmd or "when a task is clear and safe" in cmd:
        memory.set_preference("mode_auto_execute", "true")
        response = {"status": "success", "message": "Auto-execution enabled. I will proceed with safe tasks autonomously."}
    
    elif "continuously evaluate cpu" in cmd or "optimize your windows system" in cmd:
        memory.set_preference("mode_system_monitor", "true")
        response = {"status": "success", "message": "System optimization mode active. Monitoring hardware and performance."}
    
    elif "respond as if speaking" in cmd or "enter voice mode" in cmd:
        memory.set_preference("mode_voice", "true")
        response = {"status": "success", "message": "Voice mode on. Responses will be brief and conversational."}
    
    elif "remember my preferences" in cmd or "remember my habits" in cmd:
        memory.set_preference("mode_memory", "true")
        response = {"status": "success", "message": "Memory mode activated. I will track your preferences and interaction patterns."}
    
    # Automation Commands
    elif "organize" in cmd and "downloads" in cmd:
        result = jarvis.organize_downloads()
        response = result
    
    # Launcher Commands
    elif any(cmd.startswith(prefix) for prefix in ["open ", "launch ", "start "]):
        # Extract the target
        target = cmd
        for prefix in ["open ", "launch ", "start "]:
            target = target.replace(prefix, "")
        
        target = target.strip()
        
        if target:
            result = launcher.smart_open(target)
            response = result
        else:
            response = {"status": "error", "message": "What should I open?"}
    
    # Weather Command
    elif "weather" in cmd:
        try:
            import requests
            w_response = requests.get("https://wttr.in/?format=j1")
            if w_response.status_code == 200:
                w_data = w_response.json()
                current = w_data['current_condition'][0]
                temp = current['temp_C']
                desc = current['weatherDesc'][0]['value']
                humidity = current['humidity']
                wind = current['windspeedKmph']
                city = w_data['nearest_area'][0]['areaName'][0]['value']
                
                msg = f"Current weather in {city}: {temp}°C, {desc}. Humidity: {humidity}%. Wind: {wind} km/h."
                response = {
                    "status": "success", 
                    "message": msg,
                    "details": {
                        "temp": temp,
                        "condition": desc,
                        "humidity": humidity,
                        "wind": wind,
                        "city": city
                    }
                }
            else:
                response = {"status": "error", "message": "Unable to fetch weather data at this time."}
        except Exception as e:
            response = {"status": "error", "message": "Weather sensors offline."}

    # Capabilities / Help
    elif any(phrase in cmd for phrase in ["what can you do", "what you can do", "what do you do", "help", "capabilities", "what are you capable"]):
        msg = (
            "I am JARVIS, your Personal AI OS. Here are my current protocols:\n"
            "1. Research: Ask 'What is...' or 'Research...'\n"
            "2. System: Say 'Show system performance' or 'Status'\n"
            "3. Automation: Say 'Organize downloads'\n"
            "4. Memory: Say 'Remember that...' or 'Add task...'\n"
            "5. Weather: Ask 'What is the weather?'\n"
            "6. Modes: Say 'Activate full autonomous assistant mode'"
        )
        response = {"status": "success", "message": msg}

    # Research / Search Commands
    elif "search for" in cmd or "research" in cmd or any(cmd.startswith(q) for q in ["what is", "who is", "how to", "define", "tell me about"]):
        query = cmd
        for prefix in ["search for", "research", "what is", "who is", "how to", "define", "tell me about"]:
            query = query.replace(prefix, "")
        
        query = query.strip()
        
        if query:
            result = brain.search(query)
            if result['status'] == 'success':
                # Store sources for context
                memory.set_context('last_search', result.get('sources', []))
            response = result
        else:
            response = {"status": "error", "message": "What should I search for?"}

    # Explanation / Follow-up
    elif "explain" in cmd:
        last_search = memory.get_context('last_search')
        if last_search:
            top_result = last_search[0]
            explanation = f"Based on your last search about '{top_result['title']}', here is a summary: {top_result['snippet']}"
            response = {"status": "success", "message": explanation}
        else:
            response = {"status": "error", "message": "I don't have any recent search results to explain."}

    # Memory Commands
    elif "remember that" in cmd:
        content = cmd.replace("remember that", "").strip()
        memory.set_preference("note", content)
        response = {"status": "success", "message": f"I have stored that in my memory banks: '{content}'"}

    elif "add task" in cmd:
        task = cmd.replace("add task", "").strip()
        memory.add_task(task)
        response = {"status": "success", "message": f"Task added: {task}"}
        
    elif "list tasks" in cmd or "my tasks" in cmd:
        tasks = memory.get_tasks()
        if tasks:
            task_list = "\n".join([f"- {t['description']}" for t in tasks])
            response = {"status": "success", "message": "Here are your pending tasks:", "details": task_list}
        else:
            response = {"status": "success", "message": "You have no pending tasks."}

    # System Status
    elif "status" in cmd or "report" in cmd:
        response = {"status": "success", "message": "All systems nominal. Monitoring active."}
    
    # Conversational / Greetings
    elif any(greeting in cmd for greeting in ["hello", "hi", "hey", "greetings"]) or cmd == "jarvis":
        name = memory.get_preference("name") or "Boss"
        response = {"status": "success", "message": f"Yes, {name}?"}
        
    elif "call me" in cmd:
        name = cmd.split("call me")[-1].strip()
        memory.set_preference("name", name)
        response = {"status": "success", "message": f"Understood. I will call you {name} from now on."}
        
    # Casual Acknowledgement
    elif cmd in ["ok", "okei", "okay", "sure", "fine", "yeah", "yep", "yes", "affirmative", "alright", "roger that", "cool"]:
        response = {"status": "success", "message": "Got it!, Arish"}

    elif "who are you" in cmd:
        response = {"status": "success", "message": "I am JARVIS, your Personal AI Operating System."}
        
    else:
        response = {"status": "success", "message": f"I heard '{cmd}', but I don't have a protocol for that yet."}
    
    return jsonify(response)

@app.route('/')
def home():
    return "JARVIS System Monitor Backend Online"

if __name__ == "__main__":
    print("Initializing JARVIS System Monitor...")
    app.run(port=5000, debug=True)
