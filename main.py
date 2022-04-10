import requests
from bs4 import BeautifulSoup

class Champion:
    def __init__(self, champ, gamemode, role):
        self.name = champ
        self.gamemode = gamemode
        self.role = role
        self.page = self._get_champ_page()
        self.truename = self._get_true_name()
        self.items = self._get_items()
        self.runes = self._get_runes()

    def _get_champ_page(self):
        if self.gamemode == "5v5":
            page = requests.get(f"https://www.metasrc.com/{self.gamemode}/champion/{self.name}/{self.role}")
        elif self.gamemode == "aram":
            page = requests.get(f"https://www.metasrc.com/{self.gamemode}/champion/{self.name}")
        goodsoup = BeautifulSoup(page.content, "html.parser")
        return goodsoup

    def _get_true_name(self):
        true_name_search = self.page.find("h2", class_="_fcukao")
        r1 = true_name_search.text.replace("Best ", "")
        r2 = r1.replace(" Summoner Spells", "")
        return r2

    def _get_items(self):
        item_build_title = self.page.find("h2", class_="_fcukao", text=f"Best {self.truename} Item Build")
        build_items = item_build_title.parent.find_all("div")
        champ_items = []
        for obj in build_items:
            result = obj.find_all("img", class_="lozad")
            if result:
                champ_items.append(result[0]["alt"])
        return list(dict.fromkeys(champ_items))

    def _get_runes(self):
        rune_title = self.page.find("h2", class_="_fcukao", text=f"Best {self.truename} Runes")
        rune_list = rune_title.parent.find_all("div")
        
        return rune_list

def get_list_of_champs(gamemode):
    page = requests.get(f"https://www.metasrc.com/{gamemode}")
    goodsoup = BeautifulSoup(page.content, "html.parser")

    class_name = "_95ecnz champion-grid-item _4swxwm _"
    if gamemode == "aram":
        class_name += "c8xw44"
    elif gamemode == "5v5":
        class_name += "yq1p7n"

    results = goodsoup.find_all(class_= class_name)
    list_of_champs = []
    for r in results:
        list_of_champs.append(list(dict.fromkeys(r["data-search-terms-like"].lower().split("|"))))
    return list_of_champs

def search_list_of_champs(searchterm, gamemode):
    champlist = get_list_of_champs(gamemode)
    for item in champlist:
        if searchterm in item:
            return item[1] if len(item) == 2 else item[0]

def print_items(champion):
    print(f"   Items:")
    for item in champion.items[0:-1]:
        print(f"....... > {item}")
    print(f" Elixir > {champion.items[-1]}")

def main():
    gamemode = input("Gamemode (5v5, aram): ").lower()
    if gamemode not in ["5v5", "aram"]:
        print("Invalid Gamemode.")
        return
        
    role = None
    if gamemode == "5v5":
        role = input("Role: ").lower()
        if role not in ["top", "jungle", "mid", "adc", "support"]:
            print("Invalid Role.")
            return

    searchterm = search_list_of_champs(input("Search Champion: ").lower(), gamemode)
    if searchterm == None:
        print("Champion not found.")
        return   
    champion = Champion(searchterm, gamemode, role)
    print_items(champion)

if __name__ == "__main__":
    main()