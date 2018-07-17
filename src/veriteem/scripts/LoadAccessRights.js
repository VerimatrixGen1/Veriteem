loadScript("Password.js")
loadScript("Alias.js")
loadScript("AccessRightsAddress.js")
loadScript("AccessRights.js")
var AccessRightsContract = web3.eth.contract(JSON.parse(AccessRightsOutput.contracts["AccessRights.sol:AccessRights"].abi));
var AccessRights = eth.contract(AccessRightsContract.abi).at(AccessRightsAddress);


