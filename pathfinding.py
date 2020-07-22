import pygame, random
import operator
from collections import OrderedDict
from pygame import Color
from pygame.locals import *
from priorityqueue import PriorityQueue
from navi import Navi
from map_engine import Tilemap
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

BG_COLOR = BLACK
DISPLAY_WIDTH = int(config['DISPLAY']['DISPLAY_WIDTH'])
DISPLAY_HEIGHT = int(config['DISPLAY']['DISPLAY_HEIGHT'])
MAP_WIDTH = int(config['MAP']['MAP_WIDTH'])
MAP_HEIGHT = int(config['MAP']['MAP_HEIGHT'])
MAP_FILE = config['MAP']['MAP_FILE']
TILESET_FILE = config['MAP']['TILESET_FILE']

running = True
    
def print_open_list(screen, open_list, font):
    x = DISPLAY_WIDTH - 70
    y = 24
    tile_text_pos = font.render('openlist', True, (200, 0, 200), BLACK)
    screen.blit(tile_text_pos,(x,10))
    open_list.sort(key=lambda x: x.estimated_cost_to_finish, reverse=False)
    for tile in open_list:
        text_to_render = str(tile.position)+': '+str(tile.estimated_cost_to_finish)
        tile_text_pos = font.render(text_to_render, True, (200, 0, 200), BLACK)
        screen.blit(tile_text_pos,(x,y))
        y += 14

def print_closed_list(screen, closed_list, font):
    x = 10
    y = 24
    tile_text_pos = font.render('closedlist', True, (200, 0, 200), BLACK)
    screen.blit(tile_text_pos,(x,10))
    for tile in closed_list:
        text_to_render = str(tile.position)+': '+str(tile.route_cost)
        tile_text_pos = font.render(text_to_render, True, (200, 0, 200), BLACK)
        screen.blit(tile_text_pos,(x,y))
        y += 14
                 
