import random, pygame, sys
from PIL import Image
from pygame.locals import *
import time

pygame.init()

#실행시 나오는 음악
bgm = 'bgm.wav'
pygame.mixer.init()
pygame.mixer.music.load(bgm)
pygame.mixer.music.set_volume(0.2)  # bgm 소리 조절
pygame.mixer.music.play(-1) # 무한재생

titleImg = pygame.image.load("image/title.png")
startImg = pygame.image.load("image/starticon.png")
quitImg = pygame.image.load("image/quiticon.png")
clickStartImg = pygame.image.load("image/clickedStartIcon.png")
clickQuitImg = pygame.image.load("image/clickedQuitIcon.png")
pauseImg = pygame.image.load("image/pause.png")
restartImg = pygame.image.load("image/start.png")
backImg = pygame.image.load("image/back.png")
clickBackImg = pygame.image.load("image/clickedback.png")

FPS = 30 # 프레임 조절
clock = pygame.time.Clock()
WINDOWWIDTH = 800 # 가로
WINDOWHEIGHT = 600 # 세로
gameDisplay = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
REVEALSPEED = 12 # 박스 열리는 시간 조절
BOXSIZE = 60 # 카드의 가로 세로 사이즈
GAPSIZE = 15 # 카드와 카드 사이 간격
BOARDWIDTH = 4 # 가로 카드의 개수
BOARDHEIGHT = 4 # 세로 카드의 개수

assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, '게임판에는 최소한 1쌍의 카드상자가 짝수로 존재해야 됩니다.' #오류메세지

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)    # 중앙에 카드 위치
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

BGCOLOR = WHITE    # 배경색
BOXCOLOR = GRAY    # 카드 겉면의 색
HIGHLIGHTCOLOR = BLUE  # 카드에 마우스가 올라올 때 테두리 표시색

pics = ['img1', 'img2', 'img3', 'img4', 'img5', 'img6', 'img7', 'img8']

