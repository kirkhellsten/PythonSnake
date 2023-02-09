
import sys, pygame
import time, random

pygame.init()

BLOCK_SIZE = 10
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_OF_BLOCKS_W = SCREEN_WIDTH / BLOCK_SIZE
NUM_OF_BLOCKS_H = SCREEN_HEIGHT / BLOCK_SIZE
DYING_DYE_INCREMENT = 10
NUM_OF_FOODS_RELEASED = 10
NUM_OF_BODY_ADDED = 10
SCORE_EAT = 50
SCORE_RESET_FOOD = 125
FOOD_MARGIN = 1
BODY_MARGIN = 0
BACKGROUND_COLOR = (46, 52, 64)

SNAKE_INITIAL_NUM_BODY = 10
SNAKE_HEAD_COLOR = 176, 56, 56
SNAKE_BODY_COLOR = 75, 255, 75
SNAKE_DYE_INIT_COLOR = 255
SNAKE_DEATH_RCOLOR = 125

FOOD_COLOR = 176, 24, 62

SCORE_BOARD_TEXT_COLOR = (255, 255, 255)
SCORE_BOARD_FONT_SIZE = 24

FPS = 12
fpsClock = pygame.time.Clock()

class Utils:

    @staticmethod
    def getMiddlePosition():
        return [int((SCREEN_WIDTH / 2) / BLOCK_SIZE), int((SCREEN_HEIGHT / 2) / BLOCK_SIZE)]

    @staticmethod
    def getRandomDirection():
        directions = ['right', 'left', 'down', 'up']
        initialDirection = directions[random.randint(0, 3)]
        return initialDirection

class Sound:

    SND_DEATH = None
    SND_EAT = None
    SND_APPEAR = None

    @staticmethod
    def init():
        Sound.SND_DEATH = pygame.mixer.Sound("death.wav")
        Sound.SND_EAT = pygame.mixer.Sound("eat.wav")
        Sound.SND_APPEAR = pygame.mixer.Sound("appear.mp3")

    @staticmethod
    def playDeathSound():
        pygame.mixer.Sound.play(Sound.SND_DEATH)
        pygame.mixer.music.stop()

    @staticmethod
    def playEatSound():
        pygame.mixer.Sound.play(Sound.SND_EAT)
        pygame.mixer.music.stop()

    @staticmethod
    def playAppearSound():
        pygame.mixer.Sound.play(Sound.SND_APPEAR)
        pygame.mixer.music.stop()

class Scoreboard:

    @staticmethod
    def init():
        Scoreboard.score = 0
        Scoreboard.text = "Score: " + str(Scoreboard.score)

    @staticmethod
    def addScore(scoreAmount):
        Scoreboard.score += scoreAmount
        Scoreboard.text = "Score: " + str(Scoreboard.score)

