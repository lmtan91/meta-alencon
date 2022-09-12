"""
PODD_factory_test

Usage:
    PODD_factory_test.py [--config_file=<cf>] [--log_path=<lp>] [--embedded_mode=<em>] [--log_level=<ll>]
    PODD_factory_test.py -h | --help

Options:
    -h --help                Show this screen.
    --config_file=<cf>       Base config file [default: PODD_factory_test_config.json]
    --log_path=<lp>          Directory to log data [default: ./log]
    --embedded_mode=<em>     Enable tests that can only run on the BBBI [default: True]
    --log_level=<ll>         Set the log level (debug, info, warning, and error) [default: info]

"""

import sys
import json
import os
import serial
import netifaces
import csv
import time
import logging
from docopt import docopt
from datetime import datetime
from collections import OrderedDict

logger_name = "PODD_FACTORY_TEST"


def setup_logger(log_path, log_level):
    # Create logger
    logging.basicConfig()
    log = logging.getLogger(logger_name)
    level = logging.getLevelName(log_level.upper())
    log.setLevel(level)
    fh = logging.FileHandler(os.path.join(log_path, "podd_factpyy_test.log"))

    fh.setLevel(level)
    lf = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(lf)

    # Add handlers to the logger
    log.addHandler(fh)


def is_interface_up(interface):
    addr = netifaces.ifaddresses(interface)
    return netifaces.AF_INET in addr


def test_ethernet(cf):
    import Adafruit_BBIO.GPIO as GPIO
    print("\n=== Ethernet Interfaces Test ===")

    ethernet_power_pin = cf["comms"]["ethernet"]["power_pin"]["pin"]
    help_gpio_setup_pin_list([cf["comms"]["ethernet"]["power_pin"]], GPIO.OUT)
    GPIO.output(ethernet_power_pin, GPIO.HIGH)
    time.sleep(5)

    num_interfaces = cf["comms"]["ethernet"]["num_interfaces"]
    ignore_list = set(cf["comms"]["ethernet"]["ignore_list"])

    # Use set logic to remove ignored interfaces from interface list
    interface_list = set(netifaces.interfaces())
    interface_list = list(interface_list - ignore_list)
    print("Interface List", interface_list)
    len_actual_interfaces = len(interface_list)

    input("Connect all interfaces to DHCP capable network then press enter:")
    if len_actual_interfaces is not num_interfaces:
        print("Error - Ethernet Interfaces Test: Number of interfaces found was ", len_actual_interfaces,
              " desired number was ", str(num_interfaces))
        return False

    test_result = True
    for interface in interface_list:
        print("Info - Ethernet Interfaces Test: Checking", interface)
        if not is_interface_up(interface):
            print("Error - Ethernet Interfaces Test: ", interface, " was not up")
            test_result = False

    return test_result


def test_serial_port(path_port):
    try:
        s = serial.Serial(path_port)
        s.close()
    except (OSError, serial.SerialException):
        return False
    return True


def test_usb_ports(cf):
    test_result = True
    usb_serial_path = cf["comms"]["usb_ports"]["device_name"]
    num_ports = cf["comms"]["usb_ports"]["num_ports"]

    print("\n=== USB Ports Test ===")

    input("Remove all USB devices then press enter:")
    if test_serial_port(usb_serial_path):
        print("Error - USB Ports Test: USB to serial converter found before test - " + usb_serial_path)
        return False

    for i in range(0, num_ports):
        input("Insert USB to serial addapter in to port " + str(i+1) + " then press enter:")
        if not test_serial_port(usb_serial_path):
            print("Error - USB Ports Test: USB Converter not found. Port " + str(i+1))
            test_result = False
        input("Remove USB to serial addapter in port " + str(i+1) + " then press enter:")
        if test_serial_port(usb_serial_path):
            print("Error - USB Ports Test: USB Converter found after removal. Port " + str(i+1))
            return False

    return test_result


def write_results(log_path, test_results):
    file_name = "podd_test_result-" + test_results["Start Time"] + ".csv"
    csv_file = os.path.join(log_path, file_name)
    test_results["Start Time"] = str(test_results["Start Time"])

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=test_results.keys())
            writer.writeheader()
            writer.writerow(test_results)
    except IOError:
        print("I/O error")


def help_gpio_setup_pin_list(pin_kv_list, setup_type):
    import Adafruit_BBIO.GPIO as GPIO
    for pin_kv in pin_kv_list:
        pull_up_down = GPIO.PUD_DOWN
        exec("pull_up_down = %s" % pin_kv["pull"])
        GPIO.setup(pin_kv["pin"], setup_type, pull_up_down=pull_up_down)


def help_gpio_output_pin_list(pin_kv_list, pin_value):
    import Adafruit_BBIO.GPIO as GPIO
    for pin_kv in pin_kv_list:
        GPIO.output(pin_kv["pin"], pin_value)


