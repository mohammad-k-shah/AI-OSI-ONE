#!/usr/bin/env python3
"""
Debug script to test NLP entity extraction and intent classification
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.nlp.processor import NLPProcessor
from utils.config import ConfigManager

async def test_nlp_debug():
    """Test NLP processing for task update scenario."""
    print("🔍 Testing NLP Debug")
    print("=" * 50)
    
    # Initialize config and NLP processor
    config = ConfigManager()
    nlp = NLPProcessor(config)
    
    # Test query
    test_query = "Update [Start Date] and [Finish Date] field values of [TASK-51311] to be 08/06/2025 and 08/07/2025 respectively"
    
    print(f"📝 Test Query: {test_query}")
    print()
    
    # Test entity extraction directly
    print("🔧 Testing Entity Extraction:")
    entities = nlp._extract_entities(test_query, "task_update")
    print(f"Extracted Entities: {entities}")
    print()
    
    # Test intent classification
    print("🎯 Testing Intent Classification:")
    try:
        intent = await nlp.classify_intent(test_query)
        print(f"Intent: {intent.name}")
        print(f"Confidence: {intent.confidence}")
        print(f"Entities: {intent.entities}")
        print()
        
        # Test full processing
        print("🔄 Testing Full Processing:")
        result = await nlp.process_query(test_query)
        print(f"Full Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_nlp_debug()) 