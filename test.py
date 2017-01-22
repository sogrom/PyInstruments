from openbry_bm857 import OpenBryBM857


miernik = OpenBryBM857()

for _ in range(1000):
    print(miernik.data)