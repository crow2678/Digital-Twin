import re

def apply_final_fixes():
    print("🔧 Applying final system fixes...")
    
    # Fix 1: Add missing uuid import
    try:
        with open('hybrid_memory_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'import uuid' not in content:
            # Find the import section and add uuid import
            imports_section = content.split('\n')
            insert_index = 0
            for i, line in enumerate(imports_section):
                if line.startswith('import ') or line.startswith('from '):
                    insert_index = i + 1
            
            imports_section.insert(insert_index, 'import uuid')
            content = '\n'.join(imports_section)
            
            with open('hybrid_memory_manager.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Added missing uuid import")
    except Exception as e:
        print(f"❌ Error fixing uuid import: {e}")
    
    # Fix 2: Improve AI response parsing
    try:
        with open('ai_semantic_processor.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add better JSON extraction
        if 'json_match = re.search' not in content:
            # Find the _parse_ai_analysis method and enhance it
            old_parse_method = '''        try:
            # Parse JSON response
            analysis_data = json.loads(response_text)'''
            
            new_parse_method = '''        try:
            # Remove any non-JSON content before/after JSON  
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].strip()
            
            # Find JSON content if wrapped in other text
            import re
            json_match = re.search(r'\\{.*\\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # Parse JSON response
            if response_text:
                analysis_data = json.loads(response_text)
            else:
                raise json.JSONDecodeError("Empty response", "", 0)'''
            
            content = content.replace(old_parse_method, new_parse_method)
            
            with open('ai_semantic_processor.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Improved AI response parsing")
    except Exception as e:
        print(f"❌ Error fixing AI parsing: {e}")
    
    print("🎉 Final fixes applied! Test again.")

if __name__ == "__main__":
    apply_final_fixes()