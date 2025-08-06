#!/usr/bin/env python3
"""
Test script for the specific original estimate command that wasn't working
"""
import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_specific_original_estimate():
    """Test the specific original estimate command."""
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # The exact command that wasn't working
    test_query = "update task 73418, for original estimate to 13"
    
    print(f"🧪 Testing the specific command that wasn't working:")
    print("-" * 60)
    print(f"📝 Query: {test_query}")
    print(f"🎯 Expected: Should set 'Original Estimate' field value of Task-73418 to '13'")
    
    try:
        result = await agent.process_query(test_query)
        print(f"\n✅ Success: {result['success']}")
        print(f"🎯 Intent: {result.get('intent', 'N/A')}")
        print(f"🔧 Tool Used: {result.get('tool_used', 'N/A')}")
        
        if 'metadata' in result:
            entities = result['metadata'].get('entities', {})
            if entities:
                print(f"\n🔍 Extracted Entities:")
                for key, value in entities.items():
                    print(f"  • {key}: {value}")
                
                task_id = entities.get("task_id")
                field_names = entities.get("field_names", [])
                original_estimate_values = entities.get("original_estimate_values", [])
                
                print(f"\n📊 Analysis:")
                if task_id == "73418":
                    print(f"✅ Task ID correctly extracted: {task_id}")
                else:
                    print(f"❌ Task ID extraction failed. Expected: 73418, Got: {task_id}")
                
                if "original_estimate" in field_names:
                    print(f"✅ Field 'original_estimate' correctly extracted")
                else:
                    print(f"❌ Field 'original_estimate' not extracted")
                
                if original_estimate_values and original_estimate_values[0] == "13":
                    print(f"✅ Original estimate value correctly extracted: {original_estimate_values[0]}")
                else:
                    print(f"❌ Original estimate value not extracted correctly")
        
        print(f"\n📝 Response: {result.get('response', 'N/A')}")
        
        if result['success']:
            print(f"\n🎉 SUCCESS! The command is now working!")
            print(f"   ✅ Task 73418 original estimate was updated to 13")
        else:
            print(f"\n❌ FAILED! The command is still not working.")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_specific_original_estimate()) 