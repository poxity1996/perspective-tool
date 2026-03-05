import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from models import Cube, draw_axes

def draw_text(x, y, text):
    """在螢幕指定座標繪製文字"""
    font = pygame.font.SysFont('arial', 18)
    text_surface = font.render(text, True, (50, 50, 50))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), 
                 GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def reset_projection(width, height):
    """處理視窗縮放，防止畫面變形"""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = width / height if height != 0 else 1
    gluPerspective(45, aspect_ratio, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def reset_view():
    """重置物體位置與旋轉"""
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -8)

def main():
    pygame.init()
    width, height = 400, 400
    
    # 設定 OpenGL 屬性 (反鋸齒)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    
    # 開啟視窗 (可縮放)
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("3D Perspective Tool")
    
    # 開啟透明度混合與深度測試
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    reset_projection(width, height)
    reset_view()

    cube = Cube()
    
    # 功能開關狀態
    transparent_mode = False
    show_guides = False
    show_axes = False
    
    # 交互變數
    rotate_active = False
    move_active = False
    locked_axis = None
    threshold = 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == VIDEORESIZE:
                width, height = event.size
                reset_projection(width, height)

            if event.type == KEYDOWN:
                if event.key == K_SPACE: reset_view()
                if event.key == K_t: transparent_mode = not transparent_mode
                if event.key == K_g: show_guides = not show_guides
                if event.key == K_a: show_axes = not show_axes

            # 鼠標控制
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
                    if locked_axis == 'x': glRotatef(dx * 0.5, 0, 1, 0)
                    else: glRotatef(dy * 0.5, 1, 0, 0)
                if move_active and locked_axis:
                    if locked_axis == 'x': glTranslatef(dx * 0.01, 0, 0)
                    else: glTranslatef(0, -dy * 0.01, 0)

        if not running: break

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if show_axes:
            draw_axes()
        
        # 繪製輔助線 (在立方體之前畫，避免遮擋文字)
        if show_guides:
            cube.draw_vanishing_lines()
            
        # 繪製立方體 (決定透明度)
        alpha_val = 0.4 if transparent_mode else 1.0
        cube.draw(alpha=alpha_val)

        

        # UI 狀態文字
        draw_text(10, height - 30, f"Transparent (T): {'ON' if transparent_mode else 'OFF'}")
        draw_text(10, height - 55, f"Guides (G): {'ON' if show_guides else 'OFF'}")
        draw_text(10, height - 80, f"Axes (A): {'ON' if show_axes else 'OFF'}")

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()

if __name__ == "__main__":
    main()