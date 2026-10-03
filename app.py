/* Estilização robusta para st.link_button e st.button */
div.stButton > button,
div[data-testid="stLinkButton"] > a,
a[data-testid="stBaseButton-secondary"] {
    background-color: #3b5e43 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid #3b5e43 !important;
    font-weight: 600 !important;
    text-align: center !important;
    text-decoration: none !important;
    transition: all 0.3s ease !important;
}

div.stButton > button:hover,
div[data-testid="stLinkButton"] > a:hover,
a[data-testid="stBaseButton-secondary"]:hover {
    background-color: #2c4732 !important;
    border-color: #2c4732 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
}
