'''
Created on 24 ott 2017

@author: gmiletto
'''
import threading
import time
import MySQLdb

class TestThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        
    def open(self):
        try:
            try:
                self.mysql= MySQLdb.connect("127.0.0.1","ltc","ltc","ltcsite")
                self.mysqlcursor=self.mysql.cursor()
                self.mysqlcursor.execute("SELECT VERSION()")
            except (MySQLdb.Error,MySQLdb.Warning) as e:  # @UndefinedVariable
                print(e)
                self.mysql_active=False
                exit(1)
        
            self.mysql_active=True
            data,=self.mysqlcursor.fetchone()
            print("Version of mysql opened ={}".format(data))
            
        finally:
            if self.mysql_active:
                print("OK ---> Connection to MySqlDb establish!")
            else:
                print("KO ---> Connection to MySqlDb cannot be established!")

    def run(self):
        threadLock.acquire()
        self.counter=0
        while 1:
            try:
                self.mysqlcursor.execute("SELECT VERSION()")
            except (MySQLdb.Error,MySQLdb.Warning) as e:  # @UndefinedVariable
                print(e)
                self.mysql_active=False
                exit(1)
        
            self.mysql_active=True
            self.data,=self.mysqlcursor.fetchone()
            printQuery(self.name,self.counter,60, self.data)
            self.counter+=1
        threadLock.release()

def printQuery(threadName,counter ,delay, data):
        time.sleep(delay)
        print("%s: Control number %d at %s Version = %s"% (threadName, counter,time.ctime(time.time()),data))

threadLock = threading.Lock()
threads = []

# CREIAMO DUE THREAD
thread1 = TestThread(1, "Thread 1", 1)
# thread2 = TestThread(2, "Thread 2", 2)

# AVVIAMO I NUOVI THREAD
thread1.open()
thread1.start()
# thread2.start()
threads.append(thread1)
# threads.append(thread2)

for t in threads:
    t.join()

print("Fine del main thread")