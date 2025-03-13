const MyToken = artifacts.require("MyToken");

contract("MyToken", (accounts) => {
  let token;
  const initialSupply = web3.utils.toWei("1000", "ether");
  const initialOwner = accounts[1];

  beforeEach(async () => {
    token = await MyToken.new(initialSupply, initialOwner);
  });

  it("should mint the correct initial supply", async () => {
    const balance = await token.balanceOf(accounts[0]);
    assert.equal(balance.toString(), initialSupply.toString(), "Initial supply is not correct");
  });

  it("should set the correct initial owner", async () => {
    const owner = await token.owner();
    assert.equal(owner, initialOwner, "Owner is not set correctly");
  });

  it("should transfer ownership correctly", async () => {
    const newOwner = accounts[2];
    await token.transferOwnership(newOwner);
    const owner = await token.owner();
    assert.equal(owner, newOwner, "Ownership was not transferred correctly");
  });
});