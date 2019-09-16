# coding=utf-8
""" VChain system contracts, created by aaron 2019.9.16"""
from json import dumps, loads
import time
from PythonContracts.contract import *
# crypto
from generate_vchain_account import *
from PythonContracts.utils import *

contract = ChainspaceContract('vchain_system')


@contract.method('init')
def init():
    # return
    return {
        'outputs': (dumps({'type': 'BankToken'}),),
    }


@contract.method('create_account')
def create_account(inputs, reference_inputs, parameters, pub):
    # new account
    balance = loads(parameters[0])
    new_account = {'type': 'BankAccount', 'pub': pub, 'balance': balance}
    # return
    return {
        'outputs': (inputs[0], dumps(new_account))
    }


@contract.method("join")
def join(inputs, reference_inputs, parameters, priv):
    # compute outputs
    # amount = loads(parameters[0])
    new_from_account = loads(inputs[0])
    new_to_account = loads(inputs[1])
    new_from_account["balance"] -= 3
    new_to_account["balance"] += 3

    # hash message to sign
    hasher = sha256()
    hasher.update(dumps(inputs).encode('utf8'))
    hasher.update(dumps(reference_inputs).encode('utf8'))
    # hasher.update(dumps(parameters[0]).encode('utf8'))

    # sign message
    G = setup()[0]
    sig = do_ecdsa_sign(G, unpack(priv), hasher.digest())

    return {
        'outputs': (dumps(new_from_account), dumps(new_to_account)),
        'extra_parameters': (pack(sig),)
    }


@contract.method("maintain")
def maintain(inputs, reference_inputs, parameters, priv):
    # compute outputs
    # amount = loads(parameters[0])
    new_from_account = loads(inputs[0])
    new_to_account = loads(inputs[1])
    new_from_account["balance"] -= 1
    new_to_account["balance"] += 1

    # hash message to sign
    hasher = sha256()
    hasher.update(dumps(inputs).encode('utf8'))
    hasher.update(dumps(reference_inputs).encode('utf8'))
    # hasher.update(dumps(parameters[0]).encode('utf8'))

    # sign message
    G = setup()[0]
    sig = do_ecdsa_sign(G, unpack(priv), hasher.digest())

    return {
        'outputs': (dumps(new_from_account), dumps(new_to_account)),
        'extra_parameters': (pack(sig),)
    }


@contract.method("active_quit")
def active_quit(inputs, reference_inputs, parameters, priv):
    # compute outputs
    # amount = loads(parameters[0])
    new_from_account = loads(inputs[0])
    new_to_account = loads(inputs[1])
    new_from_account["balance"] -= 0
    new_to_account["balance"] += 0

    # hash message to sign
    hasher = sha256()
    hasher.update(dumps(inputs).encode('utf8'))
    hasher.update(dumps(reference_inputs).encode('utf8'))
    # hasher.update(dumps(parameters[0]).encode('utf8'))

    # sign message
    G = setup()[0]
    sig = do_ecdsa_sign(G, unpack(priv), hasher.digest())

    return {
        'outputs': (dumps(new_from_account), dumps(new_to_account)),
        'extra_parameters': (pack(sig),)
    }


""" VChain checker here """


@contract.checker('create_account')
def create_account_checker(inputs, reference_inputs, parameters, outputs, returns, dependencies):
    try:
        input_token = loads(inputs[0])
        output_token = loads(outputs[0])
        output_account = loads(outputs[1])
        balance = loads(parameters[0])

        # check format
        if len(inputs) != 1 or len(reference_inputs) != 0 or len(outputs) != 2 or len(returns) != 0:
            return False
        if output_account['pub'] == None or output_account['balance'] != balance:
            return False

        # check tokens
        if input_token['type'] != 'BankToken' or output_token['type'] != 'BankToken':
            return False
        if output_account['type'] != 'BankAccount':
            return False

        # update balance
        with open("balance.txt", "w+") as f:
            f.write(str(balance))
        f.close()

        return True

    except (KeyError, Exception):
        return False


