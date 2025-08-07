"""
OSI ONE AGENT - Desktop GUI Demo

This module provides a demo application to showcase the PyQt5 desktop GUI
for the OSI ONE AGENT with all components working together.
"""

import sys
import asyncio
from typing import Dict, Any
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from .main_window import OSIAgentGUI

class MockAgent:
    """
    Mock agent for demo purposes.
    
    Simulates the agent orchestrator for testing the GUI.
    """
    
    def __init__(self):
        """Initialize the mock agent."""
        self.responses = {
            "show my tasks": "I found 5 tasks assigned to you in the current sprint:\n\n1. **TASK-12345** - Implement user authentication\n   - Status: Active\n   - Priority: High\n   - Assigned: You\n\n2. **TASK-12346** - Fix login bug\n   - Status: In Progress\n   - Priority: Medium\n   - Assigned: You\n\n3. **TASK-12347** - Update documentation\n   - Status: New\n   - Priority: Low\n   - Assigned: You\n\n4. **TASK-12348** - Code review for PR #456\n   - Status: Active\n   - Priority: High\n   - Assigned: You\n\n5. **TASK-12349** - Performance optimization\n   - Status: New\n   - Priority: Medium\n   - Assigned: You",
            
            "update task-12345 status -> active": "✅ **Task TASK-12345 updated successfully!**\n\nUpdated fields:\n• Status: Active\n\nThe task is now marked as active and ready for work.",
            
            "fill my timesheet": "✅ **Timesheet filled successfully!**\n\nI've automatically filled your timesheet based on your recent activities:\n\n**Monday (08/11/2025):**\n• TASK-12345 - User authentication - 4 hours\n• TASK-12346 - Login bug fix - 3 hours\n• Code review - 1 hour\n\n**Tuesday (08/12/2025):**\n• TASK-12347 - Documentation update - 2 hours\n• TASK-12348 - Performance optimization - 4 hours\n• Team meeting - 2 hours\n\n**Total hours:** 16 hours\n\nYour timesheet has been submitted to OSI One.",
            
            "show my meetings today": "📅 **Today's Meetings**\n\nI found 3 meetings scheduled for today:\n\n1. **Daily Standup**\n   - Time: 9:00 AM - 9:15 AM\n   - Attendees: Development Team\n   - Location: Teams Meeting\n\n2. **Sprint Planning**\n   - Time: 2:00 PM - 3:00 PM\n   - Attendees: Product Owner, Development Team\n   - Location: Conference Room A\n\n3. **Code Review Session**\n   - Time: 4:00 PM - 4:30 PM\n   - Attendees: Senior Developers\n   - Location: Teams Meeting\n\n**Total meeting time:** 1 hour 45 minutes",
            
            "help": "🧠 **OSI Work Buddy Help**\n\nI can help you with various tasks:\n\n**Azure DevOps Commands:**\n• Show my tasks for this sprint\n• Get my recent pull requests\n• Update TASK-12345 Status -> Active\n• Update TASK-12345 Start Date -> 08/11/2025\n\n**OSI One Commands:**\n• Fill my timesheet based on last week's PRs\n• Show my timesheet entries for this week\n• Submit my timesheet\n\n**Teams Commands:**\n• Show my meetings today\n• Do I have meetings with John this week?\n• What meetings are scheduled for tomorrow?\n\n**Batch Updates:**\n• Update following individual tasks:\n  TASK 51311 -> Start Date -> 08/08/2025\n  TASK 51312 -> Start Date -> 08/11/2025\n\nTry any of these commands to get started!"
        }
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query.
        
        Args:
            query: User query
            
        Returns:
            Dict with response data
        """
        # Simulate processing delay
        await asyncio.sleep(1)
        
        query_lower = query.lower()
        
        # Find matching response
        for key, response in self.responses.items():
            if key in query_lower:
                return {
                    "success": True,
                    "message": response,
                    "data": {"query": query, "response": response}
                }
        
        # Default response
        return {
            "success": True,
            "message": f"I understand you said: '{query}'\n\nThis is a demo mode. In the real application, I would process this request and provide a detailed response based on your Azure DevOps, OSI One, and Teams data.\n\nTry saying 'help' to see what I can do!",
            "data": {"query": query, "demo_mode": True}
        }

def run_demo():
    """Run the desktop GUI demo."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("OSI Work Buddy Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create mock agent
    mock_agent = MockAgent()
    
    # Create main window
    main_window = OSIAgentGUI(agent=mock_agent)
    main_window.show()
    
    # Show welcome message
    QTimer.singleShot(1000, main_window.show_welcome_message)
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_demo() 