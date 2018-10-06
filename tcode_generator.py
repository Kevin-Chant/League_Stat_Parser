from tkinter import simpledialog, Tk, Label, Entry, StringVar, OptionMenu, messagebox, END, Button
from tkinter import *
import pyperclip
from tournament import tournament_codes, get_matches_for_tcode
from db_access import upload_tcodes, get_match_history_links, get_formatted_tcodes
from os.path import isfile, isdir
from os import mkdir
from traceback import print_exc
import json
import webbrowser

from pyupdater.client import Client
from client_config import ClientConfig

APP_NAME = 'Tournament Code Generator'
APP_VERSION = '1.2.2'
ALL_LEAGUES = ["Rampage Open", "Dominate Open", "Rampage Premade", "Dominate Premade", "Champions"]

def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print(downloaded, total, status)

def generate_default_config():
    return {"Season": 5, "League": "Rampage Open", "Autoupdate": True}

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

def is_update_avail():
    client = Client(ClientConfig(), refresh=True,
                            progress_hooks=[print_status_info])

    app_update = client.update_check(APP_NAME, APP_VERSION)
    return app_update

def update():
    app_update = is_update_avail()
    app_update.download()
    if app_update.is_downloaded():
        app_update.extract_restart()
        messagebox.showinfo("Success", "The update is complete!")

config = load_config()

if config["Autoupdate"]:
    if is_update_avail():
        messagebox.showinfo("Update", "There is an update available. It will now be downloaded and installed.")
        update()



tournament_ids = {  "Rampage Open_5": 442892,
                    "Dominate Open_5": 442893,
                    "Rampage Premade_5": 442894,
                    "Dominate Premade_5": 442895,
                    "Champions_5": 442896
                }

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
        league_dropdown = OptionMenu(parent, self.league, *ALL_LEAGUES)
        
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

        self.uploadButton = Button(parent, text="Upload Single Code", command=self.upload_code_flow)
        self.configButton = Button(parent, text="Configure Settings and Keys", command=self.config_flow)

        self.getCodeButton = Button(parent, text="Get and Format Weekly Codes", command=self.get_code_flow)
        self.matchHistButton = Button(parent, text="Get Match History Links", command=self.match_hist_flow)

        self.updateButton = Button(parent, text="Check for updates", command=self.update_flow)

        self.multiCodeButton.grid(row=0,column=0)
        self.singleCodeButton.grid(row=0,column=1)

        self.configButton.grid(row=1,column=0)
        self.uploadButton.grid(row=1,column=1)

        self.getCodeButton.grid(row=2,column=1)
        self.matchHistButton.grid(row=2,column=0)
        
        self.updateButton.grid(row=3,column=0)
    
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
            game = self.single_code_game()
            if not game:
                return
            codes = self.get_tcodes(*d.result, game=game)
            formatted_codes = "\n".join([str(code) for code in codes])
            pyperclip.copy(formatted_codes)
            messagebox.showinfo("Tournament Codes", "The codes for " + d.result[0] + " v " + d.result[1] + " week " + d.result[2] + " are\n" + formatted_codes + "\nThey have been automatically copied to your clipboard.")
            d = MatchDialog(self, league=config["League"])

    def upload_code_flow(self, game=None):
        config = load_config()
        d = MatchDialog(self, league=config["League"],bestof=1)
        while True:
            if not d.result:
                return
            num_errs = error_check(self, *d.result)
            if num_errs > 0:
                d = MatchDialog(self, *d.result)
                continue

            game = self.single_code_game()
            if not game:
                return
            code = simpledialog.askstring("Input", "What is the code to upload?")
            if code:
                resp = messagebox.askyesno("Upload code?", "Are you sure you want to overwrite the code for game " + str(game) +"? This cannot be undone.")
                if resp:
                    try:
                        bteam, rteam, week, league, _ = d.result
                        metadata = {"League": league,
                                    "Season": load_config()["Season"],
                                    "Team1": bteam,
                                    "Team2": rteam,
                                    "Week": week
                                    }
                        upload_tcodes(metadata, [code], game=game)
                        messagebox.showinfo("Success!", "Code successfully uploaded to DB")
                    except Exception as e:
                        messagebox.showwarning("Warning", "The codes were unable to be automatically uploaded to the database. Please notify one of the staff members with DB access and provide the codes, teams, and week.")
                        messagebox.showinfo("Info", "Please provide this error information as well.\n" + str(e))
                        print_exc()
                return

    def match_hist_flow(self, event=None):
        d = HistoryDialog(self)
        if not d.result:
            return
        team, week, league = d.result
        messagebox.showinfo("Working", "Trying to find match history for games from " + team + "'s week " + str(week) + " match")
        try:
            links = get_match_history_links(league, week, team)
            if len(links) > 0:
                h = HistoryPopup(self, links)
            else:
                messagebox.showwarning("404", "There are no links for those tournament codes")
        except Exception as e:
            messagebox.showerror("Error", "Unable to get requested links\n" + str(e))

    def get_code_flow(self, event=None):
        d = CodeFetchDialog(self)
        if not d.result:
            return
        week, league = d.result
        messagebox.showinfo("Working", "Will get all tournament codes for " + league + " week " + str(week))
        try:
            codes = get_formatted_tcodes(league, week)
            pyperclip.copy(codes)
            messagebox.showinfo("Done", "Successfully got codes and copied the formatted output to your clipboard")
        except Exception as e:
            messagebox.showerror("Error", "Unable to get requested codes\n" + str(e))

    def update_flow(self, event=None):
        if is_update_avail():
            messagebox.showinfo("Update", "There is an update available. It will now be downloaded and installed.")
            update()
        else:
            messagebox.showinfo("Success", "Already up to date!")

    def single_code_game(self):
        cud = CodeUploadDialog(self)
        game = cud.result
        if not game:
            return None
        # Error check
        try:
            game = int(game)
            if not game in range(1,6):
                messagebox.showerror("Error", "Game should be a number 1-5")
            else:
                return game
        except:
            messagebox.showerror("Error", "Game should be a number 1-5")

    def get_tcodes(self, bteam, rteam, week, league, bo, game=None):
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
                if game:
                    code = tournament_codes(tid, 1, [g2_metadata, metadata][game % 2])[0]
                elif i % 2 == 0:
                    code = tournament_codes(tid, 1, metadata)[0]
                else:
                    code = tournament_codes(tid, 1, g2_metadata)[0]
                codes.append(code)
            try:
                upload_tcodes(metadata, codes, game=game)
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
        self.league.set(load_config()["League"]) # initial value
        if self.leagueval:
            self.league.set(self.leagueval)
        league_dropdown = OptionMenu(master, self.league, *ALL_LEAGUES)

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

