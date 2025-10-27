import pygame, sys
from button import Button

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((640, 640))
running = True

fonte = pygame.font.Font('sprites/upheavtt.ttf', 25) 
background = pygame.image.load("sprites/bg.png").convert() 
icon_image = pygame.image.load('sprites/icone.webp').convert_alpha()

pygame.display.set_icon(icon_image)

def menu_principal():
    pygame.display.set_caption("Menu Principal")
    global running

    titulo = pygame.image.load('sprites/titulo.png').convert_alpha()
    jogar_img = pygame.image.load('sprites/bot_jogar.png').convert_alpha()
    info_img = pygame.image.load('sprites/bot_info.png').convert_alpha()
    sair_img = pygame.image.load('sprites/bot_sair.png').convert_alpha()
    ajuda_img = pygame.image.load('sprites/bot_ajuda.png').convert_alpha()

    bot_jogar = Button(145, 200, jogar_img)
    bot_ajuda = Button(145, 300, ajuda_img)
    bot_info = Button(145, 400, info_img)
    bot_sair = Button(145, 500, sair_img)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 250, 231))
        screen.blit(background, (0, 0))
        screen.blit(titulo, (80, 5))

        jogar_img = pygame.image.load('sprites/bot_jogar.png').convert_alpha()
        info_img = pygame.image.load('sprites/bot_info.png').convert_alpha()
        sair_img = pygame.image.load('sprites/bot_sair.png').convert_alpha()
        ajuda_img = pygame.image.load('sprites/bot_ajuda.png').convert_alpha()

        bot_jogar = Button(145, 200, jogar_img)
        bot_ajuda = Button(145, 300, ajuda_img)
        bot_info = Button(145, 400, info_img)
        bot_sair = Button(145, 500, sair_img)

        if bot_jogar.draw(screen) == True:
            play()
        if bot_ajuda.draw(screen) == True:
            ajuda()
        if bot_info.draw(screen) == True:
            info()
            pygame.event.clear()
        if bot_sair.draw(screen) == True:
            running = False
    
        pygame.display.update()

# def jogar():  # conecta ao servidor, faz o loop do jogo 

def info():

    pygame.display.set_caption("Informações")

    info_running = True 

    texto_info = pygame.image.load('sprites/mensagem_info.png').convert_alpha() 
    voltar_img = pygame.image.load('sprites/bot_voltar.png').convert_alpha()
    bot_voltar = Button(280, 530, voltar_img)

    while info_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                info_running = False

        screen.fill((255, 250, 231))
        screen.blit(background, (0, 0))
        screen.blit(texto_info, (0, -40))

        if bot_voltar.draw(screen) == True:
            pygame.event.clear()
            pygame.time.delay(100)
            info_running = False

        pygame.display.update()

def ajuda():

    pygame.display.set_caption("Ajuda")
    
    ajuda_running = True 

    comandos = pygame.image.load('sprites/comandos.png').convert_alpha()
    voltar_img = pygame.image.load('sprites/bot_voltar.png').convert_alpha()
    bot_voltar = Button(280, 530, voltar_img)
    
    texto_setas1 = fonte.render("Use as setas", True, (88, 27, 141)) 
    texto_setas2 = fonte.render("para mover-se.", True, (88, 27, 141)) 
    texto_p1 = fonte.render("Pressione 'P'", True, (88, 27, 141)) 
    texto_p2 = fonte.render("para pausar.", True, (88, 27, 141)) 
    texto_s1 = fonte.render("Pressione 'S'", True, (88, 27, 141)) 
    texto_s2 = fonte.render("para sair.", True, (88, 27, 141)) 

    while ajuda_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ajuda_running = False

        screen.fill((255, 250, 231))
        screen.blit(background, (0, 0))
        screen.blit(comandos, (60, 60))
        
        screen.blit(texto_setas1, (300, 100)) 
        screen.blit(texto_setas2, (300, 130)) 
        screen.blit(texto_p1, (300, 270)) 
        screen.blit(texto_p2, (300, 300)) 
        screen.blit(texto_s1, (300, 410)) 
        screen.blit(texto_s2, (300, 440))
        
        if bot_voltar.draw(screen) == True:
            pygame.time.delay(150)
            ajuda_running = False

        pygame.display.update()

    pygame.event.clear()

if __name__ == '__main__':
    menu_principal() 

pygame.quit()
sys.exit()