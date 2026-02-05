"""
FixIt.AI - Streamlit Web Interface
Machinery repair assistant with RAG
"""
import streamlit as st
import requests
import time

# Page configuration
st.set_page_config(
    page_title="FixIt.AI - Machinery Repair Assistant",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoint
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .citation-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔧 FixIt.AI</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; margin-bottom: 2rem;">Machinery Repair Assistant powered by AI</p>', unsafe_allow_html=True)

# Sidebar - System Stats
with st.sidebar:
    st.header("📊 System Information")
    
    try:
        stats_response = requests.get(f"{API_URL}/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", stats.get("total_vectors", "N/A"))
            with col2:
                st.metric("Dimensions", stats.get("vector_dimension", "N/A"))
            
            st.success("✅ Backend Online")
        else:
            st.error("❌ Backend Error")
    except requests.exceptions.RequestException:
        st.error("❌ Backend Offline")
        st.info("Make sure the backend is running:\n```\ncd backend\nuvicorn app.main:app\n```")
    
    st.divider()
    
    st.header("📝 Example Questions")
    example_questions = [
        "How do I replace the brake pads?",
        "What are the torque specifications for the wheel bolts?",
        "How do I check the oil level?",
        "What is the tire pressure specification?",
        "How do I replace the air filter?"
    ]
    
    selected_example = st.selectbox(
        "Choose an example:",
        [""] + example_questions,
        label_visibility="collapsed"
    )
    
    if selected_example and st.button("Use This Question", use_container_width=True):
        st.session_state.query_text = selected_example

# Initialize session state
if 'query_text' not in st.session_state:
    st.session_state.query_text = ""
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Main query interface
st.subheader("💬 Ask a Question")

query = st.text_area(
    "Enter your question about machinery repair:",
    value=st.session_state.query_text,
    placeholder="Example: How do I replace the brake pads?",
    height=100,
    key="query_input"
)

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    submit_button = st.button("🔍 Ask Question", type="primary", use_container_width=True)
with col2:
    top_k = st.number_input("Results", min_value=1, max_value=10, value=3, label_visibility="collapsed")
with col3:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

if clear_button:
    st.session_state.query_text = ""
    st.rerun()

# Process query
if submit_button and query.strip():
    st.info("⏳ Query processing... First query may take 10-15s (model loading). Subsequent queries will be faster.")
    start_time = time.time()
    
    with st.spinner("🔍 Searching knowledge base..."):
        try:
            response = requests.post(
                f"{API_URL}/query/text",
                json={"query": query, "top_k": top_k},
                timeout=60  # Increased timeout for longer queries
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    # Add to history
                    st.session_state.query_history.insert(0, {
                        "query": query,
                        "answer": result["answer"],
                        "citations": result["citations"],
                        "time": elapsed_time
                    })
                    
                    # Display answer
                    st.success(f"✅ Answer generated in {elapsed_time:.2f}s")
                    
                    st.subheader("📖 Answer")
                    st.markdown(result["answer"])
                    
                    # Display citations
                    st.subheader("📚 Sources")
                    st.caption(f"Retrieved {result.get('context_used', 0)} relevant sections")
                    
                    for i, citation in enumerate(result.get("citations", []), 1):
                        with st.container():
                            st.markdown(f"""
                            <div class="citation-box">
                                <strong>📄 Source {i}</strong><br>
                                Page: <code>{citation['page']}</code> | 
                                File: <code>{citation['file']}</code> | 
                                Relevance: <strong>{citation['score']:.2%}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Copy button
                    st.divider()
                    if st.button("📋 Copy Answer to Clipboard"):
                        st.code(result["answer"], language=None)
                        st.info("Answer displayed above - copy manually")
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
            else:
                st.error(f"❌ HTTP Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The query is taking too long.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend. Make sure it's running on port 8000.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

elif submit_button:
    st.warning("⚠️ Please enter a question first")

# Query history
if st.session_state.query_history:
    st.divider()
    st.subheader("📜 Query History")
    
    for i, item in enumerate(st.session_state.query_history[:5], 1):
        with st.expander(f"Query {i}: {item['query'][:50]}..."):
            st.markdown(f"**Question:** {item['query']}")
            st.markdown(f"**Answer:** {item['answer'][:200]}...")
            st.caption(f"Response time: {item['time']:.2f}s | Sources: {len(item['citations'])}")

# Footer
st.divider()
st.caption("FixIt.AI v1.0 | Powered by Gemini 3.0 Flash & RAG")
