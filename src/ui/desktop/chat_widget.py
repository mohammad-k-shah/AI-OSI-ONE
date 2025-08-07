"""
OSI ONE AGENT - Chat Widget Component

This module provides the ChatWidget for displaying and managing chat messages
in a scrollable area with modern message bubbles and conversation history.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, 
    QLabel, QSizePolicy, QApplication, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QIcon
from .message_bubble import MessageBubble
from .styles import OSI_COLORS

class ChatWidget(QWidget):
    """
    A chat widget for displaying messages in a scrollable area.
    
    Manages message history, scrolling, and message bubble display
    with smooth animations and professional styling.
    """
    
    # Signals
    message_clicked = pyqtSignal(str)  # Emitted when a message is clicked
    message_selected = pyqtSignal(str)  # Emitted when a message is selected
    message_added = pyqtSignal(str) # Emitted when a new message is added
    quick_reply_clicked = pyqtSignal(str) # Emitted when a quick reply is clicked
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the chat widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.messages: Dict[str, MessageBubble] = {}
        self.message_data: Dict[str, Dict[str, Any]] = {}
        self.selected_message_id: Optional[str] = None
        
        self.setup_ui()
        self.setup_styling()
        self.setup_behavior()
        
        # Auto-scroll timer
        self.auto_scroll_timer = QTimer()
        self.auto_scroll_timer.setSingleShot(True)
        self.auto_scroll_timer.timeout.connect(self.scroll_to_bottom)
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Scroll area widget
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scrollAreaWidgetContents")
        self.scroll_area.setWidget(self.scroll_widget)
        
        # Messages layout
        self.messages_layout = QVBoxLayout(self.scroll_widget)
        self.messages_layout.setContentsMargins(16, 16, 16, 16)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()
        
        # Welcome message
        self.show_welcome_message()
        
        # Add scroll area to main layout
        layout.addWidget(self.scroll_area)
        
        # Set up styling
        self.setup_styling()
    
    def setup_welcome_message(self):
        """Set up the welcome message."""
        welcome_content = """
        Hi there! Nice to see you 😊 
        
        I'm your OSI Work Buddy - your AI assistant for Azure DevOps, OSI One, and Microsoft Teams integration.
        
        What can I help you with today?
        """
        
        self.add_message(welcome_content, "assistant", "welcome")
        
        # Add quick reply options
        self.add_quick_replies([
            "Show my tasks",
            "Update work item",
            "Fill timesheet"
        ])
    
    def setup_styling(self):
        """Set up the styling for the chat widget."""
        # Apply styling from styles module
        from .styles import get_application_style
        self.setStyleSheet(get_application_style())
    
    def setup_behavior(self):
        """Set up interactive behavior for the chat widget."""
        # Connect scroll area signals
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)
        
        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def add_message(self, content: str, sender: str = "assistant", message_id: str = None):
        """
        Add a message to the chat.
        
        Args:
            content: Message content
            sender: Message sender ("user" or "assistant")
            message_id: Optional message ID
        """
        # Create message bubble
        message_bubble = MessageBubble(content, sender, message_id)
        
        # Add to layout (before the stretch)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_bubble)
        
        # Store message reference
        if message_id:
            self.messages[message_id] = message_bubble
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
        
        # Emit message added signal
        self.message_added.emit(message_id or str(len(self.messages)))
    
    def add_quick_replies(self, replies: list):
        """
        Add quick reply buttons.
        
        Args:
            replies: List of reply options
        """
        # Create quick reply widget
        quick_reply_widget = QWidget()
        quick_reply_layout = QHBoxLayout(quick_reply_widget)
        quick_reply_layout.setContentsMargins(8, 4, 8, 4)
        quick_reply_layout.setSpacing(8)
        
        for i, reply in enumerate(replies):
            button = QPushButton(reply)
            button.setObjectName("quickReplyButton" if i == 0 else "quickReplyButtonSecondary")
            button.clicked.connect(lambda checked, r=reply: self.quick_reply_clicked.emit(r))
            quick_reply_layout.addWidget(button)
        
        quick_reply_layout.addStretch()
        
        # Add to layout
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, quick_reply_widget)
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def hide_quick_replies(self):
        """Hide quick reply buttons."""
        # Remove quick reply widgets
        for i in reversed(range(self.messages_layout.count())):
            widget = self.messages_layout.itemAt(i).widget()
            if widget and isinstance(widget, QWidget) and widget != self.scroll_widget:
                # Check if it's a quick reply widget
                if widget.layout() and any(isinstance(child, QPushButton) for child in widget.findChildren(QPushButton)):
                    widget.deleteLater()
    
    def hide_welcome_message(self):
        """Hide the welcome message with animation."""
        animation = QPropertyAnimation(self.welcome_label, b"maximumHeight")
        animation.setDuration(300)
        animation.setStartValue(self.welcome_label.height())
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.finished.connect(self.welcome_label.hide)
        animation.start()
    
    def show_welcome_message(self):
        """Show the welcome message."""
        welcome_content = """
        Hi there! Nice to see you 😊 
        
        I'm your OSI Work Buddy - your AI assistant for Azure DevOps, OSI One, and Microsoft Teams integration.
        
        What can I help you with today?
        """
        
        self.add_message(welcome_content, "assistant", "welcome")
        
        # Add quick reply options
        self.add_quick_replies([
            "Show my tasks",
            "Update work item",
            "Fill timesheet"
        ])
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def scroll_to_top(self):
        """Scroll to the top of the chat."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(0)
    
    def on_scroll(self, value: int):
        """Handle scroll events."""
        # You can add scroll-based features here
        # For example, lazy loading of older messages
        pass
    
    def on_message_clicked(self, message_id: str):
        """Handle message click events."""
        self.message_clicked.emit(message_id)
        self.selected_message_id = message_id
        self.message_selected.emit(message_id)
    
    def get_message_by_id(self, message_id: str) -> Optional[MessageBubble]:
        """
        Get a message bubble by its ID.
        
        Args:
            message_id: The message ID
            
        Returns:
            MessageBubble or None if not found
        """
        return self.messages.get(message_id)
    
    def update_message(self, message_id: str, new_content: str):
        """
        Update an existing message.
        
        Args:
            message_id: The message ID to update
            new_content: New message content
        """
        message = self.get_message_by_id(message_id)
        if message:
            message.update_message(new_content)
            # Update stored data
            self.message_data[message_id] = message.get_message_data()
    
    def delete_message(self, message_id: str):
        """
        Delete a message from the chat.
        
        Args:
            message_id: The message ID to delete
        """
        message = self.get_message_by_id(message_id)
        if message:
            # Remove from layout
            self.messages_layout.removeWidget(message)
            message.deleteLater()
            
            # Remove from lists
            del self.messages[message_id]
            if message_id in self.message_data:
                del self.message_data[message_id]
            
            # Clear selection if this was the selected message
            if self.selected_message_id == message_id:
                self.selected_message_id = None
    
    def clear_messages(self):
        """Clear all messages."""
        # Clear stored messages
        self.messages.clear()
        
        # Remove all widgets except the stretch
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Show welcome message again
        self.show_welcome_message()
    
    def get_message_count(self) -> int:
        """Get the number of messages."""
        return len(self.messages)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history as a list of dictionaries.
        
        Returns:
            List of message data dictionaries
        """
        return list(self.message_data.values())
    
    def export_conversation(self, file_path: str) -> bool:
        """
        Export conversation to file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("OSI Work Buddy - Conversation Export\n")
                f.write("=" * 50 + "\n\n")
                
                for message_id, message_bubble in self.messages.items():
                    sender = "You" if message_bubble.sender == "user" else "OSI Work Buddy"
                    timestamp = message_bubble.timestamp_label.text()
                    content = message_bubble.content
                    
                    f.write(f"[{timestamp}] {sender}:\n{content}\n\n")
            
            return True
        except Exception as e:
            print(f"Error exporting conversation: {e}")
            return False
    
    def show_context_menu(self, position):
        """Show context menu for the chat widget."""
        from PyQt5.QtWidgets import QMenu, QAction
        
        menu = QMenu(self)
        
        # Clear chat action
        clear_action = QAction("Clear Chat", self)
        clear_action.triggered.connect(self.clear_messages)
        menu.addAction(clear_action)
        
        # Export conversation action
        if self.get_message_count() > 0:
            export_action = QAction("Export Conversation", self)
            export_action.triggered.connect(self.export_conversation_dialog)
            menu.addAction(export_action)
        
        # Separator
        if self.get_message_count() > 0:
            menu.addSeparator()
        
        # Scroll actions
        scroll_top_action = QAction("Scroll to Top", self)
        scroll_top_action.triggered.connect(self.scroll_to_top)
        menu.addAction(scroll_top_action)
        
        scroll_bottom_action = QAction("Scroll to Bottom", self)
        scroll_bottom_action.triggered.connect(self.scroll_to_bottom)
        menu.addAction(scroll_bottom_action)
        
        menu.exec_(self.mapToGlobal(position))
    
    def export_conversation_dialog(self):
        """Show dialog to export conversation."""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Conversation",
            f"osi_agent_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            if self.export_conversation(file_path):
                # Show success notification
                self.show_export_success(file_path)
            else:
                # Show error notification
                self.show_export_error()
    
    def show_export_success(self, file_path: str):
        """Show success notification for export."""
        # You can implement a notification system here
        print(f"Conversation exported successfully to: {file_path}")
    
    def show_export_error(self):
        """Show error notification for export."""
        # You can implement a notification system here
        print("Error exporting conversation")
    
    def set_typing_indicator(self, is_typing: bool):
        """
        Show or hide typing indicator.
        
        Args:
            is_typing: Whether to show typing indicator
        """
        if is_typing:
            # Add typing indicator message
            typing_message = "OSI Work Buddy is typing..."
            self.add_message(typing_message, "assistant", "typing")
        else:
            # Remove typing indicator if it exists
            if "typing" in self.messages:
                typing_bubble = self.messages["typing"]
                self.messages_layout.removeWidget(typing_bubble)
                typing_bubble.deleteLater()
                del self.messages["typing"]
    
    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        
        # Recalculate message heights
        for message in self.messages.values():
            message.resizeEvent(event)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Add keyboard shortcuts here
        if event.key() == Qt.Key_Home:
            self.scroll_to_top()
        elif event.key() == Qt.Key_End:
            self.scroll_to_bottom()
        else:
            super().keyPressEvent(event) 