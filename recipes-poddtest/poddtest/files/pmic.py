""" Interfaces with the Beaglebone PMIC TPS65217

Read some values from the PMIC and print out what we find
example i2cget -y -f  0 0x24 0x3
"""

import subprocess

I2C_DEVICE = 0
CHIP_ADDRESS = 0x24

# register addresses we are interested in
PPATH_REG = 0x1
CHG0_REG = 0x3
CHG1_REG = 0x4
CHG2_REG = 0x5
CHG3_REG = 0x6
STATUS_REG = 0xA
PGOOD_REG = 0xC

# initial values of each register
PPATH_INIT = 0x3f
CHG0_INIT = 0x08
CHG1_INIT = 0xb1
CHG2_INIT = 0x98
CHG3_INIT = 0xf2
STATUS_INIT = 0x88
PGOOD_INIT = 0x7f

# some helpful bitmasks
STATUS_AC = 1 << 3
STATUS_USB = 1 << 2
CHGCONFIG0_ACTIVE = 1 << 3  # we are charging the battery
CHGCONFIG0_CHGTOUT = 1 << 2  # Charge timeout
CHGCONFIG0_PCHGTOUT = 1 << 1  # Precharge timeout
CHGCONFIG0_BATTEMP = 1 << 0  # No temperature sensor detected or battery temperature outside valid charging range

# these labels are interpreted from the TPS65217 datasheet
PPATH_LABELS = ["USB input current limit", "AC input current limit", "Enable USB", "Enable AC", "USB Sink", "AC Sink"]
CHG0_LABELS = ["Temp sense error", "Pre-charge Timedout", "Charge Timedout", "Active (charging)",
               "Charge Termination Current", "Thermal Suspend", "DPPM Reduction", "Thermal Regulation"]
CHG1_LABELS = ["Charger enabled", "Suspend charge", "Charging terminator off", "Charger Reset", "NTC resistance type",
               "Safety timer enabled", "Charge safety time"]
CHG2_LABELS = [None, "Charge voltage"]
CHG3_LABELS = ["Temperature range", None, "Charge current setting"]
STATUS_LABELS = ["Push Button", None, "USB Power", "AC Power", None, "OFF bit"]
PGOOD_LABELS = ["LDO2 power-good", "LDO1 power-good", "DCDC3 power-good", "DCDC2 power-good", "DCDC1 power-good",
                "LDO4 power-good", "LDO3 power-good"]

# these are the corresponding number of bits to the labels
PPATH_BITNUM = [2, 2, 1, 1, 1, 1]
CHG0_BITNUM = [1, 1, 1, 1, 1, 1, 1, 1]
CHG1_BITNUM = [1, 1, 1, 1, 1, 1, 2]
CHG2_BITNUM = [3, 2]
CHG3_BITNUM = [1, 5, 2]
STATUS_BITNUM = [1, 1, 1, 1, 3, 1]
PGOOD_BITNUM = [1, 1, 1, 1, 1, 1, 1]

pmic_regs = {
    "POWER PATH CONTROL": {
        "Register": PPATH_REG,
        "Labels": PPATH_LABELS,
        "BitNum": PPATH_BITNUM
    },
    "CHARGER REGISTER 0": {
        "Register": CHG0_REG,
        "Labels": CHG0_LABELS,
        "BitNum": CHG0_BITNUM
    },
    "CHARGER REGISTER 1": {
        "Register": CHG1_REG,
        "Labels": CHG1_LABELS,
        "BitNum": CHG1_BITNUM
    },
    "CHARGER REGISTER 2": {
        "Register": CHG2_REG,
        "Labels": CHG2_LABELS,
        "BitNum": CHG2_BITNUM
    },
    "CHARGER REGISTER 3": {
        "Register": CHG3_REG,
        "Labels": CHG3_LABELS,
        "BitNum": CHG3_BITNUM
    },
    "STATUS": {
        "Register": STATUS_REG,
        "Labels": STATUS_LABELS,
        "BitNum": STATUS_BITNUM
    },
    "POWER GOOD": {
        "Register": PGOOD_REG,
        "Labels": PGOOD_LABELS,
        "BitNum": PGOOD_BITNUM
    }
}


