#!/usr/bin/env python3
"""
Demo script for Digital Twin Web Application
Shows the web interface with sample data
"""

import asyncio
import webbrowser
import time
from pathlib import Path

def show_demo_info():
    """Show demo information"""
    print("🌐 DIGITAL TWIN WEB APPLICATION DEMO")
    print("=" * 50)
    print()
    print("🎯 This demo shows:")
    print("   • Professional web interface")
    print("   • Document upload and analysis") 
    print("   • Meeting processing capabilities")
    print("   • Real-time progress tracking")
    print("   • Copy and export functionality")
    print()
    print("📋 Sample Use Cases:")
    print("   1. Upload a contract for analysis")
    print("   2. Process meeting transcript")
    print("   3. Generate smart questions")
    print("   4. Draft email responses")
    print()
    print("🚀 Starting web server...")
    print("   URL: http://localhost:8080")
    print("   Press Ctrl+C to stop")
    print()

def create_sample_files():
    """Create sample files for demo"""
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # Sample contract
    sample_contract = """
SERVICE AGREEMENT

This agreement between TechCorp Inc. and DataSolutions LLC is effective January 1, 2024.

SCOPE OF WORK:
- Provide AI consulting services for digital transformation
- Implement machine learning models for customer insights
- Monthly progress reports and strategic recommendations

DELIVERABLES:
- Initial AI strategy document due February 15, 2024
- Proof of concept delivery by March 15, 2024
- Full implementation completed by June 30, 2024

PAYMENT TERMS:
- $75,000 setup fee due upon contract signing
- $25,000 monthly recurring payments
- Performance bonus of $50,000 upon successful completion

KEY TERMS:
- 60-day cancellation notice required
- Liability cap at $200,000
- Intellectual property rights shared 50/50
- Service level agreement: 99.9% uptime
- Data confidentiality and security compliance required

POTENTIAL RISKS:
- AI model performance may vary with different data sets
- Integration challenges with legacy systems
- Regulatory compliance requirements may change
"""
    
    with open(uploads_dir / "sample_contract.txt", "w") as f:
        f.write(sample_contract)
    
    # Sample meeting transcript
    sample_meeting = """
QUARTERLY PLANNING MEETING
Date: January 20, 2024
Attendees: Sarah (VP Product), Mike (Engineering Lead), Lisa (Design Lead), John (Sales Director), Alex (Marketing)

Sarah: Let's review our Q1 objectives and finalize the product roadmap for our AI platform launch.

Mike: Engineering is 85% complete on the core ML pipeline. We should have beta ready by February 10th, but we need the UI designs finalized first.

Lisa: Design team is working on the final mockups. I can deliver the complete UI package by January 30th. However, we need feedback on the user onboarding flow.

John: Sales has pre-qualified 15 enterprise prospects who are interested in beta testing. We need pricing strategy finalized by February 1st for the beta program.

Alex: Marketing campaign is ready to launch, but we need product demo videos. Can we get a working prototype by February 5th for video production?

Sarah: Great progress everyone. Let me summarize the action items:

ACTION ITEMS:
- Mike: Deliver beta platform by February 10th
- Lisa: Complete UI designs and mockups by January 30th
- Lisa: Get feedback on user onboarding flow from product team
- John: Finalize pricing strategy by February 1st
- Alex: Coordinate with Mike for demo video production after February 5th
- Sarah: Schedule pricing review meeting for January 28th
- All: Provide feedback on UI designs by January 25th

DECISIONS MADE:
- Beta launch confirmed for February 10th
- UI design deadline set for January 30th
- Pricing strategy must be completed by February 1st
- Demo video production scheduled for after February 5th

NEXT STEPS:
- Schedule UI review meeting for January 25th
- Set up beta testing environment
- Prepare marketing materials for beta launch
- Coordinate with legal team on beta agreements
"""
    
    with open(uploads_dir / "sample_meeting.txt", "w") as f:
        f.write(sample_meeting)
    
    print("📁 Created sample files:")
    print("   • sample_contract.txt")
    print("   • sample_meeting.txt")

def main():
    """Main demo function"""
    show_demo_info()
    create_sample_files()
    
    # Import and run the web app
    try:
        # Add parent directory to path for imports
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        
        from web_app.app import app
        import uvicorn
        
        # Start server in a separate thread and open browser
        def start_server():
            uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open("http://localhost:8080")
        
        import threading
        
        # Start browser opener
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start server (this will block)
        print("🌐 Web application starting...")
        start_server()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped.")
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure you're running from the correct directory and have dependencies installed.")
        print("Run: pip install fastapi uvicorn python-multipart jinja2")
    except Exception as e:
        print(f"\n❌ Error starting demo: {e}")

if __name__ == "__main__":
    main()