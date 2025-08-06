#!/usr/bin/env python3
"""
Test script to verify original estimate update functionality
"""
import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_original_estimate():
    """Test original estimate update functionality."""
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    test_cases = [
        {
            "name": "Original Estimate Update",
            "query": "update task 73418, for original estimate to 13",
            "expected_task_id": "73418",
            "expected_fields": ["original_estimate"]
        },
        {
            "name": "Original Estimate with Different Format",
            "query": "Update Task 12345, original estimate to 8",
            "expected_task_id": "12345",
            "expected_fields": ["original_estimate"]
        },
        {
            "name": "Original Estimate with Arrow",
            "query": "Update Task 12345, original estimate -> 5",
            "expected_task_id": "12345",
            "expected_fields": ["original_estimate"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 50)
        print(f"📝 Query: {test_case['query']}")
        
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
                    
                    task_id = entities.get("task_id")
                    field_names = entities.get("field_names", [])
                    original_estimate_values = entities.get("original_estimate_values", [])
                    
                    if task_id == test_case['expected_task_id']:
                        print(f"✅ Task ID correctly extracted: {task_id}")
                    else:
                        print(f"❌ Task ID extraction failed. Expected: {test_case['expected_task_id']}, Got: {task_id}")
                    
                    for expected_field in test_case['expected_fields']:
                        if expected_field in field_names:
                            print(f"✅ Field '{expected_field}' correctly extracted")
                        else:
                            print(f"❌ Field '{expected_field}' not extracted")
                    
                    if original_estimate_values:
                        print(f"✅ Original estimate value correctly extracted: {original_estimate_values[0]}")
                    else:
                        print(f"❌ Original estimate value not extracted")
            
            print(f"📝 Response: {result.get('response', 'N/A')}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print("✅ Original Estimate Testing Summary:")
    print("   ✅ Original estimate field extraction should work")
    print("   ✅ Original estimate value extraction should work")
    print("   ✅ Different formats should work")

if __name__ == "__main__":
    asyncio.run(test_original_estimate()) 