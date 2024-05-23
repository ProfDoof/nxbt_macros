import nxbt
from controller import Controller
from controller.command import ControllerCommands
import cmd2
from typing import Any, Union
from sv_controller.breeding import SVBreedingCommands
from sv_controller.hatching import SVHatchCommands
from sv_controller.tournament import SVTournamentCommands
import argparse

class ControllerApp(cmd2.Cmd):
    '''
    A special prompt system designed to allow you to control your nintendo switch controller
    '''

    def __init__(self, *args: Any, **kwargs: Any):
        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        del shortcuts['!']
        del shortcuts['@']
        del shortcuts['@@']
        shortcuts.update({'~': 'set_game'})
        super().__init__(*args, auto_load_commands=False, shortcuts=shortcuts, allow_redirection=False, **kwargs)

        self.remove_settable('debug')
        self.remove_settable('echo')
        self.remove_settable('editor')
        self.remove_settable('feedback_to_output')
        self.remove_settable('quiet')

        # Delete builtins
        delattr(cmd2.Cmd, 'do_alias')
        delattr(cmd2.Cmd, 'do_edit')
        delattr(cmd2.Cmd, 'do_ipy')
        delattr(cmd2.Cmd, 'do_macro')
        delattr(cmd2.Cmd, 'do_py')
        delattr(cmd2.Cmd, 'do_run_pyscript')
        # delattr(cmd2.Cmd, 'do_run_script')
        delattr(cmd2.Cmd, 'do__relative_run_script')
        delattr(cmd2.Cmd, 'do_shell')
        delattr(cmd2.Cmd, 'do_run_script')

        self.commandsets = {
            'sv': {
                'breed': SVBreedingCommands(),
                'hatch': SVHatchCommands(),
                'direct': ControllerCommands(),
                'tourney': SVTournamentCommands(),
            },
            'none': {
                'direct': ControllerCommands(),
            }
        }
        self.nx = nxbt.Nxbt()
        self.current_game_name = 'sv'
        self.current_game = self.commandsets[self.current_game_name]
        self.action_set_name: str | None = None
        self.disable_command('stop', 'You can\'t stop a game action if there is no game action being taken')
        self.disable_command('del_controller', 'You must have one controller active to delete a controller')
        self._set_prompt()
        self.controller = None

    def _set_prompt(self):
        '''
        Sets the prompt to display the current game mode and the current action set
        '''

        if self.action_set_name is None:
            action_set = ''
        else:
            action_set = f'{self.action_set_name} '
        self.prompt = cmd2.ansi.style(f'({self.current_game_name}) {action_set}> ')
    

    def postcmd(self, stop: bool, statement: Union[cmd2.Statement, str]) -> bool:
        self._set_prompt()
        return super().postcmd(stop, statement)


    def game_options(self) -> list[str]:
        return list(self.commandsets.keys())


    @cmd2.with_category('Games')
    def do_create_controller(self, _):
        self.poutput('Creating the controller')
        controller_index: int = self.nx.create_controller(nxbt.PRO_CONTROLLER)
        y_n = 'n'
        try:
            y_n = self.read_input('Are you on the Change Grip/Order screen? (Y/N) ')
        except EOFError:
            pass 
        while y_n.lower() != 'y':
            try:
                y_n = self.read_input('Are you on the Change Grip/Order screen? (Y/N) ')
            except EOFError:
                pass
        
        self.poutput('Now waiting for a connection')
        self.nx.wait_for_connection(controller_index)
        self.disable_command('create_controller', 'You can only have one controller active at a time')
        self.enable_command('del_controller')
        self.controller = Controller(self.nx, controller_index)


    @cmd2.with_category('Games')
    def do_del_controller(self, _):
        if self.action_set_name is not None:
            self.poutput('You can not delete the controller while you have an active action')
            return

        assert self.controller
        self.nx.remove_controller(self.controller.ci)
        del self.controller
        self.controller = None
        self.disable_command('del_controller', 'You must have one controller active to delete a controller')
        self.enable_command('create_controller')

# controller = SVController(nx, controller_index)
# controller.run_macro(controller.create_macro()
#               .sleep(4)
#               .press_a()
#               .sleep(3)
#               .press_home()
#               .sleep(3)
#               .press_home()
#               .sleep(4))

# for macro in controller.create_macro().hatch_box():
#     time.sleep(5)
#     controller.run_macro(macro)
# # breed_eggs(controller_index, 30)

    set_game_parser = cmd2.Cmd2ArgumentParser()
    set_game_parser.add_argument('-g', '--game', choices_provider=game_options, help='The names of different games you have defined action sets for')


    @cmd2.with_category('Games') # type: ignore [arg-type]
    @cmd2.with_argparser(set_game_parser) # type: ignore [arg-type]
    def do_set_game(self, args: argparse.Namespace):
        '''
        Sets the current game action sets to the one that you input
        '''
        if args.game not in self.commandsets:
            self.poutput(f'{args.game} is not a valid option')
            return

        self.current_game = self.commandsets[args.game] 
        self.current_game_name = str(args.game)


    def current_game_action_choices(self) -> list[str]:
        return list(self.current_game.keys())


    start_parser = cmd2.Cmd2ArgumentParser()
    start_parser.add_argument('-a', '--action', choices_provider=current_game_action_choices, help='The names of different actions you can take for the current game')


    @cmd2.with_category('Games') # type: ignore [arg-type]
    @cmd2.with_argparser(start_parser) # type: ignore [arg-type]
    def do_start(self, args: argparse.Namespace) -> None:
        '''
        Enables the commands for doing the action you choose
        '''
        new_action_set_name = str(args.action)
        if self.action_set_name == new_action_set_name:
            return

        if new_action_set_name not in self.current_game:
            self.poutput(f'{new_action_set_name} is not a valid action for this game')
            return

        if self.action_set_name is not None:
            self.poutput(f'Unregistering the {self.action_set_name} action set')
            self.unregister_command_set(self.current_game[self.action_set_name])
        
        self.poutput(f'Registering the {new_action_set_name} action set')
        self.action_set_name = new_action_set_name
        self.register_command_set(self.current_game[self.action_set_name])
        self.enable_command('stop')


    @cmd2.with_category('Games')
    def do_stop(self, _):
        '''
        Stops a game action and goes back to the base prompt commands only
        '''
        if self.action_set_name is None:
            return
        
        self.unregister_command_set(self.current_game[self.action_set_name])
        self.disable_command('stop', 'You can\'t stop a game action if there is no game action being taken')
        self.action_set_name = None
