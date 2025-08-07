"""
OSI ONE AGENT - Notification Manager Component

This module provides the NotificationManager for handling native Windows
notifications and system tray notifications for the desktop application.
"""

from typing import Optional
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

class NotificationManager(QObject):
    """
    Notification manager for the OSI ONE AGENT application.
    
    Handles native Windows notifications and system tray notifications
    with different types and durations.
    """
    
    # Signals
    notification_clicked = pyqtSignal(str)  # Emitted when notification is clicked
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the notification manager.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.parent_window = parent
        self.notification_queue = []
        self.is_showing_notification = False
        
        self.setup_behavior()
    
    def setup_behavior(self):
        """Set up notification behavior."""
        # You can add notification preferences here
        pass
    
    def show_notification(
        self, 
        title: str, 
        message: str, 
        notification_type: str = "info",
        duration: int = 5000,
        click_action: Optional[str] = None
    ):
        """
        Show a notification.
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification (info, success, warning, error)
            duration: Duration in milliseconds
            click_action: Action to perform when clicked
        """
        # Add to queue
        notification_data = {
            "title": title,
            "message": message,
            "type": notification_type,
            "duration": duration,
            "click_action": click_action
        }
        
        self.notification_queue.append(notification_data)
        
        # Show next notification if not currently showing
        if not self.is_showing_notification:
            self.show_next_notification()
    
    def show_next_notification(self):
        """Show the next notification in the queue."""
        if not self.notification_queue:
            self.is_showing_notification = False
            return
        
        notification_data = self.notification_queue.pop(0)
        self.is_showing_notification = True
        
        # Show system tray notification
        if self.parent_window and hasattr(self.parent_window, 'system_tray'):
            system_tray = self.parent_window.system_tray
            
            # Map notification type to system tray icon type
            icon_type_map = {
                "info": system_tray.Information,
                "success": system_tray.Information,
                "warning": system_tray.Warning,
                "error": system_tray.Critical
            }
            
            icon_type = icon_type_map.get(notification_data["type"], system_tray.Information)
            
            # Show the notification
            system_tray.showMessage(
                notification_data["title"],
                notification_data["message"],
                icon_type,
                notification_data["duration"]
            )
            
            # Store click action
            if notification_data["click_action"]:
                self.current_click_action = notification_data["click_action"]
            
            # Schedule next notification
            QTimer.singleShot(notification_data["duration"] + 100, self.show_next_notification)
        else:
            # Fallback: just schedule next notification
            QTimer.singleShot(100, self.show_next_notification)
    
    def show_info_notification(self, title: str, message: str, duration: int = 5000):
        """
        Show an info notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        self.show_notification(title, message, "info", duration)
    
    def show_success_notification(self, title: str, message: str, duration: int = 5000):
        """
        Show a success notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        self.show_notification(title, message, "success", duration)
    
    def show_warning_notification(self, title: str, message: str, duration: int = 5000):
        """
        Show a warning notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        self.show_notification(title, message, "warning", duration)
    
    def show_error_notification(self, title: str, message: str, duration: int = 5000):
        """
        Show an error notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        self.show_notification(title, message, "error", duration)
    
    def show_agent_response_notification(self, message_preview: str):
        """
        Show a notification for agent response.
        
        Args:
            message_preview: Preview of the agent response
        """
        # Truncate message if too long
        if len(message_preview) > 100:
            message_preview = message_preview[:97] + "..."
        
        self.show_notification(
            "OSI ONE AGENT",
            f"New response: {message_preview}",
            "info",
            3000,
            "restore_window"
        )
    
    def show_processing_notification(self):
        """Show a notification that processing has started."""
        self.show_notification(
            "OSI ONE AGENT",
            "Processing your request...",
            "info",
            2000
        )
    
    def show_completion_notification(self, success: bool = True, message: str = ""):
        """
        Show a completion notification.
        
        Args:
            success: Whether the operation was successful
            message: Additional message
        """
        if success:
            self.show_success_notification(
                "OSI ONE AGENT",
                f"Operation completed successfully. {message}".strip(),
                3000
            )
        else:
            self.show_error_notification(
                "OSI ONE AGENT",
                f"Operation failed. {message}".strip(),
                5000
            )
    
    def show_connection_notification(self, connected: bool):
        """
        Show a connection status notification.
        
        Args:
            connected: Whether connected to services
        """
        if connected:
            self.show_success_notification(
                "OSI ONE AGENT",
                "Connected to all services",
                3000
            )
        else:
            self.show_warning_notification(
                "OSI ONE AGENT",
                "Connection issues detected",
                5000
            )
    
    def show_voice_notification(self, is_listening: bool):
        """
        Show a voice input notification.
        
        Args:
            is_listening: Whether voice input is active
        """
        if is_listening:
            self.show_info_notification(
                "OSI ONE AGENT",
                "Listening for voice input...",
                2000
            )
        else:
            self.show_info_notification(
                "OSI ONE AGENT",
                "Voice input stopped",
                2000
            )
    
    def clear_notifications(self):
        """Clear all pending notifications."""
        self.notification_queue.clear()
        self.is_showing_notification = False
    
    def handle_notification_click(self, reason):
        """Handle notification click events."""
        if hasattr(self, 'current_click_action'):
            action = self.current_click_action
            
            if action == "restore_window":
                if self.parent_window:
                    self.parent_window.show()
                    self.parent_window.raise_()
                    self.parent_window.activateWindow()
            
            # Emit signal
            self.notification_clicked.emit(action)
            
            # Clear current action
            delattr(self, 'current_click_action')
    
    def get_notification_count(self) -> int:
        """
        Get the number of pending notifications.
        
        Returns:
            int: Number of pending notifications
        """
        return len(self.notification_queue)
    
    def is_notification_active(self) -> bool:
        """
        Check if a notification is currently being shown.
        
        Returns:
            bool: True if notification is active
        """
        return self.is_showing_notification 