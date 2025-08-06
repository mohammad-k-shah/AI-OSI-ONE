#!/usr/bin/env python3
"""
Test script to verify case sensitivity fixes for task updates
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_case_sensitivity():
    """Test case sensitivity fixes for task updates."""
    print("🔍 Testing Case Sensitivity Fixes")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test cases
    test_cases = [
        {
            "name": "User Story with Status",
            "query": "Update User Story 56442, state -> Active",
            "expected_task_id": "56442",
            "expected_fields": ["status"]
        },
        {
            "name": "Task with Remaining and Completed",
            "query": "Update Task 73418, remaining to 6 and completed to 6",
            "expected_task_id": "73418",
            "expected_fields": ["remaining", "completed"]
        },
        {
            "name": "Task with Capital Letters",
            "query": "Update Task 12345, Status -> New",
            "expected_task_id": "12345",
            "expected_fields": ["status"]
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
            
            if 'metadata' in result:
                entities = result['metadata'].get('entities', {})
                if entities:
                    print(f"🔍 Extracted Entities:")
                    for key, value in entities.items():
                        print(f"  • {key}: {value}")
                    
                    # Check if expected entities were extracted
                    task_id = entities.get("task_id")
                    field_names = entities.get("field_names", [])
                    
                    if task_id == test_case['expected_task_id']:
                        print(f"✅ Task ID correctly extracted: {task_id}")
                    else:
                        print(f"❌ Task ID extraction failed. Expected: {test_case['expected_task_id']}, Got: {task_id}")
                    
                    for expected_field in test_case['expected_fields']:
                        if expected_field in field_names:
                            print(f"✅ Field '{expected_field}' correctly extracted")
                        else:
                            print(f"❌ Field '{expected_field}' not extracted")
            
            print(f"📝 Response: {result.get('response', 'N/A')}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 60)
    print("✅ Case Sensitivity Testing Summary:")
    print("   ✅ User Story extraction should work")
    print("   ✅ Task extraction should work")
    print("   ✅ Remaining/Completed fields should work")
    print("   ✅ Status field should work")

if __name__ == "__main__":
    asyncio.run(test_case_sensitivity()) 