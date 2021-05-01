import paho.mqtt.client as mqtt
import time
import json

host = 'mqtt.p2hp.com'
port = 1883
topic = '/public/1'
class mqtt_():
    def __init__(self) -> None:
        self.count=0
        self.client = mqtt.Client(clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(host, port)
        self.client.loop_forever()
        self.count=0
        self.msg=''
        self.data={}
        

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.client.subscribe(topic)
    def on_message(self,client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        # print(type((msg.payload).decode()))
        self.msg=msg
        # print((msg.payload).decode(),"  ",type(self.data))
        self.data=eval((msg.payload).decode())
        print(self.data,"  ",type(self.data))
        with open('./data.json','w') as f:
            f.write(str(self.data))
            
        self.client.disconnect()
        # self.count+=1
        # if self.count==6:
        #     self.client.disconnect()
        #     self.count=0
    def get_data_back(self):
        try:
            with open("hg.json", "r", "utf-8") as f:
                dic = json.loads(f)
            return dic
        except:
            return "数据异常!"
# a=mqtt_()
# a.get_data_back()


