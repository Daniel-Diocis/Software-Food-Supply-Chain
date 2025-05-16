// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    uint256 public constant MINT_LIMIT = 1000 * 10**18;

    constructor(uint256 initialSupply, address initialOwner) ERC20("MyToken", "MTK") {
        require(initialSupply <= MINT_LIMIT, "Initial supply exceeds mint limit");
        _mint(initialOwner, initialSupply);
        transferOwnership(initialOwner); // Imposta il proprietario del contratto
    }

    function decimals() public view virtual override returns (uint8) {
        return 2; // ad esempio: 2 decimali → 1.23 token è rappresentato come 123
    }

    /// @notice Permette al proprietario di mintare o burnare token
    /// @param to l'indirizzo destinatario
    /// @param amount quantità da mintare (> 0) o burnare (< 0)
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

    /// @notice Permette a chiunque di bruciare i propri token
    /// @param amount quantità di token da bruciare
    function burn(uint256 amount) external {
        require(balanceOf(msg.sender) >= amount, "Not enough tokens");
        _burn(msg.sender, amount);
    }

    /// @notice Versione esplicita di balanceOf (non strettamente necessaria)
    function balanceOf(address account) public view override returns (uint256) {
        return super.balanceOf(account);
    }
}