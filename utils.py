import json, os
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

# Constants
BASE_SNAKE_SIZE = 35        # Default size
BASE_APPLE_SIZE = 35        # Default size
BASE_ICON_SIZE = 25         # Default size
INITIAL_FPS = 10
MIN_FPS = 5
MAX_FPS = 30
WHITE = (1, 1, 1, 1)
YELLOW = (1, 1, 0, 1)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'images')
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')

def load_trivia_questions(filename='trivia.json'):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(filepath):
        print(f"Trivia file '{filename}' not found!")
        return {}
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            print(f"Successfully loaded trivia questions from '{filename}'.")
            return data
    except Exception as e:
        print(f"Error loading '{filename}': {e}")
        return {}

# Load trivia questions
trivia_questions = load_trivia_questions() 