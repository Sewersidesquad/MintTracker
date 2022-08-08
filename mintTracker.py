import customtkinter
import tkinter as tk
import json
import os
import constants as c
import threading
import actions as act
import datetime
import time
import csv
import itertools



class App(customtkinter.CTk):
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    def __init__(self):
        super().__init__()
        self.geometry("600x350")
        self.title("MintTracker.py")
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=2)
        self.grid_columnconfigure(3, weight=2)
        self.grid_columnconfigure(4, weight=1)
        self.resizable(100, 0)
        self.nfts = []
        self.log_var = tk.StringVar()
        self.log_var.set("Click create or track to get started!")


        self.title_label = customtkinter.CTkLabel(
            master=self, text="Mint Tracker", text_font=("default", 28)
        )

        self.the_log_label = customtkinter.CTkLabel(
            master=self, textvariable=self.log_var, text_font=("default", 16)
        )

        self.my_label = customtkinter.CTkLabel(
            master=self,
            text="Created by sewersidesquad.eth",
            text_font=("default", 10),
            text_color="red",
        )
        self.attr_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Attributes",
            onvalue="on",
            offvalue="off",
        )

        self.pb1 = tk.ttk.Progressbar(
            master=self,
            orient=tk.HORIZONTAL,
            length=500,
            maximum=100,
            mode="determinate",
        )

        self.entry_apik = customtkinter.CTkEntry(
            master=self, placeholder_text="API-KEY", width=400
        )
        self.entry_acc = customtkinter.CTkEntry(
            master=self, placeholder_text="Account ID", width=400
        )

        self.create_button = customtkinter.CTkButton(
            master=self, text="Create", width=70, height=50, command=self.create_consts
        )
        self.track_button = customtkinter.CTkButton(
            master=self,
            text="Track",
            width=70,
            height=50,
            command=threading.Thread(target=self.track).start,
        )
        self.create_widgets()

    def create_widgets(self):
        padding = {"padx": 5, "pady": 5}
        self.title_label.grid(row=0, column=1, columnspan=3, **padding, sticky=tk.N)
        self.entry_apik.grid(row=1, column=1, columnspan=3, **padding, sticky="new")
        self.entry_acc.grid(row=1, column=1, columnspan=3, **padding, sticky="sew")
        self.create_button.grid(row=2, column=2, **padding, sticky="nw")
        self.track_button.grid(row=2, column=2, **padding, sticky="ne")
        self.attr_checkbox.grid(row=2, column=2, **padding)
        self.the_log_label.grid(row=4, column=2, **padding, sticky=tk.N)
        self.pb1.grid(row=4, column=2, sticky=tk.S)
        self.my_label.grid(row=5, column=2, **padding)
    

    def get_consts(self):
        c.ATTRS = self.attr_checkbox.get()
        path = os.getcwd() + "\\user_info.json"
        with open(path, "r") as f:
            info = json.load(f)
            c.API_KEY = info["Loopring API Key"]
            c.ACCOUNT_ID = info["AccountID"]
            c.HEADERS = {"X-API-KEY": c.API_KEY}
        if c.API_KEY == "" or c.ACCOUNT_ID == "":
            self.log_var.set("Please enter both API-KEY & AccountID and click create")
            return False
        else:
            self.log_var.set("API-KEY and Account ID set")
            return True

    def create_consts(self):
        path = os.getcwd() + "\\user_info.json"
        with open(path, "w") as f:
            data = {
                "Loopring API Key": self.entry_apik.get(),
                "AccountID": self.entry_acc.get(),
            }
            json.dump(data, f)
        self.log_var.set("Created user_info.json")

    def track(self):
        self.get_consts()
        time.sleep(1)
        self.log_var.set("Collecting mints...")
        nft_datas = act.get_nft_datas()
        if nft_datas == False:
            self.log_var.set(
                "Please restart and enter a correct API-KEY and Account ID."
            )
            return
        else:
            p = 0
            total = c.TOTAL
            for nft in nft_datas:
                eta = datetime.datetime.now()
                p += 1
                self.nfts.append(MintedNft(nft))
                etanow = datetime.datetime.now()
                etaDelta = etanow - eta
                timeLeft = int(etaDelta.total_seconds() * (total - p))

                self.log_var.set(
                    str(
                        f"Total mints tracked: {p}/{total}, ETR: {datetime.timedelta(seconds=timeLeft)}"
                    )
                )
                step = round(100 / total, 2)
                self.pb1.step(step)

        self.create_csv()

    def create_csv(self):
        self.log_var.set("Creating DataFrame...")
        account_ID = c.ACCOUNT_ID
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        path = os.getcwd() + f"\\{account_ID}s_mints_Tracked_On_{date}.csv"
        data = [i.data for i in self.nfts]
        data = list(itertools.chain.from_iterable(data))
        amounts = {"Amount Minted": f"Total = {c.amount_minted_all}" , "Amount": f"Total: {c.amount_held_all}"}
        data.append(amounts)
        keys = set().union(*(d.keys() for d in data))
        klen = len(keys)
        keysord = [None] * klen
        keysord[0] = "Name"
        keysord[1] = "Description"
        keysord[2] = "Owner"
        keysord[3] = "Amount"
        keysord[4] = "Amount Minted"
        keysord[5] = "Royalty Percentage"
        keysord[6] = "Metadata Cid"
        keysord[7] = "Image Cid"
        if klen != 8:
            i = 1
            p = 8
            while p < klen:
                keysord[p] = f"Trait {i}"
                keysord[p + 1] = f"Value {i}"
                p += 2
                i += 1
        try:
            with open(path, 'w', newline='', encoding="utf-8") as output_file:
                dict_writer = csv.DictWriter(output_file, keysord)
                dict_writer.writeheader()
                dict_writer.writerows(data)
                self.log_var.set(
            f"Your spreadsheet is in the MintTracker folder. \n Minted All: {c.amount_minted_all}, Held Mints: {c.amount_held_all}"
        )
        except PermissionError:
            self.log_var.set(
            f"Your spreadsheet might be open, close it, you have 100 seconds"
        )
            time.sleep(100)
            try:
                with open(path, 'w', newline='', encoding="utf-8") as output_file:
                    dict_writer = csv.DictWriter(output_file, keysord)
                    dict_writer.writeheader()
                    dict_writer.writerows(data)
                    self.log_var.set(
            f"Your spreadsheet is in the MintTracker folder. \n Minted All: {c.amount_minted_all}, Held Mints: {c.amount_held_all}"
        ) 
            except Exception:      
                self.log_var.set(
                f"You didn't close the spreadsheet in time. Or something went wrong. Restart"
            )

# Object for each nft
class MintedNft:
    def __init__(self, nft_data):
        self.nft = nft_data[0].replace("'", "")
        self.amount_minted = int(nft_data[1])
        holders = act.find_holders(self.nft)
        self.holders = holders
        cid = act.convert_cid(self.nft)
        self.cid = cid
        data = act.retrieve_data(self.nft, self.amount_minted, self.holders, self.cid, c.ATTRS)
        self.data = data


# run the app
def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
