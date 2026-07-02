from datetime import datetime

class SchedulerAI:

    def criar_agendamento(
        self,
        cliente,
        oficina,
        data
    ):
        return {
            "cliente":
            cliente,
            "oficina":
            oficina,
            "data":
            data,
            "status":
            "reservado"
        }