from enum import Enum
class Color(Enum):
  white = 1
  black = 2
  unset = 3

class Module:
  def __init__(self):
    self.color = Color.unset
    self.reserved = False

def display_qr(qr):
  for row in qr:
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

def finder_pattern(qr, xstart, ystart):
  for x in range(xstart, xstart+9):
    for y in range(ystart, ystart+9):
      if x >= 0 and y >= 0 and x < len(qr) and y < len(qr[0]): # don't draw if off side of code
        from_center = max(abs(x-xstart-4), abs(y-ystart-4))
        qr[y][x].reserved = True
        if from_center == 2 or from_center == 4:
          qr[y][x].color = Color.white
        else:
          qr[y][x].color = Color.black

def alignment_pattern(qr, xstart, ystart):
  # check to make sure the space isn't occupied by something already
  for x in range(xstart, xstart+5):
    for y in range(ystart, ystart+5):
      if qr[y][x].reserved == True:
        return

  for x in range(xstart, xstart+5):
    for y in range(ystart, ystart+5):
      qr[y][x].reserved = True
      if max(abs(x-xstart-2), abs(y-ystart-2)) == 1:
        qr[y][x].color = Color.white
      else:
        qr[y][x].color = Color.black

def wrap_with_border(qr):
  mod = Module()
  mod.color = Color.white
  mod.reserved = True
  for row in qr:
    row.insert(0, mod)
    row.append(mod)
  qr.insert(0, [mod] * len(qr[0]))
  qr.append([mod] * len(qr[0]))

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
  qr = [[Module() for i in range(size)] for j in range(size)]

  # add finder patterns
  finder_pattern(qr, -1, -1) # starts at negative 1, since separator is off side of code
  finder_pattern(qr, -1, size-8)
  finder_pattern(qr, size-8, -1)

  # add alignment patters
  aligns = ALIGNMENT_TABLE[version]
  for align_a in aligns:
    for align_b in aligns:
      alignment_pattern(qr, align_a-2, align_b-2)

  # add timing patterns
  for i in range(size):
    if qr[i][6].reserved == False:
      qr[i][6].reserved = True
      qr[i][6].color = Color.black if i % 2 == 0 else Color.white
    if qr[6][i].reserved == False:
      qr[6][i].reserved = True
      qr[6][i].color = Color.black if i % 2 == 0 else Color.white

  # add dark module
  qr[size-8][8].color = Color.black
  qr[size-8][8].reserved = True

  # add reserved areas
  if version < 7:
    qr[8][8].reserved = True
    for i in range(0, 8):
      qr[i][8].reserved = True
      qr[8][i].reserved = True
      qr[8][size-i-1].reserved = True
      qr[size-i-1][8].reserved = True
  else:
    for i in range(0, 3):
      for j in range(0, 6):
        qr[size-9-i][j].reserved = True
        qr[j][size-9-i].reserved = True

  return qr

def insert_data(qr, data):
  size = len(qr)
  x = size - 1
  y = size - 1
  upward = True
  first = True # True if first in pair, false if second
  data = list(reversed(data))
  while len(data) > 0:
    # skip inserting this data if module is already reserved
    if not qr[y][x].reserved:
      qr[y][x].color = Color.black if data.pop() else Color.white

    # move to next module
    if first:
      x -= 1
    else:
      x += 1
      y += -1 if upward else 1

    first = not first

    # reverse direction if off one side
    if y < 0:
      upward = False
      x -= 2
      y = 0
    elif y >= size:
      upward = True
      x -= 2
      y = size-1

    if x < 0:
      print("WARNING: Ran out of space when trying to stuff data into qr code")
      return

    # skip reserved timing column
    if x == 6:
      x = 5

version = 5
input_data_str = "01000011111101101011011001000110010101011111011011100110111101110100011001000010111101110111011010000110000001110111011101010110010101110111011000110010110000100010011010000110000001110000011001010101111100100111011010010111110000100000011110000110001100100111011100100110010101110001000000110010010101100010011011101100000001100001011001010010000100010001001011000110000001101110110000000110110001111000011000010001011001111001001010010111111011000010011000000110001100100001000100000111111011001101010101010111100101001110101111000111110011000111010010011111000010110110000010110001000001010010110100111100110101001010110101110011110010100100110000011000111101111011011010000101100100111111000101111100010010110011101111011111100111011111001000100001111001011100100011101110011010101111100010000110010011000010100010011010000110111100001111111111011101011000000111100110101011001001101011010001101111010101001001101111000100010000101000000010010101101010001101101100100000111010000110100011111100000010000001101111011110001100000010110010001001111000010110001101111011000000000"
input_data = list(map(bool, map(int, input_data_str)))
qr = base(version)
insert_data(qr, input_data)
wrap_with_border(qr)
display_qr(qr)
