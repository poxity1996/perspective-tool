from OpenGL.GL import *

# --- [COLOR_ASSETS] 顏色資產定義 ---
COLORS = {
    'PASTEL_RED':   (1.0, 0.8, 0.8),
    'PASTEL_GREEN': (0.8, 1.0, 0.8),
    'PASTEL_BLUE':  (0.8, 0.8, 1.0),
    'BLACK':        (0.0, 0.0, 0.0),
    'INTERNAL_LINE':(0.5, 0.5, 0.5, 0.5), 
    'GUIDE_LINE':   (0.7, 0.7, 0.7),
    'PURE_RED': (1.0, 0.0, 0.0)
}

# --- [CORE_OBJECT] 方塊幾何定義與渲染 ---
class Cube:
    def __init__(self):
        self.vertices = (
            (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
            (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
        )
        self.surfaces = (
            (0, 1, 5, 4), (2, 3, 6, 7), # X
            (1, 2, 7, 5), (0, 4, 6, 3), # Y
            (4, 5, 7, 6), (0, 1, 2, 3)  # Z
        )
        self.face_colors = (
            COLORS['PASTEL_RED'],   COLORS['PASTEL_RED'],
            COLORS['PASTEL_GREEN'], COLORS['PASTEL_GREEN'],
            COLORS['PASTEL_BLUE'],  COLORS['PASTEL_BLUE']
        )
        self.edges = (
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,7), (7,6), (6,4),
            (0,4), (1,5), (2,7), (3,6)
        )

    # --- 繪製方塊實體面 ---
    def draw(self, alpha=1.0):
        glBegin(GL_QUADS)
        for i, surface in enumerate(self.surfaces):
            r, g, b = self.face_colors[i]
            glColor4f(r, g, b, alpha)
            for vertex_index in surface:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()

    # ---繪製方塊外框---
    def draw_wireframe(self, color, width=2.0):
        glLineWidth(width)
        if len(color) == 4: glColor4fv(color)
        else: glColor3fv(color)
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()

    # --- [PERSPECTIVE] 消失線渲染邏輯 ---
    # 方塊邊緣無限延伸，視覺化透視點的匯聚
    def draw_vanishing_lines(self):
        glLineWidth(1.0)
        glColor3fv(COLORS['GUIDE_LINE'])
        glBegin(GL_LINES)
        for edge in self.edges:
            v1 = list(self.vertices[edge[0]])
            v2 = list(self.vertices[edge[1]])
            for i in range(3):
                delta = v2[i] - v1[i]
                v1[i] -= delta * 1000
                v2[i] += delta * 1000 
            glVertex3fv(v1)
            glVertex3fv(v2)
        glEnd()


# --- [WORLD_REFS] 世界座標基準線 ---
# 繪製 X(紅), Y(綠), Z(藍) 三軸，幫助判斷世界空間方向
def draw_axes():
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(1.0, 0.5, 0.5); glVertex3f(0, 0, 0); glVertex3f(5, 0, 0) # X
    glColor3f(0.5, 1.0, 0.5); glVertex3f(0, 0, 0); glVertex3f(0, 5, 0) # Y
    glColor3f(0.5, 0.5, 1.0); glVertex3f(0, 0, 0); glVertex3f(0, 0, 5) # Z
    glEnd()
