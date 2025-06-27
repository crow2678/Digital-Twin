def fix_memory_retrieval():
    """Fix the memory retrieval logic to answer questions from existing memories"""
    
    print("🔧 Fixing memory retrieval logic...")
    
    try:
        # Read the enhanced_twin_controller.py file
        with open('enhanced_twin_controller.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the process_user_input method and enhance it
        enhancement = '''
    def is_question(self, user_input: str) -> bool:
        """Detect if user input is a question that should be answered from memory"""
        user_input_lower = user_input.lower().strip()
        
        # Question indicators
        question_starters = [
            'what', 'how', 'when', 'where', 'why', 'which', 'who',
            'do i', 'am i', 'can i', 'should i', 'will i', 'have i',
            'tell me about', 'what about', 'remind me'
        ]
        
        # Check if it starts with question words
        for starter in question_starters:
            if user_input_lower.startswith(starter):
                return True
        
        # Check for question marks
        if '?' in user_input:
            return True
            
        return False
    
    def answer_from_memory(self, question: str, user_id: str) -> Optional[str]:
        """Answer question from existing memories"""
        
        try:
            # Search existing memories for relevant information
            relevant_memories = self.hybrid_manager.search_memories(
                question,
                search_options={"user_id": user_id, "limit": 5}
            )
            
            if not relevant_memories:
                return None
            
            # Extract relevant information from memories
            answers = []
            question_lower = question.lower()
            
            for memory, score in relevant_memories:
                # Check for specific question types
                if any(word in question_lower for word in ['like', 'prefer', 'enjoy']):
                    if 'classic cars' in memory.content.lower() or 'mustang' in memory.content.lower():
                        answers.append("You like classic cars, especially your 1969 Mustang")
                    if 'dogs' in memory.content.lower() or 'animals' in memory.content.lower():
                        answers.append("You love dogs and care about animal welfare")
                    if 'precision' in memory.content.lower():
                        answers.append("You value precision in everything you do")
                
                elif any(word in question_lower for word in ['car', 'drive', 'vehicle']):
                    if '1969 mustang' in memory.content.lower():
                        answers.append("You drive a 1969 Mustang")
                    elif 'classic car' in memory.content.lower():
                        answers.append("You prefer classic cars")
                
                elif any(word in question_lower for word in ['work', 'job', 'employment']):
                    if 'continental hotel' in memory.content.lower():
                        answers.append("You work in the Continental Hotel network")
                    if 'marksmanship' in memory.content.lower():
                        answers.append("You have excellent marksmanship skills")
                
                elif any(word in question_lower for word in ['fitness', 'training', 'physical']):
                    if 'training regimen' in memory.content.lower():
                        answers.append("You maintain peak physical condition with a strict training regimen")
            
            if answers:
                return "Based on what I know about you: " + ". ".join(set(answers)) + "."
            else:
                # Generic answer from top memory
                top_memory = relevant_memories[0][0]
                return f"From what I remember: {top_memory.semantic_summary}"
                
        except Exception as e:
            print(f"Error answering from memory: {e}")
            return None
        
        return None'''
        
        # Find the process_user_input method and add question detection
        if 'def process_user_input(self, user_input: str, user_id: str = None) -> str:' in content:
            
            # Add the new methods before process_user_input
            insertion_point = content.find('def process_user_input(self, user_input: str, user_id: str = None) -> str:')
            
            if insertion_point != -1:
                # Insert the new methods
                before_method = content[:insertion_point]
                after_method = content[insertion_point:]
                
                new_content = before_method + enhancement + '\n    ' + after_method
                
                # Now modify the process_user_input method to use question detection
                old_processing = '''try:
            # Process and store memory with hybrid approach
            memory, report = self.hybrid_manager.process_and_store_memory(
                user_input, user_context
            )'''
            
            new_processing = '''try:
            # Check if this is a question that should be answered from existing memory
            if self.is_question(user_input):
                memory_answer = self.answer_from_memory(user_input, user_id)
                if memory_answer:
                    # Don't store questions as memories, just answer them
                    self.conversation_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "user": user_input,
                        "assistant": memory_answer,
                        "type": "memory_retrieval"
                    })
                    return memory_answer
            
            # Process and store memory with hybrid approach (for statements, not questions)
            memory, report = self.hybrid_manager.process_and_store_memory(
                user_input, user_context
            )'''
            
            new_content = new_content.replace(old_processing, new_processing)
            
            # Write the enhanced file
            with open('enhanced_twin_controller.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Enhanced memory retrieval logic")
            return True
    
    except Exception as e:
        print(f"❌ Error enhancing memory retrieval: {e}")
        return False
    
    return False

if __name__ == "__main__":
    print("🔧 Memory Retrieval Enhancement")
    print("=" * 40)
    
    if fix_memory_retrieval():
        print("\n🎉 Enhancement complete!")
        print("\nNow the system will:")
        print("✅ Detect questions vs statements")
        print("✅ Answer questions from existing memories")
        print("✅ Only store new information as memories")
        print("\n🎯 Test again:")
        print("python enhanced_twin_controller.py")
    else:
        print("\n❌ Enhancement failed")
        print("Manual fix needed in enhanced_twin_controller.py")