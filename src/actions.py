class Action(object):
    def __init__(self, name, func, args, kwargs):
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.func(*self.args, **self.kwargs)


class MoveAction(Action):
    def __init__(self, direction):
        self.direction = direction

    def __str__(self):
        return "MoveAction: " + str(self.direction)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.direction == other.direction

    def __hash__(self):
        return hash(self.direction)

    def __copy__(self):
        return MoveAction(self.direction)

    def __deepcopy__(self, memo):
        return MoveAction(deepcopy(self.direction, memo))

    def apply(self, state):
        state.agent_location = self.direction.apply(state.agent_location)
