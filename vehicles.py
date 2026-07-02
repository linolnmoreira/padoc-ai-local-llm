from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine(
"sqlite:///padoc.db"
)


Base = declarative_base()


class Vehicle(Base):

    __tablename__ = "vehicles"


    id = Column(
    Integer,
    primary_key=True
    )


    placa = Column(String)

    modelo = Column(String)

    km = Column(Integer)

    dados = Column(Text)



Base.metadata.create_all(engine)


Session = sessionmaker(
bind=engine
)



def salvar(
placa,
modelo,
km,
dados
):
    db = Session()
    carro = Vehicle(
    placa=placa,
    modelo=modelo,
    km=km,
    dados=dados
    )
    db.add(carro)
    db.commit()
    db.close() # Fechar a sessão após o uso



def memoria(placa):
    db = Session()
    carro = db.query(
    Vehicle
    ).filter_by(
    placa=placa
    ).first()
    db.close() # Fechar a sessão após o uso
    return carro