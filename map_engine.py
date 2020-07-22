import pygame, random
import configparser
from pygame import Color, Surface, draw
from pygame.locals import *
from PIL import Image
import os

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


# Speichert die Daten eines Tile-Typs:
class TileType(object):
    # Im Konstruktor speichern wir den Namen
    # und erstellen das Rect (den Bereich) dieses Typs auf der Tileset-Grafik.
    def __init__(self, name, color, width, height):
        self.name = name
        self.rect = pygame.rect.Rect(0, 0, width, height)
        self.color = color
        self.width = width
        self.height = height
        self.status = -1

# Speichert die Daten eines Tile-Typs bei der Verwendung einer Tileset-Grafik:
class TileTypeGraphic(object):
    # Im Konstruktor speichern wir den Namen
    # und erstellen das Rect (den Bereich) dieses Typs auf der Tileset-Grafik.
    def __init__(self, name, tile_set_grafic_coords, cost, width, height):
        self.name = name
        self.tile_set_grafic_coords = tile_set_grafic_coords
        self.width = width
        self.height = height
        self.cost = cost
        self.status = -1
    
# Verwaltet eine Liste mit Tile-Typen.
class Tileset(object):
    # Im Konstruktor erstellen wir ein leeres Dictionary für die Tile-Typen.
    def __init__(self, colorkey, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.color = colorkey
        self.tile_types = dict()

    def load_tile_table(self, filename, width, height):
        # Tilesetgrafik laden und einzelne Tiles zurückgeben
        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width//width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height//height):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table

    # Neuen Tile-Typ hinzufügen.
    def add_tile(self, name, color):
        self.tile_types[name] = TileType(name, color, self.tile_width, self.tile_height)
            

    def add_tile_graphic(self, name, cost, tile_set_grafic_coords):
        # Fügt den Tile-Types einen neuen Typen mit den Koordinaten in der Tileset-Grafik hinzu
        self.tile_types[name] = TileTypeGraphic(name, tile_set_grafic_coords, cost, self.tile_width, self.tile_height)
    
    # Versuchen, einen Tile-Type über seinen Namen in der Liste zu finden.
    # Falls der Name nicht existiert, geben wir None zurück.
    def get_tile(self, name):
        try:
            return self.tile_types[name]
        except KeyError:
            return None

# Die Tilemap Klasse verwaltet die Tile-Daten, die das Aussehen der Karte beschreiben.
class Tilemap(object):
    def __init__(self, screen, position_finish, font_UI, map_file='none', tile_set_file='none'):
        # Wir erstellen ein neues Tileset.
        # Hier im Tutorial fügen wir manuell vier Tile-Typen hinzu.
        self.tileset = Tileset((255, 0, 255), 32, 32)
        self.screen = screen
        self.position_finish = position_finish

        # Wenn True, dann werden auf den jeweiligen Tiles Infos angezeigt
        self.print_tileinfo = True
        self.print_pre_tile_lines = False

        # Erstellen einer leeren Liste für die Tile Daten.
        self.tiles = list()

        # Array für die Status-Text-Box
        self.status_text = []

        if tile_set_file == "none":
            # Farben, falls keine Tileset-Grafik eingestellt wurde
            self.tileset.add_tile("blank",WHITE)
            self.tileset.add_tile("wall",BLACK)
            self.tileset.add_tile("start",(255, 0, 100))
            self.tileset.add_tile("finish",RED)
            self.tileset.add_tile("route",(0, 0, 255))
            self.tileset.add_tile("closed",GREY)
            self.tileset.add_tile("open",YELLOW)
            self.use_tile_set_file = False
        else:
            # Wenn es eine Tileset-Grafik gibt, dann Grafik laden und Tiles zuweisen
            self.tile_set_table = self.tileset.load_tile_table(tile_set_file, 32, 32)
            self.tileset.add_tile_graphic("blank",1,(0,0))
            self.tileset.add_tile_graphic("wall",-1,(31,0))
            self.tileset.add_tile_graphic("forest",-1,(5,0))
            self.tileset.add_tile_graphic("start",1,(19,7))
            self.tileset.add_tile_graphic("finish",1,(28,4))
            self.tileset.add_tile_graphic("route",1,(0,7))
            self.tileset.add_tile_graphic("closed",1,(16,6))
            self.tileset.add_tile_graphic("open",1,(0,6))
            self.use_tile_set_file = True
        
        if map_file == "none":
            # Die Größe der Maps in Tiles.
            self.width = MAP_WIDTH
            self.height = MAP_HEIGHT
            self.create_random_map()
        else:
            self.create_map_from_file(map_file)
        
        # Festlegen der Startposition der Kamera auf die Mitte der Karte.
        self.camera_x = self.width/2
        self.camera_y = self.height/2
        # print(DISPLAY_WIDTH, self.width)
        # Zoomfaktor anpassen
        if self.width < self.height:
            self.tileset.tile_width = DISPLAY_WIDTH/self.width
            self.tileset.tile_height = DISPLAY_WIDTH/self.height
        else:
            self.tileset.tile_height = DISPLAY_HEIGHT/self.height
            self.tileset.tile_width = DISPLAY_HEIGHT/self.height
        scaled_size = (int(MAP_HEIGHT*self.tileset.tile_height), int(MAP_WIDTH*self.tileset.tile_height))
        self.map_image_scaled = pygame.transform.scale(self.map_image, scaled_size)
        self.tiles[10][10] = "start"
        self.tiles[self.position_finish[0]][self.position_finish[1]] = "finish"
        # print(self.tiles)
        pygame.font.init()
        # font_size = 12*self.tileset.tile_width/40
        font_size = 7
        # print(int(font_size),self.tileset.tile_width)
        self.font = pygame.font.SysFont("futura", int(font_size))
        self.font_line_height = 15
        self.font_UI = font_UI

    # Liefert den Tiletypen an gegebener Position zurück
    def get_tile_type( self, position):
        """Liefert den Tiletypen an gegebener Position zurück"""
        return self.tiles[position[0]][position[1]]
    
    def zoom(self,zoom_rate,focus_center):
        # print()
        # print('Tilesize vorher: ', self.tileset.tile_height, self.tileset.tile_width)
        # print('Camera Vorher: ', self.camera_y,self.camera_x)
        # print('Focus Screen: ', focus_center)
        # 
        tile_height_old = self.tileset.tile_height
        tile_focus_y = focus_center[0]/(self.tileset.tile_height*self.tileset.tile_height)
        tile_focus_x = focus_center[1]/(self.tileset.tile_width*self.tileset.tile_width)
        # print('Focus Tile: ', tile_focus_y, tile_focus_x)
        self.camera_y = self.camera_y + tile_focus_y
        self.camera_x = self.camera_x + tile_focus_x
        # print('Camera Nachher: ', self.camera_y,self.camera_x)
        # tile_middle_x = int(DISPLAY_WIDTH/self.tileset.tile_width/2+tile_focus_x)
        # tile_middle_y = int(DISPLAY_HEIGHT/self.tileset.tile_height/2+tile_focus_y)
        self.tileset.tile_height += zoom_rate
        self.tileset.tile_width += zoom_rate
        # print('Tilesize nachher: ', self.tileset.tile_height, self.tileset.tile_width)
        if self.tileset.tile_height < 1:
            self.tileset.tile_height = 1
        if self.tileset.tile_width < 1:
            self.tileset.tile_width = 1

        # Neue Schriftgröße berechnen
        font_size = 12*self.tileset.tile_width/40
        self.font_line_height = 15*self.tileset.tile_width/40
        self.font = pygame.font.SysFont("futura", int(font_size))

        # Grundkarte skalieren
        # zoom_factor = 1/tile_height_old*self.tileset.tile_height
        scaled_size = (int(MAP_HEIGHT*self.tileset.tile_height), int(MAP_WIDTH*self.tileset.tile_height))
        # scaled_size = (int(self.map_image_scaled.get_width()*zoom_factor), int(self.map_image_scaled.get_height()*zoom_factor))
        # print(zoom_factor, self.map_image_scaled.get_size(), scaled_size)
        self.map_image_scaled = pygame.transform.scale(self.map_image, scaled_size)
        # print(MAP_HEIGHT,MAP_WIDTH, self.map_image.get_size(), self.map_image_scaled.get_size(), self.tileset.tile_height)

    def create_map_from_file(self, map_file):
            global MAP_HEIGHT, MAP_WIDTH
            # Karte laden
            map_file = Image.open(map_file)

            # MAP_WIDTH und MAP_HEIGHT aus den Dimensionen der Karte erstellen
            MAP_WIDTH, MAP_HEIGHT = map_file.size
            
            # Leere Grafik der Karte anlegen
            self.map_image = pygame.Surface((MAP_WIDTH*32, MAP_HEIGHT*32))

            # X und Y durchgehen und nach der Pixelfarbe die Tiles anlegen
            for x in range(0,MAP_WIDTH):
                self.tiles.append(list())
                for y in range(0, MAP_HEIGHT):
                    # print(x,y, map_file.size)
                    pixel_color = map_file.getpixel((y,x))
                    if pixel_color < 200:
                        self.tiles[x].append('wall')
                    # elif pixel_color >= 10 and pixel_color < 200:
                    #     self.tiles[x].append('forest')
                    else:
                        self.tiles[x].append('blank')
            self.width = MAP_WIDTH
            self.height = MAP_HEIGHT
            for x in range(0, len(self.tiles)):
                for y in range(0, len(self.tiles[x])):
                    # print(x,y, map_file.size, len(self.tiles[y]))
                    tile = self.tileset.get_tile(self.tiles[y][x])
                    self.map_image.blit(self.tile_set_table[tile.tile_set_grafic_coords[1]][tile.tile_set_grafic_coords[0]], (x*32, y*32))

            
            scaled_size = (MAP_HEIGHT*32,MAP_WIDTH*32)
            
            self.map_image_scaled = pygame.transform.scale(self.map_image, scaled_size)
            # print(MAP_HEIGHT,MAP_WIDTH, map_file.size, self.map_image.get_size(), self.map_image_scaled.get_size(), self.tileset.tile_height)
            # quit()
            # Grafik der Karte erstellen
            
    def create_random_map( self):
        """ Erstellt eine Karte, die per Zufall mit Mauern gefüllt wird """
        # Manuelles Befüllen der Tile-Liste:
        # Jedes Feld bekommt ein zufälliges Tile zugewiesen.
        for i in range(0, self.height):
            self.tiles.append(list())
            for j in range(0, self.width):
                x = random.randint(0, 30)
                if x < 28:
                    self.tiles[i].append("blank")
                else:
                    self.tiles[i].append("wall")

    # Alternative render-Funktion
    # Die ursprüngliche ist kästchenbasiert, diese soll pixelgenau sein.
    # Hier rendern wir den sichtbaren Teil der Karte.
    def render(self, screen,navi_tiles):
        
        font = self.font
        tile_width = self.tileset.tile_width
        tile_height = self.tileset.tile_height

        # Die Größe der Tiles berechnen
        scaled_size = (int(MAP_HEIGHT*tile_height), int(MAP_WIDTH*tile_height))
        scaled_size_tile = (int(tile_height), int(tile_width))
        
        # Anzahl Tiles, die auf den Screen passen
        tile_count_x = DISPLAY_WIDTH/tile_width
        tile_count_y = DISPLAY_HEIGHT/tile_height

        # Von der Kameraposition links oben berechnen. Hiervon aus werden die TILES platziert.
        camera_null_x = int(self.camera_x-tile_count_x/2)
        camera_null_y = int(self.camera_y-tile_count_y/2)


        # Grundkarte zeichnen
        position1 = (-camera_null_x * tile_width,-camera_null_y * tile_height)
        
        screen.blit(self.map_image_scaled, position1)
        # return True
        # Zeilenweise durch die Tiles durchgehen.
        for y in range(0, int(screen.get_height() / tile_height) + 1):
            # Die Kamera Position mit einbeziehen.
            ty = y + camera_null_y
            if ty >= self.height or ty < 0:
                continue
            # Die aktuelle Zeile zum einfacheren Zugriff speichern.
            line = self.tiles[ty]
            # Und jetzt spaltenweise die Tiles rendern.
            # tx und ty ist die Position im Array
            # x und y ist die Position des Tiles auf dem Screen
            for x in range(0, int(screen.get_width() / tile_width) + 1):
                # Auch hier müssen wir die Kamera beachten.
                tx = x + camera_null_x
                # print( int(screen.get_width() / tile_width) + 1, tx, len(line))
                if tx >= self.width or tx < 0 or tx >= len(line):
                    continue
                # Wir versuchen, die Daten des Tiles zu bekommen.
                # tilename = line[tx]
                navi_tile = navi_tiles[ty][tx]
                tilename = navi_tile.type
                if tilename == "blank" or tilename == "wall":
                    continue
                tile = self.tileset.get_tile(tilename)
                # Falls das nicht fehlschlägt können wir das Tile auf die screen-Surface blitten.
                if tile is not None:
                    # screen.fill(tile.color, tile.rect)
                    tile_pos_x = x*tile_width
                    tile_pos_y = y*tile_height
                    # if navi_tiles[y][x].status == 0:
                    #     pygame.draw.rect(screen,YELLOW, pygame.rect.Rect(tile_pos_x,tile_pos_y,tile_width,tile_height),1)
                    # else:
                    #     pygame.draw.rect(screen,tile.color, pygame.rect.Rect(tile_pos_x,tile_pos_y,tile_width,tile_height),1)
                    if navi_tile.status == 0 and not tilename == 'route':
                        continue
                        # if not self.use_tile_set_file:
                        #     # self.map_image_scaled = pygame.transform.scale(self.map_image, scaled_size)
                        #     screen.blit(pygame.transform.scale(self.tile_set_table[tile.tile_set_grafic_coords[1]][tile.tile_set_grafic_coords[0]], scaled_size_tile), (tile_pos_x, tile_pos_y))
                        # else:
                        #     # print(tile.tile_set_grafic_coords, len(self.tile_set_table))
                        #     screen.blit(pygame.transform.scale(self.tile_set_table[tile.tile_set_grafic_coords[1]][tile.tile_set_grafic_coords[0]], scaled_size_tile), (tile_pos_x, tile_pos_y))
                        #     # screen.fill(BLACK, pygame.rect.Rect(tile_pos_x,tile_pos_y,tile_width,tile_height))
                    else:
                        if self.use_tile_set_file:
                            tileset_graphic_y = tile.tile_set_grafic_coords[0]
                            tileset_graphic_x = tile.tile_set_grafic_coords[1]
                            # print(tile.name, tile.tile_set_grafic_coords, tileset_graphic_x, tileset_graphic_y)
                            # print(len(self.tile_set_table),tileset_graphic_x)
                            # print(self.tile_set_table[tileset_graphic_x])
                            # print(len(self.tile_set_table[tileset_graphic_x]))
                            tileset_graphic = self.tile_set_table[tileset_graphic_x][tileset_graphic_y]
                            
                            screen.blit(pygame.transform.scale(tileset_graphic, scaled_size_tile), (tile_pos_x, tile_pos_y))
                        else:
                            screen.fill(tile.color, pygame.rect.Rect(tile_pos_x,tile_pos_y,tile_width,tile_height))
                    # print(tile_pos_y,tile_pos_x)

                    # pre_tile-Vektoren zeichnen
                    if not navi_tile.pre_tile == -1 and self.print_pre_tile_lines == True:
                        pre_tile = navi_tile.pre_tile
                        pre_tile_x = pre_tile[0]
                        pre_tile_y = pre_tile[1]
                        # pre_tile_pos = (pre_tile_y*tile_height, pre_tile_x*tile_width)
                        pre_tile_pos = (position1[0] + (pre_tile_y*tile_height + tile_width/2), position1[1] + (pre_tile_x*tile_width + tile_width/2))
                        # print(position1, tile_height, tile_width, y, x, navi_tile.position, tile_pos_y, tile_pos_x, '|', pre_tile, pre_tile_y, pre_tile_x, pre_tile_pos, camera_null_y, camera_null_x)
                        
                        pygame.draw.line(screen, BLUE, (tile_pos_x+tile_width/2,tile_pos_y+tile_height/2), pre_tile_pos, 1)
                    
                    # Texteinblendungen über den einzelnen Tiles rendern
                    if navi_tile and not tilename == "wall" and tile_width > 15 and self.print_tileinfo:
                        # Estimated Cost einfügen
                        text_to_render = str(navi_tile.get_cost_from_start())
                        # text_to_render = tilename

                        # Kosten vom Start
                        if not tilename == "closed":
                            text_to_render = str(navi_tile.get_cost_from_start())
                        tile_text_cost = font.render(text_to_render, True, (200, 0, 200), BLACK)
                        screen.blit(tile_text_cost,(tile_pos_x+1,tile_pos_y+1))
                        # Tileposition einfügen
                        # text_to_render = str(ty) + "," + str(tx)
                        text_to_render = str(round(navi_tile.get_total_cost(),2))
                        tile_text_pos = font.render(text_to_render, True, (200, 0, 200), BLACK)
                        screen.blit(tile_text_pos,(tile_pos_x+1,tile_pos_y+self.font_line_height))
        self.print_status_text()

    def render_one_tile(self, tile):
        tile_width = self.tileset.tile_width
        tile_height = self.tileset.tile_height

        # Die Größe des Tiles berechnen
        scaled_size_tile = (int(tile_height), int(tile_width))
        
        # Anzahl Tiles, die auf den Screen passen
        tile_count_x = DISPLAY_WIDTH/tile_width
        tile_count_y = DISPLAY_HEIGHT/tile_height

        # Von der Kameraposition links oben berechnen. Hiervon aus werden die TILES platziert.
        camera_null_x = int(self.camera_x-tile_count_x/2)
        camera_null_y = int(self.camera_y-tile_count_y/2)

        ty = tile.position[1] + camera_null_y
        tx = tile.position[0] + camera_null_x

        tile_type = self.tileset.get_tile(tile.type)

        if tile_type is not None:
            # screen.fill(tile.color, tile.rect)
            tile_pos_x = tile.position[1]*tile_width
            tile_pos_y = tile.position[0]*tile_height
            
            
            if not self.use_tile_set_file:
                # self.map_image_scaled = pygame.transform.scale(self.map_image, scaled_size)
                self.screen.blit(pygame.transform.scale(self.tile_set_table[tile.tile_set_grafic_coords[0]][tile.tile_set_grafic_coords[1]], scaled_size_tile), (tile_pos_x, tile_pos_y))
            else:
                self.screen.fill(RED, pygame.rect.Rect(tile_pos_x,tile_pos_y,tile_width,tile_height))

    def add_status_text(self, text):
        if len(self.status_text) > 2:
            self.status_text.pop(0)
        self.status_text.append(text)

    def add_status_text_with_clear(self, text):
        self.status_text = []
        self.add_status_text(text)

    def print_status_text(self):
        line = 1
        for text in self.status_text:
            text_to_print = self.font_UI.render(text, True, (200, 0, 200), BLACK)
            self.screen.blit(text_to_print,(self.screen.get_width()/2-(text_to_print.get_width()/2),self.screen.get_height()-80+line*15))
            line += 1