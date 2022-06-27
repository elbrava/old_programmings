import threading

answers = []


def main():
    global answers
    letters = "qwertyuiopasdfghjklzxcvbn"
    numbers = "1234567890"
    cha_racters = r"`~!@#$%^&*()_+[];''\,./{}:""|<>?"

    _iter = 1
    all_characters = letters + letters.upper() + numbers + cha_racters
    print(_iter)
    with open("keys.text", "w") as fi:
        fi.write("")
    with open("keys.text", "a") as f:
        for key in all_characters:
            answers.append(key)
            f.write(f"\n{key}")
        for _ in range(12):
            threading.Thread(target=mano())


def mano():
    for an in answers:
        threading.Thread(target=amano, args=[all_characters, an])


def amano(all_characters, an):
    for key in all_characters:
        answers.append(an + key)
        f.write(f"\n {an + key}")


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settin
if __name__ == '__main__':
    t = threading.Thread(target=main)
    t.start()
