import difflib
import logging
import requests
from bs4 import BeautifulSoup
import LQB_args
from champion import Champion

logging.basicConfig(
    level=logging.INFO,
    format= "%(levelname)-8s :: %(message)s")

# cannot use the ddragon import in directory due to differences on metasrc
def get_champ_list():
    page = requests.get(f"https://www.metasrc.com/lol/")
    HTML_content = BeautifulSoup(page.content, "html.parser")

    class_name = f"_95ecnz champion-grid-item _v0k26j _yq1p7n"

    results = HTML_content.find_all(class_= class_name)
    list_of_champs = []

    for r in results:
        aliases = list(dict.fromkeys(r["data-search-terms-like"].lower().split("|")))
        list_of_champs.append(aliases)
    
    logging.debug(f"Loaded {len(list_of_champs)} champions.")
    return list_of_champs

def search_champ_list(searchterm):
    logging.debug(f"Searching for champion: {searchterm}.")
    champlist = get_champ_list()

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
    found_champ = search_results[0][0]
    diff_percent = int(search_results[0][1] * 100)
    print(f"Did you mean: {found_champ}? ({diff_percent}%)")
    return found_champ

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

def print_starting_items(champion):
    print("Starting:")
    for item in champion.starting_items:
        print(f"....... > {item}")

def print_items(champion):
    print("   Items:")
    for item in champion.items[0:-1]:
        print(f"....... > {item}")
    print(f" Elixir > {champion.items[-1]}")
    
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
        gamemode = input("Gamemode (5v5, aram): ").lower().strip()
        if gamemode not in ["5v5", "aram"]:
            print("Invalid Gamemode.")
            return

    if role == False:
        if gamemode == "5v5":
            role = input("Role: ").lower().strip()
            if role not in ["top", "jungle", "mid", "adc", "support"]:
                print("Invalid Role.")
                return

    if champion == False:
        champion = input("Search Champion: ")

    champion = search_champ_list(champion.lower())
    print_entire_build(champion, gamemode, role)

def main():
    args = LQB_args.create_parser()

    gamemode = False
    if args.aram:
        gamemode = "aram"
    if args.summonersrift:
        gamemode = "5v5"
    user_input(gamemode, args.role, args.champ)

if __name__ == "__main__":
    main()