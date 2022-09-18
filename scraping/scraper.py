import time

from bs4 import BeautifulSoup
from playwright.sync_api import Playwright, sync_playwright


class Library:
    def __init__(self):
        self.url = "https://opac2.lib.oit.ac.jp/webopac/BB99305907"
        self.soup = None
        self.result = dict()

    def _run(self, playwright: Playwright) -> str:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(self.url, wait_until="load")
        time.sleep(10)

        try:
            html = page.content()
            self.soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            print(e)
        else:
            self._analyze_contents()
        finally:
            page.close()
            browser.close()
            context.close()

    def _analyze_contents(self):
        # 書籍名を取得
        self.result["title"] = (self.soup.find(class_="opac_book_title").text).replace(
            "\n", ""
        )
        # 書影を取得
        self.result["image"] = (
            self.soup.find(class_="opac_book_img").find("img").get("src")
        )

    def get(self):
        with sync_playwright() as playwright:
            self._run(playwright)

        return self.result
