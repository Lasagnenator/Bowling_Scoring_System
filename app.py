import Frames
import wx

buttonList = []
playerList = []

#zero indexed player
CurrentPlayer = 0
CurrentFrame = 1
CurrentBowl = 1

#these dictionaries are for conversion between text displayed and internal representation
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

#this just makes score testing readable later on.
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
    #main function to be called when enter button clicked
    global CurrentPlayer, CurrentFrame, CurrentBowl

    #un-highlight the current player
    SelectPlayer(CurrentPlayer).PlayerNameTextBox.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
    
    DisplayScores(Score)
    if Score==ValidScores.Strike and CurrentFrame!=10:
        CurrentBowl += 1
        DisplayScores(0)
    CalculateSubTotals()
    DisplayTotals()
    UpdatePlayer(CurrentPlayer, Score)
    UpdateButtons(Score)
    CheckFrame()

    #highlight the next player's turn
    SelectPlayer(CurrentPlayer).PlayerNameTextBox.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )

def DisplayScores(Score):
    #updates the textbox for the latest score
    global CurrentPlayer, CurrentFrame, CurrentBowl
    SelectBowl(CurrentPlayer, CurrentFrame, CurrentBowl).Value = ScoreToText[Score]

def CalculateSubTotals():
    #this handles every case for the scores
    global CurrentPlayer, CurrentFrame, CurrentBowl
    for i in range(1, CurrentFrame+1):
        Subtotal = 0
        if i == 10: #Frame10
            b1 = TextToScore[SelectBowl(CurrentPlayer, i, 1).Value]
            b2 = TextToScore[SelectBowl(CurrentPlayer, i, 2).Value]
            b3 = TextToScore[SelectBowl(CurrentPlayer, i, 3).Value]
            b4 = b5 = 0
        elif i == 9: #Frame 9
            b1 = TextToScore[SelectBowl(CurrentPlayer, i, 1).Value]
            b2 = TextToScore[SelectBowl(CurrentPlayer, i, 2).Value]
            b3 = TextToScore[SelectBowl(CurrentPlayer, i+1, 1).Value] #i+1 means the next frame
            b4 = TextToScore[SelectBowl(CurrentPlayer, i+1, 2).Value]
            b5 = TextToScore[SelectBowl(CurrentPlayer, i+1, 3).Value]
        else:
            b1 = TextToScore[SelectBowl(CurrentPlayer, i, 1).Value]
            b2 = TextToScore[SelectBowl(CurrentPlayer, i, 2).Value]
            b3 = TextToScore[SelectBowl(CurrentPlayer, i+1, 1).Value]
            b4 = TextToScore[SelectBowl(CurrentPlayer, i+1, 2).Value]
            b5 = TextToScore[SelectBowl(CurrentPlayer, i+2, 1).Value] #i+2 means the frame after next
        #print(b1, b2, b3, b4, b5)
        if i==10: #frame 10 special cases
            if ((b1 == b2) and (b2 == ValidScores.Strike)): #b1=b2=strike
                #home bowling goes up to 330.
                Subtotal = b1 + (2 * b2) + (3 * b3)
            elif (b1 == ValidScores.Strike) and (b3 == ValidScores.Spare): #b1=strike and b2=spare
                Subtotal = b1 + 20 #because spares are represented as 11
            elif b1 == ValidScores.Strike: #b1=strike
                Subtotal = b1 + (2 * (b2 + b3))
            elif b2 == ValidScores.Spare: #b2=spare
                Subtotal = 10 + (2 * b3) #again because spares are represented as 11
            else: #no spare or strike
                Subtotal = b1 + b2
        else: #all other frames have the same cases
            if (b1 == b3) and (b3 == b4) and (b4 == ValidScores.Strike): #frame 9 all strikes
                Subtotal = b1 + b3 + b4
            elif (b1 == b3) and (b3 == ValidScores.Strike): #b1=b3=strike
                Subtotal = b1 + b3 + b5
            elif (b1 == ValidScores.Strike) and (b4 == ValidScores.Spare): #b1=strike and b4=spare
                Subtotal = b1 + 10 #spare is counted as 11
            elif (b1 == ValidScores.Strike): #b1=strike
                Subtotal = b1 + b3 + b4
            elif (b2 == ValidScores.Spare): #b2=spare
                Subtotal = 10 + b3
            else: #no spare or strike
                Subtotal = b1+b2
        #print(Subtotal)
        DisplaySubTotals(Subtotal, i)
        #print("here")

