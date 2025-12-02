import socket
import threading
import json
from time import sleep, time
from random import random, choice
HOST = "127.0.0.1"
PORT = 65432
GRID_WIDTH = 20
GRID_HEIGHT = 20
TILE_SIZE = 32
PACMAN_SPEED = 2
GHOST_SPEED = 1


# momonga - blinky
# shisa - inky
# hachiware - pinky
# chiikawa - clyde


MAP_GRID = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

WALL_ROW = [1] * GRID_WIDTH
MAP_LAYOUT = MAP_GRID + [WALL_ROW] * (GRID_HEIGHT - len(MAP_GRID))

state_lock = threading.Lock()


class Game:
    def __init__(self):
        self.reset_game()
        self.player_connected = False
        self.client_movement_queue = None
        self.GHOST_NAMES = {
            'f1': {'name': 'Momonga', 'type': 'Blinky'}, # Chase
            'f2': {'name': 'Shisa', 'type': 'Inky'},     # Shadow/Ambush
            'f3': {'name': 'Hachiware', 'type': 'Pinky'},# Ambush
            'f4': {'name': 'Chiikawa', 'type': 'Clyde'}  # Scatter/Chase
        }

    def reset_game(self):
        self.map = [row[:] for row in MAP_LAYOUT] 
        self.pacman = {'x': 1 * TILE_SIZE, 'y': 1 * TILE_SIZE, 'direction': 'RIGHT', 'score': 0, 'power_up_timer': 0}
        self.ghosts = [
            {'id': 'f1', 'x': 9 * TILE_SIZE + TILE_SIZE // 2, 'y': 1 * TILE_SIZE + TILE_SIZE // 2, 'state': 'normal', 'dir': 'DOWN'},
            {'id': 'f2', 'x': 10 * TILE_SIZE + TILE_SIZE // 2, 'y': 1 * TILE_SIZE + TILE_SIZE // 2, 'state': 'normal', 'dir': 'DOWN'},
            {'id': 'f3', 'x': 9 * TILE_SIZE + TILE_SIZE // 2, 'y': 10 * TILE_SIZE + TILE_SIZE // 2, 'state': 'normal', 'dir': 'UP'},
            {'id': 'f4', 'x': 10 * TILE_SIZE + TILE_SIZE // 2, 'y': 10 * TILE_SIZE + TILE_SIZE // 2, 'state': 'normal', 'dir': 'UP'},
        ]
        self.game_status = 'waiting_for_players'
        self.dots_remaining = sum(row.count(0) + row.count(2) for row in self.map)


    def serializer(self):
        return {
            'map': self.map,
            'pacman': self.pacman,
            'ghosts': self.ghosts,
            'status': self.game_status,
            'names' : self.GHOST_NAMES
        }
    
    def to_grid(self, pixel_coord):
       # Converte uma coordenada de pixel p/ coordenada da grid
        return int(pixel_coord // TILE_SIZE)

    def get_tile_type(self,x,y):
        grid_x = x // TILE_SIZE
        grid_y = y // TILE_SIZE

        if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
            return self.map[grid_y][grid_x]
        return 1 

    def is_collision(self,x,y):
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2
        return self.get_tile_type(center_x,center_y) == 1
    
    def manhattan_distance(self, x1, y1, x2, y2):
        """Calcula a distância de Manhattan (horizontal + vertical)."""
        return abs(self.to_grid(x1) - self.to_grid(x2)) + abs(self.to_grid(y1) - self.to_grid(y2))


    def get_next_pacman_pos(self, x, y, direction):
        """Calcula a próxima posição do Pac-Man com base na direção."""
        temp_x, temp_y = x, y
        speed = PACMAN_SPEED
        
        if direction == 'UP': temp_y -= speed
        elif direction == 'DOWN': temp_y += speed
        elif direction == 'LEFT': temp_x -= speed
        elif direction == 'RIGHT': temp_x += speed
        
        return temp_x, temp_y

    def update_pacman(self, new_direction):
        pacman = self.pacman
        
        target_x_new, target_y_new = self.get_next_pacman_pos(pacman['x'], pacman['y'], new_direction)
        if new_direction != pacman['direction'] and not self.is_collision(target_x_new, target_y_new):
            pacman['x'], pacman['y'] = target_x_new, target_y_new
            pacman['direction'] = new_direction
        else:
            target_x_current, target_y_current = self.get_next_pacman_pos(pacman['x'], pacman['y'], pacman['direction'])
            if not self.is_collision(target_x_current, target_y_current):
                pacman['x'], pacman['y'] = target_x_current, target_y_current

        grid_x = self.to_grid(pacman['x'] + TILE_SIZE // 2)
        grid_y = self.to_grid(pacman['y'] + TILE_SIZE // 2)
        
        if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
            tile_value = self.map[grid_y][grid_x]
            
            if tile_value == 0: 
                pacman['score'] += 10
                self.map[grid_y][grid_x] = 3 
                self.dots_remaining -= 1
            elif tile_value == 2: 
                pacman['score'] += 50
                self.map[grid_y][grid_x] = 3
                self.dots_remaining -= 1
                pacman['power_up_timer'] = 60 * 10 
                self.activate_power_up()
        
        if pacman['power_up_timer'] > 0:
            pacman['power_up_timer'] -= 1
            if pacman['power_up_timer'] == 0:
                self.deactivate_power_up()


    def get_ghost_target(self, ghost_type, pacman_grid_x, pacman_grid_y, pacman_dir):
        
        # momonga
        if ghost_type == 'Blinky':
            return pacman_grid_x, pacman_grid_y

        # hachiware
        elif ghost_type == 'Pinky':
            target_x, target_y = pacman_grid_x, pacman_grid_y
            if pacman_dir == 'UP': target_y = max(0, pacman_grid_y - 4)
            elif pacman_dir == 'DOWN': target_y = min(GRID_HEIGHT - 1, pacman_grid_y + 4)
            elif pacman_dir == 'LEFT': target_x = max(0, pacman_grid_x - 4)
            elif pacman_dir == 'RIGHT': target_x = min(GRID_WIDTH - 1, pacman_grid_x + 4)
            return target_x, target_y

        # chiikawa
        elif ghost_type == 'Clyde':
            target_x_scatter, target_y_scatter = 0, GRID_HEIGHT - 1 # Canto inferior esquerdo
            
           
            dist_to_pacman = self.manhattan_distance(self.pacman['x'], self.pacman['y'], self.pacman['x'], self.pacman['y'])
            
            if dist_to_pacman <= 8 * TILE_SIZE: 
                return pacman_grid_x, pacman_grid_y # Chase
            else:
                return target_x_scatter, target_y_scatter # Scatter
                
        elif ghost_type == 'Inky':
            return pacman_grid_x, pacman_grid_y

        return pacman_grid_x, pacman_grid_y

    def update_ghosts(self):
        pacman = self.pacman
        pacman_grid_x = self.to_grid(pacman['x'] + TILE_SIZE // 2)
        pacman_grid_y = self.to_grid(pacman['y'] + TILE_SIZE // 2)

        for ghost in self.ghosts:
            ghost_type = self.GHOST_NAMES[ghost['id']]['type']
            current_x_center = ghost['x'] - TILE_SIZE // 2
            current_y_center = ghost['y'] - TILE_SIZE // 2
            
            is_centered = current_x_center % TILE_SIZE == 0 and current_y_center % TILE_SIZE == 0

            # proxima direção
            if is_centered:
                if ghost['state'] == 'vulnerable':
                    target_dir = choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                else:
                    target_grid_x, target_grid_y = self.get_ghost_target(
                        ghost_type, pacman_grid_x, pacman_grid_y, pacman['direction']
                    )

                    best_dir = ghost['dir']
                    min_dist = float('inf')
                    possible_directions = []
                    
                    reverse_dir = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}.get(ghost['dir'])
                    
                    for d in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                        next_grid_x = self.to_grid(current_x_center + (GHOST_SPEED if d == 'RIGHT' else -GHOST_SPEED if d == 'LEFT' else 0))
                        next_grid_y = self.to_grid(current_y_center + (GHOST_SPEED if d == 'DOWN' else -GHOST_SPEED if d == 'UP' else 0))

                        if self.get_tile_type(current_x_center, current_y_center) != 1 and d != reverse_dir:
                            dist = abs(next_grid_x - target_grid_x) + abs(next_grid_y - target_grid_y)
                            
                            if dist < min_dist:
                                min_dist = dist
                                best_dir = d
                                
                    if best_dir != ghost['dir']:
                        ghost['dir'] = best_dir

            new_x_center, new_y_center = current_x_center, current_y_center
            if ghost['dir'] == 'UP': new_y_center -= GHOST_SPEED
            elif ghost['dir'] == 'DOWN': new_y_center += GHOST_SPEED
            elif ghost['dir'] == 'LEFT': new_x_center -= GHOST_SPEED
            elif ghost['dir'] == 'RIGHT': new_x_center += GHOST_SPEED
            
            if not self.is_collision(new_x_center, new_y_center):
                ghost['x'] = new_x_center + TILE_SIZE // 2
                ghost['y'] = new_y_center + TILE_SIZE // 2
            else:
                ghost['dir'] = choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

            # colisao pacman-ghost
            pacman_center_x = pacman['x'] + TILE_SIZE // 2
            pacman_center_y = pacman['y'] + TILE_SIZE // 2
            
            ghost_center_x = ghost['x'] 
            ghost_center_y = ghost['y']

            # checa sobreposição de tiles
            if (self.to_grid(pacman_center_x) == self.to_grid(ghost_center_x) and 
                self.to_grid(pacman_center_y) == self.to_grid(ghost_center_y)):
                
                if ghost['state'] == 'vulnerable':
                    pacman['score'] += 200
                    # posição inicial
                    ghost['x'], ghost['y'] = 9 * TILE_SIZE + TILE_SIZE//2, 1 * TILE_SIZE + TILE_SIZE//2
                    ghost['state'] = 'normal'
                elif ghost['state'] == 'normal' and pacman['power_up_timer'] == 0:
                    self.game_status = 'game_over'
                    
            if self.game_status == 'game_over':
                break

    def activate_power_up(self):
        for ghost in self.ghosts:
            ghost['state'] = 'vulnerable'

    def deactivate_power_up(self):
        for ghost in self.ghosts:
            ghost['state'] = 'normal'

    def check_win(self):
        if self.dots_remaining == 0:
            self.game_status = 'win'

game = Game()
game_running = False
server_socket = None

def game_loop():
    global game_running
    FPS = 60

    while not game.player_connected:
        sleep(1)

    game.game_status = "Running"
    game_running = True

    while game_running:
        start_time = time()

        with state_lock:
            if game.game_status == "Running":
                if game.client_movement_queue:
                    direction = game.client_movement_queue
                    game.client_movement_queue = None
                    game.update_pacman(direction)

                game.update_ghosts()
                game.check_win()
            if game.game_status != "Running" and game.game_status != "waiting_for_players":
                game_running = False
        
        
        elapsed_time = time() - start_time
        sleep_time = (1.0 / FPS) - elapsed_time
        if sleep_time > 0:
            sleep(sleep_time)
            
    with state_lock:
        game.reset_game()
        print(f"Partida encerrada. Status final: {game.game_status}. Estado reiniciado.")


def handle_client(conn, addr):
    print(f"Novo cliente conectado: {addr}")
    global game_running
    
    with state_lock:
        if game.player_connected:
            print(f"Conexão {addr} rejeitada: Já existe um jogador principal.")
            conn.close()
            return
        
        game.player_connected = True
        print("Jogador Pac-Man conectado.")
        if not game_running:
            threading.Thread(target=game_loop).start()

    try:
        while True:
            conn.settimeout(0.01)
            message = None
            try:
                data = conn.recv(4096)
                if not data:
                    break 
                    
                message = json.loads(data.decode('utf-8'))
            except socket.timeout:
                pass
            except json.JSONDecodeError:
                 print("Erro ao decodificar JSON.")
                 continue

            if message:
                if message['command'] == 'MOVE' and game.game_status == 'running':
                    with state_lock:
                        game.client_movement_queue = message['direction'] 
                
                elif message['command'] == 'DISCONNECT':
                    break

            with state_lock:
                current_state = game.serializer()
                try:
                    conn.sendall(json.dumps(current_state).encode('utf-8'))
                except:
                    break 

            if current_state['status'] != 'running' and current_state['status'] != 'waiting_for_players':
                break


    finally:
        print(f"Cliente desconectado: {addr}")
        with state_lock:
            game.player_connected = False
            
        conn.close()

def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Servidor rodando em {HOST}:{PORT}")
        
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
            
    except OSError as e:
        print(f"Não foi possível iniciar o servidor: {e}")
    except KeyboardInterrupt:
        print("\nServidor desligado.")
    finally:
        if server_socket:
            server_socket.close()

if __name__ == '__main__':
    start_server()