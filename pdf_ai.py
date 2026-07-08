import fitz

class PDFAI:

    def analisar(self,pdf):

        doc=fitz.open(pdf)

        texto=""

        for pagina in doc:

            texto+=pagina.get_text()

        doc.close()

        return{
            "tipo":"PDF",
            "caracteres":len(texto),
            "texto":texto[:500]

        }