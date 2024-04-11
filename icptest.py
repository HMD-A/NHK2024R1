import pygame
import sys
import math
import numpy as np
from scipy.spatial import KDTree

sairo = np.array([[125, 8500],
                  [125, 9200],
                  [125, 10000],
                  [125, 10750],
                  [125, 11500]])

def icp_2d(robot_points,robot_angle,relative_ball_points, max_iterations=30, tolerance=1e-5):
    E_x = 0.0
    data_num = relative_ball_points.shape[0]
    rotate = np.array([[math.cos(math.radians(-robot_angle)),math.sin(math.radians(-robot_angle))],[-math.sin(math.radians(-robot_angle)),math.cos(math.radians(-robot_angle))]])

    for j in range(max_iterations):
        for i in range(data_num):
            real_ball_position = np.dot(rotate,relative_ball_points[i]) + robot_points
            E_x += math.pow(np.linalg.norm(real_ball_position - sairo[i]),2)

        E_x /= data_num
        print(E_x)

        u_p = np.mean(relative_ball_points,axis=0).reshape((1,2))
        u_x = np.mean(sairo,axis=0).reshape((1,2))

        X_ = sairo - u_x
        P_ = relative_ball_points - u_p

        W = np.dot(X_.T, P_)
        u, _ , v = np.linalg.svd(W)
        #print(u)
        #print(_)
        #print(v)
        rotate = np.dot(u,v)
        robot_points = u_x - np.dot(rotate,u_p.reshape(2,1)).T

    angle_radians = np.arctan2(rotate[1, 0], rotate[0, 0])
    angle_degrees = np.degrees(angle_radians)
    print(angle_degrees)
    print(robot_points)
        


# 初期化
pygame.init()

# 画面サイズ
SCREEN_WIDTH = 1225
SCREEN_HEIGHT = 800

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 画面の作成
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Place and control objects")

# フォント
font = pygame.font.Font(None, 24)

# 背景画像の読み込み
background_img = pygame.image.load("../data/webpage/img/field_detail.png")
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# ロボット画像の読み込み
robot_img = pygame.image.load("../data/webpage/img/r1.png")
robot_img = pygame.transform.scale(robot_img, (100, 100))

# ボール画像の読み込み
ball_img = pygame.image.load("../data/webpage/img/redball.png")
ball_img = pygame.transform.scale(ball_img, (40, 40))

# モード切り替えボタン
button_font = pygame.font.Font(None, 36)
button_robot = button_font.render("Robot Mode", True, BLACK)
button_ball = button_font.render("Ball Mode", True, BLACK)
button_robot_rect = button_robot.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT - 50))
button_ball_rect = button_ball.get_rect(center=(SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT - 50))

# 初期モードはロボットを置くモード
current_mode = "robot"
robot_position = np.array([SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2])  # 左下を原点とした座標
robot_angle = 0
ball_positions = []
real_robot_position = []
real_ball_position = []
relative_positions_np = []

clock = pygame.time.Clock()

running = True

while running:
    screen.blit(background_img, (0, 0))

    # モード切り替えボタンを描画
    pygame.draw.rect(screen, WHITE, button_robot_rect)
    pygame.draw.rect(screen, WHITE, button_ball_rect)
    screen.blit(button_robot, button_robot_rect)
    screen.blit(button_ball, button_ball_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # マウスクリック位置を取得
            mouse_pos = pygame.mouse.get_pos()
            # モード切り替えボタンがクリックされたかどうかをチェック
            if button_robot_rect.collidepoint(mouse_pos):
                current_mode = "robot"
                icp_2d([800,10000],70,relative_positions_np)
            elif button_ball_rect.collidepoint(mouse_pos):
                current_mode = "ball"
            else:
                if current_mode == "robot":
                    robot_position = np.array([mouse_pos[0], SCREEN_HEIGHT - mouse_pos[1]])  # 左下を原点とした座標
                elif current_mode == "ball":
                    # ボールが重ならないようにチェック
                    overlap = False
                    ball_positions.append(np.array([mouse_pos[0], SCREEN_HEIGHT-mouse_pos[1]]))  # 左下を原点とした座標
                    rbp = [(mouse_pos[0])*5,( SCREEN_HEIGHT-mouse_pos[1])*5+8000]
                    real_ball_position.append(rbp)
        elif event.type == pygame.KEYDOWN:
            if current_mode == "robot":
                # ロボットモードでのキー入力処理
                if event.key == pygame.K_LEFT:
                    robot_position[0] -= 10
                elif event.key == pygame.K_RIGHT:
                    robot_position[0] += 10
                elif event.key == pygame.K_UP:
                    robot_position[1] += 10
                elif event.key == pygame.K_DOWN:
                    robot_position[1] -= 10
                elif event.key == pygame.K_r:
                    # ロボットの回転
                    robot_angle += 10  # 反時計回りが正
                    robot_angle %= 360

    # オブジェクトを描画
    for pos in ball_positions:
        screen.blit(ball_img, (pos[0] - ball_img.get_width() // 2, SCREEN_HEIGHT - pos[1] - ball_img.get_height() // 2))  # 左下を原点とした座標

    rotated_robot = pygame.transform.rotate(robot_img, robot_angle)  # 反時計回りが正
    rotated_rect = rotated_robot.get_rect(center=( robot_position[0], SCREEN_HEIGHT - robot_position[1]))  # 左下を原点とした座標
    screen.blit(rotated_robot, rotated_rect)

    real_robot_position = robot_position * 5 + [0,8000]
    # ロボットの座標と角度を表示
    robot_text = font.render(f"Robot Position: {real_robot_position}, Robot Angle: {robot_angle} degrees", True, BLACK)
    screen.blit(robot_text, (10, 10))

    # ボールの絶対座標を2次元配列で表示
    ball_absolute_text = font.render(f"Ball Absolute Positions: {real_ball_position}", True, BLACK)
    screen.blit(ball_absolute_text, (10, 30))
    #print(real_ball_position)

    # ロボットから見たボールの相対位置座標を計算
    relative_positions = []
    real_ball_np = np.array(real_ball_position)
    real_ball_np.reshape(-1,2)
    for pos in real_ball_np:
        relative_pos = pos - real_robot_position
        rotate = np.array([[math.cos(math.radians(robot_angle)),math.sin(math.radians(robot_angle))],[-math.sin(math.radians(robot_angle)),math.cos(math.radians(robot_angle))]])
        relative_pos = np.dot(rotate,relative_pos)
        #relative_positions.append(relative_pos)

        #relative_pos = np.dot(rotate,pos)
        #relative_pos -= real_robot_position
        relative_positions.append(relative_pos)

    relative_positions_np = np.array(relative_positions)
    ball_relative_text = font.render(f"Ball Relative Positions: {relative_positions_np}", True, BLACK)
    screen.blit(ball_relative_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
