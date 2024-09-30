import pygame
import math
import random

WIDTH = 720
HEIGHT = 1000
FPS = 60

CELL_SIZE = 90
ROWS = 10
COLUMNS = 8

MIN_ANGLE = 10
RADIUS = 43
SPEED = 20
HITBOX = 0.85 # [0, 1]

TRANSPARENCY = 96
BACKGROUND_COLOR = 'black'
TOTAL_COLORS = 8
COLORS = ['purple', 'yellow', 'cyan', 'green', 'magenta', 'white', 'orange', 'red']
TCOLORS = [(175, 0, 255, TRANSPARENCY), (255, 255, 0, TRANSPARENCY), (0, 255, 255, TRANSPARENCY), (0, 255, 0, TRANSPARENCY), 
           (255, 0, 255, TRANSPARENCY), (255, 255, 255, TRANSPARENCY), (255, 128, 0, TRANSPARENCY), (255, 0, 0, TRANSPARENCY)]


pygame.font.init()
font = pygame.font.SysFont("comicsans", 60)

screen = transparent = timer = blocks = current_color = next_color = None
x = y = xspeed = yspeed = score = num_colors = 0
visited = {}

def intialize_blocks(n, m):
    for i in range(0, n):
        for j in range(0, m):
            blocks[i][j] = random.randint(0, num_colors-1)

def add_blocks():
    new = []
    for _ in range(0, COLUMNS):
        new.append(random.randint(0, num_colors-1))

    blocks.insert(0, new)

def get_color():
    global blocks
    cnt = []
    for i in range(0, num_colors):
        cnt.append(0)
    
    for i in range(0, ROWS):
        for j in range(0, COLUMNS):
            if blocks[i][j] != None:
                cnt[blocks[i][j]] += 1
    
    colors = []
    for i in range(0, num_colors):
        if cnt[i] > 0:
            colors.append(i)
    
    k = random.randint(0, len(colors)-1)
    return colors[k]

def get_angle(pos):
    x = pos[0] - WIDTH/2
    y = -pos[1] + HEIGHT - 3*RADIUS
    angle = math.atan2(y, x)

    if math.degrees(angle) <= MIN_ANGLE or math.degrees(angle) >= 180 - MIN_ANGLE:
        return None
    return angle

def get_distance(angle):
    deg = math.degrees(angle)
    if deg < 70 or deg > 110:
        return abs((WIDTH/2 - RADIUS) / math.cos(angle))
    else: 
        return abs((HEIGHT - 3*RADIUS) / math.sin(angle))

def color_exists(color):
    for i in range(0, ROWS):
        for j in range(0, COLUMNS):
            if blocks[i][j] != None:
                if blocks[i][j] == color:
                    return True
    return False

def validIndex(i, j):
    return i >= 0 and i < ROWS and j >= 0 and j < COLUMNS

def collision(i2, j2):
    global x, y, xspeed, yspeed
    i = int(y / CELL_SIZE)
    j = int(x / CELL_SIZE)

    while not validIndex(i, j) or blocks[i][j] != None:
        x -= xspeed
        y -= yspeed
        i = int(y / CELL_SIZE)
        j = int(x / CELL_SIZE)

    if i2 != -1 and i != i2 and j != j2:
        if xspeed > 0:
            if i2 < i:
                if j2 < j and validIndex(i, j-1):
                    j -= 1
                else:
                    if abs(xspeed) > abs(yspeed) and validIndex(i, j+1):
                        j += 1
                    elif validIndex(i-1, j):
                        i -= 1
            elif validIndex(i+1, j):
                i += 1
        elif xspeed < 0:
            if i2 < i:
                if j2 < j:
                    if abs(xspeed) > abs(yspeed) and validIndex(i, j-1):
                        j -= 1
                    elif validIndex(i-1, j):
                        i -= 1
                elif validIndex(i, j+1):
                    j += 1
            elif validIndex(i+1, j):
                i += 1

    blocks[i][j] = current_color
    y = i
    x = j
    xspeed = 0
    yspeed = 0

