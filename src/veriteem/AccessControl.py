import traceback
import sys
import os
import shutil
import time

from .Config import Config 

class AccessControl():

    myConfig = []

    def __init__(self, path):

        try:
           AccessControl.myConfig = Config(path)
        except:
           print ("Site configuration not specified")
           print(traceback.format_exc())
           return;
        try:
           AccessControl.myConfig.LoadConfig()
        except:
           print(traceback.format_exc())

    @classmethod
    def AddAccess(self):
        #
        #  We are running our modified geth
        #
        scriptPath = os.path.join(AccessControl.myConfig.INSTALLPATH, "scripts")
        ipcPath = os.path.join(AccessControl.myConfig.GETHDATA, "geth.ipc")
        os.chdir(scriptPath)

        # provide the password control to run the access control script
        pwFile = open("Access.js", "w")
        pwFile.writelines('var ContractOwner = "' + AccessControl.myConfig.ACCOUNT + '"\n')
        pwFile.writelines('var ContractOwnerPassword = "' + AccessControl.myConfig.ACCOUNTPWD + '"\n')
        pwFile.close()
        
        chainExe = AccessControl.myConfig.getChainExe()

        Cmd = chainExe + ' --exec "loadScript(' + "'AddAccessRights.js')" + '" attach ipc:' + ipcPath
        Cmd = Cmd +  ' >> ' + os.path.join(AccessControl.myConfig.GETHDATA, 'logs', 'accesscontrol.log') +  ' 2>&1 &'
        
        print (Cmd)
        os.system(Cmd)
    
        os.remove("Access.js")
