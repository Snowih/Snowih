import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import re
from datetime import datetime
import json

from utils import get_image_as_base64, detailed_progress_bar, clean_doi
from core import add_paper_to_graph, snowball_paper
from visualizations import (
    create_network_graph, export_graph_data, create_csv_export, 
    create_png_image, create_pdf, generate_gexf, generate_graphml
)

def render_header():
    logo_base64 = get_image_as_base64("assets/snowih_logo.png")
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-content">
            <div class="header-logo">
                <img src="data:image/png;base64,{logo_base64}" class="logo" alt="Snowih Logo">
            </div>
            <div class="header-text">
                <h1 class="main-header">Snowih</h1>
                <p class="header-subtitle">AI-Powered Backward Snowballing for Reproducible Literature Searches.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_ai_settings():
    st.markdown("## Set AI model")
    st.info("To use AI screening, please enter your HuggingFace API Token.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_key = st.text_input(
            "HuggingFace API Token", 
            type="password", 
            value=st.session_state.hf_api_key,
            key="hf_api_key_input_ui"
        )
        st.session_state.hf_api_key = api_key

    with col2:
        model_name = st.text_input(
            "AI Model Name", 
            value=st.session_state.hf_model, 
            placeholder="facebook/bart-large-mnli",
            key="hf_model_input_ui"
        )
        st.session_state.hf_model = model_name

def get_criteria_inputs(prefix=""):
    """Helper to get criteria inputs based on selected framework"""
    framework = st.session_state.get(f'{prefix}framework', 'Manual')
    criteria = {'framework': framework}
    
    col1, col2 = st.columns(2)
    
    with col1:
        if framework == "Manual":
            keywords = st.text_input(
                "Research Keywords (comma separated):",
                placeholder="e.g., machine learning, healthcare, diagnosis",
                key=f"{prefix}keywords"
            )
            criteria['keywords'] = keywords
            
            study_type = st.selectbox(
                "Study Type:",
                ["Any", "Experimental", "Review", "Case Study", "Observational", "Simulation"],
                key=f"{prefix}study_type"
            )
            criteria['study_type'] = study_type
            
        elif framework == "PICO":
            st.markdown("### PICO Framework")
            population = st.text_input(
                "Population (P):",
                placeholder="e.g., elderly patients",
                key=f"{prefix}pico_population"
            )
            criteria['pico_population'] = population
            
            intervention = st.text_input(
                "Intervention (I):",
                placeholder="e.g., aspirin",
                key=f"{prefix}pico_intervention"
            )
            criteria['pico_intervention'] = intervention

    with col2:
        from_year = st.number_input(
            "From Year:",
            min_value=1900,
            max_value=2030,
            value=2010,
            key=f"{prefix}from_year"
        )
        criteria['from_year'] = from_year
        
        to_year = st.number_input(
            "To Year:",
            min_value=1900,
            max_value=2030,
            value=2023,
            key=f"{prefix}to_year"
        )
        criteria['to_year'] = to_year
        
        if framework == "PICO":
            comparison = st.text_input(
                "Comparison (C):",
                placeholder="e.g., placebo",
                key=f"{prefix}pico_comparison"
            )
            criteria['pico_comparison'] = comparison
            
            outcome = st.text_input(
                "Outcome (O):",
                placeholder="e.g., stroke incidence",
                key=f"{prefix}pico_outcome"
            )
            criteria['pico_outcome'] = outcome
            
    return criteria

def render_criteria_panel():
    st.markdown("<div class='criteria-panel'>", unsafe_allow_html=True)
    st.markdown("## Set Screening Criteria")
    
    framework = st.radio(
        "Select Framework:",
        ["Manual", "PICO"],
        horizontal=True,
        key="criteria_framework_select"
    )
    st.session_state.criteria_framework = framework
    
    criteria = get_criteria_inputs(prefix="criteria_")

    if st.button("Set Criteria", key="set_criteria_btn"):
        st.session_state.criteria = criteria
        st.session_state.criteria_set = True
        st.success("Screening criteria set!")

    st.markdown("</div>", unsafe_allow_html=True)

def render_control_panel():
    if not st.session_state.criteria_set:
        return
        
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    st.markdown("## Add Paper to Graph")

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        doi_input = st.text_input(
            "Enter DOI (e.g., 10.1038/nature12373):",
            placeholder="10.1038/nature12373",
            key="doi_input"
        )

    with col2:
        if st.button("Add Paper", key="add_paper_btn", use_container_width=True):
            if doi_input:
                with st.spinner("Fetching paper..."):
                    start_time = time.time()
                    success = add_paper_to_graph(doi_input, is_main_paper=True, criteria=st.session_state.criteria)
                    elapsed_time = time.time() - start_time
                    
                    if success:
                        st.session_state.selected_node = clean_doi(doi_input)
                        st.success(f"Paper added to the graph in {elapsed_time:.2f} seconds!")
            else:
                st.error("Please enter a valid DOI")

    with col3:
        if st.button("Reset Graph", key="reset_graph_btn", use_container_width=True):
            st.session_state.graph.clear()
            st.session_state.papers = {}
            st.session_state.selected_node = None
            st.session_state.screening_results = {}
            st.session_state.main_paper = None
            st.session_state.snowballed_papers = set()
            st.session_state.failed_dois = set()
            st.success("Graph has been reset!")

    st.markdown("</div>", unsafe_allow_html=True)

