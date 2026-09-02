from datetime import datetime


class TelemetryAI:

    def analisar(self, dados):

        alertas = []
        recomendacoes = []
        score_geral = 100
        critico = False

        rpm = dados.get("rpm")
        velocidade = dados.get("velocidade")
        temperatura = dados.get("temperatura")
        maf = dados.get("maf")
        map_sensor = dados.get("map")
        tps = dados.get("tps")
        bateria = dados.get("bateria")
        combustivel = dados.get("combustivel")
        stft = dados.get("stft")
        ltft = dados.get("ltft")
        iat = dados.get("iat")
        ect = dados.get("ect")
        lambda1 = dados.get("lambda1")
        pressao_oleo = dados.get("pressao_oleo")
        pressao_combustivel = dados.get("pressao_combustivel")
        torque = dados.get("torque") # Adicionado
        marcha = dados.get("marcha") # Adicionado
        pressao_turbo = dados.get("pressao_turbo") # Adicionado
        temperatura_dpf = dados.get("temperatura_dpf") # Adicionado
        status_dpf = dados.get("status_dpf") # Adicionado

        # NEW SENSOR PARAMETERS (now expected within the 'dados' dictionary)
        tensao_bateria_principal = dados.get("tensao_bateria_principal") # Main battery voltage
        corrente_bateria_principal = dados.get("corrente_bateria_principal") # Main battery current
        tensao_bateria_auxiliar = dados.get("tensao_bateria_auxiliar") # Auxiliary battery voltage (e.g., for hybrids)
        corrente_bateria_auxiliar = dados.get("corrente_bateria_auxiliar") # Auxiliary battery current
        temperatura_cabine = dados.get("temperatura_cabine")
        umidade_cabine = dados.get("umidade_cabine")
        ocupacao_cabine = dados.get("ocupacao_cabine") # Number of occupants
        distancia_ultrassom_frente = dados.get("distancia_ultrassom_frente") # Front ultrasonic sensor
        distancia_ultrassom_tras = dados.get("distancia_ultrassom_tras") # Rear ultrasonic sensor
        aceleracao_x = dados.get("aceleracao_x") # Accelerometer X-axis
        aceleracao_y = dados.get("aceleracao_y") # Accelerometer Y-axis
        aceleracao_z = dados.get("aceleracao_z") # Accelerometer Z-axis
        posicao_gps_lat = dados.get("posicao_gps_lat")
        posicao_gps_lon = dados.get("posicao_gps_lon")
        radar_objetos_frente = dados.get("radar_objetos_frente") # List of detected objects from radar
        camera_deteccao_faixa = dados.get("camera_deteccao_faixa") # Lane detection status
        camera_deteccao_sinal = dados.get("camera_deteccao_sinal") # Traffic sign detection
        camera_deteccao_obstaculo = dados.get("camera_deteccao_obstaculo") # Obstacle detection from camera
        radar_distancia_min = dados.get("radar_distancia_min") # Minimum distance from radar
        radar_velocidade_relativa = dados.get("radar_velocidade_relativa") # Relative speed from radar

        # RPM
        if rpm is not None:
            if rpm < 600:
                alertas.append("Marcha lenta muito baixa.")
                recomendacoes.append("Verificar corpo de borboleta e entrada de ar.")
                score_geral -= 5
            elif rpm > 6500:
                alertas.append("Motor em alta rotação.")
                recomendacoes.append("Reduzir rotação imediatamente.")
                score_geral -= 20
                critico = True

        # Temperatura (General engine temperature, if ECT is not available)
        if temperatura is not None and ect is None:
            if temperatura > 105:
                alertas.append("Motor superaquecido.")
                recomendacoes.append("Verificar sistema de arrefecimento.")
                score_geral -= 25
                critico = True
            elif temperatura < 60:
                alertas.append("Motor ainda frio.")
                recomendacoes.append("Aguardar temperatura ideal.")
                score_geral -= 2

        # Temperatura ECT
        if ect is not None:
            if ect > 105:
                alertas.append("ECT acima do normal.")
                recomendacoes.append("Verificar sensor ECT e arrefecimento.")
                score_geral -= 20
            elif ect < 60 and rpm is not None and rpm > 1000: # Engine running but cold
                alertas.append("Motor não atingindo temperatura ideal de operação.")
                recomendacoes.append("Verificar termostato.")
                score_geral -= 5

        # MAF
        if maf is not None:
            if maf < 2 and rpm is not None and rpm > 800: # Low MAF at idle
                alertas.append("Fluxo de ar muito baixo.")
                recomendacoes.append("Limpar ou substituir sensor MAF.")
                score_geral -= 8
            elif maf > 150:
                alertas.append("Fluxo de ar elevado.")
                score_geral -= 5

        # MAP
        if map_sensor is not None:
            if map_sensor > 110:
                alertas.append("Pressão MAP elevada.")
                recomendacoes.append("Verificar turbo ou sensor MAP.")
                score_geral -= 8
            elif map_sensor < 30 and rpm is not None and rpm > 800: # Very low MAP at idle (high vacuum)
                alertas.append("Pressão MAP muito baixa em marcha lenta.")
                recomendacoes.append("Verificar vazamentos de vácuo, sensor MAP.")
                score_geral -= 5

        # TPS
        if tps is not None:
            if tps > 95:
                alertas.append("Acelerador totalmente aberto.")
            elif tps < 0:
                alertas.append("Leitura inválida do TPS.")
                score_geral -= 5

        # Bateria
        if bateria is not None and tensao_bateria_principal is None:
            if bateria < 12.0:
                alertas.append("Bateria descarregada.")
                recomendacoes.append("Testar bateria e alternador.")
                score_geral -= 10
            elif bateria > 15:
                alertas.append("Sobretensão do alternador.")
                recomendacoes.append("Verificar regulador de tensão.")
                score_geral -= 20

        # NEW: Main Battery Voltage/Current
        if tensao_bateria_principal is not None:
            if tensao_bateria_principal < 12.0:
                alertas.append("Tensão da bateria principal baixa.")
                recomendacoes.append("Verificar bateria, alternador e conexões.")
                score_geral -= 10
            elif tensao_bateria_principal > 15.0:
                alertas.append("Tensão da bateria principal alta (sobrecarga).")
                recomendacoes.append("Verificar regulador de tensão do alternador.")
                score_geral -= 15
        if corrente_bateria_principal is not None:
            if corrente_bateria_principal < -50: # High discharge
                alertas.append("Alta descarga da bateria principal.")
                recomendacoes.append("Verificar consumo elétrico excessivo ou falha no sistema de carga.")
                score_geral -= 10
            elif corrente_bateria_principal > 50: # High charge
                alertas.append("Alta corrente de carga da bateria principal.")
                recomendacoes.append("Pode indicar bateria muito descarregada ou problema no alternador.")
                score_geral -= 5

        # NEW: Auxiliary Battery Voltage/Current (for hybrids/EVs)
        if tensao_bateria_auxiliar is not None:
            if tensao_bateria_auxiliar < 12.0:
                alertas.append("Tensão da bateria auxiliar baixa.")
                recomendacoes.append("Verificar bateria auxiliar e sistema de carga.")
                score_geral -= 8
        if corrente_bateria_auxiliar is not None:
            if abs(corrente_bateria_auxiliar) > 30:
                alertas.append("Corrente da bateria auxiliar elevada.")
                recomendacoes.append("Verificar consumo ou carga do sistema auxiliar.")
                score_geral -= 5

        # Combustível
        if combustivel is not None:
            if combustivel < 10:
                alertas.append("Combustível baixo.")

        # STFT
        if stft is not None:
            if abs(stft) > 15:
                alertas.append("STFT fora da faixa ideal.")
                recomendacoes.append("Verificar mistura ar/combustível.")
                score_geral -= 8

        # LTFT
        if ltft is not None:
            if abs(ltft) > 15:
                alertas.append("LTFT fora da faixa ideal.")
                recomendacoes.append("Inspecionar sistema de alimentação.")
                score_geral -= 8

        # Temperatura do ar
        if iat is not None:
            if ect is not None and iat > (ect + 20): # IAT significantly higher than ECT
                alertas.append("Temperatura do ar de admissão elevada em relação ao motor.")
                recomendacoes.append("Verificar intercooler, filtro de ar.")
                score_geral -= 5
            elif iat > 70:
                alertas.append("Temperatura do ar de admissão elevada.")
                score_geral -= 5

        # Lambda
        if lambda1 is not None:
            if lambda1 < 0.8:
                alertas.append("Mistura pobre.")
                recomendacoes.append("Verificar combustível, MAF e entrada falsa de ar.")
                score_geral -= 10
            elif lambda1 > 1.2:
                alertas.append("Mistura rica.")
                recomendacoes.append("Verificar bicos injetores e pressão de combustível.")
                score_geral -= 10

        # Pressão do óleo
        if pressao_oleo is not None:
            if pressao_oleo < 10:
                alertas.append("Baixa pressão do óleo.")
                recomendacoes.append("Parar o motor imediatamente.")
                score_geral -= 30
                critico = True
            elif pressao_oleo > 800: # Assuming kPa, this is very high
                alertas.append("Pressão do óleo excessivamente alta.")
                recomendacoes.append("Verificar válvula reguladora de pressão do óleo.")
                score_geral -= 10

        # Pressão combustível
        if pressao_combustivel is not None:
            if pressao_combustivel < 250:
                alertas.append("Pressão de combustível baixa.")
                recomendacoes.append("Verificar bomba, filtro e regulador.")
                score_geral -= 15
            elif pressao_combustivel > 500: # Assuming kPa, this is high
                alertas.append("Pressão de combustível alta.")
                recomendacoes.append("Verificar regulador de pressão de combustível.")
                score_geral -= 10

        # Velocidade
        if velocidade is not None:
            if velocidade > 180:
                alertas.append("Velocidade muito elevada.")

        # Torque
        if torque is not None:
            if torque > 400: # Valor alto, ex: 400 Nm
                alertas.append("Torque do motor em nível máximo.")

        # Marcha
        if marcha is not None:
            if velocidade is not None and velocidade > 80 and marcha is not None and marcha < 4:
                alertas.append("Relação marcha/velocidade ineficiente (marcha baixa para alta velocidade).")
                recomendacoes.append("Utilizar marchas mais altas para economizar combustível.")
                score_geral -= 3

        # Consumo de Combustível (Cálculo)
        # Fórmula: Consumo (L/100km) = (MAF / (Velocidade * Densidade_Combustível * Fator_Estequiométrico)) * 100
        # Simplificação para L/h: (MAF em g/s * 3600) / (Densidade_Gasolina_g_L * 1000)
        # Densidade da gasolina ~750 g/L
        consumo_l_100km = None
        if maf is not None and velocidade is not None and velocidade > 0:
            try:
                consumo_l_100km = (maf / (velocidade / 3.6)) / 750 * 100000
                dados["consumo_l_100km"] = round(consumo_l_100km, 2)
            except (ZeroDivisionError, TypeError):
                pass # Evita divisão por zero se a velocidade for 0

        # Pressão do Turbo
        if pressao_turbo is not None:
            # A pressão é em kPa acima da atmosférica. 100 kPa ~ 1 bar
            if pressao_turbo > 150: # Acima de 1.5 bar (gauge)
                alertas.append("Pressão do turbo excessivamente alta (overboost).")
                recomendacoes.append("Verificar válvula wastegate e solenoide de controle do turbo.")
                score_geral -= 15
                critico = True
            elif pressao_turbo < 20 and rpm is not None and rpm > 2000: # Very low boost under load
                alertas.append("Pressão do turbo muito baixa sob carga.")
                recomendacoes.append("Verificar vazamentos no sistema de admissão, turbo, válvula wastegate.")
                score_geral -= 10

        # DPF (Filtro de Partículas Diesel)
        if temperatura_dpf is not None:
            if temperatura_dpf > 650: # Regeneração ativa
                alertas.append("Regeneração do DPF em andamento.")
                recomendacoes.append("Manter o veículo em funcionamento em estrada até o fim do ciclo.")
            elif temperatura_dpf > 800:
                alertas.append("Temperatura do DPF crítica.")
                score_geral -= 20
        if status_dpf == "entupido":
            alertas.append("DPF entupido.")
            recomendacoes.append("Realizar regeneração forçada ou limpeza do DPF.")
            score_geral -= 25
            critico = True

        # NEW: Cabin Sensors
        if temperatura_cabine is not None:
            if temperatura_cabine > 30:
                alertas.append("Temperatura da cabine elevada.")
                recomendacoes.append("Verificar sistema de climatização.")
                score_geral -= 2
            elif temperatura_cabine < 10:
                alertas.append("Temperatura da cabine muito baixa.")
                recomendacoes.append("Verificar sistema de aquecimento.")
                score_geral -= 2
        if umidade_cabine is not None and umidade_cabine > 80:
            alertas.append("Alta umidade na cabine.")
            recomendacoes.append("Verificar vedação, filtro de cabine, sistema de A/C.")
            score_geral -= 1
        if ocupacao_cabine is not None and ocupacao_cabine > 5: # Assuming a 5-seater car
            alertas.append("Excesso de ocupantes na cabine.")
            recomendacoes.append("Verificar capacidade do veículo.")
            score_geral -= 1

        # NEW: Ultrasonic Sensors
        if distancia_ultrassom_frente is not None and distancia_ultrassom_frente < 0.2:
            alertas.append("Objeto muito próximo à frente do veículo (ultrassom).")
            recomendacoes.append("Alerta de colisão iminente.")
            score_geral -= 5
        if distancia_ultrassom_tras is not None and distancia_ultrassom_tras < 0.2:
            alertas.append("Objeto muito próximo à traseira do veículo (ultrassom).")
            recomendacoes.append("Alerta de colisão iminente ao dar ré.")
            score_geral -= 5

        # NEW: Accelerometer
        if aceleracao_x is not None and abs(aceleracao_x) > 1.5: # High lateral acceleration (e.g., hard cornering)
            alertas.append("Alta aceleração lateral detectada (manobra brusca).")
            recomendacoes.append("Pode indicar condução agressiva ou perda de controle.")
            score_geral -= 5
        if aceleracao_y is not None and abs(aceleracao_y) > 1.5: # High longitudinal acceleration (e.g., hard braking/acceleration)
            alertas.append("Alta aceleração longitudinal detectada (frenagem/aceleração brusca).")
            recomendacoes.append("Pode indicar condução agressiva ou evento de emergência.")
            score_geral -= 5
        if aceleracao_z is not None and abs(aceleracao_z) > 2.0: # High vertical acceleration (e.g., hitting a pothole)
            alertas.append("Alta aceleração vertical detectada (impacto).")
            recomendacoes.append("Pode indicar impacto com buraco ou obstáculo. Inspecionar suspensão/pneus.")
            score_geral -= 8

        # NEW: GPS Position (basic check for invalid data)
        if posicao_gps_lat is not None and (posicao_gps_lat < -90 or posicao_gps_lat > 90):
            alertas.append("Leitura de latitude GPS inválida.")
            score_geral -= 1
        if posicao_gps_lon is not None and (posicao_gps_lon < -180 or posicao_gps_lon > 180):
            alertas.append("Leitura de longitude GPS inválida.")
            score_geral -= 1

        # NEW: Radar
        if radar_objetos_frente:
            alertas.append(f"Radar detectou objetos à frente: {radar_objetos_frente}.")
            if radar_distancia_min is not None and radar_distancia_min < 5 and radar_velocidade_relativa is not None and radar_velocidade_relativa > 0:
                alertas.append(f"Alerta de colisão frontal: objeto a {radar_distancia_min}m com velocidade relativa de {radar_velocidade_relativa} km/h.")
                recomendacoes.append("Acionar sistema de frenagem de emergência ou desviar.")
                score_geral -= 15
                critico = True
            score_geral -= 3

        # NEW: Camera
        if camera_deteccao_faixa == "saida_faixa":
            alertas.append("Saída de faixa detectada sem sinalização.")
            recomendacoes.append("Manter atenção à condução. Verificar sistema de assistência de faixa.")
            score_geral -= 2
        if camera_deteccao_sinal == "limite_velocidade_excedido":
            alertas.append("Limite de velocidade excedido conforme sinalização da câmera.")
            recomendacoes.append("Reduzir velocidade.")
            score_geral -= 1
        if camera_deteccao_obstaculo:
            alertas.append(f"Câmera detectou obstáculo: {camera_deteccao_obstaculo}.")
            recomendacoes.append("Verificar ambiente e tomar ação evasiva.")
            score_geral -= 5


        # Score
        score_geral = max(0, score_geral)

        if score_geral >= 90: estado_geral = "Excelente"
        elif score_geral >= 75: estado_geral = "Bom"
        elif score_geral >= 60: estado_geral = "Regular"
        elif score_geral >= 40: estado_geral = "Ruim"
        else: estado_geral = "Crítico"

        diagnostico = " ; ".join(alertas) if alertas else "Nenhuma anomalia detectada."

        return{
            "tipo":"Telemetria",
            "data": datetime.now().isoformat(),
            "sensores": dados, # Return all raw data for context
            "diagnostico": diagnostico,
            "alertas": alertas,
            "recomendacoes": recomendacoes,
            "score_geral": score_geral, # Renamed from score_motor
            "estado_geral": estado_geral, # Renamed from estado_motor
            "falha_critica": critico
        }

        # Score
        score = max(0, score)

        if score >= 90: estado = "Excelente"
        elif score >= 75: estado = "Bom"
        elif score >= 60: estado = "Regular"
        elif score >= 40: estado = "Ruim"
        else: estado = "Crítico"

        diagnostico = " ; ".join(alertas) if alertas else "Nenhuma anomalia detectada."

        return{
            "tipo":"Telemetria",
            "data": datetime.now().isoformat(),
            "sensores": dados,
            "diagnostico": diagnostico,
            "alertas": alertas,
            "recomendacoes": recomendacoes,
            "score_motor": score,
            "estado_motor": estado,
            "falha_critica": critico
        }