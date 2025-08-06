#!/usr/bin/env python3
"""
Test script to verify the fixed commands work correctly
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_fixed_commands():
    """Test the fixed commands."""
    print("🔍 Testing Fixed Commands")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test cases
    test_cases = [
        {
            "name": "Update User Story with Status",
            "query": "Update User Story 56442, state -> Active",
            "should_succeed": True
        },
        {
            "name": "Update Task with Remaining and Completed",
            "query": "Update Task 73418, remaining to 6 and completed to 6",
            "should_succeed": True
        },
        {
            "name": "Update Task with Status",
            "query": "Update Task 73418, status -> Active",
            "should_succeed": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 50)
        print(f"📝 Query: {test_case['query']}")
        print()
        
        try:
            result = await agent.process_query(test_case['query'])
            
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
            
            # Check if result matches expectation
            if test_case['should_succeed']:
                if result['success']:
                    print(f"✅ CORRECT: Command processed successfully")
                else:
                    print(f"❌ INCORRECT: Command failed but should have succeeded")
            else:
                if not result['success']:
                    print(f"✅ CORRECT: Command correctly blocked")
                else:
                    print(f"❌ INCORRECT: Command succeeded but should have been blocked")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 60)
    print("✅ Fixed Commands Testing Summary:")
    print("   ✅ User Story updates should work")
    print("   ✅ Task updates with remaining/completed should work")
    print("   ✅ Status updates should work")

if __name__ == "__main__":
    asyncio.run(test_fixed_commands()) 