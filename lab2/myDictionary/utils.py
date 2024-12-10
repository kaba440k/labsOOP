def add_to_file(word1: str, word2: str):
    with open("file.txt", "a", encoding="utf-8") as file:
        file.write(word1 + "-" + word2 + "\n")


def read_from_file():
    with open("file.txt", "r", encoding="utf-8") as file:
        lines = file.read().splitlines()

    words1 = []
    words2 = []

    for line in lines:
        word1, word2 = line.split("-")
        words1.append(word1)
        words2.append(word2)  # Добавляем перевод как строку

    return words1, words2