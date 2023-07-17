"""
    The BlockMeter Experiment
    ~~~~~~~~~
    This module is necessary to register a meter in the blockchain. It
    receives the meter ID and its respective public key.
    This module must be called before any query against the ledger.
        
    :copyright: © 2020 by Wilson Melo Jr.
"""

import sys
from hfc.fabric import Client as client_fabric
import asyncio

#For convencion, the first domain should be your admin domain.
domain = ["inmetro.br"]
channel_name = "nmi-channel"
cc_name = "fabpki"
cc_version = "1.0"
callpeer = []

if __name__ == "__main__":
    #test if the meter ID was informed as argument
    if len(sys.argv) != 4:
        print("É esperado: Placa, combustível e distância")
        exit(1)

    #get the meter ID
    placa = sys.argv[1]
    combustivel = sys.argv[2]
    distancia = sys.argv[3]

    #shows the meter public key
    print("foram informado: ", placa, combustivel, distancia)

    # creates a loop object to manage async transactions
    # o código necessário para acessa Fabric começa aqui
    loop = asyncio.get_event_loop()

    #instantiate the hyperledeger fabric client
    c_hlf = client_fabric(net_profile=(domain[0] + ".json"))

    #get access to Fabric as Admin user
    admin = c_hlf.get_user(domain[0], 'Admin')
    
    for i in domain:
    	callpeer.append("peer0." + i)

    #the Fabric Python SDK do not read the channel configuration, we need to add it mannually'''
    c_hlf.new_channel(channel_name)

    #invoke the chaincode to register the meter
    response = loop.run_until_complete(c_hlf.chaincode_invoke(
        requestor=admin, 
        channel_name=channel_name, 
        peers=callpeer,
        cc_name=cc_name, 
        fcn='EnumerateHistory', 
        args=[placa, combustivel, distancia], 
        cc_pattern=None))

    #so far, so good
    print("Success on register meter and public key!")
