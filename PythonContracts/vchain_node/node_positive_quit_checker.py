# coding=utf-8

from json import dumps, loads

# chainspace
from PythonContracts.contract import *
# crypto
from PythonContracts.utils import *

## contract name
contract = ChainspaceContract('node_positive_quit_checker')


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
        if amount != 0:
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

        # conn = sqlite3.connect("test.db")
        # c = conn.cursor()
        # try:
        #     c.execute("delete from identity_list where pub = ?", (str(pub),))
        #     conn.commit()
        # except Exception as e:
        #     conn.rollback()
        #     print(e)
        # finally:
        #     c.close()
        #     conn.close()
        print "see you!"

        # verify signature
        (G, _, _, _) = setup()
        return do_ecdsa_verify(G, pub, sig, hasher.digest())

    except (KeyError, Exception):
        return False
