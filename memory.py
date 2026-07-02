import sqlite3
import os

class VehicleMemory:

    def __init__(self):
        os.makedirs("database", exist_ok=True)
        self.db = sqlite3.connect(
            "database/padoc.db"
        )
        self.criar()

    def criar(self):
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS carros(
        placa TEXT,
        modelo TEXT,
        km INTEGER,
        historico TEXT
        )
        """)
        self.db.commit()

    def salvar(
        self,
        placa,
        modelo,
        km,
        historico
    ):
        self.db.execute(
            """
            INSERT INTO carros VALUES(?,?,?,?)
            """,
            (
                placa,
                modelo,
                km,
                historico
            )
        )
        self.db.commit()