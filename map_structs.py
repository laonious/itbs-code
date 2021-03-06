import pygame, sys, random, itertools, math, pickle
from pygame.locals import *
from utils import load_image
class Effect:
    def __init__(self,name,size,framerate,duration):
        filename = 'effects/'+name+'/'+name
        number_images = framerate*duration
        self.data = []
        for i in range(0,number_images):
            image,rect = load_image(filename+str(i+1).zfill(3)+'.png',-1)
            self.data.append(image)
        self.duration = duration
        self.size = size
        self.width = self.size[0]
        self.height = self.size[1]
        self.animation_frame_time = 1000/framerate
        self.births = []
        self.counters = []
        self.locations = []
        self.last_animated = []


    def Create(self,location):
        self.locations.append(location)
        self.counters.append(0)
        self.births.append(pygame.time.get_ticks())
        self.last_animated.append(pygame.time.get_ticks())

    def Draw(self,surface,index,pos):
        tile_width = 80
        tile_height = 40
        loc = self.locations[index]
        x = pos[0]+tile_width/2-self.width/2+tile_width/2*(loc[1]%2)
        y = pos[1]-tile_height/2*loc[1]-self.height
        #surface.blit(self.data,[x,y],((9,self.height*self.counters[index]),(self.width,self.height)))
        try:
            surface.blit(self.data[self.counters[index]],[x,y])
        except IndexError:
            return

    def Update(self):
        for loc in self.locations:
            if pygame.time.get_ticks()-self.last_animated[self.locations.index(loc)]>=self.animation_frame_time:
                self.counters[self.locations.index(loc)] = self.counters[self.locations.index(loc)]+1
                self.last_animated[self.locations.index(loc)] = pygame.time.get_ticks()
            if pygame.time.get_ticks()-self.births[self.locations.index(loc)] >= self.duration*1000:
                self.births.remove(self.births[self.locations.index(loc)])
                self.counters.remove(self.counters[self.locations.index(loc)])
                self.last_animated.remove(self.last_animated[self.locations.index(loc)])
                self.locations.remove(self.locations[self.locations.index(loc)])

                

        


class Tile:
    def __init__(self,image,water=0):
        self.water = water
        if water:
            self.images=[]
            self.rects=[]
            rect = pygame.Rect((0,0),(80,60))
            self.frames = 2*71
            for i in range(0,self.frames-1):
                im = pygame.Surface((80,60))
                image,rect = load_image('water_images/water-'+str(71-abs(i-71))+'.png',-1)
                im.blit(image,(0,0),rect)
                image,rect = load_image('water_images/water_side-'+str(71-abs(i-71))+'.png',(231,77,189))
                pygame.draw.polygon(image, (231,77,189,255), ((0,22),(40,41),(0,41)))
                image.set_alpha(80)
                im.blit(image,(0,20),rect)
                self.images.append(im)
                self.rects.append(rect)
                self.images[i].set_colorkey((0,0,0))
                self.images[i]=self.images[i].convert_alpha()
                self.last_animated = pygame.time.get_ticks()
                self.animation_frame_time = 42
            self.image_count = 0
            self.image = self.images[0]
        else:
            self.image,self.rect = load_image(image,-1)
            self.image = self.image.convert()

    def Update(self):
        if self.water==0:
            return
        else:
            if pygame.time.get_ticks() - self.last_animated >=self.animation_frame_time:
                self.last_animated = pygame.time.get_ticks()
                self.image_count=(self.image_count+1)%len(self.images)
            self.image = self.images[self.image_count]

class Object:
    def __init__(self, image):
        self.image,self.rect = load_image(image,-1)
        self.image = self.image.convert()

    def Draw(self,surface,loc):
        x=loc[0]
        y=loc[1]-self.image.get_height()
        surface.blit(self.image,[x,y])

