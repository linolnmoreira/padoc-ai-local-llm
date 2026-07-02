class PadocAssistant:


    def responder(self,msg):


        msg=msg.lower()


        if "óleo" in msg:

            return (
            "Recomendo verificar nível,"
            " viscosidade e histórico."
            )


        if "motor" in msg:

            return (
            "Vou analisar sintomas "
            "e códigos OBD2."
            )


        return (

        "Sou a PADOC AI."
        " Informe o problema do veículo."

        )