@contract.checker("join")
def join_checker(inputs, reference_inputs, parameters, outputs, returns, dependencies):
    try:
        # amount = loads(parameters[0])
        input_from_account = loads(inputs[0])
        input_to_account = loads(inputs[1])
        output_from_account = loads(outputs[0])
        output_to_account = loads(outputs[1])
        sig = unpack(parameters[0])

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

        # amount transfered should not exceed balance
        if input_from_account['balance'] < 3:
            return False

        # consistency between inputs and outputs
        if input_from_account['balance'] != output_from_account['balance'] + 3:
            return False
        if input_to_account['balance'] != output_to_account['balance'] - 3:
            return False

        # hash message to verify signature
        hasher = sha256()
        hasher.update(dumps(inputs).encode('utf8'))
        hasher.update(dumps(reference_inputs).encode('utf8'))
        # hasher.update(dumps(parameters[0]).encode('utf8'))

        # recompose signed digest
        pub = unpack(input_from_account['pub'])

        # verify signature
        (G, _, _, _) = setup()
        flag = do_ecdsa_verify(G, pub, sig, hasher.digest())
        # update balance
        with open("balance.txt", "w+") as f:
            f.write(str(output_from_account['balance']))
        f.close()

        print "Welcome to VChain!"
        return flag

    except (KeyError, Exception):
        return False


@contract.checker("maintain")
def maintain_checker(inputs, reference_inputs, parameters, outputs, returns, dependencies):
    try:
        # amount = loads(parameters[0])
        input_from_account = loads(inputs[0])
        input_to_account = loads(inputs[1])
        output_from_account = loads(outputs[0])
        output_to_account = loads(outputs[1])
        sig = unpack(parameters[0])

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

        # amount transfered should not exceed balance
        if input_from_account['balance'] < 1:
            return False

        # consistency between inputs and outputs
        if input_from_account['balance'] != output_from_account['balance'] + 1:
            return False
        if input_to_account['balance'] != output_to_account['balance'] - 1:
            return False

        # hash message to verify signature
        hasher = sha256()
        hasher.update(dumps(inputs).encode('utf8'))
        hasher.update(dumps(reference_inputs).encode('utf8'))
        # hasher.update(dumps(parameters[0]).encode('utf8'))

        # recompose signed digest
        pub = unpack(input_from_account['pub'])

        # verify signature
        (G, _, _, _) = setup()
        flag = do_ecdsa_verify(G, pub, sig, hasher.digest())
        # update balance
        with open("balance.txt", "w+") as f:
            f.write(str(output_from_account['balance']))
        f.close()

        print "maintain successfully!"

        return flag

    except (KeyError, Exception):
        return False


@contract.checker("active_quit")
def active_quit_checker(inputs, reference_inputs, parameters, outputs, returns, dependencies):
    try:
        # amount = loads(parameters[0])
        input_from_account = loads(inputs[0])
        input_to_account = loads(inputs[1])
        output_from_account = loads(outputs[0])
        output_to_account = loads(outputs[1])
        sig = unpack(parameters[0])

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

        # consistency between inputs and outputs
        if input_from_account['balance'] != output_from_account['balance'] + 0:
            return False
        if input_to_account['balance'] != output_to_account['balance'] - 0:
            return False

        # hash message to verify signature
        hasher = sha256()
        hasher.update(dumps(inputs).encode('utf8'))
        hasher.update(dumps(reference_inputs).encode('utf8'))
        # hasher.update(dumps(parameters[0]).encode('utf8'))

        # recompose signed digest
        pub = unpack(input_from_account['pub'])

        # verify signature
        (G, _, _, _) = setup()
        flag = do_ecdsa_verify(G, pub, sig, hasher.digest())
        # update balance
        with open("balance.txt", "w+") as f:
            f.write(str(output_from_account['balance'] + 3))
        f.close()

        print "See you!"

        return flag

    except (KeyError, Exception):
        return False
