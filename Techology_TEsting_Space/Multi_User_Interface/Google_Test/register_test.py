from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

class LoginApp(App):
    def build(self):
        return ScreenManagement()

if __name__ == "__main__":
    LoginApp().run()

