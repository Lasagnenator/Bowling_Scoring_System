import Frames
import wx

buttonList = []
playerList = []

CurrentPlayer = 0
CurrentFrame = 1
CurrentBowl = 1

ScoreToText= {0:"-",
              1:"1",
              2:"2",
              3:"3",
              4:"4",
              5:"5",
              6:"6",
              7:"7",
              8:"8",
              9:"9",
              10:"X",
              11:"/"}

TextToScore= {"":0,
              "-":0,
              "1":1,
              "2":2,
              "3":3,
              "4":4,
              "5":5,
              "6":6,
              "7":7,
              "8":8,
              "9":9,
              "X":10,
              "/":11}

class ValidScores():
    Miss = 0
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Strike = 10
    Spare = 11

def SelectPlayer(number):
    return playerList[number]

def SelectFrame(panel, num):
    return eval("panel.Frame{}".format(num))

def SelectBowl(player, frame, bowl):
    return eval("playerList[{}].Frame{}.Bowl{}".format(player, frame, bowl))

class mainWindow(Frames.MainFrame):
    def __init__(self, parent):
        global buttonList
        global playerList
        global CurrentPlayer, CurrentFrame, CurrentBowl, TotalPlayers
        Frames.MainFrame.__init__(self, parent)
        buttonList = [self.m_radioBtn1,self.m_radioBtn2,self.m_radioBtn3,self.m_radioBtn4,self.m_radioBtn5,self.m_radioBtn6,self.m_radioBtn7,self.m_radioBtn8,self.m_radioBtn9,self.m_radioBtn10,self.m_radioBtn11,self.m_radioBtn12]
        playerList = [self.PlayerPanel1,self.PlayerPanel2,self.PlayerPanel3,self.PlayerPanel4,self.PlayerPanel5,self.PlayerPanel6]
        TotalPlayers = len(playerList)
        buttonList[11].Enable(False)

    def EnterScore(self, event):
        global buttonList
        #this lets us iterate over the buttons but not have to increment a counter as
        #automatically does this for us
        for i, button in enumerate(buttonList):
            if button.GetValue():
                AddScore(i)

def AddScore(Score):
    global CurrentPlayer, CurrentFrame, CurrentBowl
    DisplayScores(Score)
    if Score==10 and CurrentFrame!=10:
        CurrentBowl += 1
    CalculateSubTotals()
    DisplayTotals()
    UpdatePlayer(CurrentPlayer, Score)
    UpdateButtons(Score)
    CheckFrame()

def DisplayScores(Score):
    global CurrentPlayer, CurrentFrame, CurrentBowl
    SelectBowl(CurrentPlayer, CurrentFrame, CurrentBowl).Value = ScoreToText[Score]

