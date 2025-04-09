const MyToken = artifacts.require("MyToken");

module.exports = async function (deployer, network, accounts) {
  const initialSupply = web3.utils.toWei("1000", "ether"); // 1000 token con 18 decimali
  const initialOwner = accounts[0];

  await deployer.deploy(MyToken, initialSupply, initialOwner);

  // opzionale: log
  const instance = await MyToken.deployed();
  console.log(`✔️ MyToken deployed at ${instance.address}`);
};