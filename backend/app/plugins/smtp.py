import smtplib
from email.message import EmailMessage
from typing import Dict, Any
from .base import BaseNotificationChannel

class SMTPChannel(BaseNotificationChannel):
    
    @classmethod
    def get_plugin_id(cls) -> str:
        return "smtp"
        
    @classmethod
    def get_name(cls) -> str:
        return "SMTP (Email)"
        
    @classmethod
    def get_config_schema(cls) -> dict:
        return {
            "type": "object",
            "properties": {
                "host": {"type": "string", "title": "SMTP Host"},
                "port": {"type": "integer", "title": "SMTP Port"},
                "username": {"type": "string", "title": "Username"},
                "password": {"type": "string", "title": "Password", "format": "password"},
                "use_tls": {"type": "boolean", "title": "Use TLS", "default": True},
                "from_email": {"type": "string", "title": "From Email Address"}
            },
            "required": ["host", "port", "from_email"]
        }
        
    @classmethod
    def get_notification_schema(cls) -> dict:
        return {
            "type": "object",
            "properties": {
                "to_email": {"type": "string", "title": "Recipient Email"},
                "cc_email": {"type": "string", "title": "CC Email (Optional)"},
                "subject": {"type": "string", "title": "Subject"},
                "body": {"type": "string", "title": "Body (Message)"}
            },
            "required": ["to_email", "subject", "body"]
        }
        
    def validate_config(self) -> bool:
        required = ["host", "port", "from_email"]
        for req in required:
            if not self.config.get(req):
                return False
        return True
        
    async def send(self, title: str, payload: str, parameters: Dict[str, Any], **kwargs) -> bool:
        try:
            msg = EmailMessage()
            msg.set_content(parameters.get("body", payload or ""))
            msg['Subject'] = parameters.get("subject", title)
            msg['From'] = self.config.get("from_email")
            msg['To'] = parameters.get("to_email", self.config.get("from_email")) # Fallback to sending to self
            if parameters.get("cc_email"):
                msg['Cc'] = parameters.get("cc_email")
            
            # Synchronous smtplib inside async - for a real heavy load app use aiosmtplib.
            # Good enough for KeepMeUpdated default channel.
            host = self.config.get("host")
            port = int(self.config.get("port", 587))
            
            server = smtplib.SMTP(host, port)
            if self.config.get("use_tls", True):
                server.starttls()
                
            username = self.config.get("username")
            password = self.config.get("password")
            if username and password:
                server.login(username, password)
                
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"SMTP send failed: {e}")
            return False
