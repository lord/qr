def display_qr(data):
  for row in data:
    for cell in row:
      if cell == 1:
        print("\033[47m  \033[0m", end="")
      else:
        print("\033[40m  \033[0m", end="")
    print()

display_qr([[1,0,1,1,0,0,1,1,1], [1,0,1,1,1,0,1,1,1]])
