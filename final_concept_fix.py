def fix_concept_field_error():
    """Fix the 'concept' field access error in hybrid processing"""
    
    print("🔧 Fixing concept field access error...")
    
    try:
        # Read the hybrid_memory_system.py file
        with open('hybrid_memory_system.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and fix the concept field access issue
        # Look for patterns like: concept.get("concept") or concept["concept"]
        
        # Common patterns to fix:
        fixes = [
            # Fix 1: concept.get("concept") should be concept.get("concept", "")
            ('concept.get("concept")', 'concept.get("concept", "")'),
            
            # Fix 2: for concept in concepts: concept["concept"] 
            ('concept["concept"]', 'concept.get("concept", "")'),
            
            # Fix 3: concept.concept (if using dot notation)
            ('concept.concept', 'concept.get("concept", "") if isinstance(concept, dict) else str(concept)'),
            
            # Fix 4: In list comprehensions
            ('[c["concept"] for c in', '[c.get("concept", "") for c in'),
            
            # Fix 5: Direct concept access in loops
            ('concept_name = concept["concept"]', 'concept_name = concept.get("concept", "unknown")'),
        ]
        
        fixed_count = 0
        for old_pattern, new_pattern in fixes:
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                fixed_count += 1
                print(f"✅ Fixed pattern: {old_pattern}")
        
        # Write the fixed content back
        if fixed_count > 0:
            with open('hybrid_memory_system.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Applied {fixed_count} fixes to hybrid_memory_system.py")
        else:
            print("⚠️ No obvious patterns found, checking ai_semantic_processor.py...")
            
            # Check ai_semantic_processor.py as well
            with open('ai_semantic_processor.py', 'r', encoding='utf-8') as f:
                ai_content = f.read()
            
            ai_fixes = [
                ('concept["concept"]', 'concept.get("concept", "")'),
                ('[c["concept"] for c in', '[c.get("concept", "") for c in'),
                ('concept.get("concept")', 'concept.get("concept", "")'),
            ]
            
            ai_fixed_count = 0
            for old_pattern, new_pattern in ai_fixes:
                if old_pattern in ai_content:
                    ai_content = ai_content.replace(old_pattern, new_pattern)
                    ai_fixed_count += 1
                    print(f"✅ Fixed AI processor pattern: {old_pattern}")
            
            if ai_fixed_count > 0:
                with open('ai_semantic_processor.py', 'w', encoding='utf-8') as f:
                    f.write(ai_content)
                print(f"✅ Applied {ai_fixed_count} fixes to ai_semantic_processor.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False

def add_debug_logging():
    """Add debug logging to identify the exact error location"""
    
    print("🔍 Adding debug logging to identify error...")
    
    try:
        # Add debug logging to hybrid_memory_manager.py
        with open('hybrid_memory_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the process_and_store_memory method and add debug logging
        if 'except Exception as e:' in content and 'Error in hybrid memory processing' in content:
            # Add more detailed error logging
            old_error_line = 'logger.error(f"Error in hybrid memory processing: {e}")'
            new_error_line = '''logger.error(f"Error in hybrid memory processing: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error args: {e.args}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")'''
            
            if old_error_line in content:
                content = content.replace(old_error_line, new_error_line)
                
                with open('hybrid_memory_manager.py', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ Added detailed error logging")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error adding debug logging: {e}")
        return False

def create_simple_test():
    """Create a simple test to isolate the issue"""
    
    simple_test = '''
import sys
import traceback
from hybrid_memory_manager import HybridMemoryManager
from dotenv import load_dotenv
import os

load_dotenv()

try:
    print("🧪 Simple Memory Processing Test")
    
    # Initialize system
    azure_config = {
        "search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
        "search_key": os.getenv("AZURE_SEARCH_KEY"),
        "index_name": os.getenv("AZURE_SEARCH_INDEX")
    }
    
    hybrid_manager = HybridMemoryManager(azure_config)
    print("✅ System initialized")
    
    # Test simple memory processing
    test_content = "Hello, this is a simple test"
    user_context = {"user_id": "test", "tenant_id": "test"}
    
    print(f"🔄 Processing: {test_content}")
    
    memory, report = hybrid_manager.process_and_store_memory(test_content, user_context)
    
    print(f"✅ Success! Report: {report}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    print("Full traceback:")
    traceback.print_exc()
'''
    
    with open('simple_test.py', 'w', encoding='utf-8') as f:
        f.write(simple_test)
    
    print("✅ Created simple_test.py")
    print("Run: python simple_test.py")

if __name__ == "__main__":
    print("🔧 Final System Fix")
    print("=" * 40)
    
    # Try to fix the concept field error
    if fix_concept_field_error():
        print("\n🎯 Test the fix:")
        print("python quick_system_test.py")
    else:
        print("\n🔍 Adding debug logging...")
        add_debug_logging()
        
        print("\n🧪 Creating simple test...")
        create_simple_test()
        
        print("\n🎯 Run these to debug:")
        print("python simple_test.py")
        print("python quick_system_test.py")