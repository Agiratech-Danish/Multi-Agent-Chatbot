import streamlit as st
import requests
import json
import os

# API base URL - Dynamic from environment or defaults to localhost
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Knowledge Copilot", page_icon="🤖", layout="wide")

st.title("🤖 Enterprise Multi-Agent AI Knowledge Copilot")

# Initialize session state
if "session_id" not in st.session_state:
    try:
        response = requests.post(f"{API_URL}/api/chat/session/new", timeout=5)
        if response.status_code == 200:
            st.session_state.session_id = response.json()["session_id"]
            st.session_state.messages = []
        else:
            st.error(f"❌ Backend error. Check if FastAPI is running on {API_URL}")
            st.stop()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {API_URL}. Please start FastAPI first: `python app/main.py`")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Document Upload
    st.subheader("📄 Upload Documents")
    uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf", "md"])
    if uploaded_file and st.button("Upload"):
        with st.spinner("📤 Uploading document..."):
            try:
                files = {"file": uploaded_file}
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("⏳ Uploading file...")
                progress_bar.progress(30)
                
                response = requests.post(f"{API_URL}/api/documents/upload", files=files)
                
                status_text.text("⚙️ Processing document...")
                progress_bar.progress(70)
                
                if response.status_code == 200:
                    progress_bar.progress(100)
                    status_text.text("✅ Upload complete!")
                    st.success(f"✅ Document '{uploaded_file.name}' uploaded successfully!")
                    st.balloons()
                else:
                    st.error(f"❌ Upload failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Agent Info
    st.subheader("🤖 Available Agents")
    st.info("**Retrieval Agent**: General knowledge queries")
    st.info("**OCR Agent**: Image text extraction")
    st.info("**Data Agent**: SQL & Analytics")
    
    # New Session
    if st.button("🔄 New Session"):
        response = requests.post(f"{API_URL}/api/chat/session/new")
        st.session_state.session_id = response.json()["session_id"]
        st.session_state.messages = []
        st.rerun()

# Chat Interface
st.subheader("💬 Chat")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show Agent and Source
        if "agent" in message and "source_info" in message:
            source_display = "📄 Uploaded Documents (RAG)" if message["source_info"]["type"] == "rag" else "🤖 Direct LLM"
            st.caption(f"🤖 Agent: {message['agent']} | 📍 Source: {source_display}")
        elif "agent" in message:
            st.caption(f"🤖 Agent: {message['agent']}")

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = {
                "message": prompt,
                "session_id": st.session_state.session_id
            }
            response = requests.post(f"{API_URL}/api/chat/message", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                st.markdown(data["response"])
                
                # Show source type
                source_type = data.get("source_type", "unknown")
                note = data.get("note", "")
                
                # Display Agent and Source inline
                if source_type == "rag":
                    source_display = "📄 Uploaded Documents (RAG)"
                    st.success(note)
                elif source_type == "direct_llm":
                    source_display = "🤖 Direct LLM"
                    st.warning(note)
                else:
                    source_display = "Unknown"
                
                st.caption(f"🤖 Agent: {data['agent_used']} | 📍 Source: {source_display}")
                
                # Show sources if available
                if data.get("sources"):
                    with st.expander("📚 View Document Sources"):
                        for i, source in enumerate(data["sources"][:3], 1):
                            st.markdown(f"**Source {i}:**")
                            st.text(source.get("content", "")[:200] + "...")
                            st.caption(f"Relevance Score: {source.get('score', 0):.2f}")
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["response"],
                    "agent": data["agent_used"],
                    "source_info": {"type": source_type, "note": note}
                })
            else:
                st.error("Error getting response")
