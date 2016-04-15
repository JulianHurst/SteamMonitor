#!/usr/bin/env python3
import json
from pprint import pprint
import urllib.request
from os.path import expanduser
from os import stat
from os.path import isfile
import sys
from bs4 import BeautifulSoup

import http.client, urllib

def notifyphone(games,price):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    for i in range(len(games)):
        conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
            "token": "ajoGmJU6WFVMCXmohqHiGJ4hcJEwis",
            "user": "u41FwymKTrXv6hQgyqoNPrzBFHwGWN",
            "title": games[i]["name"],
            "message": "Price : "+str(prices[i])+"\nlowest price : "+str(games[i]["lowprice"]),
            "url": "http://store.steampowered.com/app/"+str(games[i]["appid"])+"/",
            "url_title": "Steam Store",
        }), { "Content-type": "application/x-www-form-urlencoded" })
        resp = conn.getresponse()
        if resp.status!=200:
            print(resp.status,resp.reason)
    conn.close()


def addgame(name,games):
    count=0
    gamelist = []
    req=json.loads(urllib.request.urlopen("http://api.steampowered.com/ISteamApps/GetAppList/v0001/").read().decode('utf-8'))
    for i in req["applist"]["apps"]["app"]:
        if name.lower() in i["name"].lower():
            gamelist.append(i)
    if len(gamelist)==0:
        print("No results")
        return
    for i in gamelist:
        print(i)
    with open(expanduser("~")+'/gamemonitor.json','w+') as d_file:
        if len(gamelist)==1:
            lprice = getlowestprice(gamelist[0]["appid"])
            if lprice == None:
                print("This game has no lowest recorded price")
                return 
            games["games"].append({"name":gamelist[0]["name"], "appid":gamelist[0]["appid"], "lowprice":lprice})
            print(games)
        else:
            gameid=input("Which appid ? ")
            for i in gamelist:
                if i["appid"]==int(gameid):
                    lprice = getlowestprice(gameid)
                    if lprice==None:
                        print("This game has no lowest recorded price")
                        return
                    games["games"].append({"name":i["name"], "appid":i["appid"], "lowprice":lprice})
                    print(games)
        json.dump(games,d_file, indent=4)

def getlowestprice(appid):
    months=["January","February","March","April","June","July","August","September","October","November","December"]
    url="https://steamdb.info/app/"+str(appid)+"/"
    req=urllib.request.Request("https://steamdb.info/app/"+str(appid)+"/",headers={'User-Agent' : "Magic Browser"})
    data=urllib.request.urlopen(req)
#    print(data.read().decode('utf-8'))
    soup = BeautifulSoup(data, 'html.parser')
#    print(soup.prettify())
    td=soup.find_all('td')
    for i in td:
        if i.has_attr('data-cc'):
            if "eu" in i['data-cc']:
                for j in i.find_next_siblings():
                    if j.has_attr('title'):
                        for m in months:
                            if m in j['title']:
                                s=j.text[:j.text.index(",")]
                                s+="."
                                s+=j.text[j.text.index(",")+1:j.text.index("€")]
                                n=float(s)
                                return n
    return None


filename=(expanduser("~")+'/gamemonitor.json')
if not isfile(filename):
    open(filename, 'a').close()

with open(filename,'r+') as d_file:
    print(d_file.name)
    if stat(d_file.name).st_size>0:
        games = json.load(d_file)
    else:
        games = {}
        games["games"]=[]
        #games = json.dumps(games)
        print(games)

if len(sys.argv)==3:
    if sys.argv[1]=="-a":
        addgame(sys.argv[2],games)
        sys.exit(0)

appid = []
notifgames = []
prices = []
for i in range(len(games["games"])):
    print(i)
    appid.append(games["games"][i]["appid"])
    data = json.loads(urllib.request.urlopen("http://store.steampowered.com/api/appdetails/?appids="+str(appid[i])+"&cc=EE&l=english&v=1").read().decode('utf-8'))
    print(data[str(appid[i])]["data"]["name"])
    lowprice = float(games["games"][i]["lowprice"])
    price = float(data[str(appid[i])]["data"]["price_overview"]["final"])/100
    diff = price-lowprice
    print("lowest price : ",lowprice,"euros")
    print("actual price : ",price,"euros")
    print("difference : ",diff,"euros")
    print("discount (%) : ",data[str(appid[i])]["data"]["price_overview"]["discount_percent"])
    if lowprice>=price and data[str(appid[i])]["data"]["price_overview"]["discount_percent"]!=0:
        notifgames.append(games["games"][i])
        prices.append(price)
notifyphone(notifgames,prices)
