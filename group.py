class Group:
    def __init__(self, password):
        self.password = password
        self.participantes = []
        
    def addParticipante(self, participante):
        self.participantes.append(participante)
        
    def removeParticipante(self, participante):
        self.participantes.remove(participante)