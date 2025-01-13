import requests
from bs4 import BeautifulSoup

# the base URL for the website
prefix = 'https://www.ikw.uni-osnabrueck.de/en/'

# the initial webpage that the program will visit
start_url = prefix+'home.html'

# the list of acting as a queue of URLs to visit
agenda = [start_url]

# the Crawling loop
while agenda:
    # retrieves and removes the last URL in the list (agenda)
    url = agenda.pop()
    # Logs the URL being fetched for debugging or informational purposes
    print("Get ",url)
    # Sends an HTTP GET request to the URL
    r = requests.get(url)
    # Prints th HTTP response object r and its character encoding
    print(r, r.encoding)
    #Checking the HTTP status
    # Ensures the request was successful
    if r.status_code == 200:
        # Prints the response headers, which might include metadata about the webpage
        print(r.headers)
        # parsing the HTML
        soup = BeautifulSoup(r.content, 'html.parser')
        # Extracting Links
        print(soup.find_all('a'))
        