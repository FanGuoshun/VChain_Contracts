# coding=utf-8

import ast
from multiprocessing import Process
from json import dumps, loads
import time
import unittest
import requests
# chainspace
from PythonContracts.contract import transaction_to_solution
from PythonContracts.bank_authenticated import contract as bank_authenticated_contract
from node_join_checker import contract as init_authenticated_contract
from PythonContracts import bank_authenticated
# crypto
from PythonContracts.utils import setup, key_gen, pack
from generate_vchain_account import *


# 生成一个账户，并向vchain系统缴纳一定数量的保证金
def join():
    checker_service_process = Process(target=init_authenticated_contract.run_checker_service)
    checker_service_process.start()
    time.sleep(0.1)

    params = setup()
    (node_priv, node_pub) = key_gen(params)
    #  Record the public-private key pair locally
    fo = open("pub_priv.txt", "w+")
    fo.write(str(node_pub))
    fo.write("\n")
    fo.write(str(node_priv))
    fo.write("\n")
    fo.close()

    # 生成账户
    init_transaction = bank_authenticated.init()['transaction']
    token = init_transaction['outputs'][0]

    create_node_account_transaction = bank_authenticated.create_account(
        (token,),
        None,
        [dumps(10)],
        pack(node_pub)
    )['transaction']

    node_account = create_node_account_transaction['outputs'][1]
    transaction_dict = bank_authenticated.auth_transfer(
        [node_account, vchain_account],
        None,
        [dumps(3)],
        pack(node_priv)
    )

    # update balance.txt
    update_node_account = loads(transaction_dict['transaction']['outputs'][0])
    fo = open("balance.txt", "w+")
    fo.write(str(update_node_account['balance']))

    response = requests.post(
        'http://127.0.0.1:5000/' + init_authenticated_contract.contract_name + '/auth_transfer',
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
    join()
