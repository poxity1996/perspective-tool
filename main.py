import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from models import Cube, draw_axes, COLORS

def draw_text(x, y, text):
    font = pygame.font.SysFont('arial', 18)
    text_surface = font.render(text, True, (50, 50, 50))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), 
                 GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def reset_projection(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = width / height if height != 0 else 1
    gluPerspective(45, aspect_ratio, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def reset_view():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -8)

def main():
    pygame.init()
    width, height = 400, 400
    
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("3D Perspective Tool")
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    reset_projection(width, height)
    reset_view()

    cube = Cube()
    
    transparent_mode = False
    show_guides = False
    show_axes = False
    
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

        # --- 渲染開始 ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 1. 畫背景輔助（座標軸、地平線或輔助線）
        if show_axes:
            draw_axes()
        
        # 1. 準備繪製面：啟用多邊形偏移，解決閃爍 (Z-fighting)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0) # 讓面稍微後退

        alpha_val = 0.4 if transparent_mode else 1.0
        cube.draw(alpha=alpha_val) # 只呼叫這一次 draw

        glDisable(GL_POLYGON_OFFSET_FILL) # 畫完面就關閉偏移

        # 2. 處理框線
        if not transparent_mode:
            # 非透明模式：只畫正常深度下的黑框
            cube.draw_wireframe(COLORS['BLACK'], width=1.2)
        else:
            # 透明模式：
            # A. 內部線 (不計深度，灰色半透明)
            glDisable(GL_DEPTH_TEST)
            cube.draw_wireframe(COLORS['INTERNAL_LINE'], width=0.8)
            glEnable(GL_DEPTH_TEST)
            
            # B. 外部黑框
            cube.draw_wireframe(COLORS['BLACK'], width=1.2)

        # 3. 繪製輔助線 (放在最後確保不被方塊遮擋)
        if show_guides:
            cube.draw_vanishing_lines()

        # 4. UI 狀態文字
        draw_text(10, height - 30, f"Transparent (T): {'ON' if transparent_mode else 'OFF'}")
        draw_text(10, height - 55, f"Guides (G): {'ON' if show_guides else 'OFF'}")
        draw_text(10, height - 80, f"Axes (A): {'ON' if show_axes else 'OFF'}")
        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()

if __name__ == "__main__":
    main()