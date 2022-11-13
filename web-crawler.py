from bs4 import BeautifulSoup
import requests
from queue import Queue

REFERENCE_URL = "https://news.ycombinator.com/"
HREF_ELEMENTS = ["a", "link"]
MAX_URL_COUNT = 100

def crawl(input, max):
    """
    Performs a Breadth First Search on the current URL, using its embedded URLS
    as neighbours to continue crawling.
    Returns:
        Set(String)
    """
    num_urls = 1
    visited = {input}
    queue = Queue()
    queue.put(input)

    # Go through the queue of URLs and crawl to retrieve more

    while not queue.empty():
        current = queue.get()
        next_urls = get_next_urls(current)
        for next in next_urls:
            if num_urls >= max:
                return visited

            if next not in visited:
                visited.add(next)
                num_urls += 1
                queue.put(next)

    return visited

def get_next_urls(source):
    """
    Downloads all of the HMTL at the source URL and extracts valid URLs from
    the relevant tags.
    Returns:
        Set(String)

    """
    next_urls = set()
    html = requests.get(source).text
    soup = BeautifulSoup(html, "html.parser")
    base_tag = soup.find("base")
    hrefs = soup.find_all(HREF_ELEMENTS)
    
    for link in hrefs:
        new_url = link.get("href")

        # Ensure we are only adding valid URLs
        if isinstance(new_url, type(None)) or len(new_url) == 0:
            continue
        
        # Skip URLs that we don't want
        if new_url[0] == '#' or new_url[0:7] == "mailto:" or new_url[0:4] == "tel":
            continue

        formatted_url = format_url(source, base_tag, new_url)
        next_urls.add(formatted_url)

    return next_urls

def format_url(source, base_tag, new_url):
    """
    A way to format URLs that reference the host site, or others
    without the http to avoid errors with the requests.
    Returns:
        String
    """

    if isinstance(base_tag, type(None)):
        pair = source.split("//")
        protocol = pair[0]
        remainder = pair[1]
        name = remainder.split("/")[0]
        base_url = protocol + "//" + name
    else:
        base_url = base_tag

    if new_url[0:4] == "http":
        return new_url
    elif new_url[0:2] == "//":
        return "http:" + new_url
    elif new_url[0] == "/":
        return base_url + new_url
    else:
        return base_url + '/' + new_url

def main():
    source = input("Enter source URL:")
    found = crawl(source, MAX_URL_COUNT)
    for item in found:
        print(item)

main()
