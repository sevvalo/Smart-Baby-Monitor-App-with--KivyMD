# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 13:44:49 2024

@author: sevva
"""
from kivymd.uix.screen import MDScreen, Screen
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFillRoundFlatButton, MDFloatingActionButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar, MDBottomAppBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.utils import platform
from kivy.core.audio import SoundLoader
from App_client_recv import Receiver
from App_send import Sender
from sensor_client_recv import Data
from sound_class_recv import Sound_class
import threading
import time
from kivy.clock import Clock




# from kivy.utils import get_color_from_hex
"""if platform == 'android':
    from android.permissions import request_permissions, Permission"""

class Function_def:
    def __init__(self, data = Data(), sound_class = Sound_class(), **kwargs):
        super().__init__(**kwargs)
        self._data = data
        self.s_class = sound_class
        self.t_data = self._data.temp
        self.movement_recv = self._data.mov
        self.sleep_recv = self._data.sleeping   
        self.sound_class = self.s_class.sound
        self._data.take_data()
        self.s_class.take_class()
    
    def data_collection(self):   
        self.t_data = self._data.temp #temperature data received from rpi
        self.movement_recv = self._data.mov   #0 (stationary) or 1 (moving)
        self.sleep_recv = self._data.sleeping   #0 (stationary) or 1 (moving)
        self.sound_class = self.s_class.sound
    
    def temperature(self):
        temp_data = self.t_data
        return temp_data
    
    def movement(self):
        """ 
        This part defines the actions in Movement screen
        """
        if self.movement_recv == 0:
            movement_data = "not moving" 
            badge_move ="numeric-0" 
        elif self.movement_recv == 1:# when on_ress is called activate
            movement_data = "moving"
            badge_move = "numeric-1"
        return [movement_data, badge_move]
    
    
    def sleep(self):
        """ 
        This part defines the actions in sleep/awake screen
        """
        if (self.sleep_recv == 0) or (self.sound_class == 0): 
            sleep_data = "awake"
            badge_sleep = "numeric-1"
        else: 
            sleep_data = "sleeping"
            badge_sleep ="numeric-0" 
        
        return sleep_data, badge_sleep
    
    def baby_sound(self):

        """ 
        This part defines the actions in talking/crying

        if baby says mama print baby said mama 2
        is papa baby says papa 1
        and when baby is crying say baby is crying 0
        we also have 4th class which is not-crying 3
        """
        if self.sound_class == 0:
            write = "Baby is crying"
        elif self.sound_class == 1:
            write = "Baby said dada"
        elif self.sound_class == 2:
            write = "Baby said mama"
        elif self.sound_class == 3:
            write = "Baby is not crying"

        return write 


class Demo(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.sender = Sender()
        self.receiver = Receiver()
        self.temp_data = 0
        self.mov_data = ""
        self.move_badge = ""
        self.sleep_data = ""
        self.sleep_badge = ""
        self.sound_class = ""
        
    """def on_enter(self):
    if platform == 'android':
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])"""
    sm = ScreenManager()
    

    def rec_data_thread(self):
        temp_thread = threading.Thread(target=self.rec_data)
        temp_thread.daemon = True
        temp_thread.start()
        

    def rec_data(self):
        while True:
            time.sleep(1)
            self.temp_data = Function_def().temperature()
            self.mov_data = Function_def().movement()[0]
            self.sleep_data = Function_def().sleep()[0]

    def rec_sound_thread(self):
        temp_thread = threading.Thread(target=self.rec_sound)
        temp_thread.daemon = True
        temp_thread.start()

    def rec_sound(self):
        while True:
            try:
                time.sleep(3)
                self.sound_class = Function_def().baby_sound()
            except Exception as e:
                print(e)

    def badge_data_thread(self):
        temp_thread = threading.Thread(target=self.data_badge)
        temp_thread.daemon = True
        temp_thread.start()

    def data_badge(self):
        while True:
            time.sleep(1)    
            self.move_badge = Function_def().movement()[1]
            self.sleep_badge = Function_def().sleep()[1]
    

    def on_tab_press(self):
        if self.move_badge == "numeric-1":
            self.move_badge = "numeric-0"
    
    #badge_situation = on_press(badge_situation)

    def receive_sound(self, *args):
        self.receiver.listen()

    def close_sound(self):
        self.receiver.close()

    def talk_to(self):
        self.sender.talk()

    def close_send(self):
        self.sender.close()

class Temperature(Screen):
    pass
class Movement(Screen):
    pass
class Sleep(Screen):
    pass
class Cry(Screen):
    pass
class Listen(Screen):
    pass


class Main(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_label, 2)
        Clock.schedule_interval(self.update_sound, 5)

    def build(self):
        sm = ScreenManager()
        self.theme_cls.primary_palette = "Teal"

        sm.add_widget(Temperature(name='Temperature'))
        sm.add_widget(Movement(name='Movement'))
        sm.add_widget(Sleep(name='Sleep'))
        sm.add_widget(Cry(name='Cry'))
        sm.add_widget(Listen(name='Listen'))
        
        #me = Demo().data_collection()
        Builder.load_file("eesbm.kv")
        return Demo()


    #Alternatively
    def update_label(self, dt):
        demo_screen = self.root
        demo_screen.rec_data_thread()  # Update the temperature data
        demo_screen.ids.temperature_label.text = "Here is the temperature of your baby: \n" + str(demo_screen.temp_data) + u'\N{DEGREE SIGN} C'  # Update the label text
        demo_screen.ids.movement_label.text = "Baby is \n" + str(demo_screen.mov_data)
        demo_screen.badge_data_thread()
        demo_screen.ids.movement_item.badge_icon = str(demo_screen.move_badge)
        demo_screen.ids.sleep_label.text = 'Baby is \n' + str(demo_screen.sleep_data)
        demo_screen.ids.sleep_item.badge_icon = str(demo_screen.sleep_badge)
    
    def update_sound(self,dt):

        demo_screen = self.root
        demo_screen.rec_sound_thread()
        demo_screen.ids.sound_label.text = str(demo_screen.sound_class)
    



if __name__ == '__main__':
    Main().run()

# Main().run()
