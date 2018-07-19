#! python
import traceback
import sys
import os
import argparse
import veriteem as vmx


def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config", help="configure parameters",  action="store_true")
    parser.add_argument("-i","--init",   help="initialize blockchain", action="store_true")
    parser.add_argument("-r","--run",    help="start the veriteem service ", action="store_true")
    parser.add_argument("-m","--miner",  help="start the veriteem mining service ", action="store_true")
    parser.add_argument("-s","--stop",   help="stop the chain miner",  action="store_true")
    parser.add_argument("-a","--access", help="add account to access control", action="store_true")
    parser.add_argument("-t","--total",  help="configure, init, and start the chain miner", action="store_true")
    parser.add_argument("-p","--path",   help="configuration path")
    parser.add_argument("-n","--nosave", help="do not save path", action="store_true")

    path    = None

    args     = parser.parse_args()

    #
    #  Check on the installation to see if we need to install assets/programs
    #
    myInstall = vmx.VeriteemInstall()
    myInstall.CheckInstallation()

    # if no arguments were provided, default to --total
    if len(argv) == 1 :
       args.total = True

    if args.path != None:
       path     = args.path

    # if the user wants to run all items or the config option
    if (args.config == True) or (args.total == True) :
       try:
          myConfig = vmx.Configure(path, args.nosave )
       except Exception as ex:
          # print(traceback.format_exc())
          print(ex)
          return
       myConfig.Create()

    # if the user wants to run all items or create the blockchain
    if (args.init == True) or (args.total == True) :
       try:
          myInit = vmx.InitGeth(path)
       except:
          print(traceback.format_exc())
          return
       myInit.CreateBlockChain()

    # if the user wants to run all items or start the veriteem service
    if (args.run == True) or (args.total == True) :
       try:
          myVeriteem = vmx.StartVeriteem(path)
       except:
          print(traceback.format_exc())
          return
       myVeriteem.Start()

    # if the user wants to start the miner
    if (args.miner == True)  :
       try:
          myMiner = vmx.StartMiner(path)
       except:
          print(traceback.format_exc())
          return
       myMiner.Start()

    if (args.access == True) or (args.total == True) :
       try:
          myAccess = vmx.AccessControl(path)
       except:
          print(traceback.format_exc())
          return
       myAccess.AddAccess()

    if args.total == True :
       readMe = myConfig.myConfig.getPackageFile("veriteem", None, "README.md")
       fd = open(readMe, "r")
       readMeStr = fd.read()
       print(readMeStr)
       
    if args.stop == True :
       Cmd = "killall veriteem"
       os.system(Cmd)
  
if __name__ == "__main__":
  main(sys.argv)
