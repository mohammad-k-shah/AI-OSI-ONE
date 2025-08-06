#!/usr/bin/env python3
"""
Test Configuration Setup

This script tests the environment variable configuration and provides setup instructions.
"""

import asyncio
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import ConfigManager
from utils.logger import setup_logging
from security.token_manager import TokenManager
from core.agent.orchestrator import AgentOrchestrator


def check_environment_variables():
    """Check if required environment variables are set."""
    print("🔍 Checking Environment Variables...")
    print("=" * 50)
    
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key for natural language processing",
        "AZURE_DEVOPS_TOKEN": "Azure DevOps Personal Access Token",
        "AZURE_DEVOPS_ORGANIZATION": "Azure DevOps organization name",
        "AZURE_DEVOPS_PROJECT": "Azure DevOps project name"
    }
    
    missing_vars = []
    present_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Show first few characters for security
            masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"✅ {var}: {masked_value}")
            present_vars.append(var)
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    print(f"\n📊 Summary:")
    print(f"✅ Present: {len(present_vars)}/{len(required_vars)}")
    print(f"❌ Missing: {len(missing_vars)}/{len(required_vars)}")
    
    if missing_vars:
        print(f"\n🔧 Missing Variables: {', '.join(missing_vars)}")
        return False
    else:
        print(f"\n🎉 All environment variables are configured!")
        return True


def test_config_manager():
    """Test configuration manager with environment variables."""
    print("\n🧪 Testing Configuration Manager...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Initialize config
    config = ConfigManager()
    
    # Test OpenAI API key
    openai_key = config.get_openai_api_key()
    if openai_key:
        masked_key = openai_key[:4] + "..." + openai_key[-4:] if len(openai_key) > 8 else "***"
        print(f"✅ OpenAI API Key: {masked_key}")
    else:
        print(f"❌ OpenAI API Key: Not configured")
    
    # Test Azure DevOps configuration
    ado_token = config.get_azure_devops_token()
    ado_org = config.get_azure_devops_organization()
    ado_project = config.get_azure_devops_project()
    
    if ado_token:
        masked_token = ado_token[:4] + "..." + ado_token[-4:] if len(ado_token) > 8 else "***"
        print(f"✅ Azure DevOps Token: {masked_token}")
    else:
        print(f"❌ Azure DevOps Token: Not configured")
    
    if ado_org:
        print(f"✅ Azure DevOps Organization: {ado_org}")
    else:
        print(f"❌ Azure DevOps Organization: Not configured")
    
    if ado_project:
        print(f"✅ Azure DevOps Project: {ado_project}")
    else:
        print(f"❌ Azure DevOps Project: Not configured")
    
    # Check required configuration
    missing_configs = config.check_required_config()
    
    print(f"\n📋 Configuration Status:")
    for config_name, is_missing in missing_configs.items():
        status = "❌ Missing" if is_missing else "✅ Present"
        print(f"   {status}: {config_name}")
    
    return missing_configs


async def test_agent_with_config():
    """Test agent with current configuration."""
    print("\n🧪 Testing Agent with Configuration...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Initialize components
    config = ConfigManager()
    token_manager = TokenManager()
    agent = AgentOrchestrator(config, token_manager)
    
    print("✅ Agent orchestrator initialized")
    
    # Test queries
    test_queries = [
        "Show my tasks for this sprint",
        "Get my recent pull requests"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            result = await agent.process_query(query)
            print(f"✅ Result: {result['success']}")
            if result['success']:
                print(f"📝 Response: {result['response'][:100]}...")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test health check
    health = await agent.health_check()
    print(f"\n🔍 Agent health check: {health['status']}")
    print(f"🛠️ Available tools: {health.get('tools', [])}")
    
    return True


def show_setup_instructions():
    """Show setup instructions for missing configuration."""
    print("\n📋 Setup Instructions")
    print("=" * 50)
    
    print("""
🔧 **Required Environment Variables**

To use the OSI ONE AGENT with Azure DevOps integration, you need to set the following environment variables:

**1. OpenAI API Key (Required for NLP)**
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

**2. Azure DevOps Configuration (Required for Azure DevOps integration)**
```bash
export AZURE_DEVOPS_TOKEN=your_personal_access_token_here
export AZURE_DEVOPS_ORGANIZATION=your_organization_name
export AZURE_DEVOPS_PROJECT=your_project_name
```

**📝 How to Set Environment Variables:**

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
$env:AZURE_DEVOPS_TOKEN="your_pat_token_here"
$env:AZURE_DEVOPS_ORGANIZATION="your_organization"
$env:AZURE_DEVOPS_PROJECT="your_project"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
set AZURE_DEVOPS_TOKEN=your_pat_token_here
set AZURE_DEVOPS_ORGANIZATION=your_organization
set AZURE_DEVOPS_PROJECT=your_project
```

**Linux/macOS:**
```bash
export OPENAI_API_KEY=your_openai_api_key_here
export AZURE_DEVOPS_TOKEN=your_pat_token_here
export AZURE_DEVOPS_ORGANIZATION=your_organization
export AZURE_DEVOPS_PROJECT=your_project
```

**🔗 Where to Get These Values:**

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with 'sk-')

**Azure DevOps Personal Access Token:**
1. Go to your Azure DevOps organization
2. Click on your profile → Personal Access Tokens
3. Create a new token with these scopes:
   - Work Items (Read)
   - Code (Read)
   - Project and Team (Read)
4. Copy the generated token

**Azure DevOps Organization & Project:**
1. Go to your Azure DevOps organization URL
2. Organization: The name in the URL (e.g., https://dev.azure.com/YOUR_ORG)
3. Project: The project name from your Azure DevOps dashboard

**✅ After Setting Environment Variables:**
1. Restart your terminal/command prompt
2. Run this script again to verify configuration
3. Test the agent with real Azure DevOps integration

**🔒 Security Note:**
- Never commit API keys or tokens to version control
- Use environment variables for sensitive configuration
- Consider using a .env file for development (not included in git)
""")


async def main():
    """Run all configuration tests."""
    print("🚀 Configuration Setup Test")
    print("=" * 50)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Test configuration manager
    missing_configs = test_config_manager()
    
    # Test agent if basic config is available
    if any(not missing for missing in missing_configs.values()):
        await test_agent_with_config()
    
    # Show setup instructions if anything is missing
    if not env_ok or any(missing_configs.values()):
        show_setup_instructions()
    
    print("\n🎯 Next Steps:")
    if env_ok and not any(missing_configs.values()):
        print("✅ All configuration is set up correctly!")
        print("🚀 You can now test the real Azure DevOps integration")
    else:
        print("🔧 Please set up the missing environment variables")
        print("📋 Follow the setup instructions above")
        print("🔄 Run this script again after configuration")


if __name__ == "__main__":
    asyncio.run(main()) 