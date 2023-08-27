from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen

from MongoDB import DBConnection


class Screen1(Screen):
    def on_button_press(self, widget):
        self.manager.current = 'screen2'
        username = widget.text

        my_app.db = db_init(username)
        my_app.messages.display_messages()
        Clock.schedule_interval(my_app.messages.display_messages, 5)


class Screen2(Screen):
    def __init__(self, **kwargs):
        super(Screen2, self).__init__(**kwargs)

    def on_button_press(self, txt_input):
        print(txt_input.text)
        my_app.db.send_message(txt_input.text)
        my_app.messages.display_messages()
        self.ids.scroll_view.scroll_y = 0

        txt_input.text = ''


class Messages(BoxLayout):
    def __init__(self, **kwargs):
        super(Messages, self).__init__(**kwargs)
        my_app.messages = self

    def display_messages(self, dt=5):
        messages = my_app.db.get_messages_in_order()
        print(messages)

        self.clear_widgets()

        for message in messages:
            if message['user'] == "User1":
                l = MessageLabel()
            else:
                l = MessageLabel2()
            l.text = message['user'] + ': ' + message["message"]
            self.add_widget(l)


class MessageLabel(Label):
    pass

class MessageLabel2(Label):
    pass


class TheChatApp(App):
    db = None
    messages = None

    def build(self):
        return ScreenManager()


def db_init(username):
    db_str = 'add db string'

    data_base = DBConnection(db_str, username)
    return data_base


if __name__ == '__main__':
    my_app = TheChatApp()
    my_app.run()
