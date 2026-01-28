from opcua import Server
from pymodbus.client import ModbusTcpClient
import time

# ======================
# OPC UA SERVER SETUP
# ======================

server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840")

uri = "http://modbus.opcua.server"
idx = server.register_namespace(uri)

objects = server.get_objects_node()
plc = objects.add_object(idx, "PLC1")

print("Value IDX "+str(idx))

temperature = plc.add_variable(idx, "Temperature", 0.0)
pressure = plc.add_variable(idx, "Pressure", 0.0)
motor = plc.add_variable(idx, "MotorStatus", False)

temperature.set_writable()
pressure.set_writable()
motor.set_writable()


# ======================
# MODBUS CLIENT SETUP
# ======================
client = ModbusTcpClient(
    host="192.168.0.143",
    port=502
)

is_modbus_connect = client.connect()
        
# ======================
# START SERVER
# ======================
server.start()
print("OPC UA Server running at opc.tcp://localhost:4840")

try:
    while True:
        if not is_modbus_connect:
            print("❌ Modbus connection failed")
            time.sleep(1)
            continue

        # Read holding registers
        rr = client.read_holding_registers(address=0, count=10, device_id=1)
        cc = client.read_coils(address=0, count=10, device_id=1)

        if not rr.isError():
            temp = rr.registers[0]     # scaling
            pres = rr.registers[1]
            motor_status = bool(cc.bits[0])

            temperature.set_value(temp)
            pressure.set_value(pres)
            motor.set_value(motor_status)
            #print(f"Temp={temp} Pressure={pres} Motor={motor_status}")
        else:
            print("⚠️ Modbus read error")

        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping server...")
finally:
    client.close()
    server.stop()
