import socket
import gameboard
import tkinter as tk

import threading
import queue
# act as a server, always use 'O/o'

def listen_to_player1(buffer, s):
    """Listen to player1's connection.

    Args:
        buffer (queue): message buffer to communicate with main thread.
        s (socket): socket object to receive and send messages between two players.
    """
    s.listen(1)
    conn, addr = s.accept()
    buffer.put(conn)

def recv_player1_name(buffer, conn):
    """Receive player1's name and put it into buffer.

    Args:        
        buffer (queue): message buffer to communicate with main thread.
        conn (socket): socket object to receive and send messages between two players.
    """
    player1_name = conn.recv(1024).decode()
    buffer.put(player1_name)

def recv_player1_move(buffer, conn):
    """Receive player player1's move and put it into buffer.

    Args:        
        buffer (queue): message buffer to communicate with main thread.
        conn (socket): socket object to receive and send messages between two players.
    """
    player1_move = conn.recv(1024).decode()
    r = int(player1_move[0])
    c = int(player1_move[1])
    buffer.put((r, c))    
   
def recv_player1_play_again(buffer, conn):
    """Receive player1's decision of playing again, and
       put it into the buffer.

    Args:        
        buffer (queue): message buffer to communicate with main thread.
        conn (socket): socket object to receive and send messages between two players.
    """
    message = conn.recv(1024).decode()
    buffer.put(message)
    
    
