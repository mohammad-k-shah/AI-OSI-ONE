"""
OSI ONE AGENT - Desktop UI Styles

This module provides QSS (Qt Style Sheets) styling for the desktop application,
including OSI branding colors, modern UI elements, and professional appearance.
"""

from typing import Dict, Any
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt

# OSI Branding Colors - Updated to match modern design
OSI_COLORS = {
    "header_blue": "#1E3A8A",      # Dark blue header
    "primary_blue": "#3B82F6",     # Primary blue for buttons
    "secondary_blue": "#60A5FA",   # Light blue for hover
    "chat_white": "#FFFFFF",       # White chat area
    "input_gray": "#F3F4F6",       # Light gray input area
    "message_gray": "#F1F5F9",     # Light gray message bubbles
    "text_primary": "#1F2937",     # Dark text
    "text_secondary": "#6B7280",   # Secondary text
    "text_white": "#FFFFFF",       # White text
    "border": "#E5E7EB",           # Light border
    "success": "#10B981",          # Success green
    "warning": "#F59E0B",          # Warning yellow
    "error": "#EF4444",            # Error red
    "info": "#3B82F6"              # Info blue
}

def get_application_style() -> str:
    """
    Get the main application QSS style sheet.
    
    Returns:
        str: Complete QSS style sheet for the application
    """
    return f"""
    /* Main Application Window */
    QMainWindow {{
        background-color: {OSI_COLORS["chat_white"]};
        color: {OSI_COLORS["text_primary"]};
        border: none;
        border-radius: 12px;
    }}
    
    /* Header Section */
    QFrame#headerFrame {{
        background-color: {OSI_COLORS["header_blue"]};
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        border: none;
        padding: 16px;
    }}
    
    QLabel#titleLabel {{
        color: {OSI_COLORS["text_white"]};
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 18px;
        font-weight: 600;
    }}
    
    QLabel#statusLabel {{
        color: {OSI_COLORS["text_white"]};
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 12px;
        opacity: 0.8;
    }}
    
    QPushButton#settingsButton {{
        background-color: transparent;
        border: none;
        color: {OSI_COLORS["text_white"]};
        font-size: 16px;
        padding: 8px;
        border-radius: 4px;
    }}
    
    QPushButton#settingsButton:hover {{
        background-color: rgba(255, 255, 255, 0.1);
    }}
    
    QPushButton#minimizeButton {{
        background-color: transparent;
        border: none;
        color: {OSI_COLORS["text_white"]};
        font-size: 14px;
        padding: 8px;
        border-radius: 4px;
    }}
    
    QPushButton#minimizeButton:hover {{
        background-color: rgba(255, 255, 255, 0.1);
    }}
    
    /* Chat Area */
    QScrollArea {{
        background-color: {OSI_COLORS["chat_white"]};
        border: none;
        border-radius: 0px;
    }}
    
    QWidget#scrollAreaWidgetContents {{
        background-color: {OSI_COLORS["chat_white"]};
        border: none;
    }}
    
    /* Message Bubbles */
    QFrame#botMessage {{
        background-color: {OSI_COLORS["message_gray"]};
        border: none;
        border-radius: 16px;
        padding: 12px 16px;
        margin: 4px 8px;
    }}
    
    QFrame#userMessage {{
        background-color: {OSI_COLORS["primary_blue"]};
        border: none;
        border-radius: 16px;
        padding: 12px 16px;
        margin: 4px 8px;
    }}
    
    QLabel#messageText {{
        color: {OSI_COLORS["text_primary"]};
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 14px;
        line-height: 1.4;
        background-color: transparent;
        border: none;
    }}
    
    QLabel#userMessageText {{
        color: {OSI_COLORS["text_white"]};
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 14px;
        line-height: 1.4;
        background-color: transparent;
        border: none;
    }}
    
    /* Quick Reply Buttons */
    QPushButton#quickReplyButton {{
        background-color: {OSI_COLORS["primary_blue"]};
        color: {OSI_COLORS["text_white"]};
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 13px;
        font-weight: 500;
    }}
    
    QPushButton#quickReplyButton:hover {{
        background-color: {OSI_COLORS["secondary_blue"]};
    }}
    
    QPushButton#quickReplyButtonSecondary {{
        background-color: transparent;
        color: {OSI_COLORS["primary_blue"]};
        border: 2px solid {OSI_COLORS["primary_blue"]};
        border-radius: 20px;
        padding: 8px 16px;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 13px;
        font-weight: 500;
    }}
    
    QPushButton#quickReplyButtonSecondary:hover {{
        background-color: {OSI_COLORS["primary_blue"]};
        color: {OSI_COLORS["text_white"]};
    }}
    
    /* Input Area */
    QFrame#inputFrame {{
        background-color: {OSI_COLORS["input_gray"]};
        border: none;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
        padding: 16px;
    }}
    
    QLineEdit#messageInput {{
        background-color: {OSI_COLORS["chat_white"]};
        border: 1px solid {OSI_COLORS["border"]};
        border-radius: 20px;
        padding: 12px 16px;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 14px;
        color: {OSI_COLORS["text_primary"]};
    }}
    
    QLineEdit#messageInput:focus {{
        border-color: {OSI_COLORS["primary_blue"]};
        outline: none;
    }}
    
    QLineEdit#messageInput::placeholder {{
        color: {OSI_COLORS["text_secondary"]};
    }}
    
    /* Action Buttons */
    QPushButton#emojiButton, QPushButton#attachmentButton {{
        background-color: transparent;
        border: none;
        color: {OSI_COLORS["text_secondary"]};
        font-size: 18px;
        padding: 8px;
        border-radius: 4px;
    }}
    
    QPushButton#emojiButton:hover, QPushButton#attachmentButton:hover {{
        background-color: rgba(59, 130, 246, 0.1);
        color: {OSI_COLORS["primary_blue"]};
    }}
    
    QPushButton#sendButton {{
        background-color: {OSI_COLORS["primary_blue"]};
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        color: {OSI_COLORS["text_white"]};
        font-size: 16px;
    }}
    
    QPushButton#sendButton:hover {{
        background-color: {OSI_COLORS["secondary_blue"]};
    }}
    
    QPushButton#sendButton:pressed {{
        background-color: {OSI_COLORS["header_blue"]};
    }}
    
    /* Scrollbar */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 8px;
        border-radius: 4px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {OSI_COLORS["border"]};
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {OSI_COLORS["text_secondary"]};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* Menu Bar */
    QMenuBar {{
        background-color: {OSI_COLORS["header_blue"]};
        color: {OSI_COLORS["text_white"]};
        border: none;
        padding: 4px;
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 12px;
        border-radius: 4px;
        color: {OSI_COLORS["text_white"]};
    }}
    
    QMenuBar::item:selected {{
        background-color: rgba(255, 255, 255, 0.1);
    }}
    
    /* Tool Bar */
    QToolBar {{
        background-color: {OSI_COLORS["header_blue"]};
        border: none;
        spacing: 5px;
        padding: 5px;
    }}
    
    QToolButton {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 8px;
        color: {OSI_COLORS["text_white"]};
    }}
    
    QToolButton:hover {{
        background-color: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
    }}
    
    QToolButton:pressed {{
        background-color: rgba(255, 255, 255, 0.2);
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {OSI_COLORS["input_gray"]};
        color: {OSI_COLORS["text_secondary"]};
        border: none;
        padding: 4px 8px;
    }}
    
    QStatusBar QLabel {{
        color: {OSI_COLORS["text_secondary"]};
        font-size: 12px;
    }}
    """

