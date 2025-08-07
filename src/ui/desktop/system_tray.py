"""
OSI ONE AGENT - System Tray Component

This module provides the SystemTray widget for system tray integration
with context menu and notifications for the desktop application.
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from .styles import OSI_COLORS

class SystemTray(QSystemTrayIcon):
    """
    System tray icon for the OSI ONE AGENT application.
    
    Provides system tray integration with context menu,
    notifications, and window management.
    """
    
    # Signals
    restore_requested = pyqtSignal()  # Emitted when restore is requested
    exit_requested = pyqtSignal()     # Emitted when exit is requested
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the system tray icon.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.parent_window = parent
        self.setup_icon()
        self.setup_tooltip()
        self.setup_context_menu()
        self.setup_behavior()
    
    def setup_icon(self):
        """Set up the system tray icon."""
        # Create a simple icon (you can replace with actual icon file)
        icon_pixmap = QPixmap(32, 32)
        icon_pixmap.fill(Qt.transparent)
        
        # Draw a simple brain icon
        from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
        
        painter = QPainter(icon_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw brain icon
        painter.setPen(QPen(QColor(OSI_COLORS['primary_blue']), 2))
        painter.setBrush(QBrush(QColor(OSI_COLORS['primary_blue'])))
        
        # Simple brain shape
        painter.drawEllipse(8, 8, 16, 16)
        painter.drawEllipse(12, 4, 8, 8)
        painter.drawEllipse(12, 20, 8, 8)
        
        painter.end()
        
        self.setIcon(QIcon(icon_pixmap))
    
    def setup_tooltip(self):
        """Set up the tooltip for the system tray icon."""
        self.setToolTip("OSI ONE AGENT\nAI-Powered Desktop Assistant")
    
    def setup_context_menu(self):
        """Set up the context menu for the system tray icon."""
        menu = QMenu()
        
        # Show/Hide action
        self.show_action = QAction("Show/Hide", self)
        self.show_action.setStatusTip("Show or hide the main window")
        self.show_action.triggered.connect(self.toggle_window_visibility)
        menu.addAction(self.show_action)
        
        menu.addSeparator()
        
        # Status action
        self.status_action = QAction("Status: Ready", self)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        # Message count action
        self.message_count_action = QAction("Messages: 0", self)
        self.message_count_action.setEnabled(False)
        menu.addAction(self.message_count_action)
        
        menu.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)
        
        # About action
        about_action = QAction("About", self)
        about_action.setStatusTip("About OSI ONE AGENT")
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.exit_application)
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)
    
    def setup_behavior(self):
        """Set up interactive behavior for the system tray icon."""
        # Connect activation signal
        self.activated.connect(self.handle_activation)
        
        # Connect context menu signals
        self.contextMenu().aboutToShow.connect(self.update_context_menu)
    
    def handle_activation(self, reason):
        """Handle system tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            # Double-click to show/hide window
            self.toggle_window_visibility()
        elif reason == QSystemTrayIcon.Trigger:
            # Single-click to show window
            self.show_window()
    
    def toggle_window_visibility(self):
        """Toggle main window visibility."""
        if self.parent_window and hasattr(self.parent_window, 'isVisible'):
            if self.parent_window.isVisible():
                self.parent_window.hide()
            else:
                self.show_window()
    
    def show_window(self):
        """Show the main window."""
        if self.parent_window:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()
            
            # Emit restore signal
            self.restore_requested.emit()
    
    def hide_window(self):
        """Hide the main window."""
        if self.parent_window:
            self.parent_window.hide()
    
    def update_context_menu(self):
        """Update the context menu with current status."""
        if self.parent_window:
            # Update status
            if hasattr(self.parent_window, 'status_label'):
                status = self.parent_window.status_label.text()
                self.status_action.setText(f"Status: {status}")
            
            # Update message count
            if hasattr(self.parent_window, 'chat_widget'):
                count = self.parent_window.chat_widget.get_message_count()
                self.message_count_action.setText(f"Messages: {count}")
            
            # Update show/hide action text
            if self.parent_window.isVisible():
                self.show_action.setText("Hide")
            else:
                self.show_action.setText("Show")
    
    def open_settings(self):
        """Open settings dialog."""
        # You can implement settings dialog here
        from PyQt5.QtWidgets import QMessageBox
        
        QMessageBox.information(
            self.parent_window,
            "Settings",
            "Settings dialog not implemented yet.\n\n"
            "This will include:\n"
            "• API configuration\n"
            "• Theme preferences\n"
            "• Notification settings\n"
            "• Voice input settings"
        )
    
    def show_about(self):
        """Show about dialog."""
        from PyQt5.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self.parent_window,
            "About OSI ONE AGENT",
            """
            <h2>🧠 OSI ONE AGENT</h2>
            <p><b>AI-Powered Desktop Assistant for OSI Digital Engineers</b></p>
            <p>Version: 1.0.0</p>
            <p>Built with PyQt5 and OpenAI GPT-4</p>
            <p>© 2024 OSI Digital</p>
            """
        )
    
    def exit_application(self):
        """Exit the application."""
        # Emit exit signal
        self.exit_requested.emit()
        
        # Close application
        if self.parent_window:
            self.parent_window.close()
    
    def show_notification(self, title: str, message: str, duration: int = 5000):
        """
        Show a system tray notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        self.showMessage(title, message, QSystemTrayIcon.Information, duration)
    
    def show_error_notification(self, title: str, message: str, duration: int = 5000):
        """
        Show an error notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        self.showMessage(title, message, QSystemTrayIcon.Critical, duration)
    
    def show_warning_notification(self, title: str, message: str, duration: int = 5000):
        """
        Show a warning notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        self.showMessage(title, message, QSystemTrayIcon.Warning, duration)
    
    def update_status(self, status: str):
        """
        Update the status in the context menu.
        
        Args:
            status: New status text
        """
        self.status_action.setText(f"Status: {status}")
    
    def update_message_count(self, count: int):
        """
        Update the message count in the context menu.
        
        Args:
            count: New message count
        """
        self.message_count_action.setText(f"Messages: {count}")
    
    def set_icon_color(self, color: str):
        """
        Set the icon color.
        
        Args:
            color: Color hex code
        """
        # You can implement dynamic icon color changes here
        pass
    
    def flash_icon(self, duration: int = 1000):
        """
        Flash the icon to draw attention.
        
        Args:
            duration: Flash duration in milliseconds
        """
        # You can implement icon flashing here
        pass 