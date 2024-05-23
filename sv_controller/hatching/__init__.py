from cmd2 import CommandSet, with_default_category
import cmd2
from utils import CommandSetRegistrationException
import controller
import app
from sv_controller import SVControllerMacroBuilder
import time

@with_default_category('Scarlet/Violet Hatching')
class SVHatchCommands(CommandSet):
    def __init__(self) -> None:
        super().__init__()

        self.steps = 5120
        self.add_settable(cmd2.Settable('steps', int, 'Number of steps to hatch the first egg', self))

    def on_register(self, cmd: 'cmd2.Cmd') -> None:
        if isinstance(cmd, app.ControllerApp) and cmd.controller is None:
            raise CommandSetRegistrationException('No controller is registered so we can not register these commands')
        return super().on_register(cmd)


    @property
    def cmd(self) -> cmd2.Cmd:
        assert self._cmd
        return self._cmd


    @property
    def controller(self) -> controller.Controller:
        assert self._cmd and isinstance(self._cmd, app.ControllerApp) and self._cmd.controller
        return self._cmd.controller

    def do_hatch_box(self, _):
        '''Hatches an entire box of eggs in Pokemon SV'''
        self.cmd.poutput('Hatching an entire box of eggs')
        # 110 steps / second

        base_time = (self.steps / 110) + 5
        for macro in SVControllerMacroBuilder().hatch_box(base_time):
            time.sleep(3)
            self.controller.run_macro(macro)

    
    def open_boxes(self, _):
        '''Opens the boxes assuming that the present highlighted section is the bag'''
        self.cmd.poutput('Opening the boxes')
        self.controller.run_macro(SVControllerMacroBuilder().open_boxes())


    def release_egg(self, _):
        '''Release the highlighted egg'''
        self.cmd.poutput('Releasing the highlighted egg')
        self.controller.run_macro(SVControllerMacroBuilder()
            .press_a()
            .press_du(2)
            .press_a()
            .sleep(.5)
            .press_du()
            .press_a()
            .sleep(.5)
            .press_a()
        )


    def do_hatch_stack(self, _):
        '''Hatches a single stack of eggs in Pokemon SV'''
        self.cmd.poutput('Hatch a single stack of eggs!')


    def do_hatch_egg(self, _):
        '''Hatches a single egg in Pokemon SV'''
        self.cmd.poutput('Hatch an egg')
    