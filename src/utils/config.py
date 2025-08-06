"""
Configuration Manager

Handles loading and managing application configuration from YAML files.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from pydantic import BaseModel, Field


class NLPConfig(BaseModel):
    """NLP configuration settings."""
    provider: str = Field(default="openai", description="NLP provider (openai, ollama)")
    model: str = Field(default="gpt-4", description="Model name")
    max_tokens: int = Field(default=1000, description="Maximum tokens for response")
    temperature: float = Field(default=0.1, description="Response temperature")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class UIConfig(BaseModel):
    """UI configuration settings."""
    theme: str = Field(default="dark", description="UI theme")
    show_progress: bool = Field(default=True, description="Show progress indicators")
    auto_complete: bool = Field(default=True, description="Enable auto-completion")
    max_history: int = Field(default=100, description="Maximum command history")


class PerformanceConfig(BaseModel):
    """Performance configuration settings."""
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout: int = Field(default=30, description="Default timeout")
    rate_limit_delay: float = Field(default=1.0, description="Rate limit delay")


class SecurityConfig(BaseModel):
    """Security configuration settings."""
    token_encryption: bool = Field(default=True, description="Enable token encryption")
    token_rotation: bool = Field(default=True, description="Enable token rotation")
    audit_logging: bool = Field(default=True, description="Enable audit logging")


class AppConfig(BaseModel):
    """Application configuration settings."""
    name: str = Field(default="OSI ONE AGENT", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")
    openai: Dict[str, Any] = Field(default_factory=lambda: {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "model": "gpt-4",
        "max_tokens": 1000,
        "temperature": 0.1
    }, description="OpenAI configuration")
    azure_devops: Dict[str, Any] = Field(default_factory=lambda: {
        "token": os.getenv("AZURE_DEVOPS_TOKEN", ""),
        "organization": os.getenv("AZURE_DEVOPS_ORGANIZATION", ""),
        "project": os.getenv("AZURE_DEVOPS_PROJECT", "")
    }, description="Azure DevOps configuration")


class ConfigManager:
    """Manages application configuration from YAML files."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_dir = Path(config_dir) if config_dir else Path("config")
        self._config_cache: Dict[str, Any] = {}
        self._load_configs()
    
    def _load_configs(self) -> None:
        """Load all configuration files."""
        try:
            # Load main app configuration
            app_config_path = self.config_dir / "app" / "app.yaml"
            if app_config_path.exists():
                with open(app_config_path, 'r', encoding='utf-8') as f:
                    app_data = yaml.safe_load(f)
                    self._config_cache['app'] = AppConfig(**app_data.get('app', {}))
                    self._config_cache['nlp'] = NLPConfig(**app_data.get('nlp', {}))
                    self._config_cache['ui'] = UIConfig(**app_data.get('ui', {}))
                    self._config_cache['performance'] = PerformanceConfig(**app_data.get('performance', {}))
                    self._config_cache['security'] = SecurityConfig(**app_data.get('security', {}))
            else:
                # Use defaults if config file doesn't exist
                self._config_cache['app'] = AppConfig()
                self._config_cache['nlp'] = NLPConfig()
                self._config_cache['ui'] = UIConfig()
                self._config_cache['performance'] = PerformanceConfig()
                self._config_cache['security'] = SecurityConfig()
            
            # Load tool configurations
            self._load_tool_configs()
            
        except Exception as e:
            print(f"⚠️ Warning: Failed to load configuration: {e}")
            # Use defaults on error
            self._config_cache['app'] = AppConfig()
            self._config_cache['nlp'] = NLPConfig()
            self._config_cache['ui'] = UIConfig()
            self._config_cache['performance'] = PerformanceConfig()
            self._config_cache['security'] = SecurityConfig()
    
    def _load_tool_configs(self) -> None:
        """Load tool-specific configurations."""
        tools_dir = self.config_dir / "tools"
        if not tools_dir.exists():
            return
        
        for config_file in tools_dir.glob("*.yaml"):
            tool_name = config_file.stem
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._config_cache[f'tool_{tool_name}'] = yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ Warning: Failed to load {tool_name} config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self._config_cache
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_app_config(self) -> AppConfig:
        """Get application configuration."""
        return self._config_cache.get('app', AppConfig())
    
    def get_nlp_config(self) -> NLPConfig:
        """Get NLP configuration."""
        return self._config_cache.get('nlp', NLPConfig())
    
    def get_ui_config(self) -> UIConfig:
        """Get UI configuration."""
        return self._config_cache.get('ui', UIConfig())
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration."""
        return self._config_cache.get('performance', PerformanceConfig())
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return self._config_cache.get('security', SecurityConfig())
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get tool-specific configuration."""
        return self._config_cache.get(f'tool_{tool_name}', {})
    
    def reload(self) -> None:
        """Reload all configuration files."""
        self._config_cache.clear()
        self._load_configs()
    
    def get_env_var(self, key: str, default: Any = None) -> Any:
        """Get environment variable with fallback to config."""
        return os.getenv(key, self.get(key, default))
    
    def get_openai_api_key(self) -> str:
        """Get OpenAI API key from environment or config."""
        # First try environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return api_key
        
        # Fall back to config file
        app_config = self.get_app_config()
        return app_config.openai.get("api_key", "")
    
    def get_azure_devops_token(self) -> str:
        """Get Azure DevOps PAT token from environment or config."""
        # First try environment variable
        token = os.getenv("AZURE_DEVOPS_TOKEN")
        if token:
            return token
        
        # Fall back to config file
        app_config = self.get_app_config()
        return app_config.azure_devops.get("token", "")
    
    def get_azure_devops_organization(self) -> str:
        """Get Azure DevOps organization from environment or config."""
        # First try environment variable
        org = os.getenv("AZURE_DEVOPS_ORGANIZATION")
        if org:
            return org
        
        # Fall back to config file
        app_config = self.get_app_config()
        return app_config.azure_devops.get("organization", "")
    
    def get_azure_devops_project(self) -> str:
        """Get Azure DevOps project from environment or config."""
        # First try environment variable
        project = os.getenv("AZURE_DEVOPS_PROJECT")
        if project:
            return project
        
        # Fall back to config file
        app_config = self.get_app_config()
        return app_config.azure_devops.get("project", "")
    
    def check_required_config(self) -> Dict[str, bool]:
        """Check if required configuration is available."""
        missing_configs = {}
        
        # Check OpenAI API key
        openai_key = self.get_openai_api_key()
        missing_configs["openai_api_key"] = not bool(openai_key)
        
        # Check Azure DevOps configuration
        ado_token = self.get_azure_devops_token()
        ado_org = self.get_azure_devops_organization()
        ado_project = self.get_azure_devops_project()
        
        missing_configs["azure_devops_token"] = not bool(ado_token)
        missing_configs["azure_devops_organization"] = not bool(ado_org)
        missing_configs["azure_devops_project"] = not bool(ado_project)
        
        return missing_configs 