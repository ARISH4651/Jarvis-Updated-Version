// JARVIS HUD Frontend Script
// ------------------------------------------------------------
// This file implements the interactive HUD, including visual effects,
// a friendly male‑voice TTS engine, command handling, and system stats.
// ------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    // ------------------- Particle System -------------------
    const canvas = document.getElementById('particles-canvas');
    const ctx = canvas.getContext('2d');
    let particles = [];
    const resizeCanvas = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2;
            this.speedX = (Math.random() - 0.5) * 0.5;
            this.speedY = (Math.random() - 0.5) * 0.5;
            this.opacity = Math.random() * 0.5;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }
        draw() {
            ctx.fillStyle = `rgba(0, 243, 255, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    const initParticles = () => {
        for (let i = 0; i < 50; i++) particles.push(new Particle());
    };
    const animateParticles = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });
        requestAnimationFrame(animateParticles);
    };
    initParticles();
    animateParticles();

    // ------------------- Clock -------------------
    const updateClock = () => {
        const now = new Date();
        document.getElementById('clock').textContent = now.toLocaleTimeString('en-US', { hour12: false });
        const options = { month: 'short', day: 'numeric', weekday: 'long' };
        document.getElementById('date').textContent = now.toLocaleDateString('en-US', options).toUpperCase();
    };
    setInterval(updateClock, 1000);
    updateClock();

    // ------------------- UI Elements -------------------
    const input = document.getElementById('command-input');
    const chatHistory = document.getElementById('chat-history');
    const voiceBtn = document.getElementById('voice-btn');
    const systemOverlay = document.getElementById('system-overlay');
    const notificationZone = document.getElementById('notification-zone');
    const waveform = document.getElementById('voice-waveform');

    // ------------------- Notifications -------------------
    const showNotification = (text) => {
        notificationZone.innerHTML = '';
        const notif = document.createElement('div');
        notif.className = 'notification';
        notif.textContent = `⚠ ${text}`;
        notificationZone.appendChild(notif);
        setTimeout(() => {
            notif.style.opacity = '0';
            setTimeout(() => notif.remove(), 500);
        }, 3000);
    };

    // ------------------- Chat Helper -------------------
    const addMessage = (text, sender) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        msgDiv.textContent = sender === 'ai' ? `JARVIS: ${text}` : `BOSS: ${text}`;
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    };

    // ------------------- TTS (Male Voice) -------------------
    const speak = (text) => {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel(); // Interrupt current speech
        const utterance = new SpeechSynthesisUtterance(text);
        const voices = window.speechSynthesis.getVoices();
        const maleNames = [
            'David', 'Mike', 'Alex', 'Brian', 'James', 'John', 'Robert',
            'William', 'George', 'Mark', 'Paul', 'Tom', 'Richard', 'Daniel',
            'Matthew', 'Andrew', 'Steven', 'Kevin', 'Jason', 'Eric', 'Ryan',
            'Scott', 'Anthony', 'Patrick', 'Benjamin', 'Samuel', 'Gregory',
            'Larry', 'Frank', 'Jonathan', 'Justin', 'Aaron', 'Kyle', 'Dylan',
            'Ethan', 'Jordan', 'Tyler', 'Chad', 'Travis', 'Cameron', 'Derek',
            'Shawn', 'Phillip', 'Neil', 'Gordon', 'Harold', 'Leonard', 'Michael',
            'Victor', 'Wesley', 'Zack', 'Zachary', 'Zane', 'Zeke'
        ];
        // Prefer male English voices; fallback to any English voice.
        const preferred = voices.find(v => maleNames.some(name => v.name.includes(name)) && v.lang.startsWith('en'))
            || voices.find(v => v.lang.startsWith('en'));
        if (preferred) utterance.voice = preferred;
        // Friendly, natural parameters
        utterance.pitch = 1.0;
        utterance.rate = 0.95;
        utterance.volume = 1.0;
        utterance.onstart = () => waveform.classList.add('active');
        utterance.onend = () => waveform.classList.remove('active');
        window.speechSynthesis.speak(utterance);
    };

    const stopSpeaking = () => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            waveform.classList.remove('active');
        }
    };

    // ------------------- Command Handling -------------------
    const handleCommand = async (cmd) => {
        const command = cmd.toLowerCase().trim();

        // Interrupt Handling
        if (command === 'stop' || command === 'silence' || command === 'quiet' || command === 'shut up') {
            stopSpeaking();
            showNotification('AUDIO STOPPED');
            return;
        }

        // System overlay commands
        if (command.includes('show system') || command.includes('system performance') || command.includes('status')) {
            systemOverlay.classList.remove('hidden');
            speak('Displaying system diagnostics.');
            showNotification('SYSTEM OVERLAY ACTIVE');
            return;
        }
        if (command.includes('hide system') || command.includes('close system')) {
            systemOverlay.classList.add('hidden');
            speak('Closing diagnostics.');
            return;
        }

        // Vitals overlay commands
        const vitalsOverlay = document.getElementById('vitals-overlay');
        if (command.includes('show vitals') || command.includes('check vitals') || command.includes('biometrics')) {
            vitalsOverlay.classList.remove('hidden');
            speak('Displaying biometric data.');
            showNotification('VITALS OVERLAY ACTIVE');
            return;
        }
        if (command.includes('hide vitals') || command.includes('close vitals')) {
            vitalsOverlay.classList.add('hidden');
            speak('Closing biometric monitor.');
            return;
        }
        // General commands – forward to backend
        try {
            const response = await fetch('http://localhost:5000/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command })
            });
            const data = await response.json();
            if (data.status === 'success') {
                addMessage(data.message, 'ai');
                speak(data.message);
                if (data.data && Array.isArray(data.data) && data.data.length) {
                    const top = data.data[0];
                    addMessage(`Result: ${top.title}`, 'ai');
                }
            } else {
                addMessage(data.message, 'ai');
                speak(data.message);
            }
        } catch (e) {
            addMessage('Neural Link Offline.', 'ai');
            showNotification('CONNECTION ERROR');
        }
    };

    const sendCommand = () => {
        const text = input.value.trim();
        if (text) {
            addMessage(text, 'user');
            input.value = '';
            handleCommand(text);
        }
    };
    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendCommand(); });

    // ------------------- Voice Recognition (Enhanced) -------------------
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = false; // Set to false for command-based interaction, true for dictation
        recognition.interimResults = true; // Enable real-time feedback

        let isListening = false;

        voiceBtn.addEventListener('click', () => {
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });

        recognition.onstart = () => {
            isListening = true;
            voiceBtn.classList.add('listening');
            showNotification('LISTENING...');
        };

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');

            input.value = transcript;

            // If final result, send command
            if (event.results[0].isFinal) {
                sendCommand();
            }
        };

        recognition.onend = () => {
            isListening = false;
            voiceBtn.classList.remove('listening');
            // Auto-restart if in continuous mode (optional, can be toggled via command)
            // recognition.start(); 
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            isListening = false;
            voiceBtn.classList.remove('listening');
        };
    }

    // ------------------- System Stats -------------------
    const cpuHistory = new Array(20).fill(0);
    const updateGraph = (history, elementId) => {
        const svg = document.getElementById(elementId).parentElement;
        const width = svg.clientWidth;
        const height = svg.clientHeight;
        const step = width / (history.length - 1);
        const points = history.map((val, i) => {
            const x = i * step;
            const y = height - (val / 100) * height;
            return `${x},${y}`;
        }).join(' ');
        document.getElementById(elementId).setAttribute('points', points);
    };
    const getColorClass = (value) => {
        if (value < 50) return 'load-low';
        if (value < 80) return 'load-med';
        return 'load-high';
    };
    const fetchStats = async () => {
        try {
            const response = await fetch('http://localhost:5000/stats');
            const data = await response.json();
            const jitter = (Math.random() - 0.5) * 2;
            const cpuVal = Math.min(100, Math.max(0, data.cpu + jitter));
            // CPU
            const cpuBar = document.getElementById('cpu-bar');
            cpuBar.style.width = `${cpuVal}%`;
            cpuBar.className = `bar ${getColorClass(cpuVal)}`;
            document.getElementById('cpu-val').textContent = `${Math.round(cpuVal)}%`;
            // Graph
            cpuHistory.shift();
            cpuHistory.push(cpuVal);
            updateGraph(cpuHistory, 'cpu-polyline');
            // RAM
            const ramBar = document.getElementById('ram-bar');
            ramBar.style.width = `${data.ram.percent}%`;
            ramBar.className = `bar ${getColorClass(data.ram.percent)}`;
            document.getElementById('ram-val').textContent = `${data.ram.percent}%`;
            // GPU
            if (data.gpu) {
                const gpuBar = document.getElementById('gpu-bar');
                gpuBar.style.width = `${data.gpu.load}%`;
                gpuBar.className = `bar ${getColorClass(data.gpu.load)}`;
                document.getElementById('gpu-val').textContent = `${data.gpu.temperature}°C`;
            }
            // Vitals
            if (data.vitals) {
                document.getElementById('bpm-val').textContent = `${data.vitals.bpm} BPM`;
                document.getElementById('spo2-val').textContent = `${data.vitals.spo2}%`;
                document.getElementById('stress-val').textContent = `${data.vitals.stress}%`;

                document.getElementById('spo2-bar').style.width = `${data.vitals.spo2}%`;
                document.getElementById('stress-bar').style.width = `${data.vitals.stress}%`;
            }
            // Core pulse
            document.getElementById('core-text').textContent = Math.floor(cpuVal);
        } catch (e) {
            // silent fail
        }
    };
    setInterval(fetchStats, 1000);

    // ------------------- Personalized Greeting -------------------
    setTimeout(async () => {
        try {
            const response = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'get user name' })
            });
            const data = await response.json();
            let userName = 'Sir';
            if (data.message && data.message.toLowerCase().includes('arish')) userName = 'Arish';
            const greeting = `Hey ${userName}, what can I do for you today?`;
            showNotification('SYSTEM ONLINE');
            addMessage(greeting, 'ai');
            speak(greeting);
        } catch (e) {
            const greeting = 'Hey Arish, what can I do for you today?';
            showNotification('SYSTEM ONLINE');
            addMessage(greeting, 'ai');
            speak(greeting);
        }
    }, 1000);
});
