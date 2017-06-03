from enum import Enum
import math
from copy import deepcopy

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

# TODO test all masks with QR code reader by forcing a mask
MASKS = [
  lambda col, row: (row + col) % 2 == 0,
  lambda col, row: row % 2 == 0,
  lambda col, row: col % 3 == 0,
  lambda col, row: (row + col) % 3 == 0,
  lambda col, row: (row//2 + col//3) % 2 == 0,
  lambda col, row: ((row*col) % 2) + ((row*col) % 3) == 0,
  lambda col, row: ((((row*col) % 2) + ((row*col) % 3))) % 2 == 0, # TODO check order of operations of this
  lambda col, row: ((((row+col) % 2) + ((row*col) % 3))) % 2 == 0 # TODO check order of operations of this
]

CORRECTION_INT_TABLE = {
  "L": 0b01,
  "M": 0b00,
  "Q": 0b11,
  "H": 0b10
}

CONDITION_3_PATTERN = [False, False, False, False, True, False, True, True, True, False, True]

class Color(Enum):
  white = 1
  black = 2
  unset = 3

class Module:
  def __init__(self):
    self.color = Color.unset
    self.reserved = False
    self.mark = False # mark for debugging purposes

def display_qr(qr):
  for row in qr:
    for cell in row:
      msg = "  "
      if cell.mark:
        msg = " "
        print(cell.mark, end="")
      if cell.color == Color.black:
        print("\033[40m" + msg + "\033[0m", end="")
      elif cell.color == Color.white:
        print("\033[47m" + msg + "\033[0m", end="")
      elif cell.reserved == True:
        print("\033[42m" + msg + "\033[0m", end="") # unset but reserved space
      else:
        print("\033[41m" + msg + "\033[0m", end="") # completely unset space
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
  qr[8][8].reserved = True
  for i in range(0, 8):
    qr[i][8].reserved = True
    qr[8][i].reserved = True
    qr[8][size-i-1].reserved = True
    qr[size-i-1][8].reserved = True
  if version >= 7:
    for i in range(0, 3):
      for j in range(0, 6):
        qr[size-9-i][j].reserved = True
        qr[j][size-9-i].reserved = True

  return qr

def apply_mask(qr, mask):
  qr = deepcopy(qr)
  size = len(qr)
  for x in range(size):
    for y in range(size):
      if mask(x, y) and not qr[y][x].reserved:
        if qr[y][x].color == Color.black:
          qr[y][x].color = Color.white
        else:
          qr[y][x].color = Color.black
  return qr

def get_penalty_score(qr):
  penalty = 0
  size = len(qr)

  # eval condition 1
  for flipped in [False, True]:
    for i in range(size):
      white = 0
      black = 0
      for j in range(size):
        cell = qr[i][j] if flipped else qr[j][i]
        if cell.color == Color.black: # count unset squares as white
          white = 0
          black += 1
        else:
          black = 0
          white += 1

        if white == 5 or black == 5:
          penalty += 3
        elif white > 5 or black > 5:
          penalty += 1

  # eval condition 2
  for x in range(size-1):
    for y in range(size-1):
      first = qr[y][x].color == Color.black
      all_same = True
      for i in range(2):
        for j in range(2):
          if first != (qr[y+i][x+j].color == Color.black):
            all_same = False
      if all_same:
        penalty += 3

  # eval condition 3
  for flip_axis in [False, True]:
    for x in range(size-10 if flip_axis else size):
      for y in range(size if flip_axis else size-10):
        matched_forward = True
        matched_backward = True
        for i in range(11):
          mod = qr[y][x+i] if flip_axis else qr[y+i][x]
          if (mod.color == Color.black) != CONDITION_3_PATTERN[i]:
            matched_forward = False
          if (mod.color == Color.black) != CONDITION_3_PATTERN[-i-1]:
            matched_backward = False

        if matched_forward or matched_backward:
          penalty += 40
          mod = qr[y][x+1] if flip_axis else qr[y+1][x]

  # eval condition 4
  total_count = size ** 2
  dark_count = 0
  for row in qr:
    for item in row:
      if item.color == Color.black:
        dark_count += 1
  per_20 = (dark_count / total_count) * 20
  low = abs(math.floor(per_20)*5 - 50) // 5 # next down multiple of 5 of the percent dark
  high = abs(math.ceil(per_20)*5 - 50) // 5 # next up multiple of 5 of the percent dark
  penalty += min(low, high) * 10

  return penalty

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

def get_format_string(correction_level, mask_pattern):
  gen_poly = 0b10100110111
  mask_string = 0b101010000010010
  msg_bits = (CORRECTION_INT_TABLE[correction_level] << 3) | mask_pattern
  error_bits = msg_bits << 10
  while len(bin(error_bits)) > 12:
    len_diff = len(bin(error_bits)) - 13
    error_bits = (gen_poly << len_diff) ^ error_bits
  final = bin(((msg_bits << 10) | error_bits) ^ mask_string)
  final = final[2:] # get rid of '0b' in string
  final_list = list(map(bool, map(int, final))) # convert to array of bools
  while len(final_list) < 15: # left pad out to 15 long with zeros
    final_list.insert(0, False)
  return final_list

def insert_format_string(qr, format_str):
  size = len(qr)
  format_str = list(reversed(format_str))
  for i in range(15):
    color = Color.black if format_str[i] else Color.white
    if i <= 7:
      qr[8][size-i-1].color = color
      if i >= 6: # skip over timing pattern
        qr[i+1][8].color = color
      else:
        qr[i][8].color = color
    else:
      qr[i+size-7-8][8].color = color
      if i == 8:
        qr[8][7].color = color
      else:
        qr[8][5+9-i].color = color

def get_version_string(version):
  res = {
    7:  "000111110010010100",
    8:  "001000010110111100",
    9:  "001001101010011001",
    10: "001010010011010011"
  }[version]
  return list(map(bool, map(int, res)))

def insert_version_string(qr, version_str):
  size = len(qr)
  for i in range(18):
    color = Color.black if version_str[i] else Color.white
    j = i % 3
    k = i // 3
    qr[5-k][size-9-j].color = color
    qr[size-9-j][5-k].color = color
    qr[size-9-j][5-k].mark = str(i % 10)

def generate_qr(version, input_data_str):
  # put in data
  input_data = list(map(bool, map(int, input_data_str)))
  qr = base(version)
  insert_data(qr, input_data)

  # select best mask
  best_score = -1
  best_mask = 0
  for i in range(len(MASKS)):
    score = get_penalty_score(apply_mask(qr, MASKS[i]))
    if best_score == -1 or score < best_score:
      best_score = score
      best_mask = i
  qr = apply_mask(qr, MASKS[best_mask])

  # calculate and add format string
  format_str = get_format_string("Q", best_mask) # TODO set correct correction level
  insert_format_string(qr, format_str)

  if version >= 7:
    version_str = get_version_string(version)
    insert_version_string(qr, version_str)

  # wrap with border and display
  wrap_with_border(qr)
  wrap_with_border(qr)
  display_qr(qr)
