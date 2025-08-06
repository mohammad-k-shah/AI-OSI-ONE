#!/usr/bin/env python3
"""
Test script to verify status updates with work item type-specific validation
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_status_update_with_validation():
    """Test status update functionality with type-specific validation."""
    print("🔍 Testing Status Update with Work Item Type Validation")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test queries for different work item types
    test_queries = [
        "Update TASK-73437 Status -> Active",
        "Update TASK-73437 Status -> New", 
        "Update TASK-73437 Status -> Closed",
        "Update TASK-73437 Status -> Resolved",  # Should fallback to Active for TASK
        "Update TASK-73437 Status -> Approved"   # Should fallback to Active for TASK
    ]
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {test_query}")
        print("-" * 50)
        
        try:
            # Process the query
            result = await agent.process_query(test_query)
            
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
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 60)
    print("✅ Status update validation testing completed!")
    print("   The system now validates status updates based on work item type:")
    print("   • TASK: New, Active, Closed, Removed")
    print("   • USER STORY: New, Approved, Active, Resolved, Closed, Removed")

if __name__ == "__main__":
    asyncio.run(test_status_update_with_validation()) 