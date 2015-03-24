__author__ = 'Sam Davies'


class StateMachine(object):

    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []
        self.actions = {}
        self.state_trace = []

    def add_state(self, name, handler, end_state=False):
        name = name.upper()
        self.handlers[name] = handler
        if end_state:
            print name
            assert self.actions[name] is not None
            self.endStates.append(name)

    def add_final_state_and_action(self, name, action):
        name = name.upper()
        self.actions[name] = action
        self.add_state(name, None, end_state=True)

    def do_action(self, name):
        name = name.upper()
        return self.actions[name]()

    def set_start(self, name):
        self.startState = name.upper()

    def run(self):
        self.state_trace = []
        try:
            handler = self.handlers[self.startState]
        except:
            raise ValueError("must call .set_start() before .run()")
        if not self.endStates:
            raise ValueError("at least one state must be an end_state")

        while True:
            new_state = handler()
            self.state_trace.append(new_state.upper())
            if new_state.upper() in self.endStates:
                return new_state
                break
            else:
                handler = self.handlers[new_state.upper()]