def test_RS_422(cf):
    import Adafruit_BBIO.GPIO as GPIO
    import serial

    print("\n=== RS-422 Test ===")

    # Setup control lines
    print("Setup control lines")
    de_dict = cf["comms"]["rs-422"]["control_DE"]
    re_dict = cf["comms"]["rs-422"]["control_RE"]
    help_gpio_setup_pin_list([de_dict, re_dict], GPIO.OUT)
    GPIO.output(de_dict["pin"], GPIO.HIGH)
    GPIO.output(re_dict["pin"], GPIO.LOW)

    # Setup serial port
    device = cf["comms"]["rs-422"]["device_name"]
    print("Opening port", device)
    ser = serial.Serial(device)

    # Loopback test
    print("Running loop back test")
    test_string = bytes("Loop back test!", "UTF-8")
    ser.write(test_string)
    time.sleep(0.5)
    bytes_read = ser.read(ser.in_waiting)

    if test_string == bytes_read:
        print("Test passed")
        return True
    else:
        print("Error - RS-422: Test failed. Tx: ", test_string, " - RX: ", bytes_read)
        return False


def test_status_leds(cf):
    import Adafruit_BBIO.GPIO as GPIO

    led_list_kv = cf["gpio"]["leds"]
    led_list_name = [pin_kv["name"] for pin_kv in led_list_kv]

    # Setup all pins as outputs
    help_gpio_setup_pin_list(led_list_kv, GPIO.OUT)

    print("\n=== Status LED Test ===")
    for pin_name in led_list_name:
        print(pin_name)
    print("\n")

    # Make sure all are off
    help_gpio_output_pin_list(led_list_kv, GPIO.LOW)
    all_off = input("Are all status LEDs off (y/n)?")
    if all_off.lower() != "y":
        print("Error - Status LED Test: LED stuck on")
        return False

    # Make sure all are on
    help_gpio_output_pin_list(led_list_kv, GPIO.HIGH)
    all_on = input("Are all status LEDs on (y/n)?")
    if all_on.lower() != "y":
        print("Error - Status LED Test: LED stuck off")
        return False

    # One by one test
    help_gpio_output_pin_list(led_list_kv, GPIO.LOW)
    test_result = True
    for led_kv in led_list_kv:
        GPIO.output(led_kv["pin"], GPIO.HIGH)
        pin_answer = input("Is only LED " + str(led_kv["name"]) + " on (y,n)?")
        GPIO.output(led_kv["pin"], GPIO.LOW)
        if pin_answer.lower() != "y":
            print("Error - Status LED Test: LED", led_kv["name"], "stuck off or tied to other LEDs")
            test_result = False

    return test_result


def test_switches(cf):
    import Adafruit_BBIO.GPIO as GPIO

    switch_list_kv = cf["gpio"]["switches"]

    # Setup all pins as inputs
    help_gpio_setup_pin_list(switch_list_kv, GPIO.IN)

    print("\n=== Switch Input Test ===")
    for switch_kv in switch_list_kv:
        print(switch_kv["name"])
    print("\n")

    # One by one test
    test_result = True
    for switch_kv in switch_list_kv:
        if GPIO.input(switch_kv["pin"]):
            print("Error - Switch Input", switch_kv["name"], " stuck on")
            test_result = False
            continue
        input("Assert switch " + str(switch_kv["name"]) + " then press enter")
        if GPIO.input(switch_kv["pin"]):
            input("Test passed. Release switch " + str(switch_kv["name"]) + " then press enter")
        else:
            input("Error - Switch Input: Test failed. Release switch " + str(switch_kv["name"]) + " then press enter")
            test_result = False

    return test_result


def test_battery():
    from pmic import Pmic

    print("\n=== Battery Test ===")
    input("Testing communication to PMIC:")
    pmic = Pmic()
    charging = pmic.charging()
    errors = pmic.battery_errors()

    # pmic.show_all_reg()

    # passed = not charging and not errors
    passed = not errors
    if passed:
        print("Battery test passed")
    # elif charging:
    #     print("Error - Battery: Test failed. Battery was detected")
    # else:
    #     print("Error - Battery: Test failed. Battery errors detected")

    # return not charging and not errors
    return not errors

def test_humidity_sensor():
    import subprocess
    print("\n=== Humidity Sensor Test ===")

    # Read part number from part number register
    bus = 1
    chip_addr = 0x43
    part_id_reg_addr = 0x00
    sys_ctrl_reg_addr = 0x10
    print("Reading part number from ES210")
    try:
        # Turn off low power / stand by --> Set to active mode
        subprocess.check_output(["i2cset", "-y", str(bus), str(chip_addr), str(sys_ctrl_reg_addr), str(0x00)])
        # Read part number
        part_number = int(
            subprocess.check_output(["i2cget", "-y", str(bus), str(chip_addr), str(part_id_reg_addr), "w"]).strip(), 16)
    except subprocess.CalledProcessError as grepexc:
        print("Error - Humidity Sensor: Test failed. Could not read part number. Error code", grepexc.returncode,
              grepexc.output)
        return False

    if part_number == 0x0210:
        print("Test passed")
        return True
    else:
        print("Error - Humidity Sensor: Test failed. Part number read:", str(part_number))
        return False


