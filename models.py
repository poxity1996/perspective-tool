from OpenGL.GL import *

COLORS = {
    'PASTEL_RED':   (1.0, 0.8, 0.8),
    'PASTEL_GREEN': (0.8, 1.0, 0.8),
    'PASTEL_BLUE':  (0.8, 0.8, 1.0),
    'BLACK':        (0.0, 0.0, 0.0),    # 外部框線：純黑
    'INTERNAL_LINE':(0.5, 0.5, 0.5, 0.5), # 內部框線：灰色，50%透明度
    'GUIDE_LINE':   (0.7, 0.7, 0.7)
}

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

    def draw(self, alpha=1.0):
        # 1. 繪製面
        glBegin(GL_QUADS)
        for i, surface in enumerate(self.surfaces):
            r, g, b = self.face_colors[i]
            glColor4f(r, g, b, alpha)
            for vertex_index in surface:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()

    def draw_wireframe(self, color, width=2.0):
        """通用線框繪製"""
        glLineWidth(width)
        # 檢查顏色是否有包含 alpha 通道
        if len(color) == 4:
            glColor4fv(color)
        else:
            glColor3fv(color)
            
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()

    def draw_vanishing_lines(self):
        """繪製向外延伸的消失點輔助線"""
        glLineWidth(1.0)
        glColor3fv(COLORS['GUIDE_LINE'])
        glBegin(GL_LINES)
        for edge in self.edges:
            v1 = list(self.vertices[edge[0]])
            v2 = list(self.vertices[edge[1]])
            
            # 計算方向並大幅度延伸線段
            for i in range(3):
                delta = v2[i] - v1[i]
                v1[i] -= delta * 30 # 向一端延伸 30 倍
                v2[i] += delta * 30 # 向另一端延伸 30 倍
                
            glVertex3fv(v1)
            glVertex3fv(v2)
        glEnd()

def draw_axes():
    """繪製世界座標軸"""
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(1.0, 0.5, 0.5); glVertex3f(0, 0, 0); glVertex3f(5, 0, 0) # X
    glColor3f(0.5, 1.0, 0.5); glVertex3f(0, 0, 0); glVertex3f(0, 5, 0) # Y
    glColor3f(0.5, 0.5, 1.0); glVertex3f(0, 0, 0); glVertex3f(0, 0, 5) # Z
    glEnd()