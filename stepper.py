import RPi.GPIO as GPIO ## Import GPIO library
import time
import threading




#Stepper vars
slide_step_pin = 16
slide_dir_pin = 12

pan_step_pin = 20
pan_dir_pin = 21

enable_pin = 25

servo_pin = 18

slide_limit_left = 6
slide_limit_right = 13

output_List = [slide_dir_pin, slide_step_pin, pan_dir_pin, pan_step_pin, enable_pin]

# Constants
LEFT = False
RIGHT = True


pan_amount = 0
pan_start_time = 0
pan_home_set = False
pan_start_set = False
slide_delay_time = 500
slider_threading = 0
activeStepping = False
last_servo_position = 5
slide_speed = 0.01
slide_direction = LEFT
pan_direction = LEFT

# step_size = 100
GPIO.setmode(GPIO.BCM) ## Use board pin numbering

GPIO.setup(18, GPIO.OUT)
servo = GPIO.PWM(18, 100)
servo.start(5)


def gpio_setup():
	# GPIO.setmode(GPIO.BCM) ## Use board pin numbering
	GPIO.setup(slide_limit_left, GPIO.IN, pull_up_down=GPIO.PUD_UP) ##setup gpio as out
	GPIO.setup(slide_limit_right, GPIO.IN, pull_up_down=GPIO.PUD_UP) ##setup gpio as out
	for x in output_List:
		print(x)
		GPIO.setup(x, GPIO.OUT) ##setup gpio as out
		GPIO.output(x, False) ##set initial state to low

def motor_on_off():
	moveMotor(DC_slide_L)

def run_servo():
	servo.ChangeDutyCycle(2.5)  # turn towards 0 degree
	time.sleep(1) # sleep 1 second
	servo.ChangeDutyCycle(12.5) # turn towards 180 degree
	time.sleep(1) # sleep 1 second 
	servo.stop()

def servo_position(angle):
	global last_servo_position
	duty = float(angle) / 10.0 + 2.5
	last_servo_position = angle
	servo.ChangeDutyCycle(duty)

def variable_slide_step(step_speed, steps):
	step_count = int(steps)
	GPIO.output(enable_pin, 1)
	GPIO.output(slide_dir_pin, slide_direction)
	for x in range(step_count):
		if checkLimits() == False:
			print("Limit Hit")
			time.sleep(1)
			reset_slide_limit(step_speed)
			break
		GPIO.output(slide_step_pin, 1)
		time.sleep(step_speed)
		GPIO.output(slide_step_pin, 0)
		time.sleep(step_speed)
	GPIO.output(enable_pin, 0)


def ramp_slide_step(step_speed, steps):
	step_count = int(steps)
	GPIO.output(enable_pin, 1)
	GPIO.output(slide_dir_pin, slide_direction)
	start_speed = 0.03
	while start_speed > step_speed:
		GPIO.output(slide_step_pin, 1)
		time.sleep(start_speed)
		GPIO.output(slide_step_pin, 0)
		time.sleep(start_speed)
		if step_count % 2 == 0:
			start_speed = start_speed - 0.001
		step_count -= 1
		print(step_count)
		print(start_speed)
	for x in range(step_count):
		if checkLimits() == False:
			print("Limit Hit")
			time.sleep(1)
			reset_slide_limit(step_speed)
			break
		GPIO.output(slide_step_pin, 1)
		time.sleep(step_speed)
		GPIO.output(slide_step_pin, 0)
		time.sleep(step_speed)
	GPIO.output(enable_pin, 0)

def variable_pan_step(step_speed, steps):
	step_count = int(steps)
	GPIO.output(enable_pin, 1)
	GPIO.output(pan_dir_pin, pan_direction)
	for x in range(step_count):
		GPIO.output(pan_step_pin, 1)
		time.sleep(step_speed)
		GPIO.output(pan_step_pin, 0)
		time.sleep(step_speed)
	GPIO.output(enable_pin, 0)


def reset_slide_limit(step_speed):
	global slide_direction
	GPIO.output(enable_pin, 1)
	if slide_direction == False:
		slide_direction = True
		GPIO.output(slide_dir_pin, slide_direction)
	else:
		slide_direction = False
		GPIO.output(slide_dir_pin, slide_direction)

	for x in range(100):
		GPIO.output(slide_step_pin, 1)
		time.sleep(step_speed)
		GPIO.output(slide_step_pin, 0)
		time.sleep(step_speed)

	GPIO.output(enable_pin, 1)



def start_servo():
	servo.start(5)

def stop_servo():
	servo.ChangeDutyCycle(0)

def set_pan_dir(dir):
	GPIO.output(pan_dir_pin, dir)

def pan_step_on():
	GPIO.output(pan_step_pin, 1)

def pan_step_off():
	GPIO.output(pan_step_pin, 0)


def set_slide_direction(direction):
	global slide_direction
	slide_direction = direction
	print("direction: " + str(slide_direction))

def set_pan_direction(direction):
	global pan_direction
	pan_direction = direction
	print("direction: " + str(pan_direction))


def find_slide_home():
	global slide_direction
	GPIO.output(enable_pin, 1)
	GPIO.output(slide_dir_pin, slide_direction)
	while checkLimits():
		GPIO.output(slide_step_pin, 1)
		time.sleep(slide_speed)
		GPIO.output(slide_step_pin, 0)

	if slide_direction == LEFT:
		print("was left, now right")
		GPIO.output(slide_dir_pin, RIGHT)
	else:
		print("going left")
		GPIO.output(slide_dir_pin, LEFT)

	steps = 200

	for x in range(steps):
		GPIO.output(slide_step_pin, 1)
		time.sleep(slide_speed)
		GPIO.output(slide_step_pin, 0)
		time.sleep(slide_speed)

	GPIO.output(enable_pin, 1)
	print("Finished")

def set_slide_dir(dir):
	GPIO.output(slide_dir_pin, dir)

def slide_step_on():
	GPIO.output(slide_step_pin, 1)

def slide_step_off():
	GPIO.output(slide_step_pin, 0)	

def toggle_stepper(step_speed):
	print("start")

	# servo.stop()

def move_stepper(steps, step_speed, direction):
	GPIO.output(enable_pin, 1)
	GPIO.output(slide_dir_pin, direction)
	for x in range(steps):
		GPIO.output(slide_step_pin, 1)
		time.sleep(step_speed)
		GPIO.output(slide_step_pin, 0)
		time.sleep(step_speed)
	GPIO.output(enable_pin, 0)

def run_cycle_f(step_speed):
	for x in range(10):
		move_stepper(10, step_speed, RIGHT)
		servo_angle = last_servo_position + 2
		servo_position(servo_angle)
	servo.ChangeDutyCycle(0)

def run_cycle_r(step_speed):
	for x in range(10):
		move_stepper(10, step_speed, LEFT)
		servo_angle = last_servo_position - 2
		servo_position(servo_angle)
	servo.ChangeDutyCycle(0)

def stepMotors():
	step_count = 200
	GPIO.output(enable_pin, 1)
	for x in range(step_count):
		GPIO.output(slide_step_pin, 1)
		time.sleep(0.005)
		GPIO.output(slide_step_pin, 0)
		time.sleep(0.005)

	for x in range(step_count):
		GPIO.output(pan_step_pin, 1)
		time.sleep(0.005)
		GPIO.output(pan_step_pin, 0)
		time.sleep(0.005)

	GPIO.output(enable_pin, 0)





def enable_stepper():
	GPIO.output(enable_pin, 1)

def disable_stepper():
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























