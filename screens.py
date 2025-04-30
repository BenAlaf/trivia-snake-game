import os
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.slider import Slider
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from PIL import Image as PILImage
from kivy.graphics.texture import Texture

from game_widget import GameWidget
from utils import INITIAL_FPS, MIN_FPS, MAX_FPS, WHITE, YELLOW, ASSETS_DIR, trivia_questions

class TriviaSnakeScreenManager(ScreenManager):
    pass

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.fps = INITIAL_FPS
        root_layout = FloatLayout()
        main_layout = BoxLayout(orientation='vertical', spacing=dp(20), size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        # Title
        title = Label(text="Trivia Snake Game", font_size=dp(36), color=WHITE, size_hint=(1, None), height=dp(60), halign='center', valign='middle')
        title.bind(size=title.setter('text_size'))
        main_layout.add_widget(title)

        main_layout.add_widget(Widget(size_hint=(1, 0.1)))

        # Categories
        categories_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint=(1, None))
        categories_layout.bind(minimum_height=categories_layout.setter('height'))
        categories = list(trivia_questions.keys())
        for category in categories:
            btn = Button(text=category, font_size=dp(24), size_hint=(1, None), height=dp(60), background_color=get_color_from_hex('#4CAF50'), color=WHITE)
            btn.bind(on_release=self.select_category)
            categories_layout.add_widget(btn)
        categories_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None))
        categories_anchor.add_widget(categories_layout)
        main_layout.add_widget(categories_anchor)

        spacer = Widget(size_hint=(1, 1))
        main_layout.add_widget(spacer)

        version_label = Label(text="Version 1.1.2", font_size=dp(18), color=WHITE, size_hint=(1, None), height=dp(30), halign='center', valign='middle')
        version_label.bind(size=version_label.setter('text_size'))
        main_layout.add_widget(version_label)

        # Settings Button
        settings_btn = Button(
            text="Settings",
            font_size=dp(24),
            size_hint=(1, None),
            height=dp(60),
            background_color=get_color_from_hex('#2196F3'),
            color=WHITE
        )
        settings_btn.bind(on_release=self.open_settings)
        main_layout.add_widget(settings_btn)

        root_layout.add_widget(main_layout)

        # Speed Control Buttons
        speed_layout = BoxLayout(orientation='horizontal', spacing=dp(20), size_hint=(None, None), size=(dp(140), dp(60)))
        speed_up_icon = self.load_icon('speed_up.png')
        slow_down_icon = self.load_icon('slow_down.png')

        speed_up_btn = Button(background_normal='', background_color=(0, 0, 0, 0), size_hint=(None, None), size=(dp(60), dp(60)))
        speed_up_btn.bind(on_release=self.speed_up)
        speed_up_btn.canvas.before.add(Rectangle(texture=speed_up_icon, pos=speed_up_btn.pos, size=speed_up_btn.size))
        speed_up_btn.bind(pos=self.update_icon, size=self.update_icon)

        slow_down_btn = Button(background_normal='', background_color=(0, 0, 0, 0), size_hint=(None, None), size=(dp(60), dp(60)))
        slow_down_btn.bind(on_release=self.slow_down)
        slow_down_btn.canvas.before.add(Rectangle(texture=slow_down_icon, pos=slow_down_btn.pos, size=slow_down_btn.size))
        slow_down_btn.bind(pos=self.update_icon, size=self.update_icon)

        speed_layout.add_widget(slow_down_btn)
        speed_layout.add_widget(speed_up_btn)

        self.speed_label = Label(text=f"Speed: {self.fps} FPS", font_size=dp(18), color=WHITE, size_hint=(1, None), height=dp(20), halign='center', valign='middle')
        self.speed_label.bind(size=self.speed_label.setter('text_size'))

        speed_box = BoxLayout(orientation='vertical', spacing=dp(5), size_hint=(None, None), size=(dp(140), dp(100)), pos_hint={'x': 0, 'y': 0})
        speed_box.add_widget(speed_layout)
        speed_box.add_widget(self.speed_label)
        root_layout.add_widget(speed_box)

        self.add_widget(root_layout)

    def select_category(self, instance):
        category = instance.text
        game_screen = self.manager.get_screen('game')
        game_screen.set_fps(self.fps)
        game_screen.start_game(category)
        self.manager.current = 'game'

    def open_settings(self, instance):
        self.manager.current = 'settings'

    def load_icon(self, filename):
        fullname = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(fullname):
            print(f"Icon file '{filename}' not found.")
            return Texture.create(size=(dp(60), dp(60)))
        pil_image = PILImage.open(fullname).convert('RGBA')
        data = pil_image.tobytes()
        texture = Texture.create(size=pil_image.size)
        texture.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        return texture

    def update_icon(self, instance, value):
        for instruction in instance.canvas.before.children:
            if isinstance(instruction, Rectangle):
                instruction.pos = instance.pos
                instruction.size = instance.size

    def speed_up(self, instance):
        if self.fps < MAX_FPS:
            self.fps += 1
        else:
            print(f"FPS is already at maximum limit: {self.fps}")
        self.update_speed_label(self.fps)

    def slow_down(self, instance):
        if self.fps > MIN_FPS:
            self.fps -= 1
        else:
            print(f"FPS is already at minimum limit: {self.fps}")
        self.update_speed_label(self.fps)

    def update_speed_label(self, current_fps):
        self.speed_label.text = f"Speed: {current_fps} FPS"

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))

        # Title
        title = Label(
            text="Settings",
            font_size=dp(36),
            color=WHITE,
            size_hint=(1, None),
            height=dp(60),
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        self.layout.add_widget(title)

        # Snake Size Slider
        self.snake_size_slider = self.create_slider(
            "Snake Size",
            self.app.snake_size,
            self.on_snake_size_change
        )
        self.layout.add_widget(self.snake_size_slider)

        # Apple Size Slider
        self.apple_size_slider = self.create_slider(
            "Apple Size",
            self.app.apple_size,
            self.on_apple_size_change
        )
        self.layout.add_widget(self.apple_size_slider)

        # Icon Size Slider
        self.icon_size_slider = self.create_slider(
            "Icon Size",
            self.app.icon_size,
            self.on_icon_size_change
        )
        self.layout.add_widget(self.icon_size_slider)

        # Save Button
        save_btn = Button(
            text="Save",
            font_size=dp(24),
            size_hint=(1, None),
            height=dp(60),
            background_color=get_color_from_hex('#4CAF50'),
            color=WHITE
        )
        save_btn.bind(on_release=self.save_settings)
        self.layout.add_widget(save_btn)

        self.add_widget(self.layout)

    def create_slider(self, label_text, value, callback):
        layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(100))
        label = Label(
            text=f"{label_text}: {value}",
            font_size=dp(20),
            color=WHITE,
            size_hint=(1, None),
            height=dp(40),
            halign='left',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        slider = Slider(
            min=20,
            max=60,
            value=value,
            step=1,
            size_hint=(1, None),
            height=dp(40)
        )
        slider.bind(value=callback)
        layout.add_widget(label)
        layout.add_widget(slider)
        slider.label = label
        return layout

    def on_snake_size_change(self, instance, value):
        instance.label.text = f"Snake Size: {int(value)}"
        self.app.snake_size = int(value)

    def on_apple_size_change(self, instance, value):
        instance.label.text = f"Apple Size: {int(value)}"
        self.app.apple_size = int(value)

    def on_icon_size_change(self, instance, value):
        instance.label.text = f"Icon Size: {int(value)}"
        self.app.icon_size = int(value)

    def save_settings(self, instance):
        self.manager.current = 'menu'

class GameOverScreen(Screen):
    def __init__(self, **kwargs):
        super(GameOverScreen, self).__init__(**kwargs)
        anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        main_layout = BoxLayout(orientation='vertical', spacing=dp(20), size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.game_over_label = Label(text="GAME OVER!", font_size=dp(36), color=get_color_from_hex('#F44336'), size_hint=(1, None), height=dp(60), halign='center', valign='middle')
        self.game_over_label.bind(size=self.game_over_label.setter('text_size'))
        main_layout.add_widget(self.game_over_label)
        self.score_label = Label(text="Your Final Score: 0", font_size=dp(24), color=WHITE, size_hint=(1, None), height=dp(40), halign='center', valign='middle')
        self.score_label.bind(size=self.score_label.setter('text_size'))
        main_layout.add_widget(self.score_label)
        self.high_score_label = Label(text="High Score: 0", font_size=dp(24), color=YELLOW, size_hint=(1, None), height=dp(40), halign='center', valign='middle')
        self.high_score_label.bind(size=self.high_score_label.setter('text_size'))
        main_layout.add_widget(self.high_score_label)
        main_layout.add_widget(Widget(size_hint=(1, 0.1)))
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(20), size_hint=(1, None), height=dp(60))
        restart_btn = Button(text="Restart", font_size=dp(24), background_color=get_color_from_hex('#4CAF50'), color=WHITE)
        restart_btn.bind(on_release=self.restart_game)
        quit_btn = Button(text="Quit", font_size=dp(24), background_color=get_color_from_hex('#F44336'), color=WHITE)
        quit_btn.bind(on_release=self.quit_game)
        buttons_layout.add_widget(restart_btn)
        buttons_layout.add_widget(quit_btn)
        buttons_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None))
        buttons_anchor.add_widget(buttons_layout)
        main_layout.add_widget(buttons_anchor)
        anchor_layout.add_widget(main_layout)
        self.add_widget(anchor_layout)

    def update_scores(self, final_score, high_score):
        self.score_label.text = f"Your Final Score: {final_score}"
        self.high_score_label.text = f"High Score: {high_score}"

    def restart_game(self, instance):
        self.manager.current = 'menu'

    def quit_game(self, instance):
        App.get_running_app().stop()

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.question_label = Label(text='', font_size=dp(24), size_hint=(1, 0.1), color=YELLOW, halign='center', valign='middle')
        self.question_label.bind(size=self.question_label.setter('text_size'))
        self.layout.add_widget(self.question_label)
        self.game_widget = GameWidget(self.update_question_label, size_hint=(1, 0.9))
        self.layout.add_widget(self.game_widget)
        self.add_widget(self.layout)
        self.fps = INITIAL_FPS

    def update_question_label(self, question_text):
        self.question_label.text = question_text

    def set_fps(self, fps):
        self.fps = fps

    def start_game(self, category):
        self.game_widget.fps = self.fps
        self.game_widget.start_game(category) 