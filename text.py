import pykerio
import ssl
server = "88.198.113.206"
server2 = '31.128.70.43'
ssl._create_default_https_context = ssl._create_unverified_context
api = pykerio.PyKerioControl(server=server, port=4081)

application = pykerio.structs.ApiApplication({'name': pykerio.APP_NAME, 'vendor': pykerio.APP_AUTHOR, 'version': pykerio.APP_VERSION})
session = pykerio.interfaces.Session(api)
session.login('S.Vlasyuk', 'VNvTc5z$W7', application)
response = api.request_rpc(method='Interfaces.get',
                               params={"query":{"orderBy":[],"conditions":[]}, "sortByGroup": True})

for iface in response.result['list']:
    if iface["ip"]:
        print('up', iface["name"], iface["ip"])
    else:
        print('down', iface["name"], iface["ip"])