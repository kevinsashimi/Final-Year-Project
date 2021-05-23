import webbrowser
import time

from pyautogui import press


if __name__ == '__main__':
    webbrowser.open('https://geekprank.com/fake-virus/')
    time.sleep(2)
    press('f11')

