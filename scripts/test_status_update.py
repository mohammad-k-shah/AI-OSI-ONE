#!/usr/bin/env python3
"""
Test script to verify status update functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_status_update():
    """Test status update functionality."""
    print("🔍 Testing Status Update Functionality")
    print("=" * 50)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test query
    test_query = "Update TASK-73437 Status -> Active"
    
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
    asyncio.run(test_status_update()) 