#!/usr/bin/env python3
"""
Enhanced General Website Browsing Recognition for Digital Twin
"""

def add_general_browsing_recognition():
    """Add recognition for general website browsing in simple terms"""
    
    print("🌐 Adding general website browsing recognition...")
    
    try:
        with open('enhanced_twin_controller.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the explain_work_activities method and enhance it
        enhanced_work_explanation = '''
    def explain_work_activities(self, memories):
        """Explain work activities including general browsing in simple terms"""
        
        activities = []
        websites_visited = set()
        
        for memory, score in memories[:10]:
            content = memory.content.lower()
            
            # Specific work platforms
            if 'salesforce' in content:
                activities.append("worked on your sales computer")
                websites_visited.add("Salesforce")
            if 'linkedin' in content or 'research' in content:
                activities.append("looked up information about people")
                websites_visited.add("LinkedIn")
            if 'outlook' in content or 'email' in content:
                activities.append("sent emails")
                websites_visited.add("Email")
            
            # General website browsing
            if 'page_visit' in content or 'browsing' in content:
                activities.append("browsed different websites")
            if 'claude.ai' in content:
                activities.append("used AI tools")
                websites_visited.add("Claude AI")
            if 'microsoft' in content:
                activities.append("used Microsoft tools")
                websites_visited.add("Microsoft")
            if 'navan' in content:
                activities.append("managed travel stuff")
                websites_visited.add("Navan")
            if 'github' in content:
                activities.append("worked on coding projects")
                websites_visited.add("GitHub")
            
            # Behavioral patterns
            if 'focus' in content:
                activities.append("did some deep thinking work")
            if 'switch' in content or 'tab' in content:
                activities.append("switched between different websites")
            if 'time_tracking' in content:
                activities.append("spent focused time working")
        
        if not activities:
            return "I didn't see you do any activities yet. Start browsing and working, and I'll remember everything you do!"
        
        unique_activities = list(set(activities))
        unique_websites = list(websites_visited)
        
        # Build response
        response = "Today you "
        
        if len(unique_activities) == 1:
            response += f"{unique_activities[0]}."
        elif len(unique_activities) == 2:
            response += f"{unique_activities[0]} and {unique_activities[1]}."
        else:
            main_activities = unique_activities[:2]
            extra_count = len(unique_activities) - 2
            response += f"{main_activities[0]}, {main_activities[1]}, and {extra_count} other things."
        
        # Add websites information
        if unique_websites:
            if len(unique_websites) == 1:
                response += f" You mainly used {unique_websites[0]}."
            elif len(unique_websites) <= 3:
                response += f" You used {', '.join(unique_websites[:-1])}, and {unique_websites[-1]}."
            else:
                response += f" You used {len(unique_websites)} different websites including {unique_websites[0]}, {unique_websites[1]}, and others."
        
        response += " I'm watching and learning about your work habits!"
        
        return response'''
        
        # Replace the existing explain_work_activities method
        import re
        pattern = r'def explain_work_activities\(self, memories\):.*?(?=\n    def |\nclass |\Z)'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, enhanced_work_explanation.strip(), content, flags=re.DOTALL)
            print("✅ Enhanced work activities explanation")
        
        # Also enhance the platform usage explanation
        enhanced_platform_explanation = '''
    def explain_platform_usage(self, memories, question):
        """Explain platform usage including general websites simply"""
        
        platform_counts = {}
        
        for memory, score in memories:
            content = memory.content.lower()
            
            # Work platforms
            if 'salesforce' in content:
                platform_counts['Salesforce (your sales program)'] = platform_counts.get('Salesforce (your sales program)', 0) + 1
            if 'linkedin' in content:
                platform_counts['LinkedIn (people finder)'] = platform_counts.get('LinkedIn (people finder)', 0) + 1
            if 'outlook' in content or 'email' in content:
                platform_counts['Email'] = platform_counts.get('Email', 0) + 1
            
            # General websites
            if 'claude.ai' in content:
                platform_counts['Claude AI (smart assistant)'] = platform_counts.get('Claude AI (smart assistant)', 0) + 1
            if 'microsoft' in content:
                platform_counts['Microsoft websites'] = platform_counts.get('Microsoft websites', 0) + 1
            if 'navan' in content:
                platform_counts['Navan (travel booking)'] = platform_counts.get('Navan (travel booking)', 0) + 1
            if 'github' in content:
                platform_counts['GitHub (coding website)'] = platform_counts.get('GitHub (coding website)', 0) + 1
            if 'page_visit' in content and not any(platform in content for platform in ['salesforce', 'linkedin', 'outlook']):
                platform_counts['Other websites'] = platform_counts.get('Other websites', 0) + 1
        
        # Handle specific platform questions
        if 'salesforce' in question:
            salesforce_key = next((k for k in platform_counts.keys() if 'Salesforce' in k), None)
            if salesforce_key:
                count = platform_counts[salesforce_key]
                return f"You used Salesforce {count} times today! That's where you manage your sales work, right?"
            else:
                return "I didn't see you use Salesforce today. When you open it, I'll start tracking what you do there!"
        
        if 'linkedin' in question:
            linkedin_key = next((k for k in platform_counts.keys() if 'LinkedIn' in k), None)
            if linkedin_key:
                count = platform_counts[linkedin_key]
                return f"You used LinkedIn {count} times today! That's where you look up people for work."
            else:
                return "I didn't see you use LinkedIn today. When you research people there, I'll remember it!"
        
        if 'website' in question or 'sites' in question or 'browsing' in question:
            if not platform_counts:
                return "I haven't seen you browse any websites yet today. Start surfing the web and I'll remember where you go!"
            
            total_sites = len(platform_counts)
            if total_sites == 1:
                site, count = list(platform_counts.items())[0]
                return f"Today you mainly browsed {site}. You visited it {count} times!"
            else:
                response = f"Today you browsed {total_sites} different websites: "
                site_list = [f"{site} ({count} times)" for site, count in list(platform_counts.items())[:3]]
                response += ", ".join(site_list)
                if total_sites > 3:
                    response += f", and {total_sites - 3} more sites"
                response += ". You really explored the internet today!"
                return response
        
        # General response
        if not platform_counts:
            return "I haven't seen you use any websites or programs yet today. Start browsing and I'll remember everything!"
        
        if len(platform_counts) == 1:
            program, count = list(platform_counts.items())[0]
            return f"Today you mainly used {program}. You used it {count} times!"
        else:
            response = "Today you used: "
            programs = [f"{program} ({count} times)" for program, count in list(platform_counts.items())[:4]]
            response += ", ".join(programs)
            if len(platform_counts) > 4:
                response += f", and {len(platform_counts) - 4} other websites"
            response += ". You're great at using different websites and programs!"
            return response'''
        
        # Replace the platform usage method
        pattern = r'def explain_platform_usage\(self, memories, question\):.*?(?=\n    def |\nclass |\Z)'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, enhanced_platform_explanation.strip(), content, flags=re.DOTALL)
            print("✅ Enhanced platform usage explanation")
        
        # Also enhance the question detection to include browsing questions
        enhanced_question_detection = '''
    def is_question(self, user_input: str) -> bool:
        """Detect if user input is a question that should be answered from memory"""
        user_input_lower = user_input.lower().strip()
        
        # Question indicators - expanded list
        question_starters = [
            'what', 'how', 'when', 'where', 'why', 'which', 'who',
            'do i', 'am i', 'can i', 'should i', 'will i', 'have i',
            'tell me about', 'what about', 'remind me', 'show me',
            'what do', 'what are', 'what is', 'how do', 'where do',
            'list', 'describe', 'explain', 'analyze'
        ]
        
        # Check if it starts with question words
        for starter in question_starters:
            if user_input_lower.startswith(starter):
                return True
        
        # Check for question marks
        if '?' in user_input:
            return True
        
        # Check for implicit questions (common patterns)
        implicit_questions = [
            'what i like', 'what i do', 'what i want', 'what i need',
            'what i have', 'what i know', 'my preferences', 'my interests',
            'about me', 'tell me', 'remind me', 'behavioral events',
            'events', 'activities', 'patterns', 'insights', 'websites',
            'browsing', 'sites', 'visited', 'platforms', 'tools'
        ]
        
        for pattern in implicit_questions:
            if pattern in user_input_lower:
                return True
        
        return False'''
        
        # Update question detection
        pattern = r'def is_question\(self, user_input: str\) -> bool:.*?return False'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, enhanced_question_detection.strip() + '\n        return False', content, flags=re.DOTALL)
            print("✅ Enhanced question detection for browsing")
        
        # Write the enhanced file
        with open('enhanced_twin_controller.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added general website browsing recognition!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding browsing recognition: {e}")
        return False

if __name__ == "__main__":
    print("🌐 General Website Browsing Tracker")
    print("=" * 50)
    print("Adding recognition for ALL your website browsing!")
    
    if add_general_browsing_recognition():
        print("\n🎉 Success! Your Digital Twin now tracks general browsing!")
        print("\nNow you can ask:")
        print("• 'What websites did I visit?'")
        print("• 'What sites did I browse today?'") 
        print("• 'Where did I go on the internet?'")
        print("• 'What platforms did I use?'")
        
        print("\n🌟 Expected friendly responses:")
        print("• 'Today you browsed 5 different websites: Salesforce, LinkedIn, Claude AI, and 2 more sites!'")
        print("• 'You used LinkedIn (people finder), Microsoft websites, and other sites. You really explored the internet!'")
        print("• 'Today you worked on your sales computer, used AI tools, and browsed different websites.'")
        
        print("\n🚀 Restart your Digital Twin:")
        print("python enhanced_twin_controller.py")
    else:
        print("\n❌ Enhancement failed - try manual approach")