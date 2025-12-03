import pygame, sys, socket, json
from pygame import mixer

HOST = "127.0.0.1"
PORT = 65432
TILE_SIZE = 32
# Ajustar para bater com o tamanho do mapa do servidor (30x33)
GRID_WIDTH = 30
GRID_HEIGHT = 33 

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE))
fonte = pygame.font.Font('sprites/upheavtt.ttf', 25)
background = pygame.image.load("sprites/bg.png").convert()
mixer.music.load("assets/BGM.mp3")
mixer.music.play(-1)
pygame.mixer.music.set_volume(0.2)

# Carrega e redimensiona as imagens UMA vez
pacman_img = pygame.transform.scale(pygame.image.load('sprites/Usagi1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE))
power_img = pygame.transform.scale(pygame.image.load('sprites/power_up.png').convert_alpha(), (TILE_SIZE, TILE_SIZE))
vul_img = pygame.transform.scale(pygame.image.load('sprites/fantasma1-2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE))
ghost_imgs = {
    'f1': pygame.transform.scale(pygame.image.load('sprites/fantasma1.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    'f2': pygame.transform.scale(pygame.image.load('sprites/fantasma2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    'f3': pygame.transform.scale(pygame.image.load('sprites/fantasma3.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    'f4': pygame.transform.scale(pygame.image.load('sprites/fantasma4.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
}

# Cache de rotação para não processar a cada frame
pacman_rotations = {
    'RIGHT': pacman_img,
    'LEFT': pygame.transform.flip(pacman_img, True, False),
    'UP': pygame.transform.rotate(pacman_img, 90),
    'DOWN': pygame.transform.rotate(pacman_img, -90)
}

def draw_game(state):
    screen.blit(background, (0, 0))
    game_map = state.get('map', [])
    
    # Desenha o mapa
    for y, row in enumerate(game_map):
        for x, tile in enumerate(row):
            r = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            # Paredes (3 a 8)
            if 3 <= tile <= 8:
                pygame.draw.rect(screen, (88,27,141), r)
                inner = r.inflate(-8, -8)
                pygame.draw.rect(screen, (0,0,0), inner)
            # Portão (9)
            elif tile == 9:
                pygame.draw.rect(screen, (255,182,193), r.inflate(0, -20))
            # Ponto (1)
            elif tile == 1:
                pygame.draw.circle(screen, (255,250,231), r.center, 3)
            # PowerUp (2)
            elif tile == 2:
                screen.blit(power_img, r.topleft)

    # Desenha Pacman
    p = state.get('pacman', {})
    px, py = p.get('x', 0), p.get('y', 0)
    d = p.get('direction', 'RIGHT')
    screen.blit(pacman_rotations.get(d, pacman_img), (px, py))

    # Desenha Fantasmas
    for g in state.get('ghosts', []):
        gx, gy = g['x'], g['y']
        gi = vul_img if g['state'] == 'vulnerable' else ghost_imgs.get(g['id'], ghost_imgs['f1'])
        screen.blit(gi, (gx, gy)) # Servidor já manda coordenada ajustada do topleft? Se não, ajustar aqui.
        # No servidor está: ghost['x'] = coordenada pixel. Assumindo topleft para facilitar. 
        # Se servidor usa centro, aqui seria (gx - TILE_SIZE//2, gy - TILE_SIZE//2). 
        # O meu servidor revisado usa topleft na lógica de update_ghosts final para facilitar.

    # UI
    score = p.get('score', 0)
    pw = p.get('power_up_timer', 0)
    st = fonte.render(f"PONTOS: {score}", True, (88,27,141))
    screen.blit(st, (20, screen.get_height() - 40))
    
    if pw > 0:
        t = fonte.render(f"POWER UP: {pw//60}", True, (255,255,0))
        screen.blit(t, (screen.get_width() - t.get_width() - 20, screen.get_height() - 40))
    
    gs = state.get('status','')
    center_x = screen.get_width()//2
    center_y = screen.get_height()//2
    
    if gs == 'game_over':
        t = fonte.render("GAME OVER", True, (255,0,0))
        screen.blit(t, (center_x - t.get_width()//2, center_y))
    elif gs == 'win':
        t = fonte.render("VOCÊ VENCEU", True, (0,255,0))
        screen.blit(t, (center_x - t.get_width()//2, center_y))
    elif gs == 'waiting_for_players':
        t = fonte.render("AGUARDANDO...", True, (255,255,255))
        screen.blit(t, (center_x - t.get_width()//2, center_y))

def play():
    pygame.display.set_caption("Usagi Pac-Man - Jogo")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
        # Envia comando inicial com \n
        s.sendall(json.dumps({'command':'CONNECT'}).encode() + b'\n')
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return

    clock = pygame.time.Clock()
    hold_dir = None
    buffer = ""
    
    # Loop Principal
    while True:
        # 1. Eventos e Input
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                try: s.sendall(json.dumps({'command':'DISCONNECT'}).encode() + b'\n')
                except: pass
                s.close()
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP: hold_dir = 'UP'
                elif e.key == pygame.K_DOWN: hold_dir = 'DOWN'
                elif e.key == pygame.K_LEFT: hold_dir = 'LEFT'
                elif e.key == pygame.K_RIGHT: hold_dir = 'RIGHT'
                elif e.key == pygame.K_s:
                    s.close()
                    return
            if e.type == pygame.KEYUP:
                # Opcional: parar se soltar a tecla (estilo clássico pacman costuma manter movendo)
                # Se quiser parar, descomente:
                # if e.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT): hold_dir = None
                pass

        # 2. Enviar Comando para Servidor
        try:
            msg = {'command': 'MOVE', 'direction': hold_dir} if hold_dir else {'command': 'GET_STATE'}
            s.sendall(json.dumps(msg).encode() + b'\n')
        except OSError:
            break

        # 3. Receber Dados (Com Buffer \n)
        try:
            data = s.recv(8192) # Buffer maior
            if not data: break
            buffer += data.decode('utf-8')
            
            # Processa todas as mensagens completas no buffer
            last_valid_state = None
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if line.strip():
                    try:
                        last_valid_state = json.loads(line)
                    except json.JSONDecodeError:
                        continue
            
            # 4. Atualiza Tela com o estado mais recente recebido
            if last_valid_state:
                draw_game(last_valid_state)
                pygame.display.update()
                
                status = last_valid_state.get('status')
                if status in ('game_over', 'win'):
                    pygame.time.delay(3000)
                    break

        except OSError:
            break
        
        clock.tick(60) # Limita a 60 FPS

    s.close()

def menu_principal():
    from button import Button # Import local
    
    titulo = pygame.image.load('sprites/titulo.png').convert_alpha()
    jogar_img = pygame.image.load('sprites/bot_jogar.png').convert_alpha()
    sair_img = pygame.image.load('sprites/bot_sair.png').convert_alpha()
    
    b1 = Button(145, 200, jogar_img)
    b2 = Button(145, 500, sair_img) # Botão sair
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
        screen.fill((255, 250, 231))
        screen.blit(background, (0, 0))
        screen.blit(titulo, (80, 5))
        
        if b1.draw(screen): play()
        if b2.draw(screen): return
        
        pygame.display.update()

if __name__ == '__main__':
    menu_principal()
    pygame.quit()
    sys.exit()