import streamlit as st
import requests
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import time
import re
import pandas as pd
from datetime import datetime
import json
import os
import base64
from io import BytesIO
from bs4 import BeautifulSoup

CROSSREF_API = "https://api.crossref.org/works/"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/"
HUGGINGFACE_API = "https://api.inference.huggingface.co/models/facebook/bart-large-mnli"
DOI_RESOLVER = "https://doi.org/"

st.set_page_config(
    page_title="Snowih",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    initial_theme_state="light" 
)

def initialize_session_state():
    if 'graph' not in st.session_state:
        st.session_state.graph = nx.DiGraph()
    if 'papers' not in st.session_state:
        st.session_state.papers = {}
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None
    if 'criteria' not in st.session_state:
        st.session_state.criteria = {}
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

initialize_session_state()

def apply_custom_css():
    st.markdown("""
    <style>
        * {
            box-sizing: border-box;
        }
        
        body {
            background-color: #FFFFFF;
            color: #000000;
            font-family: 'Inter', sans-serif;
        }
        
        .header-container {
            position: relative;
            width: 100%;
            height: 350px;
            overflow: hidden;
            margin-bottom: 2rem;
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            justify-content: flex-end;
            padding: 0.2rem 4rem 1rem 1rem;
        }
        
        .header-content {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-end;
            max-width: 1200px;
            width: 100%;
        }
        
        .header-logo {
            flex: 0 0 auto;
            margin-right: 2rem;
        }
        
        .header-text {
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: flex-end;
        }
        
        .logo {
            width: 340px;
            height: 340px;
            object-fit: contain;
        }
        
        .main-header {
            font-size: 5.6rem;
            color: #000000;
            text-align: right;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .header-subtitle {
            font-size: 3rem !important;
            color: #000000;
            text-align: right;
            margin-bottom: 1rem;
            line-height: 1.1;
        }
        
        .section-title {
            font-size: 1.5rem;
            color: #000000;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[style*="flex-direction: column;"] {
            background-color: #FFFFFF;
            border: none;
            box-shadow: none;
            color: #000000;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none;
        }
        
        div[data-testid="stVerticalBlock"] {
            border: none;
            box-shadow: none;
            background-color: #FFFFFF;
            color: #000000;
        }
        
        .stTextInput > div > div > input {
            background-color: #E6F3FF;
            border: 1px solid transparent;
            border-radius: 0.375rem;
            color: #000000 !important;
            caret-color: #000000;
        }
        
        .stSelectbox > div > div > select {
            background-color: #E6F3FF;
            border: 1px solid transparent;
            border-radius: 0.375rem;
            color: #000000 !important;
            caret-color: #000000;
        }
        
        .stNumberInput > div > div > input {
            background-color: #E6F3FF;
            border: 1px solid transparent;
            border-radius: 0.375rem;
            color: #000000 !important;
            caret-color: #000000;
        }
        
        .snowball-inputs .stNumberInput > div > div > input,
        .snowball-inputs .stSelectbox > div > div > select {
            background-color: #bfbfbf !important;
            color: #000000 !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #AAAAAA !important;
        }
        
        .stButton button, button, .stDownloadButton, .stDownloadButton button {
            background-color: #333333 !important;
            color: #FFFFFF !important;
            border: none;
            border-radius: 0.375rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        
        .stButton button p, button p, .stDownloadButton p, .stDownloadButton button p {
            color: #FFFFFF !important;
        }
        
        button[kind="primary"] {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        
        button[kind="primary"] p {
            color: #FFFFFF !important;
        }
        
        .stButton button span, button span, .stDownloadButton span, .stDownloadButton button span {
            color: #FFFFFF !important;
        }
        
        .stButton button div, button div, .stDownloadButton div, .stDownloadButton button div {
            color: #FFFFFF !important;
        }
        
        .stButton button *, button *, .stDownloadButton *, .stDownloadButton button * {
            color: #FFFFFF !important;
        }
        
        .stDataFrame {
            border: none;
            background-color: #FFFFFF;
            color: #000000;
        }
        
        .paper-card {
            background-color: #1E3A8A !important;
            color: #FFFFFF !important;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border-left: 4px solid #3B82F6;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .paper-card * {
            color: #FFFFFF !important;
        }
        
        .doi-badge {
            background-color: #FFFFFF;
            color: #000000;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            display: inline-block;
            margin-top: 0.5rem;
            margin-right: 0.5rem;
        }
        
        .citation-badge {
            background-color: #FFFFFF;
            color: #000000;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            display: inline-block;
            margin-top: 0.5rem;
            margin-right: 0.5rem;
        }
        
        .eligible-badge {
            background-color: #10B981;
            color: #FFFFFF;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            display: inline-block;
            margin-top: 0.5rem;
        }
        
        .not-eligible-badge {
            background-color: #EF4444;
            color: #FFFFFF;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            display: inline-block;
            margin-top: 0.5rem;
        }
        
        .network-container {
            border-radius: 0.5rem;
            overflow: hidden;
            margin-bottom: 2rem;
            border: 1px solid #000000;
        }
        
        .progress-container {
            margin: 1rem 0;
        }
        
        .control-panel {
            background-color: transparent;
            border: none;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .criteria-panel {
            background-color: transparent;
            border: none;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            margin-top: 10rem;
        }
        
        .element-container .stDivider {
            display: none;
        }
        
        .css-1d391kg {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        .css-1v0mbdj {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        .css-1kyxreq {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        .css-1r6slv0 {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        .css-1c0m1x2 {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        .dataframe {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        .dataframe td {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        .dataframe th {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        .streamlit-expanderHeader {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        .stRadio > div {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        .stSelectbox > div {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        .stNumberInput > div {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        .stTextInput > div {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        .stButton > button {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        
        .stDownloadButton {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        
        .stProgress > div > div > div {
            background-color: #333333 !important;
        }
        
        p, h1, h2, h3, h4, h5, h6, li, span, div, label {
            color: #000000 !important;
        }
        
        input, select, textarea {
            color: #000000 !important;
        }
        
        .stAlert {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #000000 !important;
        }
        
        .paper-card, .paper-card *, .paper-card p, .paper-card h3, .paper-card strong, .paper-card span {
            color: #FFFFFF !important;
        }
        
        .doi-badge, .citation-badge {
            color: #000000 !important;
        }
        
        .stButton button, button, .stDownloadButton, .stDownloadButton button,
        .stButton button *, button *, .stDownloadButton *, .stDownloadButton button * {
            color: #FFFFFF !important;
        }
        
        .download-options {
            display: flex;
            flex-direction: row;
            gap: 5px;
            margin-top: 1rem;
        }
        
        .download-options > div {
            display: inline-block;
        }
        
        .error-message {
            color: #EF4444;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        
        .progress-details {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        
        .progress-text {
            font-size: 0.875rem;
            color: #000000;
        }
        
        .footer-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #000;
            padding: 1rem;
            font-size: 1.05rem;
            background-color: #f8f9fa;
            border-top: 1px solid #e9ecef;
            z-index: 1000;
        }
        .footer-left { 
            text-align:left; 
        }
        .footer-center { 
            display:flex; 
            gap:40px; 
            justify-content:center; 
            align-items:center; 
        }
        .footer-link { 
            color:#3498db; 
            text-decoration:none; 
            transition:color 0.3s ease; 
        }
        .footer-link:hover { 
            color:#5682B1; 
        }
        
        .main-content {
            padding-bottom: 80px;
        }
        
        /* Responsiveness */
        @media (max-width: 768px) {
            .header-container {
                height: auto;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 1rem;
            }
            
            .header-content {
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            
            .header-logo {
                margin-right: 0;
                margin-bottom: 1rem;
            }
            
            .logo {
                width: 200px;
                height: 200px;
            }
            
            .header-text {
                align-items: center;
                text-align: center;
            }
            
            .main-header {
                font-size: 3rem;
                text-align: center;
            }
            
            .header-subtitle {
                font-size: 1.8rem !important;
                text-align: center;
            }
            
            .criteria-panel {
                margin-top: 2rem;
            }
            
            .footer-container {
                flex-direction: column;
                gap: 10px;
                font-size: 0.9rem;
            }
            
            .footer-center {
                gap: 20px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_css()

def get_image_as_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image {path}: {e}")
        return ""

def render_header():
    logo_base64 = get_image_as_base64("assets/1.png")
    
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

def extract_doi(text):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    match = re.search(doi_pattern, text, re.IGNORECASE)
    return match.group(0) if match else None

def clean_doi(doi):
    doi = re.sub(r'^https?://doi\.org/', '', doi)
    doi = re.sub(r'^doi:', '', doi, flags=re.IGNORECASE)
    doi = doi.strip()
    return doi

def fetch_paper_crossref(doi):
    try:
        doi = clean_doi(doi)
        url = f"{CROSSREF_API}{doi}"
        headers = {'User-Agent': 'ResearchSnowballer/1.0 (mailto:your.email@example.com)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        message = data.get('message', {})
        
        title = message.get('title', [''])[0]
        authors = []
        for author in message.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            if given or family:
                authors.append(f"{given} {family}".strip())
        
        year = message.get('published-print', {}).get('date-parts', [['']])[0][0]
        if not year:
            year = message.get('published-online', {}).get('date-parts', [['']])[0][0]
        
        journal = message.get('short-container-title', [''])[0]
        if not journal:
            journal = message.get('container-title', [''])[0]
        
        references = []
        for ref in message.get('reference', []):
            if 'DOI' in ref:
                references.append(ref['DOI'])
            elif 'unstructured' in ref:
                doi_match = re.search(r'doi:\s*(10\.\d+\/[^\s]+)', ref['unstructured'], re.IGNORECASE)
                if doi_match:
                    references.append(doi_match.group(1))
                else:
                    doi_match = extract_doi(ref['unstructured'])
                    if doi_match:
                        references.append(doi_match)
        
        citation_count = message.get('is-referenced-by-count', 0)
        
        return {
            'title': title,
            'authors': authors,
            'year': year,
            'journal': journal,
            'references': references,
            'doi': doi,
            'citation_count': citation_count,
            'source': 'Crossref'
        }
    except Exception as e:
        return None

def fetch_paper_semantic_scholar(doi):
    try:
        doi = clean_doi(doi)
        url = f"{SEMANTIC_SCHOLAR_API}DOI:{doi}"
        params = {
            'fields': 'title,authors,year,publicationDate,venue,referenceCount,citationCount,references,abstract'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        title = data.get('title', '')
        authors = [f"{author.get('name', '')}" for author in data.get('authors', [])]
        year = data.get('year') or data.get('publicationDate', '')[:4]
        journal = data.get('venue', '')
        abstract = data.get('abstract', '')
        
        references = []
        for ref in data.get('references', []):
            if 'doi' in ref:
                references.append(ref['doi'])
        
        citation_count = data.get('citationCount', 0)
        
        return {
            'title': title,
            'authors': authors,
            'year': year,
            'journal': journal,
            'abstract': abstract,
            'references': references,
            'doi': doi,
            'citation_count': citation_count,
            'source': 'Semantic Scholar'
        }
    except Exception as e:
        return None

def fetch_paper_doi_resolver(doi):
    try:
        doi = clean_doi(doi)
        url = f"{DOI_RESOLVER}{doi}"
        headers = {
            'Accept': 'application/vnd.citationstyles.csl+json',
            'User-Agent': 'ResearchSnowballer/1.0 (mailto:your.email@example.com)'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        title = data.get('title', '')
        if isinstance(title, list):
            title = title[0] if title else ''
            
        authors = []
        for author in data.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            if given or family:
                authors.append(f"{given} {family}".strip())
        
        year = data.get('issued', {}).get('date-parts', [['']])[0][0]
        if not year:
            year = data.get('published-print', {}).get('date-parts', [['']])[0][0]
        if not year:
            year = data.get('published-online', {}).get('date-parts', [['']])[0][0]
        
        journal = data.get('container-title', '')
        if isinstance(journal, list):
            journal = journal[0] if journal else ''
        
        references = []
        citation_count = 0
        
        return {
            'title': title,
            'authors': authors,
            'year': year,
            'journal': journal,
            'abstract': '',
            'references': references,
            'doi': doi,
            'citation_count': citation_count,
            'source': 'DOI Resolver'
        }
    except Exception as e:
        return None

def fetch_paper_web_scraping(doi):
    try:
        doi = clean_doi(doi)
        url = f"{DOI_RESOLVER}{doi}"
        headers = {'User-Agent': 'ResearchSnowballer/1.0 (mailto:your.email@example.com)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = ""
        title_tag = soup.find('h1', class_='citation__title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        authors = []
        author_tags = soup.find_all('span', class_='citation__author')
        for author_tag in author_tags:
            authors.append(author_tag.get_text().strip())
        
        journal = ""
        journal_tag = soup.find('span', class_='citation__journal')
        if journal_tag:
            journal = journal_tag.get_text().strip()
        
        year = ""
        year_tag = soup.find('span', class_='citation__date')
        if year_tag:
            year_match = re.search(r'\b(19|20)\d{2}\b', year_tag.get_text())
            if year_match:
                year = year_match.group(0)
        
        references = []
        ref_section = soup.find('div', class_='references')
        if ref_section:
            ref_links = ref_section.find_all('a', href=True)
            for link in ref_links:
                ref_doi = extract_doi(link.get('href', ''))
                if ref_doi:
                    references.append(ref_doi)
        
        return {
            'title': title,
            'authors': authors,
            'year': year,
            'journal': journal,
            'abstract': '',
            'references': references,
            'doi': doi,
            'citation_count': 0,
            'source': 'Web Scraping'
        }
    except Exception as e:
        return None

def fetch_paper(doi):
    sources = [
        fetch_paper_crossref,
        fetch_paper_semantic_scholar,
        fetch_paper_doi_resolver,
        fetch_paper_web_scraping
    ]
    
    for source in sources:
        paper = source(doi)
        if paper and paper.get('title'):
            return paper
    
    return {
        'title': f"Paper with DOI: {doi}",
        'authors': [],
        'year': '',
        'journal': '',
        'abstract': '',
        'references': [],
        'doi': doi,
        'citation_count': 0,
        'source': 'Unknown'
    }

def screen_paper_with_ai(paper, criteria):
    try:
        text = paper.get('title', '')
        if paper.get('abstract'):
            text += " " + paper.get('abstract', '')
        
        candidate_labels = []
        
        if criteria.get('keywords'):
            keywords = [k.strip() for k in criteria.get('keywords', '').split(',')]
            for keyword in keywords:
                candidate_labels.append(f"related to {keyword}")
        
        if criteria.get('study_type') and criteria.get('study_type') != 'Any':
            candidate_labels.append(f"about {criteria.get('study_type').lower()}")
        
        year = paper.get('year', '')
        if year and criteria.get('from_year') and criteria.get('to_year'):
            try:
                year_int = int(year)
                from_year = criteria.get('from_year')
                to_year = criteria.get('to_year')
                if year_int >= from_year and year_int <= to_year:
                    candidate_labels.append("published in the specified time range")
            except:
                pass
        
        if not candidate_labels:
            return {
                'eligible': True,
                'year_match': True,
                'keyword_match': True,
                'study_type_match': True,
                'ai_confidence': 1.0
            }
        
        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": candidate_labels}
        }
        
        response = requests.post(HUGGINGFACE_API, json=payload)
        
        if response.status_code != 200:
            return screen_paper_with_rules(paper, criteria)
        
        result = response.json()
        
        scores = {label: score for label, score in zip(result['labels'], result['scores'])}
        
        keyword_match = True
        study_type_match = True
        year_match = True
        
        if criteria.get('keywords'):
            keyword_scores = [scores.get(f"related to {k.strip()}", 0) for k in criteria.get('keywords', '').split(',')]
            keyword_match = max(keyword_scores) > 0.5 if keyword_scores else True
        
        if criteria.get('study_type') and criteria.get('study_type') != 'Any':
            study_type_score = scores.get(f"about {criteria.get('study_type').lower()}", 0)
            study_type_match = study_type_score > 0.5
        
        year = paper.get('year', '')
        if year and criteria.get('from_year') and criteria.get('to_year'):
            try:
                year_int = int(year)
                from_year = criteria.get('from_year')
                to_year = criteria.get('to_year')
                year_match = year_int >= from_year and year_int <= to_year
            except:
                year_match = True
        
        eligible = keyword_match and study_type_match and year_match
        
        overall_confidence = 0
        if criteria.get('keywords'):
            keyword_scores = [scores.get(f"related to {k.strip()}", 0) for k in criteria.get('keywords', '').split(',')]
            overall_confidence += max(keyword_scores) if keyword_scores else 1
        
        if criteria.get('study_type') and criteria.get('study_type') != 'Any':
            overall_confidence += scores.get(f"about {criteria.get('study_type').lower()}", 0)
        
        if criteria.get('from_year') and criteria.get('to_year'):
            overall_confidence += scores.get("published in the specified time range", 1)
        
        num_criteria = sum([
            1 if criteria.get('keywords') else 0,
            1 if criteria.get('study_type') and criteria.get('study_type') != 'Any' else 0,
            1 if criteria.get('from_year') and criteria.get('to_year') else 0
        ])
        
        overall_confidence = overall_confidence / max(num_criteria, 1)
        
        return {
            'eligible': eligible,
            'year_match': year_match,
            'keyword_match': keyword_match,
            'study_type_match': study_type_match,
            'ai_confidence': overall_confidence
        }
    
    except Exception as e:
        return screen_paper_with_rules(paper, criteria)

def screen_paper_with_rules(paper, criteria):
    title = paper.get('title', '').lower()
    abstract = paper.get('abstract', '').lower()
    text = f"{title} {abstract}"
    year = paper.get('year', '')
    
    year_match = True
    if criteria.get('from_year') and year:
        try:
            year_int = int(year)
            if year_int < criteria.get('from_year'):
                year_match = False
        except:
            pass
    
    if criteria.get('to_year') and year:
        try:
            year_int = int(year)
            if year_int > criteria.get('to_year'):
                year_match = False
        except:
            pass
    
    keyword_match = True
    if criteria.get('keywords'):
        keywords = [k.lower() for k in criteria.get('keywords', '').split(',')]
        if not any(keyword in text for keyword in keywords):
            keyword_match = False
    
    study_type_match = True
    if criteria.get('study_type') and criteria.get('study_type') != 'Any':
        study_type = criteria.get('study_type').lower()
        if study_type not in text:
            study_type_match = False
    
    eligible = year_match and keyword_match and study_type_match
    
    return {
        'eligible': eligible,
        'year_match': year_match,
        'keyword_match': keyword_match,
        'study_type_match': study_type_match,
        'ai_confidence': 1.0 if eligible else 0.0
    }

def add_paper_to_graph(doi, parent_doi=None, is_main_paper=False, criteria=None):
    doi = clean_doi(doi)
    
    if doi in st.session_state.papers:
        return True
        
    paper = fetch_paper(doi)
    if not paper or not paper.get('title'):
        st.session_state.failed_dois.add(doi)
        st.error(f"Failed to fetch paper with DOI: {doi}")
        return False
        
    st.session_state.papers[doi] = paper
    
    if is_main_paper:
        st.session_state.main_paper = doi
    
    screening_criteria = criteria if criteria is not None else st.session_state.criteria
    if screening_criteria:
        screening_result = screen_paper_with_ai(paper, screening_criteria)
        st.session_state.screening_results[doi] = screening_result
    
    st.session_state.graph.add_node(
        doi, 
        title=paper['title'],
        authors=paper['authors'],
        year=paper['year'],
        journal=paper['journal'],
        citation_count=paper['citation_count'],
        source=paper['source'],
        is_main_paper=is_main_paper
    )
    
    if parent_doi and parent_doi in st.session_state.graph:
        st.session_state.graph.add_edge(parent_doi, doi)
    
    return True

def snowball_paper(doi, criteria=None):
    doi = clean_doi(doi)
    
    if doi in st.session_state.snowballed_papers:
        return 0
    
    if doi not in st.session_state.papers:
        return 0
    
    paper = st.session_state.papers[doi]
    references = paper.get('references', [])
    
    success_count = 0
    for ref_doi in references:
        ref_doi_clean = clean_doi(ref_doi)
        if add_paper_to_graph(ref_doi_clean, parent_doi=doi, criteria=criteria):
            success_count += 1
    
    st.session_state.snowballed_papers.add(doi)
    
    return success_count

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

def create_network_graph():
    net = Network(height="600px", width="100%", directed=True, notebook=True, cdn_resources='in_line')
    
    for node, data in st.session_state.graph.nodes(data=True):
        if node not in st.session_state.papers:
            continue
            
        title = data.get('title', 'No title')
        authors = ", ".join(data.get('authors', []))
        year = data.get('year', 'No year')
        journal = data.get('journal', 'No journal')
        citation_count = data.get('citation_count', 0)
        source = data.get('source', 'Unknown')
        is_main_paper = data.get('is_main_paper', False)
        
        if is_main_paper:
            color = "#1E3A8A"
        elif node in st.session_state.screening_results:
            if st.session_state.screening_results[node]['eligible']:
                color = "#10B981"
            else:
                color = "#EF4444"
        else:
            color = "#3B82F6"
            
        size = 15 + min(citation_count / 2, 30)
            
        label = title[:25] + "..." if len(title) > 25 else title
            
        net.add_node(
            node, 
            label=label,
            title=f"<b>{title}</b><br><i>{authors}</i><br>{journal} ({year})<br>Citations: {citation_count}<br>Source: {source}",
            color=color,
            size=size,
            font={'size': 12, 'face': 'Inter', 'color': '#000000'},
            borderWidth=2,
            borderColor="#000000"
        )
    
    for source, target in st.session_state.graph.edges():
        if source not in st.session_state.papers or target not in st.session_state.papers:
            continue
            
        if st.session_state.selected_node:
            if nx.has_path(st.session_state.graph, source, st.session_state.selected_node) and nx.has_path(st.session_state.graph, st.session_state.selected_node, target):
                edge_color = "#F59E0B"
                edge_width = 2.5
            else:
                edge_color = "#000000"
                edge_width = 1.5
        else:
            edge_color = "#000000"
            edge_width = 1.5
            
        net.add_edge(source, target, width=edge_width, color=edge_color, smooth={'type': 'curvedCW'})
    
    net.set_options("""
    {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -30000,
          "centralGravity": 0.1,
          "springLength": 200,
          "springConstant": 0.05,
          "damping": 0.09
        },
        "maxVelocity": 50,
        "minVelocity": 0.75,
        "stabilization": {
          "enabled": true,
          "iterations": 1000,
          "fit": true
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200,
        "hideEdgesOnDrag": true
      },
      "nodes": {
        "font": {
          "face": "Inter",
          "size": 12,
          "color": "#000000"
        }
      }
    }
    """)
    
    return net

def export_graph_data():
    nodes = []
    for node, data in st.session_state.graph.nodes(data=True):
        if node not in st.session_state.papers:
            continue
            
        node_data = {'doi': node}
        paper = st.session_state.papers[node]
        node_data.update({
            'title': paper['title'],
            'authors': ", ".join(paper['authors']),
            'year': paper['year'],
            'journal': paper['journal'],
            'citation_count': paper['citation_count'],
            'source': paper['source']
        })
        if node in st.session_state.screening_results:
            node_data['eligible'] = st.session_state.screening_results[node]['eligible']
            node_data['ai_confidence'] = st.session_state.screening_results[node]['ai_confidence']
        nodes.append(node_data)
    
    edges = []
    for source, target in st.session_state.graph.edges():
        if source in st.session_state.papers and target in st.session_state.papers:
            edges.append({'source': source, 'target': target})
    
    return {
        'nodes': nodes,
        'edges': edges,
        'criteria': st.session_state.criteria,
        'created_at': datetime.now().isoformat()
    }

def create_csv_export():
    data = []
    for doi, paper in st.session_state.papers.items():
        paper_data = {
            'DOI': doi,
            'Title': paper['title'],
            'Authors': ', '.join(paper['authors']),
            'Year': paper['year'],
            'Journal': paper['journal'],
            'Citation Count': paper['citation_count'],
            'Source': paper['source']
        }
        
        if doi in st.session_state.screening_results:
            screening = st.session_state.screening_results[doi]
            paper_data['Eligible'] = screening['eligible']
            paper_data['AI Confidence'] = screening['ai_confidence']
            paper_data['Year Match'] = screening['year_match']
            paper_data['Keyword Match'] = screening['keyword_match']
            paper_data['Study Type Match'] = screening['study_type_match']
        else:
            paper_data['Eligible'] = ''
            paper_data['AI Confidence'] = ''
            paper_data['Year Match'] = ''
            paper_data['Keyword Match'] = ''
            paper_data['Study Type Match'] = ''
        
        data.append(paper_data)
    
    return pd.DataFrame(data)

def create_png_image():
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 10))
        
        pos = nx.spring_layout(st.session_state.graph, seed=42)
        
        node_colors = []
        for node in st.session_state.graph.nodes():
            if node == st.session_state.main_paper:
                node_colors.append('#1E3A8A')
            elif node in st.session_state.screening_results:
                if st.session_state.screening_results[node]['eligible']:
                    node_colors.append('#10B981')
                else:
                    node_colors.append('#EF4444')
            else:
                node_colors.append('#3B82F6')
        
        nx.draw(st.session_state.graph, pos, with_labels=False, node_color=node_colors, 
                node_size=500, font_size=8, font_weight='bold', edge_color='#000000')
        
        labels = {}
        for node in st.session_state.graph.nodes():
            if node == st.session_state.main_paper or (node in st.session_state.screening_results and st.session_state.screening_results[node]['eligible']):
                paper = st.session_state.papers.get(node, {})
                title = paper.get('title', 'No title')
                labels[node] = title[:15] + "..." if len(title) > 15 else title
        
        nx.draw_networkx_labels(st.session_state.graph, pos, labels, font_size=8)
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    except Exception as e:
        st.error(f"Error creating PNG image: {str(e)}")
        return None

def create_pdf():
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        
        pdf_buffer = BytesIO()
        
        with PdfPages(pdf_buffer) as pdf:
            plt.figure(figsize=(12, 10))
            
            pos = nx.spring_layout(st.session_state.graph, seed=42)
            
            node_colors = []
            for node in st.session_state.graph.nodes():
                if node == st.session_state.main_paper:
                    node_colors.append('#1E3A8A')
                elif node in st.session_state.screening_results:
                    if st.session_state.screening_results[node]['eligible']:
                        node_colors.append('#10B981')
                    else:
                        node_colors.append('#EF4444')
                else:
                    node_colors.append('#3B82F6')
            
            nx.draw(st.session_state.graph, pos, with_labels=False, node_color=node_colors, 
                    node_size=500, font_size=8, font_weight='bold', edge_color='#000000')
            
            labels = {}
            for node in st.session_state.graph.nodes():
                if node == st.session_state.main_paper or (node in st.session_state.screening_results and st.session_state.screening_results[node]['eligible']):
                    paper = st.session_state.papers.get(node, {})
                    title = paper.get('title', 'No title')
                    labels[node] = title[:15] + "..." if len(title) > 15 else title
            
            nx.draw_networkx_labels(st.session_state.graph, pos, labels, font_size=8)
            
            plt.title("Research Paper Citation Network", fontsize=16)
            
            pdf.savefig()
            plt.close()
        
        pdf_buffer.seek(0)
        return pdf_buffer
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def render_criteria_panel():
    st.markdown("<div class='criteria-panel'>", unsafe_allow_html=True)
    st.markdown("## Set Screening Criteria")

    col1, col2 = st.columns(2)

    with col1:
        keywords = st.text_input(
            "Research Keywords (comma separated):",
            placeholder="e.g., machine learning, healthcare, diagnosis",
            key="keywords_input"
        )
        
        study_type = st.selectbox(
            "Study Type:",
            ["Any", "Experimental", "Review", "Case Study", "Observational", "Simulation"],
            key="study_type_input"
        )

    with col2:
        from_year = st.number_input(
            "From Year:",
            min_value=1900,
            max_value=2030,
            value=2010,
            key="from_year_input"
        )
        
        to_year = st.number_input(
            "To Year:",
            min_value=1900,
            max_value=2030,
            value=2023,
            key="to_year_input"
        )

    if st.button("Set Criteria", key="set_criteria_btn"):
        st.session_state.criteria = {
            'keywords': keywords,
            'study_type': study_type,
            'from_year': from_year,
            'to_year': to_year
        }
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
            st.session_state.graph = nx.DiGraph()
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
            key="use_same_criteria"
        )
        
        if snowball_option == "Snowball and screen snowballed paper (1 at a time)":
            selected_snowball_paper = st.selectbox(
                "Select a snowballed paper to snowball further:",
                options=paper_options,
                key="snowball_paper_select"
            )
            
            selected_snowball_doi = re.search(r'\((10\.\d+\/[^\)]+)\)$', selected_snowball_paper)
            if selected_snowball_doi:
                selected_snowball_doi = selected_snowball_doi.group(1)
            
            if st.button("Snowball Selected Paper", key="snowball_selected_btn"):
                if selected_snowball_doi:
                    with st.spinner(f"Snowballing {selected_snowball_doi}..."):
                        if use_same_criteria == "No":
                            st.markdown("### Set New Criteria")
                            st.markdown('<div class="snowball-inputs">', unsafe_allow_html=True)
                            new_keywords = st.text_input(
                                "New Research Keywords (comma separated):",
                                key="new_keywords"
                            )
                            new_study_type = st.selectbox(
                                "New Study Type:",
                                ["Any", "Experimental", "Review", "Case Study", "Observational", "Simulation"],
                                key="new_study_type"
                            )
                            new_from_year = st.number_input(
                                "New From Year:",
                                min_value=1900,
                                max_value=2030,
                                value=2010,
                                key="new_from_year"
                            )
                            new_to_year = st.number_input(
                                "New To Year:",
                                min_value=1900,
                                max_value=2030,
                                value=2023,
                                key="new_to_year"
                            )
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            new_criteria = {
                                'keywords': new_keywords,
                                'study_type': new_study_type,
                                'from_year': new_from_year,
                                'to_year': new_to_year
                            }
                        else:
                            new_criteria = st.session_state.criteria
                        
                        success_count = snowball_paper(selected_snowball_doi, new_criteria)
                        
                        st.success(f"Added {success_count} references for {selected_snowball_doi}!")
                        
                        st.rerun()
                else:
                    st.error("Please select a paper to snowball")
        
        else:
            if st.button("Snowball All Papers", key="snowball_all_btn"):
                with st.spinner("Snowballing all papers..."):
                    if use_same_criteria == "No":
                        st.markdown("### Set New Criteria")
                        st.markdown('<div class="snowball-inputs">', unsafe_allow_html=True)
                        all_new_keywords = st.text_input(
                            "New Research Keywords (comma separated):",
                            key="all_new_keywords"
                        )
                        all_new_study_type = st.selectbox(
                            "New Study Type:",
                            ["Any", "Experimental", "Review", "Case Study", "Observational", "Simulation"],
                            key="all_new_study_type"
                        )
                        all_new_from_year = st.number_input(
                            "New From Year:",
                            min_value=1900,
                            max_value=2030,
                            value=2010,
                            key="all_new_from_year"
                        )
                        all_new_to_year = st.number_input(
                            "New To Year:",
                            min_value=1900,
                            max_value=2030,
                            value=2023,
                            key="all_new_to_year"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        all_new_criteria = {
                            'keywords': all_new_keywords,
                            'study_type': all_new_study_type,
                            'from_year': all_new_from_year,
                            'to_year': all_new_to_year
                        }
                    else:
                        all_new_criteria = st.session_state.criteria
                    
                    status_text = st.empty()
                    start_time = time.time()
                    
                    total_success = 0
                    papers_to_snowball = [doi for doi in st.session_state.papers.keys() 
                                        if doi not in st.session_state.snowballed_papers and doi != st.session_state.main_paper]
                    
                    for i, doi in enumerate(papers_to_snowball):
                        detailed_progress_bar(i+1, len(papers_to_snowball), start_time, status_text)
                        
                        success_count = snowball_paper(doi, all_new_criteria)
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
    
    with download_cols[2]:
        st.download_button(
            label="Download HTML",
            data=HtmlFile.read(),
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
    
    gexf_data = '<?xml version="1.0" encoding="UTF-8"?>\n'
    gexf_data += '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n'
    gexf_data += '<graph mode="static" defaultedgetype="directed">\n'
    gexf_data += '<attributes class="node">\n'
    gexf_data += '<attribute id="0" title="title" type="string"/>\n'
    gexf_data += '<attribute id="1" title="authors" type="string"/>\n'
    gexf_data += '<attribute id="2" title="year" type="string"/>\n'
    gexf_data += '<attribute id="3" title="journal" type="string"/>\n'
    gexf_data += '<attribute id="4" title="citation_count" type="integer"/>\n'
    gexf_data += '<attribute id="5" title="source" type="string"/>\n'
    gexf_data += '<attribute id="6" title="eligible" type="boolean"/>\n'
    gexf_data += '<attribute id="7" title="ai_confidence" type="float"/>\n'
    gexf_data += '</attributes>\n'
    gexf_data += '<nodes>\n'
    
    for node, data in st.session_state.graph.nodes(data=True):
        if node not in st.session_state.papers:
            continue
            
        paper = st.session_state.papers[node]
        gexf_data += f'<node id="{node}" label="{paper["title"][:25]}...">\n'
        gexf_data += f'<attvalues>\n'
        gexf_data += f'<attvalue for="0" value="{paper["title"]}"/>\n'
        gexf_data += f'<attvalue for="1" value="{", ".join(paper["authors"])}"/>\n'
        gexf_data += f'<attvalue for="2" value="{paper["year"]}"/>\n'
        gexf_data += f'<attvalue for="3" value="{paper["journal"]}"/>\n'
        gexf_data += f'<attvalue for="4" value="{paper["citation_count"]}"/>\n'
        gexf_data += f'<attvalue for="5" value="{paper["source"]}"/>\n'
        
        if node in st.session_state.screening_results:
            screening = st.session_state.screening_results[node]
            gexf_data += f'<attvalue for="6" value="{screening["eligible"]}"/>\n'
            gexf_data += f'<attvalue for="7" value="{screening["ai_confidence"]}"/>\n'
        
        gexf_data += f'</attvalues>\n'
        gexf_data += f'</node>\n'
    
    gexf_data += '</nodes>\n'
    gexf_data += '<edges>\n'
    
    edge_id = 0
    for source, target in st.session_state.graph.edges():
        if source not in st.session_state.papers or target not in st.session_state.papers:
            continue
            
        gexf_data += f'<edge id="{edge_id}" source="{source}" target="{target}"/>\n'
        edge_id += 1
    
    gexf_data += '</edges>\n'
    gexf_data += '</graph>\n'
    gexf_data += '</gexf>'
    
    with download_cols[5]:
        st.download_button(
            label="Download GEXF (Gephi)",
            data=gexf_data,
            file_name=f"paper_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gexf",
            mime="application/xml"
        )
    
    graphml_data = '<?xml version="1.0" encoding="UTF-8"?>\n'
    graphml_data += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\n'
    graphml_data += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
    graphml_data += 'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns\n'
    graphml_data += 'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n'
    graphml_data += '<key id="title" for="node" attr.name="title" attr.type="string"/>\n'
    graphml_data += '<key id="authors" for="node" attr.name="authors" attr.type="string"/>\n'
    graphml_data += '<key id="year" for="node" attr.name="year" attr.type="string"/>\n'
    graphml_data += '<key id="journal" for="node" attr.name="journal" attr.type="string"/>\n'
    graphml_data += '<key id="citation_count" for="node" attr.name="citation_count" attr.type="integer"/>\n'
    graphml_data += '<key id="source" for="node" attr.name="source" attr.type="string"/>\n'
    graphml_data += '<key id="eligible" for="node" attr.name="eligible" attr.type="boolean"/>\n'
    graphml_data += '<key id="ai_confidence" for="node" attr.name="ai_confidence" attr.type="float"/>\n'
    graphml_data += '<graph id="G" edgedefault="directed">\n'
    
    for node, data in st.session_state.graph.nodes(data=True):
        if node not in st.session_state.papers:
            continue
            
        paper = st.session_state.papers[node]
        graphml_data += f'<node id="{node}">\n'
        graphml_data += f'<data key="title">{paper["title"]}</data>\n'
        graphml_data += f'<data key="authors">{", ".join(paper["authors"])}</data>\n'
        graphml_data += f'<data key="year">{paper["year"]}</data>\n'
        graphml_data += f'<data key="journal">{paper["journal"]}</data>\n'
        graphml_data += f'<data key="citation_count">{paper["citation_count"]}</data>\n'
        graphml_data += f'<data key="source">{paper["source"]}</data>\n'
        
        if node in st.session_state.screening_results:
            screening = st.session_state.screening_results[node]
            graphml_data += f'<data key="eligible">{screening["eligible"]}</data>\n'
            graphml_data += f'<data key="ai_confidence">{screening["ai_confidence"]}</data>\n'
        
        graphml_data += f'</node>\n'
    
    for source, target in st.session_state.graph.edges():
        if source not in st.session_state.papers or target not in st.session_state.papers:
            continue
            
        graphml_data += f'<edge source="{source}" target="{target}"/>\n'
    
    graphml_data += '</graph>\n'
    graphml_data += '</graphml>'
    
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

def main():
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    render_header()
    render_criteria_panel()
    render_control_panel()
    render_paper_details()
    render_snowballing_section()
    render_network_visualization()
    st.markdown("</div>", unsafe_allow_html=True)
    render_footer()

if __name__ == "__main__":
    main()