class Pmic():

    def __init__(self):
        self.set(PPATH_REG, PPATH_INIT)
        self.set(CHG0_REG, CHG0_INIT)
        self.set(CHG1_REG, CHG1_INIT)
        self.set(CHG2_REG, CHG2_INIT)
        self.set(CHG3_REG, CHG3_INIT)
        self.set(STATUS_REG, STATUS_INIT)
        self.set(PGOOD_REG, PGOOD_INIT)

    def show_all_reg(self):
        for key in sorted(pmic_regs):
            title = key
            reg = pmic_regs[key]["Register"]
            labels = pmic_regs[key]["Labels"]
            bitNum = pmic_regs[key]["BitNum"]
            self.show_reg(reg, title, labels, bitNum)

    # query a register, print out value breakdown
    def show_reg(self, reg, title, labels, bitNum):
        val = self.get(reg)
        print()
        print("%s: r[0x%x]=0x%x" % (title, reg, val))
        self.describe_bits(val, labels, bitNum)
        print()

    # get the I2C register, strip off \n and cast to int from hex
    # -y means non-interactive mode (just do it!)
    # -f forces the connection
    def get(self, reg=0):
        return int(subprocess.check_output(
            ["i2cget", "-y", "-f", str(I2C_DEVICE), str(CHIP_ADDRESS), str(reg)]).strip(), 16)

    def set(self, reg=0, value=0):
        subprocess.run(["i2cset", "-y", "-f", str(I2C_DEVICE), str(CHIP_ADDRESS), str(reg), str(value)])

    # display value of each bit in the register, along with its label
    def describe_bits(self, val, labels, bitNum):
        bit_counter = 0
        for x in range(0, len(labels)):  # Look through all labels
            raw_label_value = 0  # Make a variable to store raw value
            for y in range(0, bitNum[x]):  # Look through number of bits corresponding to that label
                raw_label_value += (((val >> bit_counter) & 1) << y)  # Construct raw data from reg
                bit_counter += 1

            if not labels[x]:  # skip None labels
                continue
            label_value = self.bit_interpreter(labels[x], raw_label_value)  # Interperet the raw value

            print("%s = %s" % (labels[x], label_value))  # Print the interpreted value

    def bit_interpreter(self, label, raw_value):
        if label == PPATH_LABELS[0]:
            if raw_value == 0:
                return "100 mA"
            elif raw_value == 1:
                return "500 mA"
            elif raw_value == 2:
                return "1300 mA"
            elif raw_value == 3:
                return "1800 mA"
        elif label == PPATH_LABELS[1]:
            if raw_value == 0:
                return "100 mA"
            elif raw_value == 1:
                return "500 mA"
            elif raw_value == 2:
                return "1300 mA"
            elif raw_value == 3:
                return "2500 mA"
        elif label == CHG1_LABELS[4]:
            if raw_value == 0:
                return "100k (B = 3960)"
            elif raw_value == 1:
                return "10k (B = 3480)"
        elif label == CHG1_LABELS[6]:
            if raw_value == 0:
                return "4 hours"
            elif raw_value == 1:
                return "5 hours"
            elif raw_value == 2:
                return "6 hours"
            elif raw_value == 3:
                return "8 hours"
        elif label == CHG2_LABELS[1]:
            if raw_value == 0:
                return "4.1 V"
            elif raw_value == 1:
                return "4.15 V"
            elif raw_value == 2:
                return "4.2V"
            elif raw_value == 3:
                return "4.2V"
        elif label == CHG3_LABELS[0]:
            if raw_value == 0:
                return "0 to 45 degrees Celsius"
            elif raw_value == 1:
                return "0 to 60 degrees Celsius"
        elif label == CHG3_LABELS[2]:
            if raw_value == 0:
                return "300 mA"
            elif raw_value == 1:
                return "400 mA"
            elif raw_value == 2:
                return "500 mA"
            elif raw_value == 3:
                return "700 mA"
        else:
            if raw_value == 0:
                return "False"
            elif raw_value == 1:
                return "True"

    # specific helpers
    def onBattery(self):
        return self.get(STATUS_REG) & (STATUS_AC | STATUS_USB) == 0

    def charging(self):
        return self.get(CHG0_REG) & CHGCONFIG0_ACTIVE != 0

    def battery_errors(self):
        return self.get(CHG0_REG) & (CHGCONFIG0_CHGTOUT | CHGCONFIG0_PCHGTOUT | CHGCONFIG0_BATTEMP) != 0


if __name__ == "__main__":
    power = Pmic()

    print("Querying Beaglebone Black Power Management IC on i2c-%s device 0x%x" % (I2C_DEVICE, CHIP_ADDRESS))

    print("On battery power only? %d\r\n" % power.onBattery())
    print("Charging Battery? %d\r\n" % power.charging())

    power.show_all_reg()
