import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import sqlite3

class LoginScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        self.add_widget(Label(text='Username'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        
        self.add_widget(Label(text='Password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)
        
        self.login_button = Button(text='Login')
        self.login_button.bind(on_press=self.login)
        self.add_widget(self.login_button)
        
        self.message = Label()
        self.add_widget(self.message)

    def login(self, instance):
        username = self.username.text
        password = self.password.text
        if self.validate_user(username, password):
            self.message.text = 'Login successful!'
        else:
            self.message.text = 'Invalid username or password'

    def validate_user(self, username, password):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        return user is not None

class RegisterScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        self.add_widget(Label(text='Username'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        
        self.add_widget(Label(text='Password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)
        
        self.register_button = Button(text='Register')
        self.register_button.bind(on_press=self.register)
        self.add_widget(self.register_button)
        
        self.message = Label()
        self.add_widget(self.message)

    def register(self, instance):
        username = self.username.text
        password = self.password.text
        if self.add_user(username, password):
            self.message.text = 'Registration successful!'
        else:
            self.message.text = 'Username already exists'

    def add_user(self, username, password):
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

class MyApp(App):
    def build(self):
        self.root = BoxLayout(orientation='horizontal')
        self.root.add_widget(LoginScreen())
        self.root.add_widget(RegisterScreen())
        return self.root

if __name__ == '__main__':
    MyApp().run()
