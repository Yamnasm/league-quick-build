import logging
import json
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format= "%(levelname)-8s :: %(message)s")

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
        r = true_name_search.text.replace("Best ", "")
        truename = r.replace(" Summoner Spells", "")
        logging.debug(f"Loaded true-name of {self.name}: {truename}.")
        return truename

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