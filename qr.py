def display_qr(data):
  for row in data:
    for cell in row:
      if cell == 1:
        print("\033[47m  \033[0m", end="") # black cell
      elif cell == -1:
        print("\033[40m  \033[0m", end="") # white cell
      else:
        print("\033[41m  \033[0m", end="") # free data cell that should have been overwritten
    print()

def finder_pattern(data, xstart, ystart):
  for x in range(7):
    for y in range(7):
      if ((y != 1 and y != 5) or x == 0 or x == 6) and ((x != 1 and x != 5) or y == 0 or y == 6):
        data[y+ystart][x+xstart] = 1
      else:
        data[y+ystart][x+xstart] = -1

# 0 = unclaimed free space
# 1 = black
# -1 = white
def base(version):
  size = (version-1)*4+21
  data = [[0 for i in range(size)] for j in range(size)]
  finder_pattern(data, 0, 0)
  finder_pattern(data, 0, size-7)
  finder_pattern(data, size-7, 0)
  return data

display_qr(base(1))
