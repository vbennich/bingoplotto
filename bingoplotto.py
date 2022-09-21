import requests
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import RLock
import json
import argparse
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


def scrape(zero_filled_serie: str, lottnummer: int, session: requests.Session):
    url = ""
    zero_filled_lottnummer = str(lottnummer).zfill(5)
    payload = {"S": zero_filled_serie, "L": zero_filled_lottnummer}
    r = session.post(url=url, params=payload)
    soup = BeautifulSoup(r.text, "html.parser")
    win_alert = soup.find("div", class_="alert alert-success")
    if win_alert:
        win_text = win_alert.find("span").get_text().split()
        amount = win_text[1]
        return zero_filled_serie, zero_filled_lottnummer, amount


def run_in_threads(serie, lottnummer, i):
    vinster = {}
    with requests.Session() as s:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(scrape, serie, i, s): i for i in lottnummer}
            with tqdm(
                total=len(lottnummer), desc=f"Process: {i}", position=i + 1
            ) as pbar:
                for future in as_completed(futures):
                    pbar.update(1)
                    try:
                        serie, lottnummer, vinst = future.result()
                        vinster[int(f"{serie}{lottnummer}")] = int(vinst)
                    except Exception:
                        pass
    return vinster


def run_in_processes(cores, chunks, serie):
    vinster = {}
    with ProcessPoolExecutor(
        max_workers=cores, initargs=(RLock(),), initializer=tqdm.set_lock
    ) as p:
        futures = {
            p.submit(run_in_threads, serie, chunk, i): chunk
            for i, chunk in enumerate(chunks)
        }
    for future in as_completed(futures):
        vinster |= future.result()
    return vinster


def save_to_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
    with open(file_name, "w") as file:
        file.write(json.dumps(results))


def plot(results, serie):
    vinst_list = sorted(results.items())
    number_of_wins = len(vinst_list)
    print(f"På serien {serie} var det {number_of_wins} vinster")
    x, y = zip(*vinst_list)
    plt.plot(x, y, marker="o")
    for i, j in zip(x, y):
        plt.text(i, j + 0.5, "({}, {})".format(i, j))
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serie", help="Ange serie", type=int)
    args = parser.parse_args()
    serie = args.serie
    zero_filled_serie = str(serie).zfill(4)
    cores = cpu_count()
    chunks = list(split(range(99999), cores))

    results = run_in_processes(cores, chunks, zero_filled_serie)

    save_to_file(f"{zero_filled_serie}.json")

    plot(results, zero_filled_serie)
