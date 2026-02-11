import grpc
import os
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

    def set_sending_mode(self, mode):
        response = self.stub.SendCommand(devicecontrol_pb2.Command(name="set_sending_mode", value=mode))
        print("Response:", response.success, response.message)