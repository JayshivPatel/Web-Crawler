import time

from bs4 import BeautifulSoup
import requests;

INPUT_URL = "https://www.freecodecamp.org/news/how-to-substring-a-string-in-python/"
HREF_ELEMENTS = ["a", "link"]
MAX_URL_COUNT = 1000


class SiteCrawlerParent:
    def __init__(self, init_url, max_urls):
        self.init_url = init_url
        self.max_urls = max_urls

        # Clear the previous runs, if applicable
        SiteCrawlerChild.clear_visited()

    def crawl(self):
        previous_urls = {self.init_url}
        sites_remaining = self.max_urls

        while sites_remaining > 0:
            current_urls = set()

            # Go through the previously found URLs and generate children, to crawl and retrieve more urls
            for previous_url in previous_urls:
                if sites_remaining <= 0:
                    break

                child = SiteCrawlerChild(previous_url, sites_remaining)
                urls_found = child.get_urls()
                current_urls.update(urls_found)
                sites_remaining -= len(urls_found)

            previous_urls = current_urls

        return SiteCrawlerChild.visited

    @staticmethod
    def reset_children():
        SiteCrawlerChild.clear_visited()

    @staticmethod
    def format(base_url, url_found):
        if (url_found[0:7] == "mailto:") or (url_found[0:4] == "tel:") or (url_found[0:4] == "http"):
            return url_found
        else:
            return base_url + '/' + url_found

    @staticmethod
    def extract_base_url(full_url):
        pair = full_url.split("//")
        protocol = pair[0]
        remainder = pair[1]
        name = remainder.split("/")[0]
        return protocol + "//" + name


class SiteCrawlerChild:
    visited = set()

    def __init__(self, url_to_crawl, max_urls):
        self.url_to_crawl = url_to_crawl
        self.max_urls = max_urls

    def get_urls(self):
        new_urls = set()
        html = requests.get(self.url_to_crawl).text
        soup = BeautifulSoup(html, "html.parser")
        base_tag = soup.find("base")

        if isinstance(base_tag, type(None)):
            copy = self.url_to_crawl
            pair = copy.split("//")
            protocol = pair[0]
            remainder = pair[1]
            name = remainder.split("/")[0]
            base_url = protocol + "//" + name
        else:
            base_url = base_tag.get()

        for link in soup.find_all(HREF_ELEMENTS):
            # Make sure we don't exceed the number or URLs we have to find
            if self.max_urls <= 0:
                break

            new_url = link.get("href")

            # Ensure we are only checking for valid urls
            if isinstance(new_url, type(None)):
                continue

            if new_url not in SiteCrawlerChild.visited:
                formatted_url = SiteCrawlerParent.format(base_url, new_url)
                new_urls.add(formatted_url)
                SiteCrawlerChild.visited.add(formatted_url)
                self.max_urls -= 1

        return new_urls

    @staticmethod
    def clear_visited():
        SiteCrawlerChild.visited = set()


manager = SiteCrawlerParent(INPUT_URL, MAX_URL_COUNT)
urls = manager.crawl()
print("Found " + str(len(urls)) + " unique URLs")
count = 0
for url in urls:
    count += 1
    print(str(count) + ": " + url)
