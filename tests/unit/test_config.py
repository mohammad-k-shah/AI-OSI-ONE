"""
Unit tests for configuration management.
"""

import pytest
from unittest.mock import patch, mock_open
from src.utils.config import ConfigManager, NLPConfig, UIConfig, AppConfig


class TestConfigManager:
    """Test configuration manager functionality."""
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization with defaults."""
        config = ConfigManager()
        
        assert config is not None
        assert config.get_app_config() is not None
        assert config.get_nlp_config() is not None
        assert config.get_ui_config() is not None
    
    def test_get_config_values(self):
        """Test getting configuration values."""
        config = ConfigManager()
        
        # Test app config
        app_config = config.get_app_config()
        assert app_config.name == "OSI ONE AGENT"
        assert app_config.version == "1.0.0"
        assert app_config.log_level == "INFO"
        assert app_config.debug is False
        
        # Test NLP config
        nlp_config = config.get_nlp_config()
        assert nlp_config.provider == "openai"
        assert nlp_config.model == "gpt-4"
        assert nlp_config.max_tokens == 1000
        assert nlp_config.temperature == 0.1
        
        # Test UI config
        ui_config = config.get_ui_config()
        assert ui_config.theme == "dark"
        assert ui_config.show_progress is True
        assert ui_config.auto_complete is True
    
    def test_get_env_var(self):
        """Test getting environment variables."""
        config = ConfigManager()
        
        # Test with environment variable
        with patch.dict('os.environ', {'TEST_VAR': 'test_value'}):
            value = config.get_env_var('TEST_VAR', 'default')
            assert value == 'test_value'
        
        # Test with default value
        value = config.get_env_var('NONEXISTENT_VAR', 'default')
        assert value == 'default'
    
    def test_reload_config(self):
        """Test configuration reload."""
        config = ConfigManager()
        original_nlp_config = config.get_nlp_config()
        
        # Reload should not fail
        config.reload()
        reloaded_nlp_config = config.get_nlp_config()
        
        # Should have same default values
        assert reloaded_nlp_config.provider == original_nlp_config.provider
        assert reloaded_nlp_config.model == original_nlp_config.model


class TestNLPConfig:
    """Test NLP configuration model."""
    
    def test_nlp_config_defaults(self):
        """Test NLP config default values."""
        config = NLPConfig()
        
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.max_tokens == 1000
        assert config.temperature == 0.1
        assert config.timeout == 30
    
    def test_nlp_config_custom_values(self):
        """Test NLP config with custom values."""
        config = NLPConfig(
            provider="ollama",
            model="llama3",
            max_tokens=500,
            temperature=0.5,
            timeout=60
        )
        
        assert config.provider == "ollama"
        assert config.model == "llama3"
        assert config.max_tokens == 500
        assert config.temperature == 0.5
        assert config.timeout == 60


class TestUIConfig:
    """Test UI configuration model."""
    
    def test_ui_config_defaults(self):
        """Test UI config default values."""
        config = UIConfig()
        
        assert config.theme == "dark"
        assert config.show_progress is True
        assert config.auto_complete is True
        assert config.max_history == 100
    
    def test_ui_config_custom_values(self):
        """Test UI config with custom values."""
        config = UIConfig(
            theme="light",
            show_progress=False,
            auto_complete=False,
            max_history=50
        )
        
        assert config.theme == "light"
        assert config.show_progress is False
        assert config.auto_complete is False
        assert config.max_history == 50


class TestAppConfig:
    """Test application configuration model."""
    
    def test_app_config_defaults(self):
        """Test app config default values."""
        config = AppConfig()
        
        assert config.name == "OSI ONE AGENT"
        assert config.version == "1.0.0"
        assert config.log_level == "INFO"
        assert config.debug is False
    
    def test_app_config_custom_values(self):
        """Test app config with custom values."""
        config = AppConfig(
            name="Test Agent",
            version="2.0.0",
            log_level="DEBUG",
            debug=True
        )
        
        assert config.name == "Test Agent"
        assert config.version == "2.0.0"
        assert config.log_level == "DEBUG"
        assert config.debug is True 