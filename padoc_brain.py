import json


class PadocBrain:


    def __init__(self):

        with open(
            "brain/knowledge_base.json",
            "r",
            encoding="utf-8"
        ) as file:

            self.base = json.load(file)



    def analisar(self, codigo):

        if codigo in self.base:

            return self.base[codigo]


        return {
            "erro":
            "Código não encontrado"
        }