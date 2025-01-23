import random

# Assigning point values to each piece (Scoring)
pieceValues={"K":0,"Q":10,"R":5,"B":3,"N":3,"p":1}
CHECKMATE=1000
STALEMATE=0
DEPTH=4 # for recursion - how far into the recursion tree to dive (ie. how many moves ahead is computer looking)

def findRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]

def findBestMove(gamestate,validMoves):
    global nextMove
    nextMove=None
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gamestate,validMoves,DEPTH,-CHECKMATE,CHECKMATE,1 if gamestate.whiteToMove else -1)
    return nextMove

def findMoveNegaMaxAlphaBeta(gamestate,validMoves,depth,alpha,beta,turnMultiplier):
    """
    Determines AI moves based on negaMax algorithm
        - Negamax -- Always look for maximum
            - if black's turn then multiply by -1
        - Implements Alpha/Beta pruning
            - alpha:=upper bound; beta:=lower bound
    """
    global nextMove
    if depth==0:
        return turnMultiplier*scoreBoard(gamestate)

    # move ordering - want to evaluate best moves first to find better scores to eliminate irrelevant branches (improves efficiency) 
    maxScore=-CHECKMATE
    for move in validMoves:
        gamestate.makeMove(move)
        nextMoves=gamestate.getValidMoves()
        score=-findMoveNegaMaxAlphaBeta(gamestate,nextMoves,depth-1,-beta,-alpha,-turnMultiplier)  # note - switch alpha and beta each turn (-alpha becomes new minimum, while -beta becomes new maximum)
        if score>maxScore:
            maxScore=score
            if depth==DEPTH:
                nextMove=move
        gamestate.undoMove()
        # pruning
        if maxScore>alpha: 
            alpha=maxScore
        if alpha>=beta:
            break
    return maxScore
    
def scoreBoard(gamestate):
    # score>0 => white winning vs score<0 => black winning
    # 0) Before scoring the board, check for checkmate or stalemate
    if gamestate.checkmate:
        if gamestate.whiteToMove:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif gamestate.stalemate:
        return STALEMATE
    score=0
    for row in gamestate.board:
        for square in row:
            if square[0]=="w":
                score+=pieceValues[square[1]]
            elif square[0]=="b":
                score-=pieceValues[square[1]]
    return score
    
    

################################################################################################################
###################################### ANYTHING PAST THIS POINT IS UNUSED ######################################
################################################################################################################

# Primitive scoring algorithm
def scorePieces(board):
    """
    Score the board based on pieces captured
    """
    score=0
    for row in board:
        for square in row:
            if square[0]=="w":
                score+=pieceValues[square[1]]
            elif square[0]=="b":
                score-=pieceValues[square[1]]
    return score


def findBestMove_old(gamestate, validMoves):  # first attempt at greedy chess AI
    # toggle to check which color's turn it is
    turnMultiplier=(1 if gamestate.whiteToMove else -1)
    
    # Greedy Algorithm - Minimize opponent score while maximizing self's score with that in mind
    opponentMinMaxScore=CHECKMATE
    bestPlayerMove=None
    random.shuffle(validMoves) # makes sure it doesn't pick first valid move in list every time
    for playerMove in validMoves:
        # 1) make move
        gamestate.makeMove(playerMove)
        # 2) Look at opponent's moves & calculate opponent's max score
        opponentMoves=gamestate.getValidMoves()
        if gamestate.stalemate:
            opponentMaxScore=STALEMATE
        elif gamestate.checkmate:
            opponentMaxScore=-CHECKMATE
        else:
            opponentMaxScore=-CHECKMATE
            # 3) find opponent's best move given the move by player
            for opponentMove in opponentMoves:
                gamestate.makeMove(opponentMove)
                gamestate.getValidMoves()
                if gamestate.checkmate:
                    score=CHECKMATE
                elif gamestate.stalemate:
                    score=STALEMATE
                else:
                    score=-turnMultiplier*scorePieces(gamestate.board)
                # Find opponent's max score given current gamestate
                if (score>opponentMaxScore):
                    opponentMaxScore=score
                gamestate.undoMove()
        # 3) Minimize score
        if opponentMaxScore<opponentMinMaxScore:
            opponentMinMaxScore=opponentMaxScore
            bestPlayerMove=playerMove
        # 4) After making a move and scoring the board, before making another move need to undo the move
        gamestate.undoMove()
    return bestPlayerMove


# Second attempt at chess AI
def findBestMoveMinMax(gamestate,validMoves):
    """
    Helper method for `findMoveMinMax()` method - makes first recursive call of `findMoveMinMax()`
    """
    global nextMove
    nextMove=None
    findMoveMinMax(gamestate,validMoves,DEPTH,gamestate.whiteToMove)
    return nextMove

def findMoveMinMax(gamestate,validMoves,depth,whiteToMove):
    global nextMove
    # 1) Check if at a terminal node of recursive tree
    if depth==0:
        return scorePieces(gamestate.board)
    
    # If it's white's turn to move, then try to maximize
    if whiteToMove:
        maxScore=-CHECKMATE
        for move in validMoves:
            gamestate.makeMove(move)
            nextMoves=gamestate.getValidMoves()
            score=findMoveMinMax(gamestate,nextMoves,depth-1,False)  # False => not white's turn
            if score>maxScore:
                maxScore=score
                # find best score at particular depth of recursion
                if depth==DEPTH:
                    nextMove=move
            gamestate.undoMove()
        return maxScore

    # If it's black's turn to move, then try to minimize
    else:
        minSCORE=CHECKMATE
        for move in validMoves:
            gamestate.makeMove(move)
            nextMoves=gamestate.getValidMoves()
            score=findMoveMinMax(gamestate,nextMoves,depth-1,True)  # True => white's turn
            if score<minScore:
                minScore=score
                if depth==DEPTH:
                    nextMove=move
            gamestate.undoMove()
        return minScore

# Third attempt at chess AI
def findBestMoveNegaMax(gamestate,validMoves):
    global nextMove
    nextMove=None
    random.shuffle(validMoves)
    findMoveNegaMax(gamestate,validMoves,DEPTH,1 if gamestate.whiteToMove else -1)
    return nextMove

def findMoveNegaMax(gamestate,validMoves,depth,turnMultiplier):
    """
    Determines AI moves based on negaMax algorithm
        - Negamax -- Always look for maximum
            - if black's turn then multiply by -1
    """
    global nextMove
    if depth==0:
        return turnMultiplier*scoreBoard(gamestate)
    maxScore=-CHECKMATE
    for move in validMoves:
        gamestate.makeMove(move)
        nextMoves=gamestate.getValidMoves()
        score=-findMoveNegaMax(gamestate,nextMoves,depth-1,-turnMultiplier)
        if score>maxScore:
            maxScore=score
            if depth==DEPTH:
                nextMove=move
        gamestate.undoMove()
    return maxScore


