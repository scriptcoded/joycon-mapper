from pyjoycon import get_device_ids, PythonicJoyCon
import time
import math

colors = {
  (180, 0, 230): 'purple',
  (250, 160, 5): 'orange'
}

def remap(old_val, old_range, new_range):
  return (new_range[1] - new_range[0])*(old_val - old_range[0]) / (old_range[1] - old_range[0]) + new_range[0]

def get_color(color: tuple[int, int, int]):
  if color in colors:
    return colors[color]
  return str(color)

class CustomJoyCon(PythonicJoyCon):
  def __init__(self, *a, **kw):
    super().__init__(*a, **kw)
  
  offset_x = 0
  offset_y = 0

  range_x = (0, 0)
  range_y = (0, 0)

  stick_range = 1000
  stick_deadzone = 100

  @property
  def a_uni(self):
    return self.a or self.left

  @property
  def b_uni(self):
    return self.b or self.up

  @property
  def x_uni(self):
    return self.x or self.down

  @property
  def y_uni(self):
    return self.y or self.right

  @property
  def stick(self):
    x, y = self.stick_zeroed

    new_x = 0
    if x < 0:
      new_x = remap(x, (self.range_x[0], 0), (-self.stick_range, 0))
      new_x = remap(new_x+self.stick_deadzone, (-(self.stick_range-self.stick_deadzone), 0), (-self.stick_range, 0))
      new_x = min(new_x, 0)
    else:
      new_x = remap(x, (0, self.range_x[1]), (0, self.stick_range))
      new_x = remap(new_x-self.stick_deadzone, (0, self.stick_range-self.stick_deadzone), (0, self.stick_range))
      new_x = max(new_x, 0)

    new_y = 0
    if y < 0:
      new_y = remap(y, (self.range_y[0], 0), (-self.stick_range, 0))
      new_y = remap(new_y+self.stick_deadzone, (-(self.stick_range-self.stick_deadzone), 0), (-self.stick_range, 0))
      new_y = min(new_y, 0)
    else:
      new_y = remap(y, (0, self.range_y[1]), (0, self.stick_range))
      new_y = remap(new_y-self.stick_deadzone, (0, self.stick_range-self.stick_deadzone), (0, self.stick_range))
      new_y = max(new_y, 0)

    return (new_x, new_y)

  @property
  def stick_zeroed(self):
    x, y = self.stick_raw
    return (x - self.offset_x, y - self.offset_y)

  @property
  def stick_raw(self):
    if self.is_right():
      return self.stick_r
    else:
      return self.stick_l

  def zero_sticks(self):
    self.offset_x = self.stick_raw[0]
    self.offset_y = self.stick_raw[1]

  def calibrate(self):
    self.zero_sticks()

    self.range_x = (math.inf, -math.inf)
    self.range_y = (math.inf, -math.inf)

    wait = True
    while wait:
      x, y = self.stick_zeroed

      self.range_x = (
        min(self.range_x[0], x),
        max(self.range_x[1], x)
      )
      self.range_y = (
        min(self.range_y[0], y),
        max(self.range_y[1], y)
      )

      if self.a_uni:
        wait = False

    print(self.range_x, self.range_y)


def getPlayerNumberPattern(number: int):
  return ~(~0 << number)

joycons: list[CustomJoyCon] = []
device_ids = get_device_ids()

if len(device_ids) < 1:
  print("No controllers found")
  exit(1)

print("Getting controllers", device_ids)
i = 1
for id in device_ids:
  print("Initializing", id)
  joycon = CustomJoyCon(*id)
  joycons.append(joycon)

  # Set player lights
  joycon.set_player_lamp_on(0)
  time.sleep(0.05)
  joycon.set_player_lamp_on(getPlayerNumberPattern(i))

  print("Calibrating", get_color(joycon.color_body))
  time.sleep(1)
  joycon.calibrate()

  i += 1

print("Starting program")
running = True
while running:
  number = 1
  for joycon in joycons:
    # joycon.stick
    if (number == 2):
      print(number, joycon.stick)

    # if joycon.a_uni:
    #   print("Button A on", number)
    # if joycon.b_uni:
    #   print("Button B on", number)
    # if joycon.x_uni:
    #   print("Button X on", number)
    # if joycon.y_uni:
    #   print("Button Y on", number)

    number += 1
