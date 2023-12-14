import pygame
import sys
import random
import os

# 이미지 로드
imgplayer = pygame.image.load("imgplayer.png")
imgmap1 = pygame.image.load("imgmap1.png")
imgmap2 = pygame.image.load("imgmap2.png")
imgmap3 = pygame.image.load("imgmap3.png")
imgmap4 = pygame.image.load("imgmap4.png")
imgmonster1 = pygame.image.load_extended("imgmonster1.gif")
imgmonster2 = pygame.image.load_extended("imgmonster2.gif")
imgmonster3 = pygame.image.load_extended("imgmonster3.gif")
imgmonsterboss = pygame.image.load_extended("imgmonsterboss.gif")

# 변수
screen = None
screenwt, screenht = 1280, 800
playerwt, playerht = 32, 32   # 플레이어 크기 32*32
xplayer, yplayer = 50, 50  # 플레이어 처음 위치
playerspeed = 5
player = None
monsters = None
monsterwt, monsterht = 32, 32
monsterspeed = 3
monsterbosshealth = 400
max_monsters, monster_spawn_interval, last_spawn_time = None, None, None
clock = None
currentmap = None
current_monster_types = None
fullscreen = False
font1, font2 = None, None

monster_types = {
    1: {"image": imgmonster1, "size": (32, 32), "health": 32},
    2: {"image": imgmonster2, "size": (32, 32), "health": 32},
    3: {"image": imgmonster3, "size": (32, 32), "health": 32},
    4: {"image": imgmonsterboss, "size": (480, 480), "health": 480}
}

def initialize_game():
    global screenwt, screenht, screen
    pygame.init()
    screen = pygame.display.set_mode((screenwt, screenht))
    pygame.display.set_caption("영웅의 사랑 part 1:공주를 찾아서")
    
def load_maps():
    global maps, currentmap, current_monster_types

    maps = [
        {  
            "bg": imgmap1,  # 이미 앞에서 로드를 했으므로 변수이름 사용
            "portal": [    # 다 같은 딕셔너리로 만들어주기 위함, 공간낭비X
                {"portalxy" : (1210, 30), "tomap": 1}
            ],
            "monsters": [{ "type": 1, "position": (800, 500) }],
            "max_monsters": 4,
            "monster_spawn_interval": 10000
        },
        { 
            "bg": imgmap2,  
            "portal": [
                {"portalxy": (1250, 30), "tomap": 2},
                {"portalxy": (1, 1), "tomap": 0 } 
            ],
            "monsters": [{"type": 2, "position": (800, 500)}],
            "max_monsters": 6,
            "monster_spawn_interval": 10000
        },
        {  
            "bg": imgmap3,  
            "portal": [
                { "portalxy" : (1235, 755), "tomap" : 3},
                { "portalxy" : (1, 1), "tomap" : 1} 
            ],
            "monsters": [{ "type": 3, "position": (800, 500)}],
            "max_monsters": 8,
            "monster_spawn_interval": 10000
        },
        { 
            "bg": imgmap4,
            "portal": [
                { "portalxy" : (1, 1), "tomap" : 2}],
            "monsters": [{ "type": 4, "position": (500, 200)}],
            "max_monsters": 1,
            "monster_spawn_interval": 10000            
        }
    ]
    current_monster_types = set(monster["type"] for map_info in maps for monster in map_info["monsters"])
    currentmap = 0
    
def reset_player_and_monsters():
    global player, monsters, maps, max_monsters, monster_spawn_interval, last_spawn_time

    monsters = maps[currentmap]["monsters"]
    max_monsters = maps[currentmap]["max_monsters"]
    monster_spawn_interval = maps[currentmap]["monster_spawn_interval"]
    last_spawn_time = pygame.time.get_ticks()
    
def draw_entities():
    global screen, xplayer, yplayer, monsters, maps, playerwt, playerht, imgplayer, monster_types, current_monster_types
    screen.blit(maps[currentmap]["bg"], (0, 0))

    for monster_type in current_monster_types:
        for monster in [m for m in monsters if m["type"] == monster_type]:
            monster_image = monster_types[monster_type]["image"]
            monster_health = monster_types[monster_type]["health"]
            
            if isinstance(monster_image, list):
                # GIF 이미지의 경우 첫 번째 프레임을 사용
                monster_image = pygame.surfarray.make_surface(monster_image[0])
            screen.blit(monster_image, (monster["position"][0], monster["position"][1]))
           
            monster_x, monster_y = monster["position"]
            if currentmap == 3 and monster_type == 4:
                pygame.draw.rect(screen, (255, 0, 0), (monster_x, monster_y - 10, monster_health, 10))
            else:
                pygame.draw.rect(screen, (255, 0, 0), (monster_x, monster_y - 2, monster_health, 3))

    for portal in maps[currentmap]["portal"]:
        xportal, yportal = portal["portalxy"]
        pygame.draw.rect(screen, (0, 0, 0, 0), (xportal, yportal, playerwt, playerht))

    screen.blit(imgplayer, (xplayer, yplayer))

    pygame.display.flip()
    
