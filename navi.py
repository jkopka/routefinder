from priorityqueue import PriorityQueue
from math import sqrt
from pygame import Color
import configparser

# Konfiguration
config = configparser.ConfigParser()
config.read('config.ini')

WHITE = Color(config['COLOR']['WHITE'])
BLUE = Color(config['COLOR']['BLUE'])
GREEN = Color(config['COLOR']['GREEN'])
RED = Color(config['COLOR']['RED'])
YELLOW = Color(config['COLOR']['YELLOW'])
BLACK = Color(config['COLOR']['BLACK'])
GREY = Color(config['COLOR']['GREY'])

# BG_COLOR = (10,   30,   30)
BG_COLOR = WHITE
DISPLAY_WIDTH = int(config['DISPLAY']['DISPLAY_WIDTH'])
DISPLAY_HEIGHT = int(config['DISPLAY']['DISPLAY_HEIGHT'])
MAP_WIDTH = int(config['MAP']['MAP_WIDTH'])
MAP_HEIGHT = int(config['MAP']['MAP_HEIGHT'])

# Navi-Klassen
class TileInfo:
    def __init__(self, position, tile_type, estimated_cost_to_finish, cost_from_start,pre_tile):
        self.position = position
        self.estimated_cost_to_finish = estimated_cost_to_finish
        self.cost_from_start = cost_from_start
        self.pre_tile = pre_tile
        self.route_cost = cost_from_start + estimated_cost_to_finish
        self.type = tile_type

        # Status des Tiles
        # -1 > Nicht bearbeitet
        # 0 > Bearbeitet
        self.status = -1

    def set_cost_from_start(self, cost):
        self.cost_from_start = cost
    
    def get_cost_from_start(self):
        return self.cost_from_start

    def set_route_cost(self, cost):
        self.route_cost = cost

    def get_route_cost(self):
        return self.route_cost
    
    def get_estimated_cost_to_finish(self):
        return self.estimated_cost_to_finish
    
    def get_total_cost(self):
        return self.route_cost

