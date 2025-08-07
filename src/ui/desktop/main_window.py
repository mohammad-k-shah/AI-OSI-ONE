"""
OSI ONE AGENT - Main Window Component

This module provides the main application window that brings together
all UI components and provides the complete desktop application interface.
"""

import sys
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QToolBar, QStatusBar, QAction, QMenu,
    QMessageBox, QFileDialog, QApplication, QSplitter,
    QLabel, QFrame, QSizePolicy, QPushButton
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QFont, QIcon, QPixmap, QKeySequence
from .chat_widget import ChatWidget
from .input_widget import InputWidget
from .system_tray import SystemTray
from .notifications import NotificationManager
from .voice_input import VoiceInputHandler
from .styles import get_application_style, get_dark_palette, get_application_font, OSI_COLORS

class AgentWorker(QObject):
    """
    Worker thread for handling agent operations asynchronously.
    """
    
    # Signals
    response_received = pyqtSignal(str)  # Emitted when agent responds
    error_occurred = pyqtSignal(str)     # Emitted when an error occurs
    processing_started = pyqtSignal()     # Emitted when processing starts
    processing_finished = pyqtSignal()    # Emitted when processing finishes
    
    def __init__(self, agent):
        """
        Initialize the agent worker.
        
        Args:
            agent: The agent orchestrator instance
        """
        super().__init__()
        self.agent = agent
    
    def process_message(self, message: str):
        """
        Process a message asynchronously.
        
        Args:
            message: The message to process
        """
        try:
            self.processing_started.emit()
            
            # Create event loop for async operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Process the message
            result = loop.run_until_complete(self.agent.process_query(message))
            
            if result.get("success", False):
                response = result.get("message", "No response received")
                self.response_received.emit(response)
            else:
                error_msg = result.get("message", "Unknown error occurred")
                self.error_occurred.emit(error_msg)
            
            loop.close()
            
        except Exception as e:
            self.error_occurred.emit(f"Error processing message: {str(e)}")
        finally:
            self.processing_finished.emit()

