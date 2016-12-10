from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.layout import Layout
from kivy.uix.button import Button
from kivy.properties import ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.adapters.models import SelectableDataItem
from kivy.graphics import Color, Ellipse, Line
# import RPi.GPIO as GPIO ## Import GPIO library
from subprocess import call
import controls
import programcontrol
import stepper
import time


appConfig = [2.8, 3.2, 3.5, 4, 4.5, 5, 5.6, 6.3, 7.1, 8, 9, 10, 11, 13, 14, 16, 18, 20, 22, 25, 29, 32]

expConfig = ["1/30","1/40","1/50","1/60","1/80","1/100","1/125","1/160","1/200","1/250","1/320","1/400","1/500","1/640","1/800","1/1000","1/1250","1/1600","1/2000","1/2500","1/3200","1/4000","1/5000","1/6400","1/8000"]

red = [1,0,0,1]
green = [0,1,0,1]
blue =  [0,0,1,1]
purple = [1,0,1,1]

globalSettings = 0

stepper.gpio_setup()

class Manager(ScreenManager):
    timelapse_screen = ObjectProperty(None)
    camera_screen = ObjectProperty(None)
    actions_screen = ObjectProperty(None)
    motor_settings = ObjectProperty(None)
    program_screen = ObjectProperty(None)
    home_screen = ObjectProperty(None)



class SettingsClass(object):
    def __init__(self):
        self.apertureOptions = [2.8, 3.2, 3.5, 4, 4.5, 5, 5.6, 6.3, 7.1, 8, 9, 10, 11, 13, 14, 16, 18, 20, 22, 25, 29, 32]
        self.currentAperture = 15
        self.interval = 1
        self.eventDuration = 60
        self.programStartTime = 0
        self.shutterTime = 0.1
        self.rampActive = False
        self.totalPictures = 0
        self.rampStart = 600
        self.rampDuration = 60
        self.programElapsedTime = 0
        self.exposureIndex = 30
        self.ramp_direction = 1 # positive = sunset
        self.stopPicturePoint = 5;
        self.exposure_comp = 0;
    def returnVal(self):
        print(self.interval)

    def printInterval(self):
        return 'Interval: ' + str(self.interval) + 's'

    def printClipDuration(self):
        clipDuration = ((self.eventDuration * 60) / self.interval) / 25
        return "Clip Duration: " + str(clipDuration) + "s"

    def printTotalPictures(self):
        pictureCount = (self.eventDuration * 60) / self.interval
        return "Total Pictures: " + str(pictureCount)

    def printCurrentExposure(self):
        setValue = "shutterspeed="+str(self.exposureIndex)

        call (["gphoto2","--set-config-index", setValue])
        return "index: " + str(self.exposureIndex)

    def printPictureCount(self):
        return str(self.totalPictures)

    def printEventDuration(self):
        return "Event Duration: " + str(self.eventDuration) + 'min'

    def printShutterTime(self):
        return 'Shutter Time: ' + str(self.shutterTime) + 's'

    def printRampStart(self):
        return "Ramp Delay: " + str(self.rampStart / 60) + 'min'

    def printRampDuration(self):
        return "Ramp Duration: " + str(self.rampDuration / 60) + 'min'

    def printExposureComp(self):
        return "Exposure Chg: " + str(self.exposure_comp) + 'ev'

    def printRamping(self):
        if self.rampActive:
            return "Ramping: ON"
        else:
            return "Ramping: OFF"


    def printAperture(self):
        setValue = "aperture="+str(self.currentAperture)

        call (["gphoto2","--set-config-index", setValue])
        return "f/"+str(self.apertureOptions[self.currentAperture])

class MainWindow(BoxLayout):

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

    def endProgram(self):
        stepper.cleanup()
        App.get_running_app().stop()
        

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

    def endProgram(self):
        stepper.cleanup()
        App.get_running_app().stop()


