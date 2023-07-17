import requests
import sys
from hfc.fabric import Client as client_fabric
import asyncio
import datetime
import time
from get_previsao import getPrevisao
from get_estacao import getEstacao

domain = ["inmetro.br"]
channel_name = "nmi-channel"
cc_name = "fabpki"
cc_version = "1.0"
callpeer = []

clientTimestamp = time.time()
arrayPrevisao = []
arrayPrevisao = getPrevisao(print_output=False)
horarioPrevisao = arrayPrevisao[8] # Usar isso como base na hora de verificar a cada 5 minutos
print(horarioPrevisao)


# if __name__ == "__main__":

#     #test if the city name was informed as argument
#     if len(sys.argv) != 2: # o primeiro  argumentosempre vai ser o chamado do python
#         print("Usage:",sys.argv[0], "<\"city name\"> ")
#         exit(1)

#     # recebe os argumentos das funções get estação e get previsão
#     cidade = sys.argv[1]

#     #creates a loop object to manage async transactions
#     loop = asyncio.get_event_loop()

#     #instantiate the hyperledeger fabric client
#     c_hlf = client_fabric(net_profile=(domain[0] + ".json"))

#     #get access to Fabric as Admin user
#     admin = c_hlf.get_user(domain[0], 'Admin')
#     for i in domain:
#     	callpeer.append("peer0." + i)

#     #the Fabric Python SDK do not read the channel configuration, we need to add it mannually'''
#     c_hlf.new_channel(channel_name)

#     #invoke the chaincode to register the meter
#     response = loop.run_until_complete(c_hlf.chaincode_invoke(
#         requestor=admin, 
#         channel_name=channel_name, 
#         peers=callpeer,
#         cc_name=cc_name, 
#       # cc_version=cc_version,
#         fcn='registerWeatherFromWeb',
#         args=[cidade, situacao, temperaturaString],
#         cc_pattern=None))

#     #so far, so good
#     print("Success on register climate")