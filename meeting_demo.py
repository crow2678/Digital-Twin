#!/usr/bin/env python3
"""
Interactive Meeting Processing Demo
Shows how to use the meeting feature step by step
"""

def demo_meeting_scenarios():
    """Demo different types of meeting scenarios"""
    
    scenarios = {
        "team_planning": {
            "title": "Team Planning Meeting",
            "transcript": """
Team Planning Meeting - January 15, 2024
Attendees: Sarah (PM), Mike (Dev), Lisa (Design), Me

Sarah: Let's finalize our Q1 roadmap. We need to ship the new dashboard by March 15th.

Me: I can handle the API integration, but I'll need the database schema from Mike first.

Mike: I'll have the schema ready by February 1st. Also, we should consider performance testing.

Lisa: I'm working on the UI mockups. Should have initial designs by January 25th.

Sarah: Great. Mike, can you also set up the staging environment?

Mike: Yes, I'll get that done by February 5th.

Me: I'll need to coordinate with the QA team for testing. Should I schedule that now?

Sarah: Yes, please reach out to them this week. Also, we need to decide on the rollout strategy.

DECISIONS:
- Dashboard launch: March 15th
- Performance testing included
- QA team involvement confirmed
            """,
            "expected_insights": [
                "My action items: Get schema from Mike, Contact QA team",
                "Questions to ask: Mike about schema format, QA about testing timeline",
                "Follow-up emails: To Mike about schema, To QA about coordination",
                "Calendar events: Schema deadline reminder, QA meeting"
            ]
        },
        
        "client_meeting": {
            "title": "Client Requirements Meeting", 
            "transcript": """
Client Requirements Meeting - TechCorp Project
Attendees: Jennifer (Client), Mark (Client Tech Lead), Me

Jennifer: We need the new system to handle 10,000 concurrent users by Q2.

Me: That's ambitious but doable. What's your current peak load?

Mark: Around 2,000 users, but we're expecting 5x growth after the marketing campaign.

Me: I'll need to review your infrastructure. Can you provide current server specs?

Jennifer: Mark can get you that by tomorrow. Also, what about data migration?

Me: For 10,000 users, we'll need a phased approach. I recommend starting with a pilot group.

Mark: Makes sense. How long for full migration?

Me: About 6-8 weeks for complete rollout, assuming no major technical blockers.

Jennifer: We need it done by April 30th for the board presentation.

NEXT STEPS:
- Mark to send server specs tomorrow
- Me to create migration timeline by Friday
- Schedule technical deep-dive next week
            """,
            "expected_insights": [
                "My action items: Review infrastructure, Create migration timeline",
                "Client commitments: Server specs from Mark tomorrow", 
                "Questions to ask: About budget for infrastructure upgrades",
                "Risks: Tight timeline, 5x scale increase, technical unknowns"
            ]
        },
        
        "vendor_meeting": {
            "title": "Vendor Evaluation Meeting",
            "transcript": """
Vendor Evaluation - DataSoft Solutions
Attendees: Alex (Vendor Sales), Sarah (Vendor Tech), Me

Alex: Our platform can reduce your processing time by 60% and cut costs by 40%.

Me: That sounds impressive. What's the implementation timeline?

Sarah: Typically 8-12 weeks depending on data complexity and integration needs.

Me: We have some legacy systems. How do you handle data migration?

Sarah: We provide automated migration tools and dedicated support. Success rate is 99.2%.

Alex: We're offering a 20% discount if you sign by month-end, plus free training.

Me: I need to evaluate this against two other vendors. When do you need a decision?

Alex: We'd like an answer by February 15th to lock in Q1 pricing.

CONCERNS:
- No mention of data security certifications
- Pricing seems too good - what are the hidden costs?
- 8-12 week timeline might conflict with our Q2 deadline
            """,
            "expected_insights": [
                "My action items: Compare with other vendors, Check references",
                "Questions to ask: About security certifications, hidden costs",
                "Timeline pressure: Decision needed by Feb 15th",
                "Red flags: Aggressive pricing, vague timeline"
            ]
        }
    }
    
    print("🎤 MEETING PROCESSING SCENARIOS")
    print("=" * 50)
    
    for scenario_id, scenario in scenarios.items():
        print(f"\n📋 {scenario['title']}")
        print("-" * 30)
        
        print("What the meeting processing will extract:")
        for insight in scenario['expected_insights']:
            print(f"  ✓ {insight}")
        
        print(f"\nTo process this meeting, you would use:")
        print(f"meeting {scenario['transcript'][:100]}...")