# 버튼 클래스
class Button:
    def __init__(self, img_in, x, y, width, height, img_act, x_act, y_act, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x + width > mouse[0] > x and y + height > mouse[1] > y:
            gameDisplay.blit(img_act, (x_act, y_act))
            if click[0] and action != None:
                time.sleep(1)
                action()
        else:
            gameDisplay.blit(img_in, (x, y))


#시작 화면 메뉴
def mainmenu():

    pygame.display.set_caption('같은 그림 찾기')
    pygame.display.set_icon(pygame.image.load('image/img15.png'))
    menu = True

    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()

        gameDisplay.fill(WHITE)

        gameDisplay.blit(titleImg, (120, 130))
        Button(startImg, 280, 360, 60, 20, clickStartImg, 273, 358, main)
        Button(quitImg, 445, 360, 60, 20, clickQuitImg, 440, 358, quitgame)
        pygame.display.update()
        clock.tick(15)   #일정 주기로 화면 갱신


# 종료
def quitgame():
    pygame.quit()
    sys.exit()


#게임 메인화면
def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()

    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0
    mousey = 0 #마우스 이벤트 발생 좌표
    pygame.display.set_caption('같은 그림 찾기')
    pygame.display.set_icon(pygame.image.load('image/img15.png'))
    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # 첫 클릭 좌표 저장
    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)


    while True:
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR) # 전체 배경색
        drawBoard(mainBoard, revealedBoxes)

        Button(backImg,635, 280, 60, 20,clickBackImg , 630, 278, mainmenu)
        Button(quitImg, 635, 360, 60, 20, clickQuitImg, 630, 358, quitgame)

        for event in pygame.event.get(): #이벤트 처리 루프
            if event.type == QUIT or (event.type ==KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = False
            elif event.type == MOUSEBUTTONDOWN:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx != None and boxy != None:
            # 마우스가 현재 박스 위에 있다.
            if not revealedBoxes[boxx][boxy]: #닫힌 상자라면 하이라이트만!
                drawHighlightBox(boxx,boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard,[(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True #닫힌 상자+클릭-> 박스 열기
                if firstSelection ==None : #1번 박스>좌표 기록
                    firstSelection = (boxx, boxy)
                else: #1번 박스 아님>2번 박스>짝검사
                    icon1shape, icon1color = getPicAndNum(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getPicAndNum(mainBoard, boxx, boxy)
                    if icon1shape !=icon2shape or icon1color != icon2color:
                        #서로 다름이면 둘 다 닫기
                        pygame.time.wait(1000) #1000 milliseconds = 1sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]]=False
                        revealedBoxes[boxx][boxy] =False

                    #짝이면
                    elif hasWon(revealedBoxes):
                       pygame.time.wait(2000)

                       #게임판 재설정
                       mainBoard = getRandomizedBoard()
                       revealedBoxes = generateRevealedBoxesData(False)

                       #잠깐 공개
                       drawBoard(mainBoard, revealedBoxes)
                       pygame.display.update()
                       pygame.time.wait(1000)

                       #게임 시작
                       startGameAnimation(mainBoard)

                    firstSelection = None #1번 박스 리셋

                #화면을 다시 그린 다음 시간 지연을 기다린다..
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val]*BOARDHEIGHT)
    return revealedBoxes

def getRandomizedBoard():
    global pics
    cards=[]
    for pic in pics:
        for num in range(1, 2):
            cards.append((pic,num))
    random.shuffle(cards)
    numCardsUsed = int(BOARDWIDTH * BOARDHEIGHT /2)
    cards = cards[:numCardsUsed]*2
    random.shuffle(cards)


        #게임판 만들기
    board=[]
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(cards[0])
            del cards[0] #추가한 아이콘을 지운다
        board.append(column)
    return board

def splitIntoGroupsOf(groupSize, theList):
    #2차원 리스트 생성. 최대로 groupSize만큼의 요소 포함)
    result = []
    for i in range(0, len(theList),groupSize):
        result.append(theList[i:i + groupSize])
    return result

def leftTopCardsOfBox(boxx, boxy):
    #좌표를 픽셀좌표로 변환
    left = boxx*(BOXSIZE+GAPSIZE) +XMARGIN
    top = boxy*(BOXSIZE+GAPSIZE) +YMARGIN
    return(left, top)

def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCardsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def drawCard(pic, boxx, boxy):

    left,top=leftTopCardsOfBox(boxx,boxy) #보드 좌표에서 픽셀 좌표 구하기

    #그림 카드 만들기

    Img1 = pygame.image.load('image/img1.png')
    Img2 = pygame.image.load('image/img2.png')
    Img3 = pygame.image.load('image/img3.png')
    Img4 = pygame.image.load('image/img4.png')
    Img5 = pygame.image.load('image/img5.png')
    Img6 = pygame.image.load('image/img6.png')
    Img7 = pygame.image.load('image/img7.png')
    Img8 = pygame.image.load('image/img8.png')

    if pic == 'img1':
        DISPLAYSURF.blit(Img1, (left, top))
    elif pic =='img2':
        DISPLAYSURF.blit(Img2, (left, top))
    elif pic =='img3':
        DISPLAYSURF.blit(Img3, (left, top))
    elif pic =='img4':
        DISPLAYSURF.blit(Img4, (left, top))
    elif pic =='img5' :
        DISPLAYSURF.blit(Img5, (left, top))
    elif pic =='img6' :
        DISPLAYSURF.blit(Img6, (left, top))
    elif pic =='img7':
        DISPLAYSURF.blit(Img7, (left, top))
    elif pic =='img8':
        DISPLAYSURF.blit(Img8, (left, top))

def getPicAndNum(board, boxx, boxy):
    # 아이콘 값은 board[x][y][0]에 있다
    # 색깔 값은 board[x][y][1]에 있다
    return board[boxx][boxy][0], board[boxx][boxy][1]

def drawBoxCovers(board, boxes, coverage):
    # 닫히거나 열린 상태의 상자를 그린다
    # 상자는 요소 2개를 가진 리스트이며 xy 위치를 가진다
    for box in boxes:
        left, top = leftTopCardsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
        pic, num = getPicAndNum(board, box[0], box[1])
        drawCard(pic, box[0], box[1])
        if coverage > 0: # 닫힌 상태이면, 덮개만!
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):
    # 상자가 열려요
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    # 상자가 닫혀요
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    # 모든 상자를 상태에 맞추어 그리기
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCardsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # 닫힌 상자를 만든다
                pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
            else:
                # 열린 상자
                pic, num = getPicAndNum(board, boxx, boxy)
                drawCard(pic, boxx, boxy)


def drawHighlightBox(boxx, boxy):   #테두리색 박스
    left, top = leftTopCardsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)


def startGameAnimation(board):
    # 무작위로 상자를  4개씩 열어서 보여준다
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(4, boxes)
    drawBoard(board, coveredBoxes)

    for boxGroup in boxGroups:

        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

def hasWon(revealedBoxes):
    #모든 상자가 열렸으면 True, 아니면 False
    for i in revealedBoxes:
        if False in i:
            return False #  닫힌게 있으면 False
    return True

if __name__ == '__main__':
    mainmenu()
