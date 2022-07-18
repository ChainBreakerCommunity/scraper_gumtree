import unittest
import requests 
from dotenv import dotenv_values
config = dotenv_values(".env.test")

class ScraperTesting(unittest.TestCase):

    def test_bot(self):
        route = config["ENDPOINT"] + "/api/execute_scraper"
        res = requests.get(route)
        print(res.text)
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
