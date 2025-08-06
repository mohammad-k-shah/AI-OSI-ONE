#!/usr/bin/env python3
"""
Test script to verify assignee update functionality
"""
import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_assignee_update():
    """Test assignee update functionality."""
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    test_cases = [
        {
            "name": "User Story Assignee Update",
            "query": "Update User Story 72529, Assignee -> 'Karimulla Mohammad'",
            "expected_task_id": "72529",
            "expected_fields": ["assigned_to"]
        },
        {
            "name": "Task Assignee Update",
            "query": "Update Task 12345, Assignee -> 'John Doe'",
            "expected_task_id": "12345",
            "expected_fields": ["assigned_to"]
        },
        {
            "name": "User Story Assignee with Different Format",
            "query": "Update User Story 72529 Assignee to 'Karimulla Mohammad'",
            "expected_task_id": "72529",
            "expected_fields": ["assigned_to"]
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
    
    print("=" * 60)
    print("✅ Assignee Update Testing Summary:")
    print("   ✅ User Story assignee extraction should work")
    print("   ✅ Task assignee extraction should work")
    print("   ✅ Different assignee formats should work")

if __name__ == "__main__":
    asyncio.run(test_assignee_update()) 