def main():
    global running, screen

    pygame.init()
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.font.init()
    font_UI = pygame.font.SysFont("futura", int(10))
    
    pygame.display.set_caption("Routefinding")
    screen.fill(BG_COLOR)
    pygame.display.update()

    position_finish = (20,20)
    # Tilemap erstellen
    map = Tilemap(screen, position_finish, font_UI, MAP_FILE,TILESET_FILE)
    navi = Navi((10,10),position_finish,map)

    ticks = 0
    drag_active = False
    navi.navi_active = False
    setting_start_point = False
    while running:
        ticks += 1
        screen.fill(BG_COLOR)
        
        # Routenberechnung
        if ticks > 0 and navi.navi_active == True:
            ticks = 0
            navi.navi_step()
        ev = pygame.event.get()
        for event in ev:
            mouse_pos = getPos()
            
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    rel_pos = (getPos()[1] - (DISPLAY_HEIGHT/2),getPos()[0] - (DISPLAY_WIDTH/2))
                    map.zoom(.5,rel_pos)
                elif event.button == 5:
                    rel_pos = ((DISPLAY_HEIGHT/2) - getPos()[1], (DISPLAY_WIDTH/2) - getPos()[0])
                    map.zoom(-.5,rel_pos)
                else:
                    drag_active = True
                    drag_start = getPos()
                    # print("drag_active")
            if event.type == pygame.MOUSEMOTION:
                if drag_active and not drag_start == mouse_pos:
                    distance = (drag_start[0]- mouse_pos[0],drag_start[1] - mouse_pos[1])
                    map.camera_x += distance[0]/map.tileset.tile_width
                    map.camera_y += distance[1]/map.tileset.tile_height
                    # print("drag_move")
                    # print(mouse_pos[0] - drag_start[0], mouse_pos[1] - drag_start[1])
                    drag_start = mouse_pos
            if event.type == pygame.MOUSEBUTTONUP:
                if setting_start_point == True:
                    drag_active = False
                    setting_start_point = False
                    tile_selected_y = mouse_pos[1]/map.tileset.tile_height
                    tile_selected_x = mouse_pos[0]/map.tileset.tile_width
                    
                    tmp_y = int((map.camera_y-(DISPLAY_HEIGHT/map.tileset.tile_height)/2)+tile_selected_y)
                    tmp_x = int((map.camera_x-(DISPLAY_WIDTH/map.tileset.tile_width)/2)+tile_selected_x)
                    position_finish = (tmp_y, tmp_x)
                    if position_finish == (10,10):
                        continue
                    position_last_finish = map.position_finish
                    navi = Navi(position_last_finish,position_finish,map)
                    map.position_finish = position_finish
                    map.add_status_text('Neues Ziel gesetzt: '+str(position_finish))
                    navi.navi_active = True
                    continue
                if drag_active == True and not drag_start == mouse_pos:
                    drag_active = False
                    print("drag_end")
                    map.camera_x = round(map.camera_x)
                    map.camera_y = round(map.camera_y)
                    continue
                else:
                    print("Tile_info!")
                    drag_active = False
                    
                    tile_selected_y = mouse_pos[1]/map.tileset.tile_height
                    tile_selected_x = mouse_pos[0]/map.tileset.tile_width
                    
                    tmp_y = int((map.camera_y-(DISPLAY_HEIGHT/map.tileset.tile_height)/2)+tile_selected_y)
                    tmp_x = int((map.camera_x-(DISPLAY_WIDTH/map.tileset.tile_width)/2)+tile_selected_x)
                    # navi.navi_step(navi.tiles[tmp_y][tmp_x])
                    map.tiles[tmp_y][tmp_x] = "wall"
                    navi.tiles[tmp_y][tmp_x].type = "wall"
                    print("Tile:{0},{1}".format(tmp_x,tmp_y),mouse_pos)
                    map.add_status_text_with_clear("Tile:{0},{1}".format(tmp_x,tmp_y))
                    print("Kosten:",navi.tiles[tmp_y][tmp_x].estimated_cost_to_finish)
                    map.add_status_text("Kosten:" + str(navi.tiles[tmp_y][tmp_x].estimated_cost_to_finish))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    map.camera_x -= 1
                if event.key == pygame.K_RIGHT:
                    map.camera_x += 1
                # Und das gleiche nochmal für die y-Position.
                if event.key == pygame.K_UP:
                    map.camera_y -= 1
                if event.key == pygame.K_DOWN:
                    map.camera_y += 1
                if event.key == pygame.K_e:
                    # tile_middle_x = int(DISPLAY_WIDTH/map.tileset.tile_width/2+map.camera_x)
                    # tile_middle_y = int(DISPLAY_HEIGHT/map.tileset.tile_height/2+map.camera_y)
                    # map.tileset.tile_height += 5
                    # map.tileset.tile_width += 5
                    # font_size = 12*map.tileset.tile_width/40
                    # map.font_line_height = 15*map.tileset.tile_width/40
                    # map.font = pygame.font.SysFont("futura", int(font_size))
                    rel_pos = (getPos()[1] - (DISPLAY_HEIGHT/2),getPos()[0] - (DISPLAY_WIDTH/2))
                    map.zoom(2,rel_pos)
                if event.key == pygame.K_s:
                    # Neuen Startpunkt setzen und alles auf Anfang
                    setting_start_point = True
                    map.add_status_text('Mit Mausklick neues Ziel setzen')
                if event.key == pygame.K_i:
                    if map.print_tileinfo == True:
                        map.print_tileinfo = False
                    else:
                        map.print_tileinfo = True
                if event.key == pygame.K_l:
                    if map.print_pre_tile_lines == True:
                        map.print_pre_tile_lines = False
                    else:
                        map.print_pre_tile_lines = True
                if event.key == pygame.K_f:
                    navi.route_finished(navi.get_finish_tile())
                if event.key == pygame.K_q:
                    # map.tileset.tile_height -= 5
                    # map.tileset.tile_width -= 5
                    # font_size = 12*map.tileset.tile_width/40
                    # map.font_line_height = 15*map.tileset.tile_width/40
                    # map.font = pygame.font.SysFont("futura", int(font_size))
                    rel_pos = (getPos()[1] - (DISPLAY_HEIGHT/2),getPos()[0] - (DISPLAY_WIDTH/2))
                    map.zoom(-2,rel_pos)
                if event.key == pygame.K_n:
                    if navi.navi_active == True:
                        navi.navi_active = False
                    else:
                        navi.navi_active = True
                if event.key == pygame.K_m:
                    navi.navi_step()
                if event.key == pygame.K_c:
                    navi.show_closed_list()
                if event.key == pygame.K_o:
                    navi.show_open_list()    
        # print(map.camera_x,map.camera_y)
        map.render(screen,navi.tiles)
        # print_open_list(screen,navi.get_open_list(),font_UI)
        # print_closed_list(screen,navi.get_closed_list(),font_UI)
        pygame.display.update()

def getPos():
    pos = pygame.mouse.get_pos()
    # print(pos)
    return pos

if __name__ == '__main__':
    main()