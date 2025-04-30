import json, os, random
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.text import Label as CoreLabel
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
from PIL import Image as PILImage
from kivy.graphics.texture import Texture

from utils import YELLOW, WHITE, MIN_FPS, MAX_FPS, INITIAL_FPS, ASSETS_DIR, SOUNDS_DIR, trivia_questions

class GameWidget(Widget):
    def __init__(self, question_callback, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.question_callback = question_callback
        self.WIDTH, self.HEIGHT = Window.size
        Window.bind(size=self.update_size)
        self.snake_direction = 'RIGHT'
        self.change_to = self.snake_direction
        self.snake_pos = [self.WIDTH // 2, self.HEIGHT // 2]
        self.snake_body = []
        self.score = 0
        self.high_score = 0
        self.fps = INITIAL_FPS
        self.grow_snake = False
        self.swipe_start = None
        self.question_data = None
        self.correct_answer = None
        self.apple_positions = []
        self.options = []
        self.category = None
        self.current_difficulty = 'Easy'
        self.load_assets()
        self.load_background()
        self.checkmark_texture = self.load_icon('checkmark.png')
        self.wrong_texture = self.load_icon('wrong.png')
        self.active_feedback = []
        self.correct_sound = SoundLoader.load(os.path.join(SOUNDS_DIR, 'correct.wav'))
        self.wrong_sound = SoundLoader.load(os.path.join(SOUNDS_DIR, 'wrong.wav'))
        self.high_score_file = os.path.join(os.path.dirname(__file__), 'high_score.json')
        self.load_high_score()

    def load_icon(self, name):
        fullname = os.path.join(ASSETS_DIR, name)
        if not os.path.exists(fullname):
            print(f"Cannot load icon image: {fullname}")
            App.get_running_app().stop()
        pil_image = PILImage.open(fullname).convert('RGBA')
        data = pil_image.tobytes()
        texture = Texture.create(size=pil_image.size)
        texture.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        return texture

    def update_size(self, instance, size):
        self.WIDTH, self.HEIGHT = size

    def load_assets(self):
        self.snake_head_textures = {
            'RIGHT': self.load_image('snake_head.png', 0),
            'UP': self.load_image('snake_head.png', 90),
            'LEFT': self.load_image('snake_head.png', 180),
            'DOWN': self.load_image('snake_head.png', -90)
        }
        self.snake_body_texture = self.load_image('snake_body.png')
        self.apple_texture = self.load_image('apple.png')

    def load_image(self, name, angle=0):
        fullname = os.path.join(ASSETS_DIR, name)
        if not os.path.exists(fullname):
            print(f"Cannot load image: {fullname}")
            App.get_running_app().stop()
        pil_image = PILImage.open(fullname).convert('RGBA')
        if angle != 0:
            pil_image = pil_image.rotate(angle, expand=True)
        data = pil_image.tobytes()
        texture = Texture.create(size=pil_image.size)
        texture.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        return texture

    def load_background(self):
        background_path = os.path.join(ASSETS_DIR, 'background.jpg')
        if os.path.exists(background_path):
            self.background_texture = CoreImage(background_path).texture
            self.background_texture.wrap = 'repeat'
        else:
            print(f"Background image not found: {background_path}")
            self.background_texture = None

    def load_high_score(self):
        if os.path.exists(self.high_score_file):
            try:
                with open(self.high_score_file, 'r') as file:
                    data = json.load(file)
                    self.high_score = data.get('high_score', 0)
                    print(f"Loaded high score: {self.high_score}")
            except Exception as e:
                print(f"Error loading high score: {e}")
                self.high_score = 0
        else:
            self.high_score = 0

    def save_high_score(self):
        data = {'high_score': self.high_score}
        try:
            with open(self.high_score_file, 'w') as file:
                json.dump(data, file)
                print(f"Saved high score: {self.high_score}")
        except Exception as e:
            print(f"Error saving high score: {e}")

    def start_game(self, category):
        print(f"Starting game with category: {category}")
        self.category = category
        self.current_difficulty = 'Easy'
        self.snake_direction = 'RIGHT'
        self.change_to = self.snake_direction
        self.WIDTH, self.HEIGHT = Window.size
        self.snake_pos = [self.WIDTH // 2, self.HEIGHT // 2]
        self.snake_body = [
            [self.snake_pos[0], self.snake_pos[1]],
            [self.snake_pos[0] - self.get_snake_size(), self.snake_pos[1]],
            [self.snake_pos[0] - (2 * self.get_snake_size()), self.snake_pos[1]]
        ]
        self.score = 0
        self.grow_snake = False
        self.swipe_start = None
        self.apple_positions = []
        self.options = []
        self.get_random_question()
        self.place_apples()
        self.update_score_labels()
        self.canvas.clear()
        Clock.unschedule(self.game_event) if hasattr(self, 'game_event') else None
        self.game_event = Clock.schedule_interval(self.update, 1 / self.fps)

    def get_snake_size(self):
        return dp(self.app.snake_size)

    def get_apple_size(self):
        return dp(self.app.apple_size)

    def get_icon_size(self):
        return dp(self.app.icon_size)

    def place_apples(self):
        num_apples = 3
        self.apple_positions = []
        if self.question_data and "options" in self.question_data:
            options = self.question_data["options"][:3]
            random.shuffle(options)
            self.options = options
        else:
            self.options = ["Option 1", "Option 2", "Option 3"]
        estimated_text_height = dp(30)
        vertical_margin = self.get_apple_size() + dp(10) + estimated_text_height
        while len(self.apple_positions) < num_apples:
            x_max = int((self.WIDTH - self.get_apple_size()) // self.get_apple_size())
            y_max = int((self.HEIGHT - 2 * vertical_margin - self.get_apple_size()) // self.get_apple_size())
            if x_max <= 0 or y_max <= 0:
                print("Screen too small for apples.")
                break
            x = random.randint(0, x_max) * self.get_apple_size()
            y = random.randint(0, y_max) * self.get_apple_size() + vertical_margin
            if [x, y] not in self.snake_body and [x, y] not in self.apple_positions:
                self.apple_positions.append([x, y])

    def get_random_question(self):
        available_questions = trivia_questions.get(self.category, {}).get(self.current_difficulty, [])
        if not available_questions:
            print(f"No {self.current_difficulty} questions available for category '{self.category}'.")
            self.question_data = {"question": "No questions available.", "options": ["N/A", "N/A", "N/A"], "correct": "N/A"}
        else:
            self.question_data = random.choice(available_questions)
            print(f"Selected question data: {self.question_data}")
            self.question_data["options"] = self.question_data["options"][:3]
            while len(self.question_data["options"]) < 3:
                self.question_data["options"].append("N/A")
        self.correct_answer = self.question_data["correct"]
        self.question_callback(self.question_data["question"])

    def on_touch_down(self, touch):
        self.swipe_start = touch.pos

    def on_touch_up(self, touch):
        if self.swipe_start:
            swipe_end = touch.pos
            self.change_to = self.detect_swipe(self.swipe_start, swipe_end)
            self.swipe_start = None

    def detect_swipe(self, start, end):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        threshold = self.WIDTH * 0.05
        if abs(dx) > abs(dy):
            if abs(dx) > threshold:
                return 'RIGHT' if dx > 0 else 'LEFT'
        else:
            if abs(dy) > threshold:
                return 'UP' if dy > 0 else 'DOWN'
        return self.snake_direction

    def update(self, dt):
        if self.change_to == 'UP' and self.snake_direction != 'DOWN':
            self.snake_direction = 'UP'
        elif self.change_to == 'DOWN' and self.snake_direction != 'UP':
            self.snake_direction = 'DOWN'
        elif self.change_to == 'LEFT' and self.snake_direction != 'RIGHT':
            self.snake_direction = 'LEFT'
        elif self.change_to == 'RIGHT' and self.snake_direction != 'LEFT':
            self.snake_direction = 'RIGHT'
        if self.snake_direction == 'UP':
            self.snake_pos[1] += self.get_snake_size()
        elif self.snake_direction == 'DOWN':
            self.snake_pos[1] -= self.get_snake_size()
        elif self.snake_direction == 'LEFT':
            self.snake_pos[0] -= self.get_snake_size()
        elif self.snake_direction == 'RIGHT':
            self.snake_pos[0] += self.get_snake_size()
        self.snake_pos[0] %= self.WIDTH
        self.snake_pos[1] %= self.HEIGHT
        self.snake_body.insert(0, list(self.snake_pos))
        head_rect = (self.snake_pos[0], self.snake_pos[1], self.get_snake_size(), self.get_snake_size())
        for i in range(len(self.apple_positions)):
            apple = self.apple_positions[i]
            apple_rect = (apple[0], apple[1], self.get_apple_size(), self.get_apple_size())
            if self.check_collision(head_rect, apple_rect):
                selected_option = self.options[i] if i < len(self.options) else ""
                if selected_option == self.correct_answer:
                    self.score += 1
                    self.grow_snake = True
                    print("Correct Answer!")
                    self.show_feedback(True, apple)
                else:
                    self.score -= 1
                    self.grow_snake = False
                    if len(self.snake_body) > 1:
                        self.snake_body.pop()
                    print("Wrong Answer!")
                    self.show_feedback(False, apple)
                self.apple_positions.pop(i)
                if i < len(self.options):
                    self.options.pop(i)
                self.get_random_question()
                self.place_apples()
                self.update_score_labels()
                self.adjust_difficulty()
                if self.score <= -3:
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                        print(f"New high score: {self.high_score}")
                    self.game_over()
                    return
                break
        if not self.grow_snake:
            self.snake_body.pop()
        else:
            self.grow_snake = False
        if self.snake_body[0] in self.snake_body[1:]:
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
                print(f"New high score: {self.high_score}")
            self.game_over()
            return
        self.draw_elements()
        current_time = Clock.get_boottime()
        self.active_feedback = [fb for fb in self.active_feedback if fb['expire_time'] > current_time]

    def adjust_difficulty(self):
        if self.score > 0 and self.score % 5 == 0:
            if self.current_difficulty == 'Easy':
                self.current_difficulty = 'Medium'
                print("Difficulty increased to Medium!")
            elif self.current_difficulty == 'Medium':
                self.current_difficulty = 'Hard'
                print("Difficulty increased to Hard!")
            elif self.current_difficulty == 'Hard':
                print("Already at Hard difficulty.")
            self.fps += 1
            if self.fps > MAX_FPS:
                self.fps = MAX_FPS
                print("FPS reached maximum limit.")
            Clock.unschedule(self.game_event)
            self.game_event = Clock.schedule_interval(self.update, 1 / self.fps)

    def adjust_fps(self, delta):
        new_fps = self.fps + delta
        if new_fps < MIN_FPS:
            new_fps = MIN_FPS
        elif new_fps > MAX_FPS:
            new_fps = MAX_FPS
        if new_fps != self.fps:
            print(f"Adjusting FPS from {self.fps} to {new_fps}")
            self.fps = new_fps
            Clock.unschedule(self.game_event)
            self.game_event = Clock.schedule_interval(self.update, 1 / self.fps)
        else:
            print(f"FPS is already at the {'minimum' if delta < 0 else 'maximum'} limit: {self.fps}")

    def update_score_labels(self):
        self.score_label_text = f"Score: {self.score}"
        self.high_score_label_text = f"High Score: {self.high_score}"

    def check_collision(self, rect1, rect2):
        return (rect1[0] < rect2[0] + rect2[2] and rect1[0] + rect1[2] > rect2[0] and rect1[1] < rect2[1] + rect2[3] and rect1[1] + rect1[3] > rect2[1])

    def draw_elements(self):
        self.canvas.clear()
        with self.canvas:
            if self.background_texture:
                Rectangle(texture=self.background_texture, pos=(0, 0), size=self.size)
            head_x, head_y = self.snake_body[0]
            head_texture = self.snake_head_textures[self.snake_direction]
            Rectangle(texture=head_texture, pos=(head_x, head_y), size=(self.get_snake_size(), self.get_snake_size()))
            for segment in self.snake_body[1:]:
                Rectangle(texture=self.snake_body_texture, pos=segment, size=(self.get_snake_size(), self.get_snake_size()))
            for i, apple in enumerate(self.apple_positions):
                Rectangle(texture=self.apple_texture, pos=apple, size=(self.get_apple_size(), self.get_apple_size()))
                option_text = self.options[i] if i < len(self.options) else ""
                option_label = CoreLabel(text=option_text, font_size=dp(20), color=WHITE)
                option_label.refresh()
                text_texture = option_label.texture
                text_size = text_texture.size
                if apple[1] + self.get_apple_size() + dp(10) + text_size[1] > self.HEIGHT:
                    text_y = apple[1] - text_size[1] - dp(10)
                else:
                    text_y = apple[1] + self.get_apple_size() + dp(10)
                text_x = apple[0] + (self.get_apple_size() - text_size[0]) / 2
                if text_x + text_size[0] > self.WIDTH:
                    text_x = self.WIDTH - text_size[0] - dp(10)
                elif text_x < 0:
                    text_x = dp(10)
                Rectangle(texture=text_texture, pos=(text_x, text_y), size=text_size)
            score_label = CoreLabel(text=self.score_label_text, font_size=dp(24), color=WHITE)
            score_label.refresh()
            text_texture = score_label.texture
            text_size = text_texture.size
            Rectangle(texture=text_texture, pos=(dp(10), dp(10)), size=text_size)
            high_score_label = CoreLabel(text=self.high_score_label_text, font_size=dp(24), color=YELLOW)
            high_score_label.refresh()
            text_texture = high_score_label.texture
            text_size = text_texture.size
            Rectangle(texture=text_texture, pos=(self.WIDTH - text_size[0] - dp(10), dp(10)), size=text_size)
            for feedback in self.active_feedback:
                icon_size = self.get_icon_size()
                Rectangle(texture=feedback['texture'], pos=feedback['pos'], size=(icon_size, icon_size))

    def show_feedback(self, is_correct, apple_position):
        texture = self.checkmark_texture if is_correct else self.wrong_texture
        if is_correct and self.correct_sound:
            self.correct_sound.play()
        elif not is_correct and self.wrong_sound:
            self.wrong_sound.play()
        icon_size = self.get_icon_size()
        icon_x = apple_position[0] + (self.get_apple_size() / 2) - (icon_size / 2)
        icon_y = apple_position[1] + self.get_apple_size() + dp(5)
        if icon_y + icon_size > self.HEIGHT:
            icon_y = apple_position[1] - icon_size - dp(5)
        expire_time = Clock.get_boottime() + 1
        self.active_feedback.append({'texture': texture, 'pos': (icon_x, icon_y), 'expire_time': expire_time})

    def game_over(self):
        Clock.unschedule(self.game_event)
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            print(f"New high score: {self.high_score}")
        try:
            app = App.get_running_app()
            sm = app.root
            game_over_screen = sm.get_screen('game_over')
            game_over_screen.update_scores(self.score, self.high_score)
            sm.current = 'game_over'
        except Exception as e:
            print(f"Error transitioning to Game Over screen: {e}") 