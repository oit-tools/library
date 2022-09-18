import json

import scraping


def main():
    url = "https://opac2.lib.oit.ac.jp/webopac/BB99305907"
    result = scraping.Library().get(url)

    with open("book.json", "w") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
