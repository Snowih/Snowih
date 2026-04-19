import streamlit as st
import requests
import networkx as nx
import time
from api import fetch_paper
from utils import clean_doi

def screen_paper_with_ai(paper, criteria):
    try:
        text = paper.get('title', '')
        if paper.get('abstract'):
            text += " " + paper.get('abstract', '')
        
        framework = criteria.get('framework', 'Manual')
        
        model_name = st.session_state.get('hf_model', 'facebook/bart-large-mnli')
        api_url = f"https://api.inference.huggingface.co/models/{model_name}"
        headers = {}
        if st.session_state.get('hf_api_key'):
            headers['Authorization'] = f"Bearer {st.session_state.hf_api_key}"
        
        candidate_labels = []
        hypothesis_text = ""
        
        if framework == "PICO":
            population = criteria.get('pico_population', '')
            intervention = criteria.get('pico_intervention', '')
            comparison = criteria.get('pico_comparison', '')
            outcome = criteria.get('pico_outcome', '')
            
            parts = []
            if population: parts.append(f"population: {population}")
            if intervention: parts.append(f"intervention: {intervention}")
            if comparison: parts.append(f"comparison: {comparison}")
            if outcome: parts.append(f"outcome: {outcome}")
            
            if not parts:
                return {'eligible': True, 'ai_confidence': 1.0}
            
            hypothesis_text = "This study involves " + ", ".join(parts) + "."
            candidate_labels = ["Relevant", "Irrelevant"]
            
        else: 
            keywords = criteria.get('keywords', '')
            study_type = criteria.get('study_type', '')
            
            if not keywords and not study_type:
                return {'eligible': True, 'ai_confidence': 1.0}
            
            if keywords:
                candidate_labels.append(f"related to {keywords}")
            if study_type and study_type != 'Any':
                candidate_labels.append(f"about {study_type.lower()}")
            
            hypothesis_text = None
            
        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": candidate_labels}
        }
        
        if hypothesis_text and framework == "PICO":
            payload["parameters"]["hypothesis_template"] = hypothesis_text
        
        if not st.session_state.get('hf_api_key'):
            # Fallback silently or inform user via UI if needed, here we fallback to rules
            return screen_paper_with_rules(paper, criteria)

        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return screen_paper_with_rules(paper, criteria)
        
        result = response.json()
        
        if framework == "PICO":
            labels = result.get('labels', [])
            scores = result.get('scores', [])
            
            relevant_score = 0
            for label, score in zip(labels, scores):
                if label == "Relevant":
                    relevant_score = score
                    break
            
            eligible = relevant_score > 0.5
            
            return {
                'eligible': eligible,
                'ai_confidence': relevant_score,
                'year_match': True,
                'keyword_match': eligible,
                'study_type_match': eligible
            }
        else:
            scores = {label: score for label, score in zip(result['labels'], result['scores'])}
            
            keyword_match = True
            study_type_match = True
            
            keywords = criteria.get('keywords', '')
            if keywords:
                keyword_scores = [scores.get(f"related to {k.strip()}", 0) for k in keywords.split(',')]
                keyword_match = max(keyword_scores) > 0.5 if keyword_scores else True
            
            study_type = criteria.get('study_type', '')
            if study_type and study_type != 'Any':
                study_type_score = scores.get(f"about {study_type.lower()}", 0)
                study_type_match = study_type_score > 0.5
            
            eligible = keyword_match and study_type_match
            
            confs = []
            if keywords: confs.append(max([scores.get(f"related to {k.strip()}", 0) for k in keywords.split(',')]))
            if study_type: confs.append(scores.get(f"about {study_type.lower()}", 0))
            overall_confidence = sum(confs) / len(confs) if confs else 0

            return {
                'eligible': eligible,
                'year_match': True, 
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
    
    framework = criteria.get('framework', 'Manual')
    
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
    
    eligible = year_match
    
    if framework == "Manual":
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
        
        eligible = eligible and keyword_match and study_type_match
        return {
            'eligible': eligible,
            'year_match': year_match,
            'keyword_match': keyword_match,
            'study_type_match': study_type_match,
            'ai_confidence': 1.0 if eligible else 0.0
        }
    
    elif framework == "PICO":
        components = [
            criteria.get('pico_population', '').lower(),
            criteria.get('pico_intervention', '').lower(),
            criteria.get('pico_comparison', '').lower(),
            criteria.get('pico_outcome', '').lower()
        ]
        
        for comp in components:
            if comp and comp not in text:
                eligible = False
                break
                
        return {
            'eligible': eligible,
            'year_match': year_match,
            'keyword_match': eligible, 
            'study_type_match': eligible, 
            'ai_confidence': 1.0 if eligible else 0.0
        }
        
    return {
        'eligible': True,
        'year_match': True,
        'keyword_match': True,
        'study_type_match': True,
        'ai_confidence': 1.0
    }

def add_paper_to_graph(doi, parent_doi=None, is_main_paper=False, criteria=None):
    doi = clean_doi(doi)
    
    if doi in st.session_state.papers:
        return True
        
    paper = fetch_paper(doi)
    if not paper or not paper.get('title'):
        st.session_state.failed_dois.add(doi)
        if is_main_paper: 
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