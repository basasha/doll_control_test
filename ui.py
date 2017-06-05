# coding=utf-8
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QProgressBar, QComboBox, QSlider, QFileDialog, QCheckBox
    )
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QKeyEvent
import subprocess
import serial
import threading
import sys
import time
import datetime
from pynput import keyboard
import getch
import re
import doll_cmd
Ts = 50 #sampling time(ms)
class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        # 設定UI介面初始大小
        self.setMinimumSize(640, 480)
        self.setMaximumSize(640, 480)
        # 設定UI介面上的各個元件
        self.broseBtn = QPushButton('Brose', self)
        self.playBtn = QPushButton('Play', self)
        self.recordBtn = QPushButton('Record', self)
        self.saveBtn = QPushButton('Save', self)
        self.stopBtn = QPushButton('Stop', self)
        self.logLabel = QLabel('Log',self)
        self.timeLabel=QLabel('time',self)
        self.pathViewer=QLabel('',self)
        self.comboBox=QComboBox(self)
        self.comboBox2=QComboBox(self)
        self.view1=QLabel('Input Port', self)
        self.view2=QLabel('Output Port', self)
        self.track01 = QCheckBox('Track01', self)
        self.track02 = QCheckBox('Track02', self)
        self.track03 = QCheckBox('Track03', self)
        self.track04 = QCheckBox('Track04', self)

        self.eyeCheck     = QCheckBox('eye', self)
        self.eyebrowCheck = QCheckBox('eyebrow', self)
        #self.noseCheck    = QCheckBox('nose', self)
        self.mouthCheck   = QCheckBox('mouth', self)
        self.earCheck     = QCheckBox('ear', self)
        self.allCheck     = QCheckBox('all', self)




        '''
        #架構改變 每個軌道包含不同的輸入輸出選擇
        #亦添加部分錄製功能
        #未來以下幾個UI物件希望能模組化
        ####
        #UI物件
        self.sourceList   = QComboBox(self)
        self.sourceLabel  = QLabel('Source', self)
        self.deviceList   = QComboBox(self)
        self.deviceLabel  = QLabel('Device', self)
        self.eyeCheck     = QCheckBox('eye', self)
        self.eyebrowCheck = QCheckBox('eyebrow', self)
        #self.noseCheck    = QCheckBox('nose', self)
        self.mouthCheck   = QCheckBox('mouth', self)
        self.earCheck     = QCheckBox('ear', self)
        self.allCheck     = QCheckBox('all', self)
        self.timeSlider   = QSlider(Qt.Horizontal)
        self.tLabel       = QLabel('time', self)
        #賦值給各個UI元件
        self.timeSlider.setMaximum(100)
        self.timeSlider.setMinimum(0)
        self.slider.setValue(0)
        self.sourceList.addItem('None')
        self.sourceList.addItem('commPort')
        self.sourceList.addItem('wifi')
        #connect()
        #if self.allCheck.isChecked():
            #self.eyeCheck.
        ####
        '''
        # 賦值給各個UI元件
        self.slider=QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.valuechange)
        self.broseBtn.clicked.connect(self.handlebroseBtn)
        self.playBtn.clicked.connect(self.handleplayBtn)
        self.recordBtn.clicked.connect(self.handlerecordBtn)
        self.saveBtn.clicked.connect(self.handlesaveBtn)
        self.stopBtn.clicked.connect(self.handlestopBtn)

        self.eyeCheck.stateChanged.connect(lambda: self.handleCheck(self.eyeCheck))
        self.eyebrowCheck.stateChanged.connect(lambda: self.handleCheck(self.eyebrowCheck))
        #self.noseCheck.stateChanged.connect(lambda: self.handleCheck(self.noseCheck))
        self.earCheck.stateChanged.connect(lambda: self.handleCheck(self.earCheck))
        self.mouthCheck.stateChanged.connect(lambda: self.handleCheck(self.mouthCheck))
        self.allCheck.stateChanged.connect(lambda: self.handleAllCheck())



        #設定初始資料
        self.logList=['Welcome to this Qbe Robot Expression Editor ver.0.1.0\n','Have a nice Day !!\n',]
        
        #設置資料內部計數器，方便資料寫入
        self.timeFlag=0
        self.timeMax=0
        self.setTime(self.timeFlag* 0.001)
        self.setLog()
        self.mode = 0 # 0 as init; 1 as recording ; 2 as playing ; 3 as pause 

        self.lastFlag = 0
        self.tracks=[self.track01, self.track02, self.track03, self.track04]
        self.tracksEnable=[True, False, False, False]

        
        #prepareComboBox Item
        # use s.sh to get the com port
        try:
            ans = subprocess.check_output('./s.sh')
        except subprocess.CalledProcessError:
            self.logList.append('Warning!! there are no devices connected.\n')
            ans='NULL\n'
        mlist=ans.split('\n')
        mlist=mlist[:len(mlist)-1]
        for i in mlist:
            self.comboBox.addItem(i)
            self.comboBox2.addItem(i)


        layout = QGridLayout(self)
        layout.addWidget(self.broseBtn, 2, 4, 1, 1)
        layout.addWidget(self.playBtn, 3, 1, 1, 1)
        layout.addWidget(self.stopBtn, 3, 2, 1, 1)
        layout.addWidget(self.recordBtn, 3, 3, 1, 1)
        layout.addWidget(self.saveBtn, 3, 4, 1, 1)
        layout.addWidget(self.pathViewer, 2, 0, 1, 4)
        layout.addWidget(self.timeLabel, 3, 0, 1, 1)
        layout.addWidget(self.slider,6, 0, 1, 5)
        layout.addWidget(self.logLabel, 7, 0, 1, 5)
        layout.addWidget(self.comboBox, 0, 1, 1, 3)
        layout.addWidget(self.comboBox2,1, 1, 1, 3)
        layout.addWidget(self.view1,0, 0, 1, 1)
        layout.addWidget(self.view2,1, 0, 1, 1)
        layout.addWidget(self.track01, 4, 0, 1, 1)
        layout.addWidget(self.track02, 4, 1, 1, 1)
        layout.addWidget(self.track03, 4, 2, 1, 1)
        layout.addWidget(self.track04, 4, 3, 1, 1)
        
        layout.addWidget(self.eyeCheck, 5, 0, 1, 1)
        layout.addWidget(self.eyebrowCheck, 5, 1, 1, 1)
        #ayout.addWidget(self.noseCheck, 5, 2, 1, 1)
        layout.addWidget(self.mouthCheck, 5, 2, 1, 1)
        layout.addWidget(self.earCheck, 5, 3, 1, 1)
        layout.addWidget(self.allCheck, 5, 4, 1, 1)

        for i in range(0 ,len(self.tracksEnable)):
            if self.tracksEnable[i]:
                self.tracks[i].setCheckState(Qt.Checked)
            else:
                self.tracks[i].setCheckState(Qt.Unchecked)

    def handleCheck(self, this):
        if not this.isChecked():self.allCheck.setCheckState(Qt.Unchecked)
    def handleAllCheck(self):
        if self.allCheck.isChecked():
            self.eyeCheck.setCheckState(Qt.Checked)
            self.eyebrowCheck.setCheckState(Qt.Checked)
            #self.noseCheck.setCheckState(Qt.Checked)
            self.earCheck.setCheckState(Qt.Checked)
            self.mouthCheck.setCheckState(Qt.Checked)

    def handlebroseBtn(self):
        self.logList.append('broseBtn Clicked!\n')
        self.setLog()
        openfile = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.pathViewer.setText(openfile)
    def handleplayBtn(self):
        self.logList.append('playBtn Clicked!\n')
        self.setLog()
        SendDataHandle=threading.Thread(target=self.handleReadWrite, args=(self.comboBox.currentText(),self.comboBox2.currentText()))
        self.Flag=True
        self.mode=2
        SendDataHandle.start()
        self.timeFlag=self.slider.value() * self.timeMax * 0.01
    def handlerecordBtn(self):
        self.logList.append('recordBtn Clicked!\n')
        self.setLog()

        SerialHandle=threading.Thread(target=self.handleReadWrite, args=(self.comboBox.currentText(),self.comboBox2.currentText(),))
        self.Flag=True
        self.mode=1
        SerialHandle.start()
    def handlesaveBtn(self):
        self.logList.append('saveBtn Clicked!\n')
        self.setLog()
    def handlestopBtn(self):
        self.logList.append('stopBtn Clicked!\n')
        self.setLog()
        self.Flag=False
        self.timeFlag=0
    def prepareComboBox(self):
        # use s.sh to get the com port
        ans = subprocess.check_output('./s.sh')
        mlist=ans.split('\n')
        mlist=mlist[:len(mlist)-1]
        for i in mlist:
            self.comboBox.addItem(i)
    def setLog(self):
        if len(self.logList) > 10 : 
            self.logList=self.logList[len(self.logList)-10: len(self.logList)]              
        s=''
        for e in self.logList:
            s+=''.join(str(e))
        self.logLabel.setText(s)
        #self.logList=[]

    def handleReadWrite(self, inPort, outPort):
        si = serial.Serial (port=inPort, baudrate=115200)
        so = serial.Serial (port=inPort, baudrate=115200)
        files  = []
        cursor = []
        doll_cmd.prepareUDP()
        doll_cmd.setComPort(inPort) 
        #initial the tracks file
        for i in range(0,4):
            if self.tracksEnable[i]:
                s  = 'track0{}.txt'.format(i+1)
                f  = open(s, 'a+')
                f.close()
                files.append(open(s, 'r+'))
                cursor.append(0)

        count = 0
        si.flushInput()
        while self.Flag:
            if self.mode == 3: # pause mode
                si.flushInput()
                time.sleep(Ts * 0.001)
                continue
            if self.mode == 1: # record mode
                '''
                si.flushInput()
                data = si.readline()
                while not self.strAuth(data):
                    if not data: self.Flag = False
                    data = si.readline()
                data = self.handleOutputData(data, 4)    
                so.write(data)
                '''
                data = doll_cmd.handleIOData(si)
                
                doll_cmd.sendUDP(data)

                stamp = self.zeroFill('@'+str(count * Ts)+'@', 8)
                count += 1
                #data = self.zeroFill(data, 4)
                self.logList.append(data)
                self.setLog()

                cursor = self.writeData2File(files, stamp + data, cursor)

                self.setTime(count * 0.001)

            if self.mode == 2: # play mode
                si.flushInput()
                #datas   = files[0].readline()
                cursor, data =self.readDatafromFile(files, cursor)
                if len(data) == 0: 
                    self.Flag=False
                    continue
                s=data[0].split('@')
                if len(s) < 2: 
                    self.Flag=False
                    continue
                if int(s[1]) > int(self.timeFlag):
                    self.logList.append(s[1]+'@@'+s[2])
                    self.setLog()
                    #so.write(s[2])
                    doll_cmd.sendUDP(s[2])
                    time.sleep(Ts * 0.001)

        #f.write('####\n')
        #f.close()
        for fi in files:
            if self.mode == 1:
                if fi.readline() =='':
                    fi.write('######################################################\n')
                #each row 55 words
            fi.close()

    # @rewrite_needed
    def setTime(self, time):
        st = datetime.datetime.fromtimestamp(time).strftime('%M:%S')
        self.timeLabel.setText(st)

    # @rewrite_needed
    def valuechange(self):
        self.timeFlag=self.timeMax * 0.01 *self.slider.value()
        self.setTime(self.timeFlag * 0.001)    


    #確認現在哪個按鈕被按，並讀取鍵盤事件
    def on_press(self, key):
        if key == keyboard.Key.space :
            self.Flag = False
        setLog(key +' is pressed\n')
    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_R:
                self.mode = 1
            if event.key() == Qt.Key_P:
                if self.mode == 1 : pass
                else : self.mode == 2
            if event.key() == Qt.Key_Space:
                if self.lastFlag == 0 :
                        self.lastFlag  = self.mode
                        self.mode = 3
                else:
                    self.mode = self.lastFlag
                    self.lastFlag  = 0
        self.logList.append( str(event.key()) +' is pressed!\n')
        self.setLog()

    #將字串中所有數字出現的地方，未達特定的長度者，補０將之補滿    
    def zeroFill(self, string, cout):
        s = ''
        numlist  = re.split('\D', string)
        chaclist = re.split('\d{1,4}', string)
        if chaclist[0] == '':
            for i in range(0,len(chaclist)):
                s += chaclist[i] 
                if not numlist[i] == '':
                    s += str(numlist[i]).zfill(cout)
        else:
            for i in range(0,len(chaclist)):
                if not numlist[i] == '':
                    s += str(numlist[i]).zfill(cout)
                s += chaclist[i]                        
        return s

    #判斷字串是否符合最小單位之資料需求#等待更正
    def strAuth(self, string):    
        l=string.split(',')
        if '\n' in string and len(l) > 11:
            return True
        else: return False

    #寫入資料 不過多軌輸出入功能尚未完成，單軌輸出入請引入只含單筆資料之清單
    def writeData2File(self, files, data, cursor):
        if not data == '' :
            s =''
            c = []
            for i in range(0, len(files)):
                if self.tracks[i].isChecked():
                    files[i].seek(cursor[i])
                    s = files[i].readline()
                    files[i].seek(cursor[i])
                    a =s.split('@')
                    if  len(a) > 2:#有可能打亂整個排序
                        files[i].write(self.handleWriteData(s, data, 4))
                    else:
                        
                        files[i].write(data)

                    c.append(files[i].tell())
        return c

    #讀出資料 不過多軌輸出入功能尚未完成，單軌輸出入請引入只含單筆資料之清單
    def readDatafromFile(self, files, cursor):
        c = []
        d = []
        for i in range(0, len(files)):
            if self.tracks[i].isChecked():
                files[i].seek(cursor[i])
                d.append(files[i].readline())
                c.append(files[i].tell())
        return c, d




    '''
    左眉角度 左眉高度 眼珠左右 眼珠上下 右耳 左耳 嘴 右眉角度 右眉高度
    self.dataCheck =
    [self.eyeCheck, self.eyebrowCheck, self.noseCheck, self.earCheck, self.mouthCheck]

    '''
    # rewrite_needed or deprecate_needed
    def handleOutputData(self, data, cout):
        if self.allCheck.isChecked():
            return self.zeroFill(data, cout )
        else:
            s = ''
            numlist  = re.split('\D', data)
            chaclist = re.split('\d{1,4}', data)
            if not self.eyeCheck.isChecked():     
                numlist[6]=doll_cmd.init[6]
                numlist[7]=doll_cmd.init[7]
                numlist[8]=doll_cmd.init[8]
                numlist[9]=doll_cmd.init[9]
            if not self.eyebrowCheck.isChecked():
                numlist[2]=doll_cmd.init[2]
                numlist[3]=doll_cmd.init[3]
                numlist[4]=doll_cmd.init[4]
                numlist[5]=doll_cmd.init[5]
            if not self.earCheck.isChecked():
                numlist[0]= doll_cmd.init[0]
                numlist[1]= doll_cmd.init[1]
            if not self.mouthCheck.isChecked():
                numlist[10]=doll_cmd.init[10]
                numlist[11]=doll_cmd.init[11]
                numlist[12]=doll_cmd.init[12]


            if chaclist[0] == '':
                for i in range(0,len(chaclist)):
                    s += chaclist[i] 
                    if not numlist[i] == '':
                        s += str(numlist[i]).zfill(cout)
            else:
                for i in range(0,len(chaclist)):
                    if not numlist[i] == '':
                        s += str(numlist[i]).zfill(cout)
                    s += chaclist[i]                        
            return s
    def handleWriteData(self, oldData, newData, cout):
        
        
        new = newData.split('@')
        #print new[2]
        s =new[0] + '@' + new[1] +'@' 
        newNum = re.split('\D', new[2])
        
        chaclist = re.split('\d{1,4}', new[2])
        

        #oldChaclist = re.split('\d{1,4}', newData)
        numlist = newNum

        if '#' not in oldData:
            o  = oldData.split('@')
            if len(o) > 2:
                oldNum = re.split('\D', o[2])
                
                if not self.eyeCheck.isChecked():     
                    numlist[6]=oldNum[6]
                    numlist[7]=oldNum[7]
                    numlist[8]=oldNum[8]
                    numlist[9]=oldNum[9]
                if not self.eyebrowCheck.isChecked():
                    numlist[2]=oldNum[2]
                    numlist[3]=oldNum[3]
                    numlist[4]=oldNum[4]
                    numlist[5]=oldNum[5]
                if not self.earCheck.isChecked():
                    numlist[0]=oldNum[0]
                    numlist[1]=oldNum[1]
                if not self.mouthCheck.isChecked():
                    numlist[10]=oldNum[10]
                    numlist[11]=oldNum[11]
                    numlist[12]=oldNum[12]


        if chaclist[0] == '':
            for i in range(0,len(chaclist)):
                s += chaclist[i] 
                if not numlist[i] == '':
                    s += str(numlist[i]).zfill(cout)
        else:
            for i in range(0,len(chaclist)):
                if not numlist[i] == '':
                    s += str(numlist[i]).zfill(cout)
                s += chaclist[i]                        
        return s


if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec_())
