import os
import httpx
import importlib.util
from typing import Type, Dict, List
from sqlalchemy.future import select

from .base import BaseNotificationChannel
from .smtp import SMTPChannel

PLUGINS_DIR = "/app/data/plugins"

class PluginManager:
    def __init__(self):
        self._plugins: Dict[str, Type[BaseNotificationChannel]] = {}
        self.register_plugin(SMTPChannel)
        
        if not os.path.exists(PLUGINS_DIR):
            os.makedirs(PLUGINS_DIR, exist_ok=True)
        else:
            self.load_local_plugins()
        
    def register_plugin(self, plugin_class: Type[BaseNotificationChannel]):
        self._plugins[plugin_class.get_plugin_id()] = plugin_class
        
    def get_plugin(self, plugin_id: str) -> Type[BaseNotificationChannel]:
        return self._plugins.get(plugin_id)
        
    def get_all_plugins(self) -> List[dict]:
        return [
            {
                "id": p.get_plugin_id(),
                "name": p.get_name(),
                "schema": p.get_config_schema(),
                "notification_schema": p.get_notification_schema()
            }
            for p in self._plugins.values()
        ]
        
    def load_local_plugins(self):
        for filename in os.listdir(PLUGINS_DIR):
            if filename.endswith(".py"):
                self.load_plugin_file(os.path.join(PLUGINS_DIR, filename))
                
    def load_plugin_file(self, filepath: str):
        module_name = f"dynamic_plugin_{os.path.basename(filepath)[:-3]}"
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseNotificationChannel) and attr is not BaseNotificationChannel:
                        self.register_plugin(attr)
                        print(f"Loaded dynamic plugin: {attr.get_plugin_id()}")
            except Exception as e:
                print(f"Failed to load plugin {filepath}: {e}")

    async def sync_plugins(self, db):
        from app.models import Repository
        result = await db.execute(select(Repository))
        repos = result.scalars().all()
        
        os.makedirs(PLUGINS_DIR, exist_ok=True)
        
        async with httpx.AsyncClient() as client:
            for repo in repos:
                try:
                    url = repo.url.rstrip("/")
                    registry_url = f"{url}/registry.json" if not url.endswith(".json") else url
                    resp = await client.get(registry_url)
                    if resp.status_code == 200:
                        registry = resp.json()
                        base_url = registry_url.rsplit("/", 1)[0]
                        for pinfo in registry.get("plugins", []):
                            file_url = pinfo.get("file_url")
                            if not file_url.startswith("http"):
                                file_url = f"{base_url}/{file_url}"
                                
                            filename = file_url.split("/")[-1]
                            filepath = os.path.join(PLUGINS_DIR, filename)
                            
                            presp = await client.get(file_url)
                            if presp.status_code == 200:
                                with open(filepath, "wb") as f:
                                    f.write(presp.content)
                                self.load_plugin_file(filepath)
                except Exception as e:
                    print(f"Error syncing repo {repo.url}: {e}")

plugin_manager = PluginManager()
