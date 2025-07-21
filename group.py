class Group:
    def __init__(self, name, password=None):
        self.name = name
        self.password = password
        self.participants = []

    def add_participant(self, participant):
        self.participants.append(participant)

    def remove_participant(self, participant):
        if participant in self.participants:
            self.participants.remove(participant)

    def check_access(self, password):
        return self.password is None or self.password == password
