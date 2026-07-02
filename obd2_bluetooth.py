"""
PADOC AI
Scanner OBD2 Bluetooth.
Requer: pip install obd
"""

import obd


def conectar():
    """Tenta estabelecer uma conexão com um adaptador OBD2."""
    try:
        # obd.OBD() tenta conectar-se automaticamente ao primeiro porto serial disponível
        conexao = obd.OBD()
        if conexao.is_connected():
            print("✓ Conectado ao scanner OBD2.")
        else:
            print("✗ Falha na conexão. Verifique o adaptador Bluetooth.")
        return conexao
    except Exception as e:
        print(f"✗ Erro ao tentar conectar: {e}")
        return None


def ler_motor():
    """Lê RPM e temperatura do motor via OBD2."""
    conexao = conectar()
    if not conexao or not conexao.is_connected():
        return {"erro": "Não foi possível ler os dados do motor."}

    rpm_cmd = obd.commands.RPM
    temp_cmd = obd.commands.COOLANT_TEMP

    rpm = conexao.query(rpm_cmd)
    temperatura = conexao.query(temp_cmd)

    return {
        "rpm": str(rpm.value) if rpm.value is not None else "N/A",
        "temperatura": str(temperatura.value) if temperatura.value is not None else "N/A"
    }