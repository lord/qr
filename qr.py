def display_qr(data):
  for row in data:
    for cell in row:
      if cell == 1:
        print("\033[40m  \033[0m", end="") # black cell
      elif cell == -1:
        print("\033[47m  \033[0m", end="") # white cell
      else:
        print("\033[41m  \033[0m", end="") # free data cell that should have been overwritten
    print()

def finder_pattern(data, xstart, ystart):
  for x in range(xstart, xstart+9):
    for y in range(ystart, ystart+9):
      if x >= 0 and y >= 0 and x < len(data) and y < len(data[0]): # don't draw if off side of code
        from_center = max(abs(x-xstart-4), abs(y-ystart-4))
        if from_center == 2 or from_center == 4:
          data[y][x] = -1
        else:
          data[y][x] = 1

# 0 = unclaimed free space
# 1 = black
# -1 = white
def base(version):
  size = (version-1)*4+21
  data = [[0 for i in range(size)] for j in range(size)]
  finder_pattern(data, -1, -1) # starts at negative 1, since separator is off side of code
  finder_pattern(data, -1, size-8)
  finder_pattern(data, size-8, -1)
  return data

display_qr(base(1))
