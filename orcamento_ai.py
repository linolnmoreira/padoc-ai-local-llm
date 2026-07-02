"""
PADOC AI
Gerador de orçamento
"""


def gerar_orcamento(
    servico,
    pecas,
    valor_mao_obra
):


    total_pecas=0


    lista=[]



    for p in pecas:


        lista.append({

        "item":p,

        "valor_estimado":150

        })


        total_pecas +=150



    total = (
        total_pecas +
        valor_mao_obra
    )



    return {


    "servico":servico,


    "pecas":lista,


    "mao_obra":
    valor_mao_obra,


    "total":
    total

    }