import sys
import os
import shutil


from .Config import Config 

class InitGeth():
   
    myConfig = []

    def __init__(self, path):

       
       try:
          InitGeth.myConfig = Config(path)
          InitGeth.myConfig.LoadConfig()
       except:
          raise RunTimeError("Site Configuration Not Specified")
       

    @classmethod
    def CreateBlockChain(self):

        #
        # Make sure we have some necessary files before making changes
        #
        filePath = os.path.join(InitGeth.myConfig.CONFIGPATH, "genesis.json")
        if not os.path.exists(filePath):
           raise RunTimeError ("Missing genesis.json")

        #
        #  if we have an existing installation, remove it
        #
        filePath = os.path.join(InitGeth.myConfig.CONFIGPATH, "GethData")
        if os.path.exists(filePath):
           try:
              shutil.rmtree(filePath)
           except Exception as ex:
              print(ex)

        #
        #  Create the directories needed for operations
        #
        try:
           os.mkdir(filePath)
           os.mkdir(filePath + "/logs")
           os.mkdir(filePath + "/geth")
        except Exception as ex:
           print (ex)

        #
        # Use our modified geth to generate the new block chain with the genesis file
        #
        try:
           logFile = os.path.join(InitGeth.myConfig.GETHDATA, "logs", "geth.log")
           chainExe  = InitGeth.myConfig.getChainExe()
           genesis = os.path.join(InitGeth.myConfig.CONFIGPATH, "genesis.json")
           Cmd = chainExe + " --datadir " + InitGeth.myConfig.GETHDATA + " init " + genesis +  " >>" + logFile + " 2>&1 "
           print(Cmd)
           os.system(Cmd)
        except Exception as ex:
           print (ex)



