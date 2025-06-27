#!/usr/bin/env python3
"""
Environment Test Script
Verifies that all required dependencies and configurations are available
"""

import os
import sys
from pathlib import Path

def test_python_version():
    """Test Python version compatibility"""
    print("🐍 Testing Python Version")
    print("-" * 30)
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
        return True
    else:
        print("❌ Python version too old. Need 3.8+")
        return False

def test_required_packages():
    """Test if required packages can be imported"""
    print("\n📦 Testing Required Packages")
    print("-" * 30)
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic models"),
        ("dotenv", "Environment variables"),
        ("pathlib", "Path handling"),
        ("datetime", "Date/time handling"),
        ("json", "JSON processing"),
        ("uuid", "UUID generation"),
        ("logging", "Logging"),
        ("typing", "Type hints"),
        ("re", "Regular expressions"),
    ]
    
    optional_packages = [
        ("langchain_openai", "Azure OpenAI integration"),
        ("azure.search", "Azure Search"),
        ("azure.core", "Azure Core"),
    ]
    
    all_good = True
    
    print("Required packages:")
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} - {description}")
        except ImportError:
            print(f"  ❌ {package} - {description} - MISSING")
            all_good = False
    
    print("\nOptional packages (for full functionality):")
    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} - {description}")
        except ImportError:
            print(f"  ⚠️ {package} - {description} - Not available (fallback mode)")
    
    return all_good

def test_environment_variables():
    """Test Azure environment variables"""
    print("\n🔧 Testing Environment Variables")
    print("-" * 30)
    
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv()
            print(f"✅ Loaded .env file: {env_file.absolute()}")
        else:
            print("⚠️ No .env file found")
    except ImportError:
        print("⚠️ python-dotenv not available")
    
    # Check Azure configuration
    azure_vars = [
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_KEY", 
        "AZURE_SEARCH_INDEX",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_KEY",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_ENDPOINT"
    ]
    
    print("\nAzure configuration:")
    azure_configured = 0
    for var in azure_vars:
        value = os.getenv(var)
        if value:
            # Don't print sensitive values, just show they exist
            masked_value = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  ✅ {var} = {masked_value}")
            azure_configured += 1
        else:
            print(f"  ❌ {var} = Not set")
    
    if azure_configured == len(azure_vars):
        print(f"✅ All Azure variables configured ({azure_configured}/{len(azure_vars)})")
        return True
    elif azure_configured >= 3:  # At least search config
        print(f"⚠️ Partial Azure config ({azure_configured}/{len(azure_vars)}) - some features may not work")
        return True
    else:
        print(f"❌ Insufficient Azure config ({azure_configured}/{len(azure_vars)}) - will run in fallback mode")
        return False

def test_file_structure():
    """Test that required files exist"""
    print("\n📁 Testing File Structure")
    print("-" * 30)
    
    required_files = [
        "enhanced_twin_controller.py",
        "hybrid_memory_manager.py",
        "behavioral_api_server.py",
    ]
    
    optional_files = [
        "digital_twin_ontology.py",
        "ai_semantic_processor.py",
        "hybrid_memory_system.py",
    ]
    
    all_good = True
    
    print("Required files:")
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_good = False
    
    print("\nOptional files:")
    for file in optional_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ {file} - Not found")
    
    return all_good

def test_write_permissions():
    """Test write permissions for sessions and logs"""
    print("\n✏️ Testing Write Permissions")
    print("-" * 30)
    
    test_dirs = ["sessions", "logs"]
    
    for dir_name in test_dirs:
        try:
            test_dir = Path(dir_name)
            test_dir.mkdir(exist_ok=True)
            
            # Test writing a file
            test_file = test_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()  # Clean up
            
            print(f"  ✅ {dir_name}/ - Writable")
        except Exception as e:
            print(f"  ❌ {dir_name}/ - Cannot write: {e}")
            return False
    
    return True

def run_environment_tests():
    """Run all environment tests"""
    print("🔍 Enhanced Digital Twin - Environment Test")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Required Packages", test_required_packages), 
        ("Environment Variables", test_environment_variables),
        ("File Structure", test_file_structure),
        ("Write Permissions", test_write_permissions),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 ENVIRONMENT TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Environment is fully configured!")
        print("➡️ You can now run: python test_enhanced_twin.py")
    elif passed >= 3:
        print("⚠️ Environment is partially configured - some features may not work")
        print("➡️ You can still test basic functionality")
    else:
        print("❌ Environment needs configuration before testing")
        print("➡️ Please set up Azure credentials and install missing packages")

if __name__ == "__main__":
    run_environment_tests()