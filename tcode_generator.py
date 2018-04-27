from tkinter import simpledialog, Tk, Label, Entry, StringVar, OptionMenu, messagebox, END
import pyperclip

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
        league_dropdown = OptionMenu(master, self.league, "Rampage", "Dominate", "Alumnus", "Champion's League")

        self.bo = StringVar(master)
        self.bo.set("3") # initial value
        if self.boval:
            self.bo.set(self.boval)
        bo_dropdown = OptionMenu(master, self.bo, "3", "5")

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

def get_tcodes(bteam, rteam, week, league, bo):
    return [1,2,3]

def error_check(root, bteam, rteam, week, league, bo):
    numerrors = 0
    if not len(bteam) in [2,3]:
        messagebox.showerror("Error", "The blue team should be the 2 or 3 letter team acronym.")
        numerrors += 1
    if not len(rteam) in [2,3]:
        messagebox.showerror("Error", "The red team should be the 2 or 3 letter team acronym.")
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



done = False
root = Tk()
root.withdraw()
d = MatchDialog(root)
while not done:
    if not d.result:
        exit(0)
    ne = error_check(root, *d.result)
    print(d.result)
    if ne > 0:
        d = MatchDialog(root, *d.result)
        continue
    codes = get_tcodes(*d.result)
    print(codes)
    formatted_codes = "\n".join([str(code) for code in codes])
    pyperclip.copy(formatted_codes)
    messagebox.showinfo("Tournament Codes", "The codes for " + d.result[0] + " v " + d.result[1] + " week " + d.result[2] + " are\n" + formatted_codes + "\nThey have been automatically copied to your clipboard.")
    done = True