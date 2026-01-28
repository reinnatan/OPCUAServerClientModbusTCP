import threading
from opcua import Client
from flask import Flask
from flask_socketio import SocketIO
from pymodbus.client import ModbusTcpClient
import time


app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

client = Client("opc.tcp://localhost:4840")
client.connect()
idx = client.get_namespace_index("http://modbus.opcua.server")

modbus_lock = threading.Lock()


def modbus_loop():
    objects = client.get_objects_node()
    idx = client.get_namespace_index("http://modbus.opcua.server")
    device = objects.get_child([f"{idx}:PLC1"])

    # print for browser name
    #for child in device.get_children():
    #    bn = child.get_browse_name()
    #    print(bn.Name, " | NodeId:", child.nodeid)
    
    
    temp = device.get_child([f"{idx}:Temperature"])
    presure = device.get_child([f"{idx}:Pressure"])
    motor_status = device.get_child([f"{idx}:MotorStatus"])

    while True: # melakukan process modbus secara realtime
        socketio.sleep(2)
        try:
                data = {
                    "temprature" : temp.get_value(),
                    "pressure": presure.get_value()
                }
                socketio.emit("modbus_data", data)

                coil = {
                    "motor": motor_status.get_value(),
                }

                socketio.emit("coil_data", coil)
               
        except Exception as e:
            print("Modbus error ", e)

               
@app.route("/")
def index():
    return app.send_static_file("index.html")

socketio.start_background_task(modbus_loop)

if __name__ == "__main__":
    print("=======================")
    print("=== SERVER STARTING ===")
    print("=======================")
    socketio.run(app, host="0.0.0.0", port=5000)