class TimelapseSettings(Screen):

    def __init__(self, **kwargs):
        super(TimelapseSettings, self).__init__(**kwargs)
        global globalSettings
        globalSettings = SettingsClass()
        self.interval_text = globalSettings.printInterval()
        self.clipDuration = globalSettings.printClipDuration()
        self.pictureCount = globalSettings.printTotalPictures()
        self.eventDuration = globalSettings.printEventDuration()
        self.rampActive = globalSettings.printRamping()
        self.rampingOff = True

    def updateLabels(self):
        global globalSettings
        self.ids['interval_label'].text = globalSettings.printInterval()
        self.ids['clip_duration_label'].text = globalSettings.printClipDuration() 
        self.ids['picture_count_label'].text = globalSettings.printTotalPictures() 
        self.ids['event_duration_label'].text = globalSettings.printEventDuration() 

    def change_time_interval(self):
        global globalSettings
        globalSettings.interval = self.ids['time_interval_slider'].value
        self.updateLabels()

    def change_event_duration(self):
        global globalSettings
        globalSettings.eventDuration = self.ids['duration_slider'].value
        self.updateLabels()


    def toggleRamping(self):
        global globalSettings
        if globalSettings.rampActive:
            globalSettings.rampActive = False
            self.ids['sunset_button'].disabled = True
            self.ids['sunrise_button'].disabled = True
            self.ids['ramp_button'].text = "Ramping Off" 
        else:
            globalSettings.rampActive = True
            self.ids['sunset_button'].disabled = False
            self.ids['sunrise_button'].disabled = False
            self.ids['ramp_button'].text = "Ramping On"
        self.updateLabels

    def ramp_sunset(self):
        global globalSettings
        globalSettings.ramp_direction = 1
        print("Sunset")

    def ramp_sunrise(self):
        global globalSettings
        globalSettings.ramp_direction = -1
        print("Sunrise")


           

class CameraSettings(Screen):
    
    def __init__(self, **kwargs):
        super(CameraSettings, self).__init__(**kwargs)
        global globalSettings
        self.rampStartTime = globalSettings.printRampStart()
        self.rampDuration = globalSettings.printRampDuration()
        self.exposure_comp = globalSettings.printExposureComp()
        self.bulbTime = globalSettings.printShutterTime()

    def updateLabels(self):
        self.ids['ramp_start_time_label'].text = globalSettings.printRampStart() 
        self.ids['ramp_duration_time_label'].text = globalSettings.printRampDuration()

    def rampStartEarly(self):
        global globalSettings
        globalSettings.rampStart -= 60
        self.updateLabels()

    def rampStartLater(self):
        global globalSettings
        globalSettings.rampStart += 60
        self.updateLabels() 

    def rampIncreaseDuration(self):
        global globalSettings
        globalSettings.rampDuration += 60
        self.updateLabels() 

    def rampDecreaseDuration(self):
        global globalSettings
        globalSettings.rampDuration -= 60
        self.updateLabels()

    def increase_exp_comp(self):
        global globalSettings
        globalSettings.exposure_comp += 0.3
        self.ids.exposure_comp_label.text = globalSettings.printExposureComp() 

    def decrease_exp_comp(self):
        global globalSettings
        globalSettings.exposure_comp -= 0.3
        self.ids.exposure_comp_label.text = globalSettings.printExposureComp()

    def increaseBulb(self):
        global globalSettings
        globalSettings.shutterTime += 0.1
        self.ids.bulb_time_label.text = globalSettings.printShutterTime()

    def decreaseBulb(self):
        global globalSettings
        globalSettings.shutterTime -= 0.1
        self.ids.bulb_time_label.text = globalSettings.printShutterTime()


    def openShutter(self):
        start_time = time.time()
        call (["gphoto2","--set-config", "eosremoterelease=2"])
        elapsed_time = time.time() - start_time
        print(elapsed_time)

    def closeShutter(self):
        start_time = time.time()
        call (["gphoto2","--set-config", "eosremoterelease=4"])
        elapsed_time = time.time() - start_time
        print(elapsed_time)


