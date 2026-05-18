# Minecraft-Guesser

A guessing game where you identify Minecraft mobs, items, and blocks. Get hints from the integrated wiki, track your scores, and test your Minecraft knowledge!

Inspired by [mcdle.net](https://mcdle.net).


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

This project is inspired by and uses data from [mcdle.net](https://mcdle.net). Consider supporting them!
