#!/usr/bin/env python3
"""
Script to get available states from Azure DevOps
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.azure_devops import AzureDevOpsTool
from utils.config import ConfigManager

async def get_available_states():
    """Get available states from Azure DevOps."""
    print("🔍 Getting Available States from Azure DevOps")
    print("=" * 50)
    
    # Initialize components
    config = ConfigManager()
    ado_tool = AzureDevOpsTool(config)
    
    try:
        # Setup connection
        await ado_tool.setup()
        
        # Get some tasks to see what states are available
        tasks = await ado_tool.get_my_tasks()
        
        print("📋 Available States from Tasks:")
        states = set()
        for task in tasks:
            state = task.state
            states.add(state)
            print(f"  • {state}")
        
        print(f"\n🎯 Total unique states found: {len(states)}")
        print(f"📝 States: {sorted(list(states))}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(get_available_states()) 