import os
import shutil
from datetime import datetime

class Automator:
    def __init__(self):
        self.downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

    def organize_downloads(self):
        """Organizes files in the Downloads folder by extension."""
        if not os.path.exists(self.downloads_path):
            return {"status": "error", "message": "Downloads folder not found."}

        stats = {"moved": 0, "errors": 0}
        
        # Define categories
        extensions = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
            "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
            "Installers": [".exe", ".msi", ".dmg", ".iso"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Video": [".mp4", ".mkv", ".mov", ".avi"],
            "Audio": [".mp3", ".wav", ".flac"]
        }

        try:
            for filename in os.listdir(self.downloads_path):
                file_path = os.path.join(self.downloads_path, filename)
                
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    moved = False
                    for category, exts in extensions.items():
                        if file_ext in exts:
                            target_dir = os.path.join(self.downloads_path, category)
                            os.makedirs(target_dir, exist_ok=True)
                            try:
                                shutil.move(file_path, os.path.join(target_dir, filename))
                                stats["moved"] += 1
                                moved = True
                                break
                            except Exception:
                                stats["errors"] += 1
                    
                    # Optional: Move everything else to 'Misc'
                    # if not moved:
                    #     ...
            
            return {
                "status": "success", 
                "message": f"Protocol Complete. Organized {stats['moved']} files.",
                "details": stats
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_system_summary(self):
        """Returns a quick text summary of the system state."""
        # Placeholder for more complex logic
        return "System is running efficiently. No critical alerts."
