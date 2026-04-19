import streamlit as st
import networkx as nx
import re
import os
import base64
import time

def initialize_session_state():
    if 'graph' not in st.session_state:
        st.session_state.graph = nx.DiGraph()
    if 'papers' not in st.session_state:
        st.session_state.papers = {}
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None
    if 'criteria' not in st.session_state:
        st.session_state.criteria = {}
    if 'batch_criteria' not in st.session_state:
        st.session_state.batch_criteria = {}
    if 'screening_results' not in st.session_state:
        st.session_state.screening_results = {}
    if 'main_paper' not in st.session_state:
        st.session_state.main_paper = None
    if 'criteria_set' not in st.session_state:
        st.session_state.criteria_set = False
    if 'snowballed_papers' not in st.session_state:
        st.session_state.snowballed_papers = set()
    if 'failed_dois' not in st.session_state:
        st.session_state.failed_dois = set()
    if 'hf_api_key' not in st.session_state:
        st.session_state.hf_api_key = ""
    if 'hf_model' not in st.session_state:
        st.session_state.hf_model = "facebook/bart-large-mnli"
    if 'criteria_framework' not in st.session_state:
        st.session_state.criteria_framework = "Manual"

def get_image_as_base64(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        else:
            return ""
    except Exception as e:
        return ""

def extract_doi(text):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    match = re.search(doi_pattern, text, re.IGNORECASE)
    return match.group(0) if match else None

def clean_doi(doi):
    doi = re.sub(r'^https?://doi\.org/', '', doi)
    doi = re.sub(r'^doi:', '', doi, flags=re.IGNORECASE)
    doi = doi.strip()
    return doi

def detailed_progress_bar(current, total, start_time, status_text):
    progress = current / total if total > 0 else 0
    elapsed_time = time.time() - start_time
    
    if current > 0:
        avg_time_per_item = elapsed_time / current
        remaining_items = total - current
        estimated_remaining = avg_time_per_item * remaining_items
    else:
        estimated_remaining = 0
    
    elapsed_str = f"{elapsed_time:.1f}s"
    remaining_str = f"{estimated_remaining:.1f}s" if estimated_remaining > 0 else "Calculating..."
    
    st.markdown(f"""
    <div class="progress-details">
        <div class="progress-text">Processing: {current}/{total} papers</div>
        <div class="progress-text">Elapsed: {elapsed_str} | Remaining: {remaining_str}</div>
    </div>
    """, unsafe_allow_html=True)
    
    progress_bar = st.progress(progress)
    status_text.text(f"Processing paper {current}/{total}")
    
    return progress_bar