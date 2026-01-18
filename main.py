# main.py
from machine import Pin, I2C
import time
from BMX055 import BMX055

# I2C0 → GP0=SDA, GP1=SCL
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

bmx = BMX055(i2c)

while True:
    ax, ay, az = bmx.accel
    gx, gy, gz = bmx.gyro
    mx, my, mz = bmx.mag

    print("ACC:", ax, ay, az)
    print("GYR:", gx, gy, gz)
    print("MAG:", mx, my, mz)
    print("----------------------")

    time.sleep_ms(200)
