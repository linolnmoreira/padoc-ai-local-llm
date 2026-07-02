import obd


class PadocOBD:


    def __init__(self):
        self.carro = None

    def conectar(self):
        print("Tentando conectar ao adaptador ELM327...")
        # obd.OBD() tenta conectar automaticamente
        self.carro = obd.OBD()
        if self.carro.is_connected():
            print("Conectado ao ELM327.")
            return True
        else:
            print("Falha na conexão com o ELM327. Verifique o adaptador e as permissões.")
            return False


    def dados_motor(self):
        if not self.carro or not self.carro.is_connected():
            return {"erro": "OBD não conectado"}

        rpm = self.carro.query(obd.commands.RPM)
        temp = self.carro.query(obd.commands.COOLANT_TEMP)

        return {
        "rpm": str(rpm.value) if rpm.value is not None else "N/A",
        "temperatura": str(temp.value) if temp.value is not None else "N/A"
        }