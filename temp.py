import pickle
import chess

def save(data, slot: str) -> None:
    with open(F"{slot}.asdf", "wb+") as f:
        pickle.dump(data, f)
        
def load(slot: str):
    with open(F"{slot}.asdf", "rb") as f:
        return pickle.load(f)

if __name__ == "__main__":
    dat = load(R"analyses\rnbqkbnr-pppppppp-8-8-8-8-PPPPPPPP-RNBQKBNR w KQkq - 0 1")
    
    print(dat)