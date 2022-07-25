import leagueQB, random

def random_champ(blacklist, champ_pool):
    while True:
        result = random.choice(champ_pool)
        if result not in blacklist:
            return result

def import_champlist():
    champlist = leagueQB.get_list_of_champs("5v5")
    clean_champlist = []
    for champ in champlist:
        if champ[0] == "wukong": # why the fuck did they call wukong "monkeyking"??
            clean_champlist.append(champ[0])
        else: 
            if len(champ) > 1:
                clean_champlist.append(champ[1])
            else:
                clean_champlist.append(champ[0])
    return clean_champlist  

def pick_champion():
    with open("lol coop used champions.txt", "r") as file:
        used_champs = [line.strip() for line in file]

    with open("free champions.txt", "r") as file:
        freechamps = [line.strip() for line in file]

    with open("lol champs not owned.txt", "r") as file:
        unowned_champs = [line.strip() for line in file]
    unowned_champs = [c for c in unowned_champs if c not in freechamps]

    blacklist = used_champs + unowned_champs

    champlist = import_champlist()
    return random_champ(blacklist, champlist)

def main():
    champion = pick_champion()
    print(champion)
    if input("Use champ? ").lower() == "yes":
        leagueQB.print_entire_build(champion, "5v5", "mid")
        with open("lol coop used champions.txt", "a") as f:
            f.write("\n" + champion)
    
if __name__ == "__main__":
    main()