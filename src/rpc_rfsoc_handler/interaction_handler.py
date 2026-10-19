import grpc
import os
import json
import base64
import serial
from . import devicecontrol_pb2
from . import devicecontrol_pb2_grpc

class InteractionHandler:
    def __init__(self, ip_address, timeout=2.0):
        self.ip_address = ip_address
        self.channel = grpc.insecure_channel(
            self.ip_address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ],
        )

        try:
            grpc.channel_ready_future(self.channel).result(timeout=timeout)
        except grpc.FutureTimeoutError:
            raise ConnectionError(
                f"Couldn't connect to {self.ip_address}")
        
        self.stub =  devicecontrol_pb2_grpc.DeviceServiceStub(self.channel)
    
    def send_message(self, instruction, par):
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name=instruction, value=par))
        print("Response:", response.success, response.message)
    
    def send_start(self):
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="start_sending", value=1))
        print("Response:", response.success, response.message)
    
    def send_stop(self):
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="stop_sending", value=1))
        print("Response:", response.success, response.message)

    def send_set_trigger_in(self):
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="set_trigger", value=0))
        print("Response:", response.success, response.message)
    
    def send_set_trigger_out(self):
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="set_trigger", value=1))
        print("Response:", response.success, response.message)
    
    def send_data(self, filepath):
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            data = f.read()
        response = self.stub.SendData(
            devicecontrol_pb2.DataMessage(
                id=filename,
                filename=filename,
                data=data
            )
        )
        print("Response:", response.success, response.message)
    
    def list_files(self):
        response = self.stub.ListFiles(devicecontrol_pb2.ListFilesRequest())
        return [f.filename for f in response.files]


    def select_signal(self, channel_id, filename):
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="load_signal", value=channel_id, filename=filename))
        print("Response:", response.success, response.message)
    
    def delete_signal(self, filename):
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="delete_signal", value=0, filename=filename))
        print("Response:", response.success, response.message)
    
    def set_freq(self, frequency):
        freq = int(frequency)
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="set_sample_freq", value=freq))
        print("Response:", response.success, response.message)

    def set_scaling(self, scaling):
        scal = int(scaling*100)
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="set_scaling_freq", value=scal))
        print("Response:", response.success, response.message)

    def set_sending_mode(self, mode):
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="set_sending_mode", value=mode))
        print("Response:", response.success, response.message)

class SerialInteractionHandler:
    def __init__(self, port="/dev/ttyUSB1", baudrate=3000000, timeout=5.0):                                                                                                                    
      try:                                                                                                                                                                                   
          self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)                                                                                                                 
      except serial.SerialException as e:                                                                                                                                                    
          raise ConnectionError(f"Could not open serial port {port}: {e}") from e                                                                                                                                                                                                                                                                                               
      try:                                                                                                                                                                                   
          resp = self._send({"method": "ping"})                                                                                                                                              
          if not resp.get("success"):                                                                                                                                                        
              raise ConnectionError(f"Handshake failed: {resp.get('message')}")                                                                                                              
      except Exception as e:                                                                                                                                                                 
          self.ser.close()                                                                                                                                                                   
          raise ConnectionError(f"No response from device on {port}") from e 
    
    def _send(self, payload: dict, timeout=None) -> dict:
        if timeout is not None:
            self.ser.timeout = timeout
        line = json.dumps(payload) + "\n"
        self.ser.reset_input_buffer()
        self.ser.write(line.encode())
        self.ser.flush()
        resp = self.ser.readline().decode().strip()
        if timeout is not None:
            self.ser.timeout = 5.0
        print(f"[DEBUG] sent={list(payload.keys())} raw_resp={repr(resp)}")
        return json.loads(resp)

    def send_start(self):
        return self._send({"method": "start_sending"})

    def send_stop(self):
        return self._send({"method": "stop_sending"})

    def send_set_trigger_in(self):
        return self._send({"method": "set_trigger_in"})

    def send_set_trigger_out(self):
        return self._send({"method": "set_trigger_out"})

    def set_freq(self, frequency):
        return self._send({"method": "set_freq", "value": frequency})

    def set_sending_mode(self, mode):
        return self._send({"method": "set_sending_mode", "value": mode})

    def list_files(self):
        resp = self._send({"method": "list_files"})
        return resp.get("files", [])

    def select_signal(self, channel_id, filename):
        return self._send({"method": "select_signal", "channel_id": channel_id, "filename": filename})

    def delete_signal(self, filename):
        return self._send({"method": "delete_signal", "filename": filename})

    def send_data(self, filepath):
        with open(filepath, "rb") as f:
            raw = f.read()
        data = base64.b64encode(raw).decode()
        filename = filepath.split("/")[-1]
        # timeout scales with file size: 10s base + 1s per 10KB
        transfer_timeout = 10.0 + len(raw) / 10_000
        return self._send({"method": "send_data", "filename": filename, "data": data}, timeout=transfer_timeout)

    def close(self):
        self.ser.close()