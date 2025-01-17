# Web Crawler Search App
This repository contains a Python-based web crawler search application built using Flask, Whoosh, and BeautifulSoup4. The app crawls a given starting URL, indexes the content, and allows users to search through the indexed pages with results including the title, URL, and teaser text.

## Features
- **Web Crawler**: The app uses a simple web crawler to index a starting URL and build a search index using Whoosh.
- **Search Interface**: The app provides a search form for users to input their search terms.
- **Search Results**: The app displays results including the page title, URL, and a teaser text snippet.
- **Error Handling**: The app has proper error handling for both server and search-related errors.

## Prerequisites
Before running this project, make sure you have the following installed:
- Python 3.x
- Flask
- Whoosh
- BeautifulSoup4
- Any other dependencies used in the project

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/AiWebTask2.git
2. **Navigate to the project directory:**
   ```bash
   cd AiWebTask2-main
3. **Install the requirements:**
   ```bash
   pip install requirements.txt
4. **Build the Whoosh index:**
   ```bash
   python whoosh_crawler.py
5. **Run the Flask app:**
   ```bash
   python app.py

Once the application is running, you can access it in your browser at:
http://127.0.0.1:5000/

This is the public address on the server, you can access it in your browser at:
http://vm146.rz.uni-osnabrueck.de/u101/app.wsgi/s
