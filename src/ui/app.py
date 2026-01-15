import streamlit as st
import os
import sys

# Add project root to sys.path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.rag.engine import SARREngine

# Set page config
st.set_page_config(
    page_title="AML SAR Assistant",
    page_icon="🕵️‍♂️",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #475569;
    }
    .evidence-box {
        background-color: #F1F5F9;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #E2E8F0;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .sar-box {
        background-color: #FEF2F2; /* Light red/alert tint for SAR */
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #DC2626;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for Configuration
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=50) 
    st.title("Settings")
    
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Dynamic Model Selection
    default_models = ["gpt-4o", "gpt-3.5-turbo", "claude-3-5-sonnet-20240620"]
    local_models = []
    
    try:
        import ollama
        # Try to fetch available local models
        models_info = ollama.list()
        # Handle different response formats (object or dict)
        if isinstance(models_info, dict) and 'models' in models_info:
            local_models = [f"ollama/{m['name']}" for m in models_info['models']]
        elif hasattr(models_info, 'models'):
             local_models = [f"ollama/{m.model}" for m in models_info.models]
    except Exception as e:
        # Ollama might not be running or installed
        pass

    if not local_models:
        local_models = ["ollama/mistral (not found - pull first)", "ollama/llama3 (not found - pull first)"]
        
    model_choice = st.selectbox("Model", default_models + local_models)
    
    # Handle selection
    if "ollama" in model_choice:
        real_model_name = model_choice.replace("ollama/", "").split(" ")[0]
        os.environ["MODEL_NAME"] = f"ollama/{real_model_name}"
        
        st.info(f"Using Local Model: {real_model_name}")
        
        # Check if actually reachable
        try:
            import requests
            if requests.get("http://localhost:11434").status_code == 200:
                st.success("🟢 Ollama Service is Running")
                if "not found" in model_choice:
                    st.error(f"⚠️ Model '{real_model_name}' not found. Run in terminal: `ollama pull {real_model_name}`")
            else:
                st.error("🔴 Ollama Service not reachable at localhost:11434")
        except:
             st.error("🔴 Ollama Service not detected")
    else:
        os.environ["MODEL_NAME"] = model_choice
    
    st.divider()
    st.info("Ensure ingestion is run before generating reports.")
    if st.button("Re-run Ingestion"):
        with st.spinner("Ingesting data... (this uses local embeddings)"):
            try:
                # Run the indexer script
                import subprocess
                result = subprocess.run(["python", "src/ingestion/indexer.py"], capture_output=True, text=True, cwd=os.getcwd())
                if result.returncode == 0:
                    st.success("Ingestion complete!")
                else:
                    st.error(f"Ingestion failed:\n{result.stderr}")
            except Exception as e:
                st.error(f"Error running ingestion: {e}")

# Main Content
st.markdown('<div class="main-header">🕵️‍♂️ AML SAR Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Suspicious Activity Report Generation via RAG</div>', unsafe_allow_html=True)
st.markdown("---")

# Input Section
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Case Details")
    customer_id = st.text_input("Customer ID", value="C001", help="Enter the ID of the customer under investigation (e.g., C001, C002)")
    
    generate_btn = st.button("Generate SAR Draft", type="primary", use_container_width=True)

# Application Logic
@st.cache_resource
def get_engine():
    # Only load if DB exists
    db_path = os.path.join(os.getcwd(), "chroma_db")
    if not os.path.exists(db_path):
        return None
    return SARREngine(db_path=db_path)

if generate_btn:
    if not os.environ.get("OPENAI_API_KEY") and "gpt" in model_choice:
        st.warning("Please enter an OpenAI API Key in the sidebar to proceed.")
    else:
        engine = get_engine()
        if not engine:
            st.error("Database not found. Please run ingestion first using the sidebar button.")
        else:
            with st.spinner(f"Analyzing Evidence for {customer_id} & Drafting Report..."):
                try:
                    result = engine.generate_sar(customer_id)
                    
                    if isinstance(result, str) and result.startswith("Error"):
                        st.error(result)
                    else:
                        # Success
                        draft = result.get("draft")
                        evidence = result.get("evidence")
                        
                        # Layout results
                        st.subheader("📝 Generated SAR Draft")
                        st.markdown(f'<div class="sar-box">{draft}</div>', unsafe_allow_html=True)
                        
                        with st.expander("🔎 View Retrieved Evidence (Anonymized)"):
                            st.markdown(f'<div class="evidence-box">{evidence}</div>', unsafe_allow_html=True)
                            
                        # Download button
                        st.download_button(
                            label="Download Report",
                            data=draft,
                            file_name=f"SAR_{customer_id}.txt",
                            mime="text/plain"
                        )
                        
                except Exception as e:
                    st.error(f"An error occurred: {e}")

