from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button

from MyDB import DBConnection

import hashlib

class Screen1(Screen):
    def on_username_send_button_press(self, text_input):
        self.username = text_input.text
        self.ids.numerical_keyboard.disabled = False


class NumericalKeyboard(GridLayout):
    def __init__(self, **kwargs):
        super(NumericalKeyboard, self).__init__(**kwargs)
        self.cols = 3  # Set the number of columns in the GridLayout
        self.spacing = 5
        self.code = ''

        # Create buttons for numbers 1-9 and 0
        for i in range(1, 10):
            button = Button(text=str(i))
            button.bind(on_release=self.on_number_click)
            self.add_widget(button)

        # Add a button for zero
        delete_button = Button(text='Delete')
        delete_button.bind(on_release=self.on_delete_click)
        self.add_widget(delete_button)

        zero_button = Button(text='0')
        zero_button.bind(on_release=self.on_number_click)
        self.add_widget(zero_button)

        send_button = Button(text='Send')
        send_button.bind(on_release=self.on_send_click)
        self.add_widget(send_button)


    def on_number_click(self, widget):
        # Handle button click here (you can customize this method)
        print(f'Button {widget.text} clicked')
        self.code += widget.text

    def on_send_click(self, widget):
        print(f'Button {widget.text} clicked')

        sha256_hash = hashlib.sha256(self.code.encode('utf-8')).hexdigest()

        username = self.parent.parent.username
        password = sha256_hash

        if my_app.db.login(username, password):
            self.parent.parent.manager.current = 'screen2'
            my_app.db.start_messages()
            Clock.schedule_interval(lambda dt: my_app.messages.display_messages(my_app.db.get_new_messages()), 1)
        else:
            self.parent.parent.manager.current = 'screen3'

    def on_delete_click(self, widget):   
        print(f'Button {widget.text} clicked')
        if len(self.code) > 0:
            self.code = self.code[:-1] 


class Screen2(Screen):
    def __init__(self, **kwargs):
        super(Screen2, self).__init__(**kwargs)

    def on_button_press(self, txt_input):
        print(txt_input.text)
        my_app.db.create_message(txt_input.text)

        txt_input.text = ''
        txt_input.text_validate_unfocus = False


class Messages(BoxLayout):
    def __init__(self, **kwargs):
        super(Messages, self).__init__(**kwargs)
        my_app.messages = self

    def display_messages(self, messages):
        if messages:
            for message in messages:
                if message['user'] == my_app.db.username:
                    label = MessageLabel1()
                else:
                    label = MessageLabel2()
                label.text = message['user'] + ': ' + message["message"]
                self.add_widget(label)

            self.parent.scroll_y = 0

class Screen3(Screen):
    pass

class MessageLabel1(Label):
    pass


class MessageLabel2(Label):
    pass


class TheChatApp(App):
    db = DBConnection()
    messages = None

    def build(self):
        return ScreenManager()


if __name__ == '__main__':
    my_app = TheChatApp()
    my_app.run()