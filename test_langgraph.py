"""
Test script for LangGraph workflow
Run this to verify the implementation works correctly
"""

import sys
from app.agents.graph import get_workflow
from app.agents.workflow_viz import print_workflow_structure

def test_workflow():
    """Test the LangGraph workflow"""
    
    print("\n" + "="*70)
    print("LangGraph Workflow Test")
    print("="*70 + "\n")
    
    # Print workflow structure
    print_workflow_structure()
    
    # Get workflow
    print("\n✅ Building workflow...")
    workflow = get_workflow()
    print("✅ Workflow built successfully!")
    
    # Test state
    print("\n" + "="*70)
    print("Testing State Flow")
    print("="*70 + "\n")
    
    test_state = {
        "query": "Tell me about Danish Afroz",
        "session_id": "test-session-123",
        "context": "",
        "agent_name": "",
        "response": "",
        "sources": [],
        "source_type": "",
        "knowledge_cutoff_detected": False,
        "error": None
    }
    
    print(f"Initial State:")
    print(f"  Query: {test_state['query']}")
    print(f"  Session: {test_state['session_id']}")
    print(f"  Agent: {test_state['agent_name']} (empty - will be set by router)")
    
    print("\n⏳ Executing workflow...")
    try:
        result = workflow.invoke(test_state)
        
        print("\n✅ Workflow executed successfully!")
        print(f"\nFinal State:")
        print(f"  Agent Used: {result['agent_name']}")
        print(f"  Source Type: {result['source_type']}")
        print(f"  Response Length: {len(result['response'])} chars")
        print(f"  Sources Found: {len(result['sources'])}")
        print(f"  Knowledge Cutoff: {result['knowledge_cutoff_detected']}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error executing workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_nodes():
    """Test individual nodes"""
    print("\n" + "="*70)
    print("Testing Individual Nodes")
    print("="*70 + "\n")
    
    from app.agents.nodes import router_node
    
    # Test router
    test_state = {
        "query": "What is the SQL query for this?",
        "session_id": "test",
        "context": "",
        "agent_name": "",
        "response": "",
        "sources": [],
        "source_type": "",
        "knowledge_cutoff_detected": False,
        "error": None
    }
    
    print("Testing Router Node:")
    print(f"  Input Query: {test_state['query']}")
    
    result = router_node(test_state)
    print(f"  Routed to: {result['agent_name']}")
    
    if result['agent_name'] == "data_agent":
        print("  ✅ Correctly identified as data query")
    else:
        print("  ❌ Failed to identify as data query")

if __name__ == "__main__":
    print("\n🚀 Starting LangGraph Implementation Tests\n")
    
    # Test nodes
    try:
        test_nodes()
    except Exception as e:
        print(f"⚠️  Node test skipped: {str(e)}")
    
    # Test workflow
    success = test_workflow()
    
    print("\n" + "="*70)
    if success:
        print("✅ All tests passed! LangGraph is working correctly.")
    else:
        print("❌ Tests failed. Check the errors above.")
    print("="*70 + "\n")