def demo_interactive_usage():
    """Show how to use meeting processing interactively"""
    
    print("\n🚀 HOW TO USE MEETING PROCESSING")
    print("=" * 50)
    
    print("\n1. START THE PRODUCTIVITY TWIN:")
    print("   python3 productivity_enhanced_twin.py")
    
    print("\n2. USE THE MEETING COMMAND:")
    print("   meeting [paste your transcript or notes here]")
    
    print("\n3. EXAMPLE SESSION:")
    print("   You: meeting Team standup: Sarah said API is 80% done.")
    print("        Mike needs help with deployment. I offered to review.")
    print("        Deadline is still Friday. Need to sync with QA tomorrow.")
    print("")
    print("   Twin: 🎤 MEETING ANALYSIS")
    print("         My Action Items:")
    print("         • Review Mike's deployment (Priority: high)")
    print("         • Sync with QA team tomorrow")
    print("         ")
    print("         Questions to Ask:")
    print("         • Mike: What specific deployment issues?")
    print("         • QA: Are you ready for Friday testing?")
    print("         ")
    print("         Suggested Emails:")
    print("         • To Mike: Deployment review offer")
    print("         • To QA: Tomorrow sync confirmation")
    
    print("\n4. ADVANCED FEATURES:")
    print("   • Automatically tracks action items")
    print("   • Generates follow-up questions")
    print("   • Suggests calendar events")
    print("   • Identifies decision points")
    print("   • Rates meeting effectiveness")
    print("   • Recommends next steps")

def demo_meeting_types():
    """Show different types of meetings you can process"""
    
    meeting_types = [
        "📊 **Team Standups** - Extract blockers, progress, action items",
        "📋 **Planning Meetings** - Identify roadmap items, deadlines, dependencies", 
        "🤝 **Client Meetings** - Track requirements, commitments, next steps",
        "🔍 **Vendor Meetings** - Evaluate proposals, identify concerns, compare options",
        "🎯 **Strategy Sessions** - Capture decisions, priorities, strategic questions",
        "🐛 **Bug Triage** - Assign issues, set priorities, track resolution plans",
        "📈 **Review Meetings** - Note feedback, action items, improvement areas",
        "🚨 **Incident Reviews** - Document timeline, causes, prevention measures",
        "💼 **Sales Calls** - Track client needs, objections, follow-up actions",
        "🎓 **Training Sessions** - Capture key learnings, application steps"
    ]
    
    print("\n📝 TYPES OF MEETINGS YOU CAN PROCESS")
    print("=" * 50)
    
    for meeting_type in meeting_types:
        print(f"  {meeting_type}")

def main():
    """Run the complete meeting demo"""
    
    print("🎤 MEETING PROCESSING - COMPLETE GUIDE")
    print("=" * 60)
    
    demo_meeting_scenarios()
    demo_interactive_usage()
    demo_meeting_types()
    
    print("\n" + "=" * 60)
    print("🚀 READY TO PROCESS YOUR MEETINGS!")
    print("=" * 60)
    
    print("\nQuick Start:")
    print("1. Run: python3 productivity_enhanced_twin.py")
    print("2. Type: meeting [your meeting content]")
    print("3. Get instant action items and insights!")
    
    print("\n💡 Pro Tips:")
    print("• Include attendee names for better analysis")
    print("• Mention deadlines and commitments clearly") 
    print("• The more context, the better the insights")
    print("• Review and customize the generated action items")

if __name__ == "__main__":
    main()