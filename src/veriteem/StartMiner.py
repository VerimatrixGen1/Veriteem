import traceback
import sys
import os
import shutil
import time

from .Config import Config 

class StartMiner():

    myConfig = []

    def __init__(self, path):

        try:
           StartMiner.myConfig = Config(path)
        except:
           print ("Site configuration not specified")
           print(traceback.format_exc())
           return;
        try:
           StartMiner.myConfig.LoadConfig()
        except:
           print(traceback.format_exc())

    @classmethod
    def Start(self):
        #
        #  We are running our modified geth
        #
        pwFile = open("pauth.txt", "w")
        passwd = StartMiner.myConfig.ACCOUNTPWD 
        pwFile.writelines(passwd)
        pwFile.close()
        chainExe = StartMiner.myConfig.getChainExe()
        Cmd = chainExe + ' --mine --rpc --rpcaddr localhost --rpcport 8545 --rpcapi "web3,eth" --rpccorsdomain "http://localhost:8000" '
        Cmd = Cmd + '--datadir ' + StartMiner.myConfig.GETHDATA  + ' '
    
        Cmd = Cmd + '--port 60303 --networkid ' + StartMiner.myConfig.NETWORK + ' --targetgaslimit 15000000 --gasprice 0 --maxpeers 25 --nat none '
    
        Cmd = Cmd + ' --keystore ' + StartMiner.myConfig.KEYSTORE + ' --unlock ' + StartMiner.myConfig.ACCOUNT + ' --etherbase ' + StartMiner.myConfig.ACCOUNT 
        Cmd = Cmd + ' --password pauth.txt --bootnodes ' + StartMiner.myConfig.BOOTNODE
        Cmd = Cmd +  ' >> ' + os.path.join(StartMiner.myConfig.GETHDATA, 'logs', 'geth.log') +  ' 2>&1 &'
        
        print (Cmd)
        os.system(Cmd)
    
        print("Waiting for server to start")
        time.sleep(10)
        os.remove("pauth.txt")