def render_paper_details():
    if not st.session_state.selected_node or st.session_state.selected_node not in st.session_state.papers:
        return
        
    paper = st.session_state.papers[st.session_state.selected_node]
    
    with st.container():
        eligibility_badge = ""
        confidence_text = ""
        if st.session_state.selected_node in st.session_state.screening_results:
            if st.session_state.screening_results[st.session_state.selected_node]['eligible']:
                eligibility_badge = '<div class="eligible-badge">Eligible</div>'
            else:
                eligibility_badge = '<div class="not-eligible-badge">Not Eligible</div>'
            
            confidence = st.session_state.screening_results[st.session_state.selected_node].get('ai_confidence', 0)
            confidence_text = f"<p><strong>AI Confidence:</strong> {confidence:.2f}</p>"
        
        st.markdown(f"""
        <div class="paper-card">
            <h3>{paper['title']}</h3>
            <p><strong>Authors:</strong> {', '.join(paper['authors'])}</p>
            <p><strong>Year:</strong> {paper['year']}</p>
            <p><strong>Journal:</strong> {paper['journal']}</p>
            <div class="doi-badge">DOI: {paper['doi']}</div>
            <div class="citation-badge">Citations: {paper['citation_count']}</div>
            {eligibility_badge}
            {confidence_text}
            <p><strong>Data Source:</strong> {paper['source']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if paper['references']:
        st.markdown("<h3 class='section-title'>References</h3>", unsafe_allow_html=True)
        
        ref_data = []
        for ref_doi in paper['references']:
            ref_doi_clean = clean_doi(ref_doi)
            if ref_doi_clean in st.session_state.papers:
                ref_paper = st.session_state.papers[ref_doi_clean]
                eligibility_status = ""
                confidence = ""
                if ref_doi_clean in st.session_state.screening_results:
                    if st.session_state.screening_results[ref_doi_clean]['eligible']:
                        eligibility_status = "Eligible"
                    else:
                        eligibility_status = "Not Eligible"
                    confidence = f"{st.session_state.screening_results[ref_doi_clean].get('ai_confidence', 0):.2f}"
                ref_data.append({
                    'DOI': ref_doi_clean,
                    'Title': ref_paper['title'],
                    'Authors': ', '.join(ref_paper['authors']),
                    'Year': ref_paper['year'],
                    'Journal': ref_paper['journal'],
                    'Citations': ref_paper['citation_count'],
                    'Eligibility': eligibility_status,
                    'AI Confidence': confidence
                })
            else:
                ref_data.append({
                    'DOI': ref_doi_clean,
                    'Title': 'Not loaded',
                    'Authors': '',
                    'Year': '',
                    'Journal': '',
                    'Citations': '',
                    'Eligibility': '',
                    'AI Confidence': ''
                })
        
        ref_df = pd.DataFrame(ref_data)
        st.dataframe(ref_df, use_container_width=True)
        
        if st.button("Load All References", key="load_all_refs"):
            with st.spinner("Loading all references..."):
                status_text = st.empty()
                start_time = time.time()
                
                success_count = snowball_paper(st.session_state.selected_node, st.session_state.criteria)
                
                elapsed_time = time.time() - start_time
                status_text.text(f"Completed: {success_count} references loaded in {elapsed_time:.2f} seconds")
                st.success(f"Loaded {success_count} references successfully")
                
                st.rerun()

def render_snowballing_section():
    if st.session_state.graph.number_of_nodes() <= 1:
        return
        
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    st.markdown("## Snowball Snowballed Papers")
    
    snowballed_papers = [doi for doi in st.session_state.papers.keys() if doi != st.session_state.main_paper]
    
    if snowballed_papers:
        paper_options = []
        for doi in snowballed_papers:
            paper = st.session_state.papers[doi]
            paper_options.append(f"{paper['title']} ({doi})")
        
        snowball_option = st.radio(
            "Select snowballing option:",
            ["Snowball and screen snowballed paper (1 at a time)", "Snowball and screen all the Snowballed papers at a single time"],
            key="snowball_option"
        )
        
        use_same_criteria = st.radio(
            "Use same criteria for all?",
            ["Yes", "No"],
            key="use_same_criteria",
            horizontal=True
        )
        
        batch_criteria_to_use = st.session_state.criteria
        if use_same_criteria == "No":
            st.markdown("### Batch Snowballing Criteria")
            
            batch_criteria_to_use = get_criteria_inputs(prefix="batch_")
            
        if snowball_option == "Snowball and screen snowballed paper (1 at a time)":
            selected_snowball_paper = st.selectbox(
                "Select a snowballed paper to snowball further:",
                options=paper_options,
                key="snowball_paper_select"
            )
            
            selected_snowball_doi = re.search(r'\((10\.\d+\/[^\)]+)\)$', selected_snowball_paper)
            if selected_snowball_doi:
                selected_snowball_doi = selected_snowball_doi.group(1)
            
            final_criteria = st.session_state.criteria if use_same_criteria == "Yes" else batch_criteria_to_use
            
            if st.button("Snowball Selected Paper", key="snowball_selected_btn"):
                if selected_snowball_doi:
                    with st.spinner(f"Snowballing {selected_snowball_doi}..."):
                        success_count = snowball_paper(selected_snowball_doi, final_criteria)
                        
                        st.success(f"Added {success_count} references for {selected_snowball_doi}!")
                        
                        st.rerun()
                else:
                    st.error("Please select a paper to snowball")
        
        else:
            final_criteria = st.session_state.criteria if use_same_criteria == "Yes" else batch_criteria_to_use
            
            if st.button("Snowball All Papers", key="snowball_all_btn"):
                with st.spinner("Snowballing all papers..."):
                    status_text = st.empty()
                    start_time = time.time()
                    
                    total_success = 0
                    papers_to_snowball = [doi for doi in st.session_state.papers.keys() 
                                        if doi not in st.session_state.snowballed_papers and doi != st.session_state.main_paper]
                    
                    for i, doi in enumerate(papers_to_snowball):
                        detailed_progress_bar(i+1, len(papers_to_snowball), start_time, status_text)
                        
                        success_count = snowball_paper(doi, final_criteria)
                        total_success += success_count
                        time.sleep(0.5)
                    
                    elapsed_time = time.time() - start_time
                    status_text.text(f"Completed: {total_success} references loaded from all papers in {elapsed_time:.2f} seconds")
                    st.success(f"Loaded {total_success} references from all papers!")
                    
                    st.rerun()
    
    if st.session_state.failed_dois:
        st.markdown("### Failed to Fetch")
        failed_dois_list = list(st.session_state.failed_dois)
        st.markdown(f"<div class='error-message'>Failed to fetch {len(failed_dois_list)} papers. These DOIs will be retried in subsequent operations.</div>", unsafe_allow_html=True)
        with st.expander("View Failed DOIs"):
            st.write(failed_dois_list)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_network_visualization():
    if st.session_state.graph.number_of_nodes() == 0:
        return
        
    st.markdown("<h2 class='section-title'>Paper Citation Network</h2>", unsafe_allow_html=True)
    
    net = create_network_graph()
    net.save_graph("paper_network.html")
    HtmlFile = open("paper_network.html", 'r', encoding='utf-8')
    st.markdown("<div class='network-container'>", unsafe_allow_html=True)
    components.html(HtmlFile.read(), height=650)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<h3 class='section-title'>Export Options</h3>", unsafe_allow_html=True)
    
    download_cols = st.columns(7)
    
    data = export_graph_data()
    with download_cols[0]:
        st.download_button(
            label="Download JSON",
            data=json.dumps(data, indent=2),
            file_name=f"paper_snowball_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    csv_data = create_csv_export()
    with download_cols[1]:
        st.download_button(
            label="Download CSV",
            data=csv_data.to_csv(index=False).encode('utf-8'),
            file_name=f"paper_snowball_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with open("paper_network.html", 'r', encoding='utf-8') as f:
        html_content = f.read()

    with download_cols[2]:
        st.download_button(
            label="Download HTML",
            data=html_content,
            file_name=f"paper_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html"
        )
    
    png_data = create_png_image()
    if png_data:
        with download_cols[3]:
            st.download_button(
                label="Download PNG",
                data=png_data,
                file_name=f"paper_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
    else:
        with download_cols[3]:
            st.button("Download PNG", disabled=True, help="PNG generation failed")
    
    pdf_data = create_pdf()
    if pdf_data:
        with download_cols[4]:
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name=f"paper_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
    else:
        with download_cols[4]:
            st.button("Download PDF", disabled=True, help="PDF generation failed")
    
    gexf_data = generate_gexf()
    with download_cols[5]:
        st.download_button(
            label="Download GEXF (Gephi)",
            data=gexf_data,
            file_name=f"paper_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gexf",
            mime="application/xml"
        )
    
    graphml_data = generate_graphml()
    with download_cols[6]:
        st.download_button(
            label="Download GraphML",
            data=graphml_data,
            file_name=f"paper_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.graphml",
            mime="application/xml"
        )

def render_footer():
    st.markdown("""
    <div class="footer-container">
        <div class="footer-left">
            <div>© 2025 Vihaan Sahu</div>
            <div>Licensed under the Apache License, Version 2.0</div>
        </div>
        <div class="footer-center">
            <span>Snowih</span>
            <span>Ai-Powered Snowballing</span>
            <a href='https://github.com/Snowih/Snowih' target='_blank' class='footer-link'>GitHub Repository</a>
        </div>
    </div>
    """, unsafe_allow_html=True)