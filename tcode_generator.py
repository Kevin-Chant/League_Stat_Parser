from tkinter import simpledialog, Tk, Label, Entry, StringVar, OptionMenu, messagebox, END, Button
from tkinter import *
import pyperclip
from tournament import load_tournament_key, tournament_codes
from db_access import upload_tcodes
from os.path import isfile
from traceback import print_exc
import json

from pyupdater.client import Client
from client_config import ClientConfig

APP_NAME = 'Tournament Code Generator'
APP_VERSION = '1.0.3'

def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print(downloaded, total, status)

def generate_default_config():
    return {"Season": 4, "League": "Rampage", "Autoupdate": False}

def store_config(config):
    config_file = open("config.json", "w")
    json.dump(config, config_file)

def load_config():
    try:
        config_file = open("config.json", "r")
        config = json.load(config_file)
    except:
        config_file = open("config.json", "w")
        config = generate_default_config()
        json.dump(config, config_file)
    return config

config = load_config()

if config["Autoupdate"]:
    print("Checking for autoupdate")
    client = Client(ClientConfig())
    print(client)
    client.refresh()

    client.add_progress_hook(print_status_info)

    client = Client(ClientConfig(), refresh=True,
                            progress_hooks=[print_status_info])

    app_update = client.update_check(APP_NAME, APP_VERSION)
    print("App update is", app_update)

    if app_update is not None:
        app_update.download()
        if app_update.is_downloaded():
            app_update.extract_restart()



tournament_ids = {  "Rampage_4": 393536,
                    "Dominate_4": 393545,
                    "Alumnus_4": 393546,
                    "Champions_4": 393547}

CONFIG_KEYS = ["Season", "League", "Autoupdate"]

class ConfigInfo(simpledialog.Dialog):
    def __init__(self, parent, config):
        self.prev_config = config
        super(ConfigInfo, self).__init__(parent)


    def body(self, parent):

        self.season_entry = Entry(parent)
        self.season_entry.insert(END, self.prev_config["Season"])

        self.league = StringVar(parent)
        self.league.set(self.prev_config["League"])
        league_dropdown = OptionMenu(parent, self.league, "Rampage", "Dominate", "Alumnus", "Champions")
        
        self.autoupdate = BooleanVar()
        self.autoupdate.set(self.prev_config["Autoupdate"])
        autoupdate_checkbox = Checkbutton(parent, text="", variable=self.autoupdate)

        Label(parent, text="Season").grid(row=0,column=0)
        self.season_entry.grid(row=0,column=1)

        Label(parent, text="League").grid(row=1,column=0)
        league_dropdown.grid(row=1,column=1)

        Label(parent, text="Autoupdate").grid(row=2,column=0)
        autoupdate_checkbox.grid(row=2,column=1)

        return league_dropdown

    def apply(self):
        season = self.season_entry.get()
        try:
            s = int(season)
            if s < 4:
                messagebox.showerror("Error", "Cannot have season before 4")
                return
        except:
            messagebox.showerror("Error", "Season must be a number")
            return
        new_config = {  "Season": int(season),
                        "League": self.league.get(),
                        "Autoupdate": self.autoupdate.get()
                        }
        if new_config != self.prev_config:
            if messagebox.askyesno("Save Changes?", "You have made changes, save new config?"):
                self.result = new_config
            else:
                self.result = None
        else:
            self.result = None


class CodeUploadDialog(simpledialog.Dialog):

    def body(self, parent):
        Label(parent, text="Enter the game of the series this code is being generated to replace.\nIf you don't know, press cancel and upload this code manually later.").grid(row=0,columnspan=2)

        Label(parent, text="Game number:").grid(row=1, column=0)
        self.game = Entry(parent)
        self.game.grid(row=1, column=1)

        return self.game

    def apply(self):
        self.result = self.game.get()

