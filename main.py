from playwright.sync_api import Playwright, sync_playwright
import time
from bs4 import BeautifulSoup
import unicodedata
import json

class Library:
    def __init__(self):
        self.url = "https://opac2.lib.oit.ac.jp/webopac/BB50280486"
        self.soup = None
        self.table_list = list()
        self.result = dict()

    def main(self):
        with sync_playwright() as playwright:
            self.run(playwright)

    def run(self,playwright: Playwright) -> str:
        # ブラウザを開く
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # ページを開く
        page.goto(self.url, wait_until="load")

        # ページの読み込みのため、スリープ
        time.sleep(10)

        # 要素を取得
        html = page.content()

        # BeautifulSoupで解析
        self.soup = BeautifulSoup(html, "html.parser")

        # 解析する
        self.analyze_contents()

        print(json.dumps(self.result, indent=4, ensure_ascii=False))

        # 終了
        page.close()
        browser.close()
        context.close()

    def analyze_contents(self):
        self.analyze_synopsis_contents() # あらすじと目次
        # self.analyze_table() # その他情報
        self.analyze_holdings() # 所蔵館

    def analyze_synopsis_contents(self):
        block_body_small = list()

        for block_body_middle in self.soup.find_all(class_="opac_block_body_middle"):
            for opac_block_body_small in block_body_middle.find_all(
                class_="opac_block_body_small"
            ):
                block_body_small.append(opac_block_body_small)

        try:
            synopsis = unicodedata.normalize("NFKC",(block_body_small[0].text).replace("\n", ""))
        except IndexError:
            print("情報の取得に失敗しました\nリトライします")
            self.main()
        contents = block_body_small[1].get_text("@").split("@")

        for i in range(len(contents)):
            contents[i] = unicodedata.normalize("NFKC", contents[i]).replace("\n", "")

        self.result.update({"synopsis": synopsis, "contents": contents})

    def analyze_table(self):
        key_list = list()
        value_list = list()
        table = list()

        for tr in self.table_list[1].find_all("tr"):
            key_list.append((tr.find("th").get_text("@")).replace("\n", ""))
            value_list.append((tr.find("td").get_text("@")).replace("\n", ""))

        response = dict(zip(key_list, value_list))

        self.result.update({"table": table})

        # key_list = [
        #     "no",
        #     "volume_number",
        #     "holding_library",
        #     "position",
        #     "ndc_id",
        #     "book_id",
        #     "reference_only",
        #     "status",
        #     "scheduled_return_date",
        #     "booking",
        #     "title",
        #     "author",
        #     "publisher",
        #     "year",
        #     "bookpage",
        #     "thickness",
        #     "isbn",
        #     "imprint_title",
        #     "quote",
        #     "academic_id",
        #     "language",
        # ]

    def analyze_holdings(self):
        tr_list = list()
        td_list = list()
        key_list = list()
        value_list = list()
        holdings = list()

        key_list = [
            "no",
            "holding_library",
            "position",
            "ndc_id",
            "book_id",
            "reference_only",
            "status",
            "scheduled_return_date",
            "booking"
        ]

        # テーブルの中身を取得
        for opac_block_middle in self.soup.find_all(class_="opac_block_middle"):
            for table in opac_block_middle.find_all("table"):
                self.table_list.append(table)

        for tr in self.table_list[0].find_all("tr"):
            tr_list.append(tr)

        for i in range(len(tr_list[1:])):
            td_list.append(tr_list[i + 1].text.split("\n"))

        for i in range(len(td_list)):
            value_list.append(td_list[i][3])  # No
            value_list.append(td_list[i][7])  # 所属館
            value_list.append(td_list[i][9])  # 配置場所
            value_list.append(td_list[i][12]) # 請求番号
            value_list.append(td_list[i][14]) # 資料ID
            value_list.append(td_list[i][16]) # 禁帯出区分
            value_list.append(td_list[i][17]) # 状態
            value_list.append(td_list[i][18]) # 返却予定日
            value_list.append(td_list[i][20]) # 予約

            holdings.append(dict(zip(key_list, value_list)))
            value_list.clear()

        self.result.update({"holdings": holdings})

if __name__ == "__main__":
    lib = Library()
    lib.main()