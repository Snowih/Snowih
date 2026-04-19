import streamlit as st
import networkx as nx
from pyvis.network import Network
import pandas as pd
from datetime import datetime
import json
from io import BytesIO

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

def generate_gexf():
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
        # Basic XML escaping
        title_esc = paper["title"].replace('"', '&quot;')
        gexf_data += f'<node id="{node}" label="{title_esc[:25]}...">\n'
        gexf_data += f'<attvalues>\n'
        gexf_data += f'<attvalue for="0" value="{title_esc}"/>\n'
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
    return gexf_data

def generate_graphml():
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
    return graphml_data