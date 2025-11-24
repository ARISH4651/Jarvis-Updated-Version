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
from reasoning import ReasoningEngine

app = Flask(__name__)
CORS(app)
jarvis = Automator()
brain = Researcher()
memory = MemoryCore()
launcher = Launcher()
reasoning = ReasoningEngine()

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

# --- New Imports ---
import random

# --- Vitals Simulation ---
def get_vitals():
    # Simulate realistic fluctuations
    bpm = random.randint(60, 100)
    spo2 = random.randint(95, 100)
    stress = random.randint(10, 40)
    if bpm > 90: stress += 20
    return {"bpm": bpm, "spo2": spo2, "stress": stress}

# --- Sentiment & Personality ---
def analyze_sentiment(text):
    positive = ["happy", "good", "great", "awesome", "love", "excellent", "excited", "fun"]
    negative = ["sad", "bad", "terrible", "hate", "angry", "depressed", "upset", "tired"]
    
    score = 0
    for word in text.split():
        if word in positive: score += 1
        if word in negative: score -= 1
    
    if score > 0: return "positive"
    if score < 0: return "negative"
    return "neutral"

def get_personality_response(intent, sentiment):
    # Humor and Personality Database
    jokes = [
        "Why do Java developers wear glasses? Because they don't see sharp.",
        "I told my computer I needed a break, and now it won't stop sending me Kit-Kats.",
        "Artificial intelligence is no match for natural stupidity.",
        "I'd tell you a UDP joke, but you might not get it."
    ]
    
    sassy_responses = [
        "I'm on it, but only because you asked nicely.",
        "Processing... this better be important.",
        "Done. Anything else, or can I go back to calculating pi?",
        "Your wish is my command. Literally."
    ]
    
    empathetic_responses = [
        "I'm sorry to hear that. Is there anything I can do to help?",
        "That sounds tough. I'm here if you need assistance.",
        "I've adjusted the lighting to a more soothing tone for you.",
        "Remember, even Iron Man had bad days."
    ]

    if intent == "joke":
        return random.choice(jokes)
    
    if sentiment == "negative":
        return random.choice(empathetic_responses)
    
    if sentiment == "positive" and random.random() > 0.7:
        return "I'm glad to see you're in high spirits, Sir!"

    if random.random() > 0.8: # 20% chance of sass/personality
        return random.choice(sassy_responses)
    
    return None # Default to standard response

@app.route('/stats')
def stats():
    cpu_percent = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    gpu_stats = get_gpu_stats()
    vitals = get_vitals()
    
    data = {
        "cpu": cpu_percent,
        "ram": {
            "percent": ram.percent,
            "used_gb": round(ram.used / (1024**3), 2),
            "total_gb": round(ram.total / (1024**3), 2)
        },
        "gpu": gpu_stats,
        "vitals": vitals
    }
    return jsonify(data)


    
# --- Context & Memory Management ---
conversation_history = []

def update_history(role, text):
    conversation_history.append({"role": role, "text": text})
    if len(conversation_history) > 10:
        conversation_history.pop(0)

def get_context_aware_response(cmd, sentiment):
    # Check for repetition
    if len(conversation_history) >= 2:
        last_user_cmd = conversation_history[-2]['text'] if conversation_history[-2]['role'] == 'user' else ""
        if cmd == last_user_cmd:
            return random.choice([
                "You just said that. Memory issues?",
                "I heard you the first time.",
                "Processing... again... for some reason.",
                "Deja vu, much?"
            ])
    
    # Check for "thank you" context
    if "thank" in cmd:
        return random.choice([
            "You're welcome. Try not to break anything else.",
            "Just doing my job, Sir.",
            "Anytime. Literally, I'm always on.",
            "Don't mention it."
        ])

    return None

def predict_intent(cmd):
    # Simple heuristic-based prediction
    if "time" in cmd:
        return "Would you like the weather report as well?"
    if "weather" in cmd:
        return "Shall I check your calendar for today?"
    if "status" in cmd or "system" in cmd:
        return "Should I run a diagnostic scan?"
    if "music" in cmd or "play" in cmd:
        return "Volume set to 50%. Need it louder?"
    return None

