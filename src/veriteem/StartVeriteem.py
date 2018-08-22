import traceback
import sys
import os
import shutil
import time

from .Configure import Configure 
from .Config import Config 

class StartVeriteem():

    myConfig = []
    myPath = None

    def __init__(self, path):

        StartVeriteem.myPath = path

        try:
           StartVeriteem.myConfig = Config(path)
        except:
           print ("Site configuration not specified")
           print(traceback.format_exc())
           return;
        #
        #  Load the configuration 
        #
        try:
           StartVeriteem.myConfig.LoadConfig()
        except:
           print(traceback.format_exc())

    @classmethod
    def Start(self):
        #
        # If we do not have an Account, have the user create one
        #
        if StartVeriteem.myConfig.ACCOUNT is None:
           myConfigure = Configure(StartVeriteem.myPath, False)
           myConfigure.getAccount(StartVeriteem.myConfig.KEYSTORE)
           StartVeriteem.myConfig.ACCOUNT = myConfigure.Account
           StartVeriteem.myConfig.ACCOUNTPWD = myConfigure.AccountPwd
           StartVeriteem.myConfig.saveConfig(StartVeriteem.myConfig)

        #
        #  We are running our modified geth
        #
        pwFile = open("pauth.txt", "w")
        passwd = StartVeriteem.myConfig.ACCOUNTPWD 
        pwFile.writelines(passwd)
        pwFile.close()
        chainExe = StartVeriteem.myConfig.getChainExe()
        Cmd = chainExe + ' --rpc --rpcaddr localhost --rpcport 8545 --rpcapi "web3,eth" --rpccorsdomain "http://localhost:8000" '
        Cmd = Cmd + '--datadir ' + StartVeriteem.myConfig.GETHDATA  + ' '
    
        Cmd = Cmd + '--port 60303 --networkid ' + StartVeriteem.myConfig.NETWORK + ' --targetgaslimit 15000000 --gasprice 0 --maxpeers 25 --nat none '
        Cmd = Cmd + ' --keystore ' + StartVeriteem.myConfig.KEYSTORE + ' --unlock ' + StartVeriteem.myConfig.ACCOUNT + ' --etherbase ' + StartVeriteem.myConfig.ACCOUNT
    
        Cmd = Cmd + ' --password pauth.txt --bootnodes ' + StartVeriteem.myConfig.BOOTNODE
        Cmd = Cmd +  ' >> ' + os.path.join(StartVeriteem.myConfig.GETHDATA, 'logs', 'geth.log') +  ' 2>&1 &'
        
        print (Cmd)
        os.system(Cmd)
    
        print("Waiting for server to start")
        time.sleep(10)
        os.remove("pauth.txt")
