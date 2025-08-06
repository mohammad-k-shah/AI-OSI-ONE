#!/usr/bin/env python3
"""
Test script to verify multi-line input functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent.orchestrator import AgentOrchestrator
from utils.config import ConfigManager
from security.token_manager import TokenManager

async def test_multiline_input():
    """Test multi-line input functionality."""
    print("🔍 Testing Multi-line Input Functionality")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    # Test multi-line queries
    test_queries = [
        # Single line (should work as before)
        "Show my recent tasks which are in Active status",
        
        # Multi-line query (should be treated as one command)
        """Update TASK-73401
Start Date -> 08/11/2025
Finish Date -> 08/11/2025""",
        
        # Multi-line with semicolon
        """Update TASK-73437
Status -> Active;""",
        
        # Multi-line with 'done' keyword
        """Update TASK-51311
Start Date -> 08/06/2025
Finish Date -> 08/07/2025
done"""
    ]
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: Multi-line Query")
        print("-" * 50)
        print(f"📝 Input:")
        print(f"```")
        print(test_query)
        print(f"```")
        print()
        
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
    print("✅ Multi-line input testing completed!")
    print("   The system should now properly handle multi-line commands.")

if __name__ == "__main__":
    asyncio.run(test_multiline_input()) 