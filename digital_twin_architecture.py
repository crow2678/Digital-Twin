#!/usr/bin/env python3
"""
Digital Twin Architecture Diagram Generator
Creates a visual representation of the sophisticated digital twin system architecture
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_architecture_diagram():
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Color scheme
    colors = {
        'frontend': '#3498db',      # Blue
        'api': '#e74c3c',          # Red  
        'ai': '#f39c12',           # Orange
        'memory': '#9b59b6',       # Purple
        'storage': '#2ecc71',      # Green
        'services': '#34495e',     # Dark gray
        'data': '#1abc9c'          # Teal
    }
    
    # Title
    ax.text(10, 14.5, 'Digital Twin Architecture', fontsize=24, fontweight='bold', 
            ha='center', va='center')
    ax.text(10, 14, 'AI-Powered Personal Productivity Assistant', fontsize=14, 
            ha='center', va='center', style='italic')

    # Frontend Layer
    frontend_box = FancyBboxPatch((0.5, 11.5), 4, 2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['frontend'], 
                                  edgecolor='black', alpha=0.7)
    ax.add_patch(frontend_box)
    ax.text(2.5, 12.8, 'Frontend Layer', fontsize=14, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(2.5, 12.4, '• Modern Web Dashboard', fontsize=10, ha='center', va='center', color='white')
    ax.text(2.5, 12.1, '• Real-time Voice Interface', fontsize=10, ha='center', va='center', color='white')
    ax.text(2.5, 11.8, '• Digital Cockpit UI', fontsize=10, ha='center', va='center', color='white')

    # Chrome Extension
    chrome_box = FancyBboxPatch((6, 12), 3, 1.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor=colors['data'], 
                               edgecolor='black', alpha=0.7)
    ax.add_patch(chrome_box)
    ax.text(7.5, 12.9, 'Chrome Extension', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(7.5, 12.5, 'Behavioral Tracking', fontsize=10, ha='center', va='center', color='white')
    ax.text(7.5, 12.2, 'Tab & Activity Monitor', fontsize=10, ha='center', va='center', color='white')

    # API Gateway
    api_box = FancyBboxPatch((0.5, 9), 8, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=colors['api'], 
                            edgecolor='black', alpha=0.7)
    ax.add_patch(api_box)
    ax.text(4.5, 9.9, 'FastAPI Gateway Layer', fontsize=14, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(4.5, 9.4, 'REST APIs • WebSocket • CORS • Authentication • Rate Limiting', 
            fontsize=10, ha='center', va='center', color='white')

    # Core Services Layer
    # Whisper Service
    whisper_box = FancyBboxPatch((0.5, 6.5), 3, 1.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['services'], 
                                edgecolor='black', alpha=0.7)
    ax.add_patch(whisper_box)
    ax.text(2, 7.6, 'Whisper Service', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(2, 7.2, '• Speech-to-Text', fontsize=10, ha='center', va='center', color='white')
    ax.text(2, 6.9, '• Real-time Processing', fontsize=10, ha='center', va='center', color='white')
    ax.text(2, 6.6, '• Docker Container', fontsize=10, ha='center', va='center', color='white')

    # Document Processor
    doc_box = FancyBboxPatch((4, 6.5), 3, 1.8, 
                            boxstyle="round,pad=0.1", 
                            facecolor=colors['services'], 
                            edgecolor='black', alpha=0.7)
    ax.add_patch(doc_box)
    ax.text(5.5, 7.6, 'Document Intelligence', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(5.5, 7.2, '• Smart Chunking', fontsize=10, ha='center', va='center', color='white')
    ax.text(5.5, 6.9, '• Token Management', fontsize=10, ha='center', va='center', color='white')
    ax.text(5.5, 6.6, '• PDF/DOCX Parser', fontsize=10, ha='center', va='center', color='white')

    # Collaboration API
    collab_box = FancyBboxPatch((7.5, 6.5), 3, 1.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor=colors['services'], 
                               edgecolor='black', alpha=0.7)
    ax.add_patch(collab_box)
    ax.text(9, 7.6, 'Collaboration API', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(9, 7.2, '• Meeting Processing', fontsize=10, ha='center', va='center', color='white')
    ax.text(9, 6.9, '• Action Item Extract', fontsize=10, ha='center', va='center', color='white')
    ax.text(9, 6.6, '• Email Drafting', fontsize=10, ha='center', va='center', color='white')

    # AI Engine Layer
    ai_box = FancyBboxPatch((11, 9), 8, 4, 
                           boxstyle="round,pad=0.1", 
                           facecolor=colors['ai'], 
                           edgecolor='black', alpha=0.7)
    ax.add_patch(ai_box)
    ax.text(15, 12.5, 'AI Processing Engine', fontsize=16, fontweight='bold', 
            ha='center', va='center', color='white')
    
    # Azure OpenAI
    ax.text(15, 11.9, '🧠 Azure OpenAI GPT-4', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(15, 11.5, 'LLM Response Synthesis', fontsize=10, ha='center', va='center', color='white')
    
    # Embeddings
    ax.text(15, 11, '🔗 Azure OpenAI Embeddings', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(15, 10.6, 'Semantic Vector Generation', fontsize=10, ha='center', va='center', color='white')
    
    # AI Semantic Processor
    ax.text(15, 10.1, '🎯 AI Semantic Processor', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(15, 9.7, 'Confidence Scoring • Entity Extraction', fontsize=10, ha='center', va='center', color='white')
    ax.text(15, 9.4, 'Context Understanding • Relationship Mapping', fontsize=10, ha='center', va='center', color='white')

    # Memory System
    memory_box = FancyBboxPatch((11, 6), 8, 2.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor=colors['memory'], 
                               edgecolor='black', alpha=0.7)
    ax.add_patch(memory_box)
    ax.text(15, 7.8, 'Hybrid Memory System', fontsize=16, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(15, 7.4, '🔍 Azure Cognitive Search', fontsize=12, ha='center', va='center', color='white')
    ax.text(15, 7, '📊 Digital Twin Ontology (40+ Domains)', fontsize=11, ha='center', va='center', color='white')
    ax.text(15, 6.6, '⚡ Redis Caching Layer (5min TTL)', fontsize=11, ha='center', va='center', color='white')
    ax.text(15, 6.2, 'Hybrid Classification • Performance Optimization', fontsize=10, ha='center', va='center', color='white')

    # Storage Layer
    # PostgreSQL
    postgres_box = FancyBboxPatch((0.5, 3.5), 3, 1.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['storage'], 
                                 edgecolor='black', alpha=0.7)
    ax.add_patch(postgres_box)
    ax.text(2, 4.6, 'PostgreSQL', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(2, 4.2, '• User Sessions', fontsize=10, ha='center', va='center', color='white')
    ax.text(2, 3.9, '• Conversation History', fontsize=10, ha='center', va='center', color='white')
    ax.text(2, 3.6, '• Metadata Storage', fontsize=10, ha='center', va='center', color='white')

    # Redis
    redis_box = FancyBboxPatch((4, 3.5), 3, 1.8, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['storage'], 
                              edgecolor='black', alpha=0.7)
    ax.add_patch(redis_box)
    ax.text(5.5, 4.6, 'Redis Cache', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(5.5, 4.2, '• Memory Cache', fontsize=10, ha='center', va='center', color='white')
    ax.text(5.5, 3.9, '• Session Cache', fontsize=10, ha='center', va='center', color='white')
    ax.text(5.5, 3.6, '• Performance Metrics', fontsize=10, ha='center', va='center', color='white')

    # Azure Blob Storage
    blob_box = FancyBboxPatch((7.5, 3.5), 3, 1.8, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['storage'], 
                             edgecolor='black', alpha=0.7)
    ax.add_patch(blob_box)
    ax.text(9, 4.6, 'Azure Blob Storage', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(9, 4.2, '• Document Storage', fontsize=10, ha='center', va='center', color='white')
    ax.text(9, 3.9, '• Large File Handling', fontsize=10, ha='center', va='center', color='white')
    ax.text(9, 3.6, '• Content Persistence', fontsize=10, ha='center', va='center', color='white')

    # Vector Database
    vector_box = FancyBboxPatch((11.5, 3.5), 3, 1.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor=colors['storage'], 
                               edgecolor='black', alpha=0.7)
    ax.add_patch(vector_box)
    ax.text(13, 4.6, 'Vector Database', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(13, 4.2, '• Embeddings Storage', fontsize=10, ha='center', va='center', color='white')
    ax.text(13, 3.9, '• Semantic Search', fontsize=10, ha='center', va='center', color='white')
    ax.text(13, 3.6, '• Similarity Matching', fontsize=10, ha='center', va='center', color='white')

    # Infrastructure
    infra_box = FancyBboxPatch((15.5, 3.5), 3.5, 1.8, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['services'], 
                              edgecolor='black', alpha=0.7)
    ax.add_patch(infra_box)
    ax.text(17.25, 4.6, 'Infrastructure', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(17.25, 4.2, '🐳 Docker Containers', fontsize=10, ha='center', va='center', color='white')
    ax.text(17.25, 3.9, '🌐 Nginx Load Balancer', fontsize=10, ha='center', va='center', color='white')
    ax.text(17.25, 3.6, '☁️ Azure Deployment', fontsize=10, ha='center', va='center', color='white')

    # Data Flow Section
    ax.text(10, 2.8, 'Real Data Collected', fontsize=14, fontweight='bold', ha='center', va='center')
    data_text = """
    📊 1,225 conversation entries over 6 months
    🧠 40+ memory domains (personal, work, health, preferences)  
    🎯 85% AI confidence scores, 1.7 hybrid confidence ratings
    📈 Performance metrics: cache hit/miss, processing times
    🔄 Real-time behavioral tracking via browser extension
    """
    ax.text(10, 1.8, data_text, fontsize=10, ha='center', va='center', 
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))

    # Draw connections
    # Frontend to API
    conn1 = ConnectionPatch((2.5, 11.5), (4.5, 10.5), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5, 
                           mutation_scale=20, fc="black")
    ax.add_artist(conn1)
    
    # Chrome to API  
    conn2 = ConnectionPatch((7.5, 12), (6, 10.5), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5, 
                           mutation_scale=20, fc="black")
    ax.add_artist(conn2)

    # API to Services
    conn3 = ConnectionPatch((2, 9), (2, 8.3), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5, 
                           mutation_scale=20, fc="black")
    ax.add_artist(conn3)
    
    conn4 = ConnectionPatch((5.5, 9), (5.5, 8.3), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5, 
                           mutation_scale=20, fc="black")
    ax.add_artist(conn4)
    
    conn5 = ConnectionPatch((9, 9), (9, 8.3), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5, 
                           mutation_scale=20, fc="black")
    ax.add_artist(conn5)

    # Services to AI
    conn6 = ConnectionPatch((9, 7.4), (11, 11), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5, 
                           mutation_scale=20, fc="black")
    ax.add_artist(conn6)

    # AI to Memory
    conn7 = ConnectionPatch((15, 9), (15, 8.5), "data", "data",
                           arrowstyle="<->", shrinkA=5, shrinkB=5, 
                           mutation_scale=20, fc="blue")
    ax.add_artist(conn7)

    # Memory to Storage
    conn8 = ConnectionPatch((13, 6), (13, 5.3), "data", "data",
                           arrowstyle="<->", shrinkA=5, shrinkB=5, 
                           mutation_scale=20, fc="green")
    ax.add_artist(conn8)

    plt.tight_layout()
    return fig

# Generate and save the diagram
if __name__ == "__main__":
    fig = create_architecture_diagram()
    
    # Save as high-resolution PNG
    fig.savefig('/mnt/c/Tavant/Tavant/02_Paresh/Fun/digital-twin/digital_twin_architecture.png', 
                dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    
    # Save as SVG for scalability  
    fig.savefig('/mnt/c/Tavant/Tavant/02_Paresh/Fun/digital-twin/digital_twin_architecture.svg', 
                format='svg', bbox_inches='tight', facecolor='white', edgecolor='none')
    
    print("✅ Architecture diagram saved successfully!")
    print("📁 Files created:")
    print("  - digital_twin_architecture.png (High-res image)")
    print("  - digital_twin_architecture.svg (Scalable vector)")
    
    plt.show()