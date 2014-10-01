#http://www.blogjava.net/cpegtop/articles/384466.html 
#put ganymed-ssh2-build210.jar to jre lib/ext folder

from java.io import BufferedReader
from java.io import IOException
from java.io import InputStream
from java.io import InputStreamReader
from ch.ethz.ssh2 import Connection
from ch.ethz.ssh2 import Session
from ch.ethz.ssh2 import StreamGobbler
  
    
import sys
import os
import logging


class Jssh():
    logger=logging.getLogger(__name__) 
    
    def __init__(self, hostname, user, password):
        self.hostname = hostname
        self.user = user
        self.password = password
   
         
    def excmd(self, sshcmd):
        '''
        return (connected_ok, response_array)
        '''
        try:
            return self._excmd(sshcmd)
        except Exception, ex:
            connected_ok=False
            resp = [] 
            resp.append('%s'%ex) 
            return (connected_ok,resp)    


    def _excmd(self, sshcmd):
        '''
        return (connected_ok, response_array)
        '''        
        connected_ok=True
        resp = []        
        try:
            conn = Connection(self.hostname)
            conn.connect()
            self.logger.info('ssh connection created.')
            isAuthenticated = conn.authenticateWithPassword(self.user, self.password)
            if not isAuthenticated:
                connected_ok=False
                self.logger.error('ssh failed to authenticatd.')
            else:
                self.logger.info('ssh authenticated.')
                sess = conn.openSession()
                
                self.logger.info('ssh session created.')
                sess.execCommand(sshcmd)
                self.logger.info('ssh command issued. cmd is %s'%sshcmd)
    
                stdout = StreamGobbler(sess.getStdout())
                br = BufferedReader(InputStreamReader(stdout))
                while True:
                    line = br.readLine()
                    if line is None:
                        break
                    else :
                        resp.append(line)
                self.logger.warning('ssh command output: '%resp)
        except IOException ,ex:
            connected_ok=False
            #print "oops..error,", ex            
            self.logger.error('ssh exception: %s'% ex)
        finally:
            sess.close()
            self.logger.info('ssh session closed.')
            conn.close()
            self.logger.info('ssh connection closed.')
            return (connected_ok,resp)
        
        
                 
def ssh_exec(hostname,user,password,sshcmd):
    ss = Jssh(hostname,user,password)
    return ss.excmd(sshcmd) 
            
       

if __name__ == '__main__':  
    ssh_exec(hostname='XXXXX', user='root', password='XXXX',sshcmd='ls')
