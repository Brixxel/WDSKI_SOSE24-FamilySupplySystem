from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

class MenuPopup(Popup):
    def __init__(self, **kwargs):
        super(MenuPopup, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (200, 200)
        layout = BoxLayout(orientation='vertical')
        
        btn_page1 = Button(text="Gehe zu Seite 1")
        btn_page1.bind(on_press=self.go_to_page1)
        layout.add_widget(btn_page1)
        
        btn_page2 = Button(text="Gehe zu Seite 2")
        btn_page2.bind(on_press=self.go_to_page2)
        layout.add_widget(btn_page2)
        
        self.add_widget(layout)
    
    def go_to_page1(self, instance):
        App.get_running_app().root.current = 'page1'
        self.dismiss()

    def go_to_page2(self, instance):
        App.get_running_app().root.current = 'page2'
        self.dismiss()

class MenuButton(Button):
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.text = "≡"
        self.size_hint = (None, None)
        self.size = (50, 50)
        self.pos_hint = {'x': 0, 'y': 0.9}
        self.bind(on_press=self.open_menu)
    
    def open_menu(self, instance):
        menu = MenuPopup()
        menu.open()

class Page1(Screen):
    def __init__(self, **kwargs):
        super(Page1, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        menu_button = MenuButton()
        layout.add_widget(menu_button)
        
        label = Label(text="Dies ist Seite 1")
        layout.add_widget(label)
        
        table = GridLayout(cols=2)
        for i in range(4):
            table.add_widget(Label(text=f'Item {i + 1}'))
            table.add_widget(Label(text=f'Wert {i + 1}'))
        layout.add_widget(table)
        
        self.add_widget(layout)

class Page2(Screen):
    def __init__(self, **kwargs):
        super(Page2, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        menu_button = MenuButton()
        layout.add_widget(menu_button)
        
        label = Label(text="Dies ist Seite 2")
        layout.add_widget(label)
        
        table = GridLayout(cols=2)
        for i in range(4):
            table.add_widget(Label(text=f'Item {i + 1}'))
            table.add_widget(Label(text=f'Wert {i + 1}'))
        layout.add_widget(table)
        
        self.add_widget(layout)

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Page1(name='page1'))
        sm.add_widget(Page2(name='page2'))
        
        return sm

if __name__ == '__main__':
    MyApp().run()