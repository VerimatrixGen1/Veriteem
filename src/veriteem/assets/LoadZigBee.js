loadScript("../ZigBeeDeviceCompliance/ComplianceAddress.js")
loadScript("../ZigBeeDeviceCompliance/Compliance.js")
var ZigBeeContract = web3.eth.contract(JSON.parse(ComplianceOutput.contracts["Compliance.sol:Compliance"].abi));
var ZigBee = eth.contract(ZigBeeContract.abi).at(ComplianceAddress);

loadScript("../ModelInfo/ModelInfoAddress.js")
loadScript("../ModelInfo/ModelInfo.js")
var ModelInfoContract = web3.eth.contract(JSON.parse(ModelInfoOutput.contracts["ModelInfo.sol:ModelInfo"].abi));
var ModelInfo = eth.contract(ModelInfoContract.abi).at(ModelInfoAddress);

loadScript("../DeviceSecurity/DeviceSecurityAddress.js")
loadScript("../DeviceSecurity/DeviceSecurity.js")
var DeviceSecurityContract = web3.eth.contract(JSON.parse(DeviceSecurityOutput.contracts["DeviceSecurity.sol:DeviceSecurity"].abi));
var DeviceSecurity = eth.contract(DeviceSecurityContract.abi).at(DeviceSecurityAddress);