class Map:
    def __init__(self, size,layout,ratio,tile_size):
        self.size = size
        self.layout = layout
        tile_list = pickle.load(open('data/tile_list.li','r'))
        #self.tiles = [Tile('cobblestone.png'),Tile('grass.png'),Tile('water',1),Tile('dungeon.png')]
        self.tiles = []
        self.effects = []
        for tile in tile_list:
            if str(tile)!='water': self.tiles.append(Tile(str(tile)+'.png'))
            else: self.tiles.append(Tile('water',1))
        self.objects = [Object('tree.png'),Object('log.png')]
        self.ratio = ratio
        self.tile_size = tile_size

        width = 800
        height = 450
        self.pos = [(width-tile_size*(self.size[0]+1))/2,
                (height-tile_size/(2*ratio)*self.size[1])/2+50]


    def Update(self,cursor):
        top_left = self.pos
        x=cursor.pos[0]*self.tile_size+top_left[0]
        y=cursor.pos[1]*self.tile_size/self.ratio+top_left[1]-self.tile_size/(2*self.ratio)#*level
        x = x+self.tile_size/2*(cursor.pos[1]%2)
        y = y-self.tile_size/(2*self.ratio)*(cursor.pos[1]+1)

        if x<0 + self.tile_size:
            self.pos[0]+=self.tile_size/10
        if y<0 + 1.5*self.tile_size:
            self.pos[1]+=self.tile_size/10

        if x>800-self.tile_size*2:
            self.pos[0]-=self.tile_size/10

        if y>450-self.tile_size/2:
            self.pos[1]-=self.tile_size/10
        
        for tile in self.tiles:
            tile.Update()

        for effect in self.effects:
            effect.Update()

    def Draw(self,surface,cursors,actors):
        self.Update(cursors[-1])
        width = surface.get_width()
        height = surface.get_height()
        tile_size = self.tile_size
        ratio = self.ratio 
        top_left = self.pos
        font = pygame.font.Font(None,16)

#        for level in range(1,self.layout[0]+1):
#           
#            for j in range(0, self.size[1]):
#                for i in range(0, self.size[0]):
        for j in range(0, self.size[1]):
            for i in range(0,self.size[0]):
                for level in range(1,self.layout[0]+1):
                    x=i*tile_size+top_left[0]
                    y=j*tile_size/ratio+top_left[1]-tile_size/(2*ratio)*level

                    if self.layout[level][i + j * self.size[0]]!=-1:
                        surface.blit(self.tiles[self.layout[level][i+j*self.size[0]]].image,
                                                [x+tile_size/2*(j%2),y-tile_size/(2*ratio)*(j+1)])
                        # Draw Cursor
                        for cursor in cursors:
                            if [i,j]==cursor.pos and (self.layout[level+1][i + j * self.size[0]]==-1 or level==self.layout[0]):
                                cursor.Draw(surface,[x+tile_size/2*(j%2),y-tile_size/(2*ratio)*(j+1)])
                        # Draw Objects
                        if self.layout[-1][i + j * self.size[0]]!=-1 and (self.layout[level+1][i + j * self.size[0]]==-1 or level==self.layout[0]):
                                
                            self.objects[self.layout[-1][i + j * self.size[0]]].Draw(surface,
                            [x+tile_size/2*(j%2),y-tile_size/(2*ratio)*(j)+tile_size/(4*ratio)])
                       # Draw Actors
                        for actor in actors:
                            if [i,j]==actor.pos and (self.layout[level+1][i + j * self.size[0]]==-1 or level==self.layout[0]):
                                if level==actor.level:
                                    actor.Draw(surface,[x,y])#[x+tile_size/2*(j%2),y-tile_size/(2*ratio)*(j)+tile_size/(4*ratio)])

                
                        # Draw Effects
                        for effect in self.effects:
                            if [i,j] in effect.locations and (self.layout[level+1][i + j * self.size[0]]==-1 or level==self.layout[0]):
                                effect.Draw(surface,effect.locations.index([i,j]),[x,y])

                        #self.Draw_Grid(surface,(x+tile_size/2*(j%2),y-tile_size/(2*ratio)*(j)),tile_size,ratio)
                        #text = font.render('('+str(i)+','+str(j)+')',1,(250,0,0))
                        #surface.blit(text,(x+tile_size/2*(j%2)+30,y-tile_size/(2*ratio)*(j)))


    def Draw_Grid(self,surface,loc,width,ratio):
        color = (200,200,200)
        pygame.draw.line(surface,color, loc, (loc[0]+width/2,loc[1]-width/(2*ratio)))
        pygame.draw.line(surface,color, loc, (loc[0]+width/2,loc[1]+width/(2*ratio)))
        pygame.draw.line(surface,color,(loc[0]+width,loc[1]), (loc[0]+width/2,loc[1]-width/(2*ratio)))
        pygame.draw.line(surface,color,(loc[0]+width,loc[1]), (loc[0]+width/2,loc[1]+width/(2*ratio)))



