const SupplyChainNFT = artifacts.require("SupplyChainNFT");

module.exports = function (deployer) {
  deployer.deploy(SupplyChainNFT);
};