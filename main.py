import cv2
import fentoimage.board
import numpy as np
import multiprocessing
import chess
import chess.engine
import chess.svg
import pickle
from PIL import Image, ImageDraw, ImageFont
from sf import analyze

# sf = stockfish.Stockfish(
#     path="stockfish\stockfish-windows-x86-64-avx2.exe",
#     parameters={
#         "Threads": 6,
#         "Hash": 1024,
#     }
# )

coord_to_square = {
    (0, 0): chess.A1, (0, 1): chess.A2, (0, 2): chess.A3, (0, 3): chess.A4,
    (0, 4): chess.A5, (0, 5): chess.A6, (0, 6): chess.A7, (0, 7): chess.A8,
    (1, 0): chess.B1, (1, 1): chess.B2, (1, 2): chess.B3, (1, 3): chess.B4,
    (1, 4): chess.B5, (1, 5): chess.B6, (1, 6): chess.B7, (1, 7): chess.B8,
    (2, 0): chess.C1, (2, 1): chess.C2, (2, 2): chess.C3, (2, 3): chess.C4,
    (2, 4): chess.C5, (2, 5): chess.C6, (2, 6): chess.C7, (2, 7): chess.C8,
    (3, 0): chess.D1, (3, 1): chess.D2, (3, 2): chess.D3, (3, 3): chess.D4,
    (3, 4): chess.D5, (3, 5): chess.D6, (3, 6): chess.D7, (3, 7): chess.D8,
    (4, 0): chess.E1, (4, 1): chess.E2, (4, 2): chess.E3, (4, 3): chess.E4,
    (4, 4): chess.E5, (4, 5): chess.E6, (4, 6): chess.E7, (4, 7): chess.E8,
    (5, 0): chess.F1, (5, 1): chess.F2, (5, 2): chess.F3, (5, 3): chess.F4,
    (5, 4): chess.F5, (5, 5): chess.F6, (5, 6): chess.F7, (5, 7): chess.F8,
    (6, 0): chess.G1, (6, 1): chess.G2, (6, 2): chess.G3, (6, 3): chess.G4,
    (6, 4): chess.G5, (6, 5): chess.G6, (6, 6): chess.G7, (6, 7): chess.G8,
    (7, 0): chess.H1, (7, 1): chess.H2, (7, 2): chess.H3, (7, 3): chess.H4,
    (7, 4): chess.H5, (7, 5): chess.H6, (7, 6): chess.H7, (7, 7): chess.H8,
}

piece_to_img = {
    "P": [cv2.imread(F"assets/white/p{i}.png") for i in range(2)],
    "N": [cv2.imread(F"assets/white/n{i}.png") for i in range(2)],
    "B": [cv2.imread(F"assets/white/b{i}.png") for i in range(2)],
    "R": [cv2.imread(F"assets/white/r{i}.png") for i in range(2)],
    "Q": [cv2.imread(F"assets/white/q{i}.png") for i in range(2)],
    "K": [cv2.imread(F"assets/white/k{i}.png") for i in range(2)],
    "p": [cv2.imread(F"assets/black/p{i}.png") for i in range(2)],
    "n": [cv2.imread(F"assets/black/n{i}.png") for i in range(2)],
    "b": [cv2.imread(F"assets/black/b{i}.png") for i in range(2)],
    "r": [cv2.imread(F"assets/black/r{i}.png") for i in range(2)],
    "q": [cv2.imread(F"assets/black/q{i}.png") for i in range(2)],
    "k": [cv2.imread(F"assets/black/k{i}.png") for i in range(2)],
    "None": [cv2.imread(F"assets/x{i}.png") for i in range(2)],
}

for i in list("PNBRQKpnbrqk") + ["None"]:
    for j in range(2):
        piece_to_img[i][j] = cv2.resize(piece_to_img[i][j], (50, 50))

engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2.exe")
def_img = np.zeros((600, 1200, 3), dtype=np.uint8)

# for i in range(8):
#     for j in range(8):
#         if (i + j) % 2 == 0:
#             def_img[i * 50:i * 50 + 50, j * 50:j * 50 + 50, :] = [40, 120, 200]
            
#         else:
#             def_img[i * 50:i * 50 + 50, j * 50:j * 50 + 50, :] = [0, 50, 100]

# cv2.rectangle(def_img, (0, 0), (400, 400), (255, 255, 255), 5)
def_img[:400, :400, :] = [255, 255, 255]

FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
BOARD = chess.Board()
IMG = def_img.copy()
FONT = lambda x: ImageFont.truetype("fonts/FiraCode-Regular.ttf", x)
CHESSFONT = lambda x: ImageFont.truetype("fonts/Alpha.ttf", x)
ENGINES = 4

