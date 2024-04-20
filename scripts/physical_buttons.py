import importlib.util




class PhysicalButtons():
    def __init__(self, play=2,increment=3,decrement=4):
        gpiozero = importlib.util.find_spec("gpiozero")

        if gpiozero is not None:

            from gpiozero import Button

            self.play = Button(play);
            self.increment = Button(increment);
            self.decrement = Button(decrement);

        else:
            self.play = EmptyButton();
            self.increment = EmptyButton();
            self.decrement = EmptyButton();

class EmptyButton():
    def __init__(self):
        self.is_pressed = False;
