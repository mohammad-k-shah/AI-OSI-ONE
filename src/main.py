#!/usr/bin/env python3
"""
OSI ONE AGENT - Main Entry Point

AI-Powered Desktop Assistant for OSI Digital Engineers
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.agent.orchestrator import AgentOrchestrator
from ui.terminal import TerminalUI
from security.token_manager import TokenManager
from utils.config import ConfigManager
from utils.logger import setup_logging


async def main():
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging()
        
        # Initialize configuration
        config = ConfigManager()
        
        # Initialize security
        token_manager = TokenManager()
        
        # Initialize agent
        agent = AgentOrchestrator(config, token_manager)
        
        # Initialize UI
        ui = TerminalUI(agent)
        
        # Start the application
        await ui.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 