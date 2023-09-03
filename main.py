from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen

from MyDB import DBConnection

class Screen1(Screen):
    def on_button_press(self, widget):
        self.manager.current = 'screen2'
        username = widget.text

        # todo: numerical keyboard enable

        my_app.db = db_init(username)
        # my_app.messages.display_messages(my_app.db.get_recent_messages())

        Clock.schedule_interval(lambda dt: my_app.messages.display_messages(my_app.db.get_new_messages()), 1)


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


class MessageLabel1(Label):
    pass


class MessageLabel2(Label):
    pass


class TheChatApp(App):
    db = None
    messages = None

    def build(self):
        return ScreenManager()


def db_init(username):
    data_base = DBConnection(username)
    return data_base


if __name__ == '__main__':
    my_app = TheChatApp()
    my_app.run()