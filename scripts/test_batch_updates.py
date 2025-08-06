#!/usr/bin/env python3
"""
Test script to verify batch update functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_batch_updates():
    """Test batch update functionality."""
    print("🔍 Testing Batch Update Functionality")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Batch Update",
            "query": """Update following individual tasks:
TASK 51311 -> Start Date -> 08/08/2025 Finish Date -> 08/11/2025
TASK 51312 -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025
TASK 51310 -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025""",
            "should_succeed": True
        },
        {
            "name": "Invalid Batch Update (Missing Task ID)",
            "query": """Update following individual tasks:
TASK 51311 -> Start Date -> 08/08/2025 Finish Date -> 08/11/2025
TASK  -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025
TASK 51310 -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025""",
            "should_succeed": False
        },
        {
            "name": "Invalid Batch Update (Invalid Task ID)",
            "query": """Update following individual tasks:
TASK 51311 -> Start Date -> 08/08/2025 Finish Date -> 08/11/2025
TASK abc -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025
TASK 51310 -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025""",
            "should_succeed": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 50)
        print(f"📝 Query:")
        print(test_case['query'])
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
            # For invalid cases, we expect success=False OR success=True with error message
            if test_case['should_succeed']:
                # Valid case - should succeed
                if result['success']:
                    print(f"✅ CORRECT: Result matches expectation")
                else:
                    print(f"❌ INCORRECT: Result doesn't match expectation")
                    print(f"   Expected: True, Got: {result['success']}")
            else:
                # Invalid case - should fail (success=False) OR show error message
                if not result['success'] or "Invalid Batch Update Format" in result.get('response', ''):
                    print(f"✅ CORRECT: Result matches expectation")
                else:
                    print(f"❌ INCORRECT: Result doesn't match expectation")
                    print(f"   Expected: Failure/Error, Got: Success")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 60)
    print("✅ Batch Update Testing Summary:")
    print("   ✅ Valid batch updates should succeed")
    print("   ✅ Invalid batch updates should be blocked")
    print("   ✅ Missing task IDs should be detected")
    print("   ✅ Invalid task IDs should be detected")

if __name__ == "__main__":
    asyncio.run(test_batch_updates()) 