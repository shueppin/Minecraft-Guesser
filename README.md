# Minecraft-Guesser

A guessing game where you identify Minecraft mobs, items, and blocks. Get hints from the integrated wiki, track your scores, and test your Minecraft knowledge!

Visit it on [https://shueppin.github.io/Minecraft-Guesser/](https://shueppin.github.io/Minecraft-Guesser/).

The data of this project is obtained from the [Minecraft wiki](https://minecraft.wiki).  
This project is inspired by [mcdle.net](https://mcdle.net).


## Features

- **Three Game Modes**: Guess mobs, items, or blocks
- **Wiki Integration**: Look up information while playing
- **Rating System**: Track your performance and scores (based on the number of guesses and how many wiki-helps you use)
- **Responsive Web Interface**: Play in your browser


## Quick Start

### Run the data scraper
1. Go to the `data` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Run the scraper: `python scrape_newest_data.py`

### Run the testing server (not for production)
1. Run the server: `python testing_server.py`
2. Open your browser and visit the game interface (with `http://localhost:8000`)


## Attribution

Big thanks to the [Minecraft wiki](https://minecraft.wiki) for providing the data and their API.