def find(i, j, color):
    if not validIndex(i, j):
        return
    
    key = i*ROWS + j
    if key in visited:
        return

    if blocks[i][j] != color:
        return

    visited[key] = (i, j)
    find(i+1, j, color)
    find(i-1, j, color)
    find(i, j-1, color)
    find(i, j+1, color)

def visit(i, j):
    if not validIndex(i, j):
        return
    
    if blocks[i][j] == None:
        return
    
    key = i*ROWS + j
    if key in visited:
        return
    
    visited[key] = (i, j)

    visit(i, j-1)
    visit(i, j+1)
    visit(i+1, j)
    visit(i-1, j)

def update():
    global visited, x, y, blocks, score
    visited = {}
    find(y, x, blocks[y][x])
    if len(visited) < 3:
        return
    
    removed = []

    for key in visited:
        i, j = visited[key]
        removed.append((blocks[i][j], i, j))
        blocks[i][j] = None
        score += 1
    
    visited = {}
    for j in range(0, COLUMNS):
        if blocks[0][j] != None:
            visit(0, j)
    
    for i in range(0, ROWS):
        for j in range(0, COLUMNS):
            key = i*ROWS + j
            if not key in visited and blocks[i][j] != None:
                removed.append((blocks[i][j], i, j))
                blocks[i][j] = None
                score += 1
      
    x = -RADIUS
    y = -RADIUS

    iteration = 1
    duration = FPS / 6
    step = int(255 / duration)
    opacity = 255

    while iteration < duration:
        timer.tick(FPS)

        #draw
        screen.fill(BACKGROUND_COLOR)
        transparent.fill((0, 0, 0, 0))

        for rem in removed:
            color, i, j = rem
            r = TCOLORS[color][0]
            g = TCOLORS[color][1]
            b = TCOLORS[color][2]
            a = opacity
            pygame.draw.circle(transparent, (r, g, b, a), (CELL_SIZE/2 + j*CELL_SIZE, CELL_SIZE /2 + i*CELL_SIZE), RADIUS)

        draw()
        pygame.display.flip()
        opacity -= step
        if opacity < 0: opacity = 0
        iteration += 1

def empty():
    for i in range(0, ROWS):
        for j in range(0, COLUMNS):
            if blocks[i][j] != None:
                return False
                
    return True

def over():
    for j in range(0, COLUMNS):
        if blocks[ROWS-1][j] != None:
            return True
    
    return False

