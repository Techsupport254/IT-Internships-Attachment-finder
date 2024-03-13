import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from googlesearch import search
from bs4 import BeautifulSoup
import re


def setup_driver():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    return driver


def find_opportunities(location, search_type):
    query = f"{search_type} opportunities in {location}"
    urls = []
    for j in search(query):
        urls.append(j)
        if len(urls) == 10:
            break
    return urls


location_pattern = re.compile(r'\bin\s+([A-Za-z0-9, ]+)[,.]')
date_pattern = re.compile(r'\bfrom\s+([A-Za-z0-9, ]+)\b')


def extract_location(soup):
    location_matches = location_pattern.findall(soup.get_text())
    return location_matches[0].strip() if location_matches else 'Location not found'


def extract_date(soup):
    date_matches = date_pattern.findall(soup.get_text())
    return date_matches[0].strip() if date_matches else 'Date not found'


def extract_info(urls):
    with setup_driver() as driver:
        opportunities = []
        for url in urls:
            try:
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                location = extract_location(soup)
                date = extract_date(soup)
                image_url = soup.find('meta', property='og:image')['content'] if soup.find(
                    'meta', property='og:image') else 'No image available'
                opportunities.append((url, location, date, image_url))
            except Exception as e:
                st.error(f"An error occurred while processing {url}: {e}")
    return opportunities


st.sidebar.title('Opportunity Finder Settings')
st.sidebar.info('This is an Internship/Attachment finder that helps students looking for opportunities to search easily through the internet while minimizing the time required.')

search_type = st.sidebar.selectbox(
    'Select Type', ['Internship', 'Industrial Attachment'])
location = st.sidebar.text_input('Enter a city:', 'Nairobi')

if st.sidebar.button(f'Find {search_type}s'):
    with st.spinner(f'Searching for {search_type.lower()}s...'):
        urls = find_opportunities(location, search_type)
        opportunities = extract_info(urls)
        if opportunities:
            st.success(
                f'Found the following {search_type.lower()} opportunities:')
            for url, loc, date, img_url in opportunities:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if img_url != 'No image available':
                        st.image(img_url, width=150)
                    else:
                        st.write("No image available")
                with col2:
                    st.markdown(f"*Description:* {loc}, *Date:* {date}")
                    st.markdown(f"*URL:* [Link]({url})")
                st.markdown('---')
        else:
            st.error(f'No {search_type.lower()}s found.')
else:
    st.info('Please select the category and location to search for the attachment or internship opportunities.')
