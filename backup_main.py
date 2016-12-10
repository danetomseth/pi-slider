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
from subprocess import call
import time


appConfig = [2.8, 3.2, 3.5, 4, 4.5, 5, 5.6, 6.3, 7.1, 8, 9, 10, 11, 13, 14, 16, 18, 20, 22, 25, 29, 32]

expConfig = ["1/30","1/40","1/50","1/60","1/80","1/100","1/125","1/160","1/200","1/250","1/320","1/400","1/500","1/640","1/800","1/1000","1/1250","1/1600","1/2000","1/2500","1/3200","1/4000","1/5000","1/6400","1/8000"]

red = [1,0,0,1]
green = [0,1,0,1]
blue =  [0,0,1,1]
purple = [1,0,1,1]

globalSettings = 0

class Manager(ScreenManager):
    timelapse_screen = ObjectProperty(None)
    camera_screen = ObjectProperty(None)
    actions_screen = ObjectProperty(None)
    motor_settings = ObjectProperty(None)

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
        self.stopPicturePoint = 5;
    def returnVal(self):
        print(self.interval)

    def printInterval(self):
        return str(self.interval) + 's'

    def printClipDuration(self):
        clipDuration = ((self.eventDuration * 60) / self.interval) / 25
        return str(clipDuration) + "s"

    def printTotalPictures(self):
        # self.stopPicturePoint = (self.eventDuration * 60) / self.interval
        pictureCount = (self.eventDuration * 60) / self.interval
        return str(pictureCount)

    def printCurrentExposure(self):
        setValue = "shutterspeed="+str(self.exposureIndex)

        call (["gphoto2","--set-config-index", setValue])
        return "index: " + str(self.exposureIndex)

    def printPictureCount(self):
        return str(self.totalPictures)

    def printEventDuration(self):
        return "Event: " + str(self.eventDuration) + 'min'

    def printShutterTime(self):
        return "Exposure: " + str(self.shutterTime) + 's'

    def printRampStart(self):
        return str(self.rampStart / 60) + 'min'

    def printRamping(self):
        if self.rampActive:
            return "Ramping: ON"
        else:
            return "Ramping: OFF"

    def printRampDuration(self):
        return str(self.rampDuration / 60) + 'min'

    def printAperture(self):
        setValue = "aperture="+str(self.currentAperture)

        call (["gphoto2","--set-config-index", setValue])
        return "f/"+str(self.apertureOptions[self.currentAperture])

class MainWindow(BoxLayout):

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        



class TimelapseSettings(Screen):
    
    def __init__(self, **kwargs):
        super(TimelapseSettings, self).__init__(**kwargs)
        global globalSettings
        globalSettings = SettingsClass()
        self.interval_text = globalSettings.printInterval()
        self.clipDuration = globalSettings.printClipDuration()
        self.pictureCount = globalSettings.printTotalPictures()
        self.eventDuration = globalSettings.printEventDuration()
    def updateLabels(self):
        global globalSettings
        self.ids['interval_label'].text = globalSettings.printInterval()
        self.ids['clip_duration_label'].text = globalSettings.printClipDuration() 
        self.ids['picture_count_label'].text = globalSettings.printTotalPictures() 
        self.ids['event_duration_label'].text = globalSettings.printEventDuration() 

    def increaseInterval(self):
        global globalSettings
        globalSettings.interval += 0.5
        self.updateLabels()

    def decreaseInterval(self):
        global globalSettings
        globalSettings.interval -= 0.5
        self.updateLabels()

    def increaseDuration(self):
        global globalSettings
        globalSettings.eventDuration += 5
        self.updateLabels()

    def decreaseDuration(self):
        global globalSettings
        globalSettings.eventDuration -= 5
        self.updateLabels()

           

class SliderSettings(Screen):
    
    def __init__(self, **kwargs):
        super(SliderSettings, self).__init__(**kwargs)
        global globalSettings
        self.rampStartTime = globalSettings.printRampStart()
        self.rampDuration = globalSettings.printRampDuration()
        self.rampActive = globalSettings.printRamping()

    def updateLabels(self):
        self.ids['ramp_start_time_label'].text = globalSettings.printRampStart() 
        self.ids['ramp_duration_time_label'].text = globalSettings.printRampDuration()
        self.ids['ramping_label'].text = globalSettings.printRamping() 

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

    def rampingOn(self):
        global globalSettings
        globalSettings.rampActive = True
        self.updateLabels()

    def rampingOff(self):
        global globalSettings
        globalSettings.rampActive = False
        self.updateLabels()

    def toggleRamping(self):
        print "toggle"


class MotorSettings(Screen):
    def __init__(self, **kwargs):
        super(MotorSettings, self).__init__(**kwargs)
        global globalSettings



class ProgramActions(Screen):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(ProgramActions, self).__init__(**kwargs)
        global globalSettings
        self.shutterTime = globalSettings.printShutterTime()
        
        self.aperture = globalSettings.printAperture()
        self.rampCount = 0
        self.exposureIndex = globalSettings.printCurrentExposure()


    def updateLabels(self):
        self.ids['shutter_time_label'].text = globalSettings.printShutterTime()
        
        

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
            print "Start ramping!!"
        else: 
            timeLeft = globalSettings.rampStart - globalSettings.programElapsedTime
            print "Time to ramp: " + str(timeLeft)

    def takePicture(self):
        global globalSettings
        start_time = time.time()
        # call (["gphoto2","--set-config", "eosremoterelease=2"])
        # time.sleep(globalSettings.shutterTime)
        # call (["gphoto2","--set-config", "eosremoterelease=4"])
        msTime = globalSettings.shutterTime * 1000
        if globalSettings.rampActive:
            delaySetting = "--wait-event=" + str(msTime) + "ms"
            print(delaySetting)
            call (["gphoto2","--set-config", "eosremoterelease=5", delaySetting, "--set-config", "eosremoterelease=4"])
        # gphoto2 --set-config eosremoterelease=5 --wait-event=500ms --set-config eosremoterelease=4
        else:
            call (["gphoto2","--capture-image"])  
        elapsed_time = time.time() - start_time
        # print "Time: " + str(elapsed_time)
        globalSettings.totalPictures += 1
        self.ids['total_pictures_label'].text = globalSettings.printPictureCount()

        print("PICTURE!")

    def runProgram(self, dt):
        global globalSettings
        globalSettings.programElapsedTime = time.time() - globalSettings.programStartTime
        if globalSettings.rampActive:
            self.checkSettings() 
        # totalTime = (pictureCount * shutterInterval) + bulbRamp
        self.takePicture()
        if globalSettings.totalPictures > globalSettings.stopPicturePoint:
            self.program_interval.cancel()

    def startProgram(self):
        global globalSettings
        globalSettings.programStartTime = time.time()
        self.program_interval = Clock.schedule_interval(self.runProgram, globalSettings.interval)

    def endProgram(self):
        App.get_running_app().stop()

class InputBox(GridLayout):
    pass




class TimelapseApp(App):
    def build(self):
        # root = MainWindow()
        # time_settings = TimelapseSettings()
        # root.add_widget(time_settings)
        # slide_settings = SliderSettings()
        # root.add_widget(slide_settings)
        # program_actions = ProgramActions()
        # root.add_widget(program_actions)
        return Manager()


if __name__ == '__main__':
    TimelapseApp().run()