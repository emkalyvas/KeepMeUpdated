import os
import json
import httpx
import sys
import subprocess
import importlib.util
import importlib.metadata
from typing import Type, Dict, List
from sqlalchemy.future import select

from .base import BaseNotificationChannel, BaseDataSourcePlugin
from .smtp import SMTPChannel

PLUGINS_DIR = "/app/data/plugins"

class PluginManager:
    def __init__(self):
        self._channel_plugins: Dict[str, Type[BaseNotificationChannel]] = {}
        self._datasource_plugins: Dict[str, Type[BaseDataSourcePlugin]] = {}
        self.register_channel_plugin(SMTPChannel)
        
        if not os.path.exists(PLUGINS_DIR):
            os.makedirs(PLUGINS_DIR, exist_ok=True)
        else:
            self.load_local_plugins()
        
    def register_channel_plugin(self, plugin_class: Type[BaseNotificationChannel]):
        self._channel_plugins[plugin_class.get_plugin_id()] = plugin_class
        
    def register_datasource_plugin(self, plugin_class: Type[BaseDataSourcePlugin]):
        self._datasource_plugins[plugin_class.get_plugin_id()] = plugin_class
        
    def get_channel_plugin(self, plugin_id: str) -> Type[BaseNotificationChannel]:
        return self._channel_plugins.get(plugin_id)
        
    def get_datasource_plugin(self, plugin_id: str) -> Type[BaseDataSourcePlugin]:
        return self._datasource_plugins.get(plugin_id)
        
    def _load_installed_meta(self) -> dict:
        meta_path = os.path.join(PLUGINS_DIR, "installed.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_installed_meta(self, data: dict):
        meta_path = os.path.join(PLUGINS_DIR, "installed.json")
        with open(meta_path, "w") as f:
            json.dump(data, f)

    def get_all_plugins(self) -> List[dict]:
        channels = [
            {
                "id": p.get_plugin_id(),
                "name": p.get_name(),
                "type": "channel",
                "schema": p.get_config_schema(),
                "notification_schema": p.get_notification_schema()
            }
            for p in self._channel_plugins.values()
        ]
        datasources = [
            {
                "id": p.get_plugin_id(),
                "name": p.get_name(),
                "type": "datasource",
                "schema": p.get_config_schema(),
                "context_schema": p.get_context_schema()
            }
            for p in self._datasource_plugins.values()
        ]
        return channels + datasources
        
    def load_local_plugins(self):
        for filename in os.listdir(PLUGINS_DIR):
            if filename.endswith(".py"):
                self.load_plugin_file(os.path.join(PLUGINS_DIR, filename))
                
    def load_plugin_file(self, filepath: str) -> bool:
        module_name = f"app.plugins.dynamic_plugin_{os.path.basename(filepath)[:-3]}"
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            import sys
            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)
                loaded = False
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type):
                        if issubclass(attr, BaseNotificationChannel) and attr is not BaseNotificationChannel:
                            self.register_channel_plugin(attr)
                            print(f"Loaded dynamic channel plugin: {attr.get_plugin_id()}")
                            loaded = True
                        elif issubclass(attr, BaseDataSourcePlugin) and attr is not BaseDataSourcePlugin:
                            self.register_datasource_plugin(attr)
                            print(f"Loaded dynamic datasource plugin: {attr.get_plugin_id()}")
                            loaded = True
                return loaded
            except Exception as e:
                print(f"Failed to load plugin {filepath}: {e}")
        return False

    async def get_repo_plugins(self, db, repo_id: int) -> List[dict]:
        from app.models import Repository
        result = await db.execute(select(Repository).where(Repository.id == repo_id))
        repo = result.scalars().first()
        if not repo:
            return []
            
        async with httpx.AsyncClient() as client:
            try:
                url = repo.url.rstrip("/")
                if "github.com" in url and "raw.githubusercontent.com" not in url:
                    clean_url = url.split("github.com/")[-1]
                    parts = clean_url.split("/")
                    if len(parts) >= 2:
                        url = f"https://raw.githubusercontent.com/{parts[0]}/{parts[1]}/main"
                
                registry_url = f"{url}/registry.json" if not url.endswith(".json") else url
                resp = await client.get(registry_url)
                if resp.status_code == 200:
                    registry = resp.json()
                    base_url = registry_url.rsplit("/", 1)[0]
                    plugins = registry.get("plugins", [])
                    installed_meta = self._load_installed_meta()
                    for p in plugins:
                        p["repo_id"] = repo.id
                        file_url = p.get("file_url")
                        if not file_url.startswith("http"):
                            p["full_file_url"] = f"{base_url}/{file_url}"
                        else:
                            p["full_file_url"] = file_url
                        p["is_installed"] = p["id"] in self._channel_plugins or p["id"] in self._datasource_plugins
                        if p["is_installed"]:
                            meta = installed_meta.get(p["id"], {})
                            p["installed_version"] = meta.get("version", "0.0.0")
                    return plugins
            except Exception as e:
                print(f"Error fetching repo plugins {repo.url}: {e}")
        return []

    async def install_plugin(self, plugin_id: str, version: str, full_file_url: str, requirements: List[str] = None) -> bool:
        if requirements:
            missing_reqs = []
            for req in requirements:
                pkg_name = req.split("=")[0].split(">")[0].split("<")[0].strip()
                try:
                    importlib.metadata.version(pkg_name)
                except importlib.metadata.PackageNotFoundError:
                    missing_reqs.append(req)
                    
            if missing_reqs:
                try:
                    print(f"Installing missing dependencies for {plugin_id}: {missing_reqs}")
                    subprocess.run([sys.executable, "-m", "pip", "install", *missing_reqs], check=True)
                except Exception as e:
                    print(f"Failed to install dependencies for {plugin_id}: {e}")
                    return False

        os.makedirs(PLUGINS_DIR, exist_ok=True)
        filename = full_file_url.split("/")[-1]
        filepath = os.path.join(PLUGINS_DIR, filename)
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(full_file_url)
                if resp.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(resp.content)
                    
                    success = self.load_plugin_file(filepath)
                    if success:
                        meta = self._load_installed_meta()
                        meta[plugin_id] = {"version": version, "filename": filename}
                        self._save_installed_meta(meta)
                    return success
            except Exception as e:
                print(f"Error installing plugin from {full_file_url}: {e}")
        return False

    def uninstall_plugin(self, plugin_id: str) -> bool:
        if plugin_id not in self._channel_plugins and plugin_id not in self._datasource_plugins:
            return False
            
        meta = self._load_installed_meta()
        plugin_meta = meta.get(plugin_id)
        if plugin_meta and "filename" in plugin_meta:
            filepath = os.path.join(PLUGINS_DIR, plugin_meta["filename"])
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error deleting plugin file {filepath}: {e}")
                    return False
                    
        if plugin_id in meta:
            del meta[plugin_id]
            self._save_installed_meta(meta)
            
        if plugin_id in self._channel_plugins:
            del self._channel_plugins[plugin_id]
        if plugin_id in self._datasource_plugins:
            del self._datasource_plugins[plugin_id]
        
        return True

plugin_manager = PluginManager()
