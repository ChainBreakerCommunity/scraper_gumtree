from dotenv import dotenv_values
import os

def get_config():
    conf_debug = dotenv_values(".env.development")
    if conf_debug["DEBUG"] == "TRUE":
        config = dotenv_values(".env")
        return config
    else:
        config = os.environ
        return config

if __name__ == "__main__":
    print(get_config())