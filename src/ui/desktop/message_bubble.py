"""
OSI ONE AGENT - Message Bubble Component

This module provides the MessageBubble widget for displaying chat messages
in a modern, professional chat interface with proper styling and formatting.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QWidget, QSizePolicy, QMenu, QAction
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextCursor
from .styles import OSI_COLORS
from PyQt5.QtWidgets import QApplication

class MessageBubble(QFrame):
    """
    A message bubble widget for displaying chat messages.
    
    Supports both user and assistant messages with different styling,
    timestamps, and rich text formatting.
    """
    
    # Signal emitted when message is clicked
    message_clicked = pyqtSignal(str)
    
    def __init__(
        self, 
        content: str, 
        sender: str = "user",
        message_id: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize the message bubble.
        
        Args:
            content: The message text content
            sender: "user" or "assistant"
            message_id: Unique message identifier
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.content = content
        self.sender = sender
        self.message_id = message_id or f"{sender}_{int(datetime.now().timestamp())}"
        
        self.setup_ui()
        self.setup_content()
        self.setup_styling()
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        # Message container
        self.message_container = QFrame()
        self.message_container.setObjectName("messageContainer")
        
        message_layout = QVBoxLayout(self.message_container)
        message_layout.setContentsMargins(12, 8, 12, 8)
        message_layout.setSpacing(4)
        
        # Message text
        self.message_text = QLabel()
        self.message_text.setObjectName("messageText")
        self.message_text.setWordWrap(True)
        self.message_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.message_text.setOpenExternalLinks(True)
        
        # Timestamp
        self.timestamp_label = QLabel()
        self.timestamp_label.setObjectName("timestampLabel")
        self.timestamp_label.setAlignment(Qt.AlignRight)
        self.timestamp_label.setStyleSheet("""
            QLabel#timestampLabel {
                color: #6B7280;
                font-size: 11px;
                font-style: italic;
            }
        """)
        
        # Add widgets to message layout
        message_layout.addWidget(self.message_text)
        message_layout.addWidget(self.timestamp_label)
        
        # Add message container to main layout
        layout.addWidget(self.message_container)
        
        # Set up context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def setup_avatar(self):
        """Set up the avatar for the message sender."""
        if self.sender == "user":
            # User avatar (you can replace with actual user avatar)
            self.avatar_label.setText("👤")
            self.avatar_label.setStyleSheet(f"""
                background-color: {OSI_COLORS['primary_blue']};
                border-radius: 16px;
                color: {OSI_COLORS['text_primary']};
                font-size: 16px;
                text-align: center;
                padding: 4px;
            """)
        else:
            # Assistant avatar
            self.avatar_label.setText("🤖")
            self.avatar_label.setStyleSheet(f"""
                background-color: {OSI_COLORS['accent_green']};
                border-radius: 16px;
                color: {OSI_COLORS['text_primary']};
                font-size: 16px;
                text-align: center;
                padding: 4px;
            """)
    
    def setup_content(self):
        """Set up the message content."""
        # Set message text
        self.message_text.setText(self.content)
        
        # Set timestamp
        timestamp = datetime.now().strftime("%H:%M")
        self.timestamp_label.setText(timestamp)
        
        # Set object names for styling
        if self.sender == "user":
            self.message_container.setObjectName("userMessage")
            self.message_text.setObjectName("userMessageText")
        else:
            self.message_container.setObjectName("botMessage")
            self.message_text.setObjectName("messageText")
    
    def format_message_content(self, content: str) -> str:
        """
        Format message content with HTML styling.
        
        Args:
            content: Raw message content
            
        Returns:
            str: HTML formatted content
        """
        # Basic HTML structure
        html = f"""
        <div style="
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            line-height: 1.4;
            color: {'#FFFFFF' if self.sender == 'user' else '#2D2D30'};
        ">
        """
        
        # Process content for special formatting
        formatted_content = content
        
        # Handle code blocks
        if "```" in content:
            formatted_content = self.format_code_blocks(content)
        
        # Handle URLs
        formatted_content = self.format_urls(formatted_content)
        
        # Handle bold text
        formatted_content = formatted_content.replace("**", "<strong>").replace("**", "</strong>")
        
        # Handle italic text
        formatted_content = formatted_content.replace("*", "<em>").replace("*", "</em>")
        
        # Handle line breaks
        formatted_content = formatted_content.replace("\n", "<br>")
        
        html += formatted_content
        html += "</div>"
        
        return html
    
    def format_code_blocks(self, content: str) -> str:
        """
        Format code blocks in the message content.
        
        Args:
            content: Raw content with code blocks
            
        Returns:
            str: Content with formatted code blocks
        """
        import re
        
        # Find code blocks
        code_pattern = r'```(\w+)?\n(.*?)```'
        
        def replace_code_block(match):
            language = match.group(1) or "text"
            code = match.group(2)
            
            return f"""
            <div style="
                background-color: {'#1E1E1E' if self.sender == 'user' else '#F5F5F5'};
                border: 1px solid {'#404040' if self.sender == 'user' else '#E0E0E0'};
                border-radius: 6px;
                padding: 12px;
                margin: 8px 0;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                color: {'#FFFFFF' if self.sender == 'user' else '#2D2D30'};
                overflow-x: auto;
            ">
                <div style="
                    color: {'#00CCFF' if self.sender == 'user' else '#0066CC'};
                    font-weight: bold;
                    margin-bottom: 8px;
                    font-size: 11px;
                    text-transform: uppercase;
                ">{language}</div>
                <pre style="margin: 0; white-space: pre-wrap;">{code}</pre>
            </div>
            """
        
        return re.sub(code_pattern, replace_code_block, content, flags=re.DOTALL)
    
    def format_urls(self, content: str) -> str:
        """
        Format URLs in the message content.
        
        Args:
            content: Raw content with URLs
            
        Returns:
            str: Content with formatted URLs
        """
        import re
        
        # URL pattern
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        
        def replace_url(match):
            url = match.group(0)
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            return f'<a href="{url}" style="color: {OSI_COLORS["secondary_cyan"]}; text-decoration: none;">{match.group(0)}</a>'
        
        return re.sub(url_pattern, replace_url, content)
    
    def setup_styling(self):
        """Set up the styling for the message bubble."""
        # Apply base styling
        self.setStyleSheet("""
            QFrame {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Set alignment based on sender using layout
        if self.sender == "user":
            # User messages align to the right
            self.layout().setAlignment(Qt.AlignRight)
        else:
            # Bot messages align to the left
            self.layout().setAlignment(Qt.AlignLeft)
    
    def setup_behavior(self):
        """Set up interactive behavior for the message bubble."""
        # Make clickable
        self.setCursor(Qt.PointingHandCursor)
        
        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def update_message(self, new_content: str):
        """Update the message content."""
        self.content = new_content
        self.message_text.setText(new_content)
        
        # Update timestamp
        timestamp = datetime.now().strftime("%H:%M")
        self.timestamp_label.setText(timestamp)
    
    def get_message_id(self) -> str:
        """Get the message ID."""
        return self.message_id
    
    def show_context_menu(self, position):
        """Show context menu for the message."""
        context_menu = QMenu(self)
        
        # Copy action
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_message)
        context_menu.addAction(copy_action)
        
        # Show context menu
        context_menu.exec_(self.mapToGlobal(position))
    
    def copy_message(self):
        """Copy message to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.content)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            # Emit clicked signal
            self.message_clicked.emit(self.message_id)
        super().mousePressEvent(event)
    
    def resizeEvent(self, event):
        """Handle resize events to adjust content height."""
        super().resizeEvent(event)
        
        # Recalculate content height for message text
        if hasattr(self, 'message_text'):
            # Adjust text wrapping based on new width
            self.message_text.setWordWrap(True)
    
    def get_message_data(self) -> Dict[str, Any]:
        """
        Get message data for serialization.
        
        Returns:
            Dict containing message data
        """
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "formatted_content": self.content_widget.toHtml()
        }
    
    def set_typing_indicator(self, is_typing: bool):
        """
        Show or hide typing indicator.
        
        Args:
            is_typing: Whether to show typing indicator
        """
        if is_typing:
            self.content_widget.setHtml("""
                <div style="color: #CCCCCC; font-style: italic;">
                    <span class="typing-dots">
                        OSI ONE AGENT is typing<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
                    </span>
                </div>
            """)
            
            # Animate typing dots
            self.typing_timer = QTimer()
            self.typing_timer.timeout.connect(self.animate_typing_dots)
            self.typing_timer.start(500)
        else:
            if hasattr(self, 'typing_timer'):
                self.typing_timer.stop()
            self.setup_content()
    
    def animate_typing_dots(self):
        """Animate the typing indicator dots."""
        # Simple animation - you can enhance this
        current_html = self.content_widget.toHtml()
        if "typing-dots" in current_html:
            # Rotate dots
            dots = ["", ".", "..", "..."]
            import random
            dot_count = random.randint(1, 3)
            dots_text = "." * dot_count
            
            new_html = f"""
                <div style="color: #CCCCCC; font-style: italic;">
                    OSI ONE AGENT is typing{dots_text}
                </div>
            """
            self.content_widget.setHtml(new_html) 