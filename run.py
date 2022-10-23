import os
import argparse

def get_contract(name: str) -> str:
    return """// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;


contract %s {
    address owner;
    mapping (address => uint) public values;

    modifier onlyOwner() {
        require(msg.sender == owner, "Restrict to owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    receive() external payable {
        values[msg.sender] = msg.value;

    }

    function withdraw(address payable receiver, uint256 amount) external onlyOwner {
        if(address(this).balance < amount) {
            receiver.transfer(amount);
        }
    }

    function withDrawAll() public {
        address payable _to = payable(owner);
        _to.transfer(address(this).balance);
    }
}

    """ % name

def get_deploy(name: str, wallet: str) -> str:
    return """
import { utils, Wallet } from "zksync-web3";
import * as ethers from "ethers";
import { HardhatRuntimeEnvironment } from "hardhat/types";
import { Deployer } from "@matterlabs/hardhat-zksync-deploy";
    
// An example of a deploy script that will deploy and call a simple contract.
export default async function (hre: HardhatRuntimeEnvironment) {
  console.log(`Running deploy script for the Greeter contract`);

  // Initialize the wallet.
  const wallet = new Wallet("%s");

  // Create deployer object and load the artifact of the contract we want to deploy.
  const deployer = new Deployer(hre, wallet);
  const artifact = await deployer.loadArtifact("%s");

  // Deposit some funds to L2 in order to be able to perform L2 transactions.
  const depositAmount = ethers.utils.parseEther("0.0015");
  const depositHandle = await deployer.zkWallet.deposit({
    to: deployer.zkWallet.address,
    token: utils.ETH_ADDRESS,
    amount: depositAmount,
  });
  // Wait until the deposit is processed on zkSync
   await depositHandle.wait();

  // Deploy this contract. The returned object will be of a `Contract` type, similarly to ones in `ethers`.
  const pubContract = await deployer.deploy(artifact,  []);

  // Show the contract info.
  const contractAddress = pubContract.address;
  console.log(`${artifact.contractName} was deployed to ${contractAddress}`);
  console.log("Constructor params ABI: ", pubContract.interface.encodeDeploy([]))
  console.table(pubContract.interface.encodeDeploy([]))
}
    """ % (wallet, name)


def create_contract(name: str) -> None:
    if "contracts" not in os.listdir():
        os.mkdir("contracts")
    with open(f"contracts/{name}.sol", "w") as file:
        file.writelines(get_contract(name))


def create_deploy(name: str, wallet: str) -> None:
    if "deploy" not in os.listdir():
        os.mkdir("deploy")
    with open(f"deploy/deploy.ts", "w") as file:
        file.writelines(get_deploy(name, wallet))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-wallet", dest="wallet", required=True)
    parser.add_argument("-name", dest="name", required=True)

    args = parser.parse_args()
    create_contract(args.name)
    create_deploy(args.name, args.wallet)

    print("Good")
