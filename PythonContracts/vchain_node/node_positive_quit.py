# coding=utf-8

import ast
from multiprocessing import Process
from json import dumps, loads

import petlib
import time
import unittest
import requests
# chainspace
from PythonContracts.contract import transaction_to_solution
from PythonContracts.bank_authenticated import contract as bank_authenticated_contract
from node_positive_quit_checker import contract as quit_authenticated_contract
from PythonContracts import bank_authenticated
# crypto
from PythonContracts.utils import setup, key_gen, pack
from generate_vchain_account import *
import ast


def positive_quit(node_account, node_priv):
    checker_service_process = Process(target=quit_authenticated_contract.run_checker_service)
    checker_service_process.start()
    time.sleep(0.1)

    transaction_dict = bank_authenticated.auth_transfer(
        [node_account, vchain_account],
        None,
        [dumps(0)],
        pack(node_priv)
    )

    response = requests.post(
        'http://127.0.0.1:5000/' + quit_authenticated_contract.contract_name + '/auth_transfer',
        json=transaction_to_solution(transaction_dict)
    )

    flag = response.json()['success']
    if flag is True:
        print "通过验证！"
        # update balance.txt
        update_node_account = loads(transaction_dict['transaction']['outputs'][0])
        fo = open("balance.txt", "w+")
        fo.write(str(update_node_account['balance'] + 3))
    else:
        print "验证失败！"

    checker_service_process.terminate()
    checker_service_process.join()


if __name__ == '__main__':
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
    positive_quit(node_account, node_priv)
