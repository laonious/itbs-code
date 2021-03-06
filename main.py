#!/usr/bin/env python2.7

VERSION = "0.4"

try:
    import sys
    import random
    import math
    import os
    import getopt
    import pygame
    import utils
    import pickle
    from socket import *
    from pygame.locals import *
    import map_structs
    import character_structs
    import menu_structs
    import item_structs
    import weapons
except ImportError, err:
    print "couldn't load module. %s" % (err)
    sys.exit(2)

tile_size = 80
map_size = [16,26]
ISO_RATIO = 2
class OverLord:
    def __init__(self,size):
        self.size = size
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.size)
        self.canvas = pygame.Surface(self.size)

        # Load players
        self.actors=[
            character_structs.Actor('characters/assassin.png',{'name':'Assassin','hp':12,'mp':10,'speed':5,'agility':3,'strength':2},1,[5,3,3]),
            character_structs.Actor('characters/sniper.png',{'hp':12,'mp':10,'speed':5,'agility':2,'strength':2,'name':'Sniper'},1,[3,4,4])
                ]



#       Test weapon
        self.actors[0].character.Equip_Weapon(weapons.shortBow)
        self.actors[1].character.Equip_Weapon(weapons.longBow)
            
        # Set Background to White
        self.canvas.fill((250,250,250))
#       Load map
        f = open('maps/testmap004.map','r')
        demo_map = pickle.load(f)
        f.close()
#       Load enemies
        f = open('maps/testmap004.en','r')
        enemies = pickle.load(f)
        f.close()
        for enemy in enemies:
            self.actors.append(character_structs.Actor(enemy[0],enemy[1],enemy[2],enemy[3]))
            # Equip a basic weapon on the enemy
            self.actors[-1].character.Equip_Weapon(weapons.shortBow)


        self.maps=[map_structs.Map(map_size,demo_map,ISO_RATIO,tile_size)]
        self.cursor = map_structs.Cursor((0,250,0),tile_size,2,
                [demo_map[1],map_size])
        self.actors[0].pos=[10,14]

        self.menus=[]

        # Load Effects
        self.effects=[self.maps[0].effects.append(map_structs.Effect('fire',[120,320],24,7))]

    def newturn(self):
        print 'NEW TURN'
        turn_list = utils.sort_actors(self.actors)
        # Move Cursor to first actor
        [self.cursor.pos[0],self.cursor.pos[1]]=self.actors[turn_list[0]].pos

        # Prepare actors for turn new turn
        for actor in self.actors:
            actor.NewTurn()


        # Activate turn menu
        self.menus[0].Activate(actor,self.maps[0],self.cursor,self.actors)
        return turn_list

    def run(self):
#           Initialize menus
            self.menus = [menu_structs.Player_Turn(),menu_structs.Menu_Move(),menu_structs.Player_Attack(),menu_structs.YN_Prompt(),menu_structs.Character_Status()]
            next_step = []
            turn = 0

            # Keep Track of current player
            turn_list=[]
            output=[]
            # This variable tells the main engine whether or not to handle key input
            HANDLE_INPUT_MYSELF = 1
            while 1:
                # Caps the framerate 
                self.clock.tick(60)

                # Prints the framerate
                #print str(self.clock.get_fps())
                # Create Turn List
                if turn_list==[]:
                    turn_list = self.newturn()
                    turn+=1

                if next_step!=[]:
                    if next_step[0]=='move':
                        self.menus[1].Activate(self.actors[turn_list[0]],self.maps[0],self.cursor,self.actors)

                    elif next_step[0]=='animating':
                        if self.actors[turn_list[0]].moving==1:
                            next_step.insert(0,'animating')
                    elif next_step[0]=='turn':
                        self.menus[0].Activate(self.actors[turn_list[0]],self.maps[0],self.cursor,self.actors)
                    elif next_step[0]=='attack':
                        self.menus[2].Activate(self.actors[turn_list[0]],self.maps[0],self.cursor,self.actors)
                    elif next_step[0][0]=='y':
                        self.menus[3].Activate(self.actors[turn_list[0]],self.maps[0],self.cursor,self.actors)
                    elif next_step[0]=='status':
                        self.menus[4].Activate(self.actors[turn_list[0]],self.maps[0],self.cursor,self.actors)
                    elif next_step[0]=='done_with_turn':
                        turn_list.remove(turn_list[0])
                        try:
                            [self.cursor.pos[0],self.cursor.pos[1]]=self.actors[turn_list[0]].pos
                            self.menus[0].Activate(actor,self.maps[0],self.cursor,self.actors)
                        except IndexError: pass
                    elif next_step[0]=='back':
                        HANDLE_INPUT_MYSELF = 1

                    next_step.remove(next_step[0])

