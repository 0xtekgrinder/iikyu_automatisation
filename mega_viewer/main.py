import requests
import os

from dotenv import load_dotenv, find_dotenv
from urllib.parse import urlencode

load_dotenv(find_dotenv())

JwtToken = os.environ.get("JWTTOKEN")

nbItems = 4
URL = "https://api.streamelements.com/kappa/v2"

class seClass:

    def __init__(self):
        r = requests.get(url=URL + "/channels/me",
                        headers={'Accept':'application/json', 'Authorization': 'Bearer {}'.format(JwtToken)})
        data = r.json()
        self.GUID = data['_id']

    def getIdItems(self):
        r = requests.get(url=URL + "/store/{}/items".format(self.GUID),
                        headers={'Accept':'application/json', 'Authorization': 'Bearer {}'.format(JwtToken)})
        data = r.json()
        self.items = [None] * nbItems
        for item in data:
            for i in range(nbItems):
                if item['name'] == 'Spin MEGABALL ' + str(i + 1) + '0€':
                    self.items[i] = item['_id']

    def activateOrDisableItems(self, bool):
        for i in range(nbItems):
            r = requests.get(url=URL + "/store/{}/items/{}".format(self.GUID, self.items[i]),
                            headers={'Accept':'application/json', 'Authorization': 'Bearer {}'.format(JwtToken)})
            data = r.json()
            r = requests.put(url=URL + "/store/{}/items/{}".format(self.GUID, self.items[i]),
                            data={'name':data['name'], 'description':data['description'], 'enabled':bool},
                            headers={'Accept':'application/json', 'Authorization': 'Bearer {}'.format(JwtToken)})

    def getLastRedemption(self):
        r = requests.get(url=URL + "/store/{}/redemptions/?{}".format(self.GUID, urlencode({'pending':'true'})),
                        headers={'Accept':'application/json', 'Authorization': 'Bearer {}'.format(JwtToken)})
        data = r.json()
        self.lastRedemption = data['docs'][0]

    def sendPoints(self, username, amount):
        r = requests.put(url=URL + "/points/{}/{}/{}".format(self.GUID, username, amount),
                        headers={'Accept':'application/json', 'Authorization': 'Bearer {}'.format(JwtToken)})


def main():
    amazing = seClass()
    amazing.getIdItems()
    amazing.activateOrDisableItems(True)
    string = ""
    while string != "N":
        amazing.getLastRedemption()
        print(amazing.lastRedemption['redeemer']['username'] + " reedemed " + amazing.lastRedemption['item']['name'] + " with card value of: " + amazing.lastRedemption['input'][0])
        print("What is the win value ?")
        value = float(input())
        if (value >= int(amazing.lastRedemption['item']['name'][14]) * 10 - 1 and value <= int(amazing.lastRedemption['item']['name'][14]) * 10):
            print("Refund")
            amazing.sendPoints(amazing.lastRedemption['redeemer']['username'], int(500 * int(amazing.lastRedemption['item']['name'][14])))
        if (value > int(amazing.lastRedemption['item']['name'][14]) * 10 and value < int(amazing.lastRedemption['item']['name'][14]) * 10 + 10):
            print("Refund + Profit")
            amazing.sendPoints(amazing.lastRedemption['redeemer']['username'], int(500 * int(amazing.lastRedemption['item']['name'][14]) + (value - int(amazing.lastRedemption['item']['name'][14]) * 10) * 10))
        if (value < int(amazing.lastRedemption['item']['name'][14]) * 10):
            print("Lost")
        if (value >= int(amazing.lastRedemption['item']['name'][14]) * 10 + 10):
            print("Win,", int(500 * int(amazing.lastRedemption['item']['name'][14]) + (value - int(amazing.lastRedemption['item']['name'][14]) * 10) * 10), "points (P) or", (value - int(amazing.lastRedemption['item']['name'][14]) * 10) * 0.25, "euro (E)")
            choice = input()
            if (choice == "P"):
                amazing.sendPoints(amazing.lastRedemption['redeemer']['username'], int(500 * int(amazing.lastRedemption['item']['name'][14]) + (value - int(amazing.lastRedemption['item']['name'][14]) * 10) * 10))
            if (choice == 'E'):
                print("send ", value - int(amazing.lastRedemption['item']['name'][14]) * 10 * 0.25, "euro to " + amazing.lastRedemption['redeemer']['username'])
        print("Continue ? (Y/N)")
        string = input()
    amazing.activateOrDisableItems(False)

if __name__ == "__main__":
    main()