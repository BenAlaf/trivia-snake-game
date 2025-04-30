from kivy.app import App
from kivy.uix.screenmanager import FadeTransition

from screens import TriviaSnakeScreenManager, MenuScreen, GameScreen, GameOverScreen, SettingsScreen
from utils import BASE_SNAKE_SIZE, BASE_APPLE_SIZE, BASE_ICON_SIZE

class TriviaSnakeApp(App):
    def build(self):
        # Default sizes
        self.snake_size = BASE_SNAKE_SIZE
        self.apple_size = BASE_APPLE_SIZE
        self.icon_size = BASE_ICON_SIZE

        sm = TriviaSnakeScreenManager(transition=FadeTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(GameOverScreen(name='game_over'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

if __name__ == '__main__':
    TriviaSnakeApp().run() 