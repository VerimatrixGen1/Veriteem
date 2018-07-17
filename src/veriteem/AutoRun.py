import socket
import sys
import json
import os
import argparse

from .Config import Config

          

def Run():
      
          parser = argparse.ArgumentParser()
          parser.add_argument("--ifile", help="Test Mode")
          parser.add_argument("--ofile", help="Test Mode")
          parser.add_argument("--icontract", help="Test Mode")
          parser.add_argument("--ocontract", help="Test Mode")
          parser.add_argument("--path", help="path to blockchain config ")
          args = parser.parse_args()

          path = None
          if args.path :
             path = args.path

          myConfig = Config(path)
          myConfig.LoadConfig()

          gethExe = myConfig.getChainExe()

          if args.ifile:
    
             # Remove output results
             OutFileCopy = "rm " + args.ofile;
             os.system (OutFileCopy);
    
             # Remove Autorun.js    
             os.system ("rm AutoRun.js")
    
             #Copy new AutoRun
             TestFileCopy = "cp " + args.ifile + " AutoRun.js"
             os.system (TestFileCopy);
    
             # Remove Output.txt file
             os.system("rm Output.txt")
    
             #Run Script
             Cmd = gethExe + " --exec 'loadScript(" + '"' + "AutoRun.js" + '"' + ")' attach ipc:" + myConfig.GETHDATA + "/geth.ipc "
             Cmd = Cmd +  "--datadir " +  myConfig.GETHDATA + "  >> Output.txt"
        
             print(Cmd)
             os.system(Cmd)
    
             # Save output file
             OutFileCopy = "cp Output.txt " + args.ofile;
             os.system (OutFileCopy);

          if args.icontract:
             print ("ContractFile")
             TestFileCopy = "cp " + args.icontract + " AutoRun.js"
             print (TestFileCopy)
             os.system ("rm AutoRun.js")
             os.system (TestFileCopy);
    
             os.system("rm Output.txt")
        
             Cmd = gethExe + " --exec 'loadScript(" + '"' + "AutoRun.js" + '"' + ")' attach ipc:" + myConfig.GETHDATA + "/geth.ipc "
             Cmd = Cmd +  "--datadir " +  myConfig.GETHDATA + "  >> Output.txt"

             print(Cmd)

             os.system(Cmd)
    
             file = open("Output.txt","r")
             Data = file.readline()
             file.close()
             ParsedData = json.loads(Data)
             if ParsedData["Status"] == "Success":
                print (ParsedData["Address"])
    
                File = open(args.ocontract,"w")
                File.write ("var "+args.ocontract[:args.ocontract.find('.')]+ " = '"+ParsedData["Address"]+"'")
                File.close()
             else :
                 print(ParsedData["ErrDesc"])
    
    
