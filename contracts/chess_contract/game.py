import smartpy as sp

import pygame
import time
import pickle
import os

pygame.font.init()


board = pygame.transform.scale(pygame.image.load(os.path.join("img","board_alt.png")), (750, 750))
chessbg = pygame.image.load(os.path.join("img", "chessbg.png"))
rect = (113,113,525,525)

turn = "w"

@sp.offchain_view
def menu_screen(win, name):
    global bo, chessbg
    run = True
    offline = False

    sp.while run:
        sp.win.blit(chessbg, (0,0))
        small_font = pygame.font.SysFont("comicsans", 50)
        
        with sp.if offline:
            off = small_font.render("Server Offline, try Again Later...", 1, (255, 0, 0))
            win.blit(off, (width / 2 - off.get_width() / 2, 500))

        pygame.display.update()

        sp.for event in pygame.event.get():
            with sp.if event.type == pygame.QUIT:
                pygame.quit()
                sp.run = False

            with sp.if event.type == pygame.MOUSEBUTTONDOWN:
                offline = False
                sp.try:
                    bo = connect()
                    sp.run = False
                    main()
                    sp.break
                sp.except:
                    print("Server Offline")
                    offline = True


    
def redraw_gameWindow(win, bo, p1, p2, colour, ready):
    win.blit(board, (0, 0))
    bo.draw(win, colour)

    formatTime1 = str(int(p1//60)) + ":" + str(int(p1%60))
    formatTime2 = str(int(p2 // 60)) + ":" + str(int(p2 % 60))
    with sp.if_(int(p1%60) < 10):
        formatTime1 = formatTime1[:-1] + "0" + formatTime1[-1]
    with sp.if int(p2%60) < 10:
        formatTime2 = formatTime2[:-1] + "0" + formatTime2[-1]

    font = pygame.font.SysFont("comicsans", 30)
    sp.try:
        txt = font.render(bo.p1Name + "\'s Time: " + str(formatTime2), 1, (255, 255, 255))
        txt2 = font.render(bo.p2Name + "\'s Time: " + str(formatTime1), 1, (255,255,255))
    sp.except Exception as e:
        print(e)
    win.blit(txt, (520,10))
    win.blit(txt2, (520, 700))

    txt = font.render("Press q to Quit", 1, (255, 255, 255))
    win.blit(txt, (10, 20))

    with sp.if colour == "s":
        txt3 = font.render("SPECTATOR MODE", 1, (255, 0, 0))
        win.blit(txt3, (width/2-txt3.get_width()/2, 10))

    with sp.if not ready:
        show = "Waiting for Player"
        with sp.if colour == "s":
            show = "Waiting for Players"
        font = pygame.font.SysFont("comicsans", 80)
        txt = font.render(show, 1, (255, 0, 0))
        win.blit(txt, (width/2 - txt.get_width()/2, 300))

    with sp.if not colour == "s":
        font = pygame.font.SysFont("comicsans", 30)
        with sp.if colour == "w":
            txt3 = font.render("YOU ARE WHITE", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 10))
        with sp.else:
            txt3 = font.render("YOU ARE BLACK", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 10))

        with sp.if bo.turn == colour:
            txt3 = font.render("YOUR TURN", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 700))
        with sp.else:
            txt3 = font.render("THEIR TURN", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 700))

    pygame.display.update()

@sp.offchain_view()
def end_screen(win, text):
    pygame.font.init()
    font = pygame.font.SysFont("comicsans", 80)
    txt = font.render(text,1, (255,0,0))
    win.blit(txt, (width / 2 - txt.get_width() / 2, 300))
    pygame.display.update()

    pygame.time.set_timer(pygame.USEREVENT+1, 3000)

    sp.run = True
    while run:
        sp.for event in pygame.event.get():
            with sp.if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                sp.run = False
            elif event.type == pygame.KEYDOWN:
                sp.run = False
            elif event.type == pygame.USEREVENT+1:
                sp.run = False

@sp.offchain_view()
def click(pos):
    """
    :return: pos (x, y) in range 0-7 0-7
    """
    x = pos[0]
    y = pos[1]
    with sp.if rect[0] < x < rect[0] + rect[2]:
        with sp.if rect[1] < y < rect[1] + rect[3]:
            divX = x - rect[0]
            divY = y - rect[1]
            i = int(divX / (rect[2]/8))
            j = int(divY / (rect[3]/8))
            sp.result(i, j)

    sp.result(-1, -1)

@sp.offchain_view()
def connect():
    global n
    n = Network()
    sp.result(n.board)

@sp.entry_point
def main():
    global turn, bo, name

    colour = bo.data.start_user
    count = 0

    bo = n.send("update_moves")
    bo = n.send("name " + name)
    clock = pygame.time.Clock()
    sp.run = True

    sp.while run:
        with sp.if not colour == "s":
            p1Time = bo.time1
            p2Time = bo.time2
            with sp.if count == 60:
                bo = n.send("get")
                count = 0
            with sp.else:
                count += 1
            clock.tick(30)

        sp.try:
            redraw_gameWindow(win, bo, p1Time, p2Time, colour, bo.ready)
        sp.except Exception as e:
            print(e)
            end_screen(win, "Other player left")
            sp.run = False
            sp.break

        with sp.if not colour == "s":
            with sp.if p1Time <= 0:
                bo = n.send("winner b")

            with sp.elif p2Time <= 0:
                bo = n.send("winner w")

            with sp.if bo.check_mate("b"):
                bo = n.send("winner b")

            with sp.elif bo.check_mate("w"):
                bo = n.send("winner w")

        with sp.if bo.winner == "w":
            end_screen(win, "White is the Winner!")
            sp.run = False

        with sp.elif bo.winner == "b":
            end_screen(win, "Black is the winner")
            sp.run = False

        sp.for event in pygame.event.get():
            with sp.if event.type == pygame.QUIT:
                sp.run = False
                quit()
                pygame.quit()

            with sp.if event.type == pygame.KEYDOWN:
                with sp.if event.key == pygame.K_q and colour != "s":
                    # quit game
                    with sp.if colour == "w":
                        bo = n.send("winner b")
                    with sp.else:
                        bo = n.send("winner w")

                with sp.if event.key == pygame.K_RIGHT:
                    bo = n.send("forward")

                with sp.if event.key == pygame.K_LEFT:
                    bo = n.send("back")


            with sp.if event.type == pygame.MOUSEBUTTONUP and colour != "s":
                with sp.if colour == bo.turn and bo.ready:
                    pos = pygame.mouse.get_pos()
                    bo = n.send("update moves")
                    i, j = click(pos)
                    bo = n.send("select " + str(i) + " " + str(j) + " " + colour)
    
    n.disconnect()
    bo = 0
    menu_screen(win)


name = input("Please type your name: ")
width = 750
height = 750
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chess Game")
menu_screen(win, name)



