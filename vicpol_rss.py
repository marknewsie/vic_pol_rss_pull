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
    
    # 3. Find all <a> tags that look like news headlines
    for a in soup.find_all('a', href=True):
        title = a.get_text(strip=True)
        href = a['href']
        
        # A headline is usually at least 3 words and 15 characters long
        if len(title.split()) < 3 or len(title) < 15:
            continue
            
        # Ignore pagination buttons and generic links
        if 'breaking-news' in href or href.startswith('#') or '?' in href:
            continue
            
        # Ensure the link is a full URL
        full_link = href if href.startswith('http') else 'https://www.police.vic.gov.au' + href
        
        if full_link in added_urls:
            continue
            
        # 4. Search the surrounding code for the date and description
        parent = a.parent
        date_str = ""
        description = ""
        
        # Walk up the HTML tree up to 4 levels to find the container holding the text
        for _ in range(4):
            if not parent: break
            
            # Extract all text in this block, separated by a distinct character
            text_content = parent.get_text(separator=' | ', strip=True)
            
            # Look for a spelled-out date (e.g., 27 August 2026)
            date_match = re.search(r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', text_content, re.IGNORECASE)
            
            if date_match:
                date_str = date_match.group(0)
                
                # The description is usually the longest piece of text in this block that isn't the title
                parts = [p.strip() for p in text_content.split(' | ') if p.strip()]
                for part in parts:
                    if len(part) > 50 and part != title and part != date_str:
                        description = part
                        break
                
                # Stop walking up the tree once we find the date
                break
                
            parent = parent.parent
            
        # 5. Parse the date so RSS readers understand it
        dt = datetime.now(melb_tz)
        if date_str:
            try:
                parsed_dt = datetime.strptime(date_str, '%d %B %Y')
                dt = melb_tz.localize(parsed_dt)
            except ValueError:
                pass
                
        # 6. Add the article to the feed!
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
