// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SupplyChainNFT is ERC721URIStorage, Ownable {
    uint256 public nextTokenId;

    // Mappa: tokenId => lista di indirizzi che hanno posseduto il prodotto
    mapping(uint256 => address[]) private ownershipHistory;

    constructor() ERC721("SupplyChainNFT", "SCNFT") {}

    function mintProductNFT(address to, string memory tokenURI) public onlyOwner {
        uint256 tokenId = nextTokenId;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);

        // Inizializza lo storico con il primo proprietario
        ownershipHistory[tokenId].push(to);

        nextTokenId++;
    }

    function transferProductNFT(address from, address to, uint256 tokenId) public {
        require(_isApprovedOrOwner(msg.sender, tokenId), "Not authorized to transfer");

        _transfer(from, to, tokenId);

        // Aggiorna lo storico dei passaggi
        ownershipHistory[tokenId].push(to);
    }

    // Funzione per ottenere la lista dei proprietari storici
    function getOwnershipHistory(uint256 tokenId) public view returns (address[] memory) {
        return ownershipHistory[tokenId];
    }
}