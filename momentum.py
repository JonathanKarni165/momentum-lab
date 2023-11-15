import pygame
import math
from random import randint

WINDOW_SCALE = (600, 600)
screen = pygame.display.set_mode(WINDOW_SCALE)

FPS = 60
WHITE = (255,255,255)

static_ball_counter = 0

class Ball(pygame.sprite.Sprite):
    def __init__(self, radius=None, color=None, spawn_point=None):
        super().__init__()

        global static_ball_counter
        self.id = static_ball_counter
        static_ball_counter += 1

        self.velocity = [0.0, 0.0]
        self.speed = 0
        self.already_checked = False

        if radius:
            self.radius = radius
        else:
            self.radius = randint(10, 30)

        self.mass = self.radius

        if color:
            self.color = color
        else:
            self.color = (randint(0, 255), randint(0, 255), randint(0, 255))

        if spawn_point:
            self.x, self.y = spawn_point[0], spawn_point[1]
        else:
            self.x = randint(self.radius, WINDOW_SCALE[0]-self.radius)
            self.y = randint(self.radius, WINDOW_SCALE[1]-self.radius)

        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def add_force(self, force):
        self.velocity[0] += force[0] / self.mass
        self.velocity[1] += force[1] / self.mass
        self.speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

    def update_position(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.check_collision()

    def check_collision(self):
        horizontal_flip = self.x - self.radius < 0 or self.x + \
                self.radius > WINDOW_SCALE[0]
        vertical_flip = self.y - self.radius < 0 or self.y + \
                self.radius > WINDOW_SCALE[1]
        if horizontal_flip and self.speed > 0.5:
            self.velocity[0] *= -1
        if vertical_flip and self.speed > 0.5:
            self.velocity[1] *= -1
    
    def switch_direction(self, new_direction, magnitude):
        self.velocity = [new_direction[0]/50 * magnitude , new_direction[1]/50 * magnitude]

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Ball_To_Ball_Interaction:
    def __init__(self, first_ball : Ball, second_ball : Ball):
        self.first_ball = first_ball
        self.second_ball = second_ball
        self.min_distance = first_ball.radius + second_ball.radius
        self.offset = 2
    
    def update_interaction(self):
        self.distance = get_distance_between_two_balls(self.first_ball, self.second_ball)
        self.direction_between = (self.second_ball.x - self.first_ball.x, self.second_ball.y - self.first_ball.y)

    def check_collision(self):
        if self.distance < (self.min_distance + self.offset):
            self.bounce_opposite_directions()

    def bounce_opposite_directions(self):
        total_kinetic_energy = self.first_ball.speed + self.second_ball.speed
        self.second_ball.switch_direction(self.direction_between, total_kinetic_energy/2)
        negative_direction = (-self.direction_between[0], -self.direction_between[1])
        self.first_ball.switch_direction(negative_direction, total_kinetic_energy/2)

def get_distance_between_two_balls(first_ball, second_ball):
    return math.sqrt(math.pow(first_ball.x - second_ball.x, 2) + math.pow(first_ball.y - second_ball.y, 2))

        
class Plane:
    def __init__(self):
        self.balls = [Ball(radius=20) for x in range(30)]
        [ball.add_force((randint(-30,30), randint(-30,30))) for ball in self.balls]
        
        self.ball_interactions : list[Ball_To_Ball_Interaction] = [] 
        for i in range(len(self.balls)):
            for j in range(i+1, len(self.balls)):
                interaction = Ball_To_Ball_Interaction(self.balls[i], self.balls[j])
                self.ball_interactions.append(interaction)

    def update_screen(self):
        screen.fill((0, 0, 0))

        for interaction in self.ball_interactions:
            interaction.update_interaction()
            interaction.check_collision()

        for ball in self.balls:
            ball.update_position()
            ball.draw()
        pygame.display.update()
    
            

def main():
    pygame.init()
    clock = pygame.time.Clock()
    run = True
    plane = Plane()
    while (run):
        clock.tick(FPS)
        plane.update_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


if __name__ == '__main__':
    main()