class MenuDialog(simpledialog.Dialog):

    def body(self, parent):
        self.multiCodeButton = Button(parent, text="Generate Weekly Codes", command=self.weekly_code_flow)
        self.singleCodeButton = Button(parent, text="Generate Single Code", command=self.single_code_flow)

        self.uploadButton = Button(parent, text="Upload Single Codes", command=self.upload_code_flow)
        self.configButton = Button(parent, text="Configure Settings and Keys", command=self.config_flow)

        self.updateButton = Button(parent, text="Self Update (coming soon)", command=self.update_flow)

        self.multiCodeButton.grid(row=0,column=0)
        self.singleCodeButton.grid(row=0,column=1)

        self.configButton.grid(row=1,column=0)
        self.uploadButton.grid(row=1,column=1)
        
        self.updateButton.grid(row=2,column=1)
    
    def apply(self):
        self.result = None

    def config_flow(self, event=None):
        config = load_config()
        i = ConfigInfo(self.parent, config)
        if i.result:
            store_config(i.result)

    def weekly_code_flow(self, event=None):
        config = load_config()
        d = MatchDialog(self, league=config["League"])
        while True:
            if not d.result:
                return
            num_errs = error_check(self, *d.result)
            if num_errs > 0:
                d = MatchDialog(self, *d.result)
                continue
            codes = self.get_tcodes(*d.result)
            formatted_codes = "\n".join([str(code) for code in codes])
            pyperclip.copy(formatted_codes)
            messagebox.showinfo("Tournament Codes", "The codes for " + d.result[0] + " v " + d.result[1] + " week " + d.result[2] + " are\n" + formatted_codes + "\nThey have been automatically copied to your clipboard.")
            d = MatchDialog(self, league=config["League"])

    def single_code_flow(self, event=None):
        config = load_config()
        d = MatchDialog(self, league=config["League"], bestof=1)
        while True:
            if not d.result:
                return
            num_errs = error_check(self, *d.result)
            if num_errs > 0:
                d = MatchDialog(self, *d.result)
                continue
            codes = self.get_tcodes(*d.result)
            formatted_codes = "\n".join([str(code) for code in codes])
            pyperclip.copy(formatted_codes)
            messagebox.showinfo("Tournament Codes", "The codes for " + d.result[0] + " v " + d.result[1] + " week " + d.result[2] + " are\n" + formatted_codes + "\nThey have been automatically copied to your clipboard.")
            d = MatchDialog(self, league=config["League"])

    def upload_code_flow(self, event=None):
        config = load_config()
        d = MatchDialog(self, league=config["League"],bestof=1)
        while True:
            if not d.result:
                return
            num_errs = error_check(self, *d.result)
            if num_errs > 0:
                d = MatchDialog(self, *d.result)
                continue
            else:
                break
        code = simpledialog.askstring("Input", "What is the code to upload?")
        if code:
            bteam, rteam, week, league, _ = d.result
            metadata = {"League": league,
                        "Season": load_config()["Season"],
                        "Team1": bteam,
                        "Team2": rteam,
                        "Week": week
                        }
            if self.upload_single_code(metadata, [code]):
                messagebox.showinfo("Success!", "Code successfully uploaded to DB")


    def update_flow(self, event=None):
        print("Update triggered")
        print("This button might go away soon")


    def upload_single_code(self, metadata, codes):
        while True:
            d = CodeUploadDialog(self)
            game = d.result
            if not game:
                return

            # Error check
            try:
                game = int(game)
                if not game in range(1,6):
                    messagebox.showerror("Error", "Game should be a number 1-5")
                else:
                    resp = messagebox.askyesno("Upload code?", "Are you sure you want to overwrite the code for game " + str(game) +"? This cannot be undone.")
                    if resp:
                        try:
                            upload_tcodes(metadata, codes, game=game)
                            return True
                        except Exception as e:
                            messagebox.showwarning("Warning", "The codes were unable to be automatically uploaded to the database. Please notify one of the staff members with DB access and provide the codes, teams, and week.")
                            messagebox.showinfo("Info", "Please provide this error information as well.\n" + str(e))
                            print_exc()
                    return
            except:
                messagebox.showerror("Error", "Game should be a number 1-5")


    def get_tcodes(self, bteam, rteam, week, league, bo):
        season = load_config()["Season"]
        metadata = {"League": league,
                    "Season": season,
                    "Team1": bteam,
                    "Team2": rteam,
                    "Week": week
                    }
        g2_metadata = { "League": league,
                        "Season": season,
                        "Team1": rteam,
                        "Team2": bteam,
                        "Week": week
                        }
        tid = tournament_ids[league + "_" + str(season)]
        if tid:
            codes = []
            for i in range(bo):
                if i % 2 == 0:
                    code = tournament_codes(tid, 1, metadata)[0]
                else:
                    code = tournament_codes(tid, 1, g2_metadata)[0]
                codes.append(code)
            try:
                if len(codes) == 1:
                    self.upload_single_code(metadata, codes)
                else:
                    upload_tcodes(metadata, codes)
            except Exception as e:
                messagebox.showwarning("Warning", "The codes were unable to be automatically uploaded to the database. Please notify one of the staff members with DB access and provide the codes, teams, and week.")
                messagebox.showinfo("Info", "Please provide this error information as well.\n" + str(e))
                print_exc()
            return codes
        else:
            messagebox.showerror("Error", "The tournament for " + league + ", Season " + str(season) + " has not yet been initialized. Please create the tournament and store the ID in this program.")
            exit(0)


