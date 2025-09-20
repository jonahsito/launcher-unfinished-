import os
import subprocess
import random
import colorsys
import msvcrt
import pygame
import time

pygame.mixer.init()
key_sound = pygame.mixer.Sound("key.wav")
enter_sound = pygame.mixer.Sound("enter.wav")
backspace_sound = pygame.mixer.Sound("backspace.wav")

ambient_file = "ambient_loop.wav"
ambient_sound = None
ambient_muted = True
if os.path.isfile(ambient_file):
    ambient_sound = pygame.mixer.Sound(ambient_file)
    ambient_sound.set_volume(0.2)
    ambient_sound.play(-1)
    ambient_muted = False

# 🔹 Only keep Slot Machine
projects = ["Slot Machine"]

symbols = ["✦", "❖", "✧", "✪", "★", "◇", "☾"]
SATURATION = 0.5
VALUE = 0.8

def hsv_to_ansi(h, s, v):
    r, g, b = [int(x*255) for x in colorsys.hsv_to_rgb(h, s, v)]
    return f"\033[38;2;{r};{g};{b}m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def generate_hues(n):
    base_hue = random.random()
    return [(base_hue + random.uniform(-0.05, 0.05)) % 1 for _ in range(n)]

def print_header(hues):
    sym = random.choice(symbols)
    print(hsv_to_ansi(hues[0], SATURATION, VALUE) + sym * 10)
    print(hsv_to_ansi(hues[1], SATURATION, VALUE) + "🌀 xnieu 🌀")
    print(hsv_to_ansi(hues[2], SATURATION, VALUE) + sym * 10)
    if random.random() < 0.5:
        print(hsv_to_ansi(hues[3], SATURATION, VALUE) + ":3\n")

def print_menu(hues):
    for i, project in enumerate(projects, start=1):
        color = hsv_to_ansi(hues[i % len(hues)], SATURATION, VALUE)
        sym = random.choice(symbols)
        print(f"{color}{sym} [{i}] {project} {sym}")
    print("\nType a project number and press Enter, or type M to toggle ambient music.")

def launch_project(choice):
    filename = f"projects/{projects[choice-1].replace(' ', '_')}.py"
    if os.path.isfile(filename):
        try:
            result = subprocess.run(["python", filename], capture_output=True, text=True)
            if result.returncode != 0:
                log_file = "error_log.txt"
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(result.stderr)

                print("\n😺 Oops! Something went wrong while running your project.")
                print("Would you like to see the error log? (y/n) ", end="", flush=True)

                while True:
                    answer = input().strip().lower()
                    if answer == 'y':
                        os.system(f"notepad {log_file}")
                        break
                    elif answer == 'n':
                        break
                    else:
                        print("Please type 'y' or 'n': ", end="", flush=True)
        except Exception as e:
            log_file = "error_log.txt"
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(str(e))
            print("\n😺 Oops! Something went wrong while running your project.")
            print("Would you like to see the error log? (y/n) ", end="", flush=True)
            while True:
                answer = input().strip().lower()
                if answer == 'y':
                    os.system(f"notepad {log_file}")
                    break
                elif answer == 'n':
                    break
                else:
                    print("Please type 'y' or 'n': ", end="", flush=True)
    else:
        print("\033[31mFile not found! Make sure the .py exists in the projects folder.")

def main():
    global ambient_muted
    user_input = ""
    while True:
        hues = generate_hues(len(projects) + 5)
        clear()
        print_header(hues)
        print_menu(hues)
        print("\n[0] Exit")
        print("\nPick a project number: " + user_input, end="", flush=True)

        while True:
            time.sleep(0.02)
            print("\rPick a project number: " + user_input + " " * 10, end="", flush=True)

            if msvcrt.kbhit():
                key = msvcrt.getwch()
                if key == '\r':
                    enter_sound.play()
                    print()
                    if user_input.strip() != "":
                        if user_input.strip().lower() == 'm' and ambient_sound:
                            ambient_muted = not ambient_muted
                            if ambient_muted:
                                ambient_sound.stop()
                            else:
                                ambient_sound.play(-1)
                            print(f"Ambient music {'muted' if ambient_muted else 'unmuted'}!")
                        else:
                            try:
                                choice = int(user_input)
                                if choice == 0:
                                    return
                                elif 1 <= choice <= len(projects):
                                    launch_project(choice)
                                else:
                                    print("\033[31mInvalid choice!")
                            except ValueError:
                                print("\033[31mPlease enter a valid number or M.")
                    user_input = ""
                    break
                elif key == '\b':
                    if user_input:
                        user_input = user_input[:-1]
                        backspace_sound.play()
                else:
                    user_input += key
                    key_sound.play()

if __name__ == "__main__":
    main()