class Cursor:
    def __init__(self,color,width,ratio,layout):
        self.color = color
        self.pos = [3,3]
        #self.surface = pygame.Surface((width,width/ratio))
        #self.surface.set_colorkey((0,0,0))
        #self.surface.set_alpha(220)
        self.layout = layout
        self.flash_count = 0
        #pygame.draw.polygon(self.surface,(0,128,0),(
        #    (2,width/(2*ratio)),
        #    (width/2,0),
        #    (width-2,width/(2*ratio)-2),
        #    (width/2-2,width/ratio-2)))
        #pygame.draw.polygon(self.surface,self.color,((8,width/(2*ratio)),
        #                                             (width/2,4),
        #                                             (width-8,width/(2*ratio)),
        #                                             (width/2,width/ratio-5)))
        self.surface,self.rect = load_image('cursor.png',-1)
        self.surface_head,self.rect_head = load_image('cursor_head.png',-1)
        

    def Draw(self,surface,pos):
        self.flash_count=(self.flash_count+1)%140
        self.surface.set_alpha(105+35*math.cos(self.flash_count*2*3.14159/140))
        surface.blit(self.surface,pos)
        surface.blit(self.surface_head,[pos[0],pos[1]-75-5*math.cos(self.flash_count*2*3.14159/35)])

    def Move(self,direction):
        old_pos_x,old_pos_y = self.pos
        if direction=='right':
            self.pos[1]+=1
            if self.pos[1]%2==0:
                self.pos[0]+=1
        if direction=='left':
            self.pos[1]-=1
            if self.pos[1]%2!=0:
                self.pos[0]-=1
        if direction=='down':
            self.pos[1]+=1
            if self.pos[1]%2!=0:
                self.pos[0]-=1
        if direction=='up':
            self.pos[1]-=1
            if self.pos[1]%2==0:
                self.pos[0]+=1
        if self.pos[0] + self.layout[1][0]*self.pos[1] > len(self.layout[0]) or self.pos[0]>=self.layout[1][0] or self.pos[1]>=self.layout[1][1]: 
            self.pos = [old_pos_x,old_pos_y]
        elif self.pos[0]<0 or self.pos[1]<0: 
            self.pos=[old_pos_x,old_pos_y]
        elif self.layout[0][self.pos[0] + self.layout[1][0]*self.pos[1]]==-1:
            self.pos = [old_pos_x,old_pos_y]
        
        
class Blue_Cursor(Cursor):
    def __init__(self,width,ratio,layout):
        self.pos = [3,3]
        self.layout = layout
        self.flash_count = 0
        self.surface,self.rect = load_image('cursor_blue.png',-1)
        self.surface_head=pygame.Surface((0,0))

class Red_Cursor(Cursor):
    def __init__(self,width,ratio,layout):
        self.pos = [3,3]
        self.layout = layout
        self.flash_count = 0
        self.surface,self.rect = load_image('cursor_red.png',-1)
        self.surface_head=pygame.Surface((0,0))

