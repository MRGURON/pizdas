from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
import serial
import serial.tools.list_ports
import time
import random

class MelodyGeneratorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serial_port = None
        self.baud_rate = 9600
        self.connected = False

    def build(self):
        root = GridLayout(cols=1)

        bluetooth_layout = GridLayout(cols=3, size_hint_y=None, height=100)
        bluetooth_layout.bind(minimum_height=bluetooth_layout.setter('height'))

        self.bluetooth_address_input = TextInput(text='Введите Bluetooth адрес', multiline=False)
        bluetooth_layout.add_widget(self.bluetooth_address_input)

        connect_button = Button(text='Подключиться', on_press=self.connect_bluetooth)
        bluetooth_layout.add_widget(connect_button)

        disconnect_button = Button(text='Отключиться', on_press=self.disconnect_bluetooth)
        bluetooth_layout.add_widget(disconnect_button)

        root.add_widget(bluetooth_layout)

        settings_layout = GridLayout(cols=2, size_hint_y=None, height=400)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))

        settings_scrollview = ScrollView(size_hint=(None, None), size=(800, 400))
        settings_scrollview.add_widget(settings_layout)

        settings_scrollview_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        settings_scrollview_grid.bind(minimum_height=settings_scrollview_grid.setter('height'))

        settings_scrollview.add_widget(settings_scrollview_grid)

        settings_scrollview_grid.add_widget(Label(text='Длительность (секунды):', halign='right'))
        self.length_entry = TextInput(text='10', multiline=False)
        settings_scrollview_grid.add_widget(self.length_entry)

        settings_scrollview_grid.add_widget(Label(text='Темп (BPM):', halign='right'))
        self.tempo_entry = TextInput(text='120', multiline=False)
        settings_scrollview_grid.add_widget(self.tempo_entry)

        settings_scrollview_grid.add_widget(Label(text='Задержка между нотами (мс):', halign='right'))
        self.delay_entry = TextInput(text='500', multiline=False)
        settings_scrollview_grid.add_widget(self.delay_entry)

        settings_scrollview_grid.add_widget(Label(text='Фактор скорости:', halign='right'))
        self.speed_factor_entry = TextInput(text='1.0', multiline=False)
        settings_scrollview_grid.add_widget(self.speed_factor_entry)

        settings_scrollview_grid.add_widget(Label(text='Генерировать мелодию:', halign='right'))
        generate_button = Button(text='Генерировать и отправить', on_press=self.generate_and_send_melody)
        settings_scrollview_grid.add_widget(generate_button)

        settings_scrollview_grid.add_widget(Label(text='Пауза/Возобновить:', halign='right'))
        pause_resume_button = Button(text='Пауза/Возобновить', on_press=self.pause_or_resume_melody)
        settings_scrollview_grid.add_widget(pause_resume_button)

        root.add_widget(settings_scrollview)

        return root

    def find_hc06(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'HC-06' in port.description:
                return port.device
        return None

    def connect_bluetooth(self, instance):
        if self.connected:
            self.popup_message('Ошибка', 'Уже подключено к Bluetooth')
            return

        bt_address = self.bluetooth_address_input.text
        try:
            self.serial_port = serial.Serial(bt_address, self.baud_rate)
            self.connected = True
            self.popup_message('Соединение', f'Успешно подключено к {bt_address}')
        except Exception as e:
            self.popup_message('Ошибка подключения', f'Не удалось подключиться: {e}')

    def disconnect_bluetooth(self, instance):
        if not self.connected:
            self.popup_message('Ошибка', 'Нет активного соединения')
            return

        try:
            self.serial_port.close()
            self.connected = False
            self.popup_message('Соединение', 'Соединение разорвано')
        except Exception as e:
            self.popup_message('Ошибка отключения', f'Не удалось отключиться: {e}')

    def generate_and_send_melody(self, instance):
        if not self.connected:
            self.popup_message('Ошибка', 'Сначала подключитесь к Bluetooth')
            return

        try:
            length = int(self.length_entry.text)
            tempo = int(self.tempo_entry.text)
            delay = int(self.delay_entry.text)
            speed_factor = float(self.speed_factor_entry.text)

            melody = self.generate_melody(length, tempo, delay, speed_factor)
            self.send_melody(melody)
        except Exception as e:
            self.popup_message('Ошибка генерации', f'Не удалось сгенерировать или отправить мелодию: {e}')

    def generate_melody(self, length, tempo, delay, speed_factor):
        melody = []
        notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        for _ in range(length):
            note = random.choice(notes)
            duration = int(60000 / (tempo * speed_factor))
            melody.append((note, duration, delay))
        return melody

    def send_melody(self, melody):
        if not self.connected or not self.serial_port:
            self.popup_message('Ошибка', 'Сначала подключитесь к Bluetooth')
            return

        try:
            for note, duration, delay in melody:
                command = f'{note},{duration},{delay}\n'
                self.serial
                    self.serial_port.write(command.encode())
                    time.sleep(delay / 1000.0)
            except Exception as e:
                self.popup_message('Ошибка отправки', f'Не удалось отправить мелодию: {e}')

        def pause_or_resume_melody(self, instance):
            if not self.connected:
                self.popup_message('Ошибка', 'Сначала подключитесь к Bluetooth')
                return

            try:
                self.serial_port.write(b'PAUSE\n')
            except Exception as e:
                self.popup_message('Ошибка', f'Не удалось отправить команду паузы/возобновления: {e}')

        def popup_message(self, title, message):
            popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
            popup.open()

    if __name__ == '__main__':
        MelodyGeneratorApp().run()
