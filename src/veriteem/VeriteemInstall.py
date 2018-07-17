import sys
import os
import shutil

class VeriteemInstall():

      installPath = None

      def __init__(self):
           
          for path in sys.path:
              if path == os.getcwd() :
                 continue
              if os.path.isdir(path) and "veriteem" in os.listdir(path):
                 break

          VeriteemInstall.installPath = os.path.join(path, "veriteem")

      #
      #  Check whether we need to update the ethereum go installation
      #  and rebuild the veriteem executable
      #
      @classmethod
      def CheckInstallation(self):
          #
          # First check if the <package install>/bin/veriteem executable exists
          #
          exFile = os.path.join(VeriteemInstall.installPath, "bin", "veriteem")
          print("exFile " + exFile)
          if not os.path.isfile(exFile) :
             print("Please wait... need to install assets and programs")
             VeriteemInstall.install()
             return

          #
          # We have a veriteem executable, check its version
          #
          os.chdir(VeriteemInstall.installPath)
  
          fp = open("VERSION", "r")
          version = fp.read()
          fp.close()
          version = version.rstrip()

          for filename in os.listdir(".."):
              if filename.find("veriteem-") != -1 :
                 break

          sidx   = filename.find('-') + 1
          eidx   = filename.find('.dist')   
          if eidx < 0 :
             eidx = filename.find('-py')
          pversion = filename[sidx:eidx]
          print("version " + version)
          print("pversion " + pversion)
          if pversion != version :
             print ("Please wait, need to update package")
             VeriteemInstall.install()
      #
      #  Do the full installation setup
      #  
      @classmethod
      def install(self):
          #
          #  Install go to the standard PATH environment variable
          #
          VeriteemInstall.addGoToPath()
          VeriteemInstall.installEthereum()

      def find_module_path():
          for path in sys.path:
              if path == os.getcwd() :
                 continue
              if os.path.isdir(path) and "veriteem" in os.listdir(path):
                 return os.path.join(path, "veriteem")
          return None
      #
      #  Add Golang to the executable path
      #  
      @classmethod
      def addGoToPath(self):
          try:
             with open("/etc/environment", "r") as envFile:
                  lines = envFile.readlines()
             envFile.close()
          except:
             print("Cannot modify /etc/environment to set PATH for go")
             return

          #
          #  Find the PATH= specification in the environment file
          #
          for idx in range(len(lines)) :
              pathSet = lines[idx].find("PATH=")
              if pathSet >= 0 :
                 break
                    
          #
          #  add /usr/lib/go-1.9/bin to the path if not present
          #
          if pathSet < 0 :
             print("PATH not found /etc/environment ")
             return
             
          goPath = lines[idx].find("go-1.9")
          if goPath >= 0 :
             print("go is defined in PATH ")
             return

          pathStr = lines[idx].rstrip()
          pathStr = pathStr.replace("'", '')
          pathStr = pathStr.replace('"', '')
          
          newPath = pathStr + ":/usr/lib/go-1.9/bin"
          print("PATH: " + newPath)
                 
          try:
             envFile = open("/etc/environment", "w")
          except:
             print("Unable to open /etc/environment to update PATH")
             return

          for jdx in range(len(lines)) :
              if jdx != idx:
                 envFile.write(lines[jdx])
              if jdx == idx:
                 envFile.write(newPath + "\n")
              
          envFile.close()
 
           
      #
      #  Download go-ethereum 
      #  
      @classmethod
      def installEthereum(self):

          try:
              path = os.path.join(VeriteemInstall.installPath, "bin")
              print("installgo is in " + path)
              os.chdir(path)
              os.system("./installgo.sh")
          except:
              print("Unable to install ethereum")
              return

          



