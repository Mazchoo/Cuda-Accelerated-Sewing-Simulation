"""Common setup for a controller class"""

from functools import update_wrapper

from src.qt.common.controller_abc import ControllerABC


def CreateQtController(cls):
    """
    A class decorator that makes an object into a controler.
    The controller expects to be called with a parent window,
    a model for underlying data which is not visible or editable
    to the user and a layout class containing the visual components
    of the GUI.

    If initializeUI is present, it will be checked and called.
    If initalizeModels is present, it will be checked and called.
    """

    class QtController(cls):
        """Inner class for controller"""

        def __init__(self, parent_window, Model, layout, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if not issubclass(self.controller_class, ControllerABC):
                raise NotImplementedError(
                    f"Class {self.controller_class.__name__} does not implement ControllerABC."
                )

            self.layout = layout
            self.model = Model()
            self.parent = parent_window

            self.setup()
            update_wrapper(self, self.controller_class)  # Updates doc strings

        def setup(self):
            """Create UI class, assigned callbacks to slots and intialize model"""
            self.initializeUi(self)
            self.setupCallbacks(self)
            self.initializeModels(self)

        @property
        def controller_class(self):
            """Get controller parent class"""
            return cls

    return QtController
