
class GameState():
    """
    This class is responsible for storing all the info about the current state of the game. It will also be responsible for
    determining the valid moves at the current state. It will also keep a move log
    """
    def __init__(self):
        # Board rep/d as 8x8 2D list of lists w/ element of list having two characters. Rep/d from W's perspective.
        # First char rep/s color of piece ('b','w' or '-')
        # Second char rep/s the type of piece ('K','Q','R','B',N','p', or '-')
        # The string '--' rep/s space w/ no piece
        self.board=[
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],  # First row of pieces
            ['bp','bp','bp','bp','bp','bp','bp','bp'],  # second row of pieces - could rewrite using list comprehension `['bp' for _ in range(9)]
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wp','wp','wp','wp','wp','wp','wp','wp'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR']]

        self.whiteToMove=True
        self.moveLog=[]
    
    def makeMove(self,move):
        """
        Takes move as a parameter and executes it
        """
        self.board[move.endRow][move.endCol]=move.pieceMoved  # updates sq after move w/ the piece moved
        self.board[move.startRow][move.startCol]='--'  # updates sq prior to move to empty
        self.moveLog.append(move)  # log move sq to allow for undo
        self.whiteToMove=not(self.whiteToMove)  # swap players

class Move():
    """
    Chess notation involves rows classified by a number 1-8 while columns are classified by a letter a-f.
    To use this notation, the [row][col] coordinates need to mapped to match the ones used in the original chess game.
    """
    # maps keys to values according to chess notation
    # key = value
    rankToRow = {'1':7,'2':6,'3':5,'4':4,
                 '5':3,'6':2,'7':1,'8':0}
    rowToRank = {v:k for k,v in rankToRow.items()}
    fileToCol = {'a':0,'b':1,'c':2,'d':3,
                 'e':4,'f':5,'g':6,'h':7}
    colToFile = {v:k for k,v in fileToCol.items()}

    def __init__(self,startSq, endSq, board):
        self.startRow=startSq[0]
        self.startCol=startSq[1]
        self.endRow=endSq[0]
        self.endCol=endSq[1]
        self.pieceMoved=board[self.startRow][self.startCol]
        self.pieceCaptured=board[self.endRow][self.endCol]

    def getChessNotation(self):
        """
        Converts input to pseudo chess notation.
            - Note it is possible to make this real chess notation
        """
        return self.getRankFile(self.startRow,self.startCol)+self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,row,col):
        return self.colToFile[col]+self.rowToRank[row]





        
