import unittest
from crawler import WebCrawler
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os

# Create simple test HTML files
TEST_PAGES = {
    'index.html': """
        <html>
            <body>
                <a href="page1.html">Link to Page 1</a>
                <a href="page2.html">Link to Page 2</a>
                <p>Welcome to the test page about python programming</p>
            </body>
        </html>
    """,
    'page1.html': """
        <html>
            <body>
                <a href="index.html">Back to Index</a>
                <p>This is a page about python and web development</p>
            </body>
        </html>
    """,
    'page2.html': """
        <html>
            <body>
                <a href="index.html">Back to Index</a>
                <p>This page is about web programming only</p>
            </body>
        </html>
    """
}

class TestWebCrawler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test HTML files
        for filename, content in TEST_PAGES.items():
            with open(filename, 'w') as f:
                f.write(content)
        
        # Start test server
        cls.server = HTTPServer(('localhost', 0), SimpleHTTPRequestHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Get the dynamic port number
        cls.port = cls.server.server_port
        cls.base_url = f'http://localhost:{cls.port}/'
    
    @classmethod
    def tearDownClass(cls):
        # Clean up server and files
        cls.server.shutdown()
        cls.server.server_close()
        for filename in TEST_PAGES.keys():
            os.remove(filename)
    
    def setUp(self):
        self.crawler = WebCrawler(self.base_url + 'index.html')
        self.crawler.crawl()
    
    def test_crawl_all_pages(self):
        """Test that all pages are crawled"""
        expected_pages = len(TEST_PAGES)
        self.assertEqual(len(self.crawler.visited_urls), expected_pages)
    
    def test_search_single_word(self):
        """Test searching for a single word"""
        results = self.crawler.search(['python'])
        self.assertEqual(len(results), 2)  # Should find in index and page1
    
    def test_search_multiple_words(self):
        """Test searching for multiple words"""
        results = self.crawler.search(['python', 'web'])
        self.assertEqual(len(results), 1)  # Should only find in page1
    
    def test_search_no_results(self):
        """Test searching for words that don't exist"""
        results = self.crawler.search(['nonexistent'])
        self.assertEqual(len(results), 0)
    
    def test_search_case_insensitive(self):
        """Test that search is case insensitive"""
        results1 = self.crawler.search(['PYTHON'])
        results2 = self.crawler.search(['python'])
        self.assertEqual(results1, results2)
    
    def test_empty_search(self):
        """Test searching with empty list"""
        results = self.crawler.search([])
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()