def CalculateSubTotals():
    global CurrentPlayer, CurrentFrame, CurrentBowl
    for i in range(1, CurrentFrame+1):
        Subtotal = 0
        if i == 10: #Frame10
            b1 = TextToScore[SelectBowl(CurrentPlayer, i, 1).Value]
            b2 = TextToScore[SelectBowl(CurrentPlayer, i, 2).Value]
            b3 = TextToScore[SelectBowl(CurrentPlayer, i, 3).Value]
            b4 = b5 = 0
        elif i == 9:
            b1 = TextToScore[SelectBowl(CurrentPlayer, i, 1).Value]
            b2 = TextToScore[SelectBowl(CurrentPlayer, i, 2).Value]
            b3 = TextToScore[SelectBowl(CurrentPlayer, i+1, 1).Value]
            b4 = TextToScore[SelectBowl(CurrentPlayer, i+1, 2).Value]
            b5 = TextToScore[SelectBowl(CurrentPlayer, i+1, 3).Value]
        else:
            b1 = TextToScore[SelectBowl(CurrentPlayer, i, 1).Value]
            b2 = TextToScore[SelectBowl(CurrentPlayer, i, 2).Value]
            b3 = TextToScore[SelectBowl(CurrentPlayer, i+1, 1).Value]
            b4 = TextToScore[SelectBowl(CurrentPlayer, i+1, 2).Value]
            b5 = TextToScore[SelectBowl(CurrentPlayer, i+2, 1).Value]
        #print(b1, b2, b3, b4, b5)
        if i==10: #frame 10
            if ((b1 == b2) and (b2 == ValidScores.Strike)): #b1=b2=strike
                Subtotal = b1 + b2 + b3
                #Subtotal = b1 + (2 * b2) + (3 * b3)
            elif (b1 == ValidScores.Strike) and (b3 == ValidScores.Spare):
                Subtotal = b1 + 20
            elif b1 == ValidScores.Strike:
                Subtotal = b1 + (2 * (b2 + b3))
            elif b2 == ValidScores.Spare:
                Subtotal = 10 + (2 * b3)
            else:
                Subtotal = b1 + b2
        else:
            if (b1 == b3) and (b3 == b4) and (b4 == ValidScores.Strike):
                Subtotal = b1 + b3 + b4
            elif (b1 == b3) and (b3 == ValidScores.Strike):
                Subtotal = b1 + b3 + b5
            elif (b1 == ValidScores.Strike) and (b4 == ValidScores.Spare):
                Subtotal = b1 + 10
            elif (b1 == ValidScores.Strike):
                Subtotal = b1 + b3 + b4
            elif (b2 == ValidScores.Spare):
                Subtotal = 10 + b3
            else:
                Subtotal = b1+b2
        #print(Subtotal)
        DisplaySubTotals(Subtotal, i)
        #print("here")

PreviousSubTotals = [0]*10

def DisplaySubTotals(Subtotal, Frame):
    global PreviousSubTotals
    PreviousSubTotals[Frame-1] = Subtotal
    #print(PreviousSubTotals)
    for s in PreviousSubTotals[:Frame-1]:
        Subtotal += s
    SelectFrame(SelectPlayer(CurrentPlayer), Frame).SubTotal.Value = str(Subtotal)

def DisplayTotals():
    global PreviousSubTotals
    total = 0
    for score in PreviousSubTotals:
        total += score
    SelectPlayer(CurrentPlayer).Total.Value = str(total)
    
def UpdatePlayer(player, Score):
    global CurrentPlayer, CurrentFrame, CurrentBowl
    CurrentBowl += 1
    if ((Score == ValidScores.Strike) and (not (CurrentBowl == 4))) or (CurrentBowl == 3):
        if not ((CurrentFrame == 10) and (EarnedFrame10())):
            IncrementNextPlayer()
    elif not CurrentBowl == 2:
        IncrementNextPlayer()

def IncrementNextPlayer():
    global CurrentPlayer, CurrentFrame, CurrentBowl
    CurrentBowl = 1
    CurrentPlayer += 1

def EarnedFrame10():
    t1 = TextToScore[SelectBowl(CurrentPlayer, 10, 1).Value] == ValidScores.Strike
    t2 = TextToScore[SelectBowl(CurrentPlayer, 10, 2).Value] == ValidScores.Spare
    return t1 or t2

def UpdateButtons(score):
    for button in buttonList:
        button.Enable(True)
    if (CurrentBowl == 1) or (score == ValidScores.Strike) or (score == ValidScores.Spare):
        buttonList[11].Enable(False)
        if buttonList[11].GetValue():
            buttonList[11].SetValue(False)
    else:
        for i in range(11):
            if i>=10-score:
                buttonList[i].Enable(False)
                if buttonList[i].GetValue():
                    buttonList[i].SetValue(False)
    
def CheckFrame():
    global CurrentPlayer, CurrentFrame, CurrentBowl
    if CurrentPlayer >= TotalPlayers:
        CurrentPlayer = 0
        CurrentFrame += 1
    if CurrentFrame > 10:
        for button in buttonList:
            button.SetValue(False)
            button.Enable(False)
        m.EnterButton.Enable(False)
        #end game

app = wx.App()
m = mainWindow(None)
m.Show(True)
app.MainLoop()