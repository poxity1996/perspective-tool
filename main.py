import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from models import Cube, draw_axes, COLORS

# --- [SETUP] 全域字體與效能設定 ---
pygame.font.init()
GLOBAL_FONT = pygame.font.SysFont('arial', 18)

# --- [UI_RENDER] 文字渲染 OpenGL 視窗 ---
def draw_text(x, y, text):
    text_surface = GLOBAL_FONT.render(text, True, (50, 50, 50))
    text_data = pygame.image.tobytes(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), 
                 GL_RGBA, GL_UNSIGNED_BYTE, text_data)


# --- [PROJECTION] 設定 3D 透視投影與視窗比例 (處理畫面變形) ---
def reset_projection(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = width / height if height != 0 else 1
    gluPerspective(45, aspect_ratio, 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)


# --- [VIEW] 重置攝影機位置與初始視距 ---
def reset_view():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -8)


# --- [COLLISION] 判斷滑鼠是否觸碰方塊 (3D 座標轉 2D 螢幕點擊判定) --- 
def is_mouse_on_cube(m_x, m_y, cube, current_scale, margin=50):
    """計算方塊在螢幕上的 2D 範圍，判斷滑鼠是否點擊在範圍內"""
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')

    for v in cube.vertices:
        sx, sy, sz = v[0] * current_scale, v[1] * current_scale, v[2] * current_scale
        try:
            win_x, win_y, win_z = gluProject(sx, sy, sz, modelview, projection, viewport)
            py_y = viewport[3] - win_y
            min_x, max_x = min(min_x, win_x), max(max_x, win_x)
            min_y, max_y = min(min_y, py_y), max(max_y, py_y)
        except: continue
    return (min_x - margin <= m_x <= max_x + margin) and (min_y - margin <= m_y <= max_y + margin)

# --- [SCENE] 動態視平線 ---
def draw_horizon(colors_dict): 
    glPushMatrix()
    glLoadIdentity()
    glBegin(GL_LINES)
    glColor3fv(colors_dict['PURE_RED']) 
    glVertex3f(-100, 0, -50) 
    glVertex3f(100, 0, -50)
    glEnd()
    
    glPopMatrix()