class MotorSettings(Screen):
    

    def __init__(self, **kwargs):
        super(MotorSettings, self).__init__(**kwargs)
        global globalSettings
        self.stepper_speed = float(200) / 1000
        self.pan_speed = float(200) / 1000
        self.motors_stopped = True
        self.toggle_step_count = 0
        self.left = False
        self.right = True
        self.step_amount = 200
        # self.ids['stepper_speed'].value = 200

    def set_slide_right(self):
        stepper.set_slide_direction(True)

    def set_slide_left(self):
        stepper.set_slide_direction(False)

    def set_pan_right(self):
        stepper.set_pan_direction(True)

    def set_pan_left(self):
        stepper.set_pan_direction(False)

    def turn_slide_on(self):
        stepper.variable_slide_step(self.stepper_speed, self.step_amount)
        # stepper.ramp_slide_step(self.stepper_speed, self.step_amount)

    def turn_pan_on(self):
        stepper.variable_pan_step(self.pan_speed, self.step_amount)

    def change_step_number(self):
        self.ids.step_number_label.text = "Steps: " + str(self.ids.step_number_slider.value)
        self.step_amount = self.ids.step_number_slider.value

    def turn_stepper_off(self):
        stepper.disable_stepper()

    def toggle_pan_stepper(self, dt):
        self.toggle_step_count += 1
        if self.toggle_step_count % 2 == 0:
            print("on: " + str(dt))
            stepper.pan_step_on()
        else:
            stepper.pan_step_off()
            print("off: " + str(dt))


    def scroll_pan_left(self):
        stepper.enable_stepper()
        stepper.set_pan_dir(1)
        self.stepper_interval = Clock.schedule_interval(self.toggle_pan_stepper, self.pan_speed)

    def scroll_pan_right(self):
        stepper.enable_stepper()
        stepper.set_pan_dir(0)
        self.stepper_interval = Clock.schedule_interval(self.toggle_pan_stepper, self.pan_speed)



    def find_slide_home(self):
        stepper.find_slide_home()

    def toggle_slide_stepper(self, dt):
        self.toggle_step_count += 1
        if self.toggle_step_count % 2 == 0:
            print("on: " + str(dt))
            stepper.slide_step_on()
        else:
            stepper.slide_step_off()
            print("off: " + str(dt))


    def scroll_slide_left(self):
        stepper.enable_stepper()
        stepper.set_slide_dir(1)
        self.stepper_interval = Clock.schedule_interval(self.toggle_slide_stepper, self.stepper_speed)

    def scroll_slide_right(self):
        stepper.enable_stepper()
        stepper.set_slide_dir(0)
        self.stepper_interval = Clock.schedule_interval(self.toggle_slide_stepper, self.stepper_speed)



    def stop_motors(self):
        print("stopping")
        self.stepper_interval.cancel()
        stepper.pan_step_off()
        stepper.slide_step_off()
        stepper.disable_stepper()



    def cancelReading(self):
        self.ids['limit_label'].text = "Canceled"
        self.program_interval.cancel()



    def step_left(self):
        self.stepper_interval = Clock.schedule_interval(self.run_left_stepper, self.stepper_speed)

    

    def turn_pan_off(self):
        stepper.disable_stepper()

    def change_stepper_speed(self):
        self.ids['stepper_value_label'].text = "Slide: " + str(self.ids['stepper_speed_slider'].value)
        self.stepper_speed = float(self.ids['stepper_speed_slider'].value) / 1000.0

    def change_pan_speed(self):
        self.ids['pan_value_label'].text = "Pan: " + str(self.ids['pan_speed_slider'].value)
        self.pan_speed = float(self.ids['pan_speed_slider'].value) / 1000.0





    def checkButtons(self):
        self.program_interval = Clock.schedule_interval(self.readLimits, 0.1)
            
    def endProgram(self):
        controls.cleanup()
        App.get_running_app().stop()


