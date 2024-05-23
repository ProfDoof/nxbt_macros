from cmd2 import CommandSet, with_default_category
import cmd2
import app
from controller import Controller, ControllerMacroBuilder, ALL_BUTTONS
from utils import CommandSetRegistrationException

@with_default_category('Scarlet/Violet Breeding')
class ControllerCommands(CommandSet):
    macro: ControllerMacroBuilder | None

    '''
    A set of commands designed to make breeding in Pokemon SV easier
    '''
    @property
    def cmd(self) -> cmd2.Cmd:
        assert self._cmd
        return self._cmd


    @property
    def controller(self) -> Controller:
        assert self._cmd and isinstance(self._cmd, app.ControllerApp) and self._cmd.controller
        return self._cmd.controller

    def __init__(self) -> None:
        super().__init__()
        self.macro = None

    def on_register(self, cmd: 'cmd2.Cmd') -> None:
        if isinstance(cmd, app.ControllerApp) and cmd.controller is None:
            raise CommandSetRegistrationException('No controller is registered so we can not register these commands')
        return super().on_register(cmd)

    def do_sticks(self, _: cmd2.Statement):
        self.controller.stick_mode()


def get_press_button_func(name: str):
    def do_press_button(instance: ControllerCommands, _: cmd2.Statement):
        f'''Press the {name.upper()} button on your controller or add it to the current macro'''
        fname = f'press_{name}'
        if instance.macro is not None:
            instance.cmd.poutput('Adding A to the macro')
            getattr(instance.macro, fname)()
            return

        instance.cmd.poutput(f'Pressing {name}')
        instance.controller.run_macro(getattr(ControllerMacroBuilder(), fname)())

    return do_press_button


for name in ALL_BUTTONS.keys():
    # print(f'Setting up {name}')
    setattr(ControllerCommands, f'do_{name}', get_press_button_func(name))