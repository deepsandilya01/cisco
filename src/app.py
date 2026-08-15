import streamlit as st
import pandas as st_pd
import pandas as pd
import json
import os
from datetime import datetime
from engine import diagnose_case, load_config

# Set up page config
st.set_page_config(page_title="NetSage AI Dashboard", layout="wide", page_icon="📡")

# Premium Web3.0 / Glassmorphism Custom CSS
st.markdown("""
<style>
    /* Base Theme & Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    :root {
        --primary-gradient: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        --cisco-dark: #0b1120;
        --card-bg: rgba(30, 41, 59, 0.6);
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
    }
    
    .stApp {
        background-color: var(--cisco-dark);
        background-image: radial-gradient(circle at 50% 0%, rgba(79, 172, 254, 0.1) 0%, transparent 50%);
        color: var(--text-main);
        font-family: 'Inter', system-ui, sans-serif;
    }

    /* Hide Streamlit elements */
    #MainMenu, footer {visibility: hidden;}
    header {background: transparent !important;}
    .block-container {
        padding-top: 1.5rem !important;
        max-width: 95% !important;
    }

    /* Beautiful Gradient Title */
    .gradient-title {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: var(--text-muted);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Glassmorphism Cards */
    .premium-card {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        margin-bottom: 20px;
        animation: fadeIn 0.5s ease-out forwards;
    }
    .premium-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 40px rgba(79, 172, 254, 0.15);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .card-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #4facfe;
        margin-bottom: 12px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .card-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    /* Terminal/Code block styling */
    .stCodeBlock {
        background: #000000 !important;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
    }
    .stCodeBlock code {
        color: #00ff00 !important; /* Hacker green terminal text */
        font-family: 'Consolas', 'Courier New', monospace;
    }

    /* Custom Streamlit Tabs */
    button[data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 1rem 2rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: white !important;
        border-bottom: 3px solid #4facfe !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        padding: 0.5rem 1rem !important;
    }
    .stButton>button[kind="primary"] {
        background: var(--primary-gradient) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3) !important;
    }
    .stButton>button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(79, 172, 254, 0.5) !important;
        transform: scale(1.02);
    }
    .stButton>button:hover {
        border-color: rgba(255,255,255,0.3) !important;
        background: rgba(255,255,255,0.05) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Warning Banner */
    .warning-banner {
        background: rgba(69, 26, 3, 0.6);
        backdrop-filter: blur(10px);
        color: #fde68a;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-left: 4px solid #f59e0b;
        margin-bottom: 24px;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('''
    <div class="warning-banner">
        <span style="font-size: 1.2rem;">⚠️</span>
        <div>
            <strong>CRITICAL NOTICE:</strong> NetSage AI is a decision-support & simulation engine. 
            <span style="opacity: 0.9;">NO commands are auto-executed against production equipment. All actions require manual network engineer verification.</span>
        </div>
    </div>
''', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_cases():
    cases_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cases.csv')
    return pd.read_csv(cases_path)

def log_decision(case_id, ai_root_cause, ai_confidence, decision, notes):
    log_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'model_audit_log.md')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Escape pipes for markdown table
    ai_root_cause = str(ai_root_cause).replace("|", "\\|").replace("\n", " ")
    notes = str(notes).replace("|", "\\|").replace("\n", " ")
    
    new_row = f"\n| {timestamp} | {case_id} | {ai_root_cause} | {ai_confidence:.2f} | {decision} | {notes} |"
    
    with open(log_path, 'a') as f:
        f.write(new_row)

try:
    cases_df = load_cases()
except FileNotFoundError:
    st.error("Could not find data/cases.csv. Please ensure it is created.")
    st.stop()

# Tabs
tab_diagnose, tab_dashboard = st.tabs(["🔍 Case Diagnosis", "📊 Dashboard Summary"])

with tab_diagnose:
    st.markdown('''
        <div class="gradient-title">NetSage AI</div>
        <div class="subtitle">Next-Generation Network Diagnostics Engine</div>
    ''', unsafe_allow_html=True)
    
    # Sidebar selection
    st.sidebar.markdown('''
        <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 20px; background: -webkit-linear-gradient(#00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Control Panel
        </div>
    ''', unsafe_allow_html=True)
    
    case_options = cases_df['case_id'] + " - " + cases_df['symptom']
    selected_option = st.sidebar.selectbox("Choose a case to analyze:", case_options)
    
    selected_case_id = selected_option.split(" - ")[0]
    case_data = cases_df[cases_df['case_id'] == selected_case_id].iloc[0]

    # Display case details in premium cards
    col1, col2 = st.columns([1, 1.4], gap="large")
    
    with col1:
        st.markdown(f'''
        <div class="premium-card">
            <div class="card-title">🔍 Scenario Context</div>
            <div style="margin-bottom: 20px; margin-top: 15px;">
                <span style="color: var(--text-muted); font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase;">Ticket ID</span><br>
                <strong style="font-size: 1.2rem; color: #fff;">{case_data['case_id']}</strong>
            </div>
            <div style="margin-bottom: 20px;">
                <span style="color: var(--text-muted); font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase;">Reported Symptom</span><br>
                <span style="color: white; font-size: 1.1rem; display: block; margin-top: 5px;">{case_data['symptom']}</span>
            </div>
            <div style="margin-bottom: 20px;">
                <span style="color: var(--text-muted); font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase;">Topology Details</span><br>
                <span style="color: #cbd5e1; display: block; margin-top: 5px; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">{case_data['topology_note']}</span>
            </div>
            <div style="display: flex; gap: 15px; margin-top: 25px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px;">
                <div>
                    <span style="color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; display: block; margin-bottom: 5px;">TAG</span>
                    <span style="background: rgba(79, 172, 254, 0.15); color: #4facfe; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(79, 172, 254, 0.3);">{case_data['concept_tag']}</span>
                </div>
                <div>
                    <span style="color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; display: block; margin-bottom: 5px;">SEVERITY</span>
                    <span style="background: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(239, 68, 68, 0.3);">{case_data['severity']}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="card-title" style="margin-bottom: 12px;">🖥️ Router/Switch Console Output</div>', unsafe_allow_html=True)
        st.code(case_data['show_outputs'], language="text")

    st.divider()
    
    if st.button("Run Diagnosis", type="primary"):
        with st.spinner("Analyzing output..."):
            diagnosis = diagnose_case(selected_case_id, case_data.to_dict())
            st.session_state['current_diagnosis'] = diagnosis
            st.session_state['current_case_id'] = selected_case_id

    # Display Diagnosis Results if available
    if 'current_diagnosis' in st.session_state and st.session_state.get('current_case_id') == selected_case_id:
        st.markdown('''
            <div style="display: flex; align-items: center; gap: 15px; margin-top: 30px; margin-bottom: 20px;">
                <div style="height: 1px; flex-grow: 1; background: linear-gradient(to right, transparent, rgba(79, 172, 254, 0.5));"></div>
                <h3 style="margin: 0; color: #4facfe;">🧠 AI Diagnostic Insights</h3>
                <div style="height: 1px; flex-grow: 1; background: linear-gradient(to left, transparent, rgba(79, 172, 254, 0.5));"></div>
            </div>
        ''', unsafe_allow_html=True)
        diag = st.session_state['current_diagnosis']
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'''
            <div class="premium-card" style="text-align: center; border-bottom: 4px solid #4facfe;">
                <div class="card-title" style="justify-content: center;">OSI Layer Impact</div>
                <div class="card-value" style="color: #4facfe;">{diag.get("osi_layer", "Unknown")}</div>
            </div>
            ''', unsafe_allow_html=True)
        with c2:
            st.markdown(f'''
            <div class="premium-card" style="text-align: center; border-bottom: 4px solid #10b981;">
                <div class="card-title" style="justify-content: center;">Detection Engine</div>
                <div class="card-value" style="color: #10b981; font-size: 1.5rem; margin-top: 8px;">{diag.get("source", "Unknown")}</div>
            </div>
            ''', unsafe_allow_html=True)
        with c3:
            conf = float(diag.get("confidence", 0.0))
            st.markdown(f'''
            <div class="premium-card" style="text-align: center; border-bottom: 4px solid #f59e0b;">
                <div class="card-title" style="justify-content: center;">Confidence Score</div>
                <div class="card-value" style="color: #f59e0b;">{conf * 100:.1f}%</div>
            </div>
            ''', unsafe_allow_html=True)
            
        st.markdown(f'''
        <div class="premium-card" style="border-left: 4px solid #4facfe; background: linear-gradient(90deg, rgba(79, 172, 254, 0.05) 0%, rgba(30, 41, 59, 0.6) 100%);">
            <h4 style="color: white; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
                🎯 Identified Root Cause
            </h4>
            <p style="font-size: 1.15rem; color: #f8fafc; line-height: 1.6;">{diag.get('root_cause')}</p>
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px dashed rgba(255,255,255,0.2);">
                <span style="color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">Supporting Evidence:</span><br>
                <div style="font-family: 'Consolas', monospace; color: #a5b4fc; background: rgba(0,0,0,0.4); padding: 10px; border-radius: 8px; margin-top: 8px; border: 1px solid rgba(255,255,255,0.05); border-left: 2px solid #a5b4fc;">
                    {diag.get('evidence')}
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        col_cmds, col_verify = st.columns([2, 1])
        
        with col_cmds:
            st.markdown("#### 🛠️ Proposed Remediation Steps")
            fix_steps = diag.get("fix_steps", [])
            if fix_steps:
                steps_code = "\n".join(fix_steps)
                st.code(steps_code, language="bash")
            else:
                st.info("No specific fix steps provided.")
                
        with col_verify:
            if diag.get("next_command"):
                st.markdown("#### ✅ Post-Fix Verification")
                st.info(f"Run this command to verify the fix:\n\n`{diag.get('next_command')}`")

        st.markdown('''
            <div style="height: 1px; width: 100%; background: rgba(255,255,255,0.1); margin: 30px 0;"></div>
            <h3 style="color: white; margin-bottom: 20px;">🛡️ Human Review & Approval</h3>
        ''', unsafe_allow_html=True)
        
        notes = st.text_area("Reviewer Notes (Optional)", help="Add your reasoning for approval, edits, or rejection.")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("✅ Approve & Deploy (Log Only)", key="btn_approve", use_container_width=True):
                log_decision(selected_case_id, diag.get('root_cause'), diag.get('confidence', 0), "Approved", notes or "Approved as suggested.")
                st.success("Decision logged: Approved!")
                
        with col_btn2:
            with st.popover("📝 Edit Commands & Approve"):
                edited_steps = st.text_area("Edit Fix Steps (one per line)", value="\\n".join(fix_steps), height=150)
                if st.button("Save Edits & Log Approval"):
                    log_decision(selected_case_id, diag.get('root_cause'), diag.get('confidence', 0), "Edited", f"Edited steps. Notes: {notes}")
                    st.success("Decision logged: Edited & Approved!")
                    
        with col_btn3:
            if st.button("❌ Reject", key="btn_reject", use_container_width=True):
                 if not notes:
                     st.warning("Please provide notes when rejecting.")
                 else:
                     log_decision(selected_case_id, diag.get('root_cause'), diag.get('confidence', 0), "Rejected", notes)
                     st.error("Decision logged: Rejected.")


with tab_dashboard:
    st.title("NetSage AI - Dashboard Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cases by Concept")
        concept_counts = cases_df['concept_tag'].value_counts()
        st.bar_chart(concept_counts)
        
    with col2:
        st.subheader("Cases by Severity")
        severity_counts = cases_df['severity'].value_counts()
        st.bar_chart(severity_counts)
        
    st.divider()
    
    st.subheader("AI vs Human Agreement Rate")
    
    # Parse the markdown log to calculate stats
    log_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'model_audit_log.md')
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            
        # Very basic markdown table parsing
        decisions = []
        for line in lines:
            if "|" in line and "---" not in line and "Timestamp" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 6:
                    decisions.append(parts[5]) # Index 5 is Human Decision column
                    
        if decisions:
            df_decisions = pd.DataFrame(decisions, columns=['Decision'])
            counts = df_decisions['Decision'].value_counts()
            
            total = len(decisions)
            approved = counts.get('Approved', 0)
            edited = counts.get('Edited', 0)
            rejected = counts.get('Rejected', 0)
            
            st.write(f"**Total Decisions Logged:** {total}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Approved (No Edits)", f"{approved}", f"{(approved/total)*100:.1f}%")
            c2.metric("Edited", f"{edited}", f"{(edited/total)*100:.1f}%")
            c3.metric("Rejected", f"{rejected}", f"{(rejected/total)*100:.1f}%")
            
            st.bar_chart(counts)
            
        else:
            st.info("No decisions logged yet.")
            
    except Exception as e:
        st.error(f"Could not load audit log for stats: {e}")
