# coding=utf-8
###################################################################
""" test vchain contracts, created by aaron 2019.9.16 """
# general
from multiprocessing import Process
from json import dumps, loads
import time
import unittest
import requests
# chainspace
from PythonContracts.contract import transaction_to_solution

from PythonContracts.vchain_node import vchain_system
from PythonContracts.vchain_node.vchain_system import contract as vchain_system_contract
# crypto
from PythonContracts.utils import setup, key_gen, pack
from PythonContracts.vchain_node.generate_vchain_account import *
import petlib


class TestBankAuthenticated(unittest.TestCase):

    def test_init(self):
        ##
        ## run service
        ##
        checker_service_process = Process(target=vchain_system_contract.run_checker_service)
        checker_service_process.start()
        time.sleep(0.1)

        ##
        ## create transaction
        ##
        transaction_dict = vchain_system.init()

        ##
        ## submit transaction
        ##
        response = requests.post(
            'http://127.0.0.1:5000/' + vchain_system_contract.contract_name + '/init',
            json=transaction_to_solution(transaction_dict)
        )
        self.assertTrue(response.json()['success'])

        ##
        ## stop service
        ##
        checker_service_process.terminate()
        checker_service_process.join()

    def test_create_account(self):
        ##
        ## run service
        ##
        checker_service_process = Process(target=vchain_system_contract.run_checker_service)
        checker_service_process.start()
        time.sleep(0.1)

        ##
        ## create transaction
        ##
        (priv, pub) = key_gen(setup())
        with open("pub_priv.txt", "w+") as f:
            f.write(str(pub) + "\n" + str(priv) + "\n")
        f.close()

        # init
        init_transaction = vchain_system.init()['transaction']
        token = init_transaction['outputs'][0]

        # create bank account
        transaction_dict = vchain_system.create_account(
            (token,),
            None,
            [dumps(100)],
            pack(pub)
        )

        ##
        ## submit transaction
        ##
        response = requests.post(
            'http://127.0.0.1:5000/' + vchain_system_contract.contract_name + '/create_account',
            json=transaction_to_solution(transaction_dict)
        )
        self.assertTrue(response.json()['success'])

        ##
        ## stop service
        ##
        checker_service_process.terminate()
        checker_service_process.join()

    def test_join(self):
        checker_service_process = Process(target=vchain_system_contract.run_checker_service)
        checker_service_process.start()
        time.sleep(0.1)

        with open("pub_priv.txt", "r+") as f:
            [_, node_priv_str] = f.readlines()
        f.close()

        node_priv_str = node_priv_str.strip()
        node_priv = petlib.bn.Bn.from_decimal(node_priv_str)
        (_, g, _, _) = setup()
        node_pub = node_priv * g
        with open("balance.txt", "r+") as f:
            balance = int(f.readline().strip())
        f.close()

        init_transaction = vchain_system.init()['transaction']
        token = init_transaction['outputs'][0]

        create_node_account_transaction = vchain_system.create_account(
            (token,),
            None,
            [dumps(balance)],
            pack(node_pub)
        )['transaction']

        node_account = create_node_account_transaction['outputs'][1]
        # pack transaction
        transaction_dict = vchain_system.join(
            [node_account, vchain_account],
            None,
            None,
            pack(node_priv)
        )

        ##
        ## submit transaction
        ##
        response = requests.post(
            'http://127.0.0.1:5000/' + vchain_system_contract.contract_name + '/join',
            json=transaction_to_solution(transaction_dict)
        )
        self.assertTrue(response.json()['success'])

        ##
        ## stop service
        ##
        checker_service_process.terminate()
        checker_service_process.join()

    def test_maintain(self):
        checker_service_process = Process(target=vchain_system_contract.run_checker_service)
        checker_service_process.start()
        time.sleep(0.1)

        with open("pub_priv.txt", "r+") as f:
            [_, node_priv_str] = f.readlines()
        f.close()

        node_priv_str = node_priv_str.strip()
        node_priv = petlib.bn.Bn.from_decimal(node_priv_str)
        (_, g, _, _) = setup()
        node_pub = node_priv * g
        with open("balance.txt", "r+") as f:
            balance = int(f.readline().strip())
        f.close()

        init_transaction = vchain_system.init()['transaction']
        token = init_transaction['outputs'][0]

        create_node_account_transaction = vchain_system.create_account(
            (token,),
            None,
            [dumps(balance)],
            pack(node_pub)
        )['transaction']

        node_account = create_node_account_transaction['outputs'][1]
        # pack transaction
        transaction_dict = vchain_system.maintain(
            [node_account, vchain_account],
            None,
            None,
            pack(node_priv)
        )

        ##
        ## submit transaction
        ##
        response = requests.post(
            'http://127.0.0.1:5000/' + vchain_system_contract.contract_name + '/maintain',
            json=transaction_to_solution(transaction_dict)
        )
        self.assertTrue(response.json()['success'])

        ##
        ## stop service
        ##
        checker_service_process.terminate()
        checker_service_process.join()

    def test_active_quit(self):
        checker_service_process = Process(target=vchain_system_contract.run_checker_service)
        checker_service_process.start()
        time.sleep(0.1)

        with open("pub_priv.txt", "r+") as f:
            [_, node_priv_str] = f.readlines()
        f.close()

        node_priv_str = node_priv_str.strip()
        node_priv = petlib.bn.Bn.from_decimal(node_priv_str)
        (_, g, _, _) = setup()
        node_pub = node_priv * g

        with open("balance.txt", "r+") as f:
            balance = int(f.readline().strip())
        f.close()

        init_transaction = vchain_system.init()['transaction']
        token = init_transaction['outputs'][0]

        create_node_account_transaction = vchain_system.create_account(
            (token,),
            None,
            [dumps(balance)],
            pack(node_pub)
        )['transaction']

        node_account = create_node_account_transaction['outputs'][1]
        # pack transaction
        transaction_dict = vchain_system.active_quit(
            [node_account, vchain_account],
            None,
            None,
            pack(node_priv)
        )

        ##
        ## submit transaction
        ##
        response = requests.post(
            'http://127.0.0.1:5000/' + vchain_system_contract.contract_name + '/active_quit',
            json=transaction_to_solution(transaction_dict)
        )
        self.assertTrue(response.json()['success'])

        ##
        ## stop service
        ##
        checker_service_process.terminate()
        checker_service_process.join()
