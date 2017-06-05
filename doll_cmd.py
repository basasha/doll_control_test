#coding=utf-8
import socket
import serial
import threading
import getopt
import sys
import time
port = 0
buffer_size = 1024
usbcom =''
target =''
sysnc = False
init =[0, 0, 545, 570, 555, 525, 580, 500, 555, 525, 0, 0, 0]
dic={}
f = open('saveData.txt', 'a+')
f.close()
f =open('saveData.txt', 'r+')
led =['0','0','0','0']
s_com = ''
sock=''
'''
keyboard 0,0,0,0            // 快速鍵 //最高權限
svr 887,1023,643,631,728   //  多工器輸出，由GUI導向某個硬體設備
JD1 534,563                   // 搖桿
JD2 551,521
JD3 580,501
JD4 558,523
JD5 539,531
BT 0,0,0,0,0,0                //按鈕

輸出格式：左耳 右耳 左眉上下 左眉左右 右眉上下 右眉左右 左眼上下 左眼左右 右眼上下 右眼左右 左嘴角 右嘴角 嘴巴開闔 
        svr1 svr2 JD1[0] JD1[1]   JD2[0] JD2[1]  JD3[0]  JD3[1]  JD4[0]  JD4[1] JD5[0] JD5[1]  
init = [0,0,545,570,555,525,580,500,555,525,0,0,0]
'''

def handleIO(sockets):
    global target
    global port
    global usbcom
    global sysnc
    global dic
    global f
    global led
    global s_com
    holdon = False
    UDP_IP = "192.168.4.1"
    UDP_PORT = 6000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s_com= serial.Serial(port = usbcom, baudrate = 115200)
    #so  = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    loadSetting()
    key = []
    jd1 = []
    jd2 = []
    jd3 = []
    jd4 = []
    jd5 = []
    bt  = []
    svr = []
    #key_data =[]
    #key_value = 0
    sendData = ''
    #last_key = ''
    #last_data= ''
    #dic = {}
    
    while 1:
        t =time.time()
        s_com.flushInput()
        data = s_com.readline()  #這裡基本上延遲約50-60ms
        while not (('keyboard' in data) and ('svr' in data) and ('BT' in data) and ('\n' in data)):
            data  = s_com.readline()
        print data
        print '\n'
        data      = data.replace('\n','')
        datalist  = data.split(' ')
        print 'it cost {} seconds to get data\n'.format(time.time()-t)
        print key
        print '\n'
        t=time.time()
        for i in range(0, len(datalist)):
            if 'keyboard' in datalist[i]:
                key = datalist[i+1].split(',')
            if 'JD' in datalist[i]:
                if '1' in datalist[i]: jd1 = datalist[i+1].split(',')
                if '2' in datalist[i]: jd2 = datalist[i+1].split(',')
                if '3' in datalist[i]: jd3 = datalist[i+1].split(',')
                if '4' in datalist[i]: jd4 = datalist[i+1].split(',')
                if '5' in datalist[i]: jd5 = datalist[i+1].split(',')
            if 'BT' in datalist[i]:
                bt = datalist[i+1].split(',')
            if 'svr' in datalist[i]:
                svr = datalist[i+1].split(',')
        key_value = 0 
            #將key的值轉為十進制
        for i in key:
            key_value *= 16
            key_value += int(i, 16)
            #key_data.append(int(i, 16))
        if key_value > 0:
            #pass
            # do the quick set at here
            
            if int(key[2], 16) & 0x2000 :
                holdon = not holdon
                
                #s.write('{},{},{},{}\n'.format(key[0], key[1], key[2], key[3]))
            elif int(key[2], 16) & 0x1000 :
                sysnc = not sysnc
                print 'changed '
                print key
                print '\n'        

            else:
                if holdon:
                    #last_key = key_value
                    #last_data= sendData
                    #dic[last_key] = last_data
                    dic[key_value] = sendData
                    f.write('{},{},{},{}\t{}'.format(key[0], key[1], key[2], key[3], sendData))
                    holdon = not holdon
                    if   int(key[0], 16)>0:led[0] = hex(int(led[0], 16) | int (key[0], 16)).replace('0x', '')
                    elif int(key[1], 16)>0:led[1] = hex(int(led[1], 16) | int (key[1], 16)).replace('0x', '')
                    elif int(key[2], 16)>0:led[2] = hex(int(led[2], 16) | int (key[2], 16)).replace('0x', '')
                    elif int(key[3], 16)>0:led[3] = hex(int(led[3], 16) | int (key[3], 16)).replace('0x', '')
                else:
                    if dic.get(key_value):
                        sendData = str(dic.get(key_value))
                        sock.sendto(sendData, (UDP_IP, UDP_PORT))

            if holdon:
                led[2] =hex(int(led[2], 16) | 0x2000).replace('0x', '')
            else:
                led[2] =hex(int(led[2], 16) & 0xDFFF).replace('0x', '')
            if sysnc:
                led[2] =hex(int(led[2], 16) | 0x1000).replace('0x', '')
            else:
                led[2] =hex(int(led[2], 16) & 0xEFFF).replace('0x', '')
            
            s_com.write('{},{},{},{}\n'.format(led[0], led[1], led[2], led[3]))               

        elif holdon:
            pass         
        else:
            ''' 
            jd1 =[int(int(x)/4) for x in jd1]
            jd2 =[int(int(x)/4) for x in jd2]
            jd3 =[int(int(x)/4) for x in jd3]
            jd4 =[int(int(x)/4) for x in jd4]
            jd5 =[int(int(x)/4) for x in jd5]
            bt  =[int(x) for x in  bt]
            svr =[int(int(x)/4) for x in svr]
            '''
            t = [svr[0], svr[1], jd1[0], jd1[1], jd2[0], jd2[1], jd3[0], jd3[1], jd4[0], jd4[1], svr[3], svr[4], bt[0]]
            if isInit(t):
                pass
            elif sysnc:
                sendData = '{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(svr[0], svr[1], jd3[0], jd3[1], jd3[0], jd3[1], jd4[0], jd4[1], jd4[0], jd4[1], jd5[1], jd5[1], bt[0])
            else:
                sendData = '{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(svr[0], svr[1], jd1[0], jd1[1], jd2[0], jd2[1], jd3[0], jd3[1], jd4[0], jd4[1], svr[3], svr[4], bt[0])
            
            
            '''
            print 'svr:'
            print svr
            print '\n jd'
            print jd1
            print jd2
            print jd3
            print jd4
            print jd5
            print bt
            '''
            #sendData ='{}{}{}{}{}{}{}{}{}{}{}{}{}'.format(chr(svr[0]), chr(svr[1]), chr(jd1[0]), chr(jd1[1]), chr(jd2[0]), chr(jd2[1]), chr(jd3[0]), chr(jd3[1]), chr(jd4[0]), chr(jd4[1]), chr(jd5[0]), chr(jd5[0]), chr(bt[0]))
            print 'sync {}\n{}'.format(sysnc, sendData)
            #print 'it costs {} seconds to format data'.format(time.time()-t) 約 120 us
            

            '''
            if not socket =='':
                sockets.send(sendData)
                time.sleep(0.03)
            '''
            sock.sendto(sendData, (UDP_IP, UDP_PORT))
            #time.sleep(0.05)