class MatchDialog(simpledialog.Dialog):

    def __init__(self, parent, bteam=None, rteam=None, week=None, league=None, bestof=None):
        self.bteamval = bteam
        self.rteamval = rteam
        self.weekval = week
        self.leagueval = league
        self.boval = bestof

        super(MatchDialog, self).__init__(parent)

    def body(self, master):

        Label(master, text="Blue Team:").grid(row=0, column=0)
        Label(master, text="Red Team:").grid(row=0, column=2)
        Label(master, text="Week:").grid(row=1, column=1)
        Label(master, text="League:").grid(row=2, column=1)
        Label(master, text="Best of:").grid(row=3, column=1)

        self.bteam = Entry(master)
        self.rteam = Entry(master)
        self.week = Entry(master)

        if self.bteamval:
            self.bteam.insert(END, self.bteamval)
        if self.rteamval:
            self.rteam.insert(END, self.rteamval)
        if self.weekval:
            self.week.insert(END, self.weekval)

        self.league = StringVar(master)
        self.league.set("Rampage") # initial value
        if self.leagueval:
            self.league.set(self.leagueval)
        league_dropdown = OptionMenu(master, self.league, "Rampage", "Dominate", "Alumnus", "Champions")

        self.bo = IntVar(master)
        self.bo.set(3) # initial value
        if self.boval:
            self.bo.set(self.boval)
        bo_dropdown = OptionMenu(master, self.bo, 1, 3, 5)            

        self.bteam.grid(row=0, column=1)
        self.rteam.grid(row=0, column=3)
        self.week.grid(row=1, column=2)
        league_dropdown.grid(row=2, column=2)
        bo_dropdown.grid(row=3, column=2)
        return self.bteam # initial focus

    def apply(self):
        bteam = self.bteam.get()
        rteam = self.rteam.get()
        week = self.week.get()
        league = self.league.get()
        bo = self.bo.get()

        self.result = (bteam,rteam,week,league,bo)

def setup_flow(parent):
    if not isfile("tournament_key.txt"):
        tkey = simpledialog.askstring("Input", "Please enter the tournament API key", parent=parent)
        if not tkey:
            messagebox.showwarning("Warning", "Tournament API key not entered, exiting program.")
            exit(0)
        localsave = messagebox.askyesno("Question", "Do you want this program to save the tournament API key locally? If you choose yes, take special care not to give tournament_key.txt to anyone.") 
        if localsave:
            with open("tournament_key.txt", "w") as f:
                f.write(tkey)
                f.close()

    if not isfile("db_pass.txt"):
        db_pass = simpledialog.askstring("Input", "Please enter the database password", parent=parent)
        if not db_pass:
            messagebox.showwarning("Warning", "Password not entered, exiting program.")
            exit(0)
        localsave = messagebox.askyesno("Question", "Do you want this program to save the database password locally? If you choose yes, take special care not to give db_pass.txt to anyone.")
        if localsave:
            with open("db_pass.txt", "w") as f:
                f.write(db_pass)
                f.close()


def error_check(root, bteam, rteam, week, league, bo):
    numerrors = 0
    if not len(bteam) in [1,2,3,4]:
        messagebox.showerror("Error", "The blue team should be the 1-4 letter team acronym.")
        numerrors += 1
    if not len(rteam) in [1,2,3,4]:
        messagebox.showerror("Error", "The red team should be the 1-4 letter team acronym.")
        numerrors += 1
    try:
        w = int(week)
        if w < -1 or w > 17:
            messagebox.showerror("Error", "Week should be the numbered week of the season between -1 (playins) and 17 (playoff finals)")
            numerrors += 1
    except:
        messagebox.showerror("Error", "Week should just be a number, e.g. 5")
        numerrors += 1
    return numerrors


def main():
    root = Tk()
    root.winfo_toplevel().title("Tournament Code Generator V " + str(APP_VERSION))
    root.withdraw()
    setup_flow(root)
    d = MenuDialog(root)

if __name__ == '__main__':
    main()