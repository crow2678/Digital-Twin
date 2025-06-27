#!/usr/bin/env python3
"""
Demo Script for Productivity Enhanced Digital Twin
Shows various use cases and capabilities
"""

def demo_document_analysis():
    """Demo document analysis capabilities"""
    
    sample_contract = """
    SERVICE AGREEMENT
    
    This agreement is between TechCorp Inc. and DataSolutions LLC, effective January 1, 2024.
    
    SCOPE OF WORK:
    - Provide data analytics services for customer insights
    - Monthly reporting and dashboards
    - Data migration from legacy systems
    
    DELIVERABLES:
    - Initial data audit due February 15, 2024
    - Migration plan due March 1, 2024  
    - Go-live date: April 30, 2024
    
    PAYMENT TERMS:
    - $50,000 setup fee due upon signing
    - $15,000 monthly recurring fee
    - Auto-renewal clause effective March 15, 2025
    
    KEY TERMS:
    - 30-day cancellation notice required
    - Liability cap at $100,000
    - Data retention for 7 years post-termination
    - SLA: 99.5% uptime guarantee
    
    RISKS:
    - Data migration may impact current operations
    - Legacy system compatibility unknown
    - Client team may need additional training
    """
    
    sample_meeting = """
    MEETING TRANSCRIPT: Q1 Planning Session
    Date: 2024-01-15
    Attendees: Sarah (PM), Mike (Engineering), John (Sales), Me
    
    Sarah: Let's review our Q1 objectives. We need to finalize the product roadmap.
    
    Mike: Engineering can deliver the API updates by February 20th, but we need the requirements from product team first.
    
    Me: I'll get those requirements to you by January 25th. Also, we should consider the security audit findings.
    
    John: Sales pipeline looks strong. We have 3 major prospects wanting demos by end of February.
    
    Sarah: Great. Mike, can you prepare the demo environment by February 10th?
    
    Mike: Yes, I'll handle that. But I need the UI mockups from design team.
    
    Me: I'll follow up with design team today. When do we need to make the final decision on the pricing strategy?
    
    John: We need pricing finalized by February 1st for the proposals.
    
    Sarah: Okay, let me schedule a pricing review meeting for January 28th. 
    
    ACTION ITEMS:
    - Me: Send requirements to Mike by Jan 25th
    - Me: Follow up with design team today  
    - Mike: Prepare demo environment by Feb 10th
    - John: Share prospect feedback by Jan 30th
    - Sarah: Schedule pricing meeting for Jan 28th
    
    DECISIONS:
    - API delivery date confirmed for Feb 20th
    - Demo deadline set for Feb 10th
    - Pricing review meeting scheduled
    """
    
    sample_email = """
    From: client@bigcorp.com
    Subject: Urgent: Data Migration Delays
    
    Hi,
    
    I'm writing to express concern about the delays in our data migration project. 
    We were expecting the initial phase to be completed by last Friday, but we haven't 
    received any updates.
    
    This delay is affecting our quarterly reporting and our board presentation is 
    next week. We need immediate clarification on:
    
    1. Current status of the migration
    2. Revised timeline with firm deadlines
    3. Compensation for the delays
    4. Steps to prevent future delays
    
    Please provide an update by end of day today.
    
    Best regards,
    Jennifer Smith
    CTO, BigCorp
    """
    
    print("🎬 PRODUCTIVITY TWIN DEMO")
    print("=" * 50)
    
    print("\n📄 DOCUMENT ANALYSIS DEMO")
    print("-" * 30)
    print("Sample Contract Analysis:")
    print("✓ Extracts key dates: Feb 15, Mar 1, Apr 30")
    print("✓ Identifies action items: Setup fee payment, deliverables")
    print("✓ Flags risks: Data migration impact, compatibility")
    print("✓ Generates questions:")
    print("  • Who handles the data migration testing?")
    print("  • What's our backup plan if legacy systems are incompatible?")
    print("  • Should we negotiate the liability cap upward?")
    
    print("\n🎤 MEETING PROCESSING DEMO")
    print("-" * 30)
    print("Meeting Analysis Results:")
    print("✓ My Action Items:")
    print("  • Send requirements to Mike by Jan 25th")
    print("  • Follow up with design team today")
    print("✓ Questions to Ask:")
    print("  • Mike: Do you need any specific format for requirements?")
    print("  • Design: What's your current workload for UI mockups?")
    print("✓ Suggested Emails:")
    print("  • To Mike: Requirements follow-up")
    print("  • To Design: UI mockup request")
    print("✓ Calendar Events:")
    print("  • Reminder: Send requirements (Jan 24)")
    print("  • Pricing review meeting (Jan 28)")
    
    print("\n✉️ EMAIL DRAFTING DEMO")
    print("-" * 30)
    print("Client Complaint Response:")
    print("✓ Acknowledges specific concerns")
    print("✓ Provides concrete timeline")
    print("✓ Offers compensation")
    print("✓ Suggests prevention measures")
    print("\nSample Response:")
    print("Subject: Re: Data Migration Update - Immediate Action Plan")
    print("Hi Jennifer,")
    print("I understand your frustration with the migration delays...")
    print("[Draft continues with specific timeline and compensation]")
    
    print("\n🧠 SMART QUESTIONS DEMO")
    print("-" * 30)
    print("Context: 'Planning new product launch'")
    print("Generated Questions:")
    print("• Strategic: What's our competitive differentiation?")
    print("• Risk: What regulatory approvals do we need?")
    print("• Tactical: What's our go-to-market budget?")
    print("• Opportunity: Should we target international markets?")
    
    print("\n📅 CALENDAR INTEGRATION DEMO")
    print("-" * 30)
    print("Suggested Events from Action Items:")
    print("• 'Work on: Requirements Document' - Jan 24, 2-4 PM")
    print("• 'Reminder: Mike's Demo Due' - Feb 9, 9 AM")
    print("• 'Follow-up: Design Team Response' - Jan 16, 10 AM")
    
    print("\n📊 DAILY BRIEFING DEMO")
    print("-" * 30)
    print("Today's Productivity Insights:")
    print("• Focus Time Available: 3 hours (10 AM - 1 PM)")
    print("• High Priority Tasks: 2 items due this week")
    print("• Meetings Today: 1 (with prep time needed)")
    print("• Suggested Actions:")
    print("  - Block 2 hours for requirements document")
    print("  - Prepare talking points for 3 PM client call")
    print("  - Follow up on pending design team response")

