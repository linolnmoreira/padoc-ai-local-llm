from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///oficinas.db")
Base = declarative_base()

class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True)
    carro = Column(String)
    defeito = Column(String)
    solucao = Column(String)
    peca = Column(String)
    valor = Column(Float)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def salvar_servico(carro, defeito, solucao, peca, valor):
    db = Session()
    try:
        registro = Servico(
            carro=carro,
            defeito=defeito,
            solucao=solucao,
            peca=peca,
            valor=valor
        )
        db.add(registro)
        db.commit()
        return True
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def buscar_historico_oficina(carro=None):
    db = Session()
    query = db.query(Servico)
    if carro:
        query = query.filter(Servico.carro.like(f"%{carro}%"))
    resultados = query.all()
    db.close()
    return resultados