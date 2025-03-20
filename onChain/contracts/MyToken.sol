// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    uint256 public constant MINT_LIMIT = 1000 * 10**18; // Limite massimo per ogni mint

    constructor(uint256 initialSupply, address initialOwner) ERC20("MyToken", "MTK") Ownable(initialOwner) {
        require(initialSupply <= MINT_LIMIT, "Initial supply exceeds mint limit");
        _mint(initialOwner, initialSupply); // Usa initialOwner per il mint iniziale
    }

    function balanceOf(address account) public view override returns (uint256) {
        uint256 balance = super.balanceOf(account);  // Richiamando la funzione della superclasse ERC20
        return balance;
    }

    function mint(address to, int256 amount) external onlyOwner {
        require(amount != 0, "Amount cannot be zero");

        if (amount > 0) {
            require(uint256(amount) <= MINT_LIMIT, "Mint limit exceeded");
            _mint(to, uint256(amount));
        } else {
            uint256 absAmount = uint256(-amount);
            require(balanceOf(to) >= absAmount, "Insufficient tokens to burn");
            _burn(to, absAmount);
        }
    }
}