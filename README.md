# bingoplotto

Ever wondered what the winning serie and lottnummers are? Do you want to know if the bingolott with the lottnummer after you won that million? Look no further.

## Description

Script that checks with bingolottos api for winning lottery tickets for a given serie and plots them.
The script spawns as many processes as your cpu core count and each process spawns as many threads it can to make requests to bingolottos API.
The result is stored as a {serienummer}.json with {serie+lottnummer} as keys and the win as value.

![Demo](demo.gif)

## Install

```
pip install -r requirements.txt
```

## Run

```
python bingoplotto.py --serie {serienummer}
```

## Note

Your IP might get blacklisted due to suspicious behavior and I take no responsibility for it.
