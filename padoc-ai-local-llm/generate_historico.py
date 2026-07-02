import json
from pathlib import Path

text = '''P0010 - Powertrain Control Module (PCM) failure, Variable valve timing actuator failure, Wiring issue
P0011 - Camshaft variable timing solenoid failure, Engine oil level is too low, The engine is not timed correctly, The engine oil does not meet the manufacturer's requirements, Variable valve timing actuator failure, Worn timing chain
P0012 - Camshaft variable timing solenoid failure, Engine oil level is too low, The engine is not timed correctly, The engine oil does not meet the manufacturer's requirements, Variable valve timing actuator failure, Worn timing chain
P0013 - Powertrain Control Module (PCM) failure, Variable valve timing actuator failure, Wiring issue
P0014 - Camshaft variable timing solenoid failure, Engine oil level is too low, The engine is not timed correctly, The engine oil does not meet the manufacturer's requirements, Variable valve timing actuator failure, Worn timing chain
P0101 - Large vacuum leaks, Split Intake Air Boot or PCV Hose, Defective intake manifold gaskets, Mass Airflow Sensor (MAF), Mass Air Flow Sensor circuit and or wiring problems, Defective Barometric Pressure Sensor, Dirty or contaminated Mass Air Flow Sensing wire or filament, PCM software needs to be updated
P0102 - The Mass Airflow Sensor (MAF) Sensor is unplugged or the wiring is damaged, Loose or corroded electrical terminals in the MAF Sensor circuit, Faulty MAF Sensor
P0113 - Defective Intake Air Temperature Sensor, Dirty air filter, Defective Mass Air Flow Sensor, Faulty or corroded Intake Air Temperature Sensor wiring or connections
P0128 - Defective Engine Thermostat, Defective Engine Coolant Temperature Sensor, Defective Intake Air Temperature Sensor, Defective Cooling System, Low Engine Coolant, Dirty Engine Coolant causing incorrect Coolant Temperature Sensor readings, Defective/always running Engine Cooling fan(s)
P0135 - Defective Oxygen Sensor/Air Fuel Ratio Sensor, defective Oxygen Sensor/Air Fuel Ratio Sensor Heater Circuit, Exhaust System Leak, Intake Air System leak, Low Fuel Pressure, Defective Engine Coolant Temperature Sensor, Defective sensor wiring and or circuit problem, PCM software needs to be updated, Defective PCM
P0171 - Control module software needs to be updated, Vacuum leaks (intake manifold gaskets, vacuum hoses, PCV hoses, etc.), Mass air flow sensor, Plugged fuel filter or weak fuel pump, Plugged or dirty fuel injectors
P0174 - PCM software needs to be updated, Vacuum leaks (Intake Manifold Gaskets, vacuum hoses, PCV hoses, etc.), Faulty Mass Airflow (MAF) Sensor, Plugged Fuel Filter or weak Fuel Pump, Plugged or dirty Fuel Injectors
P0200 - Defective Fuel Injector, Faulty or corroded Fuel Injector, wiring, and or connections, Plugged Fuel Injector, Dirt in the Fuel Injector
P0201 - Defective Fuel Injector, Faulty or corroded Fuel Injector, wiring, and or connections, Plugged Fuel Injector, Dirt in the Fuel Injector
P0202 - Malfunction of the Fuel Injector, Malfunction of the PCM Fuel Injector driver circuit, Defective wiring/connections in the Fuel Injector wiring harness, Defective Fuel Injector power circuit(s)
P0203 - Fuel injector failure, Powertrain Control Module (PCM) failure, Wiring issue
P0205 - Fuel injector failure, Powertrain Control Module (PCM) failure, Wiring issue
P0300 - Worn out spark plugs, ignition wires, coil(s), distributor cap and rotor (when applicable), Incorrect ignition timing, Vacuum leak(s), Low or weak fuel pressure, Improperly functioning EGR system, Defective Mass Air Flow Sensor, Defective Crankshaft and or Camshaft Sensor, Defective Throttle Position Sensor, Mechanical engine problems (i.e.—low compression, leaking head gasket(s), or valve problems)
P0301 - Worn out spark plugs, ignition wires, coil(s), distributor cap and rotor (when applicable), Incorrect ignition timing, Vacuum leak(s), Low or weak fuel pressure, Improperly functioning EGR system, Defective Mass Air Flow Sensor, Defective Crankshaft and or Camshaft Sensor, Defective Throttle Position Sensor, Mechanical engine problems (i.e.—low compression, leaking head gasket(s), or valve problems)
P0302 - Worn out spark plugs, ignition wires, coil(s), distributor cap and rotor (when applicable), Incorrect ignition timing, Vacuum leak(s), Low or weak fuel pressure, Improperly functioning EGR system, Defective Mass Air Flow Sensor, Defective Crankshaft and or Camshaft Sensor, Defective Throttle Position Sensor, Mechanical engine problems (i.e.—low compression, leaking head gasket(s), or valve problems)
P0303 - Worn out spark plugs, ignition wires, coil(s), distributor cap and rotor (when applicable), Incorrect ignition timing, Vacuum leak(s), Low or weak fuel pressure, Improperly functioning EGR system, Defective Mass Air Flow Sensor, Defective Crankshaft and or Camshaft Sensor, Defective Throttle Position Sensor, Mechanical engine problems (i.e.—low compression, leaking head gasket(s), or valve problems)
P0304 - Worn out spark plugs, ignition wires, coil(s), distributor cap and rotor (when applicable), Incorrect ignition timing, Vacuum leak(s), Low or weak fuel pressure, Improperly functioning EGR system, Defective Mass Air Flow Sensor, Defective Crankshaft and or Camshaft Sensor, Defective Throttle Position Sensor, Mechanical engine problems (i.e.—low compression, leaking head gasket(s), or valve problems)
P0401 - Restriction in the EGR passages usually caused by carbon buildup, The EGR Valve is defective, Lack of proper vacuum or electrical signal to the EGR valve, Malfunctioning EGR Vacuum supply solenoid, Lack of proper EGR system feedback to the computer from the: Manifold Absolute Pressure Sensor (MAP), Differential EGR Pressure Feedback Sensor (DPFE), EGR Valve Position Sensor (EVP), EGR Temperature Sensor
P0420 - Inefficient Catalytic Converter(s), Defective Front or Rear Oxygen Sensor(s), Misfiring engines
P0430 - Defective Catalytic Converter, Internal engine damage resulting in high oil consumption and or a leaking Head Gasket has damaged the Catalytic Converter
P0440 - Missing fuel cap, Defective or damaged fuel cap, Distorted or damaged Fuel Tank Filler Neck, Torn or punctured Evaporative system hose(s), Defective Fuel Tank Sending Unit gasket or seal, Split or damaged Carbon Canister, Defective Evaporative Vent Valve and or Evaporative Purge Valve, Defective or damaged fuel tank
P0441 - Missing fuel cap, Stuck open or closed purge valve, Defective or damaged fuel cap, Distorted damaged or cracked Fuel Tank Filler Neck, Torn or punctured Evaporative system hose(s), Defective Fuel Tank Sending Unit gasket or seal, Split or damaged Carbon Canister, Defective Evaporative Vent Valve, Defective or damaged fuel tank
P0442 - Defective or damaged fuel cap, Distorted or damaged Fuel Tank Filler Neck, Small tear or puncture in the Evaporative system hose(s) and or Carbon Canister, Defective Fuel Tank Pressure Sensor, Defective Leak Detection Pump, Slightly loose and or worn clamps or hardened O-rings anywhere in the EVAP system
P0455 - Missing fuel cap, Defective or damaged fuel cap, Distorted or damaged Fuel Tank Filler Neck, Torn or punctured Evaporative system hose(s), Defective Fuel Tank Sending Unit gasket or seal, Split or damaged Carbon Canister, Defective Evaporative Vent Valve and or Evaporative Purge Valve, Defective or damaged fuel tank, Defective Fuel Tank Pressure Sensor
P0500 - Defective Vehicle Speed Sensor, Defective Speedometer, Vehicle Speed Sensor wiring or connector, Communication (CAN) bus problems, Defective transmission or differential Vehicle Speed Sensor drive gear
P0501 - Defective Vehicle Speed Sensor, Defective Speedometer, Vehicle Speed Sensor wiring or connector, Communication (CAN) bus problems, Defective transmission or differential Vehicle Speed Sensor drive gear
P0505 - Defective Idle Air Control Motor, Intake Manifold Vacuum leaks, Carbon buildup in the Throttle Body air passages
P0506 - Defective or sticking Idle Air Control Motor, Intake Manifold Vacuum leaks, Carbon buildup in the Throttle Body air passages, Defective Power Steering Pressure Switch
P0507 - Defective or sticking Idle Air Control Motor, Intake Manifold Vacuum leaks, Carbon buildup in the Throttle Body air passages, Defective Coolant Temperature Sensor, Defective Charging System/Alternator, Defective Power Steering Pressure Switch
P0600 - Defective PCM (Power Train Control Module), Defective PCM data bus wiring/connections, Defective PCM data bus ground circuit(s), Defective PCM or other control module controlled output devices, Defective CAN bus communication
P0601 - Lack of proper voltage to the PCM, Defective PCM memory module, Defective PCM ground circuit(s), Defective PCM controlled output devices
P0602 - Powertrain Control Module (PCM) failure, Wiring issue
P0603 - Lack of proper voltage to the Keep Alive Memory connection on the PCM, Defective PCM Keep Alive Memory Module (KAM), Defective PCM ground circuit(s), Defective PCM controlled output devices
P0605 - Lack of proper voltage and or ground to the PCM, Defective PCM ROM memory module, Defective PCM ground circuit(s), Defective PCM controlled output devices
P0700 - Defective Shift Solenoids, Defective Engine Coolant Temperature Sensor, Defective Valve Body, Dirty transmission fluid that restricts the hydraulic passages
P0705 - Defective Transmission Range Sensor (PRNDL input), Defective Transmission Range Sensor (PRNDL input) wiring or connector, Defective Valve Body, Defective manual shift valve linkage, Dirty transmission fluid that restricts the hydraulic passages
P0706 - Defective Transmission Range Sensor (PRNDL input), Defective Transmission Range Sensor (PRNDL input) wiring or connector, Defective Valve Body, Defective manual shift valve linkage, Dirty transmission fluid that restricts the hydraulic passages
P0720 - Defective Output Speed Sensor, Defective Shift Solenoids, Defective Engine Coolant Temperature Sensor, Defective Valve Body, Dirty transmission fluid that restricts the hydraulic passages, Defective Output Speed Sensor wiring or connector
P0730 - Defective Shift Solenoids, Defective Engine Coolant Temperature Sensor, Defective Valve Body, Dirty transmission fluid that restricts the hydraulic passages
P0841 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission fluid pressure sensor failure, Wiring issue
P0842 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission fluid pressure sensor failure, Wiring issue
P0845 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission fluid pressure sensor failure, Wiring issue
P0846 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission fluid pressure sensor failure, Wiring issue
P0847 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission fluid pressure sensor failure, Wiring issue
P0901 - Clutch master cylinder failure, Clutch solenoid failure, Transmission Control Module (TCM) failure
P0935 - Hydraulic power unit assembly failure, Transmission Control Module (TCM) failure, Wiring issue
P0942 - Hydraulic power unit assembly failure, Transmission Control Module (TCM) failure, Wiring issue
P0944 - Clogged transmission filter, Transmission fluid level is low, Transmission oil pump failure, Wiring issue
P0961 - Transmission shift solenoid failure
P0A08 - Inverter/converter assembly failure, Powertrain Control Module (PCM) failure, Wiring issue
P0A0D - High voltage safety device failure, Inverter/converter assembly failure, Power management control module failure, Service disconnect plug is not properly connected, Wiring issue
P0A0F - Hybrid transaxle assembly failure, Internal engine failure, Power management control module failure
P0A7F - Poor connections at the HV battery, A problem with the HV battery, ECU issues
P0A80 - High voltage battery assembly failure
P0B22 - Battery contactor assembly failure, Battery Energy Control Module (BECM) failure
P0B24 - Battery Energy Control Module (BECM) failure, High voltage battery assembly failure, Wiring issue
P0B26 - Battery Energy Control Module (BECM) failure, High voltage battery assembly failure, Wiring issue
P0B28 - Battery Energy Control Module (BECM) failure, High voltage battery assembly failure, Wiring issue
P0B30 - Battery Energy Control Module (BECM) failure, High voltage battery assembly failure, Wiring issue
P0C00 - Drive motor generator power inverter control module failure
P0C09 - Drive motor generator assembly failure, Drive motor generator power inverter control module failure
P0C11 - Coolant system leak, Drive motor generator power inverter control module failure, Engine cooling fan failure, Water pump failure
P0C14 - Coolant system leak, Drive motor generator power inverter control module failure, Engine cooling fan failure, Water pump failure
P0C15 - Coolant system leak, Drive motor generator power inverter control module failure, Engine cooling fan failure, Water pump failure
P2000 - Diesel Particulate Filter (DPF) failure, Intake air leak, Mass Airflow (MAF) sensor is dirty/loss of calibration
PP2002 - Diesel Particulate Filter (DPF) failure, Intake air leak, Mass Airflow (MAF) sensor is dirty/loss of calibration
P2004 - A failed IMRC actuator, A problem with the intake manifold or linkage, Wiring issues
P2006 - Intake manifold runner control actuator failure, Powertrain Control Module (PCM) failure, Restricted vacuum lines
P2101 - Accelerator Pedal Position (APP) assembly failure, Powertrain Control Module (PCM) failure, Throttle control motor failure, Wiring issue
P2122 - Accelerator Pedal Position (APP) assembly failure, Powertrain Control Module (PCM) failure, Throttle control motor failure, Wiring issue
P2135 - Accelerator Pedal Position (APP) assembly failure, Powertrain Control Module (PCM) failure, Throttle Position Sensor (TPS) failure, Wiring issue
P2138 - Accelerator Pedal Position (APP) assembly failure, Powertrain Control Module (PCM) failure, Throttle Position Sensor (TPS) failure, Wiring issue
P2181 - Engine coolant heater failure, Engine coolant level is too low, Thermostat failure
P2210 - NOx sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2213 - NOx sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2237 - Exhaust leak, Oxygen sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2238 - Exhaust leak, Oxygen sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2251 - Exhaust leak, Oxygen sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2302 - Ignition coil failure, Powertrain Control Module (PCM) failure, Wiring issue
P2303 - Ignition coil failure, Powertrain Control Module (PCM) failure, Wiring issue
P2305 - Ignition coil failure, Powertrain Control Module (PCM) failure, Wiring issue
P2308 - Ignition coil failure, Powertrain Control Module (PCM) failure, Wiring issue
P2310 - Ignition coil failure, Powertrain Control Module (PCM) failure, Wiring issue
P2401 - Evap leak detection pump failure, Powertrain Control Module (PCM) failure, Wiring issue
P2402 - Evap leak detection pump failure, Powertrain Control Module (PCM) failure, Wiring issue
P2422 - EVAP vent valve failure, Powertrain Control Module (PCM) failure, Wiring issue
P2431 - Air control solenoid failure, Powertrain Control Module (PCM) failure, Secondary Air System pressure sensor failure, Wiring issue
P2432 - Air control solenoid failure, Powertrain Control Module (PCM) failure, Secondary Air System pressure sensor failure, Wiring issue
P2500 - Alternator failure, Battery failure, Powertrain Control Module (PCM) failure, Wiring issue
P2501 - Alternator failure, Battery failure, Powertrain Control Module (PCM) failure, Wiring issue
P2503 - Alternator failure, Battery failure, Wiring issue
P2509 - Powertrain Control Module (PCM) failure, Powertrain Control Module (PCM) power relay failure, Wiring issue
P250C - Oil level sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2601 - Coolant Heat Storage (CHS) water pump failure, Coolant Heat Storage (CHS) water pump relay, Powertrain Control Module (PCM) failure, Wiring issue
P2607 - Intake air heater, Powertrain Control Module (PCM) failure, Wiring issue
P2609 - Intake air heater, Powertrain Control Module (PCM) failure, Wiring issue
P2610 - An internal PCM problem, A problem with the PCM power or ground circuit
P2614 - Broken tone ring, Camshaft Position Sensor (CMP) failure, Powertrain Control Module (PCM) failure, Wiring issue
P2706 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission shift solenoid failure, Wiring issue
P2711 - Internal transmission failure, Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission solenoid failure, Wiring issue
P2714 - Transmission Control Module (TCM) failure, Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission shift solenoid failure, Wiring issue
P2716 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission shift solenoid failure, Wiring issue
P2723 - Transmission Control Module (TCM) failure, Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission shift solenoid failure, Wiring issue
P2803 - Powertrain Control Module (PCM) failure, Transmission Control Module (TCM) failure, Transmission range sensor failure, Wiring issue
P2806 - Powertrain Control Module (PCM) failure, Transmission Control Module (TCM) failure, Transmission range sensor failure, Transmission range sensor is out of adjustment, Wiring issue
P2809 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission pressure control solenoid failure, Wiring issue
P2810 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission pressure control solenoid failure, Wiring issue
P2815 - Transmission Control Module (TCM) failure, Transmission fluid level is low, Transmission pressure control solenoid failure, Wiring issue
P2A00 - Exhaust leak, Oxygen sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2A01 - Exhaust leak, Oxygen sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2A03 - Exhaust leak, Oxygen sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2A04 - Exhaust leak, Oxygen sensor failure, Powertrain Control Module (PCM) failure, Wiring issue
P2BA8 - Faulty NOx Sensors, NOx Sensors harness is open or shorted, NOx Sensors circuit poor electrical connection, Faulty Diesel Particulate Filter (DPF)
P3000 - Fuel level is too low, High voltage battery assembly failure, High voltage battery is not sufficiently charged
P3100 - High voltage powertrain control module failure
P3400 - Faulty Cylinder Deactivation System
P3401 - Engine oil level is too low, Powertrain Control Module (PCM) failure, Variable valve timing solenoid failure, Wiring issue
B0081 - Wiring issues, Control module problems, A problem with the airbag
C0040 - A faulty wheel speed sensor, A problem with the wheel speed sensor circuit, Reluctor issues, A problem with the ABS module
U0001 - A faulty wheel speed sensor, A problem with the wheel speed sensor circuit, Reluctor issues, A problem with the ABS module
U0073 - A faulty control module, A problem with the CAN bus
U0100 - A faulty PCM, A problem with the control module circuit, A problem with the CAN bus
U0107 - A dead battery, A faulty TAC module, A problem with TAC module circuit, A problem with the CAN bus
U0121 - A dead battery, A faulty ABS module, A problem with ABS module circuit, A problem with the CAN bus'''

