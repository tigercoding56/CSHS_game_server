from flask import Flask, jsonify
import time
import random
from multiprocessing import Process
import uuid

app = Flask(__name__)

class Client:
    def __init__(self, name, unique_code):
        self.last_refreshed = time.time()
        self.unique_code = unique_code
        self.name = name
        self.points = 0
        self.current_game = None
        self.current_game_code = None
    
    def refresh(self):
        self.last_refreshed = time.time() 

clients = []
games = {}
global_game_code = 0

def create_game(client_a, client_b):
    global games
    game_code = hash(str(client_a) + str(client_b))
    games[game_code] = ExampleGame(client_a.unique_code)
    return game_code

def get_game(game_code):
    global games
    if game_code in games:
        return games[game_code]
    else:
        return None

### Replace this function ###
def validate_data(data):
    allowed_characters = ["[", "]", "(", ")", ".", "\"", "a", "b", "\'", "S", "C", "="]
    for char in allowed_characters:
        data = data.replace(char, "")
    return eval(data)  # This is unsafe and needs to be replaced

class ExampleGame:
    def __init__(self, player_a_code):
        self.board = [[0, 0, 0]] * 3
        self.player_a_points = 0
        self.turn_count = 0
        self.player_b_points = 0
        self.is_running = True
        self.player_a_code = player_a_code
        self.current_turn_code = player_a_code

    def validate_turn_data(self, turn_data):
        if type(turn_data) != list:
            return 0
        if len(turn_data) != 2:
            return 0
        if not ((10 > turn_data[0] > -1) and (10 > turn_data[1] > -1)):
            return 0
        turn_data[0] = int(turn_data[0])
        turn_data[1] = int(turn_data[1])
        return 1

    def validate_board(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != 0:
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != 0:
                return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != 0:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != 0:
            return self.board[0][0]
        return "N"

    def terminate_game(self):
        self.is_running = False
        return [self.player_a_points, self.player_b_points]

    def player_a_disconnect(self):
        self.player_a_points = 0
        self.is_running = False

    def get_board_for_player_a(self):
        return str(self.board[0] + self.board[1] + self.board[2]).replace("A", "S").replace("B", "O")

    def get_board_for_player_b(self):
        return str(self.board[0] + self.board[1] + self.board[2]).replace("A", "O").replace("B", "S")

    def player_b_disconnect(self):
        self.player_b_points = 0
        self.is_running = False

    def player_a_turn(self, data):
        if self.current_turn_code != self.player_a_code:
            return 1
        self.current_turn_code = None
        self.turn_count += 1
        if self.turn_count > 10:
            self.is_running = False
        if self.board[data[0]][data[1]] != 0:
            return 0
        self.board[data[0]][data[1]] = "A"
        if self.validate_board() != "N":
            self.terminate_game()

    def player_b_turn(self, data):
        if self.current_turn_code == self.player_a_code:
            return 1
        self.current_turn_code = self.player_a_code
        self.turn_count += 1
        if self.turn_count > 10:
            self.is_running = False
        if self.board[data[0]][data[1]] != 0:
            return 0
        self.board[data[0]][data[1]] = "B"

def generate_unique_code():
    return str(uuid.uuid4())

@app.route('/')
def index():
    return '''hello <br> for this activity <br> code a client that calls /register/<name> with it's name as name, the program will return a random string to use as key for the rest of the session, the session ends when your client does not activate endpoint /refresh/<key> for 2 consecutive seconds <br> the refresh endpoint gives your client a code, if the code is 0 everything is fine, <br> if it is 2 please reset all game states as another round commences and using game data from previous <br> round may affect client performance, a code of 1 means waiting for your client's turn (submit it at /submit/<key>/<turn_data> turn data has to be a valid python formatted list of numbers <br> any special symbols will be stripped through a whitelist and so please do not attempt to find a RCE exploit <br>  if you need the game board data use endpoint /board/<key>/ which will return a JSON formatted list in this format {"<key>":[1,2,3]} <key> should be replaced by the key your client was assigned and the list could have any amount of items, <br> if coding in python a file is provided by someone as boilerplate it is up to someone else to make a game compatible with this for simplicity this will just include a demo that passes some arbitrary data around <br> for simplicity I did not implement a scoring endpoint, if the game is over the client should receive code 10 on refresh endpoint and shut down since what else should you do'''

@app.route('/register/<name>')
def register(name):
    unique_code = name + generate_unique_code()
    client = Client(name, unique_code)
    clients.append(client)
    return unique_code

@app.route('/board/<unique_code>')
def board(unique_code):
    client = get_client(unique_code)
    if client is None:
        return "404"
    game = get_game(client.current_game_code)
    if game is None:
        return "403"
    if game.player_a_code == unique_code:
        return game.get_board_for_player_a()
    else:
        return game.get_board_for_player_b()

def get_ready_client(unique_code):
    for client in clients:
        if client.unique_code != unique_code and client.current_game is None:
            return client
    return None

def get_client(unique_code):
    for client in clients:
        if client.unique_code == unique_code:
            return client
    return None

@app.route('/refresh/<unique_code>')
def refresh(unique_code):
    client = get_client(unique_code)
    if client is None:
        return "404"
    client.refresh()
    if client.current_game is not None:
        game = get_game(client.current_game_code)
        if not game.is_running:
            client.current_game = None
            return "0"
        else:
            if game.player_a_code == client.unique_code:
                if game.current_turn_code == game.player_a_code:
                    return "1"
                else:
                    return "0"
            else:
                if game.current_turn_code != game.player_a_code:
                    return "1"
                else:
                    return "0"
    else:
        ready_client = get_ready_client(unique_code)
        if ready_client is not None:
            game_code = create_game(client, ready_client)
            ready_client.current_game_code = game_code
            client.current_game_code = game_code
            ready_client.current_game = get_game(game_code)
            client.current_game = get_game(game_code)
    return "2"

@app.route('/submit/<unique_code>/<data>')
def submit(unique_code, data):
    client = get_client(unique_code)
    if client is not None:
        game = get_game(client.current_game_code)
        if game is not None:
            if not game.is_running:
                game = None
                return "Game over"
            if game.current_turn_code == game.player_a_code:
                if game.player_a_code != unique_code:
                    return "Not your turn"
                game.player_a_turn(validate_data(data))
            else:
                if game.player_a_code == unique_code:
                    return "Not your turn"
                game.player_b_turn(validate_data(data))
    return "Move submitted"

def main_loop():
    global clients
    print("Main loop started")
    while True:
        total_clients = len(clients)
        for i in range(total_clients):
            if (time.time() - clients[i].last_refreshed) > 2.1:
                game = get_game(clients[i].current_game_code)
                if game is not None:
                    if game.player_a_code == clients[i].unique_code:
                        game.player_a_disconnect()
                    else:
                        game.player_b_disconnect()
                del clients[i]

if __name__ == "__main__":
    process = Process(target=main_loop)
    process.start()
    app.run(port=5000)  # Ensure the server runs on port 5000

