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

        self.moveFunctions={'p':self.getPawnMoves,
                    'R':self.getRookMoves,
                    'N':self.getKnightMoves,
                    'K':self.getKingMoves,
                    'Q':self.getQueenMoves,
                    'B':self.getBishopMoves}
        self.whiteToMove=True
        self.moveLog=[]
        self.wKLocation=(7,4)
        self.bKLocation=(0,4)
    
    def makeMove(self,move):
        """
        Takes move as a parameter and executes it
        """
        self.board[move.startRow][move.startCol]='--'  # updates sq prior to move to empty
        self.board[move.endRow][move.endCol]=move.pieceMoved  # updates sq after move w/ the piece moved
        self.moveLog.append(move)  # log move sq to allow for undo
        self.whiteToMove=not(self.whiteToMove)  # swap players
        
        # Update the king's location if moved
        if move.pieceMoved=='wK':
            self.wKLocation=(move.endRow,move.endCol)
        elif move.pieceMoved=='bK':
            self.bKLocation=(move.endRow,move.endCol)

    def undoMove(self):
        """
        Undo the last move made
        """
        if len(self.moveLog)!=0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol]=move.pieceMoved
            self.board[move.endRow][move.endCol]=move.pieceCaptured
        # update king's position if move undone
            if move.pieceMoved=='wK':
                self.wKLocation=(move.startRow, move.startCol)
            elif move.pieceMoved=='bK':
                self.bKLocation=(move.startRow, move.startCol)
    
    def getValidMoves(self):
        """
        Crates a list of valid moves, factoring in check conditions
        """
        # 1. Generate all possible moves
        moves = self.getAllPossibleMoves()
        # 2. For each move, make the move
        for i in range(len(moves)-1,-1,-1):  # When removing from a list w/ for loop, go backwards b/c index doesn't shift w/ iteration
            self.makeMove(moves[i])
            # 3. Generate all oppt's moves
                # Done in `squareUnderAttack()` fxn
            # 4. If they attk king, move is invalid
                # Done in `inCheck()` fxn
            self.whiteToMove = not self.whiteToMove  # need to switch turns before calling `inCheck()` b/c `makeMove()` switched turns
            if self.inCheck():  # 5. if king in check, remove move from list of valid moves
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove  # need to switch one more time for even parity
            self.undoMove()
        return moves

    def inCheck(self):
        '''
        Determine if current player is in check
        '''
        if self.whiteToMove:
            return self.squareUnderAttack(self.wKLocation[0],self.wKLocation[1])
        else:
            return self.squareUnderAttack(self.bKLocation[0], self.bKLocation[1])
    
    def squareUnderAttack(self,row,col):
        '''
        Determine if the enemy can attack the square (row,col)
        '''
        self.whiteToMove=not(self.whiteToMove)  # switch to oppt turn
        oppMoves=self.getAllPossibleMoves()
        self.whiteToMove=not(self.whiteToMove)  # reset turn even if stmnt sq not under attack
        for move in oppMoves:
            if move.endRow==row and move.endCol==col:  # square is under attack
                return True
        return False  # by default a square is not under attack
    
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
                    self.moveFunctions[piece](row,col,moves)  # calls appropriate move function based piece type
        return moves

    def getPawnMoves(self,row,col,moves):
        """
        Gets all pawn moves for the pawn located at the row, col and add all these moves to the list of possible moves
        """
        if self.whiteToMove:  #white pawn moves
            if self.board[row-1][col]=='--':  # pawn advances one square
                if not piecePinned or pinDirection==(-1,0):
                    moves.append(Move((row,col),(row-1,col),self.board))
                    if row == 6 and self.board[row-2][col]=='--':  # pawn advances two squares
                        moves.append(Move((row,col),(row-2,col),self.board))
            if col-1>=0:  # captures to the left
                if self.board[row-1][col-1][0]=='b':  # enemy piece to capture
                    if not piecePinned or pinDirection==(-1,-1):
                        moves.append(Move((row, col),(row-1,col-1),self.board))
            if col+1<=7:  # captures to the right
                if self.board[row-1][col+1][0]=='b':  # enemy piece to capture
                    if not piecePinned or pinDirection==(-1,1):
                        moves.append(Move((row,col),(row-1,col+1),self.board))
        else:  # black pawn moves
            if self.board[row+1][col]=='--':  # pawn advances one square
                if not piecePinned or pinDirection==(1,0):
                    moves.append(Move((row,col),(row+1,col),self.board))
                    if row==1 and self.board[row+2][col]=='--':  # pawn advances two squares
                        moves.append(Move((row,col),(row+2,col),self.board))
            if col-1>=0:  # captures to the left
                if self.board[row+1][col-1][0] == 'w':  # enemy piece to capture
                    if not piecePinned or pinDirection == (1,-1):
                        moves.append(Move((row, col), (row+1, col-1), self.board))
            if col+1<=7:  # captures to the right
                if self.board[row+1][col+1][0]=='w':  # enemy piece to capture
                    if not piecePinned or pinDirection == (1,1):
                        moves.append(Move((row, col), (row+1, col+1), self.board))

    def getRookMoves(self,row,col,moves):
        """
        Gets all Rook moves for the rook located at the row, col and add all these moves to the list of possible moves
        """
        directions=((-1,0), (0,-1), (1,0), (0,1))  # up, left, right, down
        enemyColor="b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1,8):
                endRow=row+direction[0]*i
                endCol=col+direction[1]*i
                if 0<=endRow<8 and 0<=endCol<8:  # on board
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":  # empty space valid
                        moves.append(Move((row,col),(endRow,endCol),self.board))
                    elif endPiece==enemyColor:  # enemy piece valid
                        moves.append(Move((row,col),(endRow,endCol),self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else:  # off board
                    break


    def getBishopMoves(self,row,col,moves):
        """
        Gets all Bishop moves for the bishop located at the row,col and add all these moves to the list of possible moves
        """
        directions=((-1,-1), (-1,1), (1,-1), (1,1))
        enemyColor="b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1,8):
                endRow=row+direction[0]*i
                endCol=col+direction[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":  # empty space valid
                        moves.append(Move((row,col),(endRow,endCol),self.board))
                    elif endPiece[0]==enemyColor:  # enemy color valid
                        moves.append(Move((row,col),(endRow,endCol),self.board))
                        break
                    else:  # friendly piece invalid
                        break
                else: # off board
                    break


    def getQueenMoves(self, row, col, moves):
        """
        Gets all Queen moves for the queen located at the row,col and add all these moves to the list of possible moves
        """
        self.getBishopMoves(row,col,moves)
        self.getRookMoves(row,col,moves)

    def getKingMoves(self,row,col,moves):
        """
        Gets all King moves for the king located at the row,col and add all these moves to the list of potential moves
        """
        kingMoves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        allyColor = "w" if self.whiteToMove else "b"
        for move in kingMoves:
            endRow=row+move[0]
            endCol=col+move[1]
            if 0<= endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyColor:  # not an aly piece (empty or enemy piece)
                    moves.append(Move((row,col),(endRow,endCol),self.board))

    def getKnightMoves(self,row,col,moves):
        """
        Gets all knight moves for the knight located at the row,col and add all these moves to the list of potential moves
        """
        knightMoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(1,2),(2,-1),(2,1))
        allyColor="w" if self.whiteToMove else "b"
        for move in knightMoves:
            endRow=row+move[0]
            endCol=col+move[1]
            if 0<=endRow<8 and 0<=endCol<8:
                if not piecePinned:
                    endPiece=self.board[endRow][endCol]
                    if endPiece[0]!=allyColor:  # not an ally piece (empty or enemy)
                        moves.append(Move((row,col),(endRow,endCol),self.board))

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
        self.moveID=self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol  # creates unique number for each move
        
    def __eq__(self,other):
        """
        Overrides the equals method
        """
        if isinstance(other,Move):  # makes sure `other` object is instance of the Move
            return self.moveID==other.moveID
        return False
    
    def getChessNotation(self):
        """
        Converts input to pseudo chess notation.
            - Note it is possible to make this real chess notation
        """
        return self.getRankFile(self.startRow,self.startCol)+self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,row,col):
        return self.colToFile[col]+self.rowToRank[row]
