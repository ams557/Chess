import random

# Assigning point values to each piece (Scoring)
pieceValues={"K":0,"Q":10,"R":5,"B":3,"N":3,"p":1}

# prioritize knight moves to squares where more moves available
knightScores=[[1,1,1,1,1,1,1,1],
              [1,2,2,2,2,2,2,1],
              [1,2,3,3,3,3,2,1],
              [1,2,3,4,4,3,2,1],
              [1,2,3,4,4,3,2,1],
              [1,2,3,3,3,3,2,1],
              [1,2,2,2,2,2,2,1],
              [1,1,1,1,1,1,1,1]]

# prioritize diagonals
bishopScores=[[4,3,2,1,1,2,3,4],
              [3,4,3,2,2,3,4,3],
              [2,3,4,3,3,4,3,2],
              [1,2,3,4,4,3,2,1],
              [1,2,3,4,4,3,2,1],
              [2,3,4,3,3,4,3,2],
              [3,4,3,2,2,3,4,3],
              [4,3,2,1,1,2,3,4]]

# prioritize centralize queen, place into open spaces where it has most influence
queenScores=[[1,1,1,3,1,1,1,1],
             [1,2,3,3,3,1,1,1],
             [1,4,3,3,3,4,2,1],
             [1,2,3,3,3,2,2,1],
             [1,2,3,3,3,2,2,1],
             [1,4,3,3,3,4,2,1],
             [1,1,2,3,3,1,1,1],
             [1,1,1,3,1,1,1,1]]

# probably best to try to place rooks on open files, or on same file as other rook/queen
rookScores=[[4,3,4,4,4,4,3,4],
            [4,4,4,4,4,4,4,4],
            [1,1,2,3,3,2,1,1],
            [1,2,3,4,4,3,2,1],
            [1,2,3,4,4,3,2,1],
            [1,1,2,3,3,2,1,1],
            [4,4,4,4,4,4,4,4],
            [4,3,4,4,4,4,3,4]]

whitePawnScores=[[8,8,8,8,8,8,8,8],
                 [8,8,8,8,8,8,8,8],
                 [5,6,6,7,7,6,6,5],
                 [2,3,3,5,5,3,3,2],
                 [1,2,3,4,4,3,2,1],
                 [1,1,2,3,3,2,1,1],
                 [1,1,1,0,0,1,1,1],
                 [0,0,0,0,0,0,0,0]]

blackPawnScores=[[0,0,0,0,0,0,0,0],
                 [1,1,1,0,0,1,1,1],
                 [1,1,2,3,3,2,1,1],
                 [1,2,3,4,4,3,2,1],
                 [2,3,3,5,5,3,3,2],
                 [5,6,6,7,7,6,6,5],
                 [8,8,8,8,8,8,8,8],
                 [8,8,8,8,8,8,8,8]]

# Need to implement king scores (prioritize defense - castling to keep king safe)

piecePositionScores={"N": knightScores, "B": bishopScores, "Q": queenScores, "R": rookScores, "wp": whitePawnScores, "bp": blackPawnScores}

CHECKMATE=1000
STALEMATE=0
DEPTH=4 # for recursion - how far into the recursion tree to dive (ie. how many moves ahead is computer looking)

def findRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]

def findBestMove(gamestate,validMoves,returnQueue):
    global nextMove, counter
    nextMove=None
    random.shuffle(validMoves)
    counter=0
    findMoveNegaMaxAlphaBeta(gamestate,validMoves,DEPTH,-CHECKMATE,CHECKMATE,1 if gamestate.whiteToMove else -1)
    print(counter)
    returnQueue.put(nextMove)

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
    for row in range(len(gamestate.board)):
        for col in range(len(gamestate.board[row])):
            square=gamestate.board[row][col]
            if square!="--":
                # score piece positionally
                if square[1]!="K": # (king is only one that doesnt have piece position table)
                    if square[1]=="p":  # for pawns
                        piecePositionScore=piecePositionScores[square][row][col]
                    else:  # for other pieces
                        piecePositionScore=piecePositionScores[square[1]][row][col]
                
            if square[0]=="w":
                score+=pieceValues[square[1]]+piecePositionScore*0.1
            elif square[0]=="b":
                score-=pieceValues[square[1]]+piecePositionScore*0.1
    return score