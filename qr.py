from enum import Enum
class Color(Enum):
  white = 1
  black = 2
  unset = 3

class ModuleType(Enum):
  functional = 1
  data = 2

class Module:
  def __init__(self):
    self.color = Color.unset
    self.type = ModuleType.data

def display_qr(data):
  for row in data:
    for cell in row:
      if cell.color == Color.black:
        print("\033[40m  \033[0m", end="")
      elif cell.color == Color.white:
        print("\033[47m  \033[0m", end="")
      else:
        print("\033[41m  \033[0m", end="") # draw as red
    print()

def finder_pattern(data, xstart, ystart):
  for x in range(xstart, xstart+9):
    for y in range(ystart, ystart+9):
      if x >= 0 and y >= 0 and x < len(data) and y < len(data[0]): # don't draw if off side of code
        from_center = max(abs(x-xstart-4), abs(y-ystart-4))
        data[y][x].type = ModuleType.functional
        if from_center == 2 or from_center == 4:
          data[y][x].color = Color.white
        else:
          data[y][x].color = Color.black

# 0 = unclaimed free space
# 1 = black
# -1 = white
def base(version):
  size = (version-1)*4+21
  data = [[Module() for i in range(size)] for j in range(size)]
  finder_pattern(data, -1, -1) # starts at negative 1, since separator is off side of code
  finder_pattern(data, -1, size-8)
  finder_pattern(data, size-8, -1)
  return data

display_qr(base(1))
