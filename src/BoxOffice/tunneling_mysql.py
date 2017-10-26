'''
Created on 13 ott 2017

@author: gmiletto
'''
import subprocess

class MySQL_Ssh_Tunnel(object):
    '''
    classdocs
    '''


    def __init__(self, host_name):
        '''
        Constructor
        '''
        self.result=None
        self.host_name = host_name
        self.user_name = 'ltc'
        self.active = False
        
    def ssh_start(self):
        self.result= subprocess.run(['ssh','-n','-N','-f','-L','3306:127.0.0.1:3306', '{}@{}'.format(self.user_name,self.host_name)],
                                    stdout=subprocess.PIPE)
#        self.result= subprocess.run("ssh -n -N -f -L 3306:127.0.0.1:3306 {}@{}".format(self.user_name,self.host_name),

        print(self.result.stdout.decode('utf-8'))
        return
        
    def test(self):
        self.result= subprocess.run("ps -ax |grep 'ssh -n -N -f -L 3306:127.0.0.1:3306'", stdout=subprocess.PIPE).decode('utf-8')
        for row in self.result:
            if self.host_name in row:
                self.pid = row.split(' ')[0]
                self.active=True
                break
            else:
                self.active=False
                self.pid=None
        return(self.active,self.pid)
    
                
        