def prepareUDP():
    global sock
    UDP_IP = "192.168.4.1"
    UDP_PORT = 6000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
def sendUDP(sendData):
    global sock
    UDP_IP = "192.168.4.1"
    UDP_PORT = 6000
    sock.sendto(sendData, (UDP_IP, UDP_PORT))
def handleIOData(s):
    global target
    global port
    global usbcom
    global sysnc
    global dic
    global f
    global led
    global s_com
    holdon = False
    #s= serial.Serial(port = usbcom, baudrate = 115200)
    s_com = s
    loadSetting()
    key = []
    jd1 = []
    jd2 = []
    jd3 = []
    jd4 = []
    jd5 = []
    bt  = []
    svr = []
    sendData = ''
    t =time.time()
    s.flushInput()
    data = s.readline()  #這裡基本上延遲約50-60ms
    while not (('keyboard' in data) and ('svr' in data) and ('BT' in data) and ('\n' in data)):
        data  = s.readline()
    print data
    print '\n'
    data      = data.replace('\n','')
    datalist  = data.split(' ')
    print 'it cost {} seconds to get data\n'.format(time.time()-t)
    print key
    print '\n'
    t=time.time()
    for i in range(0, len(datalist)):
        if 'keyboard' in datalist[i]:
            key = datalist[i+1].split(',')
        if 'JD' in datalist[i]:
            if '1' in datalist[i]: jd1 = datalist[i+1].split(',')
            if '2' in datalist[i]: jd2 = datalist[i+1].split(',')
            if '3' in datalist[i]: jd3 = datalist[i+1].split(',')
            if '4' in datalist[i]: jd4 = datalist[i+1].split(',')
            if '5' in datalist[i]: jd5 = datalist[i+1].split(',')
        if 'BT' in datalist[i]:
            bt = datalist[i+1].split(',')
        if 'svr' in datalist[i]:
            svr = datalist[i+1].split(',')
    key_value = 0 
        #將key的值轉為十進制
    for i in key:
        key_value *= 16
        key_value += int(i, 16)
        #key_data.append(int(i, 16))
    if key_value > 0:

        if int(key[2], 16) & 0x2000 :
            holdon = not holdon

        elif int(key[2], 16) & 0x1000 :

            sysnc = not sysnc
        else:
            if holdon:
                dic[key_value] = sendData
                f.write('{},{},{},{}\t{}'.format(key[0], key[1], key[2], key[3], sendData))
                holdon = not holdon
                if   int(key[0], 16)>0:led[0] = hex(int(led[0], 16) | int (key[0], 16)).replace('0x', '')
                elif int(key[1], 16)>0:led[1] = hex(int(led[1], 16) | int (key[1], 16)).replace('0x', '')
                elif int(key[2], 16)>0:led[2] = hex(int(led[2], 16) | int (key[2], 16)).replace('0x', '')
                elif int(key[3], 16)>0:led[3] = hex(int(led[3], 16) | int (key[3], 16)).replace('0x', '')
            else:
                if dic.get(key_value):
                    sendData = str(dic.get(key_value))
                    #sock.sendto(sendData, (UDP_IP, UDP_PORT))
        if holdon:
            led[2] =hex(int(led[2], 16) | 0x2000).replace('0x', '')
        else:
            led[2] =hex(int(led[2], 16) & 0xDFFF).replace('0x', '')
        if sysnc:
            led[2] =hex(int(led[2], 16) | 0x1000).replace('0x', '')
        else:
            led[2] =hex(int(led[2], 16) & 0xEFFF).replace('0x', '')
        
        s.write('{},{},{},{}\n'.format(led[0], led[1], led[2], led[3]))               
    
    elif holdon:
        pass         
    else:
        t = [svr[0], svr[1], jd1[0], jd1[1], jd2[0], jd2[1], jd3[0], jd3[1], jd4[0], jd4[1], svr[3], svr[4], bt[0]]
        if isInit(t):
            pass
        elif sysnc:
            sendData = '{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(svr[0], svr[1], jd3[0], jd3[1], jd3[0], jd3[1], jd4[0], jd4[1], jd4[0], jd4[1], jd5[1], jd5[1], bt[0])
        else:
            sendData = '{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(svr[0], svr[1], jd1[0], jd1[1], jd2[0], jd2[1], jd3[0], jd3[1], jd4[0], jd4[1], svr[3], svr[4], bt[0])

    return sendData