class Renderer:

    @staticmethod
    def __drawBackground():
        screen.fill(BACKGROUND_COLOR)

    @staticmethod
    def __drawScoreboard():
        font = pygame.font.SysFont(None, SCORE_BOARD_FONT_SIZE)
        img = font.render(Scoreboard.text, True, SCORE_BOARD_TEXT_COLOR)
        screen.blit(img, (5, 8))

    @staticmethod
    def __drawHead():
        head = Snake.getSnakeHead()
        headRect = pygame.Rect((head[0]*BLOCK_SIZE, head[1]*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(screen, SNAKE_HEAD_COLOR, headRect)

    @staticmethod
    def __drawBody():
        snake = Snake.snake
        if not snake.dying:
            bodyColor = SNAKE_BODY_COLOR
            snake.dyingDye = SNAKE_DYE_INIT_COLOR
        else:
            snake.dyingDye -= DYING_DYE_INCREMENT
            if snake.dyingDye < 0:
                snake.dead = True
                return
            bodyColor = SNAKE_DEATH_RCOLOR, snake.dyingDye, snake.dyingDye
        for i in range(1, len(snake.positions)):
            body = snake.positions[i]
            bodyRect = pygame.Rect((body[0]*BLOCK_SIZE+BODY_MARGIN,
                                    body[1]*BLOCK_SIZE+BODY_MARGIN,
                                    BLOCK_SIZE-BODY_MARGIN , BLOCK_SIZE-BODY_MARGIN))
            pygame.draw.rect(screen, bodyColor, bodyRect)


    @staticmethod
    def __drawSnake():
        Renderer.__drawBody()
        Renderer.__drawHead()

    @staticmethod
    def __drawFood():
        for food in Food.foods:
            foodRect = pygame.Rect((food.position[0] * BLOCK_SIZE + FOOD_MARGIN,
                                    food.position[1] * BLOCK_SIZE + FOOD_MARGIN,
                                    BLOCK_SIZE - FOOD_MARGIN, BLOCK_SIZE - FOOD_MARGIN))
            pygame.draw.rect(screen, FOOD_COLOR, foodRect)

    @staticmethod
    def draw():

        Renderer.__drawBackground()
        Renderer.__drawSnake()
        Renderer.__drawFood()
        Renderer.__drawScoreboard()


class Food:
    def __init__(self, pos):
        self.position = pos

    @staticmethod
    def getNewFoodLocation():
        snake = Snake.snake
        foodLocation = [random.randint(0, NUM_OF_BLOCKS_W - 1), random.randint(0, NUM_OF_BLOCKS_H - 1)]
        while snake.isCollision(foodLocation):
            foodLocation = [random.randint(0, NUM_OF_BLOCKS_W - 1), random.randint(0, NUM_OF_BLOCKS_H - 1)]

        return foodLocation

    @staticmethod
    def createFoods(numOfFoods):
        foods = []
        for i in range(numOfFoods):
            foodPosition = Food.getNewFoodLocation()
            food = Food(foodPosition)
            foods.append(food)
        return foods

class Snake:

    def __init__(self, pos=(0,0), dir='down', numBodyBits=NUM_OF_BODY_ADDED):
        self.positions = [[int(pos[0]), int(pos[1])]]
        self.direction = dir
        self.dying = False
        self.dead = False

    @staticmethod
    def getSnakeHead():
        return Snake.snake.positions[0]

    def isCollision(self, pos):
        for i in range(len(self.positions)-1):
            if pos[0] == self.positions[0] and pos[1] == self.positions[1]:
                return True
        return False

    def moveBody(self):
        for i in range(len(self.positions)-1,0,-1):
            bodyPart = self.positions[i]
            bodyPart[0] = self.positions[i-1][0]
            bodyPart[1] = self.positions[i-1][1]

    def isCollisionWithSelf(self):
        head = self.positions[0]
        for i in range(len(self.positions)-1,0,-1):
            if head[0] == self.positions[i][0] and head[1] == self.positions[i][1]:
                return True
        return False

    def update(self):
        if not self.dying:
            self.moveBody()
            head = self.positions[0]
            if self.direction == 'right':
                head[0] += 1
                if head[0] == NUM_OF_BLOCKS_W:
                    head[0] = 0
            elif self.direction == 'left':
                head[0] -= 1
                if head[0] == -1:
                    head[0] = NUM_OF_BLOCKS_W-1
            elif self.direction == 'down':
                head[1] += 1
                if head[1] == NUM_OF_BLOCKS_H:
                    head[1] = 0
            elif self.direction == 'up':
                head[1] -= 1
                if head[1] == -1:
                    head[1] = NUM_OF_BLOCKS_H-1

            if self.isCollisionWithSelf():
                Sound.playDeathSound()
                self.dying = True

    def addBody(self, num=1):
        for i in range(num):
            head = self.positions[0]
            tail = self.positions[len(self.positions)-1]
            newBody = [tail[0], tail[1]]
            self.positions.append(newBody)


    def isCollisionWithHead(self, block):
        snakeHead = snake.positions[0]
        if snakeHead[0] == block.position[0] and snakeHead[1] == block.position[1]:
            return True
        return False

class GameWorld:

    @staticmethod
    def init():

        Snake.snake = Snake(Utils.getMiddlePosition(), Utils.getRandomDirection())
        Snake.snake.addBody(SNAKE_INITIAL_NUM_BODY)

        Food.foods = Food.createFoods(NUM_OF_FOODS_RELEASED)

        Sound.init()
        Scoreboard.init()

        Sound.playAppearSound()

    @staticmethod
    def reset():

        del Snake.snake
        del Food.foods

        Snake.snake = Snake(Utils.getMiddlePosition(), Utils.getRandomDirection())
        Snake.snake.addBody(SNAKE_INITIAL_NUM_BODY)

        Food.foods = Food.createFoods(NUM_OF_FOODS_RELEASED)

        Scoreboard.init()

        Sound.playAppearSound()

    @staticmethod
    def quit():
        return None

    @staticmethod
    def update():

        foods = Food.foods
        snake = Snake.snake

        snake.update()

        for food in foods:
            if snake.isCollisionWithHead(food):
                snake.addBody(NUM_OF_BODY_ADDED)
                foods.remove(food)
                Sound.playEatSound()
                Scoreboard.addScore(SCORE_EAT)

        if len(foods) == 0:
            foods = Food.createFoods(NUM_OF_FOODS_RELEASED)
            Food.foods += foods
            Sound.playAppearSound()
            Scoreboard.addScore(SCORE_RESET_FOOD)

        if snake.dead:
            GameWorld.reset()


if __name__ == '__main__':

    size = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Snake")

    prev_time = time.time()

    GameWorld.init()

    running = True
    while running:

        snake = Snake.snake

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and snake.direction is not 'right':
            snake.direction = 'left'
        elif keys[pygame.K_RIGHT] and snake.direction is not 'left':
            snake.direction = 'right'
        elif keys[pygame.K_UP] and snake.direction is not 'down':
            snake.direction = 'up'
        elif keys[pygame.K_DOWN] and snake.direction is not 'up':
            snake.direction = 'down'

        GameWorld.update()
        Renderer.draw()

        pygame.display.flip()
        fpsClock.tick(FPS)

    GameWorld.quit()
