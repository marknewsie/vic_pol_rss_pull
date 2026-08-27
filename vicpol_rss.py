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
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2. Initialize the RSS Feed
    fg = FeedGenerator()
    fg.title('Victoria Police - Breaking News')
    fg.link(href=url, rel='alternate')
    fg.description('Latest breaking news and updates from Victoria Police.')
    fg.language('en')
    
    melb_tz = pytz.timezone('Australia/Melbourne')
    
    # 3. Find all links on the main page
    main_content = soup.find('main') or soup
    links = main_content.find_all('a', href=True)
    
    added_urls = set()
    
    # 4. Filter the links to find the actual news articles
    for a in links:
        href = a['href']
        title = a.text.strip()
        
        # Skip short links (like "Next" or "Home") and non-article links
        if len(title) < 15 or 'breaking-news' in href or href.startswith('#'):
            continue
            
        # Make sure the URL is complete
        full_link = href if href.startswith('http') else 'https://www.police.vic.gov.au' + href
        
        # Don't add the same article twice
        if full_link in added_urls:
            continue
            
        # 5. Look near the link for the date and snippet
        parent = a.find_parent('div')
        description = ""
        date_str = ""
        
        if parent:
            text_blocks = parent.get_text(separator='|', strip=True).split('|')
            for block in text_blocks:
                # Look for a date pattern like '27 August 2026'
                if re.match(r'\d{1,2}\s+[A-Za-z]+\s+\d{4}', block):
                    date_str = block
                # Look for a longer sentence that isn't the title (the snippet)
                elif len(block) > 50 and block != title:
                    description = block
                    
        # Parse the date so RSS readers understand it
        dt = datetime.now(melb_tz)
        if date_str:
            try:
                clean_date = re.sub(r'\s+', ' ', date_str).strip()
                parsed_dt = datetime.strptime(clean_date, '%d %B %Y')
                dt = melb_tz.localize(parsed_dt)
            except ValueError:
                pass
                
        # 6. Add it to the feed!
        fe = fg.add_entry()
        fe.id(full_link)
        fe.title(title)
        fe.link(href=full_link)
        fe.description(description if description else "No description available.")
        fe.published(dt)
        added_urls.add(full_link)

    # Save the file
    fg.rss_file('vicpol_news.xml')
    print(f"Generated RSS feed with {len(added_urls)} items.")

if __name__ == '__main__':
    generate_vicpol_rss()
