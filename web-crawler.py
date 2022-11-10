from bs4 import BeautifulSoup
import requests;

INPUT_URL = "https://news.ycombinator.com"
HREF_ELEMENTS = ["a", "area", "base", "link"]
MAX_URL_COUNT = 100

class site_crawler:
    def __init__(self, url, visited):
        self.url = url
        self.visited = visited
    
    def get_urls(self):
        new_urls = set()
        html = requests.get(self.url).text
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all(HREF_ELEMENTS):
            url = link.get("href")
            if (url not in self.visited) and (url not in new_urls):
                new_urls.add(url)
        return new_urls

def main():
    visited = set()
    new_urls = {INPUT_URL} 
    
    while len(visited) < MAX_URL_COUNT:
        urls_at_depth = set()
        for url in new_urls:
            child = site_crawler(url, visited)
            urls_found = child.get_urls()
            visited.update(urls_found)
            urls_at_depth.update(urls_found)
        new_urls = urls_at_depth
            
    print(visited)

main()