class HistoryDialog(simpledialog.Dialog):

    def __init__(self, parent, team=None, week=None, league=None):
        self.teamval = team
        self.weekval = week
        self.leagueval = league

        super(HistoryDialog, self).__init__(parent)

    def body(self, master):

        Label(master, text="Team:").grid(row=0,column=0)
        Label(master, text="Week:").grid(row=1,column=0)

        self.team = Entry(master)
        self.week = Entry(master)

        if self.teamval:
            self.team.insert(END, self.teamval)
        if self.weekval:
            self.week.insert(END, self.weekval)

        self.league = StringVar(master)
        self.league.set(load_config()["League"]) # initial value
        if self.leagueval:
            self.league.set(self.leagueval)
        league_dropdown = OptionMenu(master, self.league, *ALL_LEAGUES)

        self.team.grid(row=0, column=1)
        self.week.grid(row=1, column=1)
        league_dropdown.grid(row=2, column=1)
        return self.team # initial focus

    def apply(self):
        team = self.team.get()
        week = self.week.get()
        league = self.league.get()

        self.result = (team,week,league)

class CodeFetchDialog(simpledialog.Dialog):
    def __init__(self, parent, week=None, league=None):
        self.weekval = week
        self.leagueval = league

        super(CodeFetchDialog, self).__init__(parent)

    def body(self, master):

        Label(master, text="Week:").grid(row=0,column=0)

        self.week = Entry(master)

        if self.weekval:
            self.week.insert(END, self.weekval)

        self.league = StringVar(master)
        self.league.set(load_config()["League"]) # initial value
        if self.leagueval:
            self.league.set(self.leagueval)
        league_dropdown = OptionMenu(master, self.league, *ALL_LEAGUES)

        self.week.grid(row=0, column=1)
        league_dropdown.grid(row=1, column=1)
        return self.week # initial focus

    def apply(self):
        week = self.week.get()
        league = self.league.get()

        self.result = (week,league)

class HistoryPopup(simpledialog.Dialog):
    def __init__(self, parent, links):
        self.links = links

        super(HistoryPopup, self).__init__(parent)

    def body(self, master):
        g1 = Button(master, text="Game 1", command=lambda event=None:webbrowser.open_new(self.links[0]))
        g1.grid(row=0)

        if len(self.links) > 1:
            g2 = Button(master, text="Game 2", command=lambda event=None:webbrowser.open_new(self.links[1]))
            g2.grid(row=1)

        if len(self.links) > 2:
            g3 = Button(master, text="Game 3", command=lambda event=None:webbrowser.open_new(self.links[2]))
            g3.grid(row=2)

        if len(self.links) > 3:
            g4 = Button(master, text="Game 4", command=lambda event=None:webbrowser.open_new(self.links[3]))
            g4.grid(row=3)

        if len(self.links) > 4:
            g5 = Button(master, text="Game 5", command=lambda event=None:webbrowser.open_new(self.links[4]))
            g5.grid(row=4)


def setup_flow(parent):
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

    if not isdir(".cache/"):
        mkdir(".cache/")

    if not isdir(".cache/tournament_matches/"):
        mkdir(".cache/tournament_matches/")

def error_check(root, bteam, rteam, week, league, bo):
    numerrors = 0
    if not len(bteam) in [1,2,3,4,5]:
        messagebox.showerror("Error", "The blue team should be the 1-5 letter team acronym.")
        numerrors += 1
    if not len(rteam) in [1,2,3,4,5]:
        messagebox.showerror("Error", "The red team should be the 1-5 letter team acronym.")
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