#!/usr/bin/env python3
"""
Test script to verify the original user query is now properly blocked
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_original_query():
    """Test the original user query that was causing the issue."""
    print("🔍 Testing Original User Query")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # The original problematic query
    original_query = "Update TASK Status -> Active"
    
    print(f"📝 Original Query: {original_query}")
    print("-" * 50)
    
    try:
        result = await agent.process_query(original_query)
        
        print(f"✅ Success: {result['success']}")
        print(f"🎯 Intent: {result.get('intent', 'N/A')}")
        print(f"🔧 Tool Used: {result.get('tool_used', 'N/A')}")
        print(f"📝 Response: {result.get('response', 'N/A')}")
        
        if 'metadata' in result:
            entities = result['metadata'].get('entities', {})
            if entities:
                print(f"🔍 Extracted Entities:")
                for key, value in entities.items():
                    print(f"  • {key}: {value}")
        
        # Check if it was properly blocked
        if "Please provide the missing Work Item ID" in result.get('response', ''):
            print(f"✅ SUCCESS: Query was properly blocked with safety message!")
        else:
            print(f"❌ FAILURE: Query was not blocked properly!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
    print("✅ Original Query Test Summary:")
    print("   ✅ Query should be blocked with safety message")
    print("   ✅ No accidental bulk updates allowed")

if __name__ == "__main__":
    asyncio.run(test_original_query()) 