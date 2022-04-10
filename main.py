import requests
from bs4 import BeautifulSoup

class Champion:
    def __init__(self, champ):
        self.name = champ
        self.page = self._get_champ_page()
        self.truename = self._get_true_name()
        self.items = self._retrieve_items()

    def _get_champ_page(self):
        URL = f"https://www.metasrc.com/aram/champion/{self.name}"
        page = requests.get(URL)
        soop = BeautifulSoup(page.content, "html.parser")
        return soop

    def _get_true_name(self):
        true_name_search = self.page.find("h2", class_="_fcukao")
        r1 = true_name_search.text.replace("Best ", "")
        r2 = r1.replace(" Summoner Spells", "")
        return r2

    def _retrieve_items(self):
        soop = self.page

        item_build_title = soop.find("h2", class_="_fcukao", text=f"Best {self.truename} Item Build")
        build_items = item_build_title.parent.find_all("div")
        champ_items = []
        for obj in build_items:
            result = obj.find_all("img", class_="lozad")
            if result:
                champ_items.append(result[0]["alt"])
        return list(dict.fromkeys(champ_items))

def print_items(champion):
    print(f"   Items:")
    for item in champion.items[0:-1]:
        print(f"....... > {item}")
    print(f" Elixir > {champion.items[-1]}")

def main():
    champion = Champion(input("Champion: "))
    print_items(champion)

if __name__ == "__main__":
    main()