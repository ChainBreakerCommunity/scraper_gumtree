import bot.bot 
from utils.env import get_config
config = get_config()

def execute_scraper():
    bot.bot.execute_scraper()

if __name__ == "__main__":
    execute_scraper()