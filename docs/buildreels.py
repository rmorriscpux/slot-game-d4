import random

weights = [
    [16, 21, 20, 18, 19, 16, 18],
    [18, 21, 21, 19, 16, 18, 15],
    [15, 21, 19, 18, 19, 17, 19]
]

reels = [[],[],[]]

symbols = ["2x", "Cherry", "Orange", "Lemon", "Apple", "Banana", "Strawberry"]

for wtset in range(0, len(weights)):
    for wt in range(0, len(weights[wtset])):
        for i in range(0, weights[wtset][wt]):
            reels[wtset].append(symbols[wt])
            
for reel in reels:
    random.shuffle(reel)
    
outfile = open("reels.txt", "w")
for i in range(0, len(reels[0])):
    print(f"{reels[0][i]}\t{reels[1][i]}\t{reels[2][i]}")
    print("Blank\tBlank\tBlank")
    outfile.write(f"{reels[0][i]}\t{reels[1][i]}\t{reels[2][i]}\n")
    outfile.write("Blank\tBlank\tBlank\n")

outfile.close()