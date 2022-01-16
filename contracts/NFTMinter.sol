// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract AIHumanNFT is ERC721URIStorage {
    uint256 public tokenCounter;

    constructor (string memory name, string memory symbol) public ERC721 (name, symbol){
        tokenCounter = 0;
    }

    function retrieve() public view returns (uint256){
        return tokenCounter;
        }

    function createHuman(string memory tokenURI) public returns (uint256) {
        uint256 newTokenId = tokenCounter;
        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        tokenCounter = tokenCounter + 1;
        return newTokenId;
    }
}
