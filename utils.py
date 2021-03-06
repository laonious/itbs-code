import os,pygame
from pygame.constants import *
from global_vars import *

def calculate_weapon_damage(attacker,target):
#   Base Damage
    damage = attacker.character.strength+attacker.character.e_weapon.damage

    # Height Difference
    if attacker.character.e_weapon.attack_range==1: damage = max(damage + (attacker.level - target.level)*2,0)
    else: damage = max(damage + attacker.level - target.level,0)
    return damage

def selected_actor(cursor, actors):
    s = 0
    for a in actors:
        if a.pos==[cursor][-1].pos:
            s = a
    return s

def load_image(name, colorkey=None):
	fullname = os.path.join('data',name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', name
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()

#def normal_to_iso(coords)
#    iso 
def move_in_coords(pos,direction,layout):
        old_pos_x,old_pos_y = pos
        pos_x=pos[0]
        pos_y=pos[1]
        if direction=='right':
            pos_y+=1
            if pos_y%2==0:
                pos_x+=1
        if direction=='left':
            pos_y-=1
            if pos_y%2!=0:
                pos_x-=1
        if direction=='down':
            pos_y+=1
            if pos_y%2!=0:
                pos_x-=1
        if direction=='up':
            pos_y-=1
            if pos_y%2==0:
                pos_x+=1
        if pos_x<0 or pos_y<0: 
            [pos_x,pos_y]=[old_pos_x,old_pos_y]
        return [pos_x,pos_y]

def check_for_water(current_map,pos):
    for level in range(1,current_map.layout[0]):
        try:
            if current_map.layout[level][pos[0]+current_map.size[0]*pos[1]]==2:
                return 1
        except IndexError:
            return 0

    return 0

def top_level(current_map,loc):
    top = 0
    for level in range(1,current_map.layout[0]):
        try:
            if current_map.layout[level][loc[0]+current_map.size[0]*loc[1]]!=-1:
                top = level
        except IndexError:
            return 1
    return top

def draw_attack_info(canvas,damage,hit):
#   Draw a window
    pygame.draw.rect(canvas,(0,0,0,100),((325,300),(150,50)))
#   Draw the text
    font = pygame.font.Font(None,18)

    text = font.render('Damage: '+str(damage),1,(250,250,250))
    canvas.blit(text,(350,300))
    text = font.render('Hit Chance: '+str(hit)+'%',1,(250,250,250))
    canvas.blit(text,(350,318))

def draw_circle(actor,current_map,actors,radius,people_ok=0):
    agility = actor.character.agility
    # Add center
    openList=[]
    parentList = [actor.pos]
    childList=[]
    ancestry=[]
    for i in range(0,radius):
        for parent in parentList:
            for direction in ['up','down','left','right']:
                node = move_in_coords(parent,direction,[current_map.layout,[8,16]])
                if check_for_water(current_map,node)==0:
                    if top_level(current_map,node)-top_level(current_map,parent)<= agility:
                        try:
                            if current_map.layout[-1][node[0]+current_map.size[0]*node[1]]==-1 and current_map.layout[1][node[0]+current_map.size[0]*node[1]]!=-1:
                                add=1
                                for a in actors:
                                    if a.pos==node and people_ok==0:
                                        add = 0
                                if add==1: 
                                    childList.append(node)
                                    ancestry.append([node,parent])
                        except IndexError:
                            pass
        for parent in parentList:
            openList.append(parent)

        parentList=[]
        for node in childList:
            parentList.append(node)
    output = openList
    openList = []
    for node in output:
        if node not in openList:
            openList.append(node)
    return openList,ancestry


def sort_actors(actors):
    return range(0,len(actors))

def get_direction(start,end):
    if start[1]%2==1:
        if start[0]==end[0]:
            if end[1]==start[1]-1:
                return 'nw'
            else:
                return 'sw'
        else:
            if end[1]==start[1]-1:
                return 'ne'
            else:
                return 'se'
    else:
        if start[0]==end[0]:
            if end[1]==start[1]-1:
                return 'ne'
            else:
                return 'se'
        else:
            if end[1]==start[1]-1:
                return 'nw'
            else:
                return 'sw'

def parabola_up(d,t):
    n = 20*d-t
    m = 25*d-t
    o = -t
    y = n*(1-float(t)/20)*(1-float(t)/10)+o*(float(t)/20)*(float(t)/10-1)+m*(2-float(t)/10)*(float(t)/10)
    return y
def parabola_down_n(d,t):
    o = 20*d+t
    m = 25*d+t
    n = t
    y = n*(1-float(t)/20)*(1-float(t)/10)+o*(float(t)/20)*(float(t)/10-1)+m*(2-float(t)/10)*(float(t)/10)
    return y

def parabola_down(d,t):
    o = 20*d-t
    m = 25*d-t
    n = -t
    y = n*(1-float(t)/20)*(1-float(t)/10)+o*(float(t)/20)*(float(t)/10-1)+m*(2-float(t)/10)*(float(t)/10)
    return y
