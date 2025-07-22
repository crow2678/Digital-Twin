#!/usr/bin/env python3
"""
Digital Twin Technical Architecture Diagram
Proper architecture diagram with layers, interfaces, and data flow
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Arrow
from matplotlib.patches import ConnectionPatch, FancyArrowPatch
import numpy as np

def create_technical_architecture():
    # Create figure with proper aspect ratio for architecture
    fig, ax = plt.subplots(1, 1, figsize=(18, 14))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Architecture color scheme
    colors = {
        'presentation': '#2c3e50',    # Dark blue-gray
        'application': '#3498db',     # Blue
        'business': '#e74c3c',        # Red
        'data': '#27ae60',            # Green
        'infrastructure': '#95a5a6',  # Gray
        'external': '#f39c12',        # Orange
        'security': '#8e44ad'         # Purple
    }
    
    # Title
    ax.text(9, 13.5, 'Digital Twin System - Technical Architecture', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(9, 13.1, 'Enterprise AI-Powered Personal Productivity System', 
            fontsize=12, ha='center', style='italic')

    # === PRESENTATION LAYER ===
    presentation_layer = Rectangle((0.5, 11), 17, 1.5, 
                                 facecolor=colors['presentation'], 
                                 edgecolor='black', alpha=0.8)
    ax.add_patch(presentation_layer)
    ax.text(0.7, 12.2, 'PRESENTATION LAYER', fontsize=12, fontweight='bold', 
            color='white', va='center')
    
    # Web Interface
    web_box = Rectangle((1, 11.2), 3, 1.1, facecolor='white', 
                       edgecolor='black', alpha=0.9)
    ax.add_patch(web_box)
    ax.text(2.5, 11.75, 'Web Interface\n(React/FastAPI)', 
            fontsize=10, ha='center', va='center', fontweight='bold')
    
    # Mobile Interface
    mobile_box = Rectangle((4.5, 11.2), 2.5, 1.1, facecolor='white', 
                          edgecolor='black', alpha=0.9)
    ax.add_patch(mobile_box)
    ax.text(5.75, 11.75, 'Voice Interface\n(Real-time)', 
            fontsize=10, ha='center', va='center', fontweight='bold')
    
    # Chrome Extension
    chrome_box = Rectangle((7.5, 11.2), 3, 1.1, facecolor='white', 
                          edgecolor='black', alpha=0.9)
    ax.add_patch(chrome_box)
    ax.text(9, 11.75, 'Browser Extension\n(Behavioral Tracking)', 
            fontsize=10, ha='center', va='center', fontweight='bold')
    
    # Admin Interface
    admin_box = Rectangle((11, 11.2), 2.5, 1.1, facecolor='white', 
                         edgecolor='black', alpha=0.9)
    ax.add_patch(admin_box)
    ax.text(12.25, 11.75, 'Analytics\nDashboard', 
            fontsize=10, ha='center', va='center', fontweight='bold')
    
    # API Gateway
    gateway_box = Rectangle((14, 11.2), 3, 1.1, facecolor='white', 
                           edgecolor='black', alpha=0.9)
    ax.add_patch(gateway_box)
    ax.text(15.5, 11.75, 'API Gateway\n(Auth/Rate Limit)', 
            fontsize=10, ha='center', va='center', fontweight='bold')

    # === APPLICATION LAYER ===
    app_layer = Rectangle((0.5, 8.5), 17, 2, 
                         facecolor=colors['application'], 
                         edgecolor='black', alpha=0.8)
    ax.add_patch(app_layer)
    ax.text(0.7, 10.2, 'APPLICATION LAYER', fontsize=12, fontweight='bold', 
            color='white', va='center')
    
    # Core Services
    whisper_service = Rectangle((1, 9.5), 2.5, 0.8, facecolor='white', 
                               edgecolor='black', alpha=0.9)
    ax.add_patch(whisper_service)
    ax.text(2.25, 9.9, 'Whisper Service\n(Speech-to-Text)', 
            fontsize=9, ha='center', va='center')
    
    doc_service = Rectangle((4, 9.5), 2.5, 0.8, facecolor='white', 
                           edgecolor='black', alpha=0.9)
    ax.add_patch(doc_service)
    ax.text(5.25, 9.9, 'Document Processor\n(Smart Chunking)', 
            fontsize=9, ha='center', va='center')
    
    collab_service = Rectangle((7, 9.5), 2.5, 0.8, facecolor='white', 
                              edgecolor='black', alpha=0.9)
    ax.add_patch(collab_service)
    ax.text(8.25, 9.9, 'Collaboration API\n(Meeting Analysis)', 
            fontsize=9, ha='center', va='center')
    
    # Session Management
    session_mgmt = Rectangle((10, 9.5), 2.5, 0.8, facecolor='white', 
                            edgecolor='black', alpha=0.9)
    ax.add_patch(session_mgmt)
    ax.text(11.25, 9.9, 'Session Manager\n(User Context)', 
            fontsize=9, ha='center', va='center')
    
    # Notification Service
    notification_service = Rectangle((13, 9.5), 2.5, 0.8, facecolor='white', 
                                    edgecolor='black', alpha=0.9)
    ax.add_patch(notification_service)
    ax.text(14.25, 9.9, 'Notification Service\n(Real-time)', 
            fontsize=9, ha='center', va='center')
    
    # Security Layer (Cross-cutting)
    security_layer = Rectangle((15.8, 9.5), 1.5, 0.8, facecolor=colors['security'], 
                              edgecolor='black', alpha=0.9)
    ax.add_patch(security_layer)
    ax.text(16.55, 9.9, 'Security\nLayer', fontsize=9, ha='center', va='center', 
            color='white', fontweight='bold')
    
    # Integration Layer
    integration_box = Rectangle((1, 8.7), 15.5, 0.6, facecolor='lightblue', 
                               edgecolor='black', alpha=0.7)
    ax.add_patch(integration_box)
    ax.text(8.75, 9, 'Integration Layer (Message Queue, Event Bus, Service Mesh)', 
            fontsize=10, ha='center', va='center', fontweight='bold')

    # === BUSINESS LOGIC LAYER ===
    business_layer = Rectangle((0.5, 6), 17, 2, 
                              facecolor=colors['business'], 
                              edgecolor='black', alpha=0.8)
    ax.add_patch(business_layer)
    ax.text(0.7, 7.7, 'BUSINESS LOGIC LAYER', fontsize=12, fontweight='bold', 
            color='white', va='center')
    
    # AI Processing Engine
    ai_engine = Rectangle((1, 7), 4, 0.8, facecolor='white', 
                         edgecolor='black', alpha=0.9)
    ax.add_patch(ai_engine)
    ax.text(3, 7.4, 'AI Processing Engine\n(Azure OpenAI GPT-4 + Embeddings)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Memory Management
    memory_mgmt = Rectangle((5.5, 7), 4, 0.8, facecolor='white', 
                           edgecolor='black', alpha=0.9)
    ax.add_patch(memory_mgmt)
    ax.text(7.5, 7.4, 'Hybrid Memory Manager\n(Ontology + Vector Search)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Business Rules Engine
    rules_engine = Rectangle((10, 7), 3, 0.8, facecolor='white', 
                            edgecolor='black', alpha=0.9)
    ax.add_patch(rules_engine)
    ax.text(11.5, 7.4, 'Business Rules Engine\n(Workflow & Decisions)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Analytics Engine
    analytics_engine = Rectangle((13.5, 7), 3, 0.8, facecolor='white', 
                                edgecolor='black', alpha=0.9)
    ax.add_patch(analytics_engine)
    ax.text(15, 7.4, 'Analytics Engine\n(Performance Metrics)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Domain Models
    domain_models = Rectangle((1, 6.2), 15.5, 0.6, facecolor='lightcoral', 
                             edgecolor='black', alpha=0.7)
    ax.add_patch(domain_models)
    ax.text(8.75, 6.5, 'Domain Models (User, Memory, Session, Document, Conversation)', 
            fontsize=10, ha='center', va='center', fontweight='bold', color='white')

    # === DATA LAYER ===
    data_layer = Rectangle((0.5, 3.5), 17, 2, 
                          facecolor=colors['data'], 
                          edgecolor='black', alpha=0.8)
    ax.add_patch(data_layer)
    ax.text(0.7, 5.2, 'DATA LAYER', fontsize=12, fontweight='bold', 
            color='white', va='center')
    
    # Primary Database
    primary_db = Rectangle((1, 4.5), 2.5, 0.8, facecolor='white', 
                          edgecolor='black', alpha=0.9)
    ax.add_patch(primary_db)
    ax.text(2.25, 4.9, 'PostgreSQL\n(Transactional)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Cache Layer
    cache_layer = Rectangle((4, 4.5), 2.5, 0.8, facecolor='white', 
                           edgecolor='black', alpha=0.9)
    ax.add_patch(cache_layer)
    ax.text(5.25, 4.9, 'Redis Cache\n(Session/Memory)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Search Engine
    search_engine = Rectangle((7, 4.5), 2.5, 0.8, facecolor='white', 
                             edgecolor='black', alpha=0.9)
    ax.add_patch(search_engine)
    ax.text(8.25, 4.9, 'Azure Search\n(Cognitive)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Vector Database
    vector_db = Rectangle((10, 4.5), 2.5, 0.8, facecolor='white', 
                         edgecolor='black', alpha=0.9)
    ax.add_patch(vector_db)
    ax.text(11.25, 4.9, 'Vector DB\n(Embeddings)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Blob Storage
    blob_storage = Rectangle((13, 4.5), 2.5, 0.8, facecolor='white', 
                            edgecolor='black', alpha=0.9)
    ax.add_patch(blob_storage)
    ax.text(14.25, 4.9, 'Azure Blob\n(Documents)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Data Access Layer
    data_access = Rectangle((1, 3.7), 14.5, 0.6, facecolor='lightgreen', 
                           edgecolor='black', alpha=0.7)
    ax.add_patch(data_access)
    ax.text(8.25, 4, 'Data Access Layer (Repository Pattern, ORM, Connection Pooling)', 
            fontsize=10, ha='center', va='center', fontweight='bold')

    # === INFRASTRUCTURE LAYER ===
    infra_layer = Rectangle((0.5, 1), 17, 2, 
                           facecolor=colors['infrastructure'], 
                           edgecolor='black', alpha=0.8)
    ax.add_patch(infra_layer)
    ax.text(0.7, 2.7, 'INFRASTRUCTURE LAYER', fontsize=12, fontweight='bold', 
            color='white', va='center')
    
    # Container Platform
    container_platform = Rectangle((1, 2), 3, 0.8, facecolor='white', 
                                  edgecolor='black', alpha=0.9)
    ax.add_patch(container_platform)
    ax.text(2.5, 2.4, 'Docker Platform\n(Containerization)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Load Balancer
    load_balancer = Rectangle((4.5, 2), 2.5, 0.8, facecolor='white', 
                             edgecolor='black', alpha=0.9)
    ax.add_patch(load_balancer)
    ax.text(5.75, 2.4, 'Nginx\n(Load Balancer)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Monitoring
    monitoring = Rectangle((7.5, 2), 3, 0.8, facecolor='white', 
                          edgecolor='black', alpha=0.9)
    ax.add_patch(monitoring)
    ax.text(9, 2.4, 'Monitoring & Logging\n(Metrics/Alerts)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Cloud Platform
    cloud_platform = Rectangle((11, 2), 3, 0.8, facecolor='white', 
                              edgecolor='black', alpha=0.9)
    ax.add_patch(cloud_platform)
    ax.text(12.5, 2.4, 'Azure Cloud\n(IaaS/PaaS)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Network & Security
    network_security = Rectangle((14.5, 2), 2.5, 0.8, facecolor='white', 
                                edgecolor='black', alpha=0.9)
    ax.add_patch(network_security)
    ax.text(15.75, 2.4, 'Network/Security\n(VPN/Firewall)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Runtime Environment
    runtime_env = Rectangle((1, 1.2), 15.5, 0.6, facecolor='lightgray', 
                           edgecolor='black', alpha=0.7)
    ax.add_patch(runtime_env)
    ax.text(8.75, 1.5, 'Runtime Environment (Python 3.10, Node.js, OS Layer)', 
            fontsize=10, ha='center', va='center', fontweight='bold')

    # === EXTERNAL SYSTEMS ===
    external_box = Rectangle((0.2, 0.2), 17.6, 0.6, facecolor=colors['external'], 
                            edgecolor='black', alpha=0.8)
    ax.add_patch(external_box)
    ax.text(9, 0.5, 'EXTERNAL SYSTEMS: Azure OpenAI API | Azure Cognitive Services | Third-party APIs', 
            fontsize=10, ha='center', va='center', fontweight='bold', color='white')

    # === DATA FLOW ARROWS ===
    # Presentation to Application
    arrow1 = FancyArrowPatch((9, 11), (9, 10.5), 
                            arrowstyle='->', mutation_scale=15, 
                            color='blue', linewidth=2)
    ax.add_patch(arrow1)
    
    # Application to Business Logic
    arrow2 = FancyArrowPatch((9, 8.5), (9, 8), 
                            arrowstyle='->', mutation_scale=15, 
                            color='red', linewidth=2)
    ax.add_patch(arrow2)
    
    # Business Logic to Data
    arrow3 = FancyArrowPatch((9, 6), (9, 5.5), 
                            arrowstyle='->', mutation_scale=15, 
                            color='green', linewidth=2)
    ax.add_patch(arrow3)
    
    # Data to Infrastructure
    arrow4 = FancyArrowPatch((9, 3.5), (9, 3), 
                            arrowstyle='->', mutation_scale=15, 
                            color='gray', linewidth=2)
    ax.add_patch(arrow4)

    # === ARCHITECTURAL ANNOTATIONS ===
    # Performance Metrics
    perf_box = Rectangle((16, 8.5), 1.8, 2.5, facecolor='lightyellow', 
                        edgecolor='black', alpha=0.9, linestyle='--')
    ax.add_patch(perf_box)
    ax.text(16.9, 10.7, 'METRICS', fontsize=10, fontweight='bold', ha='center')
    ax.text(16.9, 10.3, '• 1,225 memories', fontsize=8, ha='center')
    ax.text(16.9, 10.0, '• 85% AI accuracy', fontsize=8, ha='center')
    ax.text(16.9, 9.7, '• 5min cache TTL', fontsize=8, ha='center')
    ax.text(16.9, 9.4, '• <2sec response', fontsize=8, ha='center')
    ax.text(16.9, 9.1, '• 40+ domains', fontsize=8, ha='center')
    ax.text(16.9, 8.8, '• Real-time sync', fontsize=8, ha='center')

    # Legend
    ax.text(0.5, 0, 'ARCHITECTURE LEGEND:', fontsize=8, fontweight='bold')
    ax.text(3, 0, 'Blue→App Flow', fontsize=7, color='blue')
    ax.text(5, 0, 'Red→Business Logic', fontsize=7, color='red')  
    ax.text(7.5, 0, 'Green→Data Flow', fontsize=7, color='green')
    ax.text(9.5, 0, 'Gray→Infrastructure', fontsize=7, color='gray')

    plt.tight_layout()
    return fig

# Generate the proper architecture diagram
if __name__ == "__main__":
    fig = create_technical_architecture()
    
    # Save as high-resolution files
    fig.savefig('/mnt/c/Tavant/Tavant/02_Paresh/Fun/digital-twin/technical_architecture_diagram.png', 
                dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    
    fig.savefig('/mnt/c/Tavant/Tavant/02_Paresh/Fun/digital-twin/technical_architecture_diagram.svg', 
                format='svg', bbox_inches='tight', facecolor='white', edgecolor='none')
    
    print("✅ Technical Architecture Diagram created successfully!")
    print("📁 Files saved:")
    print("  - technical_architecture_diagram.png (High-resolution)")
    print("  - technical_architecture_diagram.svg (Vector format)")
    print("\n🏗️  Architecture Features:")
    print("  - Layered architecture with proper separation")
    print("  - Data flow arrows between layers") 
    print("  - Cross-cutting concerns (security, integration)")
    print("  - External systems integration")
    print("  - Performance metrics annotation")
    print("  - Proper architectural notation and patterns")