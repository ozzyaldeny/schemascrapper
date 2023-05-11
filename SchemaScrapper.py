import streamlit as st
st.set_page_config(page_title="Schema Scrapper", layout="wide")

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import json

import requests
import extruct
from w3lib.html import get_base_url



from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES

def scrape(url: str):
    """Parse structured data from a target page."""
    html = get_html(url)
    metadata = get_metadata(html, url)
    return metadata


def get_html(url):
    """Get raw HTML from a URL."""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(url, headers=headers)
    return req.content


def get_metadata(html: bytes, url: str):
    """Fetch JSON-LD structured data."""
    metadata = extruct.extract(
        html,
        base_url=get_base_url(url),
        syntaxes=['json-ld'],
        uniform=True
    )['json-ld']
    if bool(metadata) and isinstance(metadata, list):
        metadata = metadata[0]
    return metadata

def replace_values(json_obj, str_input, str_replace):
    modified_obj = {}
    
    for key, value in json_obj.items():
        if isinstance(value, dict):
            modified_obj[key] = replace_values(value, str_input, str_replace)
        elif isinstance(value, list):
            modified_list = []
            for item in value:
                if isinstance(item, dict):
                    modified_list.append(replace_values(item, str_input, str_replace))
                elif isinstance(item, str) and str_input in item:
                    modified_list.append(item.replace(str_input, str_replace))
                else:
                    modified_list.append(item)
            modified_obj[key] = modified_list
        elif isinstance(value, str) and str_input in value:
            modified_obj[key] = value.replace(str_input, str_replace)
        else:
            modified_obj[key] = value
    
    return modified_obj


def main():
    with st.sidebar:
        st.subheader("Scrap Structured Data from a URL")
        url=st.text_input('URL:')
        if st.button("Scrap Schema"):
            metadata = scrape(url)
            st.session_state['metadata']=metadata
        
    
    c1, c2 = st.columns([1, 3])
    
    if('metadata' in st.session_state):
        metadata = st.session_state['metadata']
        with c1:
            
            search_txt=st.text_input('Search String:')
            replace_txt=st.text_input('Replace With')
            if st.button('Replace'):
                st.session_state['metadata']=replace_values(metadata,search_txt,replace_txt)

        with c2:
            st.subheader("Structured Data")
            # st.json(json.dumps(st.session_state['metadata']))
            st.session_state['metadata'] = st_ace(
                json.dumps(st.session_state['metadata'],indent=4),
                language="json",
                theme="chaos",
                keybinding="vscode",
                font_size=14,
                tab_size=4,
                show_gutter=True,
                wrap=True,
                auto_update=False,
                readonly=False,
                min_lines=45,
                key="ace",
            )
        


if __name__ == "__main__":
    
    hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
    st.markdown(hide_default_format, unsafe_allow_html=True)
    main()