class ConfigureSettings(Screen):
    

    def __init__(self, **kwargs):
        super(ConfigureSettings, self).__init__(**kwargs)
        global globalSettings
        self.stepper_speed = float(200) / 1000
        self.pan_speed = float(200) / 1000
        self.motors_stopped = True
        self.toggle_step_count = 0
        self.left = False
        self.right = True
        # self.ids['stepper_speed'].value = 200

    def toggle_pan_stepper(self, dt):
        self.toggle_step_count += 1
        if self.toggle_step_count % 2 == 0:
            print("on: " + str(dt))
            stepper.pan_step_on()
        else:
            stepper.pan_step_off()
            print("off: " + str(dt))


    def scroll_pan_left(self):
        stepper.enable_stepper()
        stepper.set_pan_dir(1)
        self.stepper_interval = Clock.schedule_interval(self.toggle_pan_stepper, self.pan_speed)

    def scroll_pan_right(self):
        stepper.enable_stepper()
        stepper.set_pan_dir(0)
        self.stepper_interval = Clock.schedule_interval(self.toggle_pan_stepper, self.pan_speed)

    def set_slide_right(self):
        stepper.set_slide_direction(False)

    def set_slide_left(self):
        stepper.set_slide_direction(True)

    def find_slide_home(self):
        stepper.find_slide_home()

    def toggle_slide_stepper(self, dt):
        self.toggle_step_count += 1
        if self.toggle_step_count % 2 == 0:
            print("on: " + str(dt))
            stepper.slide_step_on()
        else:
            stepper.slide_step_off()
            print("off: " + str(dt))


    def scroll_slide_left(self):
        stepper.enable_stepper()
        stepper.set_slide_dir(1)
        self.stepper_interval = Clock.schedule_interval(self.toggle_slide_stepper, self.stepper_speed)

    def scroll_slide_right(self):
        stepper.enable_stepper()
        stepper.set_slide_dir(0)
        self.stepper_interval = Clock.schedule_interval(self.toggle_slide_stepper, self.stepper_speed)



    def stop_motors(self):
        print("stopping")
        self.stepper_interval.cancel()
        stepper.pan_step_off()
        stepper.slide_step_off()
        stepper.disable_stepper()



    def cancelReading(self):
        self.ids['limit_label'].text = "Canceled"
        self.program_interval.cancel()



    def step_left(self):
        self.stepper_interval = Clock.schedule_interval(self.run_left_stepper, self.stepper_speed)

    def turn_slide_on(self):
        stepper.variable_speed_step(self.stepper_speed)

    def turn_stepper_off(self):
        stepper.disable_stepper()

    def turn_pan_on(self):
        stepper.variable_pan_step(self.pan_speed)

    def turn_pan_off(self):
        stepper.disable_stepper()

    def change_stepper_speed(self):
        self.ids['stepper_value_label'].text = "Slide: " + str(self.ids['stepper_speed_slider'].value)
        self.stepper_speed = float(self.ids['stepper_speed_slider'].value) / 1000.0

    def change_pan_speed(self):
        self.ids['pan_value_label'].text = "Pan: " + str(self.ids['pan_speed_slider'].value)
        self.pan_speed = float(self.ids['pan_speed_slider'].value) / 1000.0





    def checkButtons(self):
        self.program_interval = Clock.schedule_interval(self.readLimits, 0.1)
            
    def endProgram(self):
        controls.cleanup()
        App.get_running_app().stop()



