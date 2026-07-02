from brain.padoc_brain import PadocBrain


class Diagnostico:


    def __init__(self):

        self.brain=PadocBrain()



    def executar(self,codigo):

        resultado=self.brain.analisar(codigo)

        return resultado