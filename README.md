# MintTracker

Please double check your sheets to make sure you're happy with them. Let me know if there's any issues. 

Track where all the nfts you have minted are stored

Download it here - https://github.com/Sewersidesquad/MintTracker/releases

extract/unzip it and read the get started pdf :)


Install dependencies by:
```
pip install -r requirements.txt
```

or read it here without the pictures - 

Step 1
Go into your loopring wallet

And click on security

Click Export account and be ready to copy your Api key and account id.
DO NOT SHARE YOUR API KEY WITH ANYONE. EVER.


Step 2

Go into the mintTracker folder and find and open the mintTracker.exe


step 3

Copy your API-KEY and Account ID into the tracker.
You can use ctrl+v to paste them into the boxes.
Once they’re both in, make sure they are correct and click create.

step 4
Once the create_user_info message appears click wether you need the nft attributes from your metadata or not. 

step 5
Now just click track and it’ll start to collect the mints.
It will track your mints one by one so just wait for it to finish it could take a while depending on how many nfts you have minted.
The ETR is not that accurate i’d say its 20/30 seconds on average per nft.

It will tell you when its ready
Once ready just go in the same folder that mintTracker.exe is in and your .csv file will be there.

The file name will be:
“{AccountID}s_mints_tracked_on_{Date}.csv”

You can open this in excel, google sheets etc.

You only need to enter your api key and account id if its your first tracking or if you want to change the account your tracking you’ll need to re enter both your api key and the new account.
If you’re tracking the same account with the same api key do not click create, just click track and it will create you your spreadsheet.
Happy Tracking

Errors
If there is an error it will try its best to let you know. Please follow what it says and restart the .exe file.