def save(data, slot: str) -> None:
    with open(F"{slot}.asdf", "wb+") as f:
        pickle.dump(data, f)
        
def load(slot: str):
    try:
        with open(F"{slot}.asdf", "rb") as f:
            return pickle.load(f)
        
    except:
        return None

engine_num = 0
def save_fen():
    global engine_num
    
    engine_num = (engine_num + 1) % 4
    fen = BOARD.fen()
    print(F"Engine {engine_num} <- {fen}")
    save((fen, engine_num), "pickles/fen")

def draw_chessboard():
    img = def_img.copy()
    
    for i in range(8):
        for j in range(8):
            piece = BOARD.piece_at(coord_to_square[(j, i)]).__str__()
            
            img[50 * (7 - i):50 * (7 - i) + 50, 50 * j:50 * j + 50, :] = piece_to_img[piece][(i + j) % 2]
            
    if lastmove != "None":
        cv2.arrowedLine(
            img,
            (50 * lastmove_coord[0] + 25, 50 * lastmove_coord[1] + 25),
            (50 * lastmove_coord[2] + 25, 50 * lastmove_coord[3] + 25),
            [0, 255, 0],
            2
        )
    
    cv2.imwrite("board.png", img)
    
    img = Image.open("board.png")
    draw = ImageDraw.Draw(img)
    
    draw.text((0, 400), F"{(' ' * 100 + (' '.join(moves)))[-33:]}", (123, 123, 123), FONT(20))
    
    depth, score = load("analyses/" + BOARD.fen().replace("/", "-")) or (0, 0)
    
    score /= 100
    
    draw.text((0, 450), F"{depth = }", (255, 255, 255), FONT(20))
    draw.text((0, 500), F"{score = :+}", (255, 255, 255), FONT(20))
    
    img.save("board.png")
    
    
dragging = False
def onMouse(event, x, y, flags, param):
    global dragging
    global s1
    global s2
    global moves
    global lastmove
    global lastmoves
    global lastmove_coord

    if event == cv2.EVENT_LBUTTONDOWN:
        if x < 400 and y < 400:
            dragging = True
            # print(F"Mouse down: {chr(97 + x // 50)}{8 - y // 50}")
            s1 = (x // 50, 7 - y // 50)
            
    if event == cv2.EVENT_LBUTTONUP:
        if dragging:
            dragging = False
            if x < 400 and y < 400:
                s2 = (x // 50, 7 - y // 50)
                move = F"{chr(97 + s1[0])}{1 + s1[1]}{chr(97 + s2[0])}{1 + s2[1]}"
                lastmove = BOARD.san(chess.Move.from_uci(move))
                lastmove_coord = (s1[0], 7 - s1[1], s2[0], 7 - s2[1])
                lastmoves.append(lastmove_coord)
                moves.append(lastmove)
                print(F"Move: {move}")
                
                if chess.Move.from_uci(move) in BOARD.legal_moves:
                    BOARD.push(chess.Move.from_uci(move))
                    save_fen()
                    
                else:
                    print("illegal move")
                    
        s1 = None
        s2 = None

s1 = None
s2 = None
moves = []
lastmoves = []
lastmove = "None"
lastmove_coord = (0, 0, 0, 0)

def main():
    global s1
    global s2
    global BOARD
    global moves
    global lastmove
    global lastmove_coord

    cv2.imshow("asdf", np.zeros((1, 1, 3), dtype=np.uint8))
    cv2.setMouseCallback("asdf", onMouse)
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == 0x1B:
            print("Preparing to exit")
            cv2.destroyAllWindows()
            engine.quit()
            save((None, -1), "pickles/fen")
            print("Exiting")
            return
        
        if key == 0x2C:
            if len(moves) > 0:
                moves.pop()
                lastmoves.pop()
                BOARD.pop()
                
                lastmove = moves[-1] if moves else "None"
                lastmove_coord = lastmoves[-1] if lastmoves else (0, 0, 0, 0)
                
                save_fen()
        
        draw_chessboard()
        
        cv2.imshow("asdf", cv2.imread("board.png"))

if __name__ == "__main__":
    save_fen()

    p = [
        multiprocessing.Process(target=main),
        multiprocessing.Process(target=analyze, args=(0, )),
        multiprocessing.Process(target=analyze, args=(1, )),
        multiprocessing.Process(target=analyze, args=(2, )),
        multiprocessing.Process(target=analyze, args=(3, )),
    ]
    
    for i in range(5):
        p[i].start()
        
    for i in range(5):
        p[i].join()