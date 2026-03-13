import streamlit as st
import requests
import json
from datetime import datetime
import os
import sys

# Page config
st.set_page_config(page_title="Multi-Agent Chatbot", layout="wide")

# API base URL - Dynamic from environment or command line
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

# Initialize session state
if "session_id" not in st.session_state:
    try:
        print(f"Attempting to connect to {API_URL}/chat/session/new")
        response = requests.post(f"{API_URL}/chat/session/new", timeout=10)
        print(f"Response status: {response.status_code}")
        st.session_state.session_id = response.json()["session_id"]
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ Cannot connect to backend at {API_URL}")
        st.error(f"Details: {str(e)}")
        st.info("Make sure backend is running: python app/main.py")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Document Management
    st.subheader("📄 Document Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Upload Document", use_container_width=True):
            st.session_state.show_upload = True
    
    with col2:
        if st.button("🗑️ Clear FAISS", use_container_width=True, help="Delete all embeddings and OCR data"):
            try:
                response = requests.delete(f"{API_URL}/documents/faiss/clear-all")
                if response.status_code == 200:
                    st.success("✅ FAISS data cleared successfully!")
                    st.session_state.messages = []
                else:
                    st.error("❌ Failed to clear FAISS data")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Document Upload
    if st.session_state.get("show_upload", False):
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "md", "png", "jpg", "jpeg", "bmp"]
        )
        
        if uploaded_file is not None:
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getbuffer())}
                response = requests.post(f"{API_URL}/documents/upload", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ {data['filename']} uploaded successfully!")
                    st.info(f"📊 Extracted text length: {data.get('extracted_text_length', 'N/A')} chars")
                    st.session_state.show_upload = False
                else:
                    st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Session Info
    st.subheader("📋 Session Info")
    st.text(f"Session ID: {st.session_state.session_id[:8]}...")
    st.text(f"Messages: {len(st.session_state.messages)}")
    
    if st.button("🔄 New Session", use_container_width=True):
        response = requests.post(f"{API_URL}/chat/session/new")
        st.session_state.session_id = response.json()["session_id"]
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("🤖 Multi-Agent AI Chatbot")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "metadata" in message:
            with st.expander("📊 Details"):
                st.json(message["metadata"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get streaming response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Use streaming endpoint
            import requests
            response = requests.post(
                f"{API_URL}/chat/message/stream",
                json={
                    "message": prompt,
                    "session_id": st.session_state.session_id
                },
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'chunk' in data:
                                    full_response += data['chunk']
                                    message_placeholder.markdown(full_response + "▌")
                            except:
                                pass
                
                # Final response without cursor
                message_placeholder.markdown(full_response)
                
                # Store message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })
            else:
                st.error(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")

# Footer
st.divider()
st.caption("🚀 Enterprise Multi-Agent AI Knowledge Copilot | Powered by LangGraph")
