#!/usr/bin/env python3
"""
Test script to verify critical safety validation for work item updates
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_safety_validation():
    """Test critical safety validation for work item updates."""
    print("🔒 Testing Critical Safety Validation")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test cases that should be BLOCKED (dangerous queries)
    dangerous_queries = [
        # Missing work item ID - should be blocked
        "Update Start Date -> 08/11/2025",
        "Update Status -> Active",
        "Update all tasks Status -> Active",
        "Update Finish Date -> 08/12/2025",
        "Modify Status to Active",
        "Change Start Date to 08/11/2025",
        
        # Invalid work item ID format - should be blocked
        "Update TASK-abc Start Date -> 08/11/2025",
        "Update STORY-xyz Status -> Active",
        "Update TASK- Start Date -> 08/11/2025",
        "Update TASK Status -> Active",
        
        # Ambiguous queries that could be interpreted as bulk updates
        "Update my tasks Status -> Active",
        "Update all Status -> Active",
        "Update everything Start Date -> 08/11/2025"
    ]
    
    # Test cases that should be ALLOWED (safe queries)
    safe_queries = [
        # Valid specific work item updates
        "Update TASK-73401 Start Date -> 08/11/2025",
        "Update USER STORY-72529 Status -> Active",
        "Update REQUIREMENT-12345 Finish Date -> 08/12/2025",
        "Update TASK-51311 Status -> New",
        "Update TASK-73437 Start Date -> 08/06/2025 Finish Date -> 08/07/2025"
    ]
    
    print("🚨 Testing DANGEROUS Queries (Should Be BLOCKED):")
    print("-" * 50)
    
    for i, query in enumerate(dangerous_queries, 1):
        print(f"\n🧪 Test {i}: {query}")
        print("-" * 30)
        
        try:
            result = await agent.process_query(query)
            
            if result['success']:
                print(f"❌ FAILED: Query was allowed but should have been blocked!")
                print(f"   Response: {result.get('response', 'N/A')}")
            else:
                print(f"✅ PASSED: Query was correctly blocked")
                print(f"   Error: {result.get('response', 'N/A')}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
    
    print("\n✅ Testing SAFE Queries (Should Be ALLOWED):")
    print("-" * 50)
    
    for i, query in enumerate(safe_queries, 1):
        print(f"\n🧪 Test {i}: {query}")
        print("-" * 30)
        
        try:
            result = await agent.process_query(query)
            
            if result['success']:
                print(f"✅ PASSED: Query was correctly allowed")
                print(f"   Intent: {result.get('intent', 'N/A')}")
                print(f"   Tool: {result.get('tool_used', 'N/A')}")
            else:
                print(f"❌ FAILED: Query was blocked but should have been allowed!")
                print(f"   Error: {result.get('response', 'N/A')}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
    
    print("=" * 60)
    print("🔒 Safety Validation Testing Summary:")
    print("   ✅ Dangerous queries should be BLOCKED")
    print("   ✅ Safe queries should be ALLOWED")
    print("   ✅ No bulk updates without specific work item IDs")
    print("   ✅ Prevents accidental company-wide impact")

if __name__ == "__main__":
    asyncio.run(test_safety_validation()) 