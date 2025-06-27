#!/usr/bin/env python3
"""
Quick Fix for Digital Twin Responses
"""

def quick_fix_responses():
    """Quick manual fix for better responses"""
    
    print("🔧 Applying quick response fix...")
    
    try:
        with open('enhanced_twin_controller.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the answer_from_memory method and replace just the return logic
        old_return = '''# Generic answer from top memory
                top_memory = relevant_memories[0][0]
                return f"From what I remember: {top_memory.semantic_summary}"'''
        
        new_return = '''# Generate natural response based on behavioral events
                activities = []
                platforms = set()
                total_events = len(relevant_memories)
                
                for memory, score in relevant_memories[:5]:
                    content_lower = memory.content.lower()
                    
                    if 'salesforce' in content_lower:
                        activities.append("Salesforce CRM work")
                        platforms.add("Salesforce")
                    if 'linkedin' in content_lower or 'research' in content_lower:
                        activities.append("prospect research")
                        platforms.add("LinkedIn")
                    if 'focus' in content_lower:
                        activities.append("focused work sessions")
                    if 'email' in content_lower:
                        activities.append("email management")
                        platforms.add("Email")
                    if 'tab' in content_lower and 'switch' in content_lower:
                        activities.append("multitasking between platforms")
                
                # Build natural response
                if activities:
                    unique_activities = list(set(activities))
                    response = f"Today you worked on: {', '.join(unique_activities[:3])}"
                    
                    if len(unique_activities) > 3:
                        response += f" and {len(unique_activities) - 3} other activities"
                    
                    if platforms:
                        response += f". You used {len(platforms)} main platforms: {', '.join(platforms)}"
                    
                    response += f". I tracked {total_events} total behavioral events."
                    return response
                else:
                    return f"I have {total_events} memories about your activities today. Keep using your work tools and I'll provide better insights!"'''
        
        # Replace the return logic
        if old_return in content:
            content = content.replace(old_return, new_return)
            print("✅ Found and replaced generic return logic")
        else:
            # Alternative: look for the simpler pattern
            simple_old = 'return f"From what I remember: {top_memory.semantic_summary}"'
            if simple_old in content:
                simple_new = '''# Generate natural response
                activities = []
                platforms = set()
                
                for memory, score in relevant_memories[:5]:
                    content_lower = memory.content.lower()
                    if 'salesforce' in content_lower:
                        activities.append("Salesforce work")
                        platforms.add("Salesforce")
                    if 'linkedin' in content_lower:
                        activities.append("LinkedIn research")
                        platforms.add("LinkedIn")
                    if 'focus' in content_lower:
                        activities.append("focused sessions")
                
                if activities:
                    return f"Today: {', '.join(set(activities))}. Used platforms: {', '.join(platforms)}. Tracked {len(relevant_memories)} events total."
                else:
                    return f"I have {len(relevant_memories)} memories. Keep working and I'll give better insights!"'''
                
                content = content.replace(simple_old, simple_new)
                print("✅ Applied simple fix")
        
        # Write the fixed content
        with open('enhanced_twin_controller.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Quick response fix applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error applying quick fix: {e}")
        return False

def test_fix():
    """Test if the fix was applied"""
    try:
        with open('enhanced_twin_controller.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'Today you worked on:' in content or 'Today:' in content:
            print("✅ Fix successfully applied - natural responses enabled!")
            return True
        else:
            print("⚠️ Fix may not have been applied completely")
            return False
            
    except Exception as e:
        print(f"❌ Error testing fix: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Digital Twin Response Fix")
    print("=" * 50)
    
    if quick_fix_responses():
        test_fix()
        print("\n🎉 Quick fix complete!")
        print("\nNext steps:")
        print("1. Stop your current Digital Twin controller (Ctrl+C)")
        print("2. Restart: python enhanced_twin_controller.py")
        print("3. Ask: 'What did I work on today?'")
        print("4. You should get natural responses like:")
        print("   'Today: Salesforce work, LinkedIn research. Used platforms: Salesforce, LinkedIn. Tracked 27 events total.'")
    else:
        print("\n❌ Quick fix failed")
        print("\nManual fix:")
        print("1. Open enhanced_twin_controller.py")
        print("2. Find: return f\"From what I remember: {top_memory.semantic_summary}\"")
        print("3. Replace with better response logic")