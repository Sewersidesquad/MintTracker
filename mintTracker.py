import requests
import json
import time
import base58
import os
import pandas as pd
import datetime
import tkinter
import customtkinter
import threading


def getNftData():
    global ACCOUNT_ID, HEADERS, logVar, total
    mintedDatas = []
    responseJson = requests.get(
        str(f"https://api3.loopring.io/api/v3/user/nft/mints?accountId={ACCOUNT_ID}"),
        headers=HEADERS,
    ).json()
    try:
        total = int(responseJson["totalNum"])
    except KeyError:
        logVar.set("Please restart and enter a correct API-KEY and Account ID.")
        time.sleep(100)
    logVar.set(str(f"Total number of mints: {total}"))
    time.sleep(1)
    logVar.set("Collecting mints...")
    try:
        while True:
            for i in range(50):
                mintedDatas.append(responseJson["mints"][i]["nftData"])
                created = responseJson["mints"][i]["createdAt"]
            url = str(
                f"https://api3.loopring.io/api/v3/user/nft/mints?accountId={ACCOUNT_ID}&start=1567053142&end={created}"
            )
            responseJson = requests.get(url, headers=HEADERS).json()
    except IndexError:
        logVar.set("Finished collecting...")

    return mintedDatas


def unScrambleNftId(nftId):
    nftId = nftId.replace("0x", "")
    nftId = "1220" + nftId
    bytesStr = bytes.fromhex(nftId)
    base58Str = base58.b58encode(bytesStr)
    cid = str(base58Str.decode("UTF-8"))
    return cid


def goHam(nftDatas):
    global HEADERS, logVar
    time.sleep(3)
    logVar.set("Gathering Data...")
    nfts = []
    p = 0
    for nftData in nftDatas:
        
        eta = datetime.datetime.now()
        p += 1
        time.sleep(1)
        nftClean = str(nftData.replace("'", ""))
        responseJson = requests.get(
            str(
                f"https://api3.loopring.io/api/v3/nft/info/nftHolders?nftData={nftClean}"
            ),
            headers=HEADERS,
        ).json()
        nftOwnersAccount = []
        nftOwnersAddress = []
        for i in range(int(responseJson["totalNum"])):
            account = responseJson["nftHolders"][i]["accountId"]
            owner = requests.get(
                str(f"https://api3.loopring.io/api/v3/account?accountId={account}")
            ).json()
            Owner = owner["owner"]
            nftOwnersAccount.append([account])
            nftOwnersAddress.append([Owner])
        nftInfo = requests.get(
            str(f"https://api3.loopring.io/api/v3/nft/info/nfts?nftDatas={nftClean}")
        ).json()
        nftId = nftInfo[0]["nftId"]
        cid = unScrambleNftId(nftId)
        metadata = requests.get(f"https://spacemonke.infura-ipfs.io/ipfs/{cid}").json()
        nftData = {
            "Name": metadata["name"],
            "Description": metadata["description"],
            "Owner Account ID(s)": [i for i in nftOwnersAccount],
            "Owner Wallet Address(es)": [i for i in nftOwnersAddress],
            "Royalty Percentage": metadata["royalty_percentage"],
            "MetaData CID": cid,
            "Image CID": metadata["image"],
        }
        nfts.append(nftData)
        # pp.pprint(nftData)
        
        etanow = datetime.datetime.now()
        etaDelta = etanow - eta
        timeLeft = int(etaDelta.total_seconds() *  (total - p))
        
        logVar.set(str(f"Total mints tracked: {p}/{total}, ETR: {datetime.timedelta(seconds=timeLeft)}"))
    logVar.set("Creating DataFrame...")
    return nfts


# perhaps use list of dictionarys to populate a data frame with for loops or think of another way so you don't have to grow the data frame


def createDf(nfts):
    global ACCOUNT_ID
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    path = os.getcwd() + f"\\{ACCOUNT_ID}s_mints_Tracked_On_{date}.xlsx"
    data = {
        "Name": [i["Name"] for i in nfts],
        "Description": [i["Description"] for i in nfts],
        "List Of Owner Account ID(s)": [i["Owner Account ID(s)"] for i in nfts],
        "List Of Owner Wallet Address(es)": [
            i["Owner Wallet Address(es)"] for i in nfts
        ],
        "Royalty Percentage": [i["Royalty Percentage"] for i in nfts],
        "Ipfs MetaData CID": [i["MetaData CID"] for i in nfts],
        "Image CID": [i["Image CID"] for i in nfts],
    }
    df = pd.DataFrame(data)
    logVar.set("Creating Spreadsheet...")
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer)
    time.sleep(1)
    logVar.set(f"Your spreadsheet is ready, in the same file as MintTracker.exe")


def getConstants():
    global logVar, entryApi, entryAccount
    path = os.getcwd() + "\\user_info.json"
    with open(path, "w") as f:
        data = {"Loopring API Key": entryApi.get(), "AccountID": entryAccount.get()}
        json.dump(data, f)
    logVar.set("Created user_info.json")


def setConstants():
    global API_KEY, ACCOUNT_ID, HEADERS, logVar
    path = os.getcwd() + "\\user_info.json"
    with open(path, "r") as f:
        info = json.load(f)
        API_KEY = info["Loopring API Key"]
        ACCOUNT_ID = info["AccountID"]
        HEADERS = {"X-API-KEY": API_KEY}
    if API_KEY == "" or ACCOUNT_ID == "":
        logVar.set("Please enter both API-KEY & AccountID and click create")
    else:
        time.sleep(1)
        logVar.set("Variable's Set")
        nfts = getNftData()
        ham = goHam(nfts)
        createDf(ham)


def main():
    global logVar, entryApi, entryAccount
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("dark-blue")
    app = customtkinter.CTk()
    app.geometry("580x400")
    app.title("MintTracker.py")
    logVar = tkinter.StringVar()
    logVar.set("Click create or track to get started!")
    theLabel = customtkinter.CTkLabel(
        master=app, text="Mint Tracker", text_font=("default", 28)
    )
    theLabelLog = customtkinter.CTkLabel(
        master=app, textvariable=logVar, text_font=("default", 16)
    )
    theLabelMe = customtkinter.CTkLabel(
        master=app,
        text="Created by sewersidesquad.eth",
        text_font=("default", 10),
        text_color="red",
    )
    entryApi = customtkinter.CTkEntry(master=app, placeholder_text="API-KEY", width=400)
    entryAccount = customtkinter.CTkEntry(
        master=app, placeholder_text="Account ID", width=400
    )
    buttonCreate = customtkinter.CTkButton(
        master=app, text="Create", width=70, height=50, command=getConstants
    )
    buttonTrack = customtkinter.CTkButton(
        master=app,
        text="Track",
        width=70,
        height=50,
        command=threading.Thread(target=setConstants).start,
    )
    theLabel.place(relx=0.5, rely=0.15, anchor=tkinter.CENTER)
    entryApi.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)
    entryAccount.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
    buttonCreate.place(relx=0.4, rely=0.52, anchor=tkinter.CENTER)
    buttonTrack.place(relx=0.6, rely=0.52, anchor=tkinter.CENTER)
    theLabelLog.place(relx=0.5, rely=0.68, anchor=tkinter.CENTER)
    theLabelMe.place(relx=0.5, rely=0.85, anchor=tkinter.CENTER)

    app.mainloop()


if __name__ == "__main__":
    main()
