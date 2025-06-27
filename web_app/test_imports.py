#!/usr/bin/env python3
"""
Test script to check what's wrong with imports
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

print("🔍 Testing imports...")
print(f"Python path: {sys.path}")

try:
    print("1. Testing productivity_enhanced_twin import...")
    from productivity_enhanced_twin import ProductivityEnhancedTwin
    print("✅ ProductivityEnhancedTwin imported successfully")
    
    print("2. Testing initialization...")
    twin = ProductivityEnhancedTwin()
    print("✅ ProductivityEnhancedTwin initialized successfully")
    print(f"   - LLM available: {getattr(twin, 'llm_available', 'Unknown')}")
    print(f"   - Productivity mode: {getattr(twin, 'productivity_mode', 'Unknown')}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    print(f"   Exception type: {type(e).__name__}")

try:
    print("3. Testing document_processor import...")
    from document_processor import SmartDocumentProcessor
    print("✅ SmartDocumentProcessor imported successfully")
    
    print("4. Testing SmartDocumentProcessor initialization...")
    processor = SmartDocumentProcessor()
    print("✅ SmartDocumentProcessor initialized successfully")
    
except ImportError as e:
    print(f"❌ SmartDocumentProcessor import failed: {e}")
except Exception as e:
    print(f"❌ SmartDocumentProcessor initialization failed: {e}")

print("\n🎯 Summary:")
print("Run this script to see what's failing:")
print("cd web_app && python test_imports.py")