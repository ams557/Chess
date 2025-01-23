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
        self.board[move.startRow][move.startCol]='--'  # updates sq prior to move to empty
        self.board[move.endRow][move.endCol]=move.pieceMoved  # updates sq after move w/ the piece moved
        self.moveLog.append(move)  # log move sq to allow for undo
        self.whiteToMove=not(self.whiteToMove)  # swap players

    def undoMove(self):
        """
        Undo the last move made
        """
        if len(self.moveLog)!=0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol]=move.pieceMoved
            self.board[move.endRow][move.endCol]=move.pieceCaptured
    
    def getValidMoves_Naive(self):
        """
        Crates a list of valid moves, factoring in check conditions
        """
        # 1. Generate all possible moves
        moves = self.getAllPossibleMoves()  # for now will not worry about checks
        return moves

    def getAllPossibleMoves(self):
        """
        Creates list of all possible moves, not considering checks
        """
        moves=[]
        for row in range(len(self.board)):  # number of rows
            for col in range(len(self.board[row])):  # number of cols in given row
                selectedPiece=self.board[row][col][0]   # checks the color of the selectedPiece
                if (selectedPiece=='w' and self.whiteToMove) or (selectedPiece=='b' and not self.whiteToMove):
                    piece=self.board[row][col][1]
                    if piece=="p":
                        self.getPawnMoves(row,col,moves)
                    if piece=="R":
                        self.getRookMoves(row,col,moves)
        return moves

    def getPawnMoves(self,row,col,moves):
        """
        Gets all pawn moves for the pawn located at the row, col and add all these moves to the list of possible moves
        """
        pass

    def getRookMoves(self,row,col,moves):
        """
        Gets all Rook moves for the rook located at the row, col and add all these moves to the list of possible moves
        """
        pass


    def getBishopMoves(self,row,col,moves):
        """
        Gets all Bishop moves for the bishop located at the row,col and add all these moves to the list of possible moves
        """
        pass


    def getQueenMoves(self, row, col, moves):
        """
        Gets all Queen moves for the queen located at the row,col and add all these moves to the list of possible moves
        """
        pass

    def getKingMoves(self,row,col,moves):
        """
        Gets all King moves for the king located at the row,col and add all these moves to the list of potential moves
        """
        pass

    def getKnightMoves(self,row,col,moves):
        """
        Gets all knight moves for the knight located at the row,col and add all these moves to the list of potential moves
        """
        pass

class Move():
    """
    Chess notation involves rows classified by a number 1-8 while columns are classified by a letter a-f.
    To use this notation, the [row][col] coordinates need to mapped to match the ones used in the original chess game.
    """
    rankToRow = {'1':7,'2':6,'3':5,'4':4,
                 '5':3,'6':2,'7':1,'8':0}
    rowToRank = {v:k for k,v in rankToRow.items()}
    fileToCol = {'a':0,'b':1,'c':2,'d':3,
                 'e':4,'f':5,'g':6,'h':7}
    colToFile = {v:k for k,v in fileToCol.items()}

    def __init__(self,startSq, endSq, board,isEnpassantMove=False, pawnPromotion=False,isCastleMove=False):
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
