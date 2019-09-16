# coding=utf-8

from multiprocessing import Process
from json import dumps, loads
import time
import unittest
import requests
# chainspace
from PythonContracts.contract import transaction_to_solution
from PythonContracts.bank_authenticated import contract as bank_authenticated_contract
from PythonContracts import bank_authenticated
# crypto
from PythonContracts.utils import setup, key_gen, pack

def init(vchain_pub):
    init_transaction = bank_authenticated.init()['transaction']
    token = init_transaction['outputs'][0]

    create_vchain_account_transaction = bank_authenticated.create_account(
        (token,),
        None,
        [dumps(10)],
        pack(vchain_pub)
    )['transaction']
    vchain_account = create_vchain_account_transaction['outputs'][1]
    return vchain_account

vchain_account = init(0)
