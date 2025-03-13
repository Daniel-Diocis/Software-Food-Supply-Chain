const MyToken = artifacts.require("MyToken");

module.exports = async function (deployer) {
  const initialSupply = 1000000; // Example - replace with your intended logic
  const accounts = await web3.eth.getAccounts();
  const initialOwner = accounts[0];

  console.log("Deploying MyToken with:");
  console.log("  Initial Supply:", initialSupply);
  console.log("  Initial Owner:", initialOwner);

  await deployer.deploy(MyToken, initialSupply, initialOwner);
};