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
        if data['_total'] == 0:
            self.getLastRedemption()
        else:
            self.lastRedemption = data['docs'][0]

    def sendPoints(self, username, amount):
        r = requests.put(url=URL + "/points/{}/{}/{}".format(self.GUID, username, amount),
                        headers={'Accept':'application/json', 'Authorization': 'Bearer {}'.format(JwtToken)})

    def updateRedemptionStatus(self, bool, guid):
        r = requests.put(url=URL + "/store/{}/redemptions/{}".format(self.GUID, guid),
                        data={'completed':bool},
                        headers={'Accept':'application/json', 'Authorization': 'Bearer {}'.format(JwtToken)})


def payoutHandle(value, buyAmountMoney, buyAmountPoints, username, amazing):

    if (value >= buyAmountMoney - 1 and value <= buyAmountMoney):
        print("Refund")
        amazing.sendPoints(username, buyAmountPoints)

    if (value > buyAmountMoney and value < buyAmountMoney + 10):
        print("Refund + Profit")
        amazing.sendPoints(username, int(buyAmountPoints + (value - buyAmountMoney) * 10))

    if (value < buyAmountMoney):
        print("Lost")

    if (value >= buyAmountMoney + 10):
        print("Win,", int(buyAmountPoints + (value - buyAmountMoney) * 10), "points (P) or", (value - buyAmountMoney) * 0.25, "euro (E)")

        choice = input()

        if (choice == "P"):
            amazing.sendPoints(username, int(buyAmountPoints + (value - buyAmountMoney) * 10))

        if (choice == 'E'):
            print("send ", value - buyAmountMoney * 0.25, "euro to " + username)


def main():

    amazing = seClass()

    amazing.getIdItems()
    amazing.activateOrDisableItems(True)

    string = ""

    while string != "N":

        amazing.getLastRedemption()

        username = amazing.lastRedemption['redeemer']['username']
        itemName = amazing.lastRedemption['item']['name']
        buyAmountPoints = 500 * int(itemName[14])
        buyAmountMoney = 10 * int(itemName[14])

        print(username + " reedemed " + itemName + " with card value of: " + amazing.lastRedemption['input'][0])

        print("What is the payout value ?")
        value = float(input())

        payoutHandle(value, buyAmountMoney, buyAmountPoints, username, amazing)

        amazing.updateRedemptionStatus(True, amazing.lastRedemption['_id'])

        print("Continue ? (Y/N)")
        string = input()

    amazing.activateOrDisableItems(False)

if __name__ == "__main__":
    main()