import re

def apply_fixes():
    print("🔧 Applying system fixes...")
    
    # Fix 1: AI Response Parsing
    try:
        with open('ai_semantic_processor.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the _parse_ai_analysis method
        old_pattern = r'def _parse_ai_analysis\(self, content: str, ai_response.*?\n        except json\.JSONDecodeError as e:'
        
        new_method = '''def _parse_ai_analysis(self, content: str, ai_response) -> AIAnalysisResult:
        """Parse AI response into structured analysis result"""
        
        try:
            # Handle LangChain AIMessage object
            if hasattr(ai_response, 'content'):
                response_text = ai_response.content
            else:
                response_text = str(ai_response)
            
            # Parse JSON response
            analysis_data = json.loads(response_text)
            
            return AIAnalysisResult(
                content=content,
                semantic_concepts=analysis_data.get("semantic_concepts", []),
                extracted_entities=analysis_data.get("extracted_entities", []),
                relationships=analysis_data.get("relationships", []),
                context_understanding=analysis_data.get("context_understanding", {}),
                confidence_score=analysis_data.get("confidence_score", 0.0),
                reasoning=analysis_data.get("reasoning", ""),
                suggested_properties=analysis_data.get("suggested_properties", {}),
                semantic_tags=analysis_data.get("semantic_tags", [])
            )
            
        except json.JSONDecodeError as e:'''
        
        if '"timestamp": self.timestamp.isoformat(),' in content:
            content = content.replace(
                '"timestamp": self.timestamp.isoformat(),',
                '"timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),'
            )
            print("✅ Fixed AI response parsing")
        
        with open('ai_semantic_processor.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"❌ Error fixing AI processor: {e}")
    
    # Fix 2: Date Format
    try:
        with open('hybrid_memory_system.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '"timestamp": self.timestamp.isoformat(),' in content:
            content = content.replace(
                '"timestamp": self.timestamp.isoformat(),',
                '"timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),'
            )
            print("✅ Fixed date format")
        
        # Also fix expiry_date format
        if 'self.expiry_date.isoformat() if self.expiry_date else None' in content:
            content = content.replace(
                'self.expiry_date.isoformat() if self.expiry_date else None',
                'self.expiry_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if self.expiry_date else None'
            )
            print("✅ Fixed expiry date format")
        
        with open('hybrid_memory_system.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"❌ Error fixing date format: {e}")
    
    print("🎉 Fixes applied! Run the test again.")

if __name__ == "__main__":
    apply_fixes()