"""
OSI ONE AGENT - Desktop UI Module

This module provides a PyQt5-based desktop GUI for the OSI ONE AGENT,
offering a professional Windows application with modern chat interface,
system tray integration, and enhanced user experience.
"""

from .main_window import OSIAgentGUI
from .chat_widget import ChatWidget
from .input_widget import InputWidget
from .message_bubble import MessageBubble
from .system_tray import SystemTray
from .notifications import NotificationManager
from .voice_input import VoiceInputHandler
from .styles import get_application_style

__all__ = [
    'OSIAgentGUI',
    'ChatWidget', 
    'InputWidget',
    'MessageBubble',
    'SystemTray',
    'NotificationManager',
    'VoiceInputHandler',
    'get_application_style'
]

__version__ = "1.0.0" 