def isInit(target):
    global init
    if len(target) == len(init):
        for i in range(0, len(target)):
            if abs(init[i]-int(target[i])) > 30:
                return False
    else:
        return False
    return True             
                
def server_loop():
    global target
    global port
    print 'listen on {} with port number {}'.format(target, port) 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # spin off a thread to handle our new client
        client_thread = threading.Thread(target=handleIO,
        args=(client_socket,))
        client_thread.start()


def usage():
    print 'please send some argument to fire up this script\n'
    print 'Usage:  '
    print '-u -usbcom this means the address of usb comPort  where your control board is connected'
    print 'you can find this by use bash script "ls -l /dev/cu*" (on macOS)'
    print '-t -target this means your tcp server ip'
    print '-p -port this means your tcp server port number'
    print 'Example: '
    print 'doll_cmd.py -u /dev/cu.wchusbserial1d**** -t 192.168.0.1 -p 6666 '

    sys.exit(0)
def setComPort(c):
    global usbcom
    usbcom = c

def loadSetting():
    global f
    global dic
    global led
    global s_com
    f.seek(0)
    while 1:
        r =f.readline()
        if len(r):
            #r = r.replace('\n','')
            datalist = r.split('\t')
            key = datalist[0].split(',')
            key_value = 0 
            #將key的值轉為十六進制
            for i in key:
                key_value *= 16
                key_value += int(i, 16)
            dic[key_value] = datalist[1]
            if   int(key[0], 16)>0:led[0] = hex(int(led[0], 16) | int (key[0], 16)).replace('0x', '')
            elif int(key[1], 16)>0:led[1] = hex(int(led[1], 16) | int (key[1], 16)).replace('0x', '')
            elif int(key[2], 16)>0:led[2] = hex(int(led[2], 16) | int (key[2], 16)).replace('0x', '')
            elif int(key[3], 16)>0:led[3] = hex(int(led[3], 16) | int (key[3], 16)).replace('0x', '')   
            print 'loadSetting success-----------------***********************'
        else:break   
    s_com.write('{},{},{},{}\n'.format(led[0], led[1], led[2], led[3]))
def saveDic():
    pass
def main():
    global port
    global usbcom
    global target
    if not len(sys.argv[1:]):
        usage()
    # read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hu:t:p:",
        ["help","usbcom","target","port"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-u", "--usbcom"):
            usbcom = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"
    if (len(target) and len(usbcom) and port>0):
        
        server_loop()
    elif len(usbcom):    
        handleIO('')
    else:
        usage() 


if __name__ =='__main__':
    #f = open('saveData.txt', 'w+')
    #f.close()
    global f
    try:
        #loadSetting()
        main()
    except Exception, e:
        raise
    except KeyboardInterrupt, k:
        raise    
    else:
        pass
    finally:
        
        f.close()

    #main()
    #handleIO('/dev/cu.wchusbserial1d1140')