def move_player(keys):
    global xplayer,yplayer, playerwt, playerht, screenwt, screenht
    
    # 플레이어가 화면 아래 경계를 넘어가지 않도록 하여, 화면 내에서 플레이어가 움직이도록 하는 제약 조건
    if keys[pygame.K_LEFT] and xplayer > 0: # xplayer : 플레이어 x좌표
        xplayer -= playerspeed
    if keys[pygame.K_RIGHT] and xplayer < screenwt - playerwt: 
        # (화면 너비 - 플레이어 너비), 화면 오른쪽끝 경계에서 플레이어만큼 떨어진 위치
        xplayer += playerspeed
    if keys[pygame.K_UP] and yplayer > 0:   # yplayer : 플레이어 y좌표
        yplayer -= playerspeed
    if keys[pygame.K_DOWN] and yplayer < screenht - playerht:
        # (화면 높이 - 플레이어 높이), 화면 하단 경계에서 플레이어의 높이만큼 떨어진 위치
        yplayer += playerspeed
        
def move_monsters():
    global monsters, monsterspeed, screenwt, screenht, monsterwt, monster
    
    for monster in monsters:
        xmonster, ymonster = monster["position"]
        monsterlrud = random.choice(['left', 'right', 'up', 'down'])

        if monsterlrud == 'left' and xmonster > 0:
            xmonster -= monsterspeed
        elif monsterlrud == 'right' and xmonster < screenwt - monsterwt:
            xmonster += monsterspeed
        elif monsterlrud == 'up' and ymonster > 0:
            ymonster -= monsterspeed
        elif monsterlrud == 'down' and ymonster < screenht - monsterht:
            ymonster += monsterspeed

        monster["position"] = (xmonster, ymonster)
        
def spawn_monster():
    global monsters, max_monsters, monster_spawn_interval, last_spawn_time, current_monster_types
    current_time = pygame.time.get_ticks()
    if len(monsters) < max_monsters and current_time - last_spawn_time > monster_spawn_interval:
        for i in range(3):  # 3마리씩 생성
            if currentmap == 0:
                monster_type = 1
            elif currentmap == 1:
                monster_type = 2
            elif currentmap == 2:
                monster_type = 3
            else:
                return  # 네 번째 맵에서는 몬스터 생성하지 않음

            new_monster_x = random.randint(0, screenwt - monsterwt)
            new_monster_y = random.randint(0, screenht - monsterht)
            monsters.append({"type": monster_type, "position": (new_monster_x, new_monster_y)})
        last_spawn_time = current_time

def check_collisions(keys):
    global currentmap, xplayer, yplayer, monsters, playerwt, playerht

    for portal in maps[currentmap]["portal"]:
        xportal, yportal = portal["portalxy"]
        portalwt, portalht = 32, 32

        if (
            xplayer < xportal + portalwt
            and xplayer + playerwt > xportal
            and yplayer < yportal + portalht
            and yplayer + playerht > yportal
        ):
            currentmap = portal["tomap"]
            reset_player_and_monsters()
            return True

    for i in range(len(monsters)):
        monster = monsters[i]
        xmonster, ymonster = monster["position"]
        monsterwt, monsterht = 32, 32

        # 보스 몬스터의 경우 이미지 전체에 대한 충돌을 검사
        monster_type = monster["type"]
        if monster_type == 4:
            boss_rect = pygame.Rect(xmonster, ymonster, monster_types[monster_type]["size"][0], monster_types[monster_type]["size"][1])
            player_rect = pygame.Rect(xplayer, yplayer, playerwt, playerht)

            if player_rect.colliderect(boss_rect):
                if keys[pygame.K_a]:
                    ATTACK = True
                    monster_types[monster_type]["health"] -= 32
                    if monster_types[monster_type]["health"] <= 0:
                        display_ending_screen()
                        return False
        else:
            # 일반 몬스터의 경우 기존 방식으로 충돌을 검사
            if (
                xplayer < xmonster + monsterwt
                and xplayer + playerwt > xmonster
                and yplayer < ymonster + monsterht
                and yplayer + playerht > ymonster
            ):
                if keys[pygame.K_a]:
                    ATTACK = True
                    monster_types[monster_type]["health"] -= 32
                    if monster_types[monster_type]["health"] <= 0:
                        monsters.pop(i)
                        return False

    return False
        
