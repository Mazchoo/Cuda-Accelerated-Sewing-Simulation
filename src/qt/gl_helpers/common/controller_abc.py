''' Abstract base class for controller set-up '''
from abc import ABCMeta, abstractmethod
from inspect import signature, getattr_static


class ControllerABC(metaclass=ABCMeta):
    '''
        A Controller object has to adhere to the functions defined in this class.
        These functions must all be static methods and have one input argument.
    '''

    @abstractmethod
    def setupCallbacks(self):
        ''' Link models and views to relevant callbacks '''
        raise NotImplementedError

    @abstractmethod
    def initializeModels(self):
        ''' Set-up model data '''
        raise NotImplementedError

    @abstractmethod
    def initializeUi(self):
        ''' Set-up UI properties '''
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, sub):
        if not hasattr(sub, 'setupCallbacks'):
            return False
        if not isinstance(getattr_static(sub, "setupCallbacks"), staticmethod):
            return False
        if len(signature(sub.setupCallbacks).parameters) != 1:
            return False
        if not hasattr(sub, 'initializeModels'):
            return False
        if not isinstance(getattr_static(sub, "initializeModels"), staticmethod):
            return False
        if len(signature(sub.initializeModels).parameters) != 1:
            return False
        if not hasattr(sub, 'initializeUi'):
            return False
        if not isinstance(getattr_static(sub, "initializeUi"), staticmethod):
            return False
        if len(signature(sub.initializeUi).parameters) != 1:
            return False
        return True