def demo_usage_scenarios():
    """Demo various usage scenarios"""
    
    print("\n🎯 USAGE SCENARIOS")
    print("=" * 50)
    
    scenarios = [
        {
            "title": "📋 Contract Review",
            "input": "Upload contract PDF",
            "output": [
                "Extracts key terms, dates, obligations",
                "Identifies potential risks and opportunities", 
                "Generates clarification questions",
                "Creates calendar reminders for deadlines",
                "Suggests negotiation points"
            ]
        },
        {
            "title": "🎤 Post-Meeting Productivity",
            "input": "Meeting transcript or notes",
            "output": [
                "Extracts your specific action items",
                "Identifies questions to ask others",
                "Drafts follow-up emails",
                "Suggests calendar events",
                "Tracks commitments made"
            ]
        },
        {
            "title": "✉️ Email Response Assistance",
            "input": "Complex email + your response intent",
            "output": [
                "Drafts professional response",
                "Addresses all original points",
                "Includes appropriate tone",
                "Suggests next steps",
                "Handles difficult situations diplomatically"
            ]
        },
        {
            "title": "🔍 Research Planning",
            "input": "Research topic + context",
            "output": [
                "Generates smart research questions",
                "Suggests information sources",
                "Creates research structure",
                "Identifies knowledge gaps",
                "Recommends deliverable formats"
            ]
        },
        {
            "title": "📈 Productivity Optimization",
            "input": "Daily work patterns",
            "output": [
                "Identifies peak productivity hours",
                "Suggests focus time blocks",
                "Optimizes meeting schedules",
                "Tracks completion patterns",
                "Recommends workflow improvements"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print(f"Input: {scenario['input']}")
        print("Output:")
        for output in scenario['output']:
            print(f"  • {output}")

def demo_integration_possibilities():
    """Demo integration with other tools"""
    
    print("\n🔗 INTEGRATION POSSIBILITIES")
    print("=" * 50)
    
    integrations = [
        "📅 Calendar (Google/Outlook) - Auto-create events from action items",
        "✉️ Email (Gmail/Outlook) - Send drafted responses directly", 
        "📋 Task Management (Asana/Trello) - Sync action items",
        "💬 Slack/Teams - Send meeting summaries to channels",
        "📄 Document Storage (Drive/OneDrive) - Analyze uploaded files",
        "🎥 Meeting Tools (Zoom/Teams) - Process auto-transcripts",
        "📊 CRM Systems - Update customer interaction data",
        "⏰ Time Tracking - Log time spent on generated tasks",
        "🔔 Notification Systems - Alert on upcoming deadlines",
        "📝 Note-taking Apps (Notion/Obsidian) - Structured insight storage"
    ]
    
    for integration in integrations:
        print(f"  • {integration}")

def main():
    """Run the complete demo"""
    
    demo_document_analysis()
    demo_usage_scenarios() 
    demo_integration_possibilities()
    
    print("\n" + "=" * 50)
    print("🚀 READY TO BUILD YOUR PRODUCTIVITY TWIN!")
    print("=" * 50)
    print("\nNext Steps:")
    print("1. Test the basic implementation: python3 productivity_enhanced_twin.py")
    print("2. Try document analysis with real content")
    print("3. Process a meeting transcript")
    print("4. Generate smart questions for your current projects")
    print("5. Draft responses to challenging emails")
    print("\n💡 The system learns your patterns and becomes more helpful over time!")

if __name__ == "__main__":
    main()