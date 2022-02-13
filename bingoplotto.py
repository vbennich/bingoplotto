import requests
from bs4 import BeautifulSoup
import json
import threading
import argparse
import matplotlib.pyplot as plt
import os
from atpbar import atpbar


def main(args: argparse.Namespace) -> None:

    threads_nr = 8
    threads = []
    serie = args.serie
    lottnummer = args.lottnummer
    antal = args.antal
    requests_per_thread_distribution = split_integer(antal, threads_nr)
    vinster = {}
    start = lottnummer
    for i in range(threads_nr):
        end = start + requests_per_thread_distribution[i]
        thread = threading.Thread(
            target=lotto_scraper, args=(vinster, serie, start, end)
        )
        threads.append(thread)
        start += requests_per_thread_distribution[i]

    for i in range(len(threads)):
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    zero_filled_serie = str(serie).zfill(4)
    file_name = f"{zero_filled_serie}.json"
    if os.path.exists(file_name):
        os.remove(file_name)
    with open(f"{zero_filled_serie}.json", "w") as file:
        file.write(json.dumps(vinster))

    vinst_list = sorted(vinster.items())
    number_of_wins = len(vinst_list)
    print(f"På de {antal} lotter ni angivit var det {number_of_wins} vinster")
    x, y = zip(*vinst_list)
    plt.plot(x, y, marker="o")
    for i, j in zip(x, y):
        plt.text(i, j + 0.5, "({}, {})".format(i, j))
    plt.show()


def split_integer(num: int, parts: int) -> list:
    quotient, remainder = divmod(num, parts)
    return [quotient + int(i < remainder) for i in range(parts)]


def lotto_scraper(vinster: dict, serie: int, start: int, end: int) -> None:
    session = requests.Session()
    for i in atpbar(range(start, end)):
        zero_filled_serie = str(serie).zfill(4)
        zero_filled_lottnummer = str(i).zfill(5)
        payload = {"S": zero_filled_serie, "L": zero_filled_lottnummer}
        r = session.post(url="https://www.bingolotto.se/ratta-lotten/", params=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        win_alert = soup.find("div", class_="alert alert-success")
        if win_alert:
            win_text = win_alert.find("span").get_text().split()
            amount = win_text[1]
            vinster[int(f"{zero_filled_serie}{zero_filled_lottnummer}")] = int(amount)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serie", help="Ange serie", type=int)
    parser.add_argument("--lottnummer", help="Ange lottnummer", type=int)
    parser.add_argument("--antal", help="Ange hur många lotter att rätta", type=int)
    args = parser.parse_args()
    main(args)
