import streamlit as st


from styles import apply_custom_css
from utils import initialize_session_state
from views import (
    render_header,
    render_ai_settings,
    render_criteria_panel,
    render_control_panel,
    render_paper_details,
    render_snowballing_section,
    render_network_visualization,
    render_footer
)


st.set_page_config(
    page_title="Snowih",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed" 
)


initialize_session_state()


apply_custom_css()

def main():
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    render_header()
    

    render_ai_settings()
    
    render_criteria_panel()
    render_control_panel()
    render_paper_details()
    render_snowballing_section()
    render_network_visualization()
    
    st.markdown("</div>", unsafe_allow_html=True)
    render_footer()

if __name__ == "__main__":
    main()