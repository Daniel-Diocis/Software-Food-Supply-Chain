// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor(uint256 initialSupply, address initialOwner) ERC20("MyToken", "MTK") Ownable(initialOwner) {
        require(initialSupply > 0, "Initial supply must be greater than 0");
        require(initialOwner != address(0), "Owner address cannot be the zero address");

        _mint(msg.sender, initialSupply); // Minta i token all'indirizzo che deploya il contratto
        transferOwnership(initialOwner); // Imposta il proprietario iniziale
    }
}