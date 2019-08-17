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

def AddScore(Score):
    global CurrentPlayer, CurrentFrame, CurrentBowl
    DisplayScores(Score)
    if Score==ValidScores.Strike and CurrentFrame!=10:
        CurrentBowl += 1
        DisplayScores(0)
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
                #home bowling goes up to 330.
                Subtotal = b1 + (2 * b2) + (3 * b3)
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
    #automatically scroll to next player
    sign = int(CurrentPlayer>0)*2-1
    main.m_scrolledWindow2.Scroll(-1, 20*(CurrentPlayer%TotalPlayers-4)*sign)

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
            buttonList[0].SetValue(True)
            buttonList[0].SetFocus()
    else:
        for i in range(11):
            if i>=10-score:
                buttonList[i].Enable(False)
                if buttonList[i].GetValue():
                    buttonList[i].SetValue(False)
                    buttonList[0].SetValue(True)
                    buttonList[0].SetFocus()
    
def CheckFrame():
    global CurrentPlayer, CurrentFrame, CurrentBowl
    if CurrentPlayer >= TotalPlayers:
        CurrentPlayer = 0
        CurrentFrame += 1
    if CurrentFrame > 10:
        for button in buttonList:
            button.SetValue(False)
            button.Enable(False)
        main.EnterButton.Enable(False)
        EndGame()

def EndGame():
    GameOver = GameOverDialog(None)
    GameOver.Report.AppendColumn("Rank")
    GameOver.Report.AppendColumn("Name")
    GameOver.Report.AppendColumn("Score")
    p = sorted(playerList, reverse=True, key = lambda x:x.Total.Value)
    for rank, panel in enumerate(p, start = 1):
        GameOver.Report.Append([rank, panel.PlayerNameTextBox.Value, panel.Total.Value])
    GameOver.Report.SetColumnWidth(0, -2)
    GameOver.Report.SetColumnWidth(1, -1)
    GameOver.Report.SetColumnWidth(2, -2)
    GameOver.ShowModal()

NumberOfPlayers = 0

early_exit = False
class NumberOfPlayersFrame(Frames.NumberOfPlayers):
    def __init__(self, parent):
        Frames.NumberOfPlayers.__init__(self, parent)
    def OkButtonClicked(self, event):
        global NumberOfPlayers
        NumberOfPlayers = self.PlayerNums.Value
        self.Show(False)
    def OnClose(self, event):
        global early_exit
        early_exit = True
        self.Show(False)

class mainWindow(Frames.MainFrame):
    def __init__(self, parent):
        global buttonList
        global playerList
        global CurrentPlayer, CurrentFrame, CurrentBowl, TotalPlayers
        Frames.MainFrame.__init__(self, parent)
        buttonList = [self.m_radioBtn1,self.m_radioBtn2,self.m_radioBtn3,self.m_radioBtn4,self.m_radioBtn5,self.m_radioBtn6,self.m_radioBtn7,self.m_radioBtn8,self.m_radioBtn9,self.m_radioBtn10,self.m_radioBtn11,self.m_radioBtn12]
        #playerList = [self.PlayerPanel1,self.PlayerPanel2,self.PlayerPanel3,self.PlayerPanel4,self.PlayerPanel5,self.PlayerPanel6]
        buttonList[11].Enable(False)
        buttonList[0].SetFocus()

    def EnterScore(self, event):
        global buttonList
        #this lets us iterate over the buttons but not have to increment a counter as
        #automatically does this for us
        for i, button in enumerate(buttonList):
            if button.GetValue():
                AddScore(i)

    def OnShow(self, event):
        global NumberOfPlayers
        global playerList, TotalPlayers
        for i in range(NumberOfPlayers):
            playerList.append(Frames.PlayerPanel( self.m_scrolledWindow2, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,90 ), wx.BORDER_NONE|wx.TAB_TRAVERSAL ))
            self.bSizer8.Add( playerList[-1], 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.EXPAND, 5 )
            playerList[-1].PlayerNameTextBox.Value = "Player {}".format(i+1)
        TotalPlayers = len(playerList)
        #print(TotalPlayers)

    def OnKeyDown(self, event):
        key = event.GetUnicodeKey()
        #print(key)
        if key==48 or key==45: #0 or - for miss
            buttonList[0].SetValue(True if buttonList[0].Enabled==True else False)
        elif key==49:
            buttonList[1].SetValue(True if buttonList[1].Enabled==True else False)
        elif key==50:
            buttonList[2].SetValue(True if buttonList[2].Enabled==True else False)
        elif key==51:
            buttonList[3].SetValue(True if buttonList[3].Enabled==True else False)
        elif key==52:
            buttonList[4].SetValue(True if buttonList[4].Enabled==True else False)
        elif key==53:
            buttonList[5].SetValue(True if buttonList[5].Enabled==True else False)
        elif key==54:
            buttonList[6].SetValue(True if buttonList[6].Enabled==True else False)
        elif key==55:
            buttonList[7].SetValue(True if buttonList[7].Enabled==True else False)
        elif key==56:
            buttonList[8].SetValue(True if buttonList[8].Enabled==True else False)
        elif key==57:
            buttonList[9].SetValue(True if buttonList[9].Enabled==True else False)
        elif key==88: #x key
            buttonList[10].SetValue(True if buttonList[10].Enabled==True else False)
        elif key==47:
            buttonList[11].SetValue(True if buttonList[11].Enabled==True else False)
        elif key==13:
            #process enter key
            self.EnterScore(None)

    def GenerateReport(self, event):
        EndGame()
    def ExitProgram(self, event):
        import sys
        sys.exit()

class GameOverDialog(Frames.GameOverDialog):
    def __init__(self, parent):
        Frames.GameOverDialog.__init__(self, parent)
    def SaveFile(self, event):
        text = ""
        text += """name,f1b1,f1b2,f2b1,f2b2,f3b1,f3b2,f4b1,f4b2,f5b1,f5b2,f6b1,f6b2,f7b1,f7b2,f8b1,f8b2,f9b1,f9b2,f10b1,f10b2,f10b3\n"""
        for i, player in enumerate(playerList):
            text += """{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},
""".format(player.PlayerNameTextBox.Value,
           *[SelectBowl(i,b//2+1, b%2+1).Value for b in range(0,19)],
           *[SelectBowl(i,10,b).Value for b in [1,2,3]])
        #print(text)
        with open(self.FilePick.Path, "w") as f:
            f.write(text)

app = wx.App()
main = mainWindow(None)
PlayerNumbers = NumberOfPlayersFrame(main)
PlayerNumbers.ShowModal()
PlayerNumbers.Show(False)
if not early_exit:
    main.Show(True)
    app.MainLoop()
