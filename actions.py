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

def retrieve_data(nft, holders, cid, attrs):
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
        name = metadata["name"]
        description = metadata["description"]
        royalty = metadata["royalty_percentage"]
        image_cid = metadata["image"]
    except Exception:
        name = nft
        description = "Not Found, nft ID provided in Name"
        royalty = "Not Found"
        image_cid = "Not Found"

    for i in holders:
        nft_data = {
            "Name": name,
            "Description": description,
            "Owner": i[0],
            "Amount": i[1],
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
    

