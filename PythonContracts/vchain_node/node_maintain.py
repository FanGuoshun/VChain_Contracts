# coding=utf-8
from multiprocessing import Process
from json import dumps, loads

import petlib
import time
import unittest
import requests
from PythonContracts.contract import transaction_to_solution
from node_maintain_checker import contract as node_maintain_contract
from PythonContracts import bank_authenticated
# crypto
from PythonContracts.utils import setup, key_gen, pack
from generate_vchain_account import *


def maintain(node_account, node_priv):
    checker_service_process = Process(target=node_maintain_contract.run_checker_service)
    checker_service_process.start()
    time.sleep(0.1)

    transaction_dict = bank_authenticated.auth_transfer(
        [node_account, vchain_account],
        None,
        [dumps(0.01)],
        pack(node_priv)
    )

    update_node_account = loads(transaction_dict['transaction']['outputs'][0])
    fo = open("balance.txt", "w+")
    fo.write(str(update_node_account['balance']))

    response = requests.post(
        'http://127.0.0.1:5000/' + node_maintain_contract.contract_name + '/auth_transfer',
        json=transaction_to_solution(transaction_dict)
    )

    flag = response.json()['success']
    if flag is True:
        print "通过验证！"
    else:
        print "验证失败！"

    checker_service_process.terminate()
    checker_service_process.join()


if __name__ == '__main__':
    # A new account is created, but the balance, public key and private key remains the same.
    fo = open("pub_priv.txt", "r+")
    [_, node_priv_str] = fo.readlines()
    fo.close()
    node_priv_str = node_priv_str.strip()
    node_priv = petlib.bn.Bn.from_decimal(node_priv_str)
    pack(node_priv)
    (_, g, _, _) = setup()
    node_pub = node_priv * g
    fo = open("balance.txt", "r+")
    balance = float(fo.readline().strip())
    fo.close()

    init_transaction = bank_authenticated.init()['transaction']
    token = init_transaction['outputs'][0]

    create_node_account_transaction = bank_authenticated.create_account(
        (token,),
        None,
        [dumps(balance)],
        pack(node_pub)
    )['transaction']

    node_account = create_node_account_transaction['outputs'][1]
    maintain(node_account, node_priv)
