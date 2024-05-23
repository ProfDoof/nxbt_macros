from cmd2 import CommandSet, with_default_category
import cmd2
import app
import controller
from utils import CommandSetRegistrationException
import time

@with_default_category('Scarlet/Violet Breeding')
class SVTournamentCommands(CommandSet):
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

    
    def do_compete(self, _: cmd2.Statement):
        controller = self.controller
        cmd = self.cmd
        FIVE_TIMES_PER_SECOND = 30 * 5
        total = 0
        while True:
            for i in range(FIVE_TIMES_PER_SECOND):
                controller.nx.macro(controller.ci, '''
                A 0.1s
                0.1s
                ''')

                if i % (100 * 5) == 0:
                    cmd.poutput(f'We have pressed A {i + total} times now')

            total += FIVE_TIMES_PER_SECOND
            cmd.poutput('If you want to stop, press CTRL + C now')
            time.sleep(5)
            cmd.poutput('Starting back up')
