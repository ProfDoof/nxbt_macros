from cmd2 import CommandSet, with_default_category
import cmd2
import app
import controller
from sv_controller import SVControllerMacroBuilder
from utils import CommandSetRegistrationException

@with_default_category('Scarlet/Violet Breeding')
class SVBreedingCommands(CommandSet):
    '''
    A set of commands designed to make breeding in Pokemon SV easier
    '''
    def __init__(self) -> None:
        super().__init__()

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

    def do_make_sandwich(self, _: cmd2.Statement):
        '''A feature I hope to add that will automatically make a sandwich that can be used to increase egg power'''
        self.cmd.poutput('Making a sandwich (but like... not really)')

    def do_check_basket(self, _: cmd2.Statement):
        '''Check the basket for an egg'''
        self.cmd.poutput('Checking the basket for eggs')
        self.controller.run_macro(SVControllerMacroBuilder().check_basket())
        egg_in_basket = self.cmd.read_input('Is there an egg in the basket? (Y/N) ')
        first = True
        
        while egg_in_basket.lower() == 'y':
            macro = SVControllerMacroBuilder() if first else SVControllerMacroBuilder().press_a().sleep(.5)
            first = False
            self.controller.run_macro(macro.grab_egg())
            egg_in_basket = self.cmd.read_input('Is there another egg in the basket? (Y/N) ')
        self.controller.run_macro(SVControllerMacroBuilder().stop_grabbing_eggs())
        