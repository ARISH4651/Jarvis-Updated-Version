document.addEventListener('DOMContentLoaded', () => {
    // --- PARTICLE SYSTEM ---
    const canvas = document.getElementById('particles-canvas');
    const ctx = canvas.getContext('2d');
    let particles = [];

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
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

    function initParticles() {
        for (let i = 0; i < 50; i++) {
            particles.push(new Particle());
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        requestAnimationFrame(animateParticles);
    }
    initParticles();
    animateParticles();

    // --- CLOCK ---
    function updateClock() {
        const now = new Date();
        document.getElementById('clock').textContent = now.toLocaleTimeString('en-US', { hour12: false });
        const options = { month: 'short', day: 'numeric', weekday: 'long' };
        document.getElementById('date').textContent = now.toLocaleDateString('en-US', options).toUpperCase();
    }
    setInterval(updateClock, 1000);
    updateClock();

    // --- UI ELEMENTS ---
    const input = document.getElementById('command-input');
    const sendBtn = document.getElementById('send-btn');
    const chatHistory = document.getElementById('chat-history');
    const voiceBtn = document.getElementById('voice-btn');
    const systemOverlay = document.getElementById('system-overlay');
    const notificationZone = document.getElementById('notification-zone');
    const waveform = document.getElementById('voice-waveform');

    // --- NOTIFICATIONS ---
    function showNotification(text) {
        notificationZone.innerHTML = '';
        const notif = document.createElement('div');
        notif.className = 'notification';
        notif.textContent = `⚠ ${text}`;
        notificationZone.appendChild(notif);
        setTimeout(() => {
            notif.style.opacity = '0';
            setTimeout(() => notif.remove(), 500);
        }, 3000);
    }

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        msgDiv.textContent = sender === 'ai' ? `JARVIS: ${text}` : `BOSS: ${text}`;
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // --- TTS & VOICE VISUALIZER ---
    function speak(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            const voices = window.speechSynthesis.getVoices();
            const preferredVoice = voices.find(v => v.name.includes("David") || v.lang === "en-US");
            if (preferredVoice) utterance.voice = preferredVoice;

            utterance.onstart = () => waveform.classList.add('active');
            utterance.onend = () => waveform.classList.remove('active');

            window.speechSynthesis.speak(utterance);
        }
    }

    // --- COMMAND HANDLING ---
    async function handleCommand(cmd) {
        const command = cmd.toLowerCase().trim();

        if (command.includes("show system") || command.includes("system performance") || command.includes("status")) {
            systemOverlay.classList.remove('hidden');
            speak("Displaying system diagnostics.");
            showNotification("SYSTEM OVERLAY ACTIVE");
            return;
        }
        if (command.includes("hide system") || command.includes("close system")) {
            systemOverlay.classList.add('hidden');
            speak("Closing diagnostics.");
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: command })
            });
            const data = await response.json();

            if (data.status === 'success') {
                addMessage(data.message, 'ai');
                speak(data.message);
                if (data.data && Array.isArray(data.data)) {
                    const top = data.data[0];
                    addMessage(`Result: ${top.title}`, 'ai');
                }
            } else {
                addMessage(data.message, 'ai');
                speak(data.message);
            }
        } catch (error) {
            addMessage("Neural Link Offline.", 'ai');
            showNotification("CONNECTION ERROR");
        }
    }

    function sendCommand() {
        const text = input.value.trim();
        if (text) {
            addMessage(text, 'user');
            input.value = '';
            handleCommand(text);
        }
    }

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendCommand();
    });

    // --- VOICE RECOGNITION ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';

        voiceBtn.addEventListener('click', () => {
            recognition.start();
            voiceBtn.classList.add('listening');
            showNotification("LISTENING...");
        });

        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            input.value = text;
            voiceBtn.classList.remove('listening');
            sendCommand();
        };

        recognition.onend = () => {
            voiceBtn.classList.remove('listening');
        };
    }

    // --- SYSTEM STATS & GRAPHS ---
    const cpuHistory = new Array(20).fill(0);

    function updateGraph(history, elementId) {
        const svg = document.getElementById(elementId).parentElement;
        const width = svg.clientWidth;
        const height = svg.clientHeight;
        const step = width / (history.length - 1);

        const points = history.map((val, i) => {
            const x = i * step;
            const y = height - (val / 100 * height);
            return `${x},${y}`;
        }).join(' ');

        document.getElementById(elementId).setAttribute('points', points);
    }

    function getColorClass(value) {
        if (value < 50) return 'load-low';
        if (value < 80) return 'load-med';
        return 'load-high';
    }

    async function fetchStats() {
        try {
            const response = await fetch('http://localhost:5000/stats');
            const data = await response.json();

            // Jitter effect for realism
            const jitter = (Math.random() - 0.5) * 2;
            const cpuVal = Math.min(100, Math.max(0, data.cpu + jitter));

            // Update CPU
            const cpuBar = document.getElementById('cpu-bar');
            cpuBar.style.width = `${cpuVal}%`;
            cpuBar.className = `bar ${getColorClass(cpuVal)}`;
            document.getElementById('cpu-val').textContent = `${Math.round(cpuVal)}%`;

            // Update Graph
            cpuHistory.shift();
            cpuHistory.push(cpuVal);
            updateGraph(cpuHistory, 'cpu-polyline');

            // Update RAM
            const ramBar = document.getElementById('ram-bar');
            ramBar.style.width = `${data.ram.percent}%`;
            ramBar.className = `bar ${getColorClass(data.ram.percent)}`;
            document.getElementById('ram-val').textContent = `${data.ram.percent}%`;

            // Update GPU
            if (data.gpu) {
                const gpuBar = document.getElementById('gpu-bar');
                gpuBar.style.width = `${data.gpu.load}%`;
                gpuBar.className = `bar ${getColorClass(data.gpu.load)}`;
                document.getElementById('gpu-val').textContent = `${data.gpu.temperature}°C`;
            }

            // Core Pulse
            document.getElementById('core-text').textContent = Math.floor(cpuVal);

        } catch (e) {
            // Silent fail
        }
    }
    setInterval(fetchStats, 1000); // Faster polling for smooth graph

    setTimeout(() => {
        showNotification("SYSTEM ONLINE");
        speak("Systems initialized.");
    }, 1000);
});
