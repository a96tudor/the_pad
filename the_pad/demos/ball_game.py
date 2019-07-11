from machine import SPI, Pin, I2C

import mcpnew
from ili934xhax import ILI9341, color565, color565n

spi = SPI(
    2,
    baudrate=40000000,
    miso=Pin(19),
    mosi=Pin(23),
    sck=Pin(18))
display = ILI9341(spi,
    cs=Pin(0),
    dc=Pin(15),
    rst=Pin(5))


I2C_SCL = 27
I2C_SDA = 32

i2c = I2C(scl = Pin(I2C_SCL), sda = Pin(I2C_SDA))

BUTTON_LEFT = 5
BUTTON_RIGHT = 6
BUTTON_UP = 7
BUTTON_DOWN = 4

pins = [BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT, BUTTON_UP]

io = mcpnew.MCP23017(i2c)


class Position:

    WIDTH = 10
    LENGTH = 10

    RESET_COLOR = color565(0, 0, 0)
    ACTUAL_COLOR = color565(255, 255, 255)

    def __init__(self, x, y, display):
        self.x = x
        self.y = y
        self.display = display
        self.last_acc = (0, 0)

    def reset(self):
        self.display.fill_rectangle(self.x, self.y, self.WIDTH, self.LENGTH,
                                    self.RESET_COLOR)

    def update(self, dx, dy):
        try_x = self.x + dx
        try_y = self.y + dy
        if try_x < 0 or try_x > self.display.width:
            dx *= -1
        if try_y < 0 or  try_y > self.display.height:
            dy *= -1
        self.x += dx
        self.y += dy
        self.last_acc = (dx, dy)

    def accelerate(self):
        self.update(*self.last_acc)

    def draw(self):
        self.display.fill_rectangle(self.x, self.y, self.WIDTH,
                                    self.LENGTH, self.ACTUAL_COLOR)


ball_pos = Position(100, 100, display)


def setup_pins_and_display():
    for p in pins:
        io.setup(p, mcpnew.IN)
        io.pullup(p, True)

    display.erase()
    display.set_pos(0, 0)
    display.width = 240
    display.height = 320

    display.fill_rectangle(0, 0, 240, 320, color565(0, 0, 0))
    draw_ball()


def draw_ball(dx=0, dy=0):
    ball_pos.reset()
    ball_pos.update(dx, dy)
    ball_pos.draw()
    print(ball_pos.x, ball_pos.y)


def show_text(txt):
    display.set_pos(30, 30)
    display.set_color(color565n(255, 255, 255), color565n(0, 0, 0))
    display.write(txt)


def run():
    setup_pins_and_display()    
    while True:
        if not io.input(BUTTON_UP):
            draw_ball(0, -5)
        elif not io.input(BUTTON_RIGHT):
            draw_ball(5, 0)
        elif not io.input(BUTTON_DOWN):
            draw_ball(0, 5)
        elif not io.input(BUTTON_LEFT):
            draw_ball(-5, 0)
        else:
            ball_pos.reset()
            ball_pos.accelerate()
            ball_pos.draw()
