import sys
import os
import shutil
import getpass
import csv
import json
import base64

from .Config import Config

class Configure():

    noSavePath = False
    AccountPwd = None
    Account    = None
    myConfig   = []
  
    def __init__(self, path, noSavePath):
        #
        #  locate the directory where the config.json exists
        # 
        Configure.noSavePath = noSavePath 
        Configure.myConfig = Config(path)
        try:
           Configure.myConfig.LoadConfig() 
        except Exception as ex:
           raise Exception(ex)
        
    @classmethod
    def getChainId(self):
        try:
           filePath    = Configure.myConfig.getFilePath("genesis.json")
           genesisFile = open(filePath, "r") 
           genesisStr  = genesisFile.read()
           genesisData = json.loads(genesisStr)
        except:
           raise Exception("Cannot locate valid genesis.json file")

        try:
           ConfigData = genesisData["config"]
           chainId = ConfigData["chainId"]
        except:
           raise Exception("no chainId value in genesis.json")
        return chainId

    @classmethod
    def Create(self):
        try:
           chainId = Configure.getChainId()
        except:
           raise Exception("Cannot locate genesis.json file")

        DefaultKeystore = os.path.join(Configure.myConfig.CONFIGPATH, "KeyFile")

        Result = input("Use Generic Defaults? [Y] : ")
        if not Result:
           Result = 'Y'
        else:
           Result = Result.upper()
   
        if Result.upper() == "N":

           GethData = Configure.myConfig.GETHDATA
           if GethData is None:
               GethData = Configure.myConfig.getFilePath("GethData")

           KeyStore = Configure.myConfig.KEYSTORE 
           if KeyStore is None:
               KeyStore = DefaultKeystore

           BootNode = Configure.myConfig.BOOTNODE
           if BootNode is None:
               BootNode = "enode://0949976132f8446dfa40023bd0c148d0d7991f67f8b06570f8455194b54effb16d9476046a4f46dd29a33b34a8b1c396e80fcac8e30101160807a22cfc985f86@34.199.143.211:60303"  
           Configure.Account = Configure.myConfig.ACCOUNT
           Configure.AccountPwd = Configure.myConfig.ACCOUNTPWD
         
        else:
           try:
               BootNode = Configure.myConfig.BOOTNODE
           except:
               BootNode = "enode://0949976132f8446dfa40023bd0c148d0d7991f67f8b06570f8455194b54effb16d9476046a4f46dd29a33b34a8b1c396e80fcac8e30101160807a22cfc985f86@34.199.143.211:60303"  
           KeyStore = DefaultKeystore
           GethData = os.path.join(Configure.myConfig.CONFIGPATH,"GethData")
           Configure.AccountPwd = None
           Configure.Account = None
  
        # BootNode
        Result = input("BootNode [" + BootNode + "]: ")
        if Result:
           BootNode = Result
  
        # GethData Dir
        Result = input("GethData Dir [" + GethData + "]: ")
        if Result:
           GethData = Result

        # Keystore Dir
        while True:
           Result = input("Keystore Dir [" + KeyStore + "]: ")
           if Result:
              KeyStore = Result
           if os.path.isdir(KeyStore) == True:
              break;
           Result = input("Directory does not exist, create it (Y)es, (N)o, (E)xit ? : [Y] ")
           if not Result:
              Result = "Y"
           if Result.upper() == "E":
              return
           if Result.upper() == "Y":
              try:
                 os.mkdir(KeyStore)
                 break
              except:
                 print("Error creating directory")
           
        # Create Account?
        Configure.getAccount(KeyStore)
 
        # 
        # We need to prep the config with the needed assets 
        #
        Configure.copyAssets()
              
        filePath = os.path.join(Configure.myConfig.CONFIGPATH,"Config.json")
        ConfigFile = open(filePath, 'w')
        ConfigFile.writelines("{")
        ConfigFile.writelines('"GETHDATA":"' + GethData.replace("\\", "\\\\") + '",\n')
        ConfigFile.writelines('"BOOTNODE":"' + BootNode + '",\n')
        ConfigFile.writelines('"KEYSTORE":"' + KeyStore.replace("\\", "\\\\") + '",\n')
        ConfigFile.writelines('"NETWORK":"' + str(chainId) + '",\n')

        # Account Name
        ConfigFile.writelines('"ACCOUNT":"' + Configure.Account + '",\n')
    
        objPswd = Configure.encode("VmxSanDiego", Configure.AccountPwd)
        ConfigFile.writelines('"ACCOUNTPWD":"' + objPswd + '"\n')

        ConfigFile.writelines("}\n")
        ConfigFile.close()

        if Configure.noSavePath:
           return
        #
        #  Create the cookie for where this config.json lives
        #  so we can run tools on the chain without being tied
        #  to starting in the directory
        #
        try:
           homePath = os.path.join(os.environ["HOME"], ".veriteem")
        except:
           return

        if os.path.isdir(homePath) == False:
           try:
              os.mkdir(homePath)
           except Exception as ex:
              print (ex)              
 

        try:
           cookieFile = open(homePath + "/config", "w")
        except:
           return

        cookieFile.writelines(Configure.myConfig.CONFIGPATH);
        cookieFile.close()

    @classmethod
    def copyAssets(self):
        configPath = Configure.myConfig.CONFIGPATH
        if not os.path.isdir(configPath):
           try:
              os.mkdir(configPath)
           except:
              errMsg = "Unable to create " + configPath 
              raise Exception(errMsg)

        fileList = ["genesis.json","Config.json"]

        for asset in fileList:
            path = os.path.join(configPath,asset)
            if path == None:
               continue
            if not os.path.isfile(path):
               path = Configure.myConfig.getFilePath(asset)
               print("Asset=" + asset)
               print("Path=" + path)
               print("ConfigPath=" + configPath)
               shutil.copy(path, configPath)

    @classmethod
    def encode(self, key, clear):
        enc = []
        for i in range(len(clear)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc).encode()).decode()
   

    @classmethod
    def getSystem(self):

        try:
            System = Configure.System
            if System == "Permissioned":
               System = "1"
            if System == "Open":
               System = "2"
            if System == "Quorum":
               System = "1"
        except:
            System = '1'

        Result = input("Select System 1=Compliance Ledger (Permissioned) 2=Compliance Ledger (Open) 3=Quorum  (" + System + ") :")
        if not Result:
           Result = System 
 
        if Result == '1':
           return 'Permissioned'
        if Result == '2':
           return 'Open'
        if Result == '3':
           return 'Quorum'
        return 'Open'

    @classmethod
    def getAccount(self, KeyStore):

        firstPass = True
        while True :
           if firstPass == False:
              Result = input("Do you want to Exit [N] : ")
              if not Result : 
                 Result = "N"
              if Result.upper() == "Y" :
                 Configure.account = None
                 return

           firstPass = False

           if Configure.Account is not None:
              print("Current Configured Account is " + Configure.Account)
              Result = input("Use (C)urrent, (N)ew, or (O)ther Account ? [C] : ")
              if not Result:
                 Result = "C" 
           else:
              Result = input("Use (N)ew, or (O)ther Account ? [N] : ")
              if not Result :
                 Result = "N"
           
           #
           # The user wants to use the account currently configured
           #
           
           if Result.upper() == "C":
              Configure.getPassword()
              if Configure.AccountPwd is not None:
                 return
              continue

           #
           # The user wants to create a new account
           #
           if Result.upper() == "N":
              Configure.createAccount(KeyStore)
              if Configure.Account is None:
                 continue
              return
                  
           #
           # The user wants to use a provided account 
           #
           if Result.upper() != "O" :
              continue

           Result = input("Enter Account Number : ")
           if not Result :
              continue

           Configure.getPassword()
           if Configure.AccountPwd is not None:
              Configure.Account = Result
              return

        
    @classmethod
    def createAccount(self, KeyStore):

        Configure.getPassword()
        if Configure.AccountPwd is None:
           print("No password entered " + Configure.AccountPwd)
           return None

        if (os.path.exists(KeyStore) == False): 
           try:
              os.mkdir(KeyStore)
           except:
              print("KeyStore directory does not exist ->" + KeyStore)
              return
   
        chainExe = Configure.myConfig.getChainExe()
        
        passFile = os.path.join(Configure.myConfig.CONFIGPATH, "Password.txt")
        logAcct  = os.path.join(Configure.myConfig.CONFIGPATH, "account.txt") 
        logErr   = os.path.join(Configure.myConfig.CONFIGPATH, "accterr.txt")

        Cmd = chainExe + ' account new --password ' + passFile +  ' --keystore ' + KeyStore + ' >' + logAcct + ' 2>' + logErr
        print (Cmd)
        try:
            os.system(Cmd)
        except:
            print ("Error launching geth account creation")
            return

        AcctFile = open(logAcct, "r")
        AccountInfo = AcctFile.read()
    
        for idx in range(0, len(AccountInfo)):
            if AccountInfo[idx] == '{':
               startIdx = idx + 1
            if AccountInfo[idx] == '}':
               endIdx = idx

        Configure.Account = "0x" + AccountInfo[startIdx:endIdx]
        print("Account = " + Configure.Account)

        os.remove(passFile)

    @classmethod
    def getPassword(self):

        print("Collecting password")
        done = False
        while done == False:
 
          AccountPwd = getpass.getpass(prompt="Enter Account Password : ")
          if not AccountPwd:
             print("Must enter password")
             Response = input("Do you want to quit? [N] ")
             if not Response :
                Response = "N"
             if Response.upper() == "Y":
                return None
             continue

          Confirm = getpass.getpass("Confirm Account Password  : ")
          if not Confirm:
             print("Must enter password")
             continue
          if AccountPwd == Confirm:
             done = True
          else:
             print("Entered passwords do not match ")

        passFile = os.path.join(Configure.myConfig.CONFIGPATH,"Password.txt")
        PasswordFile = open(passFile, "w")
        PasswordFile.writelines(AccountPwd + "\n")
        PasswordFile.close()

        Configure.AccountPwd = AccountPwd
