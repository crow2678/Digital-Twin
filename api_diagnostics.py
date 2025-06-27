#!/usr/bin/env python3
"""
API Diagnostics - Check why behavioral API isn't responding
"""

import requests
import socket
import subprocess
import sys
from time import sleep

def check_port(port):
    """Check if port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def check_process():
    """Check for running behavioral API processes"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = [line for line in result.stdout.split('\n') if 'behavioral_api_server' in line and 'grep' not in line]
        return lines
    except:
        return []

def test_api_endpoints():
    """Test various API endpoints"""
    endpoints = [
        'http://localhost:8000/',
        'http://localhost:8000/docs',
        'http://localhost:8000/health',
        'http://localhost:8000/all-events/Paresh'
    ]
    
    results = {}
    for url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            results[url] = f"✅ {response.status_code} {response.reason}"
        except requests.exceptions.Timeout:
            results[url] = "⏰ Timeout (5s)"
        except requests.exceptions.ConnectionError:
            results[url] = "❌ Connection refused"
        except Exception as e:
            results[url] = f"❌ Error: {str(e)}"
    
    return results

def main():
    print("🔍 API Diagnostics Report")
    print("=" * 40)
    
    # Check port
    port_open = check_port(8000)
    print(f"Port 8000 listening: {'✅ Yes' if port_open else '❌ No'}")
    
    # Check processes
    processes = check_process()
    print(f"API processes running: {len(processes)}")
    for proc in processes:
        print(f"  📍 {proc}")
    
    if port_open:
        print("\n🌐 Testing API endpoints...")
        results = test_api_endpoints()
        for url, status in results.items():
            print(f"  {url}: {status}")
    else:
        print("\n❌ Port 8000 not listening - API server not running")
        print("\n🚀 To start the API server:")
        print("   cd /mnt/c/Tavant/Tavant/02_Paresh/Fun/digital-twin")
        print("   python3 behavioral_api_server.py")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()