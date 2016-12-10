import RPi.GPIO as GPIO ## Import GPIO library
import time
import threading



#DC Vars
DC_pan_L = 27
DC_pan_R = 22 #P3
DC_slide_L = 4 #P7 step
DC_slide_R = 17 #P0 Dir


#Stepper vars
slide_step_pin = 4
slide_dir_pin = 17

pan_step_pin = 22
pan_slide_pin = 27

enable_pin = 25

slide_limit_left = 6
slide_limit_right = 13
motor_List = [DC_pan_L, DC_pan_R, DC_slide_L, DC_slide_R]

# Constants
LEFT = 0
RIGHT = 1


pan_amount = 0
pan_start_time = 0
pan_direction = 1
pan_home_set = False
pan_start_set = False
slide_delay_time = 500
slider_threading = 0
activeStepping = False
# step_size = 100




def gpio_setup():
	pass
	# GPIO.setmode(GPIO.BCM) ## Use board pin numbering
	# GPIO.setup(slide_limit_left, GPIO.IN, pull_up_down=GPIO.PUD_UP) ##setup gpio as out
	# GPIO.setup(slide_limit_right, GPIO.IN, pull_up_down=GPIO.PUD_UP) ##setup gpio as out
	# for x in motor_List:
	# 	print(x)
	# 	GPIO.setup(x, GPIO.OUT) ##setup gpio as out
	# 	GPIO.output(x, False) ##set initial state to low

def motor_on_off():
	moveMotor(DC_slide_L)

def stepMotor(step_size):
	GPIO.output(DC_slide_L, 1)
	# amt = step_size / 1000
	amt = (slide_delay_time / 1000)
	time.sleep(0.1)
	GPIO.output(DC_slide_L, 0)


def run_stepper():
	GPIO.output(enable_pin, 1)
	time.sleep(3)
	GPIO.output(enable_pin, 0)

def step_left(dt):
	GPIO.output(enable_pin, 1)
	GPIO.output(dir_pin, 1)
	GPIO.output(step_pin, 1)
	time.sleep(dt)
	GPIO.output(step_pin, 0)

def step_right(dt):
	GPIO.output(enable_pin, 1)
	GPIO.output(dir_pin, 0)
	GPIO.output(step_pin, 1)
	time.sleep(dt)
	GPIO.output(step_pin, 0)


def stop_stepper():
	GPIO.output(enable_pin, 0)
	GPIO.output(step_pin, 0)

def enable_motor():
	GPIO.output(enable_pin, 1)

def disable_motor():
	GPIO.output(enable_pin, 0)
	

def cleanup():
	GPIO.cleanup()
	pass

def check_left_limit():
	left_end = GPIO.input(slide_limit_left)
	if left_end == False:
		return True
	else:
		return False

def check_right_limit():
	right_end = GPIO.input(slide_limit_right)
	if right_end == False:
		return True
	else:
		return False

def checkLimits():
	limitStatus = True
	left_end = GPIO.input(slide_limit_left)
	right_end = GPIO.input(slide_limit_right)
	if left_end == False:
		limitStatus = False
	if right_end == False:
		limitStatus = False

	return limitStatus

def moveMotor(pin):
	GPIO.output(pin, 1)
	pass

def stopMotor(pin):
	GPIO.output(pin, 0)
	pass

def set_slide_speed(dir):
	global slide_delay_time
	if dir:
		slide_delay_time += 50
	else:
		slide_delay_time -= 50
	return str(slide_delay_time)
	#dir = True decrease speed


def find_home(side):
	slidePin = DC_slide_R
	if side == 'left':
		slidePin = DC_slide_L

	while checkLimits():
		step_right(0.02)
		time.sleep(0.02)

	# stopMotor(slidePin)

def slideLeft(amt):
	print("sliding")
	time.sleep(1)

def DC_pan_left():
	global pan_start_time
	global pan_direction
	if pan_start_set & (pan_home_set == False):
		pan_direction = 1 * -1
		stopMotor(DC_pan_R)
		moveMotor(DC_pan_L)
		pan_start_time = time.time()
		print("home set")
	else:
		print("nothing set")
		stopMotor(DC_pan_R)
		moveMotor(DC_pan_L)
		GPIO.output(DC_pan_L, 1)

def DC_pan_right():
	global pan_start_time
	global pan_direction
	if pan_start_set & (pan_home_set == False):
		pan_direction = 1
		stopMotor(DC_pan_L)
		moveMotor(DC_pan_R)
		pan_start_time = time.time()
	else:
		stopMotor(DC_pan_L)
		moveMotor(DC_pan_R)

def set_pan_start():
	global pan_start_set
	global pan_home_set
	pan_home_set = False
	pan_start_set = True

def set_pan_end():
	global pan_home_set
	global pan_amount
	pan_home_set = True
	pan_amount = (time.time() - pan_start_time) * pan_direction
	print("pan amount: "+str(pan_amount))

def move_delay(sec, state, pin):
	global slider_threading
	def func_wrapper():
		if state:
			moveMotor(pin)
			move_delay(sec, False, pin)
		else:
			stopMotor(pin)
			move_delay(sec, True, pin)
	slider_threading = threading.Timer(sec, func_wrapper)
	slider_threading.start()
	return slider_threading

def DC_slide_left():
    print("Slide L")
    time = slide_delay_time / 100
    stopMotor(DC_slide_R)
    moveMotor(DC_slide_L)
    # move_delay(time, True, DC_slide_L)
    # endReached = False

    # while endReached == False:
    # 	if checkLimits() == False:
    # 		endReached = True
    # 		slider_threading.cancel()
    GPIO.output(DC_slide_L, 1)

def DC_slide_right():
    print("Slide R")
    stopMotor(DC_slide_L)
    moveMotor(DC_slide_R)
    GPIO.output(DC_slide_R, 1)

def stop_slide():
	GPIO.output(DC_slide_L, False)
	GPIO.output(DC_slide_R, False)
	pass

def stop_pan():
	GPIO.output(DC_pan_L, False)
	GPIO.output(DC_pan_R, False)
	pass

def stop_motors():
    print("Stopping")
    stopMotor(DC_slide_L)
    stopMotor(DC_slide_R)
    stopMotor(DC_pan_L)
    stopMotor(DC_pan_R)

def end_pan_minus():
    print("in app")
