import traceback
import sys
import os
import json
import base64

class Config():

    INSTALLPATH = None
    CONFIGPATH  = None

    def __init__(self, path):
        Config.INSTALLPATH = self.find_module_path("veriteem")
        Config.CONFIGPATH  = self.getConfigPath(path)
        
        
    @classmethod
    def LoadConfig(self):
        if Config.CONFIGPATH is None:
           raise Exception("Must specify directory in which to store app data to proceed")

        #
        #  If a Config.json file exists, pull it in for default settings
        #
        filePath = self.getFilePath("Config.json")
        print("ConfigFile = " + filePath)
        try:
            ConfigFile = open(filePath)
            ConfigStr  = ConfigFile.read()
            ConfigData = json.loads(ConfigStr)
            ConfigFile.close()
        except Exception:
            print("Failed to read config file")
            ConfigData = []
            
        try:
            Config.SITEID = ConfigData["SITEID"]
        except:
            Config.SITEID = "NONAME"
   
        try:
            Config.GETHDATA = ConfigData["GETHDATA"]
        except:
            Config.GETHDATA = os.path.join(Config.CONFIGPATH , "GethData")

        try:
            Config.BOOTNODE = ConfigData["BOOTNODE"]
        except:
            Config.BOOTNODE = None

        try:
            Config.KEYSTORE = ConfigData["KEYSTORE"]
        except:
            Config.KEYSTORE = None
   
        try:
            Config.NETWORK = ConfigData["NETWORK"]
        except:
            Config.NETWORK = None
      
        try:
            pwd = ConfigData["ACCOUNTPWD"]
            Config.ACCOUNTPWD = self.decode("VmxSanDiego", pwd)
        except:
            Config.ACCOUNTPWD = None

        try:
            Config.ACCOUNT = ConfigData["ACCOUNT"]
        except:
            Config.ACCOUNT = None


    @classmethod
    def getFilePath(self, fileName):
        filePath = os.path.join(Config.CONFIGPATH, fileName)
        if os.path.isfile(filePath) :
           return filePath

        filePath = os.path.join(Config.INSTALLPATH, "assets", fileName)
        if os.path.isfile(filePath) :
           return filePath
        return None

    @classmethod
    def find_module_path(self, packageName):
        for path in sys.path:
            if path != os.getcwd() :
               if os.path.isdir(path) and packageName in os.listdir(path):
                  return os.path.join(path, packageName)


    @classmethod
    def getCookiePath(self):
        try:
           homeDir = os.environ["HOME"]
        except:
           print("HOME environment variable not set")
           return None

        homeDir = homeDir + "/.veriteem"
        if os.path.isdir(homeDir) == False:
           print(homeDir + " does not exist")
           return None

        try:
           configFile = os.path.join(homeDir, "config")
           cookieFile = open(configFile, "r")
           path = cookieFile.read()
           cookieFile.close()
        except:
           print("Error reading " + homeDir)
           path = None

        return path

    @classmethod
    def getConfigPath(self,path):
        #
        #  See if we have the cookie that holds the location of the
        #  app data
        #
        if path is None:
           path = self.getCookiePath()
        #
        #  If a Config.json file exists, pull it in for default settings
        #
    
        if path is None:
           cwd = os.getcwd()
           path = input("What directory should Veriteem reside in? [" + cwd + "] : ")
           if not path:
              path = cwd

        if os.path.isdir(path)  == False :
           response = input(path + " Does not exist. Create it? [Y] : ")
           if not response:
              response = "Y"
           if response.upper() == "N" : 
              raise Exception("Need valid directory to store app data in") 
           os.mkdir(path)
           
        return path

    @classmethod
    def getChainExe(self):
        path = os.path.join(Config.INSTALLPATH, "bin/veriteem")
        return path 

    @classmethod
    def decode(self, key, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc).decode()
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)

    @classmethod
    def getPackageFile(self, packageName, subDirectory, fileName):
        packagePath = Config.find_module_path(packageName) 
        if packagePath == None :
           return None
        if subDirectory == None :
           path = os.path.join(packagePath,fileName)
        else :
           path = os.path.join(packagePath,subDirectory,fileName)
        return path