def get_dark_palette() -> QPalette:
    """
    Get the dark color palette for the application.
    
    Returns:
        QPalette: Dark color palette
    """
    palette = QPalette()
    
    # Set colors
    palette.setColor(QPalette.Window, QColor(OSI_COLORS["chat_white"]))
    palette.setColor(QPalette.WindowText, QColor(OSI_COLORS["text_primary"]))
    palette.setColor(QPalette.Base, QColor(OSI_COLORS["chat_white"]))
    palette.setColor(QPalette.AlternateBase, QColor(OSI_COLORS["input_gray"]))
    palette.setColor(QPalette.ToolTipBase, QColor(OSI_COLORS["header_blue"]))
    palette.setColor(QPalette.ToolTipText, QColor(OSI_COLORS["text_white"]))
    palette.setColor(QPalette.Text, QColor(OSI_COLORS["text_primary"]))
    palette.setColor(QPalette.Button, QColor(OSI_COLORS["primary_blue"]))
    palette.setColor(QPalette.ButtonText, QColor(OSI_COLORS["text_white"]))
    palette.setColor(QPalette.BrightText, QColor(OSI_COLORS["text_white"]))
    palette.setColor(QPalette.Link, QColor(OSI_COLORS["primary_blue"]))
    palette.setColor(QPalette.Highlight, QColor(OSI_COLORS["primary_blue"]))
    palette.setColor(QPalette.HighlightedText, QColor(OSI_COLORS["text_white"]))
    
    return palette

def get_light_palette() -> QPalette:
    """
    Get the light color palette for the application.
    
    Returns:
        QPalette: Light color palette
    """
    palette = QPalette()
    
    # Set colors
    palette.setColor(QPalette.Window, QColor(OSI_COLORS["chat_white"]))
    palette.setColor(QPalette.WindowText, QColor(OSI_COLORS["text_primary"]))
    palette.setColor(QPalette.Base, QColor(OSI_COLORS["chat_white"]))
    palette.setColor(QPalette.AlternateBase, QColor(OSI_COLORS["input_gray"]))
    palette.setColor(QPalette.ToolTipBase, QColor(OSI_COLORS["header_blue"]))
    palette.setColor(QPalette.ToolTipText, QColor(OSI_COLORS["text_white"]))
    palette.setColor(QPalette.Text, QColor(OSI_COLORS["text_primary"]))
    palette.setColor(QPalette.Button, QColor(OSI_COLORS["primary_blue"]))
    palette.setColor(QPalette.ButtonText, QColor(OSI_COLORS["text_white"]))
    palette.setColor(QPalette.BrightText, QColor(OSI_COLORS["text_white"]))
    palette.setColor(QPalette.Link, QColor(OSI_COLORS["primary_blue"]))
    palette.setColor(QPalette.Highlight, QColor(OSI_COLORS["primary_blue"]))
    palette.setColor(QPalette.HighlightedText, QColor(OSI_COLORS["text_white"]))
    
    return palette

def get_application_font() -> QFont:
    """
    Get the application font.
    
    Returns:
        QFont: Application font
    """
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    return font 