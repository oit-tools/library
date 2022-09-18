import json

import scraping


def main():
    result = scraping.Library().get()

    with open("library.json", "w") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
