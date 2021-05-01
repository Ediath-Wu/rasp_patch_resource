import sys,time,psutil
from PyQt5.QtChart import QDateTimeAxis,QValueAxis,QSplineSeries,QChart,QChartView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QDateTime,Qt,QTimer

class ChartView(QChartView,QChart):
    def __init__(self, *args, **kwargs):
        super(ChartView, self).__init__(*args, **kwargs)
        self.resize(1500, 500)
        self.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        self.limitminute=60 #设置显示多少分钟内的活动，这个最好计算一下最终有多少点，点太多太密曲线不好看
        self.maxspeed = 200 #预设y轴最大值
        self.chart_init()
        self.timer_init()
        self.setWindowTitle("当前网卡流量")#设置标题

        self.y_list=[]
        self.data_list = []
        self.NIC_name = '以太网' #设定统计网卡，现在看到的名称不一定对，建议使用psutil.net_io_counters(pernic=True).keys()看看当前活跃的网卡名称

    def network_state(self,NIC_name):#定义一个函数通过网卡名获取该网卡的当前上下传总字节及当前时间
        key_info = psutil.net_io_counters(pernic=True).keys()
        if NIC_name not in key_info:
            return False, False, False #若无该网卡名称，返回三个f，给后面a,b,c=XXX免出错
        recv = psutil.net_io_counters(pernic=True).get(NIC_name).bytes_recv
        sent = psutil.net_io_counters(pernic=True).get(NIC_name).bytes_sent
        return time.time(), recv, sent

    def timer_init(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.drawLine)
        self.timer.start(10000) #10秒出一个点，一小时就是360点，还是好看的
    def chart_init(self):
        self.chart = QChart()
        self.series_download = QSplineSeries()
        self.series_upload = QSplineSeries()
        #设置曲线名称
        self.series_download.setName("下载速度")
        self.series_upload.setName('上传速度')
        #把曲线添加到QChart的实例中
        self.chart.addSeries(self.series_download)
        self.chart.addSeries(self.series_upload)
        #声明并初始化X轴，Y轴
        self.dtaxisX = QDateTimeAxis()
        self.vlaxisY = QValueAxis()
        #设置坐标轴显示范围
        self.dtaxisX.setMin(QDateTime.currentDateTime().addSecs(-self.limitminute*60))
        self.dtaxisX.setMax(QDateTime.currentDateTime().addSecs(0))
        self.vlaxisY.setMin(0)
        self.vlaxisY.setMax(self.maxspeed)

        #设置X轴时间样式
        self.dtaxisX.setFormat("hh:mm")

        #设置坐标轴上的格点
        self.dtaxisX.setTickCount(24)
        self.vlaxisY.setTickCount(10)
        #设置坐标轴名称
        self.dtaxisX.setTitleText("时间")
        self.vlaxisY.setTitleText("速度(M)")
        #设置网格不显示
        self.vlaxisY.setGridLineVisible(True)
        self.vlaxisY.setGridLineColor(Qt.gray)
        self.dtaxisX.setGridLineVisible(True)
        self.dtaxisX.setGridLineColor(Qt.gray)
        #把坐标轴添加到chart中
        self.chart.addAxis(self.dtaxisX,Qt.AlignBottom)
        self.chart.addAxis(self.vlaxisY,Qt.AlignLeft)
        #把曲线关联到坐标轴
        self.series_download.attachAxis(self.dtaxisX)
        self.series_download.attachAxis(self.vlaxisY)

        self.series_upload.attachAxis(self.dtaxisX)
        self.series_upload.attachAxis(self.vlaxisY)

        self.setChart(self.chart)
    def drawLine(self):
        #获取当前时间
        bjtime = QDateTime.currentDateTime()
        #更新X轴坐标
        self.dtaxisX.setMin(bjtime.addSecs(-self.limitminute*60))
        self.dtaxisX.setMax(bjtime.addSecs(0))

        if self.series_download.at(0):
            if self.series_download.at(0).x()<bjtime.addSecs(-self.limitminute * 60).toMSecsSinceEpoch():
                self.series_download.removePoints(0, 1)

        if self.series_upload.at(0):
            if self.series_upload.at(0).x()<bjtime.addSecs(-self.limitminute*60).toMSecsSinceEpoch():
                self.series_upload.removePoints(0, 1)

        a, b, c = self.network_state(self.NIC_name)
        if a:
            self.data_list.append([a, b, c])#以列表方式添加时间，上下总数到self.data_list中，至少需两个数据出差值才能统计速率
            if len(self.data_list) >= 2:#当大于等于2时可以出速率数据了
                if len(self.data_list) == 3:#如果有3个数据把0下标的去掉
                    del self.data_list[0]
                x1_recv = round((self.data_list[1][1] - self.data_list[0][1]) / (self.data_list[1][0] - self.data_list[0][0]) / 1024 / 1024,
                                2)
                x1_sent = round((self.data_list[1][2] - self.data_list[0][2]) / (self.data_list[1][0] - self.data_list[0][0]) / 1024 / 1024,
                                2)
#计算速率
                self.series_download.append(bjtime.toMSecsSinceEpoch(), x1_recv)#添加数据到相应轴
                self.series_upload.append(bjtime.toMSecsSinceEpoch(), x1_sent)#添加数据到相应轴
                self.y_list.append(max([x1_recv,x1_sent])) #上下传速率拿个最大的加到self.y_list.append以动态设置y轴最大值
                if len(self.y_list)>self.series_download.count():#self.y_list.append跟self.series_download轴保持相同数量的数据
                    del self.y_list[0]
                self.maxspeed=max(self.y_list)*1.1  #设置y轴最大值，简单乘个1.1
                self.vlaxisY.setMax(self.maxspeed) #设置y轴最大值，简单乘个1.1
                total_download=round(self.data_list[1][1]/1024/1024,2)
                total_upload=round(self.data_list[1][2]/1024/1024,2)
                self.chart.setTitle(f"当前网卡总上传{total_upload}M，总下载{total_download}M") #图表标题显示当前网卡总流量


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = ChartView()
    view.show()
    sys.exit(app.exec_())