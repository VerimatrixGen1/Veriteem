#!/usr/bin/python3
import traceback
import sys
import os
import argparse
import veriteem as vmx


def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--path",    help="configuration path")
    parser.add_argument("-t","--tools",   help="access Veriteem javascript tools ", action="store_true")
    parser.add_argument("-z","--zigbee",  help="access Veriteem ZigBee tools ", action="store_true")


    path    = None

    args     = parser.parse_args()
    if args.path != None:
       path = args.path


    try:
       myConfig = vmx.Config(path)
       myConfig.LoadConfig()
    except:
       raise Exception("Site Configuration Not Specified")

    if args.tools == True:
       try:
           scriptPath = os.path.join(myConfig.INSTALLPATH, "scripts")
           os.chdir(scriptPath)
       except:
           ErrMsg = "Cannot locate tools in " + scriptPath
           raise Exception(ErrMsg)
           
    if args.zigbee == True:
       try:
           ledgerPath = myConfig.find_module_path("veriteemcomplianceledger")
           scriptPath = os.path.join(ledgerPath, "scripts")
           os.chdir(scriptPath)
       except:
           ErrMsg = "Cannot locate tools in " + scriptPath
           raise Exception(ErrMsg)
           
    gethExe = myConfig.getChainExe()
    Cmd = gethExe + " attach ipc:" + myConfig.GETHDATA + "/geth.ipc --datadir " + myConfig.GETHDATA
    os.system(Cmd)
  
if __name__ == "__main__":
  main(sys.argv)