def game():
    global blocks, current_color, next_color, x, y, num_colors
    old_score = score
    num_colors = 2

    intialize_blocks(5, 8)
    next_color = get_color()

    while not over():
        if empty():
            if num_colors < TOTAL_COLORS:
                num_colors += 2
            intialize_blocks(6, 8)
            old_score = score

        x = WIDTH / 2
        y = HEIGHT - 3*RADIUS

        current_color = next_color
        next_color = get_color()

        if not color_exists(current_color):
            current_color = next_color
            next_color = get_color()

        if not animate():
            return False
        
        update()
        if ((score - old_score) // 30) > 0 and not empty():
            add_blocks()
            old_score = score

    return True

def draw():
    screen.blit(transparent, (0,0))
    
    pygame.draw.circle(screen, COLORS[next_color], (WIDTH/2 + 2*RADIUS, HEIGHT - 2.5*RADIUS), RADIUS/2)
    pygame.draw.circle(screen, COLORS[current_color], (x, y), RADIUS)

    for i in range(0, ROWS):
        for j in range(0, COLUMNS):
            if blocks[i][j] != None:
                pygame.draw.circle(screen, COLORS[blocks[i][j]], (CELL_SIZE/2 + j*CELL_SIZE, CELL_SIZE /2 + i*CELL_SIZE), RADIUS)
    
    text = font.render("Score: " + str(score), 1, 'white')
    screen.blit(text, (0, HEIGHT - 75))

def draw_path(angle):
    deg = math.degrees(angle)
    if deg <= 5 or deg >= 175:
        return
    
    dist = get_distance(angle)
    x = math.cos(angle)*dist
    y = math.sin(angle)*dist

    x += WIDTH/2
    y = -y + HEIGHT-3*RADIUS

    xoffset = RADIUS * math.sin(angle)
    yoffset = -RADIUS * math.cos(angle)

    pygame.draw.polygon(transparent, TCOLORS[current_color], [(WIDTH/2 + xoffset, HEIGHT - 3*RADIUS - yoffset), 
                                                              (WIDTH/2 - xoffset, HEIGHT - 3*RADIUS + yoffset), 
                                                              (x - xoffset, y + yoffset), 
                                                              (x + xoffset, y - yoffset)], 0)
    pygame.draw.circle(transparent, TCOLORS[current_color], (x, y), RADIUS)

    if deg < 70:
        k = -math.tan(angle)
        n = (HEIGHT - 3*RADIUS) - k*(WIDTH/2)
        x1 = WIDTH - RADIUS
        y1 = k*x1 + n
        k = -k
        n = y1 - k*x1
        x2 = -RADIUS
        y2 = k*x2 + n
        pygame.draw.polygon(transparent, TCOLORS[current_color], [(x1 - xoffset, y1 - yoffset), 
                                                                  (x1 + xoffset, y1 + yoffset),
                                                                  (x2 + xoffset, y2 + yoffset),
                                                                  (x2 - xoffset, y2 - yoffset)], 0)
        
    elif deg > 110:
        k = -math.tan(angle)
        n = (HEIGHT - 3*RADIUS) - k*(WIDTH/2)
        x1 = RADIUS
        y1 = k*x1 + n
        k = -k
        n = y1 - k*x1
        x2 = WIDTH + RADIUS
        y2 = k*x2 + n
        pygame.draw.polygon(transparent, TCOLORS[current_color], [(x1 - xoffset, y1 - yoffset), 
                                                                  (x1 + xoffset, y1 + yoffset),
                                                                  (x2 + xoffset, y2 + yoffset),
                                                                  (x2 - xoffset, y2 - yoffset)], 0)

def animate():
    global x, y, xspeed, yspeed
    angle = 0
    run = True
    while run:
        timer.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONUP:
                angle = get_angle(pygame.mouse.get_pos())
                if angle != None:
                    run = False
                    break

        angle = get_angle(pygame.mouse.get_pos())

        #draw
        screen.fill(BACKGROUND_COLOR)
        transparent.fill((0, 0, 0, 0))
        if angle != None:
            draw_path(angle)
        draw()
        pygame.display.flip()
    


    xspeed = math.cos(angle) * SPEED
    yspeed = -math.sin(angle) * SPEED
    run = True
    while run:
        timer.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return False

        x += xspeed
        y += yspeed

        min = math.inf
        pos = None

        #check collision
        if (x <= RADIUS and xspeed < 0) or (x >= WIDTH - RADIUS and xspeed > 0):
            xspeed = -xspeed
        
        for i in range(0, ROWS):
            for j in range(0, COLUMNS):
                if blocks[i][j] != None:
                    x1 = RADIUS + j*CELL_SIZE
                    y1 = RADIUS + i*CELL_SIZE
                    d = math.sqrt((x-x1)*(x-x1) + (y-y1)*(y-y1))
                    if d <= 2 * HITBOX * RADIUS:
                        if pos != None:
                            if d < min:
                                min = d
                                pos = (i, j)
                        else:
                            min = d
                            pos = (i, j)
                            
        
        if pos != None:
            collision(pos[0], pos[1])
            run = False
            break

        if y <= RADIUS:
            collision(-1, x // CELL_SIZE)
            run = False
            break

        #draw
        screen.fill(BACKGROUND_COLOR)
        transparent.fill((0, 0, 0, 0))
        draw()
        pygame.display.flip()

    return True

def main():
    global screen, transparent, timer, blocks, score
    pygame.init()

    pygame.display.set_caption('Ball Popper')
    icon = pygame.image.load('icon.ico')
    pygame.display.set_icon(icon)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    transparent = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    transparent.fill((0, 0, 0, 0))
    timer = pygame.time.Clock()

    run = True
    while run:
        score = 0
        blocks = []
        for _ in range(0, ROWS):
            dummy = []
            for _ in range(0, COLUMNS):
                dummy.append(None)
            blocks.append(dummy)
        run = game()
    
    pygame.quit()

main()
