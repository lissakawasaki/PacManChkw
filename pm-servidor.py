import socket
import threading
import json
from time import sleep, time
from random import choice

# --- CONFIGURAÇÕES ---
HOST = "127.0.0.1"
PORT = 65432
GRID_WIDTH = 30
GRID_HEIGHT = 33 # Ajustado para o tamanho real do seu array boards
TILE_SIZE = 32
PACMAN_SPEED = 4
GHOST_SPEED = 2

# Mapa do Jogo (Copiado do seu código)
boards = [
    [6,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,5],
    [3,6,4,4,4,4,4,4,4,4,4,4,4,4,5,6,4,4,4,4,4,4,4,4,4,4,4,4,5,3],
    [3,3,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,3,3],
    [3,3,1,6,4,4,5,1,6,4,4,4,5,1,3,3,1,6,4,4,4,5,1,6,4,4,5,1,3,3],
    [3,3,2,3,0,0,3,1,3,0,0,0,3,1,3,3,1,3,0,0,0,3,1,3,0,0,3,2,3,3],
    [3,3,1,7,4,4,8,1,7,4,4,4,8,1,7,8,1,7,4,4,4,8,1,7,4,4,8,1,3,3],
    [3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3],
    [3,3,1,6,4,4,5,1,6,5,1,6,4,4,4,4,4,4,5,1,6,5,1,6,4,4,5,1,3,3],
    [3,3,1,7,4,4,8,1,3,3,1,7,4,4,5,6,4,4,8,1,3,3,1,7,4,4,8,1,3,3],
    [3,3,1,1,1,1,1,1,3,3,1,1,1,1,3,3,1,1,1,1,3,3,1,1,1,1,1,1,3,3],
    [3,7,4,4,4,4,5,1,3,7,4,4,5,0,3,3,0,6,4,4,8,3,1,6,4,4,4,4,8,3],
    [3,0,0,0,0,0,3,1,3,6,4,4,8,0,7,8,0,7,4,4,5,3,1,3,0,0,0,0,0,3],
    [3,0,0,0,0,0,3,1,3,3,0,0,0,0,0,0,0,0,0,0,3,3,1,3,0,0,0,0,0,3],
    [8,0,0,0,0,0,3,1,3,3,0,6,4,4,9,9,4,4,5,0,3,3,1,3,0,0,0,0,0,7], # Linha 13 (Gate 9,9)
    [4,4,4,4,4,4,8,1,7,8,0,3,0,0,0,0,0,0,3,0,7,8,1,7,4,4,4,4,4,4],
    [0,0,0,0,0,0,0,1,0,0,0,3,0,0,0,0,0,0,3,0,0,0,1,0,0,0,0,0,0,0],
    [4,4,4,4,4,4,5,1,6,5,0,3,0,0,0,0,0,0,3,0,6,5,1,6,4,4,4,4,4,4],
    [5,0,0,0,0,0,3,1,3,3,0,7,4,4,4,4,4,4,8,0,3,3,1,3,0,0,0,0,0,6],
    [3,0,0,0,0,0,3,1,3,3,0,0,0,0,0,0,0,0,0,0,3,3,1,3,0,0,0,0,0,3],
    [3,0,0,0,0,0,3,1,3,3,0,6,4,4,4,4,4,4,5,0,3,3,1,3,0,0,0,0,0,3],
    [3,6,4,4,4,4,8,1,7,8,0,7,4,4,5,6,4,4,8,0,7,8,1,7,4,4,4,4,5,3],
    [3,3,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,3,3], # Linha 21 (Safe row)
    [3,3,1,6,4,4,5,1,6,4,4,4,5,1,3,3,1,6,4,4,4,5,1,6,4,4,5,1,3,3],
    [3,3,1,7,4,5,3,1,7,4,4,4,8,1,7,8,1,7,4,4,4,8,1,3,6,4,8,1,3,3],
    [3,3,2,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,2,3,3],
    [3,7,4,5,1,3,3,1,6,5,1,6,4,4,4,4,4,4,5,1,6,5,1,3,3,1,6,4,8,3],
    [3,6,4,8,1,7,8,1,3,3,1,7,4,4,5,6,4,4,8,1,3,3,1,7,8,1,7,4,5,3],
    [3,3,1,1,1,1,1,1,3,3,1,1,1,1,3,3,1,1,1,1,3,3,1,1,1,1,1,1,3,3],
    [3,3,1,6,4,4,4,4,8,7,4,4,5,1,3,3,1,6,4,4,8,7,4,4,4,4,5,1,3,3],
    [3,3,1,7,4,4,4,4,4,4,4,4,8,1,7,8,1,7,4,4,4,4,4,4,4,4,8,1,3,3],
    [3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3],
    [3,7,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,8,3],
    [7,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,8]
]

