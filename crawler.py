import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import re

class WebCrawler:
    def __init__(self, start_url):
        # Initialize the crawler with a start URL
        self.start_url = start_url
        self.base_domain = urlparse(start_url).netloc
        self.visited_urls = set()
        # Word -> {url: frequency}
        self.index = defaultdict(lambda: defaultdict(int))
        # Store page titles for better search results
        self.page_titles = {}
    
    def is_valid_url(self, url):
        """Check if URL belongs to the same domain and hasn't been visited"""
        parsed = urlparse(url)
        return (parsed.netloc == self.base_domain and 
                url not in self.visited_urls)
    
    def extract_text_and_links(self, html_content, current_url):
        """Extract text content and links from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Store the page title
        title = soup.find('title')
        if title:
            self.page_titles[current_url] = title.get_text().strip()
        
        # Extract text content (excluding script and style elements)
        for script in soup(['script', 'style']):
            script.decompose()
            
        # Get text from specific content areas with higher weight
        main_content = ""
        for tag in ['main', 'article', 'div', 'p']:
            for element in soup.find_all(tag):
                main_content += " " + element.get_text()
        
        # Extract all links and convert to absolute URLs
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(current_url, href)
                links.append(absolute_url)
        
        return main_content, links
    
    def process_text(self, text):
        """Process text content into words"""
        # Convert to lowercase and split into words
        words = re.findall(r'\w+', text.lower())
        return words
    
    def crawl(self):
        """Start crawling from the initial URL"""
        urls_to_visit = [self.start_url]
        
        while urls_to_visit:
            current_url = urls_to_visit.pop(0)
            
            if not self.is_valid_url(current_url):
                continue
                
            try:
                # Fetch and process the page
                response = requests.get(current_url)
                
                # Only process HTML responses
                if 'text/html' not in response.headers.get('content-type', ''):
                    continue
                    
                self.visited_urls.add(current_url)
                
                # Extract text and links
                text_content, links = self.extract_text_and_links(
                    response.text, current_url)
                
                # Process text and update index with word frequencies
                words = self.process_text(text_content)
                # Count word frequencies for this page
                word_counts = {}
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
                
                # Update the index with word frequencies
                for word, count in word_counts.items():
                    self.index[word][current_url] = count
                
                # Add new links to visit
                urls_to_visit.extend(
                    [url for url in links if url not in self.visited_urls])
                    
            except Exception as e:
                print(f"Error processing {current_url}: {e}")
    
    def search(self, words):
        """
        Search for pages containing all words in the list.
        Returns a list of URLs that contain all the search words.
        
        Args:
            words (list): List of words to search for
            
        Returns:
            list: List of URLs containing all search words
        """
        if not words:
            return []
            
        # Convert search words to lowercase
        words = [word.lower() for word in words]
        
        # Get URLs containing each word
        url_sets = []
        for word in words:
            urls = set(self.index[word].keys())
            url_sets.append(urls)
            
        # Find intersection of all URL sets
        if url_sets:
            result_urls = url_sets[0]
            for urls in url_sets[1:]:
                result_urls &= urls
            return sorted(list(result_urls))
        
        return []

def main():
    """Interactive testing of the WebCrawler"""
    # Create crawler instance
    start_url = "https://vm009.rz.uos.de/crawl/index.html"
    crawler = WebCrawler(start_url)
    
    # Crawl the website
    print("Starting crawl...")
    crawler.crawl()
    print(f"Crawl complete. Visited {len(crawler.visited_urls)} pages")
    
    # Interactive search
    print("\nEnter words to search (separated by spaces), or 'quit' to exit")
    while True:
        user_input = input("\nSearch words: ").strip()
        
        if user_input.lower() == 'quit':
            break
            
        # Split input into words and remove empty strings
        search_words = [word for word in user_input.split() if word]
        
        # Perform search
        print(f"\nSearching for: {search_words}")
        results = crawler.search(search_words)
        
        # Display results
        print(f"Found {len(results)} pages:")
        for url in results:
            print(f"  - {url}")
            
    print("\nGoodbye!")

if __name__ == "__main__":
    main()