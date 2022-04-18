import difflib
import requests
from bs4 import BeautifulSoup

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
        return BeautifulSoup(page.content, "html.parser")

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

    def _get_starting_items(self):
        item_build_title = self.page.find("h2", class_="_fcukao", text=f"Best {self.truename} Starting Items")
        start_items = item_build_title.parent.find("div", class_="_dcqhsp")
        result = start_items.find_all("img", class_="lozad")
        return [r["alt"] for r in result]

    def _get_runes(self):
        rune_title = self.page.find("h2", class_="_fcukao", text=f"Best {self.truename} Runes").parent
        rune_list = rune_title.find_all("div", class_="_g9pb7k")

        champ_runes = []
        for obj in rune_list[0]:
            result = obj.find_all("image", class_="lozad")
            for r in result:
                champ_runes.append(r["data-xlink-href"].split("/")[-1][:-4])
            
        champ_runes = self._runes_lookup(champ_runes)
        return champ_runes
    
    def _runes_lookup(self, runes_list):
        runes_lookup_table = {
            "8000": "Precision",
            "8100": "Domination",
            "8200": "Sorcery",
            "8300": "Inspiration",
            "8400": "Resolve",

            # Precision
            "conqueror": "Conqueror",
            "triumph": "Triumph",
            "legendtenacity": "Legend: Tenacity",
            "laststand": "Last Stand",
            "legendalacrity": "Legend: Alacrity",
            "coupdegrace": "Coup de Grace",
            "presenceofmind": "Presence of Mind",
            "lethaltempotemp": "Lethal Tempo",
            "cutdown": "Cut Down",
            "fleetfootwork": "Fleet Footwork",
            "legendbloodline": "Legend: Bloodline",
            "presstheattack": "Press The Attack",
            "overheal": "Overheal",

            # Domination
            "greenterror_tasteofblood": "Taste of Blood",
            "treasurehunter": "Treasure Hunter",
            "cheapshot": "Cheap Shot",
            "ultimatehunter": "Ultimate Hunter",
            "eyeballcollection": "Eyeball Collection",
            "relentlesshunter": "Relentless Hunter",
            "hailofblades": "Hail of Blades",
            "suddenimpact": "Sudden Impact",
            "electrocute": "Electrocute",
            "darkharvest": "Dark Harvest",
            "ghostporo": "Ghost Poro",
            "ingenioushunter": "Ingenious Hunter",
            "predator": "Predator",
            "zombieward": "Zombie Ward",

            # Sorcery
            "arcanecomet": "Arcane Comet",
            "manaflowband": "Manaflow Band",
            "transcendence": "Transcendence",
            "scorch": "Scorch",
            "gatheringstorm": "Gathering Storm",
            "phaserush": "Phase Rush",
            "summonaery": "Summon Aery",
            "absolutefocus": "Absolute Focus",
            "celerity": "Celerity",
            "nimbuscloak": "Nimbus Cloak",
            "nullifyingorb": "Nullifying Orb",
            "waterwalking": "Water Walking",

            # Inspiration
            "cosmicinsight": "Cosmic Insight",
            "biscuitdelivery": "Biscuit Delivery",
            "firststrike": "First Strike",
            "futuresmarket": "Futures Market",
            "glacialaugment": "Glacial Augment",
            "hextechflashtraption": "Hextech Flashtraption",
            "magicalfootwear": "Magical Footwear",
            "miniondematerializer": "Minion Dematerializer",
            "perfecttiming": "Perfect Timing",
            "timewarptonic": "Time Warp Tonic",
            "approachvelocity": "Approach Velocity",

            # Resolve
            "veteranaftershock": "Aftershock",
            "demolish": "Demolish",
            "conditioning": "Conditioning",
            "overgrowth": "Overgrowth",
            "revitalize": "Revitalize",
            "secondwind": "Second Wind",
            "unflinching": "Unflinching",
            "boneplating": "Bone Plating",
            "fontoflife": "Font of Life",
            "graspoftheundying": "Grasp of the Undying",
            "guardian": "Guardian",

            # Shards
            "statmodsadaptiveforceicon": "Adaptive Force",
            "statmodsarmoricon": "Armor",
            "statmodsattackspeedicon": "Attack Speed",
            "statmodscdrscalingicon": "Cooldown Reduction",
            "statmodshealthscalingicon": "Health"
        }
        sanitised_runes_list = []
        for item in runes_list:
            if item in runes_lookup_table:
                sanitised_runes_list.append(runes_lookup_table[item])
            else:
                sanitised_runes_list.append(item)
        return sanitised_runes_list
    
    def _get_skill_order(self):
        skill_order_title = self.page.find("h2", class_="_fcukao", text=f"Best {self.truename} Skill Order")
        skill_order = skill_order_title.parent.find_all("td")
        skill_table = []
        for i, s in enumerate(skill_order):
            if (i/19).is_integer():
                continue
            else:
                skill_table.append(s)
        return skill_table

def get_list_of_champs(gamemode):
    page = requests.get(f"https://www.metasrc.com/{gamemode}")
    HTML_content = BeautifulSoup(page.content, "html.parser")

    class_name = "_95ecnz champion-grid-item _4swxwm _"
    if gamemode == "aram":
        class_name += "c8xw44"
    elif gamemode == "5v5":
        class_name += "yq1p7n"

    results = HTML_content.find_all(class_= class_name)
    list_of_champs = []
    for r in results:
        list_of_champs.append(list(dict.fromkeys(r["data-search-terms-like"].lower().split("|"))))
    return list_of_champs

def search_list_of_champs(searchterm, gamemode):
    champlist = get_list_of_champs(gamemode)
    for champ_alias in champlist:
        if searchterm in champ_alias:
            return champ_alias[1] if len(champ_alias) == 2 else champ_alias[0]
    return fuzzy_champ_search(searchterm, champlist)

def fuzzy_champ_search(searchterm, champlist):
    flat_champlist = sum(champlist, [])
    search_results = []
    for champ_alias in flat_champlist:
        champ = champ_alias
        ratio = difflib.SequenceMatcher(None, searchterm, champ_alias).ratio()
        search_results.append([champ, ratio])
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
    champion = Champion(searchterm, gamemode, role)
    print("")
    print_runes(champion)
    print("")
    print_starting_items(champion)
    print_items(champion)
    print("")
    print_skill_order(champion)

if __name__ == "__main__":
    main()