MAP_LAYOUT = boards
state_lock = threading.Lock()

class Game:
    def __init__(self):
        self.GHOST_NAMES = {
            'f1': {'name': 'Momonga', 'type': 'Blinky'},
            'f2': {'name': 'Shisa', 'type': 'Inky'},
            'f3': {'name': 'Hachiware', 'type': 'Pinky'},
            'f4': {'name': 'Chiikawa', 'type': 'Clyde'}
        }
        self.reset_game()
        self.player_connected = False
        self.client_movement_queue = None

    def reset_game(self):
        self.map = [row[:] for row in MAP_LAYOUT]
        # Posição Segura para Pacman (Col 2, Row 2) - Baseado no seu mapa
        self.pacman = {'x': 2 * TILE_SIZE, 'y': 2 * TILE_SIZE, 'direction': 'RIGHT', 'score': 0, 'power_up_timer': 0}
        
        # Posições Seguras para Fantasmas (Dentro da casa e logo acima)
        self.ghosts = [
            {'id': 'f1', 'x': 14 * TILE_SIZE, 'y': 11 * TILE_SIZE, 'state': 'normal', 'dir': 'LEFT'},  # Fora
            {'id': 'f2', 'x': 15 * TILE_SIZE, 'y': 11 * TILE_SIZE, 'state': 'normal', 'dir': 'RIGHT'}, # Fora
            {'id': 'f3', 'x': 14 * TILE_SIZE, 'y': 14 * TILE_SIZE, 'state': 'normal', 'dir': 'UP'},    # Dentro
            {'id': 'f4', 'x': 15 * TILE_SIZE, 'y': 14 * TILE_SIZE, 'state': 'normal', 'dir': 'UP'},    # Dentro
        ]
        self.game_status = 'waiting_for_players'
        self.dots_remaining = sum(r.count(1) + r.count(2) for r in self.map)
        self.mode = 'scatter'
        self.mode_timer = time()
        self.scatter_duration = 7
        self.chase_duration = 20

    def serializer(self):
        return {
            'map': self.map,
            'pacman': self.pacman,
            'ghosts': self.ghosts,
            'status': self.game_status,
            'names': self.GHOST_NAMES
        }

    def to_grid(self, pixel_coord):
        return int(pixel_coord // TILE_SIZE)

    def get_tile_type(self, x, y):
        grid_x = x // TILE_SIZE
        grid_y = y // TILE_SIZE
        if 0 <= grid_y < len(self.map) and 0 <= grid_x < len(self.map[0]):
            return self.map[grid_y][grid_x]
        return 3 # Parede se fora

    def is_collision(self, x, y, is_ghost=False):
        # Verifica colisão no centro do sprite para evitar prender na parede
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2
        t = self.get_tile_type(center_x, center_y)
        
        # 0=Vazio, 1=Ponto, 2=Power, 9=Portão (só fantasma passa)
        walkable_pacman = (0, 1, 2)
        walkable_ghost = (0, 1, 2, 9)

        if is_ghost:
            return t not in walkable_ghost
        else:
            return t not in walkable_pacman

    def manhattan_distance(self, x1, y1, x2, y2):
        return abs(self.to_grid(x1) - self.to_grid(x2)) + abs(self.to_grid(y1) - self.to_grid(y2))

    def get_next_pacman_pos(self, x, y, direction):
        tx, ty = x, y
        s = PACMAN_SPEED
        if direction == 'UP': ty -= s
        elif direction == 'DOWN': ty += s
        elif direction == 'LEFT': tx -= s
        elif direction == 'RIGHT': tx += s
        return tx, ty

    def update_pacman(self, new_direction):
        pacman = self.pacman
        nx, ny = self.get_next_pacman_pos(pacman['x'], pacman['y'], new_direction)
        
        # Tenta mudar de direção
        if new_direction != pacman['direction'] and not self.is_collision(nx, ny):
            pacman['x'], pacman['y'] = nx, ny
            pacman['direction'] = new_direction
        else:
            # Continua na direção atual se possível
            cx, cy = self.get_next_pacman_pos(pacman['x'], pacman['y'], pacman['direction'])
            if not self.is_collision(cx, cy):
                pacman['x'], pacman['y'] = cx, cy

        # Coleta de Itens
        grid_x = self.to_grid(pacman['x'] + TILE_SIZE // 2)
        grid_y = self.to_grid(pacman['y'] + TILE_SIZE // 2)
        
        if 0 <= grid_y < len(self.map) and 0 <= grid_x < len(self.map[0]):
            tile_value = self.map[grid_y][grid_x]
            if tile_value == 1:
                pacman['score'] += 10
                self.map[grid_y][grid_x] = 0
                self.dots_remaining -= 1
            elif tile_value == 2:
                pacman['score'] += 50
                self.map[grid_y][grid_x] = 0
                self.dots_remaining -= 1
                pacman['power_up_timer'] = 600
                self.activate_power_up()

        if pacman['power_up_timer'] > 0:
            pacman['power_up_timer'] -= 1
            if pacman['power_up_timer'] == 0:
                self.deactivate_power_up()

    def get_ghost_target(self, ghost_type, ghost_x, ghost_y, pacman_grid_x, pacman_grid_y, pacman_dir):
        # Lógica simplificada de alvo
        if self.mode == 'scatter':
            if ghost_type == 'Blinky': return GRID_WIDTH - 2, 1
            if ghost_type == 'Pinky': return 1, 1
            if ghost_type == 'Inky': return GRID_WIDTH - 2, GRID_HEIGHT - 2
            return 1, GRID_HEIGHT - 2 # Clyde
        
        # Chase Mode
        if ghost_type == 'Blinky':
            return pacman_grid_x, pacman_grid_y
        
        if ghost_type == 'Pinky': # 4 à frente
            tx, ty = pacman_grid_x, pacman_grid_y
            if pacman_dir == 'UP': ty -= 4
            elif pacman_dir == 'DOWN': ty += 4
            elif pacman_dir == 'LEFT': tx -= 4
            elif pacman_dir == 'RIGHT': tx += 4
            return tx, ty
            
        if ghost_type == 'Clyde': # Covarde
            dist = self.manhattan_distance(ghost_x, ghost_y, self.pacman['x'], self.pacman['y'])
            if dist > 8: return pacman_grid_x, pacman_grid_y
            return 1, GRID_HEIGHT - 2
            
        return pacman_grid_x, pacman_grid_y # Default/Inky simplified

    def update_ghosts(self):
        current_time = time()
        if current_time - self.mode_timer > (self.scatter_duration if self.mode=='scatter' else self.chase_duration):
            self.mode = 'chase' if self.mode=='scatter' else 'scatter'
            self.mode_timer = current_time
            for ghost in self.ghosts:
                if ghost['state']=='normal':
                    # Inverte direção ao trocar modo
                    op = {'UP':'DOWN','DOWN':'UP','LEFT':'RIGHT','RIGHT':'LEFT'}
                    ghost['dir'] = op.get(ghost['dir'], ghost['dir'])

        px_grid = self.to_grid(self.pacman['x'] + TILE_SIZE//2)
        py_grid = self.to_grid(self.pacman['y'] + TILE_SIZE//2)

        for ghost in self.ghosts:
            cx = ghost['x']
            cy = ghost['y']
            
            # Só toma decisão de direção se estiver perfeitamente alinhado na grid
            # Isso evita que o fantasma tente virar no meio da parede
            if cx % TILE_SIZE == 0 and cy % TILE_SIZE == 0:
                ghost_type = self.GHOST_NAMES[ghost['id']]['type']
                
                valid_moves = []
                reverse = {'UP':'DOWN','DOWN':'UP','LEFT':'RIGHT','RIGHT':'LEFT'}.get(ghost['dir'])
                
                for d in ('UP','DOWN','LEFT','RIGHT'):
                    if d == reverse and len(valid_moves) > 0: continue # Evita voltar a menos que seja sem saída
                    
                    # Simula posição futura
                    nx, ny = cx, cy
                    if d=='UP': ny -= TILE_SIZE
                    elif d=='DOWN': ny += TILE_SIZE
                    elif d=='LEFT': nx -= TILE_SIZE
                    elif d=='RIGHT': nx += TILE_SIZE
                    
                    if not self.is_collision(nx, ny, is_ghost=True):
                        valid_moves.append(d)

                if valid_moves:
                    if ghost['state'] == 'vulnerable':
                        ghost['dir'] = choice(valid_moves)
                    else:
                        # Escolhe o movimento que minimiza distância ao alvo
                        target_x, target_y = self.get_ghost_target(ghost_type, cx, cy, px_grid, py_grid, self.pacman['direction'])
                        best_dir = ghost['dir']
                        min_dist = float('inf')
                        
                        for move in valid_moves:
                            nx, ny = cx, cy
                            if move=='UP': ny -= TILE_SIZE
                            elif move=='DOWN': ny += TILE_SIZE
                            elif move=='LEFT': nx -= TILE_SIZE
                            elif move=='RIGHT': nx += TILE_SIZE
                            
                            dist = abs(self.to_grid(nx) - target_x) + abs(self.to_grid(ny) - target_y)
                            if dist < min_dist:
                                min_dist = dist
                                best_dir = move
                        ghost['dir'] = best_dir
                else:
                    # Beco sem saída, volta
                    ghost['dir'] = reverse if reverse else 'UP'

            # Aplica Movimento
            if ghost['dir']=='UP': ghost['y'] -= GHOST_SPEED
            elif ghost['dir']=='DOWN': ghost['y'] += GHOST_SPEED
            elif ghost['dir']=='LEFT': ghost['x'] -= GHOST_SPEED
            elif ghost['dir']=='RIGHT': ghost['x'] += GHOST_SPEED

            # Colisão Pacman
            if abs(self.pacman['x'] - ghost['x']) < TILE_SIZE/2 and abs(self.pacman['y'] - ghost['y']) < TILE_SIZE/2:
                if ghost['state']=='vulnerable':
                    self.pacman['score'] += 200
                    ghost['x'] = 14 * TILE_SIZE
                    ghost['y'] = 14 * TILE_SIZE
                    ghost['state'] = 'normal'
                else:
                    self.game_status = 'game_over'

    def activate_power_up(self):
        for g in self.ghosts: g['state'] = 'vulnerable'

    def deactivate_power_up(self):
        for g in self.ghosts: g['state'] = 'normal'

    def check_win(self):
        if self.dots_remaining <= 0: self.game_status = 'win'

game = Game()
game_running = False

def game_loop():
    global game_running
    FPS = 60
    while not game.player_connected:
        sleep(0.1)
    
    with state_lock:
        game.game_status = "running"
    game_running = True
    
    while game_running:
        start = time()
        with state_lock:
            if game.game_status == "running":
                if game.client_movement_queue:
                    game.update_pacman(game.client_movement_queue)
                    game.client_movement_queue = None
                game.update_ghosts()
                game.check_win()
            
            if game.game_status in ('game_over', 'win', 'waiting_for_players'):
                # Mantém o loop rodando mas sem atualizar lógica se acabou, esperando reset
                if game.game_status != 'running':
                    pass
        
        elapsed = time() - start
        if elapsed < 1.0/FPS:
            sleep(1.0/FPS - elapsed)
    
    with state_lock:
        game.reset_game()

def handle_client(conn, addr):
    global game_running
    buffer = ""
    
    print(f"Cliente conectado: {addr}")
    
    with state_lock:
        if game.player_connected:
            conn.close()
            return
        game.player_connected = True
        if not game_running:
            threading.Thread(target=game_loop, daemon=True).start()

    try:
        conn.settimeout(None) # Timeout controlado pelo select ou blocking normal
        while True:
            try:
                data = conn.recv(4096)
                if not data: break
                buffer += data.decode('utf-8')
                
                while '\n' in buffer:
                    msg_str, buffer = buffer.split('\n', 1)
                    if not msg_str.strip(): continue
                    
                    try:
                        msg = json.loads(msg_str)
                    except json.JSONDecodeError:
                        continue
                        
                    cmd = msg.get('command')
                    
                    if cmd == 'DISCONNECT':
                        return # Sai do loop e vai pro finally
                        
                    if cmd == 'MOVE' and game.game_status == 'running':
                        with state_lock:
                            game.client_movement_queue = msg.get('direction')
                    
                    # Sempre responde com o estado atual
                    with state_lock:
                        state = game.serializer()
                    
                    try:
                        # Protocolo: JSON + \n
                        conn.sendall((json.dumps(state) + "\n").encode('utf-8'))
                    except OSError:
                        return

            except OSError:
                break
    finally:
        print(f"Cliente desconectado: {addr}")
        with state_lock:
            game.player_connected = False
            game_running = False # Para o loop do jogo
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Servidor rodando em {HOST}:{PORT}")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()

if __name__ == '__main__':
    start_server()