class ProgramActions(Screen):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(ProgramActions, self).__init__(**kwargs)
        global globalSettings
        self.shutterTime = globalSettings.printShutterTime()
        
        self.aperture = globalSettings.printAperture()
        self.rampCount = 0
        self.exposureIndex = globalSettings.printCurrentExposure()
        self.servo_angle = "1"
        stepper.servo_position(1)


    def updateLabels(self):
        self.ids['shutter_time_label'].text = globalSettings.printShutterTime()

    def change_servo_angle(self):
        self.ids.servo_position_label = str(self.ids.servo_angle_slider.value)
        stepper.servo_position(self.ids.servo_angle_slider.value)

    def idle_servo(self):
        stepper.stop_servo()
        

    def increaseShutter(self):
        global globalSettings
        globalSettings.shutterTime += 0.1
        self.updateLabels()

    def decreaseShutter(self):
        global globalSettings
        globalSettings.shutterTime -= 0.1
        self.updateLabels()

    def increaseExposure(self):
        global globalSettings
        globalSettings.exposureIndex += 1
        self.ids['exposure_label'].text = globalSettings.printCurrentExposure()

    def decreaseExposure(self):
        global globalSettings
        globalSettings.exposureIndex -= 1
        self.ids['exposure_label'].text = globalSettings.printCurrentExposure()

    def increaseAperture(self):
        global globalSettings
        globalSettings.currentAperture -= 1
        self.ids['aperture_label'].text = globalSettings.printAperture()

    def decreaseAperture(self):
        global globalSettings
        globalSettings.currentAperture += 1
        self.ids['aperture_label'].text = globalSettings.printAperture()

    

    def checkSettings(self):
        global globalSettings

        if globalSettings.programElapsedTime > globalSettings.rampStart:
            self.rampCount += 1
            if self.rampCount % 2 == 0:
                globalSettings.shutterTime += 0.2
                print("ramp here")
            print("Start ramping!!")
        else: 
            timeLeft = globalSettings.rampStart - globalSettings.programElapsedTime
            print ("Time to ramp: " + str(timeLeft))

    def test_bulb(self):
        global globalSettings
        msTime = globalSettings.shutterTime * 1000
        delaySetting = "--wait-event=" + str(msTime) + "ms"
        print(delaySetting)
        call (["gphoto2","--set-config", "eosremoterelease=5", delaySetting, "--set-config", "eosremoterelease=4"])

    def test_shutter(self):
        call (["gphoto2","--capture-image"])

    def takePicture(self):
        global globalSettings
        msTime = globalSettings.shutterTime * 1000
        if globalSettings.rampActive:
            delaySetting = "--wait-event=" + str(msTime) + "ms"
            print(delaySetting)
            call (["gphoto2","--set-config", "eosremoterelease=5", delaySetting, "--set-config", "eosremoterelease=4"])
        else:
            call (["gphoto2","--capture-image"])  
        globalSettings.totalPictures += 1

    def runProgram(self, dt):
        global globalSettings
        globalSettings.programElapsedTime = time.time() - globalSettings.programStartTime
        if globalSettings.rampActive:
            self.checkSettings() 
        self.takePicture()
        if globalSettings.totalPictures > globalSettings.stopPicturePoint:
            self.program_interval.cancel()

    def startProgram(self):
        global globalSettings
        globalSettings.programStartTime = time.time()
        self.program_interval = Clock.schedule_interval(self.runProgram, globalSettings.interval)

    def endProgram(self):
        controls.cleanup()
        App.get_running_app().stop()


class ProgramRunning(Screen):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(ProgramRunning, self).__init__(**kwargs)
        global globalSettings

    def fire_shutter(self):
        call (["gphoto2","--capture-image"])

    def fire_bulb(self):
        msTime = globalSettings.shutterTime * 1000
        delaySetting = "--wait-event=" + str(msTime) + "ms"
        call (["gphoto2","--set-config", "eosremoterelease=5", delaySetting, "--set-config", "eosremoterelease=4"])

    def timelapse_interval(self, dt):
        global globalSettings
        controls.stepMotor(1000)
        if globalSettings.rampActive:
            self.fire_shutter()
        else:
            self.fire_bulb()

        print("run")
        globalSettings.totalPictures += 1
        self.ids['total_picture_count_label'].text = str(globalSettings.totalPictures)
        timeLeft = (time.time() - globalSettings.programStartTime) / 60
        timeLeft = globalSettings.eventDuration - timeLeft
        self.ids['time_remaining_label'].text = str(round(timeLeft,1)) + 'min'

    def start_program(self):
        global globalSettings
        globalSettings.programStartTime = time.time()
        self.program_interval = Clock.schedule_interval(self.timelapse_interval, globalSettings.interval)

    def stop_program(self):
        self.program_interval.cancel()

    def exit_program(self):
        controls.cleanup()
        App.get_running_app().stop()


class TimelapseApp(App):
    def build(self):
        return Manager()


if __name__ == '__main__':
    TimelapseApp().run()