#!/usr/bin/env python3
"""
Test script to verify update queries without specific task IDs
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_update_without_id():
    """Test update queries without specific task IDs."""
    print("🔍 Testing Update Queries Without Specific Task IDs")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test cases that should be blocked or handled safely
    test_queries = [
        # Missing specific task ID - should be blocked
        "Update TASK Status -> Active",
        "Update Status -> Active", 
        "Update Start Date -> 08/11/2025",
        "Update Finish Date -> 08/12/2025",
        "Modify Status to Active",
        "Change Start Date to 08/11/2025",
        
        # Valid queries with specific task IDs - should work
        "Update TASK-73401 Status -> Active",
        "Update TASK-51311 Start Date -> 08/11/2025",
        "Update USER STORY-72529 Status -> Active"
    ]
    
    print("🧪 Testing Query Classification and Safety:")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 30)
        
        try:
            result = await agent.process_query(query)
            
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
            
            # Check if this should have been blocked
            if "Update TASK Status" in query or "Update Status" in query or "Update Start Date" in query or "Update Finish Date" in query or "Modify Status" in query or "Change Start Date" in query:
                if result['success'] and "Please provide the missing Work Item ID" in result.get('response', ''):
                    print(f"✅ CORRECT: This query was properly blocked with safety message")
                elif result['success'] and "Please provide the missing Work Item ID" not in result.get('response', ''):
                    print(f"⚠️  WARNING: This query was allowed but should have been blocked!")
                else:
                    print(f"✅ CORRECT: This query was properly blocked")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 60)
    print("✅ Update Without ID Testing Summary:")
    print("   ✅ Queries without specific task IDs should be blocked")
    print("   ✅ Queries with specific task IDs should work")
    print("   ✅ Safety validation should prevent dangerous updates")

if __name__ == "__main__":
    asyncio.run(test_update_without_id()) 