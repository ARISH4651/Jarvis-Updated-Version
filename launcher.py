import subprocess
import webbrowser
import os
from pathlib import Path

class Launcher:
    def __init__(self):
        # Desktop App Mappings (Windows)
        self.desktop_apps = {
            "vscode": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "vs code": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "code": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "task manager": "taskmgr.exe",
            "command prompt": "cmd.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "settings": "ms-settings:",
            "spotify": r"C:\Users\{username}\AppData\Roaming\Spotify\Spotify.exe",
            "discord": r"C:\Users\{username}\AppData\Local\Discord\Update.exe --processStart Discord.exe",
            "steam": r"C:\Program Files (x86)\Steam\steam.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "outlook": "outlook.exe",
        }
        
        # Website/Web App Mappings
        self.websites = {
            "gmail": "https://mail.google.com",
            "youtube": "https://www.youtube.com",
            "whatsapp": "https://web.whatsapp.com",
            "whatsapp web": "https://web.whatsapp.com",
            "chatgpt": "https://chat.openai.com",
            "github": "https://github.com",
            "figma": "https://www.figma.com",
            "linkedin": "https://www.linkedin.com",
            "stackoverflow": "https://stackoverflow.com",
            "stack overflow": "https://stackoverflow.com",
            "google drive": "https://drive.google.com",
            "drive": "https://drive.google.com",
            "twitter": "https://twitter.com",
            "x": "https://twitter.com",
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "reddit": "https://www.reddit.com",
            "netflix": "https://www.netflix.com",
            "amazon": "https://www.amazon.com",
            "google": "https://www.google.com",
        }
        
        # Bundles (Multiple apps/sites)
        self.bundles = {
            "coding setup": ["vscode", "github", "stackoverflow"],
            "work dashboard": ["gmail", "google drive", "linkedin"],
            "entertainment mode": ["youtube", "spotify", "netflix"],
            "study setup": ["youtube", "google drive", "notepad"],
        }
        
        # Get current username for path substitution
        self.username = os.getlogin()
    
    def launch_desktop_app(self, app_name):
        """Launch a desktop application"""
        app_name = app_name.lower().strip()
        
        if app_name not in self.desktop_apps:
            return {
                "status": "error",
                "message": f"Desktop app '{app_name}' not found in my registry. Would you like me to search for it?"
            }
        
        app_path = self.desktop_apps[app_name]
        
        # Substitute username in path
        app_path = app_path.replace("{username}", self.username)
        
        try:
            # Check if it's a special protocol (like ms-settings:)
            if app_path.startswith("ms-"):
                os.startfile(app_path)
            # Check if file exists
            elif os.path.exists(app_path):
                subprocess.Popen(app_path, shell=True)
            else:
                # Try to run as system command
                subprocess.Popen(app_path, shell=True)
            
            return {
                "status": "success",
                "message": f"Launched {app_name}. Done, Boss."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to launch {app_name}: {str(e)}"
            }
    
    def open_website(self, site_name):
        """Open a website in default browser"""
        site_name = site_name.lower().strip()
        
        if site_name not in self.websites:
            return {
                "status": "error",
                "message": f"Website '{site_name}' not found. Should I search for it instead?"
            }
        
        url = self.websites[site_name]
        
        try:
            webbrowser.open(url)
            return {
                "status": "success",
                "message": f"Opened {site_name}. Done, Boss."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to open {site_name}: {str(e)}"
            }
    
    def launch_bundle(self, bundle_name):
        """Launch a bundle of apps/sites"""
        bundle_name = bundle_name.lower().strip()
        
        if bundle_name not in self.bundles:
            return {
                "status": "error",
                "message": f"Bundle '{bundle_name}' not configured. Available bundles: {', '.join(self.bundles.keys())}"
            }
        
        items = self.bundles[bundle_name]
        results = []
        
        for item in items:
            # Try desktop app first
            if item in self.desktop_apps:
                result = self.launch_desktop_app(item)
            # Then try website
            elif item in self.websites:
                result = self.open_website(item)
            else:
                result = {"status": "error", "message": f"Unknown item: {item}"}
            
            results.append(result)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        return {
            "status": "success",
            "message": f"Launched {bundle_name}: {success_count}/{len(items)} items opened. Done, Boss."
        }
    
    def smart_open(self, target):
        """Smart launcher: tries to determine if target is app, site, or bundle"""
        target = target.lower().strip()
        
        # Check bundles first
        if target in self.bundles:
            return self.launch_bundle(target)
        
        # Check desktop apps
        if target in self.desktop_apps:
            return self.launch_desktop_app(target)
        
        # Check websites
        if target in self.websites:
            return self.open_website(target)
        
        # If both exist, ask user
        in_apps = target in self.desktop_apps
        in_sites = target in self.websites
        
        if in_apps and in_sites:
            return {
                "status": "clarify",
                "message": f"'{target}' exists as both a desktop app and website. Which would you prefer?"
            }
        
        # Not found anywhere
        return {
            "status": "error",
            "message": f"'{target}' not found. I can search for it, or you can teach me where it is."
        }
