import re

def fix_indentation():
    """Fix indentation issues in ai_semantic_processor.py"""
    
    print("🔧 Fixing indentation in ai_semantic_processor.py...")
    
    try:
        with open('ai_semantic_processor.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the problematic line
        for i, line in enumerate(lines):
            if 'def analyze_content(self, content: str, user_context: Dict[str, Any] = None) -> AIAnalysisResult:' in line:
                # Check if this line has wrong indentation
                if not line.startswith('    def '):  # Should be 4 spaces for class method
                    lines[i] = '    def analyze_content(self, content: str, user_context: Dict[str, Any] = None) -> AIAnalysisResult:\n'
                    print(f"✅ Fixed line {i+1}: analyze_content method indentation")
                break
        
        # Fix any other common indentation issues
        fixed_lines = []
        in_class = False
        in_method = False
        
        for line in lines:
            # Track if we're in a class
            if line.startswith('class '):
                in_class = True
                in_method = False
                fixed_lines.append(line)
            
            # Track if we're in a method
            elif line.strip().startswith('def ') and in_class:
                in_method = True
                # Ensure method has 4 spaces
                if not line.startswith('    def '):
                    line = '    ' + line.lstrip()
                fixed_lines.append(line)
            
            # Fix method content indentation
            elif in_method and line.strip() and not line.startswith('    '):
                if line.startswith('def ') or line.startswith('class '):
                    # New method/class, reset tracking
                    in_method = False
                    if line.startswith('class '):
                        in_class = True
                    fixed_lines.append(line)
                else:
                    # Method content should have 8 spaces
                    line = '        ' + line.lstrip()
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # Write fixed file
        with open('ai_semantic_processor.py', 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print("✅ Indentation fixed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing indentation: {e}")
        return False

def validate_python_syntax(filename):
    """Validate Python file syntax"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, filename, 'exec')
        print(f"✅ {filename} syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error validating {filename}: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Python Indentation and Syntax Fixer")
    print("=" * 50)
    
    # Fix indentation
    if fix_indentation():
        # Validate syntax
        if validate_python_syntax('ai_semantic_processor.py'):
            print("\n🎉 File fixed successfully!")
            print("Run: python quick_system_test.py")
        else:
            print("\n⚠️  File still has syntax issues")
    else:
        print("\n❌ Could not fix indentation automatically")
        print("\nManual fix needed:")
        print("1. Open ai_semantic_processor.py")
        print("2. Find line with 'def analyze_content'")
        print("3. Ensure it starts with exactly 4 spaces")
        print("4. Ensure all method content has 8 spaces")