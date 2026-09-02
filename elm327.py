import obd
from obd import OBDStatus # Adicionado: Importação explícita de OBDStatus


class LeitorTelemetriaOBD:
    def __init__(self):
        self.conexao = None

    def conectar_veiculo(self):
        """Tenta estabelecer conexão com o scanner ELM327 no carro."""
        print("[OBD2] Procurando interface ELM327...")
        # Em modo automatico, ele varre as portas seriais/bluetooth
        self.conexao = obd.OBD() 
        
        if self.conexao.status() == OBDStatus.CAR_CONNECTED:
            print("[OBD2] Conectado com sucesso ao veículo!")
            return True
        else:
            print(f"[OBD2] Falha na conexão. Status atual: {self.conexao.status()}")
            return False

    def ler_codigos_falha_dtc(self):
        """Lê a memória de avarias da ECU procurando códigos de erro ativos."""
        if not self.conexao or self.conexao.status() != OBDStatus.CAR_CONNECTED:
            return ["P0121"] # Retorno Simulado (Demo) caso não esteja no carro real
            
        print("[OBD2] Lendo códigos de falha (DTCs)...")
        # Comando do Modo 03 (Códigos de problemas de diagnóstico confirmados)
        resposta = self.conexao.query(obd.commands.GET_DTC)
        
        codigos_encontrados = []
        if resposta.value:
            for codigo, descricao in resposta.value:
                codigos_encontrados.append(codigo)
        
        return codigos_encontrados

    def ler_dados_vivos_criticos(self):
        """Captura a telemetria atual dos principais sensores para análise."""
        dados_vivos = {}
        
        if not self.conexao or self.conexao.status() != OBDStatus.CAR_CONNECTED:
            # Dados Simulados (Demo) para teste de bancada
            return {
                "RPM": "850 rpm",
                "Temperatura_Arrefecimento": "105 C", # Alto!
                "Posicao_Borboleta_TBI": "12%"         # Fora do padrão de marcha lenta
            }

        # Comandos de leitura em tempo real (Modo 01)
        comandos = {
            "RPM": obd.commands.RPM,
            "Temperatura_Arrefecimento": obd.commands.COOLANT_TEMP,
            "Temperatura_Oleo": obd.commands.OIL_TEMP,
            "Posicao_Borboleta_TBI": obd.commands.THROTTLE_POS,
            "Tensao_Bateria": obd.commands.ELM_VOLTAGE,
            "Carga_Motor": obd.commands.ENGINE_LOAD,
            "Pressao_Combustivel": obd.commands.FUEL_PRESSURE,
            "Marcha_Atual": obd.commands.GEAR, # Adicionado
            "Torque_Motor": obd.commands.TORQUE, # Adicionado
            "Pressao_Turbo": obd.commands.BOOST_PRESSURE, # Adicionado
            "Status_DPF": obd.commands.DPF_STATUS, # Adicionado
            "Temperatura_DPF": obd.commands.DPF_TEMP, # Adicionado
        }

        for nome, comando in comandos.items():
            resp = self.conexao.query(comando)
            if not resp.is_null():
                dados_vivos[nome] = str(resp.value)

        return dados_vivos