import chess
import chess.engine
import pickle
import time

def save(data, slot: str) -> None:
    with open(F"{slot}.asdf", "wb+") as f:
        pickle.dump(data, f)
        
def load(slot: str):
    with open(F"{slot}.asdf", "rb") as f:
        return pickle.load(f)
    
def load_fen(idx):
    while True:
        try:
            return load("pickles/fen")
        except:
            print(F"Engine {idx}: error while pickling, trying again in 0.1 seconds")
            time.sleep(0.1)

def analyze(idx: int):
    engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2.exe")
    engine.configure({
        "Hash": 32,
        "Threads": 4,
        # "MultiPV": 5,
    })
    
    print(F"Engine {idx} activated")
        
    while True:
        fen, engine_num = load_fen(idx)
        
        if fen is None:
            engine.quit()
            print(F"Engine {idx} deactivated")
            return
        
        if engine_num == idx:
            while True:
                s = fen
                md = -1
                with engine.analysis(chess.Board(fen), multipv=5) as analysis:
                    for info in analysis:
                        fen, engine_num = load_fen(idx)
                        
                        if engine_num != idx:
                            break
                        
                        if fen != s:
                            break
                        
                        # print(info)
                        if "depth" in info and "score" in info:
                            if info.get("depth") > md:
                                md = info.get("depth")
                                
                                ret = (
                                    info.get("depth"),
                                    info.get("score").white().score(mate_score=10000)
                                )
                                save(ret, "analyses/" + fen.replace("/", "-"))
                                print(F"Engine {idx}: depth {info.get('depth')}")

                        # Arbitrary stop condition.
                        # if info.get("depth", 0) > 20:
                        #     break

if __name__ == "__main__":
    ...
    