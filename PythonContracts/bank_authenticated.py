# coding=utf-8
import sqlite3
####################################################################
# imports
####################################################################
# general
from json import dumps, loads

# chainspace
from contract import *
# crypto
from utils import *

# from global_var import flag

## contract name
contract = ChainspaceContract('bank_authenticated')


####################################################################
# methods
####################################################################
# ------------------------------------------------------------------
# init
# ------------------------------------------------------------------
# 初始化合約
@contract.method('init')
def init():
    # return
    return {
        'outputs': (dumps({'type': 'BankToken'}),),
    }


# ------------------------------------------------------------------
# create account
# NOTE:
#   - only 'inputs', 'reference_inputs' and 'parameters' are used to the framework
#   - if there are more than 3 param, the checker has to be implemented by hand
# ------------------------------------------------------------------
# 創建賬戶
@contract.method('create_account')
def create_account(inputs, reference_inputs, parameters, pub):
    # new account
    new_account = {'type': 'BankAccount', 'pub': pub, 'balance': 10}
    # return
    return {
        'outputs': (inputs[0], dumps(new_account))
    }


# ------------------------------------------------------------------
# make transfer
# NOTE:
#   - only 'inputs', 'reference_inputs' and 'parameters' are used to the framework
#   - if there are more than 3 param, the checker has to be implemented by hand
# ------------------------------------------------------------------

# 执行转账交易
@contract.method('auth_transfer')
def auth_transfer(inputs, reference_inputs, parameters, priv):
    # compute outputs
    amount = loads(parameters[0])  # 转账金额
    new_from_account = loads(inputs[0])  # 旧账户
    new_to_account = loads(inputs[1])  # 新账户
    new_from_account["balance"] -= amount  # 更新旧账户余额
    new_to_account["balance"] += amount  # 更新新账户余额

    # hash message to sign
    hasher = sha256()
    hasher.update(dumps(inputs).encode('utf8'))
    hasher.update(dumps(reference_inputs).encode('utf8'))
    hasher.update(dumps(parameters[0]).encode('utf8'))
    #  生成hash摘要

    # sign message
    G = setup()[0]
    sig = do_ecdsa_sign(G, unpack(priv), hasher.digest())
    #   生成签名
    # return
    return {
        'outputs': (dumps(new_from_account), dumps(new_to_account)),
        'extra_parameters': (pack(sig),)
    }


# ------------------------------------------------------------------
# read
# ------------------------------------------------------------------

#   显示账户余额
@contract.method('read')
def read(inputs, reference_inputs, parameters):
    # return
    return {
        'returns': (reference_inputs[0],),
    }


####################################################################
# checker
####################################################################
# ------------------------------------------------------------------
# check account's creation
# ------------------------------------------------------------------
@contract.checker('create_account')
def create_account_checker(inputs, reference_inputs, parameters, outputs, returns, dependencies):
    try:
        input_token = loads(inputs[0])
        output_token = loads(outputs[0])
        output_account = loads(outputs[1])

        # check format
        if len(inputs) != 1 or len(reference_inputs) != 0 or len(outputs) != 2 or len(returns) != 0:
            return False
        if output_account['pub'] == None:  # or output_account['balance'] != 10:
            return False

        # check tokens
        if input_token['type'] != 'BankToken' or output_token['type'] != 'BankToken':
            return False
        if output_account['type'] != 'BankAccount':
            return False

        # otherwise
        return True

    except (KeyError, Exception):
        return False


# ------------------------------------------------------------------
# check transfer
# ------------------------------------------------------------------
#   验证转账交易是否合法
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

        # amount transfered should be non-negative
        if amount < 0:
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
        # verify signature
        (G, _, _, _) = setup()
        return do_ecdsa_verify(G, pub, sig, hasher.digest())

    except (KeyError, Exception):
        return False


# ------------------------------------------------------------------
# check read
# ------------------------------------------------------------------
@contract.checker('read')
def read_checker(inputs, reference_inputs, parameters, outputs, returns, dependencies):
    try:

        # check format
        if len(inputs) != 0 or len(reference_inputs) != 1 or len(outputs) != 0 or len(returns) != 1:
            return False

        # check values
        if reference_inputs[0] != returns[0]:
            return False

        # otherwise
        return True

    except (KeyError, Exception):
        return False


####################################################################
# main
####################################################################
if __name__ == '__main__':
    contract.run()

####################################################################
