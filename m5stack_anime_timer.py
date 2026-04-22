"""
M5Stack Anime Timer
Device: M5StickC Plus2 / Core2
Language: MicroPython (UIFlow)

Simple timer with UI controls, animation and auto sleep.

Author: xgcode128
GitHub: https://github.com/xgcode128
TikTok: @xg_code
"""

import M5
from M5 import *
import time

state = "idle"
minutes = 0
seconds = 0
cursor = 0

frame = 0
img = None

last_tick = 0
anim_tick = 0
anim_until = 0
anim_active = False
img_visible = False

last_activity = 0
screen_sleep_ms = 15000
screen_on = True

total_set_seconds = 0

START = 0
RESET = 1
PLUS  = 2
MINUS = 3

BG = 0x081018
PANEL = 0x0D1722
LINE = 0x30465A
TEXT = 0xFFFFFF
SUB = 0x9FB3C8

BTN_BORDER = 0x2B4257
GREEN = 0x2FBF71
RED = 0xD64545
BLUE = 0x3B6EDC
YELLOW = 0xFFD166

PANEL_X = 12
PANEL_Y = 4
PANEL_W = 136
PANEL_H = 108

ANIM_X = 168
ANIM_Y = 36
IMG_W = 64
IMG_H = 64

def fmt():
    return "{:02d}:{:02d}".format(minutes, seconds)

def now_secs():
    return minutes * 60 + seconds

def mark_activity():
    global last_activity
    last_activity = time.ticks_ms()

def set_screen(level):
    global screen_on
    ok = False

    try:
        M5.Display.setBrightness(level)
        ok = True
    except:
        pass

    if not ok:
        try:
            M5.Lcd.setBrightness(level)
            ok = True
        except:
            pass

    if not ok and level == 0:
        M5.Lcd.fillScreen(0)

    screen_on = (level > 0)

def clear_image_area():
    M5.Lcd.fillRect(ANIM_X, ANIM_Y, IMG_W, IMG_H, BG)

def show_frame(n):
    global img, img_visible
    path = "/flash/res/img/{}.png".format(n)
    img = Widgets.Image(path, ANIM_X, ANIM_Y)
    img_visible = True

def hide_image():
    global img, img_visible
    img = None
    img_visible = False
    clear_image_area()

def wake_screen():
    if not screen_on:
        set_screen(100)
        draw_static()
        update_info()
        update_buttons()
        if img_visible:
            show_frame(frame)

def sleep_screen():
    if screen_on:
        set_screen(0)

