const MyToken = artifacts.require("MyToken");

module.exports = function (deployer, network, accounts) {
    const initialSupply = web3.utils.toWei("1000", "ether"); // Inizializzazione con 1000 token
    const initialOwner = accounts[0]; // Il primo account di Ganache come proprietario iniziale
    deployer.deploy(MyToken, initialSupply, initialOwner);
};