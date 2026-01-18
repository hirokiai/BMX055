# BMX055.py
from machine import I2C
import time
import math

class BMX055:
    def __init__(self, i2c, addr_acc=0x19, addr_gyro=0x69, addr_mag=0x13):
        self.i2c = i2c
        self.addr_acc = addr_acc
        self.addr_gyro = addr_gyro
        self.addr_mag = addr_mag

        self.init_acc()
        self.init_gyro()
        self.init_mag()
        time.sleep_ms(300)

    # ----- ACCEL -----
    def init_acc(self):
        self.i2c.writeto_mem(self.addr_acc, 0x0F, bytes([0x03]))  # ±2g
        time.sleep_ms(50)
        self.i2c.writeto_mem(self.addr_acc, 0x10, bytes([0x08]))  # BW=7.81Hz
        time.sleep_ms(50)
        self.i2c.writeto_mem(self.addr_acc, 0x11, bytes([0x00]))  # normal mode
        time.sleep_ms(50)

    @property
    def accel(self):
        data = self.i2c.readfrom_mem(self.addr_acc, 0x02, 6)
        x = ((data[0] << 8) | data[1]) >> 4
        y = ((data[2] << 8) | data[3]) >> 4
        z = ((data[4] << 8) | data[5]) >> 4

        # 12bit 符号拡張
        if x > 2047: x -= 4096
        if y > 2047: y -= 4096
        if z > 2047: z -= 4096

        return x * 0.0098, y * 0.0098, z * 0.0098

    # ----- GYRO -----
    def init_gyro(self):
        self.i2c.writeto_mem(self.addr_gyro, 0x0F, bytes([0x04]))  # ±125°/s
        time.sleep_ms(50)
        self.i2c.writeto_mem(self.addr_gyro, 0x10, bytes([0x07]))  # ODR=100Hz
        time.sleep_ms(50)
        self.i2c.writeto_mem(self.addr_gyro, 0x11, bytes([0x00]))  # normal mode
        time.sleep_ms(50)

    @property
    def gyro(self):
        data = self.i2c.readfrom_mem(self.addr_gyro, 0x02, 6)
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]

        if x > 32767: x -= 65536
        if y > 32767: y -= 65536
        if z > 32767: z -= 65536

        return x * 0.0038, y * 0.0038, z * 0.0038

    # ----- MAG -----
    def init_mag(self):
        self.i2c.writeto_mem(self.addr_mag, 0x4B, bytes([0x83]))
        time.sleep_ms(50)
        self.i2c.writeto_mem(self.addr_mag, 0x4B, bytes([0x01]))
        time.sleep_ms(50)
        self.i2c.writeto_mem(self.addr_mag, 0x4C, bytes([0x00]))
        time.sleep_ms(50)
        self.i2c.writeto_mem(self.addr_mag, 0x4E, bytes([0x84]))
        time.sleep_ms(50)
        self.i2c.writeto_mem(self.addr_mag, 0x51, bytes([0x04]))
        time.sleep_ms(50)
        self.i2c.writeto_mem(self.addr_mag, 0x52, bytes([0x16]))
        time.sleep_ms(50)

    @property
    def mag(self):
        data = self.i2c.readfrom_mem(self.addr_mag, 0x42, 6)
        x = ((data[1] << 8) | (data[0] >> 3))
        y = ((data[3] << 8) | (data[2] >> 3))
        z = ((data[5] << 8) | (data[4] >> 1))

        if x > 4095: x -= 8192
        if y > 4095: y -= 8192
        if z > 16383: z -= 32768

        return x, y, z
    
    def orientation(self):
        ax, ay, az = self.accel
        mx, my, mz = self.mag

        roll = math.atan2(ay, az)
        pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az))

        mag_x = mx * math.cos(pitch) + mz * math.sin(pitch)
        mag_y = mx * math.sin(roll) * math.sin(pitch) + my * math.cos(roll) - mz * math.sin(roll) * math.cos(pitch)
        
        yaw = math.atan2(-mag_y, mag_x)

        roll = math.degrees(roll)
        pitch = math.degrees(pitch)
        yaw = math.degrees(yaw)

        return roll, pitch, yaw
