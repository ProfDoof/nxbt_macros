from __future__ import annotations
from controller import ControllerMacroBuilder

class SVControllerMacroBuilder(ControllerMacroBuilder):
    def __init__(self) -> None:
        super().__init__()


    def dash_circle(self, how_long: float):
        print('Dashing in a circle')
        self.action_list.append('L_STICK@+100+000 0.5s')
        self.action_list.append('L_STICK@+100+000 L_STICK_PRESS 0.1s')
        self.action_list.append(f'L_STICK@+100+000 {how_long:.1f}s')
        return self


    def hatch_egg(self) -> SVControllerMacroBuilder:
        print('Oh?')
        self.press_a()
        self.sleep(20)
        print('Something hatched!')
        return self.press_a()

    def hatch_eggs(self, base_time: float) -> SVControllerMacroBuilder:
        self.dash_circle(base_time)
        self.sleep(5)
        for _ in range(4):
            self.hatch_egg()
            self.sleep(5)
            self.dash_circle(16)
            self.sleep(3)
        
        return self.hatch_egg()


    def check_basket(self) -> SVControllerMacroBuilder:
        return self.press_a().sleep(.5).press_a().sleep(.5)


    def grab_egg(self) -> SVControllerMacroBuilder:
        self.press_a()
        self.sleep(.5)
        self.press_a()
        self.sleep(.5)
        self.press_a()
        return self.sleep(.5)


    def stop_grabbing_eggs(self) -> SVControllerMacroBuilder:
        self.press_a()
        return self.sleep(.5)


    def open_boxes(self) -> SVControllerMacroBuilder:
        print(f'Opening the boxes')
        # Open Rotom Phone Menu
        self.press_x()
        self.sleep(1)

        # Navigate to boxes assuming we start at Bag
        self.press_dd(1)
        self.press_a()
        return self.sleep(4)

        # We start in the top left corner of the box

    def close_boxes(self):
        print('Exiting the boxes')
        self.press_b()

        self.sleep(4)
        print('Move back to the bag button to leave us in a sane state')
        self.press_du(1)

        print('Exit the Rotom phone menu')
        self.press_b()
        return self.sleep(2)

    def grab_egg_stack(self):
        print('Grabbing a stack of eggs')
        # Activate selection box
        self.press_minus().sleep(.5)

        # Select column
        self.press_dd(4).sleep(.5)

        # Activate selection
        return self.press_a().sleep(.5)
    
    def hatch_box(self, base_time: float = 60.0, open_box_first: bool = True) -> list[SVControllerMacroBuilder]:
        macros: list[SVControllerMacroBuilder] = []
        macros.append(SVControllerMacroBuilder())
        if open_box_first:
            macros[-1].open_boxes()
        
        for batch in range(6):
            print(f'Grabbing batch {batch}')
            
            # Grab the stack of eggs we are about to hatch
            macros[-1].grab_egg_stack()

            # Go to the party so we can hatch these eggs
            macros[-1].press_dl(batch + 1).press_dd(1)

            # Drop the stack
            macros[-1].press_a()

            # Close the boxes
            macros[-1].close_boxes()
            

            # Begin hatching
            macros[-1].hatch_eggs(base_time).sleep(5)

            # Open boxes to put now hatched eggs away
            macros[-1].open_boxes()

            # Move to where the now hatched eggs are
            macros[-1].press_dl(1).sleep(.5).press_dd(1).sleep(.5)

            macros[-1].grab_egg_stack()

            # Move the hatched eggs to where they started
            macros[-1].press_dr(batch + 1).sleep(.5)
            macros[-1].press_du(1).sleep(.5)

            # Drop stack
            macros[-1].press_a().sleep(.5)

            # Move to the next column we need to hatch
            macros[-1].press_dr(1).sleep(.5)

        macros[-1].close_boxes()
        return macros