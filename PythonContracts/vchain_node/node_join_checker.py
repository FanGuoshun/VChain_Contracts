# coding=utf-8
"""A smart contract that implements a simple, authenticated bank."""
import sqlite3
####################################################################
# imports
####################################################################
# general
from json import dumps, loads

# chainspace
from PythonContracts.contract import *
# crypto
from PythonContracts.utils import *

## contract name
contract = ChainspaceContract('node_join_checker')


@contract.checker('auth_transfer')
def auth_transfer_checker(inputs, reference_inputs, parameters, outputs, returns, dependencies):
    try:
        amount = loads(parameters[0])
        input_from_account = loads(inputs[0])
        input_to_account = loads(inputs[1])
        output_from_account = loads(outputs[0])
        output_to_account = loads(outputs[1])
        sig = unpack(parameters[1])

        # check format
        if len(inputs) != 2 or len(reference_inputs) != 0 or len(outputs) != 2 or len(returns) != 0:
            return False
        if input_from_account['pub'] != output_from_account['pub'] or input_to_account['pub'] != output_to_account[
            'pub']:
            return False

        # check tokens
        if input_from_account['type'] != 'BankAccount' or input_to_account['type'] != 'BankAccount':
            return False
        if output_from_account['type'] != 'BankAccount' or output_to_account['type'] != 'BankAccount':
            return False

        if amount != 3:
            return False

        # amount transfered should not exceed balance
        if input_from_account['balance'] < amount:
            return False

        # consistency between inputs and outputs
        if input_from_account['balance'] != output_from_account['balance'] + amount:
            return False
        if input_to_account['balance'] != output_to_account['balance'] - amount:
            return False

        # hash message to verify signature
        hasher = sha256()
        hasher.update(dumps(inputs).encode('utf8'))
        hasher.update(dumps(reference_inputs).encode('utf8'))
        hasher.update(dumps(parameters[0]).encode('utf8'))

        # recompose signed digest
        pub = unpack(input_from_account['pub'])

        # balance = output_from_account['balance']
        # 将新用户加入到identity_list中
        # conn = sqlite3.connect("test.db")
        # c = conn.cursor()
        # try:
        #     c.execute(
        #         "create table if not exists identity_list(id integer PRIMARY KEY autoincrement, pub text(256), balance text(8), isMaintained text(8))")
        #     c.execute("insert into identity_list(pub, balance, isMaintained) values(?, ?, ?)",
        #               (str(pub), str(balance), str(0)))
        #     conn.commit()
        # except Exception as e:
        #     conn.rollback()
        #     # print(e)
        # finally:
        #     c.close()
        #     conn.close()
        print "welcome to vchain！"

        # verify signature
        (G, _, _, _) = setup()
        return do_ecdsa_verify(G, pub, sig, hasher.digest())

    except (KeyError, Exception):
        return False
