import tkinter as tk

class BoardClass:
    
    def __init__(self):
        """initialize the board class.

        Args:
            my_name (String): name of the player who has the board object.
        """   
        self.player1_name = None
        self.player2_name = None     
        self.my_name = None
        self.last_player = None
        self.imWinner = False
        self.isTie = False
        self.wins = 0
        self.ties = 0
        self.losses = 0
        self.games_played = 0
        self.board_width = 3
        self.game_board = [[' ' for _ in range(self.board_width)] for _ in range(3)]
    
    def init_player(self, myName, lastName):
        """initialize the player names

        Args:
            myName (String): name of myself 
            lastName (String): initial name of the player who doesn't start first
        """
        self.my_name = myName
        self.last_player = lastName
    
    def set_player_name(self, player1, player2):
        """set the name for the player 1 & player 2

        Args:
            player1 (String): name of player 1
            player2 (String): name of player 2
        """
        self.player1_name = player1
        self.player2_name = player2
            
    def updateGamesPlayed(self):
        """Keeps track of how many games have played so far.
        """
        self.games_played += 1
    
    def resetGameBoard(self):
        """Resets the game board.
        """
        self.imWinner = False
        self.game_board = [[' ' for _ in range(self.board_width)] for _ in range(self.board_width)]
    
    def updateGameBoard(self, my_name, row, col, mark):
        """Updates the game board with the player's move.

        Put the mark to the location, specified by the row and column.
        Update the last player.
        
        Args:
            my_name (string): the player who made the move.
            row (int): the row that the mark will be placed.
            col (int): the column that the mark will be placed.
            mark (character): 'X' ro 'O'.
        """
        
        self.game_board[row][col] = mark
        self.last_player = my_name
        
    def checkLegalMove(self, r, c):
        """check if the position is legal
    
        Check if the position is in board and 
        if the position is empty to place a mark.
        
        Args:
            r (int): the row to be checked.
            c (int): the column to be checked.

        Returns:
            boolean: If the position is legal, returns True. 
                     Otherwise returns False.
        """
        if r >= 0 and r < self.board_width and c >= 0 and c < self.board_width:
            if (self.game_board[r][c] == ' '):
                return True
        return False
    
    def isMyself(self):
        """Check if the last move is made by myself.

        Returns:
            boolean: If the last move is made by myself, return true. 
                     Otherwise returns false.
        """
        return self.last_player == self.my_name
    
    def isMyTurn(self):
        """Check if this is my turn.
        
        Returns:
            boolean: If this is my turn, return true. 
                     Otherwise returns false.
        """
        return self.last_player != self.my_name
    
    
    def isWinner(self, row, col):
        """Check if the latest move resulted in a win.
        
        Check if the latest move resulted in a win, i.e. the latest player gets
        3 of its game pieces aligned.
        Also, if winner exists, update the win or lose counts accordingly.

        Args:
            row (int): the row of the mark placed in the lastet move.
            col (int): the column of the mark placed in the lastet move.

        Returns:
            boolean: If the latest move resulted in a win, returns true.
                     Otherwise returns false.
        """
        
        mark = self.game_board[row][col]
        win = False
        if (
            self.game_board[row][0] == mark and
            self.game_board[row][1] == mark and
            self.game_board[row][2] == mark
        ) or (
            self.game_board[0][col] == mark and
            self.game_board[1][col] == mark and
            self.game_board[2][col] == mark
        ):
            win = True
        
        if (row == col) :
            if (self.game_board[0][0] == mark and
                self.game_board[1][1] == mark and
                self.game_board[2][2] == mark):
                win = True

        
        if (row + col == self.board_width - 1):
            if (self.game_board[0][2] == mark and
                self.game_board[1][1] == mark and
                self.game_board[2][0] == mark):
                win = True
        # if winner appears, update wins or losses count
        if win:
            if self.isMyself():
                self.wins += 1
                self.imWinner = True
            else:
                self.losses += 1
                self.imWinner = False
                
        return win
    
    def boardIsFull(self):
        """Check if the board is full.

        Check if the board is full of marks. 
        Also, if the board is full, update the tie count.
        
        Returns:
            boolean: If the board is full, returns True.
                     Otherwise, returns False.
        """
        
        for row in self.game_board:
            if ' ' in row:
                return False
            
        # updates the ties count and game_played
        self.ties += 1
        self.isTie = True
        return True
       
    def checkGameOver(self, row, col):
        """Checks if the game is over.
        
        When a winner is found or the board is full, the game is over.
        When a game is over, update the game played number.
        
        Args:
            row (int): the row of the mark placed in the lastet move.
            col (int): the column of the mark placed in the lastet move.

        Returns:
            boolean: If the game is over, returns True. Otherwise, returns False.
        """
        win = self.isWinner(row, col)
        if win:
            self.updateGamesPlayed()
            return True
        full = self.boardIsFull()
        if full:
            self.updateGamesPlayed()
            return True
        return False
         
    def computeStats(self):
        """compute the stats of the game.
        
        compute the stats of the game at the end.
        """
        
        # f"Player: {self.my_name}\n"+ \
        #       f"Last Player: {self.last_player}" +\
        str = f"Games Played: {self.games_played}\n"+\
              f"Wins Number: {self.wins}\n"+\
              f"Losses Number: {self.losses}\n"+\
              f"Ties Number: {self.ties}\n"
              
        return str
   