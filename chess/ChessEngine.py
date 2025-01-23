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
        self.inCheck=False
        self.pins=[]
        self.checks=[]

        self.checkmate=False
        self.stalemate=False
    
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
        # Enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol]='--'  # extracting pawn
        # update enpassantPossible variable
        if move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow) == 2:  # pawn advanced 2sqs
            self.enpassantPossible=((move.startRow+move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible=()

        self.enpassantPossibleLog.append(self.enpassantPossible)
        
        # pawn promotion
        if move.isPawnPromotion:
            promotedPiece=input("Promote to Q, R, B, or N: ")
            self.board[move.endRow][move.endCol]=move.pieceMoved[0]+promotedPiece

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
        #undoing an enpassant
        if move.isEnpassantMove:
            self.board[move.endRow][move.endCol]='--'  # leave landing square blank
            self.board[move.startRow][move.endCol]=move.pieceCaptured
            self.enpassantPossible=(move.endRow, move.endCol)
        # undo a 2 square pawn advance
        if move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow)==2:
            self.enpassantPossible=()
    
   def getValidMoves(self):  # updated using advanced check algorithm
        """
        Creates a list of valid moves, factoring in check conditions
        """
           
        # advanced algorithm
        moves=[]
        self.inCheck, self.pins, self.checks=self.checkForPinsAndChecks()
        
        if self.whiteToMove:
            kingRow=self.wKLocation[0]
            kingCol=self.wKLocation[1]
        else:
            kingRow=self.bKLocation[0]
            kingCol=self.bKLocation[1]
        if self.inCheck:
            if len(self.checks)==1:  # only one check, block check or move king
                moves=self.getAllPossibleMoves()
                # to block a check must move a piece into one of the several squares btwn the enemy piece and king
                check=self.checks[0]
                checkRow=check[0]
                checkCol=check[1]
                pieceChecking=self.board[checkRow][checkCol]  # enemy piece causing the check
                validSquares=[]  # squares that pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1]=='N':
                    validSquares=[(checkRow,checkCol)]
                else:
                    for i in range(1,8):
                        validSquare=(kingRow+check[2]*i, kingCol+check[3]*i) # chekc[2] and check[3] are teh check directions
                        validSquares.append(validSquare)
                        if validSquare[0]==checkRow and validSquare[1]==checkCol:  # once getting to the piece and checks
                            break
                # get rid of any moves do not block check or move king
                for i in range(len(moves)-1, -1,-1):  # go through backwards removing from a list as iterating
                    if moves[i].pieceMoved[1]!='K':  # move does not move king so it must block  or capture
                        if not (moves[i].endRow,moves[i].endCol) in validSquares: # move does not block check or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(kingRow,kingCol,moves)
        else:
            moves=self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastlingMoves(self.wKLocation[0],self.wKLocation[1],moves,allyColor="w")
            else:
                self.getCastlingMoves(self.bKLocation[0],self.bKLocation[1],moves,allyColor="b")
        
        if len(moves)==0:
            if self.inCheck:
                self.checkmate=True
            else:
                # TODO stalemate on repeated moves
                self.stalemate=True
        else:
            self.checkmate=False
            self.stalemate=False
        
        self.currentCastlingRights=tempCastlingRights
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

    def checkForPinsAndChecks(self):
        """
        This function checks to see if a king is in check, then checks to see if the king is pinned
            - If the king is in check but not pinned either it can move or another piece can cover it
            - If the king is pinned (in check by two pieces) the king must move
        """
        pins=[]  # squares where the allied pinned piece is and direction pinned from
        checks=[]  # squares where enemy is applying a check
        inCheck=False
        if self.whiteToMove:
            enemyColor='b'
            allyColor='w'
            startRow=self.wKLocation[0]
            startCol=self.wKLocation[1]
        else:
            enemyColor='w'
            allyColor='b'
            startRow=self.bKLocation[0]
            startCol=self.bKLocation[1]
        # Check outward from king for pins and checks, keeping track of pins
        directions=((-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1,1), (1,-1), (1,1))
        for j in range(len(directions)):
            direction=directions[j]
            possiblePin=()  # reset possible pins
            for i in range(1,8):
                endRow=startRow+direction[0]*i
                endCol=startCol+direction[1]*i
                if 0<=endRow<=7 and 0<=endCol<=7:
                    endPiece=self.board[endRow][endCol]
                    if endPiece[0]==allyColor and endPiece[1]!='K':
                        if possiblePin==():  # 1st allied piece could be pinned
                            possiblePin=(endRow, endCol, direction[0], direction[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0]==enemyColor:
                        type=endPiece[1]
                        # Five possibilities here in this complex conditional
                            # 1. Orthogonal from king and piece is a rook
                            # 2. Diagonal from king and piece is a bishop
                            # 3. One sq diagonal from king and piece is a pawn
                            # 4. Any direction and piece is a queen
                            # 5. Any direction one square away and the piece is a king (necessary to prevent a king to move a square controlled by another king)
                        if (0<=j<=3 and type=='R') or \
                                (4<=j<=7 and type=='B') or \
                                (i==1 and type=='p' and ((enemyColor=='w' and 6<=j<=7) or (enemyColor=='b' and 4<=j<=5))) or \
                                (type=='Q') or (i==1 and type=='K'):
                            if possiblePin==():  # on piece blocking so check
                                inCheck=True
                                checks.append((endRow,endCol,direction[0],direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off the board
                    break
        # check for knight checks
        knightMoves=((-2,-1), (-2,1), (-1,2), (1,2), (2,-1), (2,1), (-1,-2), (1,-2))
        for move in knightMoves:
            endRow=startRow+move[0]
            endCol=startCol+move[1]
            if 0<=endRow<=7 and 0<=endCol<=7:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]==enemyColor and endPiece[1]=='N':  # enemy knight attacking king
                    inCheck=True
                    checks.append((endRow,endCol,move[0],move[1]))
        return inCheck, pins, checks
    
    def getPawnMoves(self,row,col,moves):
        """
        Gets all pawn moves for the pawn located at the row, col and add all these moves to the list of possible moves
        """
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==row and self.pins[i][1]==col:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:  #white pawn moves
            moveAmt=-1
            initialRow=6
            lastRow=0
            enemyColor='b'
            kingRow,kingCol=self.wKLocation
        else:
            moveAmt=1
            initialRow=1
            lastRow=7
            enemyColor='w'
            kingRow,kingCol=self.bKLocation
        
        if self.board[row+moveAmt][col]=='--':  # pawn advances 1sq
            if not piecePinned or pinDirection==(moveAmt,0):
                if row+moveAmt==lastRow: # if piece gets to bank rank then it is a pawn promotion
                    pawnPromotion=True
                moves.append(Move((row,col),(row+moveAmt,col),self.board, pawnPromotion=pawnPromotion))
                if row==initialRow and self.board[row+2*moveAmt][col]=='--': # pawn advances 2sqs
                    moves.append(Move((row,col),(row+2*moveAmt,col),self.board))

        if col-1>=0:  # capture to the left
            if not piecePinned or pinDirection==(moveAmt,-1):
                if self.board[row+moveAmt][col-1][0]==enemyColor:
                    moves.append(Move((row,col),(row+moveAmt,col-1),self.board,pawnPromotion=pawnPromotion))
                elif (row+moveAmt,col-1)==self.enpassantPossible:
                    moves.append(Move((row,col),(row-1,col-1),self.board,isEnpassantMove=True))
        if col+1<=7:  # capture to the right
            if not piecePinned or pinDirection==(moveAmt,1):
                if self.board[row+moveAmt][col+1][0]==enemyColor:
                    moves.append(Move((row,col),(row+moveAmt,col+1),self.board,pawnPromotion=pawnPromotion))
                elif (row+moveAmt,col+1)==self.enpassantPossible:
                    moves.append(Move((row,col),(row-1,col+1),self.board,isEnpassantMove=True))

        # add pawn promotions later

    def getRookMoves(self,row,col,moves):
        """
        Gets all Rook moves for the rook located at the row, col and add all these moves to the list of possible moves
        """
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==row and self.pins[i][1]==col:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                if self.board[row][col][i]!='Q':  # cannot remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions=((-1,0), (0,-1), (1,0), (0,1))  # up, left, right, down
        enemyColor="b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1,8):
                endRow=row+direction[0] * i
                endCol=col+direction[1] * i
                if 0<=endRow<8 and 0<=endCol<8:  # on board
                    if not piecePinned or pinDirection==direction or pinDirection==(-direction[0],-direction[1]):
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
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==row and self.pins[i][1]==col:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions=((-1,-1), (-1,1), (1,-1), (1,1))
        enemyColor="b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1,8):
                endRow=row+direction[0]*i
                endCol=col+direction[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    if not piecePinned or pinDirection==direction or pinDirection==(-direction[0],-direction[1]):
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
        self.getRookMoves(row,col,moves)
        self.getBishopMoves(row,col,moves)

    def getKingMoves(self,row,col,moves):
        """
        Gets all King moves for the king located at the row,col and add all these moves to the list of potential moves
        """
        rowMoves=(-1,-1,-1, 0, 0, 1, 1, 1)
        colMoves=(-1, 0, 1,-1, 1,-1, 0, 1)
        allyColor="w" if self.whiteToMove else "b"
        for i in range(8):
            endRow=row+rowMoves[i]
            endCol=col+colMoves[i]
            if 0<=endRow<=7 and 0<=endCol<=7:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyColor:  # not an ally piece (empty or enemy place)
                    # place king on end square and check for checks
                    if allyColor=='w':
                        self.wKLocation=(endRow,endCol)
                    else:
                        self.bKLocation=(endRow,endCol)
                    inCheck, pins, checks=self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row,col),(endRow,endCol),self.board))
                    # place king back on original location
                    if allyColor=='w':
                        self.wKLocation=(row,col)
                    else:
                        self.bKLocation=(row, col)

    def getKnightMoves(self,row,col,moves):
        """
        Gets all knight moves for the knight located at the row,col and add all these moves to the list of potential moves
        """
        piecePinned=False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==row and self.pins[i][1]==col:
                piecePinned=True
                self.pins.remove(self.pins[i])
                break
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

    def __init__(self,startSq, endSq, board,isEnpassantMove=False):
        self.startRow=startSq[0]
        self.startCol=startSq[1]
        self.endRow=endSq[0]
        self.endCol=endSq[1]
        self.pieceMoved=board[self.startRow][self.startCol]
        self.pieceCaptured=board[self.endRow][self.endCol]
        self.moveID=self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol  # creates unique number for each move
        # pawn promotion
        self.isPawnPromotion=((self.pieceMoved=='wp' and self.endRow==0) or (self.pieceMoved=='bp' and self.endRow==7))
        # Enpassant
        self.isEnpassantMove=isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured='wp' if self.pieceMoved=='bp' else 'bp'  # enpassant captures opposite colored pawn    
    
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
