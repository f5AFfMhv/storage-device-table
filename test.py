#!/usr/bin/env python3

# server = {
#         'name' : 'testas',
#         'mount' : 'C',
#         'state' : 'normal'
#     }

# server_list = ('testas', 'C', 'normal')

# print(type(server))
# print(type(server_list))

# print(server)
# print(server_list)

# conv = [j for i, j in server.items()]


# print(conv)

import requests
r = requests.get('http://localhost:5000/api/v1/resources/servers?id=')
print(r.json())
print(r.status_code)