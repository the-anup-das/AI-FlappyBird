import pygame
import neat
import time
import os
import random
import pickle
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN=0
DRAW_LINES=True

BIRD_IMGS=[pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird1.png'))),pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird2.png'))),pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird3.png')))]
PIPE_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','pipe.png')))
BASE_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','base.png')))
BG_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bg.png')))

STAT_FONT=pygame.font.SysFont("comicsans",50)

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

class Bird:
    IMGS=BIRD_IMGS
    MAX_ROTATION=25
    ROT_VEL=20
    ANIMATION_TIME=5

    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.tilt=0
        self.tick_count=0
        self.vel=0
        self.height=self.y
        self.img_count=0
        self.img=self.IMGS[0]

    def jump(self):
        self.vel=-10.5
        self.tick_count=0
        self.height=self.y
    
    def move(self):
        self.tick_count+=1

        displacement=self.vel*self.tick_count+1.5*self.tick_count**2 #for downward acceleration

        if displacement>=16: #terminal velocity 
            displacement=(displacement/abs(displacement)) * 16
        if displacement<0:
            displacement-=2

        self.y=self.y+displacement

        if displacement<0 or self.y<self.height+50:    #if going upwards
            if self.tilt<self.MAX_ROTATION:
                self.tilt=self.MAX_ROTATION
        else:
            if self.tilt>-90:
                self.tilt-=self.ROT_VEL
    
    def draw(self, win):
        self.img_count += 1

        # Creating bird animation by looping through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:    #bird driving 
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image=pygame.transform.rotate(self.img,self.tilt)
        new_rect=rotated_image.get_rect(center=self.img.get_rect(topleft=(round(self.x),round(self.y))).center)
        win.blit(rotated_image,new_rect.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP=200
    VEL = 5

    def __init__(self,x):
        self.x=x
        self.height=0
        self.gap=100

        self.top=0
        self.bottom=0
        self.PIPE_TOP=pygame.transform.flip(PIPE_IMG,False, True)
        self.PIPE_BOTTOM=PIPE_IMG

        self.passed=False
        self.set_height()

    def set_height(self):
        self.height=random.randrange(50,450)
        self.top=self.height - self.PIPE_TOP.get_height()
        self.bottom=self.height+self.GAP

    def move(self):
        self.x -=self.VEL

    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))

    def collide(self,bird,win):
        bird_mask=bird.get_mask()
        top_mask=pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask=pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset=(self.x-bird.x,self.top-round(bird.y))
        bottom_offset=(self.x-bird.x,self.bottom-round(bird.y))

        b_point=bird_mask.overlap(bottom_mask,bottom_offset)
        t_point=bird_mask.overlap(top_mask,top_offset)

        if t_point or b_point:
            return True
        
        return False

class Base:
    VEL=5
    WIDTH = BASE_IMG.get_width()
    IMG=BASE_IMG

    def __init__(self,y):
        self.y=y
        self.x1=0
        self.x2=self.WIDTH

    def move(self):
        self.x1-=self.VEL
        self.x2-=self.VEL

        if self.x1+self.WIDTH<0:
            self.x1=self.x2+self.WIDTH

        if self.x2+self.WIDTH<0:
            self.x2=self.x1+self.WIDTH

    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))


def draw_window(win,birds, pipes, base,score,gen,pipe_ind):
    win.blit(BG_IMG,(0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    for bird in birds:
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
            # Exception as e: print(e)

        bird.draw(win)

    score_label =STAT_FONT.render("Score: "+ str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    score_label =STAT_FONT.render("Generation: "+ str(gen),1,(255,255,255))
    win.blit(score_label, (10 , 10))

    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()

def main(genomes,config):
    global GEN

    ge=[]
    nets=[]
    birds=[]

    for genome_id,genome in genomes:
        genome.fitness=0
        net=neat.nn.FeedForwardNetwork.create(genome,config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base=Base(730)
    pipes=[Pipe(600)]
    score=0

    win=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock=pygame.time.Clock()

    run=True
    while run and len(birds)>0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                pygame.quit()
                quit()
                break
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                bird.jump()

        pipe_ind=0
        if len(birds)>0:
            if len(pipes)>1 and birds[0].x>pipes[0].x+pipes[0].PIPE_TOP.get_width():
                pipe_ind=1

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness+=0.1

            output=nets[x].activate((bird.y,abs(bird.y-pipes[pipe_ind].height),abs(bird.y-pipes[pipe_ind].bottom)))

            if output[0]>0.5: #if over 0.5 jump
                bird.jump()
        #bird.move()
        rem=[]
        add_pipe=False
        for pipe in pipes:
            pipe.move()
            for bird in birds:
                if pipe.collide(bird,win):
                    x=birds.index(bird)
                    ge[x].fitness-=1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

            if not pipe.passed and pipe.x<bird.x:
                    pipe.passed=True
                    add_pipe=True

            if pipe.x + pipe.PIPE_TOP.get_width()<0:
                rem.append(pipe)
            

        
        if add_pipe:
            score +=1
            for genome in ge:
                genome.fitness +=5
            pipes.append(Pipe(random.randrange(550, 750)))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y+bird.img.get_height()>=730 or bird.y<0:
                x=birds.index(bird)
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)


        base.move()
        draw_window(win,birds,pipes,base,score,GEN,pipe_ind)

        if score >50:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break

    GEN+=1
    

def run(config_path):
    #with open("best.pickle", "rb") as f:
    #    nets=pickle.load(f)
        
    config=neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
    neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)

    p=neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats=neat.StatisticsReporter()
    p.add_reporter(stats)

    winner=p.run(main,20)
    print('\nBest genome:\n{!s}'.format(winner))

    #pickle.dump(winner,open("best.pickle", "wb"))


    

if __name__=="__main__":
    local_dir=os.path.dirname(__file__)
    config_path=os.path.join(local_dir,"config-feedforward.txt")
    run(config_path)