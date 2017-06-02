from enum import Enum
class Color(Enum):
  white = 1
  black = 2
  unset = 3

class Module:
  def __init__(self):
    self.color = Color.unset
    self.reserved = False

def display_qr(data):
  for row in data:
    for cell in row:
      if cell.color == Color.black:
        print("\033[40m  \033[0m", end="")
      elif cell.color == Color.white:
        print("\033[47m  \033[0m", end="")
      elif cell.reserved == True:
        print("\033[42m  \033[0m", end="") # unset but reserved space
      else:
        print("\033[41m  \033[0m", end="") # completely unset space
    print()

def finder_pattern(data, xstart, ystart):
  for x in range(xstart, xstart+9):
    for y in range(ystart, ystart+9):
      if x >= 0 and y >= 0 and x < len(data) and y < len(data[0]): # don't draw if off side of code
        from_center = max(abs(x-xstart-4), abs(y-ystart-4))
        data[y][x].reserved = True
        if from_center == 2 or from_center == 4:
          data[y][x].color = Color.white
        else:
          data[y][x].color = Color.black

def alignment_pattern(data, xstart, ystart):
  # check to make sure the space isn't occupied by something already
  for x in range(xstart, xstart+5):
    for y in range(ystart, ystart+5):
      if data[y][x].reserved == True:
        return

  for x in range(xstart, xstart+5):
    for y in range(ystart, ystart+5):
      data[y][x].reserved = True
      if max(abs(x-xstart-2), abs(y-ystart-2)) == 1:
        data[y][x].color = Color.white
      else:
        data[y][x].color = Color.black

ALIGNMENT_TABLE = {
  1: [],
  2: [6, 18],
  3: [6, 22],
  4: [6, 26],
  5: [6, 30],
  6: [6, 34],
  7: [6, 22, 38],
  8: [6, 24, 42],
  9: [6, 26, 46],
  10: [6, 28, 50]
}

# 0 = unclaimed free space
# 1 = black
# -1 = white
def base(version):
  size = (version-1)*4+21
  data = [[Module() for i in range(size)] for j in range(size)]

  # add finder patterns
  finder_pattern(data, -1, -1) # starts at negative 1, since separator is off side of code
  finder_pattern(data, -1, size-8)
  finder_pattern(data, size-8, -1)

  # add alignment patters
  aligns = ALIGNMENT_TABLE[version]
  for align_a in aligns:
    for align_b in aligns:
      alignment_pattern(data, align_a-2, align_b-2)

  # add timing patterns
  for i in range(size):
    if data[i][6].reserved == False:
      data[i][6].reserved = True
      data[i][6].color = Color.black if i % 2 == 0 else Color.white
    if data[6][i].reserved == False:
      data[6][i].reserved = True
      data[6][i].color = Color.black if i % 2 == 0 else Color.white

  # add dark module
  data[size-8][8].color = Color.black
  data[size-8][8].reserved = True

  # add reserved areas
  if version < 7:
    data[8][8].reserved = True
    for i in range(0, 8):
      data[i][8].reserved = True
      data[8][i].reserved = True
      data[8][size-i-1].reserved = True
      data[size-i-1][8].reserved = True
  else:
    for i in range(0, 3):
      for j in range(0, 6):
        data[size-9-i][j].reserved = True
        data[j][size-9-i].reserved = True

  return data

import sys
display_qr(base(int(sys.argv[1])))
