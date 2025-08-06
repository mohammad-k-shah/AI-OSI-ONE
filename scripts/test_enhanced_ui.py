#!/usr/bin/env python3
"""
Test Enhanced Terminal UI

This script demonstrates the enhanced terminal UI without requiring OpenAI API.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ui.terminal import TerminalUI
from utils.config import ConfigManager
from utils.logger import setup_logging


class MockAgent:
    """Mock agent for testing the enhanced UI."""
    
    async def process_query(self, user_input: str) -> dict:
        """Process user query with mock responses."""
        user_input_lower = user_input.lower()
        
        if "task" in user_input_lower:
            return {
                "success": True,
                "response": "I found 5 tasks assigned to you in the current sprint:\n\n1. [BUG-123] Fix login validation\n2. [FEATURE-456] Implement user dashboard\n3. [TASK-789] Update documentation\n4. [STORY-101] Add search functionality\n5. [BUG-202] Resolve performance issue",
                "metadata": {
                    "entities": {
                        "intent": "tasks",
                        "sprint": "current",
                        "count": "5"
                    }
                },
                "tool_used": "Azure DevOps"
            }
        elif "timesheet" in user_input_lower:
            return {
                "success": True,
                "response": "I've automatically filled your timesheet based on your recent work:\n\n• Monday: 8 hours (Bug fixes and code reviews)\n• Tuesday: 7.5 hours (Feature development)\n• Wednesday: 8 hours (Team meetings and planning)\n• Thursday: 6 hours (Documentation and testing)\n• Friday: 4 hours (Code cleanup and deployment)\n\nTotal: 33.5 hours",
                "metadata": {
                    "entities": {
                        "intent": "timesheet",
                        "period": "last week",
                        "total_hours": "33.5"
                    }
                },
                "tool_used": "OSI One Portal"
            }
        elif "meeting" in user_input_lower or "calendar" in user_input_lower:
            return {
                "success": True,
                "response": "Here are your meetings for today:\n\n• 9:00 AM - Daily Standup (Team Room)\n• 11:00 AM - Code Review Session (Virtual)\n• 2:00 PM - Sprint Planning (Conference Room A)\n• 4:00 PM - Architecture Discussion (Virtual)",
                "metadata": {
                    "entities": {
                        "intent": "meetings",
                        "date": "today",
                        "count": "4"
                    }
                },
                "tool_used": "Microsoft Teams"
            }
        elif "pull request" in user_input_lower or "pr" in user_input_lower:
            return {
                "success": True,
                "response": "Your recent pull requests:\n\n• PR-123: Add user authentication feature (Status: Approved)\n• PR-124: Fix navigation bug (Status: Under Review)\n• PR-125: Update API documentation (Status: Draft)\n• PR-126: Implement caching layer (Status: Needs Changes)",
                "metadata": {
                    "entities": {
                        "intent": "pull_requests",
                        "count": "4",
                        "status": "mixed"
                    }
                },
                "tool_used": "Azure DevOps"
            }
        else:
            return {
                "success": True,
                "response": f"I understand you said: '{user_input}'\n\nThis is a mock response for demonstration. In the full version, I would:\n• Analyze your request using AI\n• Connect to relevant tools (Azure DevOps, Teams, etc.)\n• Provide specific, actionable information\n• Help automate your workflow",
                "metadata": {
                    "entities": {
                        "intent": "general",
                        "confidence": "0.8"
                    }
                }
            }
    
    async def health_check(self) -> dict:
        """Return mock health status."""
        return {
            "status": "healthy",
            "tools": ["Azure DevOps", "Microsoft Teams", "OSI One Portal"],
            "available_tokens": ["azure_devops", "teams", "osi_one"]
        }


async def test_enhanced_ui():
    """Test the enhanced terminal UI."""
    print("🧪 Testing Enhanced Terminal UI...")
    
    # Setup logging
    setup_logging()
    
    # Initialize config
    config = ConfigManager()
    
    # Create mock agent
    agent = MockAgent()
    
    # Create and run terminal UI
    ui = TerminalUI(agent)
    
    print("✅ Enhanced Terminal UI is ready!")
    print("💡 Try these example commands:")
    print("   • 'Show my tasks for this sprint'")
    print("   • 'Fill my timesheet based on last week's work'")
    print("   • 'What meetings do I have today?'")
    print("   • 'Show my recent pull requests'")
    print("   • 'help' - for more commands")
    print("   • 'quit' - to exit")
    print()
    
    await ui.run()


if __name__ == "__main__":
    asyncio.run(test_enhanced_ui()) 