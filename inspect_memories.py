#!/usr/bin/env python3
"""
Memory Inspector - View and analyze stored memories
Shows where and how your digital twin stores learning
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

def inspect_azure_memories():
    """Inspect Azure Search memory store"""
    print("🔍 AZURE SEARCH MEMORY STORE")
    print("-" * 40)
    
    load_dotenv()
    
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    index = os.getenv("AZURE_SEARCH_INDEX") 
    
    print(f"Endpoint: {endpoint}")
    print(f"Index: {index}")
    
    if endpoint and index:
        try:
            from hybrid_memory_manager import HybridMemoryManager
            
            azure_config = {
                "search_endpoint": endpoint,
                "search_key": os.getenv("AZURE_SEARCH_KEY"),
                "index_name": index
            }
            
            memory_manager = HybridMemoryManager(azure_config)
            
            # Get user profile to see memory stats
            profile = memory_manager.get_user_memory_profile("default_user")
            
            print(f"\nMemory Statistics:")
            print(f"  Total memories: {profile.get('total_memories', 0)}")
            print(f"  Average importance: {profile.get('average_importance', 0):.2f}")
            print(f"  Recent activity: {profile.get('recent_activity', 0)} (last 7 days)")
            
            # Show domain distribution
            domains = profile.get('domain_distribution', {})
            if domains:
                print(f"\nMemory Domains:")
                for domain, count in domains.items():
                    print(f"  • {domain}: {count} memories")
            
            # Show top semantic tags
            tags = profile.get('top_semantic_tags', [])
            if tags:
                print(f"\nTop Topics:")
                for tag, count in tags[:5]:
                    print(f"  • {tag}: {count} mentions")
            
            return True
            
        except Exception as e:
            print(f"Error accessing Azure memories: {e}")
            return False
    else:
        print("Azure configuration not found")
        return False

def inspect_session_files():
    """Inspect local session storage"""
    print("\n💾 LOCAL SESSION STORAGE")
    print("-" * 40)
    
    sessions_dir = Path("sessions")
    if not sessions_dir.exists():
        print("No sessions directory found")
        return
    
    session_files = list(sessions_dir.glob("*.json"))
    print(f"Found {len(session_files)} session files:")
    
    for session_file in session_files:
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            user_id = session_data.get('user_id', 'unknown')
            session_start = session_data.get('session_start', 'unknown')
            history_count = len(session_data.get('conversation_history', []))
            
            print(f"\n📄 {session_file.name}")
            print(f"  User: {user_id}")
            print(f"  Started: {session_start}")
            print(f"  Conversations: {history_count}")
            
            # Show recent conversations
            history = session_data.get('conversation_history', [])
            if history:
                print(f"  Recent exchanges:")
                for exchange in history[-2:]:  # Last 2 exchanges
                    if isinstance(exchange, dict):
                        user_msg = exchange.get('user', '')
                        assistant_msg = exchange.get('assistant', '')
                        if user_msg:
                            user_preview = user_msg[:50] + "..." if len(user_msg) > 50 else user_msg
                            print(f"    User: {user_preview}")
                        if assistant_msg:
                            assistant_preview = assistant_msg[:50] + "..." if len(assistant_msg) > 50 else assistant_msg
                            print(f"    Assistant: {assistant_preview}")
                
        except Exception as e:
            print(f"  Error reading {session_file.name}: {e}")

def inspect_memory_files():
    """Inspect exported memory inspection files"""
    print("\n📊 MEMORY INSPECTION FILES")
    print("-" * 40)
    
    inspection_files = list(Path(".").glob("*memory_inspection*.json"))
    
    if inspection_files:
        print(f"Found {len(inspection_files)} inspection files:")
        
        for file in inspection_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                print(f"\n📋 {file.name}")
                
                # Show basic stats
                if isinstance(data, dict):
                    if 'memories' in data:
                        print(f"  Memories exported: {len(data['memories'])}")
                    if 'user_profile' in data:
                        profile = data['user_profile']
                        print(f"  User: {profile.get('user_id', 'unknown')}")
                        print(f"  Total memories: {profile.get('total_memories', 0)}")
                    if 'export_timestamp' in data:
                        print(f"  Exported: {data['export_timestamp']}")
                
            except Exception as e:
                print(f"  Error reading {file.name}: {e}")
    else:
        print("No memory inspection files found")

def show_storage_summary():
    """Show summary of all storage locations"""
    print("\n📚 MEMORY STORAGE SUMMARY")
    print("=" * 50)
    
    print("🏗️ ARCHITECTURE:")
    print("  1. Long-term Memory: Azure Search (cloud)")
    print("     • Permanent storage of all experiences")
    print("     • Semantic search and retrieval")
    print("     • AI-powered understanding")
    print("")
    print("  2. Session Memory: Local JSON files")
    print("     • Recent conversations")
    print("     • User preferences and context")
    print("     • Continuity between sessions")
    print("")
    print("  3. Working Memory: In-memory during session")
    print("     • Current action items")
    print("     • Active document analysis")
    print("     • Meeting processing results")
    print("")
    print("🔄 DATA FLOW:")
    print("  User Input → Processing → Azure Search (permanent)")
    print("                      ↓")
    print("  Session Files (temporary) ← Working Memory")
    print("")
    print("🔍 RETRIEVAL:")
    print("  Questions → Search Azure → Find relevant memories")
    print("  Context → Load session → Continue conversation")
    print("")
    print("🛡️ PRIVACY & CONTROL:")
    print("  • All data tied to your Azure account")
    print("  • Session files stored locally")
    print("  • You control the data and can export/delete")
    print("  • No data sent to third parties")

def main():
    """Run complete memory inspection"""
    print("🧠 DIGITAL TWIN MEMORY INSPECTOR")
    print("=" * 50)
    print("This tool shows where and how your digital twin stores memories")
    print("")
    
    # Inspect different storage locations
    azure_success = inspect_azure_memories()
    inspect_session_files()
    inspect_memory_files()
    show_storage_summary()
    
    print("\n" + "=" * 50)
    if azure_success:
        print("✅ Memory system fully operational")
        print("Your digital twin is learning and storing memories in Azure Search")
    else:
        print("⚠️ Azure Search not accessible - using local storage only")
    
    print("\n💡 To view your memories interactively:")
    print("   python3 enhanced_twin_controller.py")
    print("   Then use: 'profile' or 'search <query>'")

if __name__ == "__main__":
    main()