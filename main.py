def champion_selection(champ):
    return f"https://www.metasrc.com/aram/champion/{champ}"


def main():
    print(champion_selection("aatrox"))

if __name__ == "__main__":
    main()