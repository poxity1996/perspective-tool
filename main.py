import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from models import Cube, draw_axes

def reset_view():
    """確保重設時，攝影機回到正確的深度"""
    glMatrixMode(GL_MODELVIEW) # 切換到模型矩陣模式
    glLoadIdentity()           # 清除之前的旋轉與位移
    glTranslatef(0.0, 0.0, -7) # 將物體推向前方，讓鏡頭看得到

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("L-Click: Rotate | R-Click: Move | Space: Reset")
    
    # 投影矩陣只需要設定一次
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    
    # 初始化視角
    reset_view()

    cube = Cube()
    rotate_active = False
    move_active = False
    locked_axis = None
    threshold = 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    reset_view()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: rotate_active = True
                if event.button == 3: move_active = True
                locked_axis = None
            
            if event.type == MOUSEBUTTONUP:
                if event.button == 1: rotate_active = False
                if event.button == 3: move_active = False
                locked_axis = None
            
            if event.type == MOUSEMOTION:
                dx, dy = event.rel
                
                if (rotate_active or move_active) and locked_axis is None:
                    if abs(dx) > threshold or abs(dy) > threshold:
                        locked_axis = 'x' if abs(dx) > abs(dy) else 'y'

                if rotate_active and locked_axis:
                    if locked_axis == 'x':
                        glRotatef(dx * 0.5, 0, 1, 0)
                    else:
                        glRotatef(dy * 0.5, 1, 0, 0)
                
                if move_active and locked_axis:
                    if locked_axis == 'x':
                        glTranslatef(dx * 0.01, 0, 0)
                    else:
                        glTranslatef(0, -dy * 0.01, 0)

        if not running:
            break

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 繪製
        draw_axes()
        cube.draw()
        
        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()

if __name__ == "__main__":
    main()