import traceback
import sys
import os
import shutil
import time

from .Config import Config 

class StartVeriteem():

    myConfig = []

    def __init__(self, path):

        try:
           StartVeriteem.myConfig = Config(path)
        except:
           print ("Site configuration not specified")
           print(traceback.format_exc())
           return;
        try:
           StartVeriteem.myConfig.LoadConfig()
        except:
           print(traceback.format_exc())

    @classmethod
    def Start(self):
        #
        #  We are running our modified geth
        #
        chainExe = StartVeriteem.myConfig.getChainExe()
        Cmd = chainExe + ' --rpc --rpcaddr localhost --rpcport 8545 --rpcapi "web3,eth" --rpccorsdomain "http://localhost:8000" '
        Cmd = Cmd + '--datadir ' + StartVeriteem.myConfig.GETHDATA  + ' '
    
        Cmd = Cmd + '--port 60303 --networkid ' + StartVeriteem.myConfig.NETWORK + ' --targetgaslimit 15000000 --gasprice 0 --maxpeers 25 --nat none '
    
        Cmd = Cmd + ' --bootnodes ' + StartVeriteem.myConfig.BOOTNODE
        Cmd = Cmd +  ' >> ' + os.path.join(StartVeriteem.myConfig.GETHDATA, 'logs', 'geth.log') +  ' 2>&1 &'
        
        print (Cmd)
        os.system(Cmd)
    
        print("Waiting for server to start")
        time.sleep(10)
