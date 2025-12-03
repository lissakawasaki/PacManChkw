import socket
import json
import time
import random
import threading
import pygame
import math

HOST = "127.0.0.1"
PORT = 65432
TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 20
FPS = 60 

WALL = 1
PELLET = 0
POWER_UP = 2
EMPTY = 9

class GameServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()
        self.clients = []
        self.running = True
        
        self.mode_timer = 0
        self.current_mode = 'scatter' 
        self.last_mode_switch = time.time()
        
        self.reset_game()

    def generate_map(self):
        layout = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 1, 1, 1, 9, 1, 1, 9, 1, 1, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 9, 1, 1, 9, 9, 1, 1, 9, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 9, 1, 9, 9, 9, 9, 1, 9, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 1, 9, 1, 1, 1, 1, 1, 1, 9, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 2, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        return layout

    def reset_game(self):
        self.game_map = self.generate_map()
        self.status = 'waiting_for_players'
        self.last_mode_switch = time.time()
        self.current_mode = 'scatter'
        
        self.pacman = {
            'x': TILE_SIZE * 10,
            'y': TILE_SIZE * 15,
            'direction': 'RIGHT',
            'next_direction': 'RIGHT',
            'score': 0,
            'power_up_timer': 0,
            'speed': 4
        }

        self.ghosts = [
            {'id': 'f1', 'x': 10 * TILE_SIZE, 'y': 8 * TILE_SIZE, 'direction': 'LEFT', 'state': 'normal', 'speed': 2, 'scatter_target': (GRID_WIDTH-2, 1)}, 
            {'id': 'f2', 'x': 10 * TILE_SIZE, 'y': 10 * TILE_SIZE, 'direction': 'UP', 'state': 'normal', 'speed': 2, 'scatter_target': (1, 1)},
            {'id': 'f3', 'x': 9 * TILE_SIZE, 'y': 10 * TILE_SIZE, 'direction': 'UP', 'state': 'normal', 'speed': 2, 'scatter_target': (GRID_WIDTH-2, GRID_HEIGHT-2)},
            {'id': 'f4', 'x': 11 * TILE_SIZE, 'y': 10 * TILE_SIZE, 'direction': 'UP', 'state': 'normal', 'speed': 2, 'scatter_target': (1, GRID_HEIGHT-2)},
        ]

    def get_state(self):
        return {
            'status': self.status,
            'map': self.game_map,
            'pacman': self.pacman,
            'ghosts': self.ghosts
        }

    def is_wall(self, grid_x, grid_y):
        if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
            return self.game_map[grid_y][grid_x] == WALL
        return True

    def can_move(self, x, y, direction, speed):
        new_x, new_y = x, y
        if direction == 'UP': new_y -= speed
        elif direction == 'DOWN': new_y += speed
        elif direction == 'LEFT': new_x -= speed
        elif direction == 'RIGHT': new_x += speed

        rect = pygame.Rect(new_x, new_y, TILE_SIZE, TILE_SIZE)
        
        def get_tile(px, py):
            tx = int(px // TILE_SIZE)
            ty = int(py // TILE_SIZE)
            if 0 <= ty < GRID_HEIGHT and 0 <= tx < GRID_WIDTH:
                return self.game_map[ty][tx]
            return 1

        margin = 2
        tl = get_tile(rect.left + margin, rect.top + margin)
        tr = get_tile(rect.right - margin, rect.top + margin)
        bl = get_tile(rect.left + margin, rect.bottom - margin)
        br = get_tile(rect.right - margin, rect.bottom - margin)

        if tl == 1 or tr == 1 or bl == 1 or br == 1:
            return False, x, y
        
        return True, new_x, new_y

    def get_target_tile(self, ghost):
        pac_gx = int(self.pacman['x'] // TILE_SIZE)
        pac_gy = int(self.pacman['y'] // TILE_SIZE)
        pac_dir = self.pacman['direction']
        
        if self.current_mode == 'scatter':
            return ghost['scatter_target']

        if ghost['id'] == 'f1':
            return (pac_gx, pac_gy)

        elif ghost['id'] == 'f2':
            tx, ty = pac_gx, pac_gy
            if pac_dir == 'UP': ty -= 4
            elif pac_dir == 'DOWN': ty += 4
            elif pac_dir == 'LEFT': tx -= 4
            elif pac_dir == 'RIGHT': tx += 4
            return (tx, ty)

        elif ghost['id'] == 'f3':
            pivot_x, pivot_y = pac_gx, pac_gy
            if pac_dir == 'UP': pivot_y -= 2
            elif pac_dir == 'DOWN': pivot_y += 2
            elif pac_dir == 'LEFT': pivot_x -= 2
            elif pac_dir == 'RIGHT': pivot_x += 2
            
            blinky = next((g for g in self.ghosts if g['id'] == 'f1'), None)
            if blinky:
                b_gx = int(blinky['x'] // TILE_SIZE)
                b_gy = int(blinky['y'] // TILE_SIZE)
                
                vec_x = pivot_x - b_gx
                vec_y = pivot_y - b_gy
                return (b_gx + vec_x * 2, b_gy + vec_y * 2)
            return (pac_gx, pac_gy)

        elif ghost['id'] == 'f4':
            ghost_gx = int(ghost['x'] // TILE_SIZE)
            ghost_gy = int(ghost['y'] // TILE_SIZE)
            dist = math.sqrt((ghost_gx - pac_gx)**2 + (ghost_gy - pac_gy)**2)
            
            if dist > 8:
                return (pac_gx, pac_gy)
            else:
                return ghost['scatter_target']

        return (pac_gx, pac_gy)

    def update_ghosts(self):
        current_time = time.time()
        elapsed = current_time - self.last_mode_switch
        
        if self.current_mode == 'scatter' and elapsed > 7:
            self.current_mode = 'chase'
            self.last_mode_switch = current_time
            for g in self.ghosts:
                if g['state'] == 'normal':
                    g['direction'] = self.get_opposite(g['direction'])
        elif self.current_mode == 'chase' and elapsed > 20:
            self.current_mode = 'scatter'
            self.last_mode_switch = current_time
            for g in self.ghosts:
                if g['state'] == 'normal':
                    g['direction'] = self.get_opposite(g['direction'])

        possible_directions = ['UP', 'LEFT', 'DOWN', 'RIGHT']

        for ghost in self.ghosts:
            if self.pacman['power_up_timer'] > 0:
                ghost['state'] = 'vulnerable'
            else:
                ghost['state'] = 'normal'

            if int(ghost['x']) % TILE_SIZE == 0 and int(ghost['y']) % TILE_SIZE == 0:
                
                grid_x = int(ghost['x'] // TILE_SIZE)
                grid_y = int(ghost['y'] // TILE_SIZE)
                
                valid_moves = []
                opposite = self.get_opposite(ghost['direction'])
                
                for d in possible_directions:
                    nx, ny = grid_x, grid_y
                    if d == 'UP': ny -= 1
                    elif d == 'DOWN': ny += 1
                    elif d == 'LEFT': nx -= 1
                    elif d == 'RIGHT': nx += 1
                    
                    if not self.is_wall(nx, ny):
                        if d != opposite:
                            valid_moves.append(d)
                
                if not valid_moves:
                    if not self.is_wall(grid_x, grid_y): 
                        valid_moves.append(opposite)

                if valid_moves:
                    if ghost['state'] == 'vulnerable':
                        ghost['direction'] = random.choice(valid_moves)
                    else:
                        target_x, target_y = self.get_target_tile(ghost)
                        best_dir = valid_moves[0]
                        min_dist = float('inf')
                        
                        for d in valid_moves:
                            nx, ny = grid_x, grid_y
                            if d == 'UP': ny -= 1
                            elif d == 'DOWN': ny += 1
                            elif d == 'LEFT': nx -= 1
                            elif d == 'RIGHT': nx += 1
                            
                            dist = (nx - target_x)**2 + (ny - target_y)**2
                            
                            if dist < min_dist:
                                min_dist = dist
                                best_dir = d
                        
                        ghost['direction'] = best_dir

            moved, nx, ny = self.can_move(ghost['x'], ghost['y'], ghost['direction'], ghost['speed'])
            if moved:
                ghost['x'] = nx
                ghost['y'] = ny
            else:
                ghost['direction'] = random.choice(possible_directions)

    def get_opposite(self, direction):
        if direction == 'UP': return 'DOWN'
        if direction == 'DOWN': return 'UP'
        if direction == 'LEFT': return 'RIGHT'
        if direction == 'RIGHT': return 'LEFT'
        return 'RIGHT'

    def update_pacman(self):
        if self.pacman['next_direction'] != self.pacman['direction']:
            center_x = self.pacman['x'] + TILE_SIZE / 2
            center_y = self.pacman['y'] + TILE_SIZE / 2
            grid_x = int(center_x // TILE_SIZE)
            grid_y = int(center_y // TILE_SIZE)
            target_center_x = grid_x * TILE_SIZE + TILE_SIZE / 2
            target_center_y = grid_y * TILE_SIZE + TILE_SIZE / 2
            diff_x = abs(center_x - target_center_x)
            diff_y = abs(center_y - target_center_y)
            threshold = self.pacman['speed']

            if self.pacman['next_direction'] in ['UP', 'DOWN']:
                if diff_x <= threshold:
                    snap_x = grid_x * TILE_SIZE
                    is_free, _, _ = self.can_move(snap_x, self.pacman['y'], self.pacman['next_direction'], self.pacman['speed'])
                    if is_free:
                        self.pacman['x'] = snap_x
                        self.pacman['direction'] = self.pacman['next_direction']

            elif self.pacman['next_direction'] in ['LEFT', 'RIGHT']:
                if diff_y <= threshold:
                    snap_y = grid_y * TILE_SIZE
                    is_free, _, _ = self.can_move(self.pacman['x'], snap_y, self.pacman['next_direction'], self.pacman['speed'])
                    if is_free:
                        self.pacman['y'] = snap_y
                        self.pacman['direction'] = self.pacman['next_direction']

        moved, nx, ny = self.can_move(self.pacman['x'], self.pacman['y'], self.pacman['direction'], self.pacman['speed'])
        
        if moved:
            self.pacman['x'] = nx
            self.pacman['y'] = ny

        center_x = self.pacman['x'] + TILE_SIZE // 2
        center_y = self.pacman['y'] + TILE_SIZE // 2
        grid_x = int(center_x // TILE_SIZE)
        grid_y = int(center_y // TILE_SIZE)

        if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
            tile = self.game_map[grid_y][grid_x]
            if tile == PELLET: 
                self.game_map[grid_y][grid_x] = 3 
                self.pacman['score'] += 10
            elif tile == POWER_UP: 
                self.game_map[grid_y][grid_x] = 3
                self.pacman['score'] += 50
                self.pacman['power_up_timer'] = 600 

        if self.pacman['power_up_timer'] > 0:
            self.pacman['power_up_timer'] -= 1

    def check_collisions(self):
        pac_rect = pygame.Rect(self.pacman['x'], self.pacman['y'], TILE_SIZE, TILE_SIZE)
        
        for ghost in self.ghosts:
            ghost_rect = pygame.Rect(ghost['x'], ghost['y'], TILE_SIZE, TILE_SIZE)
            
            if pac_rect.inflate(-10, -10).colliderect(ghost_rect.inflate(-10, -10)):
                if ghost['state'] == 'vulnerable':
                    ghost['x'] = 10 * TILE_SIZE
                    ghost['y'] = 9 * TILE_SIZE
                    self.pacman['score'] += 200
                else:
                    self.status = 'game_over'

        pellets_left = sum(row.count(PELLET) + row.count(POWER_UP) for row in self.game_map)
        if pellets_left == 0:
            self.status = 'win'

    def game_loop(self):
        print(f"Server started on {HOST}:{PORT}")
        while self.running:
            start_time = time.time()
            self.handle_clients()
            if self.status == 'running':
                self.update_pacman()
                self.update_ghosts()
                self.check_collisions()
            elapsed = time.time() - start_time
            sleep_time = max(0, (1.0 / FPS) - elapsed)
            time.sleep(sleep_time)

    def handle_clients(self):
        self.server_socket.settimeout(0.001) 
        try:
            client, addr = self.server_socket.accept()
            print(f"Player connected from {addr}")
            self.clients.append(client)
            if self.status == 'waiting_for_players' or self.status == 'game_over' or self.status == 'win':
                self.reset_game()
                self.status = 'running'
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error accepting: {e}")

        for client in self.clients[:]:
            try:
                client.settimeout(0.001)
                data = client.recv(4096)
                if data:
                    message = json.loads(data.decode('utf-8'))
                    command = message.get('command')
                    if command == 'CONNECT':
                        client.sendall(json.dumps(self.get_state()).encode('utf-8'))
                    elif command == 'MOVE':
                        direction = message.get('direction')
                        self.pacman['next_direction'] = direction
                        client.sendall(json.dumps(self.get_state()).encode('utf-8'))
                    elif command == 'GET_STATE':
                        client.sendall(json.dumps(self.get_state()).encode('utf-8'))
                    elif command == 'DISCONNECT':
                        self.clients.remove(client)
                        client.close()
                        print("Player disconnected.")
                        if not self.clients:
                            self.status = 'waiting_for_players'
            except socket.timeout:
                pass
            except (ConnectionResetError, BrokenPipeError):
                if client in self.clients:
                    self.clients.remove(client)
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"Client error: {e}")

if __name__ == '__main__':
    pygame.init() 
    server = GameServer()
    try:
        server.game_loop()
    except KeyboardInterrupt:
        print("\nServer stopping...")
    finally:
        server.server_socket.close()