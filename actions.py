import constants as c
import requests
import base58
import time


def find_holders(nft):
    accounts = []
    owner_addresses = []
    offset = 0
    flag = 1
    try:
        while flag:
            time.sleep(1)
            response = requests.get(
                f"https://api3.loopring.io/api/v3/nft/info/nftHolders?nftData={nft}&offset={offset}",
                headers=c.HEADERS,
            ).json()
            for i in response['nftHolders']:
                accounts.append((i['accountId'], i['amount']))
            offset += 100
            if response['totalNum'] == 100:
                flag = 1
            else:
                flag = 0
    except Exception:
        pass
    for i in accounts:
        owner = requests.get(
            str(f"https://api3.loopring.io/api/v3/account?accountId={i[0]}")
        ).json()
        Owner = owner["owner"]
        amount = i[1]
        c.amount_held_all += int(i[1])
        owner_addresses.append((Owner, amount))
    return owner_addresses

def convert_cid(nft):
    nft_Id = requests.get(
        f"https://api3.loopring.io/api/v3/nft/info/nfts?nftDatas={nft}"
    ).json()[0]["nftId"]
    nft_Id = "1220" + nft_Id.replace("0x", "")
    bytesStr = bytes.fromhex(nft_Id)
    base58Str = base58.b58encode(bytesStr)
    return str(base58Str.decode("UTF-8"))


def retrieve_data(nft, amount_minted, holders, cid, attrs):
    datas_nft = []
    try:
        metadata = requests.get(f"https://spacemonke.infura-ipfs.io/ipfs/{cid}").json()
        try:
            if attrs == "on":
                attrs = metadata["attributes"]
            else:
                attrs = "Not selected"
        except Exception:
            attrs = "Not Found"
        name = str(metadata["name"])
        description = str(metadata["description"])
        royalty = str(metadata["royalty_percentage"])
        image_cid = str(metadata["image"])
    except Exception:
        name = str(nft)
        description = "Not Found, nft ID provided in Name"
        royalty = "Not Found"
        image_cid = "Not Found"
    for i in holders:
        nft_data = {
            "Name": name,
            "Description": description,
            "Owner": i[0],
            "Amount": i[1],
            "Amount Minted": amount_minted,
            "Royalty Percentage": royalty,
            "Metadata Cid": cid,
            "Image Cid": image_cid,
        }
        p = 1
        if type(attrs) == list:
            for i in attrs:
                key_name_trait = "Trait " + str(p)
                key_name_value = "Value " + str(p)
                nft_data[key_name_trait] = i["trait_type"]
                nft_data[key_name_value] = i["value"]
                p += 1

        datas_nft.append(nft_data)

    return datas_nft

def get_nft_datas():
    account_Id = c.ACCOUNT_ID
    headers = c.HEADERS
    mintedDatas = []
    responseJson = requests.get(
        str(f"https://api3.loopring.io/api/v3/user/nft/mints?accountId={account_Id}"),
        headers=headers,
    ).json()
    try:
        c.TOTAL = int(responseJson["totalNum"])
    except KeyError:
        return False
    try:
        while True:
            for i in range(50):
                mintedDatas.append((responseJson["mints"][i]["nftData"], responseJson["mints"][i]["amount"]))
                c.amount_minted_all += int(responseJson["mints"][i]["amount"])
                created = responseJson["mints"][i]["createdAt"]
            url = str(
                f"https://api3.loopring.io/api/v3/user/nft/mints?accountId={account_Id}&start=1567053142&end={created}"
            )
            responseJson = requests.get(url, headers=headers).json()
    except IndexError:
        pass
    return mintedDatas
    

