#!/usr/bin/env python3
"""
Test script to verify batch update functionality in real application
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_real_batch_update():
    """Test batch update functionality in real application."""
    print("🔍 Testing Real Batch Update Functionality")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test the exact user query
    user_query = """Update following individual tasks:
TASK 51311 -> Start Date -> 08/08/2025 Finish Date -> 08/11/2025
TASK 51312 -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025
TASK 51310 -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025"""
    
    print(f"📝 User Query:")
    print(user_query)
    print()
    
    try:
        result = await agent.process_query(user_query)
        
        print(f"✅ Success: {result['success']}")
        print(f"🎯 Intent: {result.get('intent', 'N/A')}")
        print(f"🔧 Tool Used: {result.get('tool_used', 'N/A')}")
        print(f"📝 Response:")
        print(result.get('response', 'N/A'))
        
        if 'metadata' in result:
            entities = result['metadata'].get('entities', {})
            if entities:
                print(f"\n🔍 Extracted Entities:")
                for key, value in entities.items():
                    print(f"  • {key}: {value}")
        
        # Test invalid case
        print("\n" + "="*60)
        print("🧪 Testing Invalid Batch Update")
        print("="*60)
        
        invalid_query = """Update following individual tasks:
TASK 51311 -> Start Date -> 08/08/2025 Finish Date -> 08/11/2025
TASK  -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025
TASK 51310 -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025"""
        
        print(f"📝 Invalid Query:")
        print(invalid_query)
        print()
        
        invalid_result = await agent.process_query(invalid_query)
        
        print(f"✅ Success: {invalid_result['success']}")
        print(f"🎯 Intent: {invalid_result.get('intent', 'N/A')}")
        print(f"🔧 Tool Used: {invalid_result.get('tool_used', 'N/A')}")
        print(f"📝 Response:")
        print(invalid_result.get('response', 'N/A'))
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ Real Batch Update Testing Summary:")
    print("   ✅ Valid batch updates should succeed")
    print("   ✅ Invalid batch updates should be blocked")
    print("   ✅ User-friendly error messages")

if __name__ == "__main__":
    asyncio.run(test_real_batch_update()) 