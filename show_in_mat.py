import matplotlib.pyplot as plt
import time
import random
import json
import paho.mqtt.client as mqtt
# from mqtt_sub_demo import mqtt_

class show_in():
    def __init__(self) -> None:

        self.times=[]
        
        self.cpu_temp=[]
        self.cpu_usage=[]
        
        self.ram_total=[]
        self.ram_used=[]
        self.ram_prec=[]
        
        self.disk_total=[]
        self.disk_used=[]
        self.disk_prec=[]
        self.ip=''
        # self.cli=mqtt_()
        self.data={}
        self.data_json=''
        
        self.topic="/public/1"
        self.port=1883
        self.host="mqtt.p2hp.com"
        
        self.client=mqtt.Client(clean_session=True)
        self.client.on_connect=self.on_connect
        self.client.on_message=self.on_message
        self.client.connect(self.host,self.port)
        self.client.loop_forever()
        
        self.msg=''
        self.times={}
        self.data={}


    def change_data(self,new_time,new_data):
        self.cpu.append(new_data)
        self.times.append(new_time)
        if len(self.cpu)>=7:
                del self.cpu[0]
                del self.times[0]
    
    def get_data_from_mqtt_server(self,port='',topic='',host=''):
        # example
        # host = 'mqtt.p2hp.com'
        # port = 1883
        # topic = '/public/1'
        port =self.port
        topic=self.topic
        host=self.host
        
        self.client=mqtt.Client()
        self.client.connect(host,port)
        self.client.loop_start()

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.client.subscribe(self.topic)
    
    def on_message(self,client, userdata, msg):
        self.data=eval((msg.payload).decode())
        # print(self.data,type(self.data))
        for key in self.data.keys():
            # print(self.data[key])
            # self.times.append(self.data[key]["localtime"])
            # print(type(eval(self.data[key])))
            # print(eval(self.data[key]))
            temp=eval(self.data[key])
            if len(self.cpu_temp)>7:
                del self.times[0]
                del self.cpu_temp[0]
            self.times.append(temp["localtime"])
            self.cpu_usage.append(temp["CPU_usage"])
            self.cpu_temp.append(temp["CPU_temp"])
            self.ram_total.append(temp["RAM_total"])
        print(self.times)
        print(self.ram_total)
        self.draw_on_plt()
        
    
    def draw_on_plt(self):
        plt.ion()
        print("start")
        plt.figure(figsize=(10,10))
        plt.plot(self.times,self.cpu_usage,label='cpu usage',color="r")
        plt.xticks(rotation=30,fontsize=14)
        plt.yticks(range(5,100,5))
        plt.ylabel('CPU usage',fontsize=14)
        plt.pause(1)
        plt.ioff()
        plt.show()
        plt.


if __name__ == "__main__":
    a=show_in()
    a.get_data_from_mqtt_server()