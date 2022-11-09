import string

def splitCell(cell: list[str]):
  '''Returns column, row'''
  for i in range(len(cell)):
    if i == 0: continue
    f: str = cell[0:i]
    b: str = cell[i:len(cell)]
    if f.isalpha() and b.isnumeric():
      return (f, int(b))

def mathCell(cell, x, y):
  '''Basic addition subtraction with cells'''
  column, row = splitCell(cell)
  return f'{n2a(a2n(column) + x)}{row + y}'

def n2a(n,b=string.ascii_uppercase):
  '''Converts a number column to alpha'''
  d, m = divmod(n,len(b))
  return n2a(d-1,b)+b[m] if d else b[m]

def a2n(col):
  '''Converts alpha to a column number'''
  num = 0
  for c in col:
    if c in string.ascii_letters:
      num = num * 26 + (ord(c.upper()) - ord('A'))
  return num

def countEmpty(data: list):
  return data.count("")

def FindEmptyRow(data, range: str = "A1:A1", excludeCount = 1):
  '''Finds an empty row within range.'''
  start, end = range.split(":")
  # Get the difference between columns
  diff = a2n(end[0]) - a2n(start[0])

  for i, val in enumerate(data):
    # Exclude count = 3 means 3 filled
    # If 2 slots are empty out of 4 where 3 should be empty
    if (len(val) <= excludeCount) or (countEmpty(val) >= (len(val) - excludeCount)):
      return [mathCell(start, 0, i), mathCell(start, diff, i)]
  return None