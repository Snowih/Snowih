import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        /* Hide Sidebar Completely */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Force light theme - override everything */
        :root {
            --background-color: #FFFFFF !important;
            --text-color: #000000 !important;
            --primary-color: #333333 !important;
            --secondary-background-color: #F0F2F6 !important;
        }
        
        /* Force body to light theme */
        body {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        /* Override all Streamlit elements */
        .stApp {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        /* Main container */
        .main {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        /* All text elements */
        h1, h2, h3, h4, h5, h6, p, span, div, label, li {
            color: #000000 !important;
        }
        
        /* Input elements */
        input, select, textarea {
            background-color: #E6F3FF !important;
            color: #000000 !important;
            border: 1px solid #CCCCCC !important;
        }
        
        /* Buttons */
        button, .stButton > button {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        
        /* Dataframes */
        .dataframe, .dataframe td, .dataframe th {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #DDDDDD !important;
        }
        
        /* Headers and sections */
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
            background-color: #FFFFFF !important;
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
            color: #000000 !important;
            text-align: right;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .header-subtitle {
            font-size: 3rem !important;
            color: #000000 !important;
            text-align: right;
            margin-bottom: 1rem;
            line-height: 1.1;
        }
        
        .section-title {
            font-size: 1.5rem;
            color: #000000 !important;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        /* Input containers */
        .stTextInput > div > div > input {
            background-color: #E6F3FF !important;
            border: 1px solid transparent !important;
            border-radius: 0.375rem !important;
            color: #000000 !important;
            caret-color: #000000 !important;
        }
        
        .stSelectbox > div > div > select {
            background-color: #E6F3FF !important;
            border: 1px solid transparent !important;
            border-radius: 0.375rem !important;
            color: #000000 !important;
            caret-color: #000000 !important;
        }
        
        .stNumberInput > div > div > input {
            background-color: #E6F3FF !important;
            border: 1px solid transparent !important;
            border-radius: 0.375rem !important;
            color: #000000 !important;
            caret-color: #000000 !important;
        }
        
        .snowball-inputs .stNumberInput > div > div > input,
        .snowball-inputs .stSelectbox > div > div > select {
            background-color: #bfbfbf !important;
            color: #000000 !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #AAAAAA !important;
        }
        
        /* Buttons */
        .stButton button, button, .stDownloadButton, .stDownloadButton button {
            background-color: #333333 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 0.375rem !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
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
        
        /* Data display */
        .stDataFrame {
            border: none !important;
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        /* Paper cards */
        .paper-card {
            background-color: #1E3A8A !important;
            color: #FFFFFF !important;
            border-radius: 0.5rem !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
            border-left: 4px solid #3B82F6 !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }
        
        .paper-card * {
            color: #FFFFFF !important;
        }
        
        .doi-badge {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            padding: 0.25rem 0.75rem !important;
            border-radius: 9999px !important;
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            display: inline-block !important;
            margin-top: 0.5rem !important;
            margin-right: 0.5rem !important;
        }
        
        .citation-badge {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            padding: 0.25rem 0.75rem !important;
            border-radius: 9999px !important;
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            display: inline-block !important;
            margin-top: 0.5rem !important;
            margin-right: 0.5rem !important;
        }
        
        .eligible-badge {
            background-color: #10B981 !important;
            color: #FFFFFF !important;
            padding: 0.25rem 0.75rem !important;
            border-radius: 9999px !important;
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            display: inline-block !important;
            margin-top: 0.5rem !important;
        }
        
        .not-eligible-badge {
            background-color: #EF4444 !important;
            color: #FFFFFF !important;
            padding: 0.25rem 0.75rem !important;
            border-radius: 9999px !important;
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            display: inline-block !important;
            margin-top: 0.5rem !important;
        }
        
        /* Network visualization */
        .network-container {
            border-radius: 0.5rem !important;
            overflow: hidden !important;
            margin-bottom: 2rem !important;
            border: 1px solid #000000 !important;
        }
        
        /* Progress and panels */
        .progress-container {
            margin: 1rem 0 !important;
        }
        
        .control-panel {
            background-color: transparent !important;
            border: none !important;
            border-radius: 0.5rem !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
        }
        
        .criteria-panel {
            background-color: transparent !important;
            border: none !important;
            border-radius: 0.5rem !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
            margin-top: 2rem !important; /* Adjusted from 10rem since sidebar is gone */
        }
        
        .element-container .stDivider {
            display: none !important;
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
        
        /* Alerts */
        .stAlert {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #000000 !important;
        }
        
        /* Footer */
        .footer-container {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            width: 100% !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            color: #000000 !important;
            padding: 1rem !important;
            font-size: 1.05rem !important;
            background-color: #f8f9fa !important;
            border-top: 1px solid #e9ecef !important;
            z-index: 1000 !important;
        }
        
        .footer-left { 
            text-align:left !important; 
        }
        
        .footer-center { 
            display:flex !important; 
            gap:40px !important; 
            justify-content:center !important; 
            align-items:center !important; 
        }
        
        .footer-link { 
            color:#3498db !important; 
            text-decoration:none !important; 
            transition:color 0.3s ease !important; 
        }
        
        .footer-link:hover { 
            color:#5682B1 !important; 
        }
        
        .main-content {
            padding-bottom: 80px !important;
        }
        
        /* Download options */
        .download-options {
            display: flex !important;
            flex-direction: row !important;
            gap: 5px !important;
            margin-top: 1rem !important;
        }
        
        .download-options > div {
            display: inline-block !important;
        }
        
        /* Error messages */
        .error-message {
            color: #EF4444 !important;
            font-size: 0.875rem !important;
            margin-top: 0.5rem !important;
        }
        
        /* Progress details */
        .progress-details {
            display: flex !important;
            justify-content: space-between !important;
            margin-bottom: 0.5rem !important;
        }
        
        .progress-text {
            font-size: 0.875rem !important;
            color: #000000 !important;
        }
        
        /* Responsiveness */
        @media (max-width: 768px) {
            .header-container {
                height: auto !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 1rem !important;
            }
            
            .header-content {
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            .header-logo {
                margin-right: 0 !important;
                margin-bottom: 1rem !important;
            }
            
            .logo {
                width: 250px !important;
                height: 250px !important;
            }
            
            .header-text {
                align-items: center !important;
                text-align: center !important;
            }
            
            .main-header {
                font-size: 2.8rem !important;
                text-align: center !important;
            }
            
            .header-subtitle {
                font-size: 1.6rem !important;
                text-align: center !important;
            }
            
            .criteria-panel {
                margin-top: 2rem !important;
            }
            
            .footer-container {
                flex-direction: column !important;
                gap: 10px !important;
                font-size: 0.9rem !important;
            }
            
            .footer-center {
                gap: 20px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)