# --- [MAIN] 主程式 ---
def main():
    pygame.init()
    width, height = 400, 400

    #設定抗鋸齒採樣
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("3D Perspective Tool")
    
    # 用於控制 FPS，防止 CPU 過度占用導致的操作延遲
    clock = pygame.time.Clock()

    # OpenGL 環境設定
    glEnable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE) 
    glEnable(GL_LINE_SMOOTH)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    reset_projection(width, height)
    reset_view()

    # --- 物件與功能狀態初始化 ---
    cube = Cube()
    transparent_mode = False
    show_guides = False
    show_axes = False
    show_horizon_line = True
    rotate_active = False
    move_active = False
    locked_axis = None
    current_scale = 1.0
    show_ui_menu = False
    threshold = 2

    #  ---載入選單圖示貼圖 ---
    menu_tex_id = None
    try:
        menu_icon_image = pygame.image.load('assets/burger_menu.png')
        img_data = pygame.image.tobytes(menu_icon_image, "RGBA", True)
        menu_tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, menu_tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, menu_icon_image.get_width(), 
                     menu_icon_image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    except Exception as e:
        print(f"圖片載入失敗: {e}")


    # ---程式主迴圈 ---
    running = True
    while running:
        # 偵測退出與視窗縮放
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == VIDEORESIZE:
                width, height = event.size
                reset_projection(width, height)

            # --- [INPUT] 處理鍵盤快捷鍵 (功能切換與視角重置) ---
            if event.type == KEYDOWN:
                if event.key == K_SPACE: reset_view()
                if event.key == K_t: transparent_mode = not transparent_mode
                if event.key == K_g: show_guides = not show_guides
                if event.key == K_a: show_axes = not show_axes
                if event.key == K_h: show_horizon_line = not show_horizon_line

            # --- [INPUT] 處理滑鼠點擊 (UI 選單觸發與 3D 操作啟動) ---
            if event.type == MOUSEBUTTONDOWN:
                m_x, m_y = event.pos
                icon_size, margin_ui = 40, 15
                
                # UI 判定
                if margin_ui <= m_x <= (margin_ui + icon_size) and 0 <= m_y <= (margin_ui + icon_size):
                    if event.button == 1: show_ui_menu = not show_ui_menu
                    continue 

                # 方塊操作判定
                if is_mouse_on_cube(m_x, m_y, cube, current_scale):
                    if event.button == 1: rotate_active = True
                    if event.button == 3: move_active = True
                    
                    # 滾輪操作
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                        if event.button == 4: current_scale *= 1.1
                        if event.button == 5: current_scale *= 0.9
                    else:
                        if event.button == 4: glTranslatef(0, 0, 0.5)
                        if event.button == 5: glTranslatef(0, 0, -0.5)
                    current_scale = max(0.1, current_scale)

            # --- [INPUT] 停止滑鼠操作 (重置狀態) ---
            if event.type == MOUSEBUTTONUP:
                rotate_active = move_active = False
                locked_axis = None

            # --- [INPUT] 處理滑鼠滑動 (執行 3D 旋轉與平移位移) ---
            if event.type == MOUSEMOTION:
                dx, dy = event.rel
                if (rotate_active or move_active) and locked_axis is None:
                    if abs(dx) > threshold or abs(dy) > threshold:
                        locked_axis = 'x' if abs(dx) > abs(dy) else 'y'

                # 執行旋轉變換 (根據鎖定軸向套用旋轉)
                if rotate_active and locked_axis:
                    if locked_axis == 'x': glRotatef(dx * 0.5, 0, 1, 0)
                    else: glRotatef(dy * 0.5, 1, 0, 0)
                    
                # 執行平移變換 (計算相對於攝影機視角的移動)
                if move_active and locked_axis:
                    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
                    axis = (modelview[0][0], modelview[1][0], modelview[2][0]) if locked_axis == 'x' else (modelview[0][1], modelview[1][1], modelview[2][1])
                    speed = dx * 0.01 if locked_axis == 'x' else -dy * 0.01
                    glTranslatef(speed * axis[0], speed * axis[1], speed * axis[2])

        if not running: break

        # --- [RENDER] 繪製 3D 場景 (清除緩衝區、繪製方塊與線框) ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        if show_horizon_line:
            draw_horizon(COLORS)
        glScalef(current_scale, current_scale, current_scale) 

        # --- [OBJECT] 方塊本體渲染 (處理透明度與 Z-Fighting) ---
        alpha = 0.4 if transparent_mode else 1.0
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)
        cube.draw(alpha=alpha) # 繪製方塊實體面
        glDisable(GL_POLYGON_OFFSET_FILL)

        # --- [WIREFRAME] 線框渲染 (一般與透明模式) ---
        if not transparent_mode:
            cube.draw_wireframe(COLORS['BLACK'], width=1.2)
        else:
            glDisable(GL_DEPTH_TEST)
            cube.draw_wireframe(COLORS['INTERNAL_LINE'], width=0.8)
            glEnable(GL_DEPTH_TEST)
            cube.draw_wireframe(COLORS['BLACK'], width=1.2)
            
        # --- [GUIDES] 輔助與重置 ---
        if show_guides: cube.draw_vanishing_lines()
        glPopMatrix()

        # --- [UI] 切換至 2D 渲染模式 (繪製選單圖示與文字) ---
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

        # --- [TEXTURE] 繪製選單按鈕貼圖 ---
        if menu_tex_id:
            glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, menu_tex_id)
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(15, height - 15)
            glTexCoord2f(1, 0); glVertex2f(55, height - 15)
            glTexCoord2f(1, 1); glVertex2f(55, height - 55)
            glTexCoord2f(0, 1); glVertex2f(15, height - 55)
            glEnd()
            glDisable(GL_TEXTURE_2D)

        # --- [UI] 繪製選單與狀態文字 ---
        if show_ui_menu:
            sy = height - 80
            draw_text(10, sy, f"Transparent (T): {'ON' if transparent_mode else 'OFF'}")
            draw_text(10, sy-25, f"Guides (G): {'ON' if show_guides else 'OFF'}")
            draw_text(10, sy-50, f"Axes (A): {'ON' if show_axes else 'OFF'}")
            draw_text(10, sy-75, f"Horizon (H): {'ON' if show_horizon_line else 'OFF'}")

        # --- [RESTORE] 恢復 3D 渲染狀態 ---
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW); glPopMatrix()
        glEnable(GL_DEPTH_TEST)

        # --- [UPDATE] 更新畫面並控制幀率 ---
        pygame.display.flip()
        clock.tick(60) # 穩定 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()