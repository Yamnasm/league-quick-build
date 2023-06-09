import arg_parser
import difflib, requests, logging, json

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, format= "%(levelname)-8s :: %(message)s")

with open("metasrc_paths.json", "r") as file:
    PATHS = json.load(file)

class Champion:
    def __init__(self, champ, gamemode, role):
        self.name = champ
        self.gamemode = gamemode
        self.role = role
        self.page = self._get_champ_page()
        self.truename = self._get_true_name()
        self.runes = self._get_runes()
        self.starting_items = self._get_starting_items()
        self.items = self._get_items()
        self.skills = self._get_skill_order()

    def _get_champ_page(self):
        if self.gamemode == "5v5":
            page = requests.get(f"https://www.metasrc.com/{self.gamemode}/champion/{self.name}/{self.role}")
        elif self.gamemode == "aram":
            page = requests.get(f"https://www.metasrc.com/{self.gamemode}/champion/{self.name}")
        logging.debug(f"Loaded {self.name}'s champion page.")
        return BeautifulSoup(page.content, "html.parser")

    def _get_true_name(self):
        true_name_search = self.page.select(PATHS["truename"])[0]
        r1 = true_name_search.text.replace("Best ", "")
        r2 = r1.replace(" Summoner Spells", "")
        logging.debug(f"Loaded true-name of {self.name}")
        return r2

    def _get_items(self):
        item_build_title = self.page.select(PATHS["items"])[0]
        build_items = item_build_title.parent.find_all("div")
        champ_items = []
        for obj in build_items:
            result = obj.find_all("img", class_="lozad")
            if result:
                champ_items.append(result[0]["alt"])
        logging.debug(f"Loaded {self.truename}'s Items.")
        return list(dict.fromkeys(champ_items))

    def _get_starting_items(self):
        item_build_title = self.page.select(PATHS["startingitems"])[0]
        start_items = item_build_title.parent.find("div", class_="_dcqhsp")
        result = start_items.find_all("img", class_="lozad")
        logging.debug(f"Loaded {self.truename}'s Starting Items.")
        return [r["alt"] for r in result]

    def _get_runes(self):
        rune_title = self.page.select(PATHS["runes"])[0]
        rune_list = rune_title.find_all("div", class_="_g9pb7k")

        champ_runes = []
        for obj in rune_list[0]:
            result = obj.find_all("image", class_="lozad")
            for r in result:
                champ_runes.append(r["data-xlink-href"].split("/")[-1][:-4])
        champ_runes = self._runes_lookup(champ_runes)
        logging.debug(f"Loaded {self.truename}'s Runes.")
        return champ_runes
    
    def _runes_lookup(self, runes_list):
        with open("runes_lookup.json", "r") as file:
            runes_lookup_dict = json.load(file)

        sanitised_runes_list = []
        for item in runes_list:
            if item in runes_lookup_dict:
                sanitised_runes_list.append(runes_lookup_dict[item])
            else:
                sanitised_runes_list.append(item)
        return sanitised_runes_list
    
    def _get_skill_order(self):
        skill_order_title = self.page.select(PATHS["skillorder"])[0]
        skill_order = skill_order_title.parent.find_all("td")
        skill_table = []
        for i, s in enumerate(skill_order):
            if (i/19).is_integer():
                continue
            else:
                skill_table.append(s)
        logging.debug(f"Loaded {self.truename}'s Skill Table.")
        return skill_table

def get_list_of_champs(gamemode):
    page = requests.get(f"https://www.metasrc.com/lol/{gamemode}")
    HTML_content = BeautifulSoup(page.content, "html.parser")

    class_suffix = ""
    
    if gamemode == "aram":
        class_suffix = "c8xw44"
    elif gamemode == "5v5":
        class_suffix = "yq1p7n"

    class_name = f"_95ecnz champion-grid-item _v0k26j _{class_suffix}"

    results = HTML_content.find_all(class_= class_name)
    list_of_champs = []
    for r in results:
        list_of_champs.append(list(dict.fromkeys(r["data-search-terms-like"].lower().split("|"))))
    logging.debug(f"Loaded {len(list_of_champs)} champions.")
    return list_of_champs

def search_list_of_champs(searchterm, gamemode):
    logging.debug(f"Searching for champion: {searchterm}.")
    champlist = get_list_of_champs(gamemode)
    for champ_alias in champlist:
        if searchterm in champ_alias:
            logging.debug(f"Found champion: {searchterm}.")
            return champ_alias[1] if len(champ_alias) == 2 else champ_alias[0]
    
    logging.debug(f"Champion \"{searchterm}\" not found.")
    return fuzzy_champ_search(searchterm, champlist)

def fuzzy_champ_search(searchterm, champlist):
    logging.debug(f"Fuzzy searching for champion: {searchterm}.")
    flat_champlist = sum(champlist, [])
    search_results = []
    for champ_alias in flat_champlist:
        ratio = difflib.SequenceMatcher(None, searchterm, champ_alias).ratio()
        search_results.append([champ_alias, ratio])
    search_results = sorted(search_results, key=lambda l:l[1], reverse=True)
    print(f"Did you mean: {search_results[0][0]}? ({int(search_results[0][1] * 100)}%)")
    return search_results[0][0]

def print_starting_items(champion):
    print("Starting:")
    for item in champion.starting_items:
        print(f"....... > {item}")

def print_items(champion):
    print("   Items:")
    for item in champion.items[0:-1]:
        print(f"....... > {item}")
    print(f" Elixir > {champion.items[-1]}")

def print_runes(champion):
    print("   Runes:")
    print(f"..... {champion.runes[0]}:")
    for item in champion.runes[1:5]:
        print(f"....... > {item}")
    print(f"..... {champion.runes[5]}:")
    for item in champion.runes[6:8]:
        print(f"....... > {item}")
    print("..... Shards:")
    for item in champion.runes[8:11]:
        print(f"....... > {item}")
    
def print_skill_order(champion):
    print(" Skills:")
    for i, s in enumerate(champion.skills):
        if i % 18 == 0:
            print("")
        if s.text:
            print(f" {s.text} ", end="")
        else:
            print(" - ", end="")
    print("")

def print_entire_build(champion, gamemode, role):
    champion = Champion(champion, gamemode, role)
    print("")
    print_runes(champion)
    print("")
    print_starting_items(champion)
    print_items(champion)
    print("")
    print_skill_order(champion)

def user_input(gamemode, role, champion):
    if gamemode == False:
        gamemode = input("Gamemode (5v5, aram): ").lower()
        if gamemode not in ["5v5", "aram"]:
            print("Invalid Gamemode.")
            return

    if role == False:
        if gamemode == "5v5":
            role = input("Role: ").lower()
            if role not in ["top", "jungle", "mid", "adc", "support"]:
                print("Invalid Role.")
                return

    if champion == False:
        champion = input("Search Champion: ")

    champion = search_list_of_champs(champion.lower(), gamemode)
    print_entire_build(champion, gamemode, role)

def debug():
    print(get_list_of_champs("aram"))

def main():
    args = arg_parser.create_parser()

    gamemode = False
    if args.aram:
        gamemode = "aram"
    if args.summonersrift:
        gamemode = "5v5"
    user_input(gamemode, args.role, args.champ)

if __name__ == "__main__":
    main()