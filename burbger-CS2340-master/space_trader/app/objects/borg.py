class Borg: # pylint: disable=too-few-public-methods
    """
    A class that makes an effective singleton.

    Any instance of Borg (or its subclasses) will have a shared state with all
    other instances of that same class. As an example, a Borg's name is the same
    as any other Borg's name, but may differ from a class called BorgTwo with
    its own name and state, though no BorgTwo will be different from any other.
    As a bonus, this makes Borgs really easy to access - just make a new one to
    get a reference to the shared state!

    Not exactly a singleton, though, since each instance really is an instance
    with its own
    """
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state
