"""
Driver file - Responsible for handling user input and displaying the current GameState object
"""

import os,sys
import pygame as p
import ChessEngine
import ChessAI
from multiprocessing import Process, Queue

BOARD_WIDTH=BOARD_HEIGHT=512 # 400 is also ok
MOVE_LOG_PANEL_WIDTH=250
MOVE_LOG_PANEL_HEIGHT=BOARD_HEIGHT
DIMENSION = 8 # dimensions of a chess board are 8x8
SQ_SIZE = BOARD_HEIGHT//DIMENSION
MAX_FPS = 15 # for animations later on
IMAGES = {}

def loadImages():
    """
    Function initializes a global dict of images (Will be called only once)
    """
    pieces = ['wp','wR','wN','wK','wB','wQ','bp','bR','bN','bK','bB','bQ']
    for piece in pieces:
        IMAGES[piece]=p.transform.scale(p.image.load(os.getcwd()+"/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: Image can be accessed by calling the dictionary ie `IMAGES['wp'] draws white pawn image

def main():
    """
    Main driver - Handles user input and updates graphics
    """
    p.init()
    screen=p.display.set_mode((BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock=p.time.Clock()
    screen.fill(p.Color('white'))
    moveLogFont=p.font.SysFont("Arial",14,False,False)
    gamestate=ChessEngine.GameState()
    validMoves=gamestate.getValidMoves()
    moveMade=False  # flag variable for when a move is made
        # only when gamestate changes ie when user makes a valid move) is the list of possible/valid moves recalc/d
            # This prevents recalling move every frame which can be computationally expensive
    animate=False  # flag variable for when animation occurs
    loadImages()  #only done once before while loop
    running=True
    sqSelected=()  # no sq is selected, keeps track of last click of user - tuple (row, col)
    playerClicks=[]  # keeps track of player clicks - two tuples: [(rows,cols),(rows up/down,cols left/right)]
    gameOver=False
    playerOne=True # if a human is playing white, this will be true. If AI is playing, then false.
    playerTwo=False # if a human is playing black, this will be true. If AI is playing, then false.
    AIThinking=False
    moveFinderProcess=None
    moveUndone=False
    
    while running:
        humanTurn=(gamestate.whiteToMove and playerOne) or (not(gamestate.whiteToMove) and playerTwo)  
        for event in p.event.get():
            if event.type==p.QUIT:
                running=False
                p.quit()
                sys.exit()
            # mouse handler
            elif event.type==p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location=p.mouse.get_pos() # (x,y) location of mouse
                    col=location[0]//SQ_SIZE
                    row=location[1]//SQ_SIZE
                    if sqSelected==(row,col) or col>=8:  # user hit same square twice
                        sqSelected=()  # deselect
                        playerClicks=[]  # clear player clicks
                    else:
                        sqSelected=(row,col)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks

                    if len(playerClicks)==2 and humanTurn:  # after 2nd click
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gamestate.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move==validMoves[i]:
                                gamestate.makeMove(validMoves[i])   # `validMoves[i] is is the move generated by the engine while `move` is the move generated by the player
                                moveMade=True
                                animate=True
                                sqSelected=()  # reset user clicks
                                playerClicks=[]  # clear player clicks
                        if not moveMade:
                            playerClicks=[sqSelected]
            # key handler
            elif event.type==p.KEYDOWN:
                if event.key==p.K_z:  # undo when 'z' is pressed
                    gamestate.undoMove()
                    moveMade=True
                    animate=False
                    gameOver=False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking=False
                    moveUndone=True
                if event.key==p.K_r:  # reset the board when 'r' is pressed
                    gamestate=ChessEngine.GameState() # reinitialize gamestate
                    validMoves=gamestate.getValidMoves()
                    sqSelected=()
                    playerClicks=[]
                    moveMade=False
                    animate=False
                    gameOver=False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking=False
                    moveUndone=True
                    

        # AI move finder
        if not(gameOver) and not(humanTurn) and not(moveUndone):
            if not(AIThinking):
                AIThinking=True
                print("thinking...")
                returnQueue=Queue()  # used to pass data btwn threads
                moveFinderProcess=Process(
                    target=ChessAI.findBestMove,  # function to call
                    args=(gamestate,validMoves,returnQueue)
                )
                moveFinderProcess.start()  # call findBestMove(gamestate,validMoves,returnQueue)
                
            if not(moveFinderProcess.is_alive()): # checks if process is still alive
                print("done thinking")
                AI_move=returnQueue.get()
                if AI_move is None:  # should never happen (only case is where next move results in checkmate)
                    AI_move=ChessAI.findRandomMove(validMoves)  # could pass in `gamestate.validMoves()` but that will regenerate valid moves over and over again (redundant)
                gamestate.makeMove(AI_move)
                moveMade=True
                animate=True
                AIThinking=False

        if moveMade:
            if animate:
                animateMove(gamestate.moveLog[-1],screen,gamestate.board,clock)  # animate last move in move log (current move)
            validMoves = gamestate.getValidMoves()
            moveMade = False
            animate=False
            moveUndone=False
        
        drawGameState(screen,gamestate,validMoves,sqSelected,moveLogFont)
        
        # GameOver States
        if gamestate.checkmate or gamestate.stalemate:
            gameOver=True
            drawEndGameText(screen,("Stalemate" if gamestate.stalemate else "Black wins by checkmate" if gamestate.whiteToMove else "White wins by checkmate"))
            
        
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gamestate, validMoves, sqSelected,moveLogFont):
    """
    Function responsible for all graphics in current gamestate
    """
    drawBoard(screen)  # 1) draws squares on board
    highlightSquares(screen,gamestate,validMoves,sqSelected) # 2) Highlights selectged squares
    drawPieces(screen,gamestate.board)  # 3) draw pieces on top of squares
    drawMoveLog(screen,gamestate,moveLogFont)

def drawBoard(screen):
    """
    Function draws board.
        - Note: Top left square of board (either perspective) is always white.
    """
    global colors
    colors = [p.Color('light yellow'),p.Color('dark grey')]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[(row+column)%2]  # black sqs at spots where sum of row position and column position is even
            p.draw.rect(screen,color,p.Rect(column*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def highlightSquares(screen, gamestate, validMoves, sqSelected):
    """
    Highlight square selected and moves for the piece selected
    """
    if sqSelected!=():
        row,col=sqSelected
        # check if square selected is a piece which can be moved
        if gamestate.board[row][col][0]==('w' if gamestate.whiteToMove else 'b'):
            # highlight selected square
            surface=p.Surface((SQ_SIZE,SQ_SIZE))
            surface.set_alpha(100)  # set transpaency value -> 0 is transparant vs 255 is opaque
            surface.fill(p.Color('blue'))
            screen.blit(surface,(col*SQ_SIZE,row*SQ_SIZE))  # background light surface at position (x,y)
            # highlight moves from that square
            surface.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow==row and move.startCol==col:
                    screen.blit(surface,(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def drawMoveLog(screen,gamestate,font):
    """
    Draws the move log
    """
    moveLogRect=p.Rect(BOARD_WIDTH,0,MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen,p.Color("black"),moveLogRect)
    moveLog=gamestate.moveLog
    moveTexts=[]
    for i in range(0,len(moveLog),2):
        moveString=str(i//2+1)+". "+str(moveLog[i])+" "
        if i+1<len(moveLog): # ensure black made a move
            moveString+=str(moveLog[i+1])+" "
        moveTexts.append(moveString)
    movesPerRow=3
    padding=5
    lineSpacing=2
    textY=padding
    for i in range(0,len(moveTexts),movesPerRow):
        text=""
        for j in range(movesPerRow):
            if i+j<len(moveTexts):
                text+=moveTexts[i+j]
        textObject=font.render(text,True,p.Color('white')) # create text object - (text,antialiasing,color)
        textLocation=moveLogRect.move(padding,textY)
        screen.blit(textObject,textLocation)
        textY+=textObject.get_height()+lineSpacing

def drawPieces(screen,board):
    """
    Draws pieces on board using current gamestate board
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != '--': # not empty space
                screen.blit(IMAGES[piece],p.Rect(column*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def animateMove(move, screen, board, clock):
    """
    Animating a move
    """
    global colors
    coordinates=[]  # list of coordinates that the animation will move through
    deltaRow=move.endRow-move.startRow
    deltaCol=move.endCol-move.startCol
    framesPerSquare=10 # frames to move one square
    frameCount=(abs(deltaRow)+abs(deltaCol))*framesPerSquare
    for frame in range(frameCount+1):
        row, col=(move.startRow+deltaRow*frame/frameCount, move.startCol+deltaCol*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)
        # erase the piece moved from its ending square
        color=colors[(move.endRow+move.endCol)%2]
        endSquare=p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured!='--':
            if move.isEnpassantMove:
                enPassantRow=((move.endRow+1) if move.pieceCaptured[0]=='b' else move.endRow-1)
                endSquare=p.Rect(move.endCol*SQ_SIZE,enPassantRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured],endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved],p.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)  # framerate for animation

def drawEndGameText(screen, text):
    font=p.font.SysFont("Helvetica",32,True,False)  # create font object - (font type, size, bold, italicized)
    # drawing text
    textObject=font.render(text,0,p.Color('gray')) # create text object - (text,antialiasing,color)
    textLocation=p.Rect(0,0,BOARD_WIDTH,BOARD_HEIGHT).move(BOARD_WIDTH/2-textObject.get_width()/2,
                                             BOARD_HEIGHT/2-textObject.get_height()/2)  # subtract half the width of the font from moving it half the width of the screen (centering text)
    screen.blit(textObject,textLocation)
    # outline effect on text
    textObject=font.render(text,0,p.Color('black')) # create text object - (text,antialiasing,color)
    screen.blit(textObject,textLocation.move(2,2))


if __name__ == "__main__":  # good practice
    main()