class OSIAgentGUI(QMainWindow):
    """
    Main application window for the OSI ONE AGENT desktop application.
    
    Provides a complete desktop interface with chat functionality,
    system tray integration, and professional appearance.
    """
    
    def __init__(self, agent=None, parent: Optional[QWidget] = None):
        """
        Initialize the main window.
        
        Args:
            agent: The agent orchestrator instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.agent = agent
        self.worker_thread = None
        self.worker = None
        self.system_tray = None
        self.notification_manager = None
        self.voice_handler = None
        
        self.setup_ui()
        self.setup_styling()
        self.setup_menu_bar()
        self.setup_tool_bar()
        self.setup_status_bar()
        self.setup_system_tray()
        self.setup_notifications()
        self.setup_voice_input()
        self.setup_worker_thread()
        self.setup_behavior()
        
        # Window state
        self.is_minimized_to_tray = False
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Set window properties
        self.setWindowTitle("OSI Work Buddy")
        self.setWindowIcon(self.get_application_icon())
        self.setGeometry(100, 100, 400, 600)
        self.setMinimumSize(350, 500)
        self.setMaximumSize(500, 800)
        
        # Remove window frame for modern look
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header Section (Dark Blue)
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setMaximumHeight(80)
        header_frame.setMinimumHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 16, 16, 16)
        header_layout.setSpacing(12)
        
        # Avatar (placeholder for now)
        avatar_label = QLabel("🧠")
        avatar_label.setObjectName("avatarLabel")
        avatar_label.setStyleSheet("""
            QLabel#avatarLabel {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                padding: 8px;
                font-size: 20px;
                color: white;
            }
        """)
        avatar_label.setFixedSize(40, 40)
        
        # Name and status
        name_status_layout = QVBoxLayout()
        name_status_layout.setSpacing(2)
        
        name_label = QLabel("Chat with OSI Work Buddy")
        name_label.setObjectName("titleLabel")
        
        status_label = QLabel("AI Assistant Online")
        status_label.setObjectName("statusLabel")
        
        name_status_layout.addWidget(name_label)
        name_status_layout.addWidget(status_label)
        
        # Right side buttons
        right_buttons_layout = QHBoxLayout()
        right_buttons_layout.setSpacing(8)
        
        # Settings button
        settings_button = QPushButton("⋮")
        settings_button.setObjectName("settingsButton")
        settings_button.setFixedSize(32, 32)
        settings_button.setToolTip("Settings")
        
        # Minimize button
        minimize_button = QPushButton("⌄")
        minimize_button.setObjectName("minimizeButton")
        minimize_button.setFixedSize(32, 32)
        minimize_button.setToolTip("Minimize")
        minimize_button.clicked.connect(self.minimize_to_tray)
        
        right_buttons_layout.addWidget(settings_button)
        right_buttons_layout.addWidget(minimize_button)
        
        # Add widgets to header
        header_layout.addWidget(avatar_label)
        header_layout.addLayout(name_status_layout)
        header_layout.addStretch()
        header_layout.addLayout(right_buttons_layout)
        
        # Chat widget
        self.chat_widget = ChatWidget()
        
        # Input widget
        self.input_widget = InputWidget()
        
        # Add widgets to main layout
        layout.addWidget(header_frame)
        layout.addWidget(self.chat_widget)
        layout.addWidget(self.input_widget)
        
        # Set size policies
        self.chat_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    def setup_styling(self):
        """Set up the styling for the main window."""
        # Apply application style
        self.setStyleSheet(get_application_style())
        
        # Apply dark palette
        self.setPalette(get_dark_palette())
        
        # Apply application font
        self.setFont(get_application_font())
        
        # Title frame styling
        self.findChild(QFrame, "headerFrame").setStyleSheet(f"""
            QFrame#headerFrame {{
                background-color: {OSI_COLORS['header_blue']};
                border-bottom: 1px solid {OSI_COLORS['border']};
            }}
        """)
        self.findChild(QLabel, "titleLabel").setStyleSheet("""
            QLabel#titleLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.findChild(QLabel, "statusLabel").setStyleSheet("""
            QLabel#statusLabel {
                color: #00CC66; /* Green for online status */
                font-size: 14px;
            }
        """)
        self.findChild(QPushButton, "settingsButton").setStyleSheet("""
            QPushButton#settingsButton {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                color: white;
                font-size: 18px;
                padding: 4px;
            }
        """)
        self.findChild(QPushButton, "minimizeButton").setStyleSheet("""
            QPushButton#minimizeButton {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                color: white;
                font-size: 18px;
                padding: 4px;
            }
        """)
    
    def setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Export conversation action
        export_action = QAction("&Export Conversation", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.setStatusTip("Export conversation to file")
        export_action.triggered.connect(self.export_conversation)
        file_menu.addAction(export_action)
        
        # Clear conversation action
        clear_action = QAction("&Clear Conversation", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.setStatusTip("Clear all messages")
        clear_action.triggered.connect(self.clear_conversation)
        file_menu.addAction(clear_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Copy action
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.setStatusTip("Copy selected text")
        edit_menu.addAction(copy_action)
        
        # Paste action
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        paste_action.setStatusTip("Paste text")
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Toggle system tray action
        self.tray_action = QAction("&Minimize to Tray", self)
        self.tray_action.setShortcut(QKeySequence("Ctrl+T"))
        self.tray_action.setStatusTip("Minimize to system tray")
        self.tray_action.triggered.connect(self.minimize_to_tray)
        view_menu.addAction(self.tray_action)
        
        # Always on top action
        self.always_on_top_action = QAction("&Always on Top", self)
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.setStatusTip("Keep window always on top")
        self.always_on_top_action.triggered.connect(self.toggle_always_on_top)
        view_menu.addAction(self.always_on_top_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About OSI ONE AGENT")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Help action
        help_action = QAction("&Help", self)
        help_action.setShortcut(QKeySequence("F1"))
        help_action.setStatusTip("Show help")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
    
    def setup_tool_bar(self):
        """Set up the tool bar."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        # Send action
        send_action = QAction("Send", self)
        send_action.setIcon(self.get_icon("send"))
        send_action.setStatusTip("Send message")
        send_action.triggered.connect(self.input_widget.send_message)
        toolbar.addAction(send_action)
        
        # Voice action
        voice_action = QAction("Voice", self)
        voice_action.setIcon(self.get_icon("voice"))
        voice_action.setStatusTip("Voice input")
        voice_action.triggered.connect(self.input_widget.request_voice_input)
        toolbar.addAction(voice_action)
        
        toolbar.addSeparator()
        
        # Clear action
        clear_action = QAction("Clear", self)
        clear_action.setIcon(self.get_icon("clear"))
        clear_action.setStatusTip("Clear conversation")
        clear_action.triggered.connect(self.clear_conversation)
        toolbar.addAction(clear_action)
        
        # Export action
        export_action = QAction("Export", self)
        export_action.setIcon(self.get_icon("export"))
        export_action.setStatusTip("Export conversation")
        export_action.triggered.connect(self.export_conversation)
        toolbar.addAction(export_action)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        status_bar = self.statusBar()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        status_bar.addWidget(self.status_label)
        
        # Message count
        self.message_count_label = QLabel("Messages: 0")
        self.message_count_label.setObjectName("messageCountLabel")
        status_bar.addPermanentWidget(self.message_count_label)
    
    def setup_system_tray(self):
        """Set up the system tray."""
        try:
            self.system_tray = SystemTray(self)
            if self.system_tray.isSystemTrayAvailable():
                self.system_tray.show()
            else:
                print("System tray is not available on this system")
                self.system_tray = None
        except Exception as e:
            print(f"Failed to initialize system tray: {e}")
            self.system_tray = None
    
    def setup_notifications(self):
        """Set up the notification manager."""
        self.notification_manager = NotificationManager(self)
    
    def setup_voice_input(self):
        """Set up the voice input handler."""
        self.voice_handler = VoiceInputHandler(self)
        self.voice_handler.voice_text_received.connect(self.handle_voice_input)
    
    def setup_worker_thread(self):
        """Set up the worker thread for agent operations."""
        if self.agent:
            self.worker_thread = QThread()
            self.worker = AgentWorker(self.agent)
            self.worker.moveToThread(self.worker_thread)
            
            # Connect signals
            self.worker.response_received.connect(self.handle_agent_response)
            self.worker.error_occurred.connect(self.handle_agent_error)
            self.worker.processing_started.connect(self.handle_processing_started)
            self.worker.processing_finished.connect(self.handle_processing_finished)
            
            # Start thread
            self.worker_thread.start()
    
    def setup_behavior(self):
        """Set up interactive behavior for the main window."""
        # Connect input widget signals
        self.input_widget.message_sent.connect(self.handle_user_message)
        self.input_widget.voice_input_requested.connect(self.handle_voice_request)
        
        # Connect chat widget signals
        self.chat_widget.message_clicked.connect(self.handle_message_clicked)
        
        # Window events
        self.closeEvent = self.handle_close_event
        self.changeEvent = self.handle_change_event
    
    def handle_user_message(self, message: str):
        """Handle user message input."""
        # Add user message to chat
        self.chat_widget.add_message(message, "user")
        
        # Update message count
        self.update_message_count()
        
        # Process with agent if available
        if self.worker:
            self.worker.process_message(message)
        else:
            # Fallback response
            self.chat_widget.add_message(
                "Agent is not available. Please check your configuration.",
                "assistant"
            )
    
    def handle_agent_response(self, response: str):
        """Handle agent response."""
        # Add assistant response to chat
        self.chat_widget.add_message(response, "assistant")
        
        # Update message count
        self.update_message_count()
        
        # Show notification if window is minimized
        if self.isMinimized() or self.is_minimized_to_tray:
            self.notification_manager.show_notification(
                "OSI ONE AGENT",
                "New response received",
                "Click to view"
            )
    
    def handle_agent_error(self, error: str):
        """Handle agent error."""
        # Add error message to chat
        self.chat_widget.add_message(
            f"❌ Error: {error}",
            "assistant"
        )
        
        # Update message count
        self.update_message_count()
        
        # Show error notification
        self.notification_manager.show_notification(
            "OSI ONE AGENT",
            "Error occurred",
            error
        )
    
    def handle_processing_started(self):
        """Handle processing started."""
        self.status_label.setText("Processing...")
        
        # Show typing indicator
        self.chat_widget.set_typing_indicator(True)
        
        # Disable input
        self.input_widget.set_send_enabled(False)
    
    def handle_processing_finished(self):
        """Handle processing finished."""
        self.status_label.setText("Ready")
        
        # Hide typing indicator
        self.chat_widget.set_typing_indicator(False)
        
        # Enable input
        self.input_widget.set_send_enabled(True)
    
    def handle_voice_request(self):
        """Handle voice input request."""
        if self.voice_handler:
            self.voice_handler.start_voice_recognition()
    
    def handle_voice_input(self, text: str):
        """Handle voice input text."""
        self.input_widget.set_input_text(text)
    
    def handle_message_clicked(self, message_id: str):
        """Handle message click."""
        # You can add message-specific actions here
        pass
    
    def handle_close_event(self, event):
        """Handle window close event."""
        if self.system_tray and self.system_tray.isVisible():
            # Minimize to tray instead of closing
            self.hide()
            self.is_minimized_to_tray = True
            self.notification_manager.show_notification(
                "OSI ONE AGENT",
                "Minimized to tray",
                "Click tray icon to restore"
            )
            event.ignore()
        else:
            # Close application
            if self.worker_thread:
                self.worker_thread.quit()
                self.worker_thread.wait()
            event.accept()
    
    def handle_change_event(self, event):
        """Handle window state change events."""
        if event.type() == event.WindowStateChange:
            if self.isMinimized():
                self.is_minimized_to_tray = True
            else:
                self.is_minimized_to_tray = False
    
    def minimize_to_tray(self):
        """Minimize window to system tray."""
        self.hide()
        self.is_minimized_to_tray = True
        self.notification_manager.show_notification(
            "OSI ONE AGENT",
            "Minimized to tray",
            "Click tray icon to restore"
        )
    
    def restore_from_tray(self):
        """Restore window from system tray."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.is_minimized_to_tray = False
    
    def toggle_always_on_top(self, checked: bool):
        """Toggle always on top behavior."""
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
    
    def export_conversation(self):
        """Export conversation to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Conversation",
            f"osi_agent_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            if self.chat_widget.export_conversation(file_path):
                self.notification_manager.show_notification(
                    "OSI ONE AGENT",
                    "Export Successful",
                    f"Conversation exported to {file_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Export Error",
                    "Failed to export conversation. Please try again."
                )
    
    def clear_conversation(self):
        """Clear the conversation."""
        reply = QMessageBox.question(
            self,
            "Clear Conversation",
            "Are you sure you want to clear all messages?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.chat_widget.clear_messages()
            self.update_message_count()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About OSI ONE AGENT",
            """
            <h2>🧠 OSI ONE AGENT</h2>
            <p><b>AI-Powered Desktop Assistant for OSI Digital Engineers</b></p>
            <p>Version: 1.0.0</p>
            <p>Built with PyQt5 and OpenAI GPT-4</p>
            <p>© 2024 OSI Digital</p>
            """
        )
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
        <h2>OSI ONE AGENT Help</h2>
        
        <h3>Basic Commands:</h3>
        <ul>
            <li><b>Show my tasks for this sprint</b> - Get your current sprint tasks</li>
            <li><b>Update TASK-12345 Status -> Active</b> - Update work item status</li>
            <li><b>Fill my timesheet based on last week's PRs</b> - Auto-fill timesheet</li>
            <li><b>Show my meetings today</b> - Get today's calendar events</li>
        </ul>
        
        <h3>Keyboard Shortcuts:</h3>
        <ul>
            <li><b>Enter</b> - Send message</li>
            <li><b>Ctrl+V</b> - Voice input</li>
            <li><b>Ctrl+E</b> - Export conversation</li>
            <li><b>Ctrl+L</b> - Clear conversation</li>
            <li><b>Ctrl+T</b> - Minimize to tray</li>
            <li><b>Ctrl+Q</b> - Exit application</li>
        </ul>
        
        <h3>Features:</h3>
        <ul>
            <li>Natural language processing</li>
            <li>Azure DevOps integration</li>
            <li>OSI One automation</li>
            <li>Microsoft Teams integration</li>
            <li>Voice input support</li>
            <li>System tray integration</li>
        </ul>
        """
        
        QMessageBox.information(
            self,
            "OSI ONE AGENT Help",
            help_text
        )
    
    def update_message_count(self):
        """Update the message count in status bar."""
        count = self.chat_widget.get_message_count()
        self.message_count_label.setText(f"Messages: {count}")
    
    def get_application_icon(self) -> QIcon:
        """Get the application icon."""
        # You can replace this with an actual icon file
        return QIcon()
    
    def get_icon(self, name: str) -> QIcon:
        """Get an icon by name."""
        # You can implement icon loading here
        return QIcon()
    
    def set_agent(self, agent):
        """Set the agent orchestrator."""
        self.agent = agent
        if self.worker:
            self.worker.agent = agent
    
    def show_welcome_message(self):
        """Show a welcome message."""
        welcome_msg = """
        🧠 **Welcome to OSI ONE AGENT!**
        
        I'm your AI-powered desktop assistant for OSI Digital engineers.
        I can help you with:
        
        • **Azure DevOps** - Tasks, PRs, work items
        • **OSI One** - Timesheet automation
        • **Microsoft Teams** - Calendar and meetings
        • **Cross-platform integration** - Data aggregation
        
        **Try these commands:**
        • "Show my tasks for this sprint"
        • "Update TASK-12345 Status -> Active"
        • "Fill my timesheet based on last week's PRs"
        • "Show my meetings today"
        
        Type your request below to get started!
        """
        
        self.chat_widget.add_message(welcome_msg, "assistant")
    
    def closeEvent(self, event):
        """Override close event to handle tray behavior."""
        self.handle_close_event(event) 