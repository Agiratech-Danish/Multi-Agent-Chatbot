# LangGraph Implementation Guide

## Overview

This project now uses **LangGraph** for multi-agent orchestration instead of manual if-else routing. LangGraph provides a structured, graph-based approach to managing complex agent workflows.

## Architecture

### What is LangGraph?

LangGraph is a framework by LangChain for building stateful, multi-agent systems using a graph-based approach:

- **Nodes**: Functions that process state
- **Edges**: Connections between nodes (can be conditional)
- **State**: TypedDict that flows through the graph
- **Graph**: Compiled workflow that executes the entire process

### Project Structure

```
app/agents/
├── state.py          # AgentState TypedDict definition
├── nodes.py          # Node functions (router, agents, memory)
├── graph.py          # LangGraph workflow builder
├── workflow_viz.py   # Visualization utilities
├── retrieval_agent.py
├── ocr_agent.py
├── data_agent.py
└── search_agent.py
```

## Key Components

### 1. State Schema (state.py)

```python
class AgentState(TypedDict):
    query: str
    session_id: str
    context: str
    agent_name: str
    response: str
    sources: List[dict]
    source_type: str
    knowledge_cutoff_detected: bool
    error: Optional[str]
```

**Purpose**: Defines the data structure that flows through the graph. Every node receives and returns this state.

### 2. Node Functions (nodes.py)

Each node is a function that:
- Takes `AgentState` as input
- Processes it
- Returns updated `AgentState`

**Example**:
```python
def router_node(state: AgentState) -> AgentState:
    """Route query to appropriate agent"""
    if "sql" in state["query"].lower():
        state["agent_name"] = "data_agent"
    return state
```

**Nodes in the workflow**:
- `router_node`: Classifies query type
- `retrieval_node`: RAG-based search
- `ocr_node`: Image processing
- `data_node`: SQL/Analytics
- `search_node`: Web search fallback
- `memory_node`: Store conversation history

### 3. Graph Builder (graph.py)

```python
def build_workflow():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("retrieval_agent", retrieval_node)
    # ... more nodes
    
    # Add edges
    workflow.add_edge("START", "router")
    workflow.add_conditional_edges(
        "router",
        lambda state: state["agent_name"],
        {
            "data_agent": "data_agent",
            "ocr_agent": "ocr_agent",
            "retrieval_agent": "retrieval_agent"
        }
    )
    
    return workflow.compile()
```

**Key concepts**:
- `add_node()`: Add a processing node
- `add_edge()`: Direct connection between nodes
- `add_conditional_edges()`: Route based on state
- `compile()`: Create executable workflow

### 4. Orchestration Service (orchestration_service.py)

```python
class OrchestrationService:
    def __init__(self):
        self.workflow = get_workflow()
    
    def process_query(self, query: str, session_id: str, **kwargs):
        state = {
            "query": query,
            "session_id": session_id,
            "context": "",
            # ... other fields
        }
        
        result = self.workflow.invoke(state)
        return result
```

## Workflow Execution Flow

```
User Query
    ↓
Initialize State
    ↓
workflow.invoke(state)
    ├─ ROUTER NODE
    │  └─ Classify query → Set agent_name
    │
    ├─ CONDITIONAL EDGE
    │  └─ Route to: DATA/OCR/RETRIEVAL
    │
    ├─ AGENT NODE (one of three)
    │  └─ Process query → Set response, sources
    │
    ├─ CONDITIONAL EDGE (if RETRIEVAL)
    │  └─ Check knowledge_cutoff_detected
    │     ├─ YES → SEARCH NODE
    │     └─ NO → MEMORY NODE
    │
    ├─ MEMORY NODE
    │  └─ Store messages in Redis/PostgreSQL
    │
    └─ END
        ↓
Return Result
```

## Interview Talking Points

### 1. Why LangGraph?

**Before (Manual Routing)**:
```python
if agent_name == "data_agent":
    result = self.data_agent.process(...)
elif agent_name == "ocr_agent":
    result = self.ocr_agent.process(...)
else:
    result = self.retrieval_agent.process(...)
```

**After (LangGraph)**:
- Declarative workflow definition
- Visual graph representation
- Built-in state management
- Easier to debug and extend
- Industry-standard approach

### 2. State Management

"We use TypedDict to define a strict schema for state. This ensures type safety and makes it clear what data flows through the system."

### 3. Conditional Routing

"LangGraph's conditional edges allow us to route based on state. For example, after retrieval, we check if knowledge cutoff was detected and route to search agent if needed."

### 4. Scalability

"Adding new agents is simple - just add a new node and edge. The graph structure makes it easy to understand the entire workflow at a glance."

### 5. Debugging

"We can visualize the entire workflow and trace execution through each node, making debugging much easier than nested if-else statements."

## Usage Examples

### Running the Workflow

```python
from app.services.orchestration_service import OrchestrationService

service = OrchestrationService()

result = service.process_query(
    query="Tell me about Danish Afroz",
    session_id="session-123"
)

print(result["response"])
print(result["agent"])  # Which agent processed it
print(result["source_type"])  # rag, direct_llm, web_search, etc.
```

### Visualizing the Workflow

```python
from app.agents.workflow_viz import print_workflow_structure

print_workflow_structure()
```

## Advantages Over Manual Routing

| Aspect | Manual | LangGraph |
|--------|--------|-----------|
| **Code Clarity** | Nested if-else | Declarative graph |
| **Debugging** | Hard to trace | Visual flow |
| **Scalability** | Add more if-else | Add node + edge |
| **State Management** | Manual passing | Automatic |
| **Type Safety** | Loose | Strict (TypedDict) |
| **Industry Standard** | Custom | Established pattern |

## Common Interview Questions

**Q: Why did you choose LangGraph over manual routing?**
A: "LangGraph provides a structured, declarative approach to multi-agent orchestration. It makes the workflow explicit, easier to debug, and follows industry standards."

**Q: How does state flow through the graph?**
A: "Each node receives the current state, processes it, and returns an updated state. This is passed to the next node automatically by LangGraph."

**Q: How do you handle conditional routing?**
A: "We use conditional_edges with a lambda function that examines the state and returns the next node name."

**Q: How would you add a new agent?**
A: "Add a new node function, add it to the graph with add_node(), and add edges to/from it. The state schema might need updating if the new agent requires new fields."

## Testing the Implementation

```bash
# Start the server
python -m uvicorn app.main:app --reload

# Test via API
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Danish Afroz",
    "session_id": "test-session"
  }'
```

## Files Modified/Created

**Created**:
- `app/agents/state.py` - State schema
- `app/agents/nodes.py` - Node functions
- `app/agents/graph.py` - Graph builder
- `app/agents/workflow_viz.py` - Visualization

**Modified**:
- `app/services/orchestration_service.py` - Now uses LangGraph

## Next Steps

1. Test the workflow with various queries
2. Add monitoring/logging to nodes
3. Implement node retry logic
4. Add performance metrics
5. Create advanced workflows with sub-graphs

---

**Version**: 1.0.0  
**Framework**: LangGraph 0.0.20  
**Last Updated**: 2024
