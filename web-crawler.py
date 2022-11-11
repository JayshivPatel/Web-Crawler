from bs4 import BeautifulSoup
import requests;

INPUT_URL = "https://news.ycombinator.com"
HREF_ELEMENTS = ["a", "area", "base", "link"]
MAX_URL_COUNT = 100


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
        if (url_found[0:6] == "mailto:") or (url_found[0:4] == "tel:") or (url_found[0:4] == "http"):
            return url_found
        else:
            return base_url + '/' + url_found


class SiteCrawlerChild:
    visited = set()

    def __init__(self, base_url, max_urls):
        self.base_url = base_url
        self.max_urls = max_urls

    def get_urls(self):
        new_urls = set()
        html = requests.get(self.base_url).text
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all(HREF_ELEMENTS):
            if self.max_urls <= 0:
                break

            new_url = link.get("href")
            if (new_url not in SiteCrawlerChild.visited) and (new_url not in new_urls):
                formatted_url = SiteCrawlerParent.format(self.base_url, new_url)
                print(formatted_url)
                new_urls.add(formatted_url)
                SiteCrawlerChild.visited.add(formatted_url)
                self.max_urls -= 1

        return new_urls

    @staticmethod
    def clear_visited():
        SiteCrawlerChild.visited = set()


manager = SiteCrawlerParent(INPUT_URL, MAX_URL_COUNT)
urls = manager.crawl()
for url in urls:
    print(url)
print(len(urls))
