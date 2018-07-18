Table of contents
=================

<!--ts-->
   * [Installation](https://github.com/VerimatrixGen1/Veriteem/wiki#installation)
   * [Overview](https://github.com/VerimatrixGen1/Veriteem/wiki#overview)
   * [Proof of Authority](https://github.com/VerimatrixGen1/Veriteem/wiki/proof-of-authority)
   * [Access Control](https://github.com/VerimatrixGen1/Veriteem/wiki/access-control)
<!--te-->

# Installation
Veriteem Compliance Ledger is an application which runs on top of Veriteem.  Currently, only **Linux Ubuntu 16.04LTS** is supported.  However, the Veriteem is deployed and accessed with Python3, and thus Windows and MacOS may be supported in the near future.  Veriteem is deployed through pip3, and then requires VeriteemConfig.py to be run to build and configure the network.

Installing Veriteem Compliance Ledger is a two step process:
```
pip3 install veriteem
VeriteemConfig.py
```

* Click here for instructions on [installing pip3](https://github.com/VerimatrixGen1/Veriteem/wiki/Detailed-Installation-and-Troubleshooting#installing-pip3)

The Veriteem Compliance Ledger may be accessed through the Veriteem command line interface:
```
Veriteem.py
```

Detailed installation and troubleshooting guides may be found [here](https://github.com/VerimatrixGen1/Veriteem/wiki/Detailed-Installation-and-Troubleshooting)

# Operation
## Command line interface
The Veriteem command line interface can be started with the following command:
```
Veriteem.py
```

## Stopping Node
Veriteem runs in the background, and thus exiting the command line interface will not halt the node's operation.  In order to halt the node, from any location type:
```
VeriteemConfig.py -s
```

## Restart Node
The Veriteem node will automatically start at the end of the installation process.  However, the default installation will not automatically start after a reboot.  From any location, type the following command to restart Veriteem:
```
VeriteemConfig.py -r
```

# Validation
Once a Veriteem node has been installed, the user should perform the following basic checks that their node is connected to the ledger, and is in sync with the network.

## Verify BlockNumber
* Retreive Block Number from [Veriteem Dashboard](http://www.veriteem.complianceblockchain.org/Veriteem/Dashboard)
* Launch Veriteem Compliance Ledger command line interface
```
Veriteem.py
```
* Verify Block Number is equal to the current network block number.
```
eth.blockNumber
```
* Verify there is at least 1 peer
```
admin.peers.length
```

If the block number and peer length does not met the expected values, then the node is not fully connected to the Veriteem Network.  Click here for a [Veriteem Troubleshooting guide](https://github.com/VerimatrixGen1/Veriteem/wiki/Detailed-Installation-and-Troubleshooting)

# Overview
Veriteem is an Ethereum Fork which provides a publicly readable ledger with multiple levels of write access and Proof of Authority consensus.  The ledger is managed by a group of Ledger Guardians, who provide the transaction processing, Proof of Authority consensus, and management of Smart Contracts running on the ledger.  Veriteem also provide contract lifecycle support to help monitor the contracts running on the ledger, along with methods to improve contract upgrades.

[[https://github.com/VerimatrixGen1/Veriteem/blob/master/Wiki/Images/VeriteemFeatures.png]]

The [Veriteem Compliance Ledger](https://github.com/VerimatrixGen1/VeriteemComplianceLedger) is and application running on Veriteem used to provide device information from manufacturers and compliance organizations to network and ecosystem operators.  The information includes compliance status, firmware update links, operating instructions, and expected network behavior.  This information is provided in a machine readable interface for use by onboarding/installer tools, gateways, and backend systems.

[[https://github.com/VerimatrixGen1/Veriteem/blob/master/Wiki/Images/UseCases.png]]


