import pygame, sys
from pygame import mixer
from button import Button
import socket
import json
from time import sleep, time

#serverside confs
HOST = "127.0.0.1"
PORT = 65432
TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 20

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((640, 640))
running = True

fonte = pygame.font.Font('sprites/upheavtt.ttf', 25) 
background = pygame.image.load("sprites/bg.png").convert() 
icon_image = pygame.image.load('sprites/icone.webp').convert_alpha()
mixer.music.load("assets/BGM.mp3")
mixer.music.play(-1)
pygame.mixer.music.set_volume(0.2)

pygame.display.set_icon(icon_image)

def menu_principal():
    pygame.display.set_caption("Menu Principal")
    global running

    titulo = pygame.image.load('sprites/titulo.png').convert_alpha()
    jogar_img = pygame.image.load('sprites/bot_jogar.png').convert_alpha()
    info_img = pygame.image.load('sprites/bot_info.png').convert_alpha()
    sair_img = pygame.image.load('sprites/bot_sair.png').convert_alpha()
    ajuda_img = pygame.image.load('sprites/bot_ajuda.png').convert_alpha()

    ura_sfx = pygame.mixer.Sound("assets/usagi-prr.mp3")

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
            ura_sfx.play()
            play()
        if bot_ajuda.draw(screen) == True:
            ura_sfx.play()
            ajuda()
        if bot_info.draw(screen) == True:
            ura_sfx.play()
            info()
            pygame.event.clear()
        if bot_sair.draw(screen) == True:
            ura_sfx.play()
            running = False
    
        pygame.display.update()

