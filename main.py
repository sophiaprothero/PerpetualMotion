# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO 
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
import Slush


# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
ON = False
OFF = True
HOME = True
TOP = False
OPEN = False
CLOSE = True
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
DEBOUNCE = 0.1
INIT_RAMP_SPEED = 150
RAMP_LENGTH = 725

b = Slush.sBoard()
axis1 = Slush.Motor(0)
axis1.resetDev()
axis1.setCurrent(20, 20, 20, 20)


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////

class MyApp(App):
    def build(self):
        self.title = "Perpetual Motion"
        return sm


Builder.load_file('main.kv')
Window.clearcolor = (0.2, 0.2, 0.2, 1)

cyprus.open_spi()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()
ramp = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20, steps_per_unit=200, speed=INIT_RAMP_SPEED)

# ////////////////////////////////////////////////////////////////////////////////
# ///                              Main Screen                                 ///
# ////////////////////////////////////////////////////////////////////////////////


class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    staircaseSpeedText = '0'
    global rspeed
    global sspeed
    sspeed = 0.5
    rspeed = 3.5

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def check_text(self, mod):
        if mod == 'gate':
            if self.gate.text == "Open Gate":
                return 'Off'
            elif self.gate.text == "Close Gate":
                return 'On'
        elif mod == 'staircase':
            if self.staircase.text == "Start Staircase":
                return 'Off'
            elif self.staircase.text == "Stop Staircase":
                return 'On'
        elif mod == 'ramp':
            if self.ramp.text == "Ramp Up":
                return 'Off'
            elif self.ramp.text == "Ramp Down":
                return 'On'
    # checks states

    def toggle_gate(self):
        if self.check_text('gate') == 'Off':
            self.gate.text = "Close Gate"
            cyprus.set_servo_position(2, 0.5)
        elif self.check_text('gate') == 'On':
            self.gate.text = "Open Gate"
            cyprus.set_servo_position(2, 0)
    # changes gate state

    def toggle_staircase(self):
        global sspeed
        if self.check_text('staircase') == 'Off':
            self.staircase.text = "Stop Staircase"
            cyprus.set_motor_speed(1, sspeed)
        elif self.check_text('staircase') == 'On':
            self.staircase.text = "Start Staircase"
            cyprus.set_motor_speed(1, 0)
    # changes staircase state

    def set_staircase_speed(self, speedy):
        global sspeed
        cyprus.set_motor_speed(1, 0)
        if self.check_text('staircase') == 'Off':
            pass
        elif self.check_text('staircase') == 'On':
            self.staircaseSpeedLabel.text = speedy
            cyprus.set_motor_speed(1, speedy)
            sspeed = speedy

    # updates speed value based on slider

    def toggle_ramp(self):
        if self.check_text('ramp') == 'Off':
            self.ramp.text = "Ramp Down"
            self.move_ramp()
        elif self.check_text('ramp') == 'On':
            self.ramp.text = "Ramp Up"
            self.move_ramp()

    @staticmethod
    def move_ramp():
        ramp.set_speed(3.5)
        ramp.free()

        if ramp.read_switch() == 1:
            ramp.go_to_position(30)
            ramp.free()
        elif ramp.get_position_in_units() == 30:
            axis1.goTo(0)

        else:
            while axis1.isBusy():
                continue
            axis1.goUntilPress(0, 0, 5000)

            while axis1.isBusy():
                continue
            axis1.setAsHome()

            ramp.set_speed(3.5)
        
    def auto(self):
        print("Run through one cycle of the perpetual motion machine")
        
    def setRampSpeed(self, speed):
        print("Set the ramp speed and update slider text")




    @staticmethod
    def initialize():
        ramp.free()
        ramp.set_speed(3.5)
        cyprus.initialize()
        cyprus.setup_servo(2)
        cyprus.set_motor_speed(1, 0)
        cyprus.set_servo_position(2, 0)

    def resetColors(self):
        self.ids.gate.color = YELLOW
        self.ids.staircase.color = YELLOW
        self.ids.ramp.color = YELLOW
        self.ids.auto.color = BLUE

    @staticmethod
    def quit():
        print("Exit")
        ramp.free()
        cyprus.close()
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()