class Navi:
    def __init__(self, position_start, position_finish, map):
        tiles = []
        self.open_list = PriorityQueue()
        self.closed_list = PriorityQueue()
        # queue = PriorityQueue()
        self.map = map
        self.finish_reached = False
        self.route = []
        self.position_start = position_start
        self.position_finish = position_finish
        self.open_list.insert(TileInfo(position_start,self.get_estimated_cost_to_finish(position_start),0,-1,-1))
        for y in range(0,map.height):
            tiles.append([])
            for x in range(0, map.width):
                tile = TileInfo((y,x), map.tiles[y][x], self.get_estimated_cost_to_finish((y,x)),99999,-1)
                tiles[y].append(tile)
        self.tiles = tiles
        self.navi_active = False
        self.recursion_level = 0
        self.max_recursion_level = 100
        self.use_diagonal_tiles = True

        # Array für die Abfrage der umgebenden Tiles
        self.surroundings = []
        if self.use_diagonal_tiles == True:
            self.surroundings.append((-1,-1))
            self.surroundings.append((-1,+1))
            self.surroundings.append((+1,-1))
            self.surroundings.append((+1,+1))
        self.surroundings.append((-1,0))
        self.surroundings.append((0,-1))
        self.surroundings.append((0,+1))
        self.surroundings.append((+1,0))

    def navi_step(self, tile_work='next'):
        # map = self.map
        # print('navistep')
        self.recursion_level += 1
        if tile_work == 'next':
            tile_work = self.open_list.get_and_delete()
        
        # pre_tile = self.tiles[tile_work.position[0]][tile_work.position[1]].pre_tile

        # Den Vorgänger-Tile des work-Tiles holen
        pre_tile = self.get_pre_tile(tile_work)
        # Wenn der Tile > -1 ist, hole die Kosten zum Start.
        if not pre_tile == -1:
            pre_tile_cost_from_start = self.tiles[pre_tile[0]][pre_tile[1]].cost_from_start
        else:
            pre_tile_cost_from_start = -1
        
        # Wenn der Work-Tile die Zielposition, also das Ziel erreicht ist.
        if tile_work.position == self.position_finish:
            self.map.add_status_text_with_clear("FINISH")
            tile_work.set_route_cost(pre_tile_cost_from_start + 1)
            self.route_finished(tile_work)
            self.finish_reached = True
        if pre_tile_cost_from_start >= 99999:
            pre_tile_cost_from_start = 0

        # Work-Tile: Die Kosten zum Start sind Pre-Tile + 1
        tile_work_cost_from_start = pre_tile_cost_from_start + 1
        tile_work.set_cost_from_start(tile_work_cost_from_start)
        tile_work.set_route_cost(self.get_estimated_cost_to_finish(tile_work.position)+tile_work.cost_from_start)
        tile_work.status = 0
        # Der Work-Tile wurde berechnet und kann also auf die Closed-List
        self.closed_list.insert(tile_work)
        self.tiles[tile_work.position[0]][tile_work.position[1]].type = "closed"

        # Um weiter zu machen, holen wir uns die umgebenden Tiles
        surrounding_tiles = self.get_surrounding_tiles(tile_work.position)
        
        # Solange wir noch nicht alle Tiles bearbeitet haben, durchlaufen wir die while-Schleife
        while not surrounding_tiles.isEmpty():
            # print(surrounding_tiles.get_size())
            surrounding_tile = surrounding_tiles.get_and_delete()
            
            if surrounding_tile == False:
                # print("Surround: no next tiles")
                break
            if surrounding_tile.type == "wall":
                # print('Surround: wall')
                continue
            
            tile_cost_from_start = tile_work_cost_from_start + 1

            if self.closed_list.exist(surrounding_tile):
                # Wenn ein Tile bereits in der closedlist ist, wurde er schon mal hinzugefügt
                # Es wird dann gecheckt, ob ...?
                # print('Surround: is in closedlist')
                continue
            elif self.open_list.exist(surrounding_tile):
                # Wenn ein Tile bereits in der openlist ist, wurde er schon mal hinzugefügt
                # Es wird dann gecheckt, ob ...?
                # print('Surround: is in openlist')
                tile_from_open_list = self.open_list.get_tile_and_delete(surrounding_tile)
                # print(tile_from_open_list.cost_from_start, tile_cost_from_start)
                if tile_from_open_list.cost_from_start + 1 >= tile_cost_from_start:
                    # print('Surround: Neuer Weg ist teurer')
                    continue
                else:
                    # print('Surround: Neuer Weg ist günstiger')
                    tile_from_open_list.cost_from_start =  surrounding_tile.cost_from_start+1
                    tile_from_open_list.set_route_cost(self.get_estimated_cost_to_finish(tile_from_open_list.position)+tile_work_cost_from_start)
                    self.open_list.insert(tile_from_open_list)
                    continue
            else:
                if surrounding_tile.position == tile_work.pre_tile:
                    # Wenn der umliegende Tile der vorherige vom tile_work ist, kann er ignoriert werden
                    continue
                # Wenn bis hierher nichts dagegen spricht, ist der Tile legitim, um ihn in nem navistep zu bearbeiten
                # pre-tile festlegen
                surrounding_tile.pre_tile = tile_work.position
                # Den pre-tile auch in der tiles.Liste festlegen
                self.tiles[surrounding_tile.position[0]][surrounding_tile.position[1]].pre_tile = tile_work.position

                # In die open-list einfügen
                self.open_list.insert(surrounding_tile)
            
                # Entsprechenden Tile als open markieren
                self.tiles[surrounding_tile.position[0]][surrounding_tile.position[1]].type = "open"
        
        # print("Open List: ", self.open_list.get_size())
        # print("Closed List: ", self.closed_list.get_size())
        # print(self.finish_reached)
        # if self.finish_reached == False and self.recursion_level < self.max_recursion_level:
            
        #     self.navi_step()
        self.recursion_level = 0
        return (tile_work.position, tile_work.route_cost)
        
        # self.navi_step(tile.position,position)

    def route_finished(self,tile):
        """ Route wurde gefunden! """
        route = []
        route.append(tile.position)
        next_tile = tile.pre_tile
        while True:
            route.append(next_tile)
            if len(route) > 1000:
                print('Finish: Route > 1000')
                break
            # print(next_tile)
            next_tile = self.tiles[next_tile[0]][next_tile[1]].pre_tile
            if next_tile == self.position_start:
                print('Finish: Start erreicht.')
                break
            if next_tile == -1:
                break
            
            
            
        for tile_position in route:
            self.tiles[tile_position[0]][tile_position[1]].type = "route"
        self.map.add_status_text("Kosten: "+ str(tile.get_route_cost()))
        print("Kosten: ", tile.get_route_cost())
        self.map.add_status_text("Länge Route: "+ str(len(route)))
        print("Länge Route: ",len(route))
        # print(route)
        self.navi_active = False
        self.position_start = tile.position

    def get_next_navi_tile(self, surrounding_tiles, position, last_position):
        """ Liefert den nächsten Navi-Tile zurück. Checkt, ob alle Bedingungen eingehalten werden."""
        # Bedingungen:
        # 1. Tiletype != wand
        # 2. Tiletype != navi
        # 3. Tiletype != last_position
        # 4. Tile ist in self.queue
        for tile in surrounding_tiles:
            if not tile:
                return False
            tile_type = self.map.get_tile_type(tile.position)
            print(tile.position, tile_type)
            if not tile_type == "wall" and not tile_type == "navi" and not tile.position == last_position:
                return tile
    
        print("Sackgasse?")
        return False
        # if tile_surround.position == self.position_finish:
        #     print("FINISH")
        #     print("Routenlänge: ",len(self.route))

    def get_estimated_cost_to_finish(self, position):
        """ Liefert die estimated cost an gegebener Position zurück."""
        distance_to_point = float(sqrt((position[0]-self.position_finish[0])**2 + (position[1]-self.position_finish[1])**2))
        return distance_to_point
    
    def get_pre_tile(self, tile):
        """ Liefert den Vorgänger zurück """
        # print('get_pre_tile()')
        surrounding_tiles = self.get_surrounding_tiles(tile.position, order='start')
        # print('surrounding_tiles: ', surrounding_tiles)
        pre_tile = surrounding_tiles.get_and_delete()
        # print('pre_tile: ', pre_tile)
        return pre_tile.position

    def get_surrounding_tiles(self, position, order='finish'):
        """ Liefert eine Queue der angrenzenden Tiles zurück."""
        tiles = PriorityQueue(order)
        # print('Order: ', order)
        # self.surroundings

        for surround in self.surroundings:
            # Ränder abfragen
            # y unten
            if position[0] == len(self.tiles)-1 and surround[0] == +1:
                continue
            # y oben
            if position [0] == 0 and surround[0] == -1:
                continue
            # x rechts
            if position[1] == len(self.tiles[0])-1 and surround[1] == +1:
                continue
            # x links
            if position[1] == 0 and surround[1] == -1:
                continue

            x = position[1]+surround[1]
            y = position[0]+surround[0]
            tiles.insert(self.tiles[y][x])
        
        # Wenn Position am unteren Rande der y-Achse ist
        
        # tiles.sort(key=lambda x: x.estimated_cost_to_finish, reverse=False)
        return tiles

    def show_open_list(self):
        for item in self.open_list.queue:
            print(item.position, item.get_estimated_cost_to_finish())
        
    def get_open_list(self):
        return self.open_list.queue
    
    def get_closed_list(self):
        return self.closed_list.queue
    
    def show_closed_list(self):
        for item in self.closed_list.queue:
            print(item.position)

    def get_finish_tile(self):
        return self.tiles[self.position_finish[0]][self.position_finish[1]]