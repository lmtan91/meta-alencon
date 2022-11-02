""" Uses the PIMC on the beaglebone black to monitor the power of the PODD

Holds two classes, a normal class and standalone thread version
of the class to monitor the power of the PODD and relay the status 
of the battery. Will shutdown if the PODD is powered off battery for
too long.
"""

import Adafruit_BBIO.ADC as ADC
from .pmic import Pmic  # Beaglebone's PMIC

import time
import logging
import threading

SYS_5V_PIN = "P9_39"
ADC_SCALAR = 1.8


class PowerMonitorThread(threading.Thread):

    def __init__(self):

        self.pmic = Pmic()
        ADC.setup()

        self.battery_shutdown_seconds = 10
        self.battery_shutdown_time_elapsed = False

        self.last_notify_second = 0  # time last notified
        self.notify_mod = int(self.battery_shutdown_seconds / 5.0)  # notify five times in log

        self.time_on_battery = 0  # time pmic has been on battery
        self.last_on_battery = time.time()  # time stamp of changed to battery power
        self.on_battery = False  # is pmic on battery power
        self.charging = False  # is pmic charging battery

        self.continue_monitoring = True

        self.logger = logging.getLogger('HUB.Peripheral_Monitor')

        self.on_battery = self.pmic.onBattery()  # find out if PMIC is initially on battery power
        if self.on_battery:
            self.logger.info('On Battery Power')
        else:
            self.logger.info('On Wired Power')

        self.charging = self.pmic.charging()  # find out if PMIC is initially charging battery
        if self.charging:
            self.logger.info('Charging Battery')
        else:
            self.logger.info('Not Charging Battery')

        super(PowerMonitorThread, self).__init__()
        self.start()

    def run(self):
        self.logger.info("Power Monitor Thread Started")
        self.continue_monitoring = True  # bool to continue monitoring or break out of loop
        self.battery_shutdown_time_elapsed = False  # bool to tell if max time on battery elapsed

        while self.continue_monitoring:
            read_sys_5V = ADC.read(SYS_5V_PIN) * ADC_SCALAR
            msg = 'Read scaled System 5V of {}'.format(read_sys_5V)
            # self.logger.info(msg)

            temp_on_battery = self.pmic.onBattery() | (
                        ADC.read(SYS_5V_PIN) < 0.5)  # record if PMIC is currently on battery
            temp_charging = self.pmic.charging()  # record if PMIC is currently charging battery

            if self.charging != temp_charging:  # log change in charging status
                msg = 'Started Charging Battery' if temp_charging else 'Stopped Charging Battery'
                self.logger.info(msg)

            if self.on_battery != temp_on_battery:  # log change in on battery status
                if temp_on_battery:
                    self.last_on_battery = time.time()
                else:
                    self.last_notify_second = 0  # if switched to on battery, start counting
                msg = 'Switched to Battery Power' if temp_on_battery else 'Switched to wired power'
                self.logger.info(msg)

            self.on_battery = temp_on_battery  # set global variables in prep for next loop
            self.charging = temp_charging

            if self.on_battery:
                self.time_on_battery = time.time() - self.last_on_battery  # find time since on battery

                if self.time_on_battery > self.battery_shutdown_seconds:  # if on battery for too long, break out of loop
                    self.battery_shutdown_time_elapsed = True
                    self.continue_monitoring = False
                    self.logger.info('On Battery power for %d secs - starting shutdown' % self.time_on_battery)

                elif int(self.time_on_battery) > (self.last_notify_second) and int(
                        self.time_on_battery) % self.notify_mod == 0:  # log intervals of time on battery
                    self.last_notify_second = int(self.time_on_battery)
                    self.logger.info('On Battery Power -- auto-shutdown in %d seconds' %
                                     (self.battery_shutdown_seconds - int(self.time_on_battery)))
                time.sleep(0.5)
            else:
                for i in range(10):
                    time.sleep(1.0)  # only check battery status every 10 seconds
                    if not self.continue_monitoring:
                        break

        self.logger.info("Power Monitor Thread Stopped")
        return self.battery_shutdown_time_elapsed

    def stop(self):
        self.continue_monitoring = False  # break out of monitoring loop


class PowerMonitor():

    def __init__(self):

        self.pmic = pmic.Pmic()

        self.battery_shutdown_seconds = 10
        self.battery_shutdown_time_elapsed = False

        self.last_notify_second = 0  # time last notified
        self.notify_mod = int(self.battery_shutdown_seconds / 5.0)  # notify five times in log

        self.time_on_battery = 0  # time pmic has been on battery
        self.last_on_battery = time.time()  # time stamp of changed to battery power
        self.on_battery = False  # is pmic on battery power
        self.charging = False  # is pmic charging battery

        self.continue_monitoring = True

        self.logger = logging.getLogger('PODD.Power_Monitor')

        self.on_battery = self.pmic.onBattery()  # find out if PMIC is initially on battery power
        if self.on_battery:
            self.logger.info('On Battery Power')
        else:
            self.logger.info('On Wired Power')

        self.charging = self.pmic.charging()  # find out if PMIC is initially charging battery
        if self.charging:
            self.logger.info('Charging Battery')
        else:
            self.logger.info('Not Charging Battery')

    def start_monitoring(self):
        self.continue_monitoring = True  # bool to continue monitoring or break out of loop
        self.battery_shutdown_time_elapsed = False  # bool to tell if max time on battery elapsed

        while self.continue_monitoring:
            temp_on_battery = self.pmic.onBattery()  # record if PMIC is currently on battery
            temp_charging = self.pmic.charging()  # record if PMIC is currently charging battery

            if self.charging != temp_charging:  # log change in charging status
                msg = 'Started Charging Battery' if temp_charging else 'Stopped Charging Battery'
                self.logger.info(msg)

            if self.on_battery != temp_on_battery:  # log change in on battery status
                if temp_on_battery:
                    self.last_on_battery = time.time()
                else:
                    self.last_notify_second = 0  # if switched to on battery, start counting
                msg = 'Switched to Battery Power' if temp_on_battery else 'Switched to wired power'
                self.logger.info(msg)

            self.on_battery = temp_on_battery  # set global variables in prep for next loop
            self.charging = temp_charging

            if self.on_battery:
                self.time_on_battery = time.time() - self.last_on_battery  # find time since on battery

                if self.time_on_battery > self.battery_shutdown_seconds:  # if on battery for too long, break out of loop
                    self.battery_shutdown_time_elapsed = True
                    self.continue_monitoring = False
                    self.logger.info('On Battery power for %d secs - starting shutdown' % self.time_on_battery)

                elif int(self.time_on_battery) > (self.last_notify_second) and int(
                        self.time_on_battery) % self.notify_mod == 0:  # log intervals of time on battery
                    self.last_notify_second = int(self.time_on_battery)
                    self.logger.info('On Battery Power -- auto-shutdown in %d seconds' %
                                     (self.battery_shutdown_seconds - int(self.time_on_battery)))
                time.sleep(0.5)
            else:
                for i in range(10):
                    time.sleep(1.0)  # only check battery status every 10 seconds
                    if not self.continue_monitoring:
                        break

        return self.battery_shutdown_time_elapsed

    def stop_monitoring(self):
        self.continue_monitoring = False  # break out of monitoring loop


if __name__ == '__main__':
    pm = PowerMonitor()
    pm.start_monitoring()
