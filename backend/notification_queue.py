from typing import List, Dict, Any
from datetime import datetime

class NotificationQueue:
    """
    In-memory alert queue for CyberNova Live Mode.
    Provides a simple way to manage unread notifications for users.
    """
    def __init__(self):
        self._notifications: List[Dict[str, Any]] = []
        
    def add_notification(self, title: str, message: str, level: str = "info"):
        self._notifications.append({
            "id": datetime.now().timestamp(),
            "title": title,
            "message": message,
            "level": level,
            "timestamp": datetime.now(),
            "read": False
        })
        
    def get_unread(self) -> List[Dict[str, Any]]:
        return [n for n in self._notifications if not n["read"]]
        
    def mark_all_read(self):
        for n in self._notifications:
            n["read"] = True
            
    def clear(self):
        self._notifications = []
        
# Global instance for app-wide use
notification_queue = NotificationQueue()
