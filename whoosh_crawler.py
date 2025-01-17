import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from pathlib import Path

from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import MultifieldParser
from whoosh import highlight

class WebCrawler:
    def __init__(self, start_url, index_dir="whoosh_index"):
        # Initialize the crawler with a start URL
        self.start_url = start_url
        self.base_domain = urlparse(start_url).netloc
        self.visited_urls = set()
        
        # Create Whoosh schema and index
        self.index_dir = index_dir
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)
            
        self.schema = Schema(
            url=ID(stored=True, unique=True),
            title=TEXT(stored=True),
            content=TEXT(stored=True, chars=True)  # Store content for debugging
        )
        
        # Try to open existing index or create new one
        if os.path.exists(os.path.join(index_dir, 'MAIN_WRITELOCK')):
            os.remove(os.path.join(index_dir, 'MAIN_WRITELOCK'))
        
        if len(os.listdir(index_dir)) > 0:
            self.ix = open_dir(index_dir)
        else:
            self.ix = create_in(index_dir, self.schema)
    
    def is_valid_url(self, url):
        """Check if URL belongs to the same domain and hasn't been visited"""
        parsed = urlparse(url)
        return (parsed.netloc == self.base_domain and 
                url not in self.visited_urls)
    
    def extract_text_and_links(self, html_content, current_url):
        """Extract text content and links from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get the page title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Extract text content (excluding script and style elements)
        for script in soup(['script', 'style']):
            script.decompose()
        text_content = soup.get_text(' ', strip=True)  # Use space separator and strip whitespace
        
        # Extract all links and convert to absolute URLs
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(current_url, href)
                links.append(absolute_url)
        
        return title_text, text_content, links
    
    def crawl(self):
        """Start crawling from the initial URL"""
        urls_to_visit = [self.start_url]
        writer = self.ix.writer()
        
        try:
            while urls_to_visit:
                current_url = urls_to_visit.pop(0)
                
                if not self.is_valid_url(current_url):
                    continue
                    
                try:
                    # Fetch and process the page
                    response = requests.get(current_url)
                    
                    # Only process HTML responses
                    if 'text/html' not in response.headers.get('content-type', '').lower():
                        continue
                        
                    self.visited_urls.add(current_url)
                    
                    # Extract text and links
                    title, content, links = self.extract_text_and_links(
                        response.text, current_url)
                    
                    print(f"Indexing {current_url}")  # Debug print
                    print(f"Title: {title}")  # Debug print
                    
                    # Add document to index
                    writer.add_document(
                        url=current_url,
                        title=title,
                        content=content
                    )
                    
                    # Add new links to visit
                    new_links = [url for url in links if url not in self.visited_urls]
                    urls_to_visit.extend(new_links)
                    
                except Exception as e:
                    print(f"Error processing {current_url}: {e}")
            
            writer.commit()
            print("Indexing complete!")  # Debug print
            
        except Exception as e:
            writer.cancel()
            raise e
    
    def search(self, query_str):
        """
        Search the index for pages matching the query.
        Returns list of (url, title, teaser) tuples.
        """
        with self.ix.searcher() as searcher:
            # Search in both title and content
            parser = MultifieldParser(["title", "content"], self.ix.schema)
            query = parser.parse(query_str)
            
            results = searcher.search(query, limit=None)  # No limit on results
            print(f"Found {len(results)} results for '{query_str}'")  # Debug print
            print(results)  # Debug print

            # Set up the highlighter
            results.fragmenter = highlight.ContextFragmenter(maxchars=200, surround=100)
            results.formatter = highlight.HtmlFormatter(tagname="b", classname="highlight", termclass="term")


            return [
                (hit['url'],
                 hit.get('title', 'Untitled'),
                 hit.highlights("content")
                 )
                    for hit in results]

def main():
    """Example usage of the WebCrawler with Whoosh"""
    # Create crawler
    start_url = "https://vm009.rz.uos.de/crawl/index.html"
    crawler = WebCrawler(start_url)
    
    # Printing for debugging
    print("Starting crawl...")
    crawler.crawl()
    print(f"Crawl complete. Visited {len(crawler.visited_urls)} pages")
    
    # Test search
    print("\nEnter search query, or 'quit' to exit")
    while True:
        query = input("\nSearch query: ").strip()
        
        if query.lower() == 'quit':
            break
            
        # Perform search
        results = crawler.search(query)
        
        # Display results
        print(f"\nFound {len(results)} pages:")
        for url, title, teaser in results:
            print(f"  - {title}")
            print(f"    {url}")
            print(f"    {teaser}")
            
    print("\nGoodbye!")

if __name__ == "__main__":
    main()