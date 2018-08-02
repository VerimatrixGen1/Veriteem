#!/bin/bash
source /etc/environment
PX=`echo $PATH | grep go-1.9`
echo $PX
if [ -z $PX ]
then
   export PATH=$PATH:/usr/lib/go-1.9/bin
fi

#
#  Download the go language, needed by ethereum-go
#
sudo add-apt-repository -y ppa:gophers/archive
sudo apt-get update
sudo apt-get install -q golang-1.9-go
#
#  Download the ethereum go package
#
git clone https://github.com/ethereum/go-ethereum.git
cd go-ethereum
git reset --hard d9575e92fc6e52ba18267410fcd2426d5a148cbc
cd ..
cp ../assets/evm.go go-ethereum/core/vm/evm.go
cp ../assets/errors.go go-ethereum/core/vm/errors.go
version=`ls ../.. | grep veriteem- | cut -d "-" -f2 | cut -d '.' -f1-3`
echo $version >../VERSION
sed -i "/pingPacket = iota + 1/c\        pingPacket = iota + 32 " go-ethereum/p2p/discover/udp.go 
sed -i "/VersionMeta  =/c\     VersionMeta = \"veriteem-$version\"" go-ethereum/params/version.go 
chmod 555 bin
cd go-ethereum
make all
cd ..
cp go-ethereum/build/bin/geth veriteem
chmod +x veriteem
#rm -rf go-ethereum

