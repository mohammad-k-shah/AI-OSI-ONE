#!/usr/bin/env python3
"""
Test script to verify environment variable setup for OSI ONE AGENT
"""

import os
import sys

def test_environment_variables():
    """Test if required environment variables are accessible"""
    print("🔍 Environment Variable Test")
    print("=" * 50)
    
    # Test OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    print(f"✅ OPENAI_API_KEY: {'Present' if openai_key else 'Missing'}")
    if openai_key:
        print(f"   Value: {openai_key[:10]}...{openai_key[-4:]}")
    
    # Test Azure DevOps Token
    ado_token = os.getenv("AZURE_DEVOPS_TOKEN")
    print(f"{'✅' if ado_token else '❌'} AZURE_DEVOPS_TOKEN: {'Present' if ado_token else 'Missing'}")
    if ado_token:
        print(f"   Value: {ado_token[:10]}...{ado_token[-4:]}")
    
    # Test Azure DevOps Organization
    ado_org = os.getenv("AZURE_DEVOPS_ORGANIZATION")
    print(f"{'✅' if ado_org else '❌'} AZURE_DEVOPS_ORGANIZATION: {'Present' if ado_org else 'Missing'}")
    if ado_org:
        print(f"   Value: {ado_org}")
    
    # Test Azure DevOps Project
    ado_project = os.getenv("AZURE_DEVOPS_PROJECT")
    print(f"{'✅' if ado_project else '❌'} AZURE_DEVOPS_PROJECT: {'Present' if ado_project else 'Missing'}")
    if ado_project:
        print(f"   Value: {ado_project}")
    
    print("\n📋 Troubleshooting Steps:")
    print("=" * 50)
    
    if not ado_token:
        print("❌ AZURE_DEVOPS_TOKEN is missing!")
        print("\n🔧 To fix this:")
        print("1. Open Windows Settings")
        print("2. Search for 'Environment Variables'")
        print("3. Click 'Edit the system environment variables'")
        print("4. Click 'Environment Variables' button")
        print("5. Under 'User variables', click 'New'")
        print("6. Variable name: AZURE_DEVOPS_TOKEN")
        print("7. Variable value: your_personal_access_token")
        print("8. Click 'OK' on all dialogs")
        print("9. Restart your terminal/command prompt")
        print("10. Run this script again")
    
    if not ado_org or not ado_project:
        print("\nℹ️  Note: Organization and Project are set in config file, so these are optional")
    
    print("\n🎯 Current Status:")
    if openai_key and ado_token:
        print("✅ Ready for Azure DevOps integration!")
    elif openai_key:
        print("⚠️  OpenAI ready, but Azure DevOps token missing")
    else:
        print("❌ Missing required configuration")

if __name__ == "__main__":
    test_environment_variables() 