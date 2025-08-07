"""
OSI ONE AGENT - Input Widget Component

This module provides the InputWidget for text input with auto-complete,
voice input capabilities, and send functionality for the chat interface.
"""

from typing import List, Optional, Callable
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, 
    QPushButton, QCompleter, QListWidget, QFrame,
    QLabel, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QStringListModel
from PyQt5.QtGui import QFont, QIcon, QPixmap, QKeySequence
from .styles import OSI_COLORS

class InputWidget(QWidget):
    """
    An input widget for text entry with auto-complete and voice input.
    
    Provides a modern input interface with command suggestions,
    voice input capability, and send functionality.
    """
    
    # Signals
    message_sent = pyqtSignal(str)  # Emitted when a message is sent
    voice_input_requested = pyqtSignal()  # Emitted when voice input is requested
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the input widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.suggestions: List[str] = []
        self.command_history: List[str] = []
        self.current_suggestion_index: int = -1
        
        self.setup_ui()
        self.setup_styling()
        self.setup_behavior()
        self.setup_suggestions()
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Input area frame
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)
        
        # Emoji button
        self.emoji_button = QPushButton("😊")
        self.emoji_button.setObjectName("emojiButton")
        self.emoji_button.setFixedSize(32, 32)
        self.emoji_button.setToolTip("Add emoji")
        self.emoji_button.clicked.connect(self.show_emoji_picker)
        
        # Attachment button
        self.attachment_button = QPushButton("📎")
        self.attachment_button.setObjectName("attachmentButton")
        self.attachment_button.setFixedSize(32, 32)
        self.attachment_button.setToolTip("Attach file")
        self.attachment_button.clicked.connect(self.attach_file)
        
        # Message input field
        self.message_input = QLineEdit()
        self.message_input.setObjectName("messageInput")
        self.message_input.setPlaceholderText("Enter your message...")
        self.message_input.setMinimumHeight(40)
        self.message_input.returnPressed.connect(self.send_message)
        
        # Send button
        self.send_button = QPushButton("➤")
        self.send_button.setObjectName("sendButton")
        self.send_button.setFixedSize(40, 40)
        self.send_button.setToolTip("Send message")
        self.send_button.clicked.connect(self.send_message)
        
        # Add widgets to input layout
        input_layout.addWidget(self.emoji_button)
        input_layout.addWidget(self.attachment_button)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        # Add input frame to main layout
        layout.addWidget(input_frame)
        
        # Quick reply buttons (initially hidden)
        self.quick_reply_layout = QHBoxLayout()
        self.quick_reply_layout.setSpacing(8)
        layout.addLayout(self.quick_reply_layout)
        
        # Hide quick replies initially
        self.hide_quick_replies()
    
    def setup_styling(self):
        """Set up the styling for the input widget."""
        # Apply styling from styles module
        from .styles import get_application_style
        self.setStyleSheet(get_application_style())
    
    def setup_behavior(self):
        """Set up interactive behavior for the input widget."""
        # Connect signals
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)
        # self.voice_button.clicked.connect(self.request_voice_input) # This line was removed from the new_code, so it's removed here.
        
        # Text input events
        self.message_input.textChanged.connect(self.on_text_changed)
        self.message_input.focusInEvent = self.on_focus_in
        self.message_input.focusOutEvent = self.on_focus_out
        
        # Suggestions events
        # self.suggestions_widget.itemClicked.connect(self.on_suggestion_selected) # This line was removed from the new_code, so it's removed here.
        # self.suggestions_widget.itemDoubleClicked.connect(self.on_suggestion_double_clicked) # This line was removed from the new_code, so it's removed here.
        
        # Keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        from PyQt5.QtWidgets import QShortcut
        
        # Voice input shortcut
        voice_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        voice_shortcut.activated.connect(self.request_voice_input)
        
        # Send message shortcut
        send_shortcut = QShortcut(QKeySequence("Return"), self)
        send_shortcut.activated.connect(self.send_message)
        
        # Escape to clear input
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.clear_input)
    
    def setup_suggestions(self):
        """Set up command suggestions."""
        self.suggestions = [
            "Show my tasks for this sprint",
            "Get my recent pull requests",
            "Update TASK-12345 Status -> Active",
            "Update TASK-12345 Start Date -> 08/11/2025",
            "Update TASK-12345 Remaining -> 8 and Completed -> 4",
            "Fill my timesheet based on last week's PRs",
            "Show my meetings today",
            "What are my assigned work items?",
            "Update USER STORY-67890 Assignee -> \"John Doe\"",
            "Show tasks assigned to me in the current sprint",
            "Get all my meetings with the development team this month",
            "Create a summary of my work from last week",
            "Show my productivity metrics for this month",
            "Generate a report of my completed tasks and meetings",
            "Update following individual tasks:",
            "TASK 51311 -> Start Date -> 08/08/2025 Finish Date -> 08/11/2025",
            "TASK 51312 -> Start Date -> 08/11/2025 Finish Date -> 08/15/2025"
        ]
        
        # Add suggestions to list widget
        self.update_suggestions_list()
    
    def update_suggestions_list(self):
        """Update the suggestions list widget."""
        # self.suggestions_widget.clear() # This line was removed from the new_code, so it's removed here.
        
        # current_text = self.text_input.text().lower() # This line was removed from the new_code, so it's removed here.
        # if not current_text: # This line was removed from the new_code, so it's removed here.
        #     # Show all suggestions when input is empty # This line was removed from the new_code, so it's removed here.
        #     for suggestion in self.suggestions[:10]:  # Limit to first 10 # This line was removed from the new_code, so it's removed here.
        #         self.suggestions_widget.addItem(suggestion) # This line was removed from the new_code, so it's removed here.
        # else: # This line was removed from the new_code, so it's removed here.
        #     # Filter suggestions based on current text # This line was removed from the new_code, so it's removed here.
        #     filtered_suggestions = [ # This line was removed from the new_code, so it's removed here.
        #         suggestion for suggestion in self.suggestions # This line was removed from the new_code, so it's removed here.
        #         if current_text in suggestion.lower() # This line was removed from the new_code, so it's removed here.
        #     ] # This line was removed from the new_code, so it's removed here.
            
        #     for suggestion in filtered_suggestions[:10]:  # Limit to first 10 # This line was removed from the new_code, so it's removed here.
        #         self.suggestions_widget.addItem(suggestion) # This line was removed from the new_code, so it's removed here.
    
    def on_text_changed(self, text: str):
        """Handle text input changes."""
        # Update suggestions
        self.update_suggestions_list()
        
        # Show/hide suggestions
        # if text and self.suggestions_widget.count() > 0: # This line was removed from the new_code, so it's removed here.
        #     self.suggestions_widget.setVisible(True) # This line was removed from the new_code, so it's removed here.
        # else: # This line was removed from the new_code, so it's removed here.
        #     self.suggestions_widget.setVisible(False) # This line was removed from the new_code, so it's removed here.
        
        # Update send button state
        self.send_button.setEnabled(bool(text.strip()))
        
        # Reset suggestion index
        self.current_suggestion_index = -1
    
    def on_focus_in(self, event):
        """Handle focus in events."""
        # Show suggestions if there's text
        # if self.text_input.text() and self.suggestions_widget.count() > 0: # This line was removed from the new_code, so it's removed here.
        #     self.suggestions_widget.setVisible(True) # This line was removed from the new_code, so it's removed here.
        
        # Call original focusInEvent
        QLineEdit.focusInEvent(self.message_input, event)
    
    def on_focus_out(self, event):
        """Handle focus out events."""
        # Hide suggestions after a delay
        QTimer.singleShot(200, self.hide_suggestions)
        
        # Call original focusOutEvent
        QLineEdit.focusOutEvent(self.message_input, event)
    
    def hide_suggestions(self):
        """Hide the suggestions list."""
        # self.suggestions_widget.setVisible(False) # This line was removed from the new_code, so it's removed here.
    
    def on_suggestion_selected(self, item):
        """Handle suggestion selection."""
        # selected_text = item.text() # This line was removed from the new_code, so it's removed here.
        # self.text_input.setText(selected_text) # This line was removed from the new_code, so it's removed here.
        # self.text_input.setFocus() # This line was removed from the new_code, so it's removed here.
        # self.hide_suggestions() # This line was removed from the new_code, so it's removed here.
    
    def on_suggestion_double_clicked(self, item):
        """Handle suggestion double-click."""
        # selected_text = item.text() # This line was removed from the new_code, so it's removed here.
        # self.text_input.setText(selected_text) # This line was removed from the new_code, so it's removed here.
        # self.send_message() # This line was removed from the new_code, so it's removed here.
    
    def send_message(self):
        """Send the current message."""
        text = self.message_input.text().strip()
        if text:
            # Emit message sent signal
            self.message_sent.emit(text)
            
            # Clear input
            self.message_input.clear()
            
            # Hide quick replies if they exist
            if hasattr(self.parent(), 'chat_widget'):
                self.parent().chat_widget.hide_quick_replies()
    
    def show_emoji_picker(self):
        """Show emoji picker (placeholder for now)."""
        # Simple emoji list for now
        emojis = ["😊", "👍", "👎", "❤️", "🎉", "🔥", "💡", "✅", "❌", "📝"]
        
        # For now, just add a smiley to the input
        current_text = self.message_input.text()
        self.message_input.setText(current_text + "😊")
    
    def attach_file(self):
        """Open file attachment dialog."""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Attach File",
            "",
            "All Files (*);;Text Files (*.txt);;Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            # For now, just add the file path to the message
            current_text = self.message_input.text()
            self.message_input.setText(f"{current_text} 📎 {file_path}")
    
    def set_input_text(self, text: str):
        """Set the input text."""
        self.message_input.setText(text)
    
    def set_send_enabled(self, enabled: bool):
        """Enable or disable the send button."""
        self.send_button.setEnabled(enabled)
        self.message_input.setEnabled(enabled)
    
    def request_voice_input(self):
        """Request voice input."""
        self.voice_input_requested.emit()
    
    def focus_input(self):
        """Focus the input field."""
        self.message_input.setFocus()
    
    def clear_input(self):
        """Clear the input field."""
        self.message_input.clear()
        self.message_input.setFocus()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if event.modifiers() == Qt.ShiftModifier:
                # Shift+Enter for new line
                super().keyPressEvent(event)
            else:
                # Enter to send
                self.send_message()
        else:
            super().keyPressEvent(event)
    
    def handle_tab_completion(self):
        """Handle tab completion for suggestions."""
        # current_text = self.text_input.text().lower() # This line was removed from the new_code, so it's removed here.
        # if not current_text: # This line was removed from the new_code, so it's removed here.
        #     return # This line was removed from the new_code, so it's removed here.
        
        # # Find matching suggestions # This line was removed from the new_code, so it's removed here.
        # matching_suggestions = [ # This line was removed from the new_code, so it's removed here.
        #     suggestion for suggestion in self.suggestions # This line was removed from the new_code, so it's removed here.
        #     if suggestion.lower().startswith(current_text) # This line was removed from the new_code, so it's removed here.
        # ] # This line was removed from the new_code, so it's removed here.
        
        # if matching_suggestions: # This line was removed from the new_code, so it's removed here.
        #     # Use the first matching suggestion # This line was removed from the new_code, so it's removed here.
        #     completion = matching_suggestions[0] # This line was removed from the new_code, so it's removed here.
        #     self.text_input.setText(completion) # This line was removed from the new_code, so it's removed here.
        #     self.text_input.setCursorPosition(len(current_text)) # This line was removed from the new_code, so it's removed here.
    
    def navigate_suggestions(self, direction: int):
        """Navigate through suggestions with arrow keys."""
        # if not self.suggestions_widget.isVisible() or self.suggestions_widget.count() == 0: # This line was removed from the new_code, so it's removed here.
        #     return # This line was removed from the new_code, so it's removed here.
        
        # # Calculate new index # This line was removed from the new_code, so it's removed here.
        # new_index = self.current_suggestion_index + direction # This line was removed from the new_code, so it's removed here.
        
        # if new_index >= self.suggestions_widget.count(): # This line was removed from the new_code, so it's removed here.
        #     new_index = 0 # This line was removed from the new_code, so it's removed here.
        # elif new_index < 0: # This line was removed from the new_code, so it's removed here.
        #     new_index = self.suggestions_widget.count() - 1 # This line was removed from the new_code, so it's removed here.
        
        # # Set selection # This line was removed from the new_code, so it's removed here.
        # self.current_suggestion_index = new_index # This line was removed from the new_code, so it's removed here.
        # self.suggestions_widget.setCurrentRow(new_index) # This line was removed from the new_code, so it's removed here.
        
        # # Update input text # This line was removed from the new_code, so it's removed here.
        # if new_index >= 0: # This line was removed from the new_code, so it's removed here.
        #     item = self.suggestions_widget.item(new_index) # This line was removed from the new_code, so it's removed here.
        #     if item: # This line was removed from the new_code, so it's removed here.
        #         self.text_input.setText(item.text()) # This line was removed from the new_code, so it's removed here.
    
    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        
        # Adjust suggestions list height if needed
        # if self.suggestions_widget.isVisible(): # This line was removed from the new_code, so it's removed here.
        #     max_height = min(150, self.suggestions_widget.count() * 30 + 20) # This line was removed from the new_code, so it's removed here.
        #     self.suggestions_widget.setMaximumHeight(max_height) 

    def hide_quick_replies(self):
        """Hide quick reply buttons."""
        # This method is called from the main window
        # Quick replies are handled by the chat widget
        pass 