#               Get input from active menus
                for menu in self.menus:
                    if menu.active==1 and (next_step==[] or
                                           next_step[0]!='animating'):
                        HANDLE_INPUT_MYSELF = 0
                        output = menu.Handle_Input(pygame.event.get())
                        if output!=[] and output!=None:
                            for out in output:
                                next_step.insert(0,out)

                #   Update the actors if they are moving
                for actor in self.actors:
                    if actor.moving==1:
                        actor.Move(self.maps[0])



                if HANDLE_INPUT_MYSELF==1:
                    # Handle Input:
                    for event in pygame.event.get():
	                    if event.type==KEYDOWN:
	                        if event.key==K_ESCAPE: sys.exit()
                                #if event.key==K_e:
                                   #self.maps[0].effects[0].Create([self.cursor.pos[0],self.cursor.pos[1]])
                                   #self.maps[0].effects.append(self.effects[0])
                                   #self.maps[0].effects[-1].location[0]=self.cursor.pos[0]
                                   #self.maps[0].effects[-1].location[1]=self.cursor.pos[1]
	                        if event.key==K_RIGHT:
	                            self.cursor.Move('right')
	                        if event.key==K_LEFT:
	                            self.cursor.Move('left')
	                        if event.key==K_DOWN:
	                            self.cursor.Move('down')
	                        if event.key==K_UP:
	                            self.cursor.Move('up')
                                if event.key==K_c:
                                    if utils.selected_actor(self.cursor,self.actors)!=0:
                                        self.menus[4].Activate(actor,self.maps[0],self.cursor,self.actors)
	                        if event.key==K_a:
	                            [self.cursor.pos[0],self.cursor.pos[1]]=self.actors[turn_list[0]].pos
                                    # This next line is buggy for some reason
                                    #self.menus[0].Activate(actor,self.maps[0],self.cursor,self.actors)
	                        if event.key==K_SPACE:
	                            for actor in self.actors:
	                                if self.cursor.pos==actor.pos:
	                                    try:
	                                        if actor==self.actors[turn_list[0]]:
	                                            self.menus[0].Activate(actor,self.maps[0],self.cursor,self.actors)
	                                    except IndexError: 
	                                        turn_list = []
	                                    
                           
#               Drawing routines
                self.canvas.fill((0,0,0))
                drawn = 0
                for m in self.menus:
                    if m.active==1:
                        m.Draw_Map(self.canvas,self.maps[0],self.cursor,self.actors)
                        drawn = 1
                if drawn == 0:
                    self.maps[0].Draw(self.canvas,[self.cursor],self.actors)
                for actor in self.actors:
                    if actor.pos==self.cursor.pos and self.menus[2].active==0 and self.menus[4].active==0:
                        actor.Display_Info(self.canvas)

                # Draw Map and Text
                text=pygame.font.Font(None,36).render('Turn '+str(turn),1,(250,250,250))
                self.canvas.blit(text,(700,0))
                self.screen.blit(self.canvas,[0,0])
                pygame.display.flip()




if __name__ == '__main__':
    game = OverLord((800,450))
    game.run()
