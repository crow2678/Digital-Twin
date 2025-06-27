#!/usr/bin/env python3
"""
Quick API Status Check
Check if the extension is actually sending data to the API
"""

import requests
import json

def check_api_status():
    """Quick check of API status and user data"""
    
    base_url = "http://localhost:8000"
    user_id = "Paresh"
    
    print("🔍 Quick API Status Check")
    print("=" * 40)
    
    try:
        # Check API health
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ API Status: {health_data.get('status')}")
            print(f"📊 Total Events Stored: {health_data.get('stored_events', 0)}")
            print(f"👥 Active Users: {health_data.get('active_users', 0)}")
        else:
            print(f"❌ API Health Check Failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ API Not Accessible: {e}")
        return
    
    try:
        # Check user stats
        stats_response = requests.get(f"{base_url}/user/{user_id}/stats", timeout=15)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            
            print(f"\n📈 User {user_id} Statistics:")
            print(f"   Total Events: {stats_data.get('total_events', 0)}")
            
            if stats_data.get('event_types'):
                print(f"   Event Types:")
                for event_type, count in stats_data['event_types'].items():
                    print(f"     • {event_type}: {count}")
            
            if stats_data.get('domains'):
                print(f"   Domains ({len(stats_data['domains'])}):")
                for domain, count in list(stats_data['domains'].items())[:5]:
                    print(f"     • {domain}: {count}")
            
            if stats_data.get('session_info'):
                session = stats_data['session_info']
                print(f"   Last Activity: {session.get('last_activity', 'Unknown')}")
                print(f"   Events Processed: {session.get('events_processed', 0)}")
        else:
            print(f"❌ User Stats Failed: {stats_response.status_code}")
    except Exception as e:
        print(f"❌ User Stats Error: {e}")
    
    try:
        # Check root endpoint for more details
        root_response = requests.get(f"{base_url}/", timeout=10)
        if root_response.status_code == 200:
            root_data = root_response.json()
            print(f"\n🏠 Server Details:")
            print(f"   Service: {root_data.get('service')}")
            print(f"   Digital Twin Available: {root_data.get('digital_twin_available')}")
            print(f"   Digital Twin Connected: {root_data.get('digital_twin_connected')}")
    except Exception as e:
        print(f"⚠️ Root endpoint error: {e}")

def test_simple_post():
    """Test a simple POST to see if validation is working"""
    
    print(f"\n🧪 Testing Simple POST...")
    
    try:
        test_data = {
            "user_id": "Paresh",
            "event_data": {
                "type": "extension_test",
                "timestamp": 1702761600000,  # Fixed timestamp
                "domain": "test.local",
                "url": "http://test.local/",
                "user_id": "Paresh",
                "session_id": "test_session_123",
                "data": {"test": True, "source": "validation_test"}
            },
            "timestamp": "2025-06-16T22:00:00.000000Z",  # Fixed ISO format
            "source": "validation_test"
        }
        
        response = requests.post(
            "http://localhost:8000/behavioral-data",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ POST Test Successful!")
            print(f"   Message: {result.get('message')}")
            print(f"   Digital Twin Processed: {result.get('digital_twin_processed')}")
        else:
            print(f"❌ POST Test Failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw Response: {response.text}")
                
    except Exception as e:
        print(f"❌ POST Test Error: {e}")

if __name__ == "__main__":
    check_api_status()
    test_simple_post()
    
    print(f"\n💡 Next Steps:")
    print("1. If events > 0: Extension is working! ✅")
    print("2. If events = 0: Extension not sending data ❌")
    print("3. If POST test fails: Fix validation issues 🔧")
    print("4. Check chrome://extensions/ for extension status 🔍")