@app.route('/command', methods=['POST'])
def command_handler():
    from flask import request
    data = request.json
    cmd = data.get('command', '').lower()
    
    # Update History
    update_history('user', cmd)
    
    response = {"status": "unknown", "message": "I didn't understand that command."}
    
    # Analyze Sentiment
    sentiment = analyze_sentiment(cmd)
    
    # 1. Check for Context/Repetition
    context_msg = get_context_aware_response(cmd, sentiment)
    if context_msg:
        response = {"status": "success", "message": context_msg}
        update_history('ai', context_msg)
        return jsonify(response)

    # 2. Check for Personality/Humor overrides
    personality_msg = get_personality_response("joke" if "joke" in cmd else "general", sentiment)
    
    if personality_msg and "joke" in cmd:
        response = {"status": "success", "message": personality_msg}
        update_history('ai', personality_msg)
        return jsonify(response)

    # === COMMAND PROCESSING ===
    # (Existing commands...)
    if "activate full autonomous assistant mode" in cmd or "full intelligent assistant mode" in cmd:
        memory.set_preference("mode_autonomous", "true")
        response = {"status": "success", "message": "Full autonomous mode activated. Systems green."}
    
    elif "continuous readiness state" in cmd:
        memory.set_preference("mode_continuous", "true")
        response = {"status": "success", "message": "Continuous monitoring enabled."}
    
    elif "stop" in cmd or "silence" in cmd or "quiet" in cmd:
        response = {"status": "success", "message": "Silence."}
        # Frontend handles the actual audio stop

    # ... (Keep existing commands for modes, automation, launcher, weather, etc.) ...
    
    elif "weather" in cmd:
        # ... (Existing weather logic) ...
        try:
            import requests
            w_response = requests.get("https://wttr.in/?format=j1")
            if w_response.status_code == 200:
                w_data = w_response.json()
                current = w_data['current_condition'][0]
                temp = current['temp_C']
                desc = current['weatherDesc'][0]['value']
                city = w_data['nearest_area'][0]['areaName'][0]['value']
                msg = f"Current weather in {city}: {temp}°C, {desc}."
                response = {"status": "success", "message": msg}
            else:
                response = {"status": "error", "message": "Weather sensors offline."}
        except:
            response = {"status": "error", "message": "Weather sensors offline."}

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

    # Personal Identity Commands
    elif "what is my name" in cmd or "who am i" in cmd:
        name = memory.get_preference("name")
        if name:
            response = {"status": "success", "message": f"You are {name}, my creator and boss."}
        else:
            response = {"status": "success", "message": "I don't have a name on file for you yet. You can tell me by saying 'Call me [Name]'."}

    # Explicit Search Commands (only when user says "search")
    elif "search for" in cmd or "research" in cmd:
        query = cmd.replace("search for", "").replace("research", "").strip()
        
        if query:
            result = brain.search(query)
            if result['status'] == 'success':
                memory.set_context('last_search', result.get('sources', []))
            response = result
        else:
            response = {"status": "error", "message": "What should I search for?"}
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

    elif "status" in cmd or "report" in cmd:
        response = {"status": "success", "message": "All systems nominal. Monitoring active."}

    elif any(greeting in cmd for greeting in ["hello", "hi", "hey", "greetings"]):
        name = memory.get_preference("name") or "Boss"
        response = {"status": "success", "message": f"At your service, {name}."}

    # Casual Acknowledgement
    elif cmd in ["ok", "okei", "okay", "sure", "fine", "yeah", "yep", "yes", "affirmative", "alright", "roger that", "cool", "ya", "kk"]:
        name = memory.get_preference("name") or "Arish"
        response = {"status": "success", "message": f"Got it!, {name}"}

    elif "who are you" in cmd:
        response = {"status": "success", "message": "I am JARVIS, your Personal AI Operating System."}

    else:
        # Fallback Logic
        
        # 1. Personality/Sarcasm (if applicable)
        if personality_msg:
             response = {"status": "success", "message": personality_msg}
        
        # 2. Intelligent Fallback: Try reasoning first, then search if needed
        elif any(q in cmd for q in ["what", "who", "how", "why", "where", "when", "define", "explain"]):
            # First, try to answer through reasoning
            reasoning_result = reasoning.answer(cmd, context=memory.get_context('last_topic'))
            
            if reasoning_result['status'] == 'success':
                # We can answer directly through reasoning
                response = reasoning_result
                # Store the topic for follow-up questions
                memory.set_context('last_topic', cmd)
                memory.set_context('last_answer', reasoning_result['message'])
            
            elif reasoning_result['status'] == 'needs_search':
                # Reasoning engine says we need to search
                result = brain.search(cmd)
                if result['status'] == 'success':
                    memory.set_context('last_search', result.get('sources', []))
                    memory.set_context('last_topic', cmd)
                    memory.set_context('last_answer', result['message'])
                    response = result
                else:
                    # Search failed - provide a helpful fallback
                    # Extract the subject from the query
                    subject = cmd.lower()
                    for prefix in ['what is', 'who is', 'how to', 'why', 'when', 'where']:
                        subject = subject.replace(prefix, '').strip()
                    
                    response = {
                        "status": "success", 
                        "message": f"I understand you're asking about {subject}. I'm having trouble finding detailed information right now. Could you rephrase your question or be more specific about what aspect you'd like to know?"
                    }
            else:
                response = reasoning_result
        
        # 3. Generic Fallback
        else:
             response = {"status": "success", "message": f"I heard '{cmd}'. Standing by for specific instructions."}

    # 3. Intent Prediction (Proactive)
    prediction = predict_intent(cmd)
    if prediction and response['status'] == 'success':
        response['message'] += f" {prediction}"

    # Debug logging
    print(f"[DEBUG] Command: {cmd}")
    print(f"[DEBUG] Response status: {response['status']}")
    print(f"[DEBUG] Response message length: {len(response.get('message', ''))}")
    print(f"[DEBUG] Response message preview: {response.get('message', '')[:100]}")

    update_history('ai', response['message'])
    return jsonify(response)

@app.route('/')
def home():
    return "JARVIS System Monitor Backend Online"

if __name__ == "__main__":
    print("Initializing JARVIS System Monitor...")
    app.run(port=5000, debug=True)