def test_rtc():
    import subprocess
    print("\n=== RTC Test ===")

    # Check that seconds register is changing
    bus = 1
    chip_addr = 0x68  # 0110 1000
    seconds_reg_addr = 0x00

    # Do two consecutive reads with a short delay in between
    try:
        time_1 = subprocess.check_output(["i2cget", "-y", "-f", str(bus), str(chip_addr), str(seconds_reg_addr)])
        time.sleep(1.1)
        time_2 = subprocess.check_output(["i2cget", "-y", "-f", str(bus), str(chip_addr), str(seconds_reg_addr)])
    except subprocess.CalledProcessError as grepexc:
        print("Error - RTC: Test failed. Could not write read from RTC. Error code", grepexc.returncode, grepexc.output)
        return False

    if time_1 != time_2:
        print("Test passed")
        return True
    else:
        print("Error - RTC: Test failed. Time1: ", str(time_1), " - Time2: ", str(time_2))
        return False


def test_wifi(cf):
    import Adafruit_BBIO.GPIO as GPIO

    print("\n=== WiFi Test ===")

    # Turn on the wifi module
    ethernet_power_pin = cf["comms"]["ethernet"]["power_pin"]["pin"]
    wifi_power_pin = cf["comms"]["wifi"]["power_pin"]["pin"]
    help_gpio_setup_pin_list([cf["comms"]["ethernet"]["power_pin"]], GPIO.OUT)
    help_gpio_setup_pin_list([cf["comms"]["wifi"]["power_pin"]], GPIO.OUT)
    print("Turning on the wifi module and waiting 7 seconds")
    GPIO.output(ethernet_power_pin, GPIO.HIGH)
    GPIO.output(wifi_power_pin, GPIO.LOW)
    time.sleep(5)
    GPIO.output(ethernet_power_pin, GPIO.HIGH)
    GPIO.output(wifi_power_pin, GPIO.HIGH)
    time.sleep(7)

    num_interfaces = cf["comms"]["wifi"]["num_interfaces"]
    ignore_list = set(cf["comms"]["wifi"]["ignore_list"])

    # Use set logic to remove ignored interfaces from interface list
    interface_list = set(netifaces.interfaces())
    interface_list = list(interface_list - ignore_list)
    print("Interface List", interface_list)
    len_actual_interfaces = len(interface_list)

    input("Connect all wifi interfaces to DHCP capable network then press enter:")
    if len_actual_interfaces is not num_interfaces:
        print("Error - Wifi Interfaces Test: Number of interfaces found was ", len_actual_interfaces,
              " desired number was ", str(num_interfaces))
        return False

    test_result = True
    for interface in interface_list:
        print("Info - Wifi Interfaces Test: Checking", interface)
        if not is_interface_up(interface):
            print("Error - Wifi Interfaces Test: ", interface, " was not up")
            test_result = False

    return test_result


def main(*args, **kwargs):
    if sys.version_info[:2] < (3, 4):
        print("Error: Python 3.4+ is required")
        sys.exit(-1)

    arg = docopt(__doc__)

    # Create specified log directory
    log_path = arg["--log_path"]
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # Setup a logger
    log_level = arg["--log_level"]
    setup_logger(log_path, log_level)

    # read config file
    config_file = arg["--config_file"]
    try:
        with open(config_file, 'r') as json_file:
            cf = json.load(json_file, object_pairs_hook=OrderedDict)
    except IOError:
        print("Error: Could not open " + config_file)
        sys.exit(2)

    test_results = OrderedDict()
    start_time = time.time()
    test_results["Start Time"] = datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
    if arg["--embedded_mode"].lower() == "true":
        test_results["Status Leds"] = test_status_leds(cf)
        test_results["Switch Inputs"] = test_switches(cf)
        test_results["Battery"] = test_battery()
        test_results["Humidity Sensor"] = test_humidity_sensor()
        test_results["RTC"] = test_rtc()
    test_results["RS-422"] = test_RS_422(cf)
    test_results["USB Ports"] = test_usb_ports(cf)
    if arg["--embedded_mode"].lower() == "true":
        test_results["WiFi"] = test_wifi(cf)
    test_results["Ethernet"] = test_ethernet(cf)
    test_results["Duration"] = time.time() - start_time

    print("\n\n")
    print(json.dumps(test_results, indent=4))

    write_results(log_path, test_results)


if __name__ == "__main__":
    main()