def draw_button(x, y, w, h, label, selected, fill):
    border = YELLOW if selected else BTN_BORDER

    M5.Lcd.fillRoundRect(x, y, w, h, 4, fill)
    M5.Lcd.drawRoundRect(x, y, w, h, 4, border)

    if selected:
        M5.Lcd.drawRoundRect(x - 1, y - 1, w + 2, h + 2, 5, YELLOW)

    M5.Lcd.setTextSize(1)
    M5.Lcd.setTextColor(TEXT, fill)

    tx = x + max(2, (w - len(label) * 6) // 2)
    ty = y + max(2, (h - 8) // 2)
    M5.Lcd.setCursor(tx, ty)
    M5.Lcd.print(label)

def draw_static():
    M5.Lcd.fillScreen(BG)
    M5.Lcd.fillRoundRect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H, 6, PANEL)

    M5.Lcd.setTextSize(1)
    M5.Lcd.setTextColor(SUB, PANEL)
    M5.Lcd.setCursor(20, 8)
    M5.Lcd.print("Timer von @xg_code")

    M5.Lcd.drawLine(18, 24, 142, 24, LINE)
    M5.Lcd.drawLine(18, 74, 78, 74, LINE)

    clear_image_area()

def update_info():
    M5.Lcd.fillRect(18, 30, 60, 64, PANEL)

    M5.Lcd.setTextSize(3)
    M5.Lcd.setTextColor(TEXT, PANEL)
    M5.Lcd.setCursor(18, 38)
    M5.Lcd.print(fmt())

    M5.Lcd.setTextSize(1)
    if state == "idle":
        M5.Lcd.setTextColor(SUB, PANEL)
        status = "READY"
    elif state == "running":
        M5.Lcd.setTextColor(GREEN, PANEL)
        status = "RUN"
    else:
        M5.Lcd.setTextColor(YELLOW, PANEL)
        status = "PAUSE"

    M5.Lcd.setCursor(26, 84)
    M5.Lcd.print(status)

def update_buttons():
    start_label = "GO" if state != "running" else "PAUSE"

    draw_button(4,   118, 42, 14, start_label, cursor == START, GREEN)
    draw_button(52,  118, 42, 14, "RST",       cursor == RESET, RED)
    draw_button(100, 118, 18, 14, "+",         cursor == PLUS,  BLUE)
    draw_button(124, 118, 18, 14, "-",         cursor == MINUS, BLUE)

def start_anim():
    global anim_active, anim_until, anim_tick, frame
    anim_active = True
    anim_until = time.ticks_add(time.ticks_ms(), 10000)
    anim_tick = time.ticks_ms()
    frame = 0
    show_frame(frame)

def stop_anim():
    global anim_active, frame
    anim_active = False
    frame = 0
    hide_image()

def update_animation(now):
    global frame, anim_tick

    if not anim_active:
        return

    if time.ticks_diff(now, anim_until) >= 0:
        stop_anim()
        return

    if time.ticks_diff(now, anim_tick) < 180:
        return

    anim_tick = now
    frame = (frame + 1) % 28
    show_frame(frame)

def reset_timer():
    global state, minutes, seconds, cursor, total_set_seconds, last_tick
    state = "idle"
    minutes = 0
    seconds = 0
    cursor = 0
    total_set_seconds = 0
    last_tick = time.ticks_ms()
    stop_anim()
    draw_static()
    update_info()
    update_buttons()

def toggle_start():
    global state, total_set_seconds, last_tick

    if now_secs() <= 0:
        return

    if state == "idle":
        total_set_seconds = now_secs()
        state = "running"
        last_tick = time.ticks_ms()
        update_info()
        update_buttons()
        start_anim()

    elif state == "running":
        state = "paused"
        update_info()
        update_buttons()

    else:
        state = "running"
        last_tick = time.ticks_ms()
        update_info()
        update_buttons()

def action():
    global minutes, seconds, total_set_seconds

    if cursor == START:
        toggle_start()
        return

    if cursor == RESET:
        reset_timer()
        return

    if state == "idle":
        if cursor == PLUS:
            minutes = min(99, minutes + 1)
            seconds = 0
            total_set_seconds = now_secs()
        elif cursor == MINUS:
            minutes = max(0, minutes - 1)
            seconds = 0
            total_set_seconds = now_secs()

    update_info()
    update_buttons()

def alarm():
    for _ in range(3):
        M5.Speaker.tone(1200, 100)
        time.sleep_ms(140)
        M5.Speaker.tone(1600, 100)
        time.sleep_ms(140)

def update_sleep(now):
    if screen_on and time.ticks_diff(now, last_activity) >= screen_sleep_ms:
        sleep_screen()

def setup():
    global last_tick, anim_tick, last_activity

    M5.begin()
    Widgets.setRotation(1)

    last_tick = time.ticks_ms()
    anim_tick = time.ticks_ms()
    last_activity = time.ticks_ms()

    set_screen(100)
    draw_static()
    update_info()
    update_buttons()
    hide_image()

def loop():
    global cursor, last_tick, state, minutes, seconds

    M5.update()
    now = time.ticks_ms()

    a = BtnA.wasPressed()
    b = BtnB.wasPressed()
    c = BtnC.wasPressed()

    if a or b or c:
        mark_activity()
        wake_screen()

    if b:
        cursor = (cursor + 1) % 4
        update_buttons()

    if a:
        action()

    if c:
        reset_timer()

    if state == "running" and time.ticks_diff(now, last_tick) >= 1000:
        last_tick = now

        if seconds > 0:
            seconds -= 1
        elif minutes > 0:
            minutes -= 1
            seconds = 59

        if minutes == 0 and seconds == 0:
            state = "idle"
            update_info()
            update_buttons()
            start_anim()
            alarm()
        else:
            update_info()

    update_animation(now)
    update_sleep(now)
    time.sleep_ms(20)

setup()
while True:
    loop()
