#!/usr/bin/env python3
"""
Test script to verify task update functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_task_update():
    """Test task update functionality."""
    print("🔍 Testing Task Update Functionality")
    print("=" * 50)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test query
    test_query = "Update [Start Date] and [Finish Date] field values of [TASK-51311] to be 08/06/2025 and 08/07/2025 respectively"
    
    print(f"📝 Test Query: {test_query}")
    print()
    
    try:
        # Process the query
        result = await agent.process_query(test_query)
        
        print("🎯 Processing Result:")
        print(f"Success: {result['success']}")
        print(f"Intent: {result.get('intent', 'N/A')}")
        print(f"Tool Used: {result.get('tool_used', 'N/A')}")
        print(f"Response: {result.get('response', 'N/A')}")
        
        if 'metadata' in result:
            print(f"Entities: {result['metadata'].get('entities', {})}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_task_update()) 