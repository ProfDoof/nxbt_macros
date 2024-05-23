from __future__ import annotations
import nxbt
from nxbt import Buttons
from enum import Flag, auto
from pynput import keyboard
from pynput.keyboard import KeyCode, Key
import queue
from queue import Empty
import threading
import time


class StickPosition(Flag):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()



class Sticks:
    # Quit
    Q = KeyCode.from_char('q')

    # Left stick
    W = KeyCode.from_char('w')
    S = KeyCode.from_char('s')
    A = KeyCode.from_char('a')
    D = KeyCode.from_char('d')

    # Right stick - Variant 1
    O = KeyCode.from_char('o')
    L = KeyCode.from_char('l')
    K = KeyCode.from_char('k')
    SEMICOLON = KeyCode.from_char(';')

    # Right stick - Variant 2
    UP = Key.up
    DOWN = Key.down
    LEFT = Key.left
    RIGHT = Key.right


    def __init__(self) -> None:
        self.left = StickPosition(0)
        self.right = StickPosition(0)

    def on_press(self, key: KeyCode | Key | None ):
        match key:
            case Sticks.W:
                self.left |= StickPosition.UP
            case Sticks.S:
                self.left |= StickPosition.DOWN
            case Sticks.A:
                self.left |= StickPosition.LEFT
            case Sticks.D:
                self.left |= StickPosition.RIGHT
            case Sticks.O | Sticks.UP:
                self.right |= StickPosition.UP
            case Sticks.L | Sticks.DOWN:
                self.right |= StickPosition.DOWN
            case Sticks.K | Sticks.LEFT:
                self.right |= StickPosition.LEFT
            case Sticks.SEMICOLON | Sticks.RIGHT:
                self.right |= StickPosition.RIGHT
            case Sticks.Q:
                return False
            case None | _:
                pass
        return True

    
    def on_release(self, key: KeyCode | Key | None):
        match key:
            case Sticks.W:
                self.left &= ~StickPosition.UP
            case Sticks.S:
                self.left &= ~StickPosition.DOWN
            case Sticks.A:
                self.left &= ~StickPosition.LEFT
            case Sticks.D:
                self.left &= ~StickPosition.RIGHT
            case Sticks.O | Sticks.UP:
                self.right &= ~StickPosition.UP
            case Sticks.L | Sticks.DOWN:
                self.right &= ~StickPosition.DOWN
            case Sticks.K | Sticks.LEFT:
                self.right &= ~StickPosition.LEFT
            case Sticks.SEMICOLON | Sticks.RIGHT:
                self.right &= ~StickPosition.RIGHT
            case None | _:
                pass
        return True


stick_state_q: queue.Queue[tuple[StickPosition, StickPosition] | None] = queue.Queue()


class StickModeThread(threading.Thread):
    def __init__(self):
        super().__init__()


    def run(self):
        sticks = Sticks()
        print('Created sticks')
        with keyboard.Events() as events:
            for event in events:
                match event:
                    case keyboard.Events.Press():
                        if not sticks.on_press(event.key):
                            break
                    case keyboard.Events.Release():
                        sticks.on_release(event.key)
                stick_state_q.put((sticks.left, sticks.right))
        stick_state_q.put(None)




class Controller:
    def __init__(self, nx: nxbt.Nxbt, controller_index: int) -> None:
        self.nx = nx
        self.ci = controller_index

    def create_macro(self) -> ControllerMacroBuilder:
        return ControllerMacroBuilder()

    def run_macro(self, macro: str | ControllerMacroBuilder, block: bool = True):
        if isinstance(macro, ControllerMacroBuilder):
            macro = macro.build()

        self.nx.macro(self.ci, macro, block=block)


    def generate_stick_pos_str(self, position: StickPosition):
        up = 0
        right = 0

        if StickPosition.UP in position:
            up += 100
        if StickPosition.DOWN in position:
            up -= 100
        if StickPosition.RIGHT in position:
            right += 100
        if StickPosition.LEFT in position:
            right -= 100

        print(f'Up: {up}, Right: {right}')
        return f'{right:0=+4d}{up:0=+4d}'

    def stick_mode(self):
        print('Starting stick mode')
        stick_mode_thread = StickModeThread()
        print('Created stick listener')
        stick_mode_thread.start()
        print('Started the stick listener')

        stick_state = (StickPosition(0), StickPosition(0))
        while True:
            try:
                stick_state = stick_state_q.get_nowait()
            except Empty:
                pass

            if stick_state is None:
                break

            macro = ""
            if bool(stick_state[0]):
                macro += f'L_STICK@{self.generate_stick_pos_str(stick_state[0])} '
            
            if bool(stick_state[1]):
                macro += f'R_STICK@{self.generate_stick_pos_str(stick_state[1])} '
            
            if bool(stick_state[0]) or bool(stick_state[1]):
                macro += '0.01s'
                print(f'Generated macro from {stick_state}')
                print(f'Adding macro to queue: {macro}')
                self.run_macro(macro, block=False)
                time.sleep(.01)
            else:
                print('Sleeping to wait for change in value')
                time.sleep(.25)
        stick_mode_thread.join()


ALL_BUTTONS = {
    'a': Buttons.A,
    'b': Buttons.B,
    'x': Buttons.X,
    'y': Buttons.Y,
    'capture': Buttons.CAPTURE,
    'dd': Buttons.DPAD_DOWN,
    'dl': Buttons.DPAD_LEFT,
    'dr': Buttons.DPAD_RIGHT,
    'du': Buttons.DPAD_UP,
    'home': Buttons.HOME,
    'l': Buttons.L,
    'lsp': Buttons.L_STICK_PRESS,
    'r': Buttons.R,
    'rsp': Buttons.R_STICK_PRESS,
    'zl': Buttons.ZL,
    'zr': Buttons.ZR,
    'minus': Buttons.MINUS,
    'plus': Buttons.PLUS,
}

class ControllerMacroBuilder:
    def __init__(self) -> None:
        self.action_list: list[str] = []
    
    def press(self, button: str):
        print(f'Pressing {button}')
        self.action_list.append(f'{button} 0.1s')
        self.action_list.append(f'1s')
        return self

    def sleep(self, how_long: float):
        self.action_list.append(f'{how_long:.1f}s')
        return self

    def build(self):
        return '\n'.join(self.action_list)


def get_button_func(button: str):
    def press_button(self: ControllerMacroBuilder, repeat: int = 1) -> ControllerMacroBuilder:
        for i in range(1, repeat + 1):
            self.press(button)
            if repeat < i:
                self.sleep(.5)

        return self

    return press_button


for name, button in ALL_BUTTONS.items():
    setattr(ControllerMacroBuilder, f'press_{name}', get_button_func(button))

# 