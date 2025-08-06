#!/usr/bin/env python3
"""
Test script to debug status extraction in batch updates
"""

import asyncio
import sys
import os
import re

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.nlp.processor import NLPProcessor
from utils.config import ConfigManager

async def test_status_extraction():
    """Test status extraction in batch updates."""
    print("🔍 Testing Status Extraction in Batch Updates")
    print("=" * 60)
    
    # Initialize components
    config = ConfigManager()
    nlp_processor = NLPProcessor(config)
    
    # Test the exact user input
    user_input = """Update following individual tasks:
TASK 51311 -> Start Date -> 08/08/2025 Finish Date -> 08/11/2025 Status -> New
TASK 51312 -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025
TASK 51310 -> Start Date -> 08/11/2025 Finish Date -> 08/11/2025"""
    
    print(f"📝 User Input:")
    print(user_input)
    print()
    
    try:
        # Test the regex pattern directly
        print("🧪 Testing Regex Pattern:")
        print("-" * 30)
        
        # Test the current pattern
        pattern = r'status\s*->\s*(\w+)'
        test_line = "TASK 51311 -> Start Date -> 08/08/2025 Finish Date -> 08/11/2025 Status -> New"
        
        match = re.search(pattern, test_line, re.IGNORECASE)
        if match:
            print(f"✅ Pattern matched: {match.group(1)}")
        else:
            print(f"❌ Pattern did not match")
        
        # Test with different case variations
        test_cases = [
            "Status -> New",
            "status -> New", 
            "STATUS -> New",
            "Status->New",
            "Status -> Active"
        ]
        
        for test_case in test_cases:
            match = re.search(pattern, test_case, re.IGNORECASE)
            if match:
                print(f"✅ '{test_case}' -> {match.group(1)}")
            else:
                print(f"❌ '{test_case}' -> No match")
        
        print()
        
        # Test the batch extraction method
        print("🧪 Testing Batch Extraction:")
        print("-" * 30)
        
        batch_updates = nlp_processor._extract_batch_updates(user_input)
        if batch_updates:
            print(f"✅ Batch updates extracted: {len(batch_updates)} tasks")
            for i, update in enumerate(batch_updates, 1):
                print(f"Task {i}:")
                print(f"  ID: {update['task_id']}")
                print(f"  Field Updates: {update['field_updates']}")
        else:
            print("❌ No batch updates extracted")
        
        print()
        
        # Test the full NLP processing
        print("🧪 Testing Full NLP Processing:")
        print("-" * 30)
        
        intent = await nlp_processor.classify_intent(user_input)
        print(f"Intent: {intent.name}")
        print(f"Confidence: {intent.confidence}")
        print(f"Entities: {intent.entities}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ Status Extraction Testing Summary")

if __name__ == "__main__":
    asyncio.run(test_status_extraction()) 