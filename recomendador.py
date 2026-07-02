class Recomendador:


    def recomendar(self,problema):


        banco={


        "freio":[

        "pastilha",
        "disco",
        "fluido"

        ],


        "motor":[

        "vela",
        "óleo",
        "filtro"

        ]


        }


        return banco.get(

        problema,

        [
        "Diagnóstico completo"
        ]

        )