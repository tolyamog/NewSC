import os
import argparse


def withdraw(address: str, wallet: str):
    return """
import {Contract, Wallet} from "zksync-web3";
import { HardhatRuntimeEnvironment } from "hardhat/types";
import { Deployer } from "@matterlabs/hardhat-zksync-deploy";
export default async function (hre: HardhatRuntimeEnvironment) {
  // The address of the counter smart contract
  const ADDRESS = "%s";
  // The ABI of the counter smart contract
  const ABI = require("../abi/IO.json");

  const wallet = new Wallet("%s");

  // Create deployer object and load the artifact of the contract we want to deploy.
  const deployer = new Deployer(hre, wallet);
  const contract = new Contract(ADDRESS, ABI, deployer.zkWallet);

  console.log(`The contract is ${await contract.address}`);
  await contract.withDrawAll()
}
    """ % (address, wallet)


def create_deploy(contractAddress: str, wallet: str) -> None:
    if "deploy" not in os.listdir():
        os.mkdir("deploy")
    with open(f"deploy/deploy.ts", "w") as file:
        file.writelines(withdraw(contractAddress, wallet))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-wallet", dest="wallet", required=True)
    parser.add_argument("-contractAddress", dest="contractAddress", required=True)

    args = parser.parse_args()
    create_deploy(args.contractAddress, args.wallet)
