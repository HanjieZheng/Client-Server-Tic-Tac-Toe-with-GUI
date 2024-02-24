import socket
import gameboard
import tkinter as tk

import threading
import queue

# act as a client, always use 'X/x'

def recv_player2_move(buffer, s):
    """Receive the move of player 2 and send it to the main thread.

    Args:
        buffer (queue): message buffer to communicate with the main thread
        s (socket): socket object to receive and send messages between two players
    """
    player2_move = s.recv(1024).decode()
    r = int(player2_move[0])
    c = int(player2_move[1])
    buffer.put((r, c))       
    

class App():
    """The user interface class for player 1.
    """
    def __init__(self):
        """initialize the app interface
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.root = tk.Tk()
        self.root.title("Tic-Tac-Toe Game -- Player 1")
        self.root.geometry("400x400")
        
        self.game = gameboard.BoardClass()
        
        self.buffer = queue.Queue()
        self.enter_host_info()

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
    
    def reset_window(self):
        """reset the window.
        """
        self.root.destroy()
        self.root = tk.Tk()
        self.root.title("Tic-Tac-Toe Game -- Player 1")
        self.root.geometry("400x400")
        
    def get_host_info(self):
        """Once `get_info` button clicked, it jumps to this function to 
           retrieve host ip and port information and try to connect to player 2.
           If successful, prompt the user to enter username. Otherwise,
           prompt the user if they want to connect to player 2 again.
        """
        self.host_ip_addr = self.host_ip_entry.get()
        self.host_port = self.host_port_entry.get()
        succ = self.connect_to_player2(self.host_ip_addr, self.host_port)
        self.reset_window()
        
        if succ:
            username_label = tk.Label(self.root, text = "Enter player1's user name")
            username_label.pack()
            self.username_entry = tk.Entry(self.root)
            self.username_entry.pack()
            
            get_username_button = tk.Button(self.root, text="Get Username", command=self.get_username)
            get_username_button.pack()
            
        else:
            self.try_connect_again()
                
    def try_connect_again(self):
        """ Once connectoin failed, prompt the user to indicate
            if they are trying to connect again.
        """
        try_again_label = tk.Label(self.root, text = "Do you want to try to connect player 2 again? (y/n)")
        try_again_label.pack()
        self.try_again_entry = tk.Entry(self.root)
        self.try_again_entry.pack()
        try_again_button = tk.Button(self.root, text="y/n", command=self.get_try_again)
        try_again_button.pack()
      
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

    def get_try_again(self):
        """get the user's input for the `try-again` option.
           If yes, jump to the window for entering the host information.
           Otherwise, exit the app.
        """
        choice = self.try_again_entry.get()
        if choice.lower() == 'y':
            self.reset_window()
            self.enter_host_info()
            
        elif choice.lower() == 'n':
            self.exit()
                  
    def get_username(self):
        """ Get player1's name from entry. Send it to player2 and
            wait for player2 to send its name back.
            Upon receiving player2's name, start a new game.
        """
        self.player1_name = self.username_entry.get()
        self.s.sendall(self.player1_name.encode())
        self.player2_name = self.s.recv(1024).decode()
        self.game.set_player_name(self.player1_name, self.player2_name)
        # jump to the board window
        self.play_game()
                     
    def connect_to_player2(self, ip, port):
        """Try to connect to player2 using socket.

        Args:
            ip (str): ip address of server
            port (str): port of the server

        Returns:
            boolean: If connected, returns true. Otherwise, returns false.
        """
        try:
            self.s.connect((ip, int(port)))
            return True
        except Exception as e:
            return False  
        
    def play_game(self):
        """ Initialize game board interface and game logic.
        """
        
        self.reset_window()
        self.canvas = tk.Canvas(self.root, width=400, height=100)
        self.turn_indicator = self.canvas.create_text(200, 15, text="Player1's turn", font=('Arial', 20))
        self.canvas.place(x=0, y=350)
        self.game.init_player(self.player1_name, self.player2_name)
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

    def handle_click(self, r, c):
        """Handle the user clicks.

        Args:
            r (int): row number
            c (int): column number
        """
        # click is valid only when it's player1's turn
        if self.game.isMyTurn():
            # check if click is valid
            legal = self.game.checkLegalMove(r, c)
            if legal is False:
                return
            # update game board.
            self.game.updateGameBoard(self.player1_name, r, c, "X")
            self.buttons[r][c].config(text="X", state=tk.DISABLED)
            # send the move to player2.
            move = str(r) + str(c)
            self.s.send(move.encode())
            self.canvas.itemconfigure(self.turn_indicator, text="Player2's turn")

            over = self.game.checkGameOver(r, c)
            # if game over, prompt the user to decide whether play again.
            if over:
                self.show_win_los_tie()                   
                self.root.after(1000, self.play_again())
            else:
                # create a new thread to receive player2's move.
                self.recv_thread = threading.Thread(target=recv_player2_move, 
                                                    kwargs={'buffer': self.buffer, 's':self.s})   
                self.recv_thread.start()
                self.root.after(1000, self.update_player2_move)    
            
    def update_player2_move(self):
        """ Receive the player2's move from the message buffer,
            and update the game board accordingly. 
        """
         # update game board
        try:
            (r,c) = self.buffer.get()
            self.recv_thread.join()
            self.game.updateGameBoard(self.player2_name, r, c, "O")
            self.buttons[r][c].config(text="O", state=tk.DISABLED)
            over = self.game.checkGameOver(r, c)  

            self.canvas.itemconfigure(self.turn_indicator, text="Player1's turn")
            
            # if game over, prompt the user to decide whether play again.
            if over:
                self.show_win_los_tie()
                self.root.after(1000, self.play_again())
        except queue.Empty:
            self.root.after(1000, self.update_player2_move)    
    
    def play_again(self):
        """When game is over, prompt the user to indicate whether to play again.
        """
        self.reset_window()
        
        play_again_label = tk.Label(self.root, text="Do you want to play again? (y/n): ")
        play_again_label.pack()
        self.play_again_entry = tk.Entry(self.root)
        self.play_again_entry.pack()
        play_again_button = tk.Button(self.root, text="y/n", command=self.get_play_again)
        play_again_button.pack()
                   
    def get_play_again(self):
        """Get the user input of whether to play again.
           Send the message to player2 accordingly.
        """
        choice = self.play_again_entry.get()
        if choice.lower() == 'y':
            self.s.sendall("Play Again".encode())
            self.play_game()
        
        elif choice.lower() == 'n':
            self.s.sendall("Fun Times".encode())
            self.root.after(100,self.show_statics())
            
    def start(self):
        """ run mainloop() to start the interface.
        """
        self.root.mainloop()
 
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
        self.s.close()  
        self.root.destroy()
    
def run():
    """run the program.
    """
    app = App()
    app.start()
    
run()