# Victoria Police Breaking News RSS Feed

This repository automatically generates a live RSS feed for the [Victoria Police Breaking News](https://www.police.vic.gov.au/breaking-news) webpage. 

Victoria Police does not offer a native RSS feed for their breaking news page, so this project uses a Python script to check the site and build a standard XML feed that can be used in any RSS reader or third-party app.

## How it works

1. The `vicpol_rss.py` script visits the Victoria Police website and reads the latest articles.
2. It formats the titles, descriptions, dates, and links into a standard RSS (`.xml`) format.
3. A **GitHub Actions** workflow (`generate-feed.yml`) acts as an automated timer. It wakes up every 2 hours, runs the Python script, and updates the feed.
4. **GitHub Pages** hosts the resulting file on a public web link.

## How to use the feed

You can plug the live RSS feed directly into your app using this URL:

**`https://<YOUR-GITHUB-USERNAME>.github.io/<YOUR-REPOSITORY-NAME>/vicpol_news.xml`**

*(Note: Replace `<YOUR-GITHUB-USERNAME>` and `<YOUR-REPOSITORY-NAME>` with your actual GitHub details. For example, if your username is `JaneDoe` and this repository is named `vicpol-rss`, your link is `https://JaneDoe.github.io/vicpol-rss/vicpol_news.xml`)*

## Update Frequency

To stay within GitHub's free usage limits and avoid overwhelming the Victoria Police website, this feed is scheduled to check for new updates **every 2 hours**.
