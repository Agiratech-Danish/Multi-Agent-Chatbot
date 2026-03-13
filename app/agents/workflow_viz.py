"""
LangGraph Workflow Visualization

This module provides utilities to visualize and understand the LangGraph workflow.
"""

def print_workflow_structure():
    """Print the workflow structure"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║           LangGraph Multi-Agent Workflow                       ║
    ╚════════════════════════════════════════════════════════════════╝
    
    START
      │
      ▼
    ┌─────────────────────────────────────┐
    │  ROUTER NODE                        │
    │  (Classify query type)              │
    └─────────────────────────────────────┘
      │
      ├─────────────────┬──────────────┬──────────────┐
      │                 │              │              │
      ▼                 ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────────┐
    │ DATA     │  │ OCR      │  │ RETRIEVAL    │
    │ AGENT    │  │ AGENT    │  │ AGENT        │
    └──────────┘  └──────────┘  └──────────────┘
      │                 │              │
      │                 │              ▼
      │                 │         ┌──────────────────┐
      │                 │         │ Knowledge Cutoff?│
      │                 │         └──────────────────┘
      │                 │              │
      │                 │         ┌────┴────┐
      │                 │         │          │
      │                 │        YES        NO
      │                 │         │          │
      │                 │         ▼          │
      │                 │    ┌─────────┐    │
      │                 │    │ SEARCH  │    │
      │                 │    │ AGENT   │    │
      │                 │    └─────────┘    │
      │                 │         │          │
      └─────────────────┴─────────┴──────────┘
                        │
                        ▼
                  ┌──────────────┐
                  │ MEMORY NODE  │
                  │ (Store msgs) │
                  └──────────────┘
                        │
                        ▼
                       END
    
    ═══════════════════════════════════════════════════════════════
    
    NODES:
    ─────
    1. ROUTER: Classifies query and routes to appropriate agent
    2. DATA AGENT: Handles SQL/Analytics queries
    3. OCR AGENT: Handles image/text extraction
    4. RETRIEVAL AGENT: Handles RAG-based queries
    5. SEARCH AGENT: Fallback for knowledge cutoff
    6. MEMORY: Stores conversation history
    
    EDGES:
    ─────
    • START → ROUTER (always)
    • ROUTER → DATA/OCR/RETRIEVAL (conditional based on query)
    • RETRIEVAL → SEARCH/MEMORY (conditional based on knowledge cutoff)
    • DATA/OCR/SEARCH → MEMORY (always)
    • MEMORY → END (always)
    
    ═══════════════════════════════════════════════════════════════
    """)

def get_workflow_info():
    """Get workflow information for debugging"""
    from app.agents.graph import get_workflow
    
    workflow = get_workflow()
    
    info = {
        "nodes": list(workflow.nodes.keys()) if hasattr(workflow, 'nodes') else [],
        "edges": list(workflow.edges) if hasattr(workflow, 'edges') else [],
        "description": "LangGraph-based multi-agent orchestration system"
    }
    
    return info

if __name__ == "__main__":
    print_workflow_structure()
    print("\nWorkflow Info:")
    print(get_workflow_info())
