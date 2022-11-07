import string

def splitCell(cell: list[str]):
  '''Returns column, row'''
  for i in range(len(cell)):
    if i == 0: continue
    f: str = cell[0:i]
    b: str = cell[i:len(cell)]
    if f.isalpha() and b.isnumeric():
      return (f, b)

def mathCell(cell, x, y):
  column, row = splitCell(cell)
  column = a2n(column)
  row = int(row)

  new_col = n2a(column + x)
  return f'{new_col}{row + y}'

def n2a(n,b=string.ascii_uppercase):
  '''Converts a number column to alpha'''
  d, m = divmod(n,len(b))
  return n2a(d-1,b)+b[m] if d else b[m]

def a2n(col):
  num = 0
  for c in col:
    if c in string.ascii_letters:
      num = num * 26 + (ord(c.upper()) - ord('A'))
  return num

def FindEmptyRow(data, top_left: str = "A1"):
  column, row = splitCell(top_left)
  row = int(row)
  length = 0

  for i, val in enumerate(data):
    if (len(val) <= 1):
      new_col = n2a(a2n(column) + length - 1)
      return [f'{column}{row + i}',f'{new_col}{row + i}']
    elif length == 0:
      length = len(val)
  
  return None