translations = {
    'powertrain control module (pcm) failure': 'Falha no Módulo de Controle de Trem de Força (PCM)',
    'variable valve timing actuator failure': 'Falha do atuador de comando variável de válvulas',
    'wiring issue': 'Problema de fiação',
    'camshaft variable timing solenoid failure': 'Falha do solenóide de comando variável do eixo de comando',
    'engine oil level is too low': 'Nível de óleo do motor muito baixo',
    'the engine is not timed correctly': 'Motor não está com o tempo correto',
    'the engine oil does not meet the manufacturer\'s requirements': 'Óleo do motor não atende às especificações do fabricante',
    'worn timing chain': 'Corrente de comando desgastada',
    'large vacuum leaks': 'Grandes vazamentos de vácuo',
    'split intake air boot or pcv hose': 'Mangueira de admissão ou PCV rachada',
    'defective intake manifold gaskets': 'Juntas do coletor de admissão defeituosas',
    'mass airflow sensor (maf)': 'Sensor de fluxo de massa de ar (MAF)',
    'mass air flow sensor circuit and or wiring problems': 'Problemas no circuito ou fiação do sensor MAF',
    'defective barometric pressure sensor': 'Sensor de pressão barométrica defeituoso',
    'dirty or contaminated mass air flow sensing wire or filament': 'Fio ou filamento do sensor MAF sujo ou contaminado',
    'pcm software needs to be updated': 'Software do PCM precisa ser atualizado',
    'the mass airflow sensor (maf) sensor is unplugged or the wiring is damaged': 'Sensor MAF desconectado ou fiação danificada',
    'loose or corroded electrical terminals in the maf sensor circuit': 'Terminais elétricos soltos ou corroídos no circuito do sensor MAF',
    'faulty maf sensor': 'Sensor MAF defeituoso',
    'defective intake air temperature sensor': 'Sensor de temperatura do ar de admissão defeituoso',
    'dirty air filter': 'Filtro de ar sujo',
    'defective mass air flow sensor': 'Sensor de fluxo de ar defeituoso',
    'faulty or corroded intake air temperature sensor wiring or connections': 'Fiação ou conexões do sensor de temperatura do ar de admissão defeituosas ou corroídas',
    'defective engine thermostat': 'Termostato do motor defeituoso',
    'defective engine coolant temperature sensor': 'Sensor de temperatura do líquido de arrefecimento defeituoso',
    'defective cooling system': 'Sistema de arrefecimento defeituoso',
    'low engine coolant': 'Nível de líquido de arrefecimento baixo',
    'dirty engine coolant causing incorrect coolant temperature sensor readings': 'Líquido de arrefecimento sujo causando leituras incorretas do sensor de temperatura',
    'defective/always running engine cooling fan(s)': 'Ventoinha(s) de arrefecimento do motor defeituosa(s) ou sempre ligada(s)',
    'defective oxygen sensor/air fuel ratio sensor': 'Sensor de oxigênio / sensor de mistura ar/combustível defeituoso',
    'defective oxygen sensor/air fuel ratio sensor heater circuit': 'Circuito de aquecedor do sensor de oxigênio / sensor de mistura defeituoso',
    'exhaust system leak': 'Vazamento no sistema de escape',
    'intake air system leak': 'Vazamento no sistema de admissão de ar',
    'low fuel pressure': 'Baixa pressão de combustível',
    'defective sensor wiring and or circuit problem': 'Problema de fiação ou circuito do sensor defeituoso',
    'control module software needs to be updated': 'Software do módulo de controle precisa ser atualizado',
    'vacuum leaks (intake manifold gaskets, vacuum hoses, pcv hoses, etc.)': 'Vazamentos de vácuo (juntas do coletor, mangueiras de vácuo, PCV, etc.)',
    'mass air flow sensor': 'Sensor de fluxo de ar',
    'plugged fuel filter or weak fuel pump': 'Filtro de combustível entupido ou bomba fraca',
    'plugged or dirty fuel injectors': 'Injetores de combustível entupidos ou sujos',
    'defective fuel injector': 'Injetor de combustível defeituoso',
    'faulty or corroded fuel injector, wiring, and or connections': 'Injetor de combustível defeituoso ou fiação/conexões corroídas',
    'plugged fuel injector': 'Injetor de combustível entupido',
    'dirt in the fuel injector': 'Sujeira no injetor de combustível',
    'malfunction of the fuel injector': 'Mau funcionamento do injetor de combustível',
    'malfunction of the pcm fuel injector driver circuit': 'Mau funcionamento do circuito driver do injetor do PCM',
    'defective wiring/connections in the fuel injector wiring harness': 'Fiação/conexões defeituosas no chicote do injetor',
    'defective fuel injector power circuit(s)': 'Circuitos de alimentação do injetor defeituosos',
    'worn out spark plugs, ignition wires, coil(s), distributor cap and rotor (when applicable)': 'Velas, fios de ignição, bobinas, tampa e rotor do distribuidor desgastados (quando aplicável)',
    'incorrect ignition timing': 'Tempo de ignição incorreto',
    'vacuum leak(s)': 'Vazamento(s) de vácuo',
    'low or weak fuel pressure': 'Pressão de combustível baixa ou fraca',
    'improperly functioning egr system': 'Sistema EGR com funcionamento inadequado',
    'defective crankshaft and or camshaft sensor': 'Sensor de virabrequim e/ou comando defeituoso',
    'defective throttle position sensor': 'Sensor de posição da borboleta defeituoso',
    'mechanical engine problems (i.e.—low compression, leaking head gasket(s), or valve problems)': 'Problemas mecânicos no motor (por exemplo, baixa compressão, junta de cabeçote vazando ou problemas de válvulas)',
    'restriction in the egr passages usually caused by carbon buildup': 'Restrição nas passagens do EGR geralmente causada por acúmulo de carbono',
    'the egr valve is defective': 'Válvula EGR defeituosa',
    'lack of proper vacuum or electrical signal to the egr valve': 'Falta de vácuo ou sinal elétrico adequado para a válvula EGR',
    'malfunctioning egr vacuum supply solenoid': 'Solenóide de alimentação de vácuo do EGR com defeito',
    'lack of proper egr system feedback to the computer from the: manifold absolute pressure sensor (map), differential egr pressure feedback sensor (dpfe), egr valve position sensor (evp), egr temperature sensor': 'Falta de feedback adequado do sistema EGR para o computador a partir de: sensor MAP, DPFE, sensor de posição da válvula EGR, sensor de temperatura EGR',
    'inefficient catalytic converter(s)': 'Catalisador(es) ineficiente(s)',
    'defective front or rear oxygen sensor(s)': 'Sensor(es) de oxigênio dianteiro(s) ou traseiro(s) defeituoso(s)',
    'misfiring engines': 'Motor com falhas de ignição',
    'defective catalytic converter': 'Catalisador defeituoso',
    'internal engine damage resulting in high oil consumption and or a leaking head gasket has damaged the catalytic converter': 'Danos internos no motor resultando em alto consumo de óleo e/ou junta de cabeçote vazando que danificaram o catalisador',
    'missing fuel cap': 'Tampa de combustível ausente',
    'defective or damaged fuel cap': 'Tampa de combustível defeituosa ou danificada',
    'distorted or damaged fuel tank filler neck': 'Bocal do tanque de combustível distorcido ou danificado',
    'torn or punctured evaporative system hose(s)': 'Mangueira do sistema evap rasgada ou perfurada',
    'defective fuel tank sending unit gasket or seal': 'Vedação da unidade de medição de combustível defeituosa',
    'split or damaged carbon canister': 'Canister de carbono rachado ou danificado',
    'defective evaporative vent valve and or evaporative purge valve': 'Válvula de ventilação evap e/ou válvula de purga evap defeituosa',
    'defective or damaged fuel tank': 'Tanque de combustível defeituoso ou danificado',
    'stuck open or closed purge valve': 'Válvula de purga presa aberta ou fechada',
    'small tear or puncture in the evaporative system hose(s) and or carbon canister': 'Pequeno rasgo ou perfuração na mangueira do sistema EVAP e/ou canister',
    'defective fuel tank pressure sensor': 'Sensor de pressão do tanque de combustível defeituoso',
    'defective leak detection pump': 'Bomba de detecção de vazamento defeituosa',
    'slightly loose and or worn clamps or hardened o-rings anywhere in the evap system': 'Abraçadeiras ligeiramente soltas ou desgastadas ou anéis O endurecidos em qualquer ponto do sistema EVAP',
    'defective vehicle speed sensor': 'Sensor de velocidade do veículo defeituoso',
    'defective speedometer': 'Velocímetro defeituoso',
    'vehicle speed sensor wiring or connector': 'Fiação ou conector do sensor de velocidade do veículo',
    'communication (can) bus problems': 'Problemas de comunicação no barramento CAN',
    'defective transmission or differential vehicle speed sensor drive gear': 'Engrenagem de acionamento do sensor de velocidade do câmbio ou diferencial defeituosa',
    'defective idle air control motor': 'Motor de controle de marcha lenta defeituoso',
    'intake manifold vacuum leaks': 'Vazamentos de vácuo no coletor de admissão',
    'carbon buildup in the throttle body air passages': 'Acúmulo de carbono nas passagens de ar do corpo de borboleta',
    'defective power steering pressure switch': 'Interruptor de pressão da direção hidráulica defeituoso',
    'defective pcm (power train control module)': 'PCM (Módulo de Controle do Trem de Força) defeituoso',
    'defective pcm data bus wiring/connections': 'Fiação/conexões do barramento de dados do PCM defeituosas',
    'defective pcm data bus ground circuit(s)': 'Circuitos de aterramento do barramento de dados do PCM defeituosos',
    'defective pcm or other control module controlled output devices': 'Dispositivos de saída controlados pelo PCM ou outro módulo defeituosos',
    'defective can bus communication': 'Comunicação CAN defeituosa',
    'lack of proper voltage to the pcm': 'Falta de tensão adequada no PCM',
    'defective pcm memory module': 'Módulo de memória do PCM defeituoso',
    'defective pcm ground circuit(s)': 'Circuito(s) de aterramento do PCM defeituoso(s)',
    'defective pcm controlled output devices': 'Dispositivos de saída controlados pelo PCM defeituosos',
    'lack of proper voltage to the keep alive memory connection on the pcm': 'Falta de tensão adequada na conexão Keep Alive Memory do PCM',
    'defective pcm keep alive memory module (kam)': 'Módulo de memória Keep Alive (KAM) do PCM defeituoso',
    'lack of proper voltage and or ground to the pcm': 'Falta de tensão e/ou aterramento adequado no PCM',
    'defective pcm rom memory module': 'Módulo de memória ROM do PCM defeituoso',
    'defective shift solenoids': 'Solenóides de câmbio defeituosos',
    'defective valve body': 'Corpo de válvula defeituoso',
    'dirty transmission fluid that restricts the hydraulic passages': 'Fluido de transmissão sujo que restringe as passagens hidráulicas',
    'defective transmission range sensor (prndl input)': 'Sensor de faixa de transmissão (entrada PRNDL) defeituoso',
    'defective transmission range sensor (prndl input) wiring or connector': 'Fiação ou conector do sensor de faixa de transmissão defeituoso',
    'defective manual shift valve linkage': 'Ligação da válvula de mudança manual defeituosa',
    'defective output speed sensor': 'Sensor de velocidade de saída defeituoso',
    'defective output speed sensor wiring or connector': 'Fiação ou conector do sensor de velocidade de saída defeituoso',
    'transmission control module (tcm) failure': 'Falha do módulo de controle de transmissão (TCM)',
    'transmission fluid level is low': 'Nível de fluido de transmissão baixo',
    'transmission fluid pressure sensor failure': 'Falha do sensor de pressão do fluido de transmissão',
    'clutch master cylinder failure': 'Falha do cilindro mestre da embreagem',
    'clutch solenoid failure': 'Falha do solenóide da embreagem',
    'hydraulic power unit assembly failure': 'Falha do conjunto da unidade hidráulica',
    'clogged transmission filter': 'Filtro de transmissão entupido',
    'transmission oil pump failure': 'Falha da bomba de óleo da transmissão',
    'transmission shift solenoid failure': 'Falha do solenóide de mudança da transmissão',
    'inverter/converter assembly failure': 'Falha do conjunto inversor/conversor',
    'high voltage safety device failure': 'Falha do dispositivo de segurança de alta tensão',
    'power management control module failure': 'Falha do módulo de controle de gerenciamento de energia',
    'service disconnect plug is not properly connected': 'Plugue de desconexão de serviço não está conectado corretamente',
    'hybrid transaxle assembly failure': 'Falha do conjunto do transcassete híbrido',
    'internal engine failure': 'Falha interna do motor',
    'poor connections at the hv battery': 'Conexões ruins na bateria de alta tensão',
    'a problem with the hv battery': 'Problema na bateria de alta tensão',
    'ecu issues': 'Problemas na ECU',
    'high voltage battery assembly failure': 'Falha do conjunto da bateria de alta tensão',
    'battery contactor assembly failure': 'Falha do conjunto do contator da bateria',
    'battery energy control module (becm) failure': 'Falha do módulo de controle de energia da bateria (BECM)',
    'oil level sensor failure': 'Falha do sensor de nível de óleo',
    'coolant heat storage (chs) water pump failure': "Falha da bomba d'água do CHS",
    'coolant heat storage (chs) water pump relay': "Relé da bomba d'água do CHS",
    'an internal pcm problem': 'Problema interno no PCM',
    'a problem with the pcm power or ground circuit': 'Problema no circuito de alimentação ou aterramento do PCM',
    'broken tone ring': 'Anel de tom quebrado',
    'camshaft position sensor (cmp) failure': 'Falha do sensor de posição do eixo de comando (CMP)',
    'transmission range sensor failure': 'Falha do sensor de faixa de transmissão',
    'transmission range sensor is out of adjustment': 'Sensor de faixa de transmissão fora de ajuste',
    'faulty nox sensors': 'Sensor NOx defeituoso',
    'nox sensors harness is open or shorted': 'Chicote dos sensores NOx aberto ou em curto',
    'nox sensors circuit poor electrical connection': 'Conexão elétrica ruim no circuito dos sensores NOx',
    'faulty diesel particulate filter (dpf)': 'Filtro de partículas diesel (DPF) defeituoso',
    'fuel level is too low': 'Nível de combustível muito baixo',
    'high voltage battery is not sufficiently charged': 'Bateria de alta tensão não está suficientemente carregada',
    'high voltage powertrain control module failure': 'Falha do módulo de controle de trem de força de alta tensão',
    'faulty cylinder deactivation system': 'Sistema de desativação de cilindros com defeito',
    'faulty wheel speed sensor': 'Sensor de velocidade de roda com defeito',
    'a problem with the wheel speed sensor circuit': 'Problema no circuito do sensor de velocidade de roda',
    'reluctor issues': 'Problemas no reluctor',
    'a problem with the abs module': 'Problema no módulo ABS',
    'a faulty control module': 'Módulo de controle com defeito',
    'a problem with the can bus': 'Problema no barramento CAN',
    'a faulty pcm': 'PCM defeituoso',
    'a dead battery': 'Bateria descarregada',
    'a faulty tac module': 'Módulo TAC defeituoso',
    'a problem with tac module circuit': 'Problema no circuito do módulo TAC',
    'a faulty abs module': 'Módulo ABS defeituoso'
}

entries = []
for line in text.splitlines():
    if not line.strip():
        continue
    code, causes = line.split(' - ', 1)
    cause_list = [translations.get(c.strip().lower(), c.strip()) for c in causes.split(',') if c.strip()]
    entries.append({
        'codigo_obd2': code,
        'componente': 'Sistema OBD2 / Diagnóstico',
        'defeito': f'Falha identificada pelo código {code}.',
        'sintomas': ['Luz de injeção acesa', 'Verificar o código com scanner'],
        'causas_provaveis': cause_list,
        'solucao_manual': '1. Ler o código com scanner.\n2. Inspecionar as causas prováveis listadas.\n3. Realizar reparos ou substituições conforme diagnóstico.',
        'historico_reparacao': 'Histórico genérico de diagnóstico baseado no código OBD2.'
    })

output_path = Path(__file__).resolve().parent / 'knowledge' / 'historico_oficina.json'
output_path.write_text(json.dumps(entries, indent=4, ensure_ascii=False), encoding='utf-8')
print(f'Updated {output_path}')
