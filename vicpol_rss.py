import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz

def generate_vicpol_rss():
    url = 'https://www.police.vic.gov.au/breaking-news'
    
    # 1. Fetch the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # 2. Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. Initialize the RSS Feed
    fg = FeedGenerator()
    fg.title('Victoria Police - Breaking News')
    fg.link(href=url, rel='alternate')
    fg.description('Latest breaking news and updates from Victoria Police.')
    fg.language('en')
    
    # Define the Melbourne timezone for accurate publishing dates
    melb_tz = pytz.timezone('Australia/Melbourne')
    
    # 4. Find the news articles on the page
    # Note: You may need to inspect the live HTML to refine these CSS selectors.
    # Victoria Police uses Drupal, so articles are typically in a specific list or div class.
    articles = soup.find_all('div', class_='view-content')[0].find_all('div', class_='views-row') if soup.find('div', class_='view-content') else soup.find_all('article')
    
    # Fallback generic parsing if strict classes aren't found
    if not articles:
        # Just grab the main content area links and headers as a fallback
        main_content = soup.find('main')
        articles = main_content.find_all('div', class_='news-item') # adjust class based on inspect element
        
    for article in articles:
        try:
            # Extract Title and Link (usually inside an <h2>, <h3> or <a> tag)
            title_tag = article.find(['h2', 'h3']).find('a') if article.find(['h2', 'h3']) else article.find('a')
            title = title_tag.text.strip()
            
            link = title_tag['href']
            if not link.startswith('http'):
                link = 'https://www.police.vic.gov.au' + link
                
            # Extract Snippet/Description
            # Look for a paragraph tag or a specific snippet div
            desc_tag = article.find('p')
            description = desc_tag.text.strip() if desc_tag else "No description available."
            
            # Extract Date (Usually in a time tag or span)
            date_tag = article.find('time') or article.find('span', class_='date')
            if date_tag:
                date_str = date_tag.text.strip()
                # Parse date string like '27 August 2026'
                try:
                    dt = datetime.strptime(date_str, '%d %B %Y')
                    dt = melb_tz.localize(dt)
                except ValueError:
                    dt = datetime.now(melb_tz) # fallback to now
            else:
                dt = datetime.now(melb_tz)
                
            # 5. Add the entry to the RSS Feed
            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.description(description)
            fe.published(dt)
            
        except AttributeError:
            # Skip items that don't match the expected structure
            continue

    # 6. Save or Output the RSS Feed
    fg.rss_file('vicpol_news.xml')
    print("RSS feed generated successfully as 'vicpol_news.xml'")
    return fg.rss_str(pretty=True)

if __name__ == '__main__':
    generate_vicpol_rss()
