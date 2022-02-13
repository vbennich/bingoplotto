from requests import Session
from bs4 import BeautifulSoup
import json
import concurrent.futures
from alive_progress import alive_bar
import argparse
import matplotlib.pyplot as plt
import os


def main(args: argparse.Namespace) -> None:
    serie = args.serie
    lottnummer = args.lottnummer
    antal = args.antal
    vinster = {}
    session = Session()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_request = {
            executor.submit(lotto_scraper, session, serie, lottnummer + i): i
            for i in range(antal)
        }
        with alive_bar(len(future_request), title="Progress") as bar:
            for future in concurrent.futures.as_completed(future_request):
                bar()
                try:
                    serie, lottnummer, vinst = future.result()
                    bar.text(f"Vinst!")
                    vinster[int(f"{serie}{lottnummer}")] = int(vinst)
                except Exception as exc:
                    bar.text("Ingen vinst")
                    # Ignore if there is no win
                    pass

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


def lotto_scraper(session: Session, serie: int, lottnummer: int):
    zero_filled_serie = str(serie).zfill(4)
    zero_filled_lottnummer = str(lottnummer).zfill(5)
    payload = {"S": zero_filled_serie, "L": zero_filled_lottnummer}
    r = session.post(url="https://www.bingolotto.se/ratta-lotten/", params=payload)
    soup = BeautifulSoup(r.text, "html.parser")
    win_alert = soup.find("div", class_="alert alert-success")
    if win_alert:
        win_text = win_alert.find("span").get_text().split()
        amount = win_text[1]
        return zero_filled_serie, zero_filled_lottnummer, amount


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serie", help="Ange serie", type=int)
    parser.add_argument("--lottnummer", help="Ange lottnummer", type=int)
    parser.add_argument("--antal", help="Ange hur många lotter att rätta", type=int)
    args = parser.parse_args()
    main(args)