def toggle_fullscreen():
    global fullscreen, screen, screenwt, screenht
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((screenwt, screenht), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((screenwt, screenht))
        
def load_fonts():
    global font1, font2

    # Initialize Pygame
    pygame.init()

    # Set the path to your Korean font file (replace 'NanumGothic.ttf' with your font file)
    font_path = os.path.join(os.path.dirname(__file__), "NanumGothic.ttf")

    try:
        # Load the font
        font1 = pygame.font.Font(font_path, 36)
        font2 = pygame.font.Font(font_path, 20)
    except pygame.error as e:
        print(f"Error loading fonts: {e}")
        pygame.quit()
        sys.exit()

def start_screen():
    global screen, screenwt, screenht

    # Load the title screen image
    startimg = pygame.image.load("startimg.png")  
    startimgrect = startimg.get_rect()

    title = True
    while title:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 스페이스 바를 누르면 opening 화면으로 이동
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                title = False

        screen.fill((0, 0, 0))
        screen.blit(startimg, (screenwt // 2 - startimgrect.width // 2, screenht // 2 - startimgrect.height // 2))
        pygame.display.flip()

def opening_screen(opening_index):
    global screen, screenwt, screenht

    opening_texts = [
        "어느 한적하고 평화로운 5만평 나라..",
        "전쟁을 마치고 돌아온 영웅은 충격적인 소식을 듣게 되는데!!",
        "공주가 납치 당했다는 소식이다.",
        "영웅은 공주의 방으로 달려가보지만 방에는 비어있는 침대뿐..",
        "당장 공주를 구해오라는 왕의 명령..",
        "전쟁을 마치고 돌아와 지쳐버린 부하들을 뒤로하고",
        "영웅은 혼자 여정을 떠나게 된다.."
    ]

    text = font1.render(opening_texts[opening_index], True, (255, 255, 255))
    keytext = font2.render("스페이스바를 눌러주세요.", True, (255, 255, 255))

    opening = True
    while opening:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 스페이스 바를 누르면 다음 오프닝으로 이동
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                opening = False

        screen.fill((0, 0, 0))
        screen.blit(text, (screenwt // 2 - text.get_width() // 2, screenht // 2 - text.get_height() // 2))
        screen.blit(keytext, (1000, 750))
        pygame.display.flip()

def display_ending_screen():
    # 결말 이미지 리스트
    ending_images = [
        pygame.image.load("ending1.png"),
        pygame.image.load("ending2.png"),
        pygame.image.load("ending3.png"),
        pygame.image.load("ending4.png"),
        pygame.image.load("ending5.png")
    ]

    # 각 이미지를 6초 동안 표시
    for ending_image in ending_images:
        screen.blit(ending_image, (0, 0))
        pygame.display.update()
        pygame.time.delay(6000)  # 6초 대기

    # 여기에 마지막 화면을 표시하는 코드 추가
    final_ending_screen = pygame.image.load("ending6.png")
    screen.blit(final_ending_screen, (0, 0))
    pygame.display.update()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                running = False
                
        pygame.time.Clock().tick(10)
        
def main():
    global currentmap, screen, imgplayer, monster_types, current_monster_types
    
    load_fonts()
    initialize_game()
    load_maps() # load_portals 함수 호출
    
    clock = pygame.time.Clock()
    currentmap = 0
    reset_player_and_monsters()
    
    start_screen()
    
    for opening_index in range(7):
        opening_screen(opening_index)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # F1 키를 누르면 전체 화면 모드 토글
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                toggle_fullscreen()

            # 스페이스 바를 누르면 게임 시작
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_running = True
        
        keys = pygame.key.get_pressed()
        move_player(keys)
        move_monsters()

        collision = check_collisions(keys)
        if collision:
            continue

        spawn_monster()
        draw_entities()
        
        pygame.display.update()
        clock.tick(100)
        
if __name__ == '__main__':
    main()