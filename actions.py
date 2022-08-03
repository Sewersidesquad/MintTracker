import constants as c
import requests
import base58

def find_holders(nft):
    response = requests.get(
        f"https://api3.loopring.io/api/v3/nft/info/nftHolders?nftData={nft}",
        headers=c.HEADERS,
    ).json()
    owner_addresses = []
    for i in range(response["totalNum"]):
        account = response["nftHolders"][i]["accountId"]
        owner = requests.get(
            str(f"https://api3.loopring.io/api/v3/account?accountId={account}")
        ).json()
        Owner = owner["owner"]
        amount = response["nftHolders"][i]["amount"]
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

def quantity_dict(holders):
    quant_dict = {}
    for i in holders:
        holder = i[0]
        quant_dict[holder] = i[1]
    return quant_dict

def retrieve_data(nft, holders, cid, attrs, props, quantity):
    if quantity == "on":
        quantity = quantity_dict(holders)
    else:
        quantity = [i[0] for i in holders]
    try:
        metadata = requests.get(
            f"https://spacemonke.infura-ipfs.io/ipfs/{cid}"
        ).json()
        try:
            if attrs == "on" and props == "on":
                attrs = metadata["attributes"]
                props = metadata["properties"]
            elif attrs == "on":
                attrs = metadata["attributes"]
                props = "Not selected"
            elif props == "on":
                attrs = "Not selected"
                props = metadata["properties"]
            else:
                attrs = "Not selected"
                props = "Not selected"
        except Exception:
            props = "Not Found"
            attrs = "Not Found"
            
        nft_data = {
            "Name": metadata["name"],
            "Description": metadata["description"],
            "Owner Wallet Address(es)": quantity,
            "Royalty Percentage": metadata["royalty_percentage"],
            "Attributes": attrs,
            "Properties": props,
            "MetaData CID": cid,
            "Image CID": metadata["image"],
        }
    except Exception:
        nft_data = {
            "Name": nft,
            "Description": "Not Found, nft ID provided in Name",
            "Owner Wallet Address(es)": quantity,
            "Royalty Percentage": "Not Found",
            "Attributes": "Not Found",
            "Properties": "Not Found",
            "MetaData CID": cid,
            "Image CID": "Not Found",
            
        }
    return nft_data

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
        total = c.TOTAL
    except KeyError:
        return False
    try:
        while True:
            for i in range(50):
                mintedDatas.append(responseJson["mints"][i]["nftData"])
                created = responseJson["mints"][i]["createdAt"]
            url = str(
                f"https://api3.loopring.io/api/v3/user/nft/mints?accountId={account_Id}&start=1567053142&end={created}"
            )
            responseJson = requests.get(url, headers=headers).json()
    except IndexError:
        pass

    return mintedDatas
    

