import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz
import re

def generate_vicpol_rss():
    url = 'https://www.police.vic.gov.au/breaking-news'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 1. Fetch the webpage
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2. Initialize the RSS Feed
    fg = FeedGenerator()
    fg.title('Victoria Police - Breaking News')
    fg.link(href=url, rel='alternate')
    fg.description('Latest breaking news and updates from Victoria Police.')
    fg.language('en')
    
    melb_tz = pytz.timezone('Australia/Melbourne')
    added_urls = set()
    
    # 3. Find the exact Ripple components based on the code you found!
    # We look for all divs that have the 'rpl-search-result__url' class
    for url_div in soup.find_all('div', class_=lambda c: c and 'rpl-search-result__url' in c):
        
        # The parent container holds the title, date, and description
        parent = url_div.parent
        if not parent:
            continue
            
        # Extract the raw link text you found
        raw_link = url_div.get_text(strip=True)
        if not raw_link:
            continue
            
        # Ensure it is a complete URL
        full_link = 'https://' + raw_link if not raw_link.startswith('http') else raw_link
        
        if full_link in added_urls:
            continue
            
        # 4. Extract the Title (usually an <a> tag inside the parent)
        title_tag = parent.find('a')
        title = title_tag.get_text(strip=True) if title_tag else "Victoria Police Update"
        
        # 5. Extract the text block to find the Date and Description
        text_content = parent.get_text(separator=' | ', strip=True)
        date_str = ""
        description = ""
        
        # Look for a spelled-out date (e.g., 27 August 2026)
        date_match = re.search(r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', text_content, re.IGNORECASE)
        
        if date_match:
            date_str = date_match.group(0)
            
        # Split the text apart and grab the longest sentence for the description
        parts = [p.strip() for p in text_content.split(' | ') if p.strip()]
        for part in parts:
            if len(part) > 40 and part != title and part != raw_link and part != date_str:
                description = part
                break
                
        # 6. Parse the date so RSS readers understand it
        dt = datetime.now(melb_tz)
        if date_str:
            try:
                parsed_dt = datetime.strptime(date_str, '%d %B %Y')
                dt = melb_tz.localize(parsed_dt)
            except ValueError:
                pass
                
        # 7. Add the article to the feed!
        fe = fg.add_entry()
        fe.id(full_link)
        fe.title(title)
        fe.link(href=full_link)
        fe.description(description if description else "Read the full update on the Victoria Police website.")
        fe.published(dt)
        
        added_urls.add(full_link)

    # Save the file
    fg.rss_file('vicpol_news.xml')
    print(f"Generated RSS feed with {len(added_urls)} items.")

if __name__ == '__main__':
    generate_vicpol_rss()
