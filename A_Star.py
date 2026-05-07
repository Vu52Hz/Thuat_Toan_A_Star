import pygame
import math
from queue import PriorityQueue

# Kích thước cửa sổ
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Trực quan hóa thuật toán A* - Nhóm 11")

# Định nghĩa các mã màu (RGB)
RED = (255, 0, 0)           # Nút đã duyệt (Closed List)
GREEN = (0, 255, 0)         # Nút đang chờ duyệt (Open List)
BLUE = (0, 0, 255)          # Điểm kết thúc (End)
YELLOW = (255, 255, 0)      # Không gian bị thu hẹp/chưa dùng
WHITE = (255, 255, 255)     # Nút trống
BLACK = (0, 0, 0)           # Vật cản (Wall)
PURPLE = (128, 0, 128)      # Đường đi ngắn nhất (Path)
ORANGE = (255, 165 ,0)      # Điểm bắt đầu (Start)
GREY = (128, 128, 128)      # Đường kẻ lưới

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row       # Vị trí hàng trong ma trận lưới
        self.col = col       # Vị trí cột trong ma trận lưới
        self.x = col * width # Tọa độ X thực tế trên màn hình pixel
        self.y = row * width # Tọa độ Y thực tế trên màn hình pixel
        self.color = WHITE   # Mặc định lúc sinh ra là ô trống (màu trắng)
        self.neighbors = []  # Danh sách các ô hàng xóm (trên, dưới, trái, phải)
        self.width = width   # Kích thước cạnh của ô vuông
        self.total_rows = total_rows # Tổng số hàng của lưới

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == BLUE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = BLUE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Kiểm tra Hướng Phải
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Kiểm tra Hướng Trái
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])
        # Kiểm tra Hướng Dưới
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Kiểm tra Hướng Trên
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        

# Hàm Heuristic (Sử dụng khoảng cách Manhattan)
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# Hàm Heuristic: Euclidean
# def h(p1, p2):
#     x1, y1 = p1
#     x2, y2 = p2
#     return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# Hàm vẽ lại đường đi sau khi tìm thấy đích
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

# Thuật toán A* Lõi
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    # Bảng g_score: Khoảng cách từ start đến node hiện tại
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    # Bảng f_score: f(n) = g(n) + h(n)
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False

# Các hàm thiết lập giao diện lưới
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos
    row = y // gap
    col = x // gap
    return row, col

# Vòng lặp chính
def main(win, width):
    ROWS = 40
    grid = make_grid(ROWS, width)

    start = None
    end = None
    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: # Chuột trái
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != start and node != end:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # Chuột phải
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

if __name__ == "__main__":
    main(WIN, WIDTH)