PreviousSubTotals = [0]*10

def DisplaySubTotals(Subtotal, Frame):
    #calculates each subtotal for the current player up to the specified frame
    global PreviousSubTotals
    PreviousSubTotals[Frame-1] = Subtotal
    #print(PreviousSubTotals)
    for s in PreviousSubTotals[:Frame-1]:
        Subtotal += s
    SelectFrame(SelectPlayer(CurrentPlayer), Frame).SubTotal.Value = str(Subtotal)

def DisplayTotals():
    #updates the total score of current player
    global PreviousSubTotals
    total = 0
    for score in PreviousSubTotals:
        total += score
    SelectPlayer(CurrentPlayer).Total.Value = str(total)
    
def UpdatePlayer(player, Score):
    #increments to next player when needed
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
    #disables buttons that need to be disabled
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
    #checks for end of game and increments to next frame when needed.
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
    #This just generates a report
    GameOver = GameOverDialog(None)
    GameOver.Report.AppendColumn("Rank")
    GameOver.Report.AppendColumn("Name")
    GameOver.Report.AppendColumn("Score")
    #sort the players by their total score
    #if a tie, the order is somewhat random
    p = sorted(playerList, reverse=True, key = lambda x:int(x.Total.Value))
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
        #we don't define the playerList here as it it dynamically added
        #disable spare as it is impossible to start with a spare
        buttonList[11].Enable(False)
        #highlight the miss button, allows for keyboard input instantly
        buttonList[0].SetFocus()

    def EnterScore(self, event):
        global buttonList
        #this lets us iterate over the buttons but not have to increment a counter as
        #enumerate automatically does this for us
        for i, button in enumerate(buttonList):
            if button.GetValue():
                AddScore(i)
                break #break to exit the loop early as there should not be anymore buttons pressed at the time

    def OnShow(self, event):
        #this handles the dynamic adding of players
        global NumberOfPlayers
        global playerList, TotalPlayers
        for i in range(NumberOfPlayers):
            playerList.append(Frames.PlayerPanel( self.m_scrolledWindow2, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,90 ), wx.BORDER_NONE|wx.TAB_TRAVERSAL ))
            self.bSizer8.Add( playerList[-1], 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.EXPAND, 5 )
            #set the player names to what number they are
            playerList[-1].PlayerNameTextBox.Value = "Player {}".format(i+1)
        TotalPlayers = len(playerList)
        #print(TotalPlayers)

        #highlight player 1 as they are the first player to bowl
        SelectPlayer(0).PlayerNameTextBox.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )

    def OnKeyDown(self, event):
        #keyboard controls
        key = event.GetUnicodeKey()
        #print(key)
        #these numbers came from doing a print(key) then writing it down
        #the inline if statements make sure that a button can only be pressed if it is enabled.
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
        elif key==47: #/ key
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
        try:
            with open(self.FilePick.Path, "w") as f:
                f.write(text)
        except: #invalid write permissions
            wx.MessageBox("Invalid write permissions to specified location", "Error", style=wx.CENTER|wx.ICON_ERROR)
            return
        wx.MessageBox("File saved.", "Info")

try:
    app = wx.App()
    main = mainWindow(None)
    PlayerNumbers = NumberOfPlayersFrame(main)
    #showmodal stops execution here
    PlayerNumbers.ShowModal()
    PlayerNumbers.Show(False)
    if not early_exit:
        main.Show(True)
        app.MainLoop()
except BaseException as e: #something bad happened
    print(e)
    wx.MessageBox("Fatal Error!")
