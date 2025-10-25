import pygame, sys
from button import Button

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((640, 640))
running = True

fonte = pygame.font.Font('sprites/upheavtt.ttf', 30) 
background = pygame.image.load("sprites/bg.png").convert() 

jogar_img = pygame.image.load('sprites/bot_jogar.png').convert_alpha()
info_img = pygame.image.load('sprites/bot_info.png').convert_alpha()
sair_img = pygame.image.load('sprites/bot_sair.png').convert_alpha()
ajuda_img = pygame.image.load('sprites/bot_ajuda.png').convert_alpha()

bot_jogar = Button(145, 200, jogar_img)
bot_ajuda = Button(145, 300, ajuda_img)
bot_info = Button(145, 400, info_img)
bot_sair = Button(145, 500, sair_img)

def menu_principal():
    pygame.display.set_caption("Menu Principal")
    global running
    while running:
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 250, 231))

        screen.blit(background, (0, 0))

        if bot_jogar.draw(screen) == True:
            play()
        if bot_ajuda.draw(screen) == True:
            ajuda()
        if bot_info.draw(screen) == True:
            info()
        if bot_sair.draw(screen) == True:
            running = False
    
        pygame.display.update()

def info():

    pygame.display.set_caption("Informações")
    
    info_running = True 
    while info_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                info_running= False

        screen.fill((255, 250, 231))
        screen.blit(background, (0, 0))

        texto_info = pygame.image.load('sprites/mensagem_info.png').convert_alpha()
        screen.blit(texto_info, (0, 0))

        pygame.display.update()

if __name__ == '__main__':
    menu_principal() 

pygame.quit()
sys.exit()