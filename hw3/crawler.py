import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urljoin, urlparse
import re
from collections import deque

def crawlerThread(frontier, collection):
    visited = set()
    target_found = False
    allowed_domain = 'www.cpp.edu'

    while frontier and not target_found:
        url = frontier.popleft()  
        if url in visited:
            continue
        visited.add(url)
        print(f"Visiting: {url}")
        try:
            response = urllib.request.urlopen(url)
            content_type = response.headers.get('Content-Type')
            if content_type and 'text/html' not in content_type:
                continue
            html_bytes = response.read()
            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html_bytes, 'html.parser')
            html_text = str(soup)
            # Store the page in MongoDB
            collection.insert_one({'url': url, 'html': html_text, 'target': False})
            # Check if target page
            h1_tags = soup.find_all('h1', class_='cpp-h1')
            for h1 in h1_tags:
                if h1.text.strip() == 'Permanent Faculty':
                    print(f"Target page found: {url}")
                    # Update the MongoDB document to flag the target page
                    collection.update_one({'url': url}, {'$set': {'target': True}})
                    target_found = True
                    break
            if target_found:
                frontier.clear()
                break
            # Else, find all links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Build the absolute URL
                new_url = urljoin(url, href)
                # Discard non-http(s) URLs
                parsed_url = urlparse(new_url)
                if parsed_url.scheme not in ['http', 'https']:
                    continue
                if parsed_url.netloc != allowed_domain:
                    continue
                # Discard resources that are not HTML or SHTML
                if not re.search(r'\.(html|shtml)$', parsed_url.path, re.IGNORECASE):
                    continue
                if new_url not in visited:
                    frontier.append(new_url)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

def main():
    frontier = deque()
    start_url = 'https://www.cpp.edu/sci/computer-science/'
    frontier.append(start_url)
    # Connect to MongoDB
    client = MongoClient()
    db = client['CPP']
    collection = db['pages']
    crawlerThread(frontier, collection)

if __name__ == "__main__":
    main()