def draw_game(current_state):
    
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0)) 
    
    pacman_image = pygame.image.load('sprites/Usagi1.png').convert_alpha()
    pacman_image_scaled = pygame.transform.scale(pacman_image, (TILE_SIZE, TILE_SIZE))
    power_up_img = pygame.image.load('sprites/power_up.png').convert_alpha()
    power_up_scaled = pygame.transform.scale(power_up_img, (TILE_SIZE, TILE_SIZE))
    
    ghost_sprites = {
        'f1': pygame.image.load('sprites/fantasma1.png').convert_alpha(),
        'f2': pygame.image.load('sprites/fantasma2.png').convert_alpha(),
        'f3': pygame.image.load('sprites/fantasma3.png').convert_alpha(),
        'f4': pygame.image.load('sprites/fantasma4.png').convert_alpha(),
    }

    vulnerable_sprite = {
        'f1': pygame.image.load('sprites/fantasma1-2.png').convert_alpha(),
        'f2': pygame.image.load('sprites/fantasma2-2.png').convert_alpha(),
        'f3': pygame.image.load('sprites/fantasma3-2.png').convert_alpha(),
        'f4': pygame.image.load('sprites/fantasma4-2.png').convert_alpha(),
    }

    game_map = current_state.get('map', [])
    for y, row in enumerate(game_map):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if tile == 1: 
                pygame.draw.rect(screen, (88, 27, 141), rect) 
            elif tile == 0: 
                pygame.draw.circle(screen, (255, 250, 231), rect.center, 3) 
            elif tile == 2: 
                screen.blit(power_up_scaled, rect.topleft)


    pacman_data = current_state.get('pacman', {})
    pacman_x = pacman_data.get('x', 0)
    pacman_y = pacman_data.get('y', 0)
    
    direction = pacman_data.get('direction', 'RIGHT')
    rotated_pacman = pacman_image_scaled
    if direction == 'UP':
        rotated_pacman = pygame.transform.rotate(pacman_image_scaled, 90)
    elif direction == 'DOWN':
        rotated_pacman = pygame.transform.rotate(pacman_image_scaled, -90)
    elif direction == 'LEFT':
        rotated_pacman = pygame.transform.flip(pacman_image_scaled, True, False)
    
    screen.blit(rotated_pacman, (pacman_x, pacman_y))
    
    ghosts_data = current_state.get('ghosts', [])
    for ghost in ghosts_data:
        blit_x = ghost['x'] - TILE_SIZE // 2
        blit_y = ghost['y'] - TILE_SIZE // 2
        
        current_ghost_image = None

        if ghost['state'] == 'vulnerable':
             current_ghost_image = vulnerable_sprite.get(ghost['id'], vulnerable_sprite['f1'])
        else:
             current_ghost_image = ghost_sprites.get(ghost['id'], ghost_sprites['f1']) 
             
        ghost_image_scaled = pygame.transform.scale(current_ghost_image, (TILE_SIZE, TILE_SIZE))
        screen.blit(ghost_image_scaled, (blit_x, blit_y))

    score = pacman_data.get('score', 0)
    power_timer = pacman_data.get('power_up_timer', 0)
    
    score_text = fonte.render(f"PONTUAÇÃO: {score}", True, (88, 27, 141))
    screen.blit(score_text, (20, 600))
    
    if power_timer > 0:
        timer_sec = power_timer // 60 
        timer_text = fonte.render(f"POWER UP: {timer_sec}", True, (255, 255, 0))
        screen.blit(timer_text, (640 - timer_text.get_width() - 20, 600))
        
    game_status = current_state.get('status', 'running')
    if game_status == 'game_over':
        over_text = fonte.render("GAME OVER", True, (255, 0, 0))
        screen.blit(over_text, (640 // 2 - over_text.get_width() // 2, 640 // 2 - over_text.get_height() // 2))
    elif game_status == 'win':
        win_text = fonte.render("PARABÉNS! VOCÊ VENCEU!", True, (0, 255, 0))
        screen.blit(win_text, (640 // 2 - win_text.get_width() // 2, 640 // 2 - win_text.get_height() // 2))
    elif game_status == 'waiting_for_players':
        wait_text = fonte.render("AGUARDANDO O INÍCIO DO JOGO...", True, (255, 255, 255))
        screen.blit(wait_text, (640 // 2 - wait_text.get_width() // 2, 640 // 2 - wait_text.get_height() // 2))

def play():
    pygame.display.set_caption("Usagi Pac-Man - Jogo")
    game_running = True
    client_socket = None
    
    current_state = {'status': 'waiting_for_players', 'map': [], 'pacman': {}, 'ghosts': {}}

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        sleep(1)
        print("Conectado ao servidor.")
        
        connect_message = {'command': 'CONNECT'}
        client_socket.sendall(json.dumps(connect_message).encode('utf-8'))
        
        client_socket.settimeout(1.0)
        data = client_socket.recv(4096)
        
        current_state = json.loads(data.decode('utf-8'))

        while game_running:
            movement_direction = None
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        movement_direction = 'UP'
                    elif event.key == pygame.K_DOWN:
                        movement_direction = 'DOWN'
                    elif event.key == pygame.K_LEFT:
                        movement_direction = 'LEFT'
                    elif event.key == pygame.K_RIGHT:
                        movement_direction = 'RIGHT'
                    elif event.key == pygame.K_s:
                        game_running = False
            
            game_status = current_state.get('status')
            if game_status == 'running' or game_status == 'waiting_for_players':
                if movement_direction and game_status == 'running':
                    move_message = {'command': 'MOVE', 'direction': movement_direction}
                else:
                    move_message = {'command': 'GET_STATE'}
                
                client_socket.sendall(json.dumps(move_message).encode('utf-8'))
            
            try:
                client_socket.settimeout(1.0/60.0) 
                data = client_socket.recv(4096)
                if not data:
                    print("Servidor fechou a conexão.")
                    break
                current_state = json.loads(data.decode('utf-8'))
            except socket.timeout:
                pass
            except ConnectionResetError:
                print("Conexão reiniciada pelo servidor.")
                break
            except Exception:
                pass
            
            draw_game(current_state)
            
            game_status = current_state.get('status')
            if game_status == 'game_over' or game_status == 'win':
                pygame.display.update()
                pygame.time.delay(3000) 
                game_running = False
            
            pygame.display.update()

    except ConnectionRefusedError:
        print(f"Não foi possível conectar ao servidor em {HOST}:{PORT}.")
        
        
    except Exception as e:
        print(f"Ocorreu um erro no cliente: {e}")

    finally:
        if client_socket:
            try:
                disconnect_message = {'command': 'DISCONNECT'}
                client_socket.sendall(json.dumps(disconnect_message).encode('utf-8'))
            except:
                pass 
            client_socket.close()
        pygame.event.clear()

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