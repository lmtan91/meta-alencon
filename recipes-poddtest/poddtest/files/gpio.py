""" Controls all gpio peripherals on the PODD

Holds thread classes for LEDs and Reset Switchwatching
"""

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM

import logging
import threading
import time

### GPIO LEDs ###
BB_DE = "P9_30"
BB_RE = "P9_27"
BB_TX = "P9_23"
BB_RX = "P9_15"
BB_STATUS = "P9_12"

# PWM LEDs #
BB_RED = "P9_14"
BB_GREEN = "P9_16"
BB_BLUE = "P8_19"

# GPIO Buttons #
BB_FACTORY_RESET = "P8_7"

# Reset button timers #
RESET_FIRMWARE_TIMER = 20

class LEDThread(threading.Thread):

    def __init__(self):
        self.logger = logging.getLogger("HUB.Peripheral_Monitor")

        self.last_time_tx = 0.0
        self.last_time_rx = 0.0
        self.LED_on_time = 0.250
        self.LED_sleep_time = 0.100
        self.led_thread_on = True

        GPIO.setup(BB_DE, GPIO.OUT)
        GPIO.setup(BB_RE, GPIO.OUT)
        GPIO.setup(BB_TX, GPIO.OUT)
        GPIO.setup(BB_RX, GPIO.OUT)
        GPIO.setup(BB_STATUS, GPIO.OUT)

        PWM.start(BB_RED, 0, 1000)    #(pin number, pwm percentage, frequency)
        PWM.start(BB_GREEN, 100, 1000)    #(pin number, pwm percentage, frequency)
        PWM.start(BB_BLUE, 0, 1000)     #(pin number, pwm percentage, frequency)

        GPIO.output(BB_DE, GPIO.HIGH)
        GPIO.output(BB_RE, GPIO.LOW)
        GPIO.output(BB_TX, GPIO.LOW)
        GPIO.output(BB_RX, GPIO.LOW)
        GPIO.output(BB_STATUS, GPIO.HIGH)

        super(LEDThread, self).__init__()

        self.start()

    def run(self):
        self.logger.info("LED Thread Started")

        while self.led_thread_on:
            now = time.time()
            if now - self.last_time_rx < self.LED_on_time:
                GPIO.output(BB_RX, GPIO.HIGH)
            else:
                GPIO.output(BB_RX, GPIO.LOW)
            if now - self.last_time_tx < self.LED_on_time:
                GPIO.output(BB_TX, GPIO.HIGH)
            else:
                GPIO.output(BB_TX, GPIO.LOW)
            time.sleep(self.LED_sleep_time)

        self.logger.info("LED Thread Stopped")

    def stop(self):
        self.led_thread_on = False                              # break out of run loop

    def update_state(self, state):
        if state == "COMMS_GODD":
            PWM.set_duty_cycle(BB_RED, 0)
            PWM.set_duty_cycle(BB_GREEN, 0)
            PWM.set_duty_cycle(BB_BLUE, 100)
        elif state == "RUNNING":
            PWM.set_duty_cycle(BB_RED, 0 )
            PWM.set_duty_cycle(BB_GREEN, 100)
            PWM.set_duty_cycle(BB_BLUE, 0)
        elif state == "ERROR":
            PWM.set_duty_cycle(BB_RED, 100)
            PWM.set_duty_cycle(BB_GREEN, 0)
            PWM.set_duty_cycle(BB_BLUE, 0)

class ResetSwitchThread(threading.Thread):

    def __init__(self):
        self.logger = logging.getLogger("HUB.Peripheral_Monitor")
        self.watching_reset = True                  # boolean to break out of blocking reset watch
        self.reset_pressed = False                  # remembers if reset was pressed
        GPIO.setup(BB_FACTORY_RESET, GPIO.IN)
        super(ResetSwitchThread, self).__init__()
        self.start()

    def run(self):
        self.logger.info("Reset Switch Thread Started")

        self.watching_reset = True                       # reset watching bool
        self.reset_pressed = False                       # reset remembered reset value

        while self.watching_reset:
            if GPIO.input(BB_FACTORY_RESET):             # if reset switch is pressed
                self.reset_pressed = True                # set reset value
                self.watching_reset = False              # break out of loop

        self.logger.info("Reset Switch Thread Stopped")

        return self.reset_pressed                        # if loop breaks by reset_stop_watching, reset_pressed will be false

    def stop(self):
        self.watching_reset = False                             # break out of run loop


class Gpio():
    
    def __init__(self):
        self.watching_reset = True       # boolean to break out of blocking reset watch
        self.reset_pressed = False       # remembers if reset was pressed
        self.reset_firmware = False      # remembers if firmware needs to be reset
        GPIO.setup(BB_FACTORY_RESET, GPIO.IN)
        PWM.start(BB_RED, 0, 1000)                  #(pin number, pwm percentage, frequency)
        PWM.start(BB_GREEN, 0, 1000)                #(pin number, pwm percentage, frequency)
        PWM.start(BB_BLUE, 0, 1000)                 #(pin number, pwm percentage, frequency)

    def set_rgb_led(self, red, green, blue):      # values are percentages (0-100)
        PWM.set_duty_cycle(BB_RED, red)
        PWM.set_duty_cycle(BB_GREEN, green)
        PWM.set_duty_cycle(BB_BLUE, blue)

    def reset_start_watching(self):         
        self.watching_reset = True                       # reset watching bool
        self.reset_pressed = False                       # reset remembered reset value
        self.reset_firmware = False
        time_pressed = time.time()

        while self.watching_reset:
            if GPIO.input(BB_FACTORY_RESET):         # if reset switch is pressed
                self.reset_pressed = True
                pressed_duration = time.time() - time_pressed           
                if pressed_duration >  RESET_FIRMWARE_TIMER:
                    self.reset_firmware = True
                    self.watching_reset = False              # break out of loop
                
                led_value = int(time.time()) % 2
                self.set_rgb_led(0, int(not led_value)*100, led_value*100)

            else:
                time_pressed = time.time()              # Reset timer when not pressed              
                if self.reset_pressed:                  # If previously pressed and reset timer wasn't hit, break loop and reboot
                    self.watching_reset = False

        return (self.reset_pressed, self.reset_firmware)       # if loop breaks by reset_stop_watching, reset_pressed will be false

    def reset_stop_watching(self):
        self.watching_reset = False

if __name__ == "__main__":

    led_worker = Gpio()

    for x in range(0, 100):
        led_worker.set_rgb_led(x, 0, 0)
        time.sleep(0.01)

    for y in range(0, 100):
        led_worker.set_rgb_led(0, y, 0)
        time.sleep(0.01)

    for z in range(0, 100):
        led_worker.set_rgb_led(0, 0, z)
        time.sleep(0.01)

    led_worker.set_rgb_led(0, 0, 0)

    led_worker.reset_start_watching()
