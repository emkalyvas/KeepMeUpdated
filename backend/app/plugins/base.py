from typing import Dict, Any

class BaseNotificationChannel:
    """Base interface for all KeepMeUpdated notification channels."""
    
    @classmethod
    def get_plugin_id(cls) -> str:
        """Unique identifier for the channel type (e.g., 'smtp', 'gotify')."""
        raise NotImplementedError
        
    @classmethod
    def get_name(cls) -> str:
        """Human-readable name for the marketplace/dashboard (e.g., 'Gotify Server')."""
        raise NotImplementedError
        
    @classmethod
    def get_config_schema(cls) -> dict:
        """
        Returns JSON schema for required configuration. 
        Used by the frontend to dynamically generate settings forms.
        """
        raise NotImplementedError
        
    @classmethod
    def get_notification_schema(cls) -> dict:
        """
        Returns JSON schema for required notification parameters.
        Used by the frontend to dynamically generate notification creation forms.
        """
        return {}
        
    def __init__(self, config: Dict[str, Any]):
        """Initialize with the user's saved JSON config."""
        self.config = config
        
    def validate_config(self) -> bool:
        """
        Validates if the current config contains all required fields 
        and is syntactically valid.
        """
        raise NotImplementedError
        
    async def send(self, title: str, payload: str, parameters: Dict[str, Any], **kwargs) -> bool:
        """Executes the notification dispatch logic."""
        raise NotImplementedError
