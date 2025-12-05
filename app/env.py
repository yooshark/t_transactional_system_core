import os

import environ

BASE_DIR = environ.Path(__file__) - 2
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
