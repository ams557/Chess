"""
Driver file - Responsible for handling user input and displaying the current GameState object
"""

import os,sys
import pygame as p
import ChessEngine
import ChessAI

BOARD_WIDTH=BOARD_HEIGHT=512 # 400 is also ok
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
    screen=p.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    clock=p.time.Clock()
    screen.fill(p.Color('white'))
    gamestate=ChessEngine.GameState()
    validMoves=gamestate.getValidMoves()
    moveMade=False  # flag variable for when a move is made
        # only when gamestate changes ie when user makes a valid move) is the list of possible/valid moves recalc/d
            # This prevents recalling move every frame which can be computationally expensive
    
    loadImages()  #only done once before while loop
    
    running=True
    sqSelected=()  # no sq is selected, keeps track of last click of user - tuple (row, col)
    playerClicks=[]  # keeps track of player clicks - two tuples: [(rows,cols),(rows up/down,cols left/right)]
    
    while running: 
        for event in p.event.get():
            if event.type==p.QUIT:
                running=False
                p.quit()
                sys.exit()
            # mouse handler
            elif event.type==p.MOUSEBUTTONDOWN:
                location=p.mouse.get_pos() # (x,y) location of mouse
                col=location[0]//SQ_SIZE
                row=location[1]//SQ_SIZE
                if sqSelected==(row,col):  # user hit same square twice
                    sqSelected=()  # deselect
                    playerClicks=[]  # clear player clicks
                else:
                    sqSelected=(row,col)
                    playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks

                if len(playerClicks)==2:  # after 2nd click
                    move = ChessEngine.Move(playerClicks[0],playerClicks[1],gamestate.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gamestate.makeMove(move)
                        moveMade=True
                    sqSelected=()  # reset user clicks
                    playerClicks=[]  # clear player clicks
                    
            # key handler
            elif event.type==p.KEYDOWN:
                if event.key==p.K_z:  # undo when 'z' is pressed
                    gamestate.undoMove()
                    moveMade=True
              
        if moveMade:
            validMoves = gamestate.getValidMoves()
            moveMade = False
        
        drawGameState(screen,gamestate)
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gamestate, validMoves, sqSelected,moveLogFont):
    """
    Function responsible for all graphics in current gamestate
    """
    drawBoard(screen)  # 1) draws squares on board
    2) Highlight selectged squares (later)
    drawPieces(screen,gamestate.board)  # 3) draw pieces on top of squares
    drawMoveLog(screen,gamestate,moveLogFont)

def drawBoard(screen):
    """
    Function draws board.
        - Note: Top left square of board (either perspective) is always white.
    """
    colors = [p.Color('light yellow'),p.Color('dark grey')]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[(row+column)%2]  # black sqs at spots where sum of row position and column position is even
            p.draw.rect(screen,color,p.Rect(column*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawPieces(screen,board):
    """
    Draws pieces on board using current gamestate board
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != '--': # not empty space
                screen.blit(IMAGES[piece],p.Rect(column*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

if __name__ == "__main__":  # good practice
    main()

