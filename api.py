import requests
import re
from bs4 import BeautifulSoup
from utils import clean_doi, extract_doi

CROSSREF_API = "https://api.crossref.org/works/"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/"
DOI_RESOLVER = "https://doi.org/"

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