class App():
    """The user interface class for player 2.
    """
    def __init__(self):
        """initialize the app interface
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.root = tk.Tk()
        self.root.title("Tic-Tac-Toe Game -- Player 2")
        self.root.geometry("400x400")
        
        self.game = gameboard.BoardClass()
        
        self.buffer = queue.Queue()
        self.enter_host_info()

    def reset_window(self):
        """reset the window.
        """
        self.root.destroy()
        self.root = tk.Tk()
        self.root.title("Tic-Tac-Toe Game -- Player 2")
        self.root.geometry("400x400")
        
    def enter_host_info(self):
        """generate the interface with the entries for the host information.
        """
        self.ip_label = tk.Label(self.root, text="Enter host ip:")
        self.ip_label.pack()
        
        self.host_ip_entry = tk.Entry(self.root)
        self.host_ip_entry.pack()
        
        self.port_label = tk.Label(self.root, text="Enter host port:")
        self.port_label.pack()
        
        self.host_port_entry = tk.Entry(self.root)
        self.host_port_entry.pack()
        
        self.get_input_button = tk.Button(self.root, text="Get Host Info", command=self.get_host_info)
        self.get_input_button.pack()
    
    def get_host_info(self):
        """Once `get_info` button clicked, it jumps to this function to 
           retrieve host ip and port information of the server.
           Then the server starts a new thread for listening to player1's connection.
        """
        self.host_ip_addr = self.host_ip_entry.get()
        self.host_port = self.host_port_entry.get()
        self.s.bind((self.host_ip_addr, int(self.host_port)))
        self.s.listen(1)
        self.reset_window()
        
        label = tk.Label(self.root, text="Listening to player1's connection...")
        label.pack()
        # create a new thread to listen to player1's connection.
        self.listen_thread = threading.Thread(target=listen_to_player1, 
                                              kwargs={'buffer': self.buffer, 's':self.s})
        self.listen_thread.start()
        self.root.after(2000, self.handle_connection)            
        
    def handle_connection(self):
        """ Handle the connection of player1.
            If connected, create a new thread to receive
            the username of player1.
        """
        try:
            self.conn = self.buffer.get()
            self.reset_window()
            label = tk.Label(self.root, text="Waiting for player1's name...")
            label.pack()
            self.recv_player1_name_thread = threading.Thread(target=recv_player1_name,
                                                     kwargs={'buffer': self.buffer, 'conn':self.conn})
            self.recv_player1_name_thread.start() 
            self.root.after(1000, self.get_player1_name)             
        except queue.Empty:
            self.root.after(1000, self.handle_connection)    
    
    def get_player1_name(self):
        """Get player1's name from buffer. Once successful, 
            prompt the user to enter the name of player2.
        """
        try:
            # receive player1's name
            self.player1_name = self.buffer.get()
            show_name = tk.Label(self.root, text= str(self.player1_name))
            show_name.pack()
            
            username_label = tk.Label(self.root, text = "Enter player2's user name")
            username_label.pack()
            self.username_entry = tk.Entry(self.root)
            self.username_entry.pack()
            
            get_username_button = tk.Button(self.root, text="Get Username", command=self.get_username)
            get_username_button.pack()
        except queue.Empty:
            self.root.after(1000, self.get_player1_name)    
        
    def get_username(self):
        """ Get the user input of the player2's name.
            Send it to player1 and starts the game.
        """
        self.player2_name = self.username_entry.get()
        self.conn.sendall(self.player2_name.encode())
        self.game.set_player_name(self.player1_name, self.player2_name)
        
        self.play_game()
    
    def play_game(self):
        """ Initialize game board interface and game logic.
            Create a new thread to wait for the player1's first move.
        """
        # init game board GUI
        self.reset_window()
        self.canvas = tk.Canvas(self.root, width=400, height=100)
        self.turn_indicator = self.canvas.create_text(200, 15, text="Player1's turn", font=('Arial', 20))
        self.canvas.place(x=0, y=350)
        self.game.init_player(self.player2_name, self.player2_name)
        self.game.resetGameBoard()
        
        self.buttons = []
        for row in range(self.game.board_width):
            button_row = []
            for col in range(self.game.board_width):
                button = tk.Button(self.root, text="", font=("Arial", 20), width=5, height=2,
                                   command=lambda r=row, c=col: self.handle_click(r, c))
                button.grid(row=row, column=col, padx=5, pady=5)
                button_row.append(button)
            self.buttons.append(button_row)  
        # spawn a thread to receive the move from player1
        self.recv_thread = threading.Thread(target=recv_player1_move, 
                                                kwargs={'buffer': self.buffer, 'conn':self.conn})   
        self.recv_thread.start()
        self.root.after(1000, self.update_player1_move)  
        
        
    def update_player1_move(self):
        """ Receive the player1's move from the message buffer,
            and update the game board accordingly. 
        """
        try:
            (r,c) = self.buffer.get()
            self.recv_thread.join()
            self.game.updateGameBoard(self.player1_name, r, c, "X")
            self.buttons[r][c].config(text="X", state=tk.DISABLED)
            over = self.game.checkGameOver(r, c)  
            self.canvas.itemconfigure(self.turn_indicator, text="Player2's turn")
            
            if over:
                self.show_win_los_tie()
                self.recv_play_again_thread = threading.Thread(target=recv_player1_play_again,
                                                               kwargs={'buffer': self.buffer, 'conn':self.conn}) 
                self.recv_play_again_thread.start()
                self.root.after(1000, self.handle_play_again)
        except queue.Empty:
            self.root.after(1000, self.update_player1_move)    
        
    def handle_click(self, r, c):
        """Handle the user clicks.

        Args:
            r (int): row number
            c (int): column number
        """
        # click is valid only when it's player2's turn
        if self.game.isMyTurn():
            legal = self.game.checkLegalMove(r, c)
            if legal is False:
                return
            self.game.updateGameBoard(self.player2_name, r, c, "O")
            self.buttons[r][c].config(text="O", state=tk.DISABLED)
            move = str(r) + str(c)
            self.conn.send(move.encode())
            over = self.game.checkGameOver(r, c)
            self.canvas.itemconfigure(self.turn_indicator, text="Player1's turn")
            
            if over:
                self.show_win_los_tie()
                self.recv_play_again_thread = threading.Thread(target=recv_player1_play_again,
                                                               kwargs={'buffer': self.buffer, 'conn':self.conn}) 
                self.recv_play_again_thread.start()
                self.root.after(1000, self.handle_play_again)
            else:
                self.recv_thread = threading.Thread(target=recv_player1_move, 
                                                    kwargs={'buffer': self.buffer, 'conn':self.conn})   
                self.recv_thread.start()
                self.root.after(1000, self.update_player1_move)    
    
    def handle_play_again(self):
        """ Get the player1's message from the buffer.
            If playing again, restart the game. Otherwise,
            jump to show statistics function.
        """
        try:
            message = self.buffer.get()
            if message == "Play Again":
                self.play_game()
            elif message == "Fun Times":
                self.root.after(100, self.show_statics())
        except queue.Empty:
            self.root.after(1000, self.handle_play_again)    
    
    def show_win_los_tie(self):
        """Show the win or lose state on canvas.
        """
        if self.game.isTie:
            self.canvas.itemconfigure(self.turn_indicator, text="It's a tie.")
            return
        if self.game.imWinner:
            self.canvas.itemconfigure(self.turn_indicator, text="I won!")
        else:
            self.canvas.itemconfigure(self.turn_indicator, text="I lost...")
                                      
    def show_statics(self):
        """When not playing again, show the statics of the game.
        """
        self.reset_window()
        name_label = tk.Label(self.root, text="Player1's name: "+self.player1_name+ 
                              "\n"+"Player2's name: "+self.player2_name)
        name_label.pack()
        label = tk.Label(self.root, text=self.game.computeStats())
        label.pack()
        self.root.after(10000, self.exit)       
    
    def exit(self):
        """ exit the game.
        """   
        self.conn.close()
        self.root.destroy()
            
    def start(self):
        """ run mainloop() to start the interface.
        """
        self.root.mainloop()


def run():
    """run the program.
    """
    app = App()
    app.start()
    
run()