from OpenGL.GL import *

class Cube:
    def __init__(self):
        self.vertices = (
            (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
            (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
        )
        self.edges = (
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 7), (7, 6), (6, 4),
            (0, 4), (1, 5), (2, 7), (3, 6)
        )

    def draw(self):
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()

def draw_axes():
    """繪製座標軸幫助辨認空間方位"""
    glBegin(GL_LINES)
    # X軸 (紅色)
    glColor3f(1, 0, 0); glVertex3f(0, 0, 0); glVertex3f(2, 0, 0)
    # Y軸 (綠色)
    glColor3f(0, 1, 0); glVertex3f(0, 0, 0); glVertex3f(0, 2, 0)
    # Z軸 (藍色)
    glColor3f(0, 0, 1); glVertex3f(0, 0, 0); glVertex3f(0, 0, 2)
    glEnd()
    glColor3f(1, 1, 1) # 重設為白色