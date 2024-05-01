from flask import Flask
import time
import random
from multiprocessing import Process
app = Flask(__name__)
class client:
    def __init__(self,name,code):
        self.lastrefreshed = time.time()
        self.code = code
        self.name=name
        self.points=0
        self.game=None
    def refresh():
        self.lastrefreshed=time.time() 
        
        
    
clients = []
ggcode=0
###replace this function
def validat(data):
    dt=["[","]","(",")",".","\"","a","b","\'","S","C","=",]
    for x in dt:
        data.replace(x,"")
    rv=eval(data)#idk if this
class gamerunner():
    pass
class examplegame():
    
    def __init__(self,Acode):
        self.board=[[0,0,0]]*3
        self.apoints=0
        self.numturns=0
        self.bpoints=0
        self.running=1
        self.acode=Acode
        
    def vd(self,tv):#used to validate data from validat (which is there to convert string to list of integers without introducing remote code execution vunerabilities) penalty for incorrectly formatted data is skipping the turn 
        if (tv.__class__.__name__!=[].__class__.__name__):#this function is used as part of API and will not need to be called from game class
            return 0
        v=0;
    
        for d in tv:
            if (tv.__class__.__name__!= v.__class__.__name__):
                return 0
        if (len(tv)!=2):
            return 0
        if not ((10>d[0]>-1) and(10>d[1]>-1)):
            return 0
        d[0]=int(d[0])
        d[1]=int(d[1])
        return 1
    def game_validate_board(self):
        ###functions prefixed with game_ are game specific duh
        for i in range(0,3):
            if (board[i][0]==board[i][1]==board[i][2]!=0 ):
                return board[i][0]
            if (board[0][i]==board[1][i]==board[2][i]!=0):
                return board[0][i]
        if (board[0][0]==board[1][1]==board[2][2]!=0):
            return board[0][0]
        if (board[0][2]==board[1][1]==board[2][0]!=0):
            return board[0][0]
        return "N"
    def terminate():
        self.running =0
        return [self.apoints,self.bpoints]
    def Adisconnect(self):
        self.apoints=0
        self.running =0
    def getboardA():## S is used by default as mark for self , O as marker for opponent
        return str(board[0]+board[1]+board[2]).replace("A","S").replace("B","O")
    def getboardB():
        return str(board[0]+board[1]+board[2]).replace("A","O").replace("B","S")
    def Bdisconnect(self):
        self.bpoints=0
        self.running =0
    def turnA(self,data):##game ends after board is filled,client times out  or 10 consecutive turns return 0 if valid 1 if not 
        self.numturns+=1
        if (self.numturns>10):
            self.running=0
        if board[data[0]][data[1]]!=0:
            return 0
        board[data[0]][data[1]]="A"
        if game_validate_board(self)!="N":
            self.terminate()
        
        
        
    def turnB(self,data):
        self.numturns+=1
        if (self.numturns>10):
            self.running=0
        if board[data[0]][data[1]]!=0:
            return 0
        board[data[0]][data[1]]="B"
            
        
        
    
    
    



###
def getcode():
    global ggcode
    t=""
    code+=1
    i=0
    for i in range(0,10):#try and prevent namespace collisions 
       i+=code
       i=i%27
       t+=chr(63+i)
    t=t.lower()
    for i in range(0,20):
            i=random.randint(0,27)
            t+=chr(63+i)
    t=t.lower()
    t.replace("@","Z")
    t.replace("?","G")
    return t
@app.route('/')
def index():
    return '''hello <br> for this activity <br> code a client that calls /register/<index> with it's name as index , the program will return a random string to use as key for the rest of the session , the session ends when your client does not activate endpoint /refresh/<key/ for 2 consecutive seconds <br> the refresh endpoint gives your client a code  if the code is 0 everything is fine, <br> if it is 1 please reset all game states as another round comencess and using gamedata from previous <br> round may affect client performance , a code of 1 means waiting for your client's turn (submit it at /submit/<key>/<turndata> turn data has to be a valid python formatted list of numbers <br> any special symbols will be stripped through a whitelist and so please do not attempt to find a RCE exploit <br>  if you need the game board data use endpoint /board/<key>/ which will return a json  formatted list in this format {\"<key>\":[1,2,3]} <key> should be replaced by the key your client was assigned and the list could have any amount of items, <br> if coding in python a file is provided by someone as boilerplate    it is up to someone else to make a game compatible with this  for simplicity this will just include a demo that passes some arbitrary data around <br> for simplicity i did not implement a scoring endpoint , if the game is over the client should recieve code 10 on refresh endpoint and shut down since  what else should you do  '''
@app.route('/register/<name>')
def register(name):
    currentcode=getcode()
    
    return currentcode
def getclient(code):
    for i in clients:
        if i.code==code:
            return i
    return None
@app.route('/submit/<code>/data'):
def submit(code,data):
    t=getclient(code)
    if not t==None:
        if not t.game==None:
            if t.game.running =0:
                t.game=None
                return
    if not hasattr(t.game,"cturn"):
        t.game.cturn="A"
    x=t.game
    if (x.cturn=="A"):
        if (x.acode!=code):
            return
        x.turnA(validat(data))
            
def mainloop():
    global clients
    print("hi")
    while True:
        t=len(clients)
        for i in range(0,t-1):
            if (time.time()-clients[i].lastrefreshed)>2.1:
                del(clients[t])
if __name__ == "__main__":
   p = Process(target=mainloop)
   p.start()
   
