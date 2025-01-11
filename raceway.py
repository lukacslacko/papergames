import random
import matplotlib.pyplot as plt

RADIUS = 30
IN_RATIO = 0.2
OUT_RATIO = 1
GRID_SIZE = 6
W = 297
H = 210
SEED = 111
random.seed(SEED)

SOLVE = True

start_x = 20 * GRID_SIZE
start_y_min = 0 * GRID_SIZE
start_y_max = 5 * GRID_SIZE
start_y = 2 * GRID_SIZE

def description():
  return f"{SEED} R{RADIUS} {IN_RATIO}-{OUT_RATIO} {W}x{H}/{GRID_SIZE} {start_x//GRID_SIZE}:{start_y//GRID_SIZE} {start_y_min//GRID_SIZE}-{start_y_max//GRID_SIZE}"

def randpoint():
  return (
    RADIUS + random.random() * (W - 2 * RADIUS),
    RADIUS + random.random() * (H - 2 * RADIUS),
  )


def randpoints():
  pts = [randpoint()]
  while True:
    nextpts = [randpoint() for _ in range(1000)]
    # Discard points that are too close to existing points
    nextpts = [
      p
      for p in nextpts
      if all(((p[0] - x[0]) ** 2 + (p[1] - x[1]) ** 2) > 4 * RADIUS**2 for x in pts)
    ]
    # Choose the point closest to the selected points
    if not nextpts:
      break
    # pts.append(min(nextpts, key=lambda p: min((p[0]-x[0])**2 + (p[1]-x[1])**2 for x in pts)))
    # pts.append(min(nextpts, key=lambda p: sum((p[0]-x[0])**2 + (p[1]-x[1])**2 for x in pts)))
    pts.append(
      min(
        nextpts,
        key=lambda p: -sum(
          ((p[0] - x[0]) ** 2 + (p[1] - x[1]) ** 2) ** 0.5 for x in pts
        ),
      )
    )
  return pts


def min_spanning_tree(pts):
  edges = []
  components = {}
  all_edges = [(i, j) for i in range(len(pts)) for j in range(i + 1, len(pts))]
  all_edges.sort(
    key=lambda e: (pts[e[0]][0] - pts[e[1]][0]) ** 2
    + (pts[e[0]][1] - pts[e[1]][1]) ** 2
  )
  while all_edges:
    edge = all_edges.pop(0)
    a = edge[0]
    b = edge[1]
    if a not in components and b not in components:
      next_component = len(components)
      components[a] = next_component
      components[b] = next_component
      edges.append(edge)
      continue
    if a in components and b not in components:
      components[b] = components[a]
      edges.append(edge)
      continue
    if a not in components and b in components:
      components[a] = components[b]
      edges.append(edge)
      continue
    if components[a] == components[b]:
      continue
    edges.append(edge)
    old_component = components[b]
    for k in components:
      if components[k] == old_component:
        components[k] = components[a]
  return [(pts[i], pts[j]) for i, j in edges]


def distance_from_segment(p, a, b):
  # Return the distance from point p to the line segment from a to b.
  # If the point is outside the segment, return the distance to the closest endpoint.
  # If the point is inside the segment, return 0.
  # https://stackoverflow.com/a/6853926
  x, y = p
  x1, y1 = a
  x2, y2 = b
  dx = x2 - x1
  dy = y2 - y1
  if dx == dy == 0:
    return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
  t = ((x - x1) * dx + (y - y1) * dy) / (dx**2 + dy**2)
  t = max(0, min(1, t))
  return ((x - (x1 + t * dx)) ** 2 + (y - (y1 + t * dy)) ** 2) ** 0.5


def distance_from_edges(p, edges):
  return min(distance_from_segment(p, a, b) for a, b in edges)


pixels = []
borders = []


def render_graph(edges):
  global pixels, borders
  # Edges is a list of ((x1, y1), (x2, y2)) tuples.
  # Render the graph as a matplotlib figure, making the axis span [0,W] and [0,H].

  # for (x1, y1), (x2, y2) in edges:
  #   plt.plot([x1, x2], [y1, y2], 'k-')
  # Draw a circle of radius RADIUS around each point
  # for edge in edges:
  #   for x, y in edge:
  #     plt.gca().add_artist(plt.Circle((x, y), RADIUS, fill=False))
  # Create a figure WxH in mm.
  plt.figure(figsize=(W / 25.4, H / 25.4))
  plt.xlim(0, W)
  plt.ylim(0, H)
  # Add the description in the corner in tiny font.
  plt.text(5, 5, description(), fontsize=4, verticalalignment="bottom")
  # Iterate over all integer pixels and render them if they are between 0.1 * RADIUS and 0.9 * RADIUS from the nearest edge.
  for x in range(0, W, GRID_SIZE):
    for y in range(0, H, GRID_SIZE):
      if (
        distance_from_edges((x, y), edges) < OUT_RATIO * RADIUS
        and distance_from_edges((x, y), edges) > IN_RATIO * RADIUS
      ):
        plt.plot([x], [y], "ro", alpha=0.7, fillstyle="none")
        pixels.append((x, y))
  # Draw a grey grid every GRID_SIZE units
  for x in range(0, W, GRID_SIZE):
    plt.plot([x, x], [0, H], "k-", alpha=0.1)
  for y in range(0, H, GRID_SIZE):
    plt.plot([0, W], [y, y], "k-", alpha=0.1)

  shape = "g-"
  d = GRID_SIZE * 0.7
  dd = GRID_SIZE - d
  for x in range(0, W, GRID_SIZE):
    for y in range(0, H, GRID_SIZE):
      square = [
        (x, y) in pixels,
        (x + GRID_SIZE, y) in pixels,
        (x + GRID_SIZE, y + GRID_SIZE) in pixels,
        (x, y + GRID_SIZE) in pixels,
      ]
      if square.count(True) == 0:
        continue
      if square.count(True) == 4:
        continue
      if square.count(True) == 3:
        if not square[0]:
          plt.plot([x, x + dd], [y + dd, y], shape)
          borders.append(((x, y + dd), (x + dd, y)))
        if not square[1]:
          plt.plot([x + d, x + GRID_SIZE], [y, y + dd], shape)
          borders.append(((x + d, y), (x + GRID_SIZE, y + dd)))
        if not square[2]:
          plt.plot([x + d, x + GRID_SIZE], [y + GRID_SIZE, y + d], shape)
          borders.append(((x + d, y + GRID_SIZE), (x + GRID_SIZE, y + d)))
        if not square[3]:
          plt.plot([x, x + dd], [y + d, y + GRID_SIZE], shape)
          borders.append(((x, y + d), (x + dd, y + GRID_SIZE)))
      if square.count(True) == 1:
        if square[0]:
          plt.plot([x, x + d], [y + d, y], shape)
          borders.append(((x, y + d), (x + d, y)))
        if square[1]:
          plt.plot([x + dd, x + GRID_SIZE], [y, y + d], shape)
          borders.append(((x + dd, y), (x + GRID_SIZE, y + d)))
        if square[2]:
          plt.plot([x + dd, x + GRID_SIZE], [y + GRID_SIZE, y + dd], shape)
          borders.append(((x + dd, y + GRID_SIZE), (x + GRID_SIZE, y + dd)))
        if square[3]:
          plt.plot([x, x + d], [y + dd, y + GRID_SIZE], shape)
          borders.append(((x, y + dd), (x + d, y + GRID_SIZE)))
      if square.count(True) == 2:
        if square[0] and square[1]:
          plt.plot([x, x + GRID_SIZE], [y + d, y + d], shape)
          borders.append(((x, y + d), (x + GRID_SIZE, y + d)))
        if square[2] and square[3]:
          plt.plot([x, x + GRID_SIZE], [y + dd, y + dd], shape)
          borders.append(((x, y + dd), (x + GRID_SIZE, y + dd)))
        if square[0] and square[3]:
          plt.plot([x + d, x + d], [y, y + GRID_SIZE], shape)
          borders.append(((x + d, y), (x + d, y + GRID_SIZE)))
        if square[1] and square[2]:
          plt.plot([x + dd, x + dd], [y, y + GRID_SIZE], shape)
          borders.append(((x + dd, y), (x + dd, y + GRID_SIZE)))
        if square[0] and square[2]:
          plt.plot([x, x + d], [y + d, y], shape)
          borders.append(((x, y + d), (x + d, y)))
          plt.plot([x + dd, x + GRID_SIZE], [y + GRID_SIZE, y + dd], shape)
          borders.append(((x + dd, y + GRID_SIZE), (x + GRID_SIZE, y + dd)))
        if square[1] and square[3]:
          plt.plot([x + dd, x + GRID_SIZE], [y, y + d], shape)
          borders.append(((x + dd, y), (x + GRID_SIZE, y + d)))
          plt.plot([x, x + d], [y + dd, y + GRID_SIZE], shape)
          borders.append(((x, y + dd), (x + d, y + GRID_SIZE)))
  for y in range(start_y_min, start_y_max + GRID_SIZE, GRID_SIZE):
    plt.plot([start_x], [y], "ko", alpha=0.7)

def save_pdf(name):
  # Only render the inside of the figure, no axis, no labels, no other things.
  plt.axis("off")
  plt.savefig(f"{name}.pdf", bbox_inches="tight", pad_inches=0)


def segments_intersect(a, b, c, d):
  # Return True if the segments ab and cd intersect.
  def ccw(A, B, C):
    val = (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])
    if val < 0:
      return -1
    if val > 0:
      return 1
    return 0

  return ccw(a, c, d) * ccw(b, c, d) <= 0 and ccw(a, b, c) * ccw(a, b, d) <= 0


def is_winning_step(step):
  a = (step[0][0], step[0][1])
  b = (step[0][0] + step[1][0], step[0][1] + step[1][1])
  return segments_intersect(a, b, (start_x, start_y_min), (start_x, start_y_max)) and step[1][0] > 0

def is_good_step(step):
  a = step[0]
  b = (step[0][0] + step[1][0], step[0][1] + step[1][1])
  for border in borders:
    if segments_intersect(a, b, border[0], border[1]):
      return False
  if segments_intersect(a, b, (start_x, start_y_min), (start_x, start_y_max)):
    return step[1][0] > 0
  return True


def find_shortest_path():
  first_state = ((start_x, start_y), (GRID_SIZE, 0))
  just_seen = {first_state}
  done = set()
  come_from = {first_state: None}
  iter = 0
  while just_seen:
    iter += 1
    print(iter, len(just_seen), len(done))
    next_round = set()
    while just_seen:
      visit_now = just_seen.pop()
      done.add(visit_now)
      for ax in [-1, 0, 1]:
        for ay in [-1, 0, 1]:
          if ax == ay == 0:
            continue
          next_state = (
            (
              visit_now[0][0] + visit_now[1][0],
              visit_now[0][1] + visit_now[1][1],
            ),
            (visit_now[1][0] + ax * GRID_SIZE, visit_now[1][1] + ay * GRID_SIZE),
          )
          if next_state in done:
            continue
          if next_state in just_seen:
            continue
          if next_state in next_round:
            continue
          if not is_good_step(next_state):
            continue
          if is_winning_step(next_state):
            come_from[next_state] = visit_now
            return next_state, come_from
          come_from[next_state] = visit_now
          next_round.add(next_state)
    just_seen = next_round




pts = randpoints()
print(len(pts))
edges = min_spanning_tree(pts)
render_graph(edges)
if SOLVE:
  last_state, come_from = find_shortest_path()
  while last_state is not None:
    plt.plot([last_state[0][0]], [last_state[0][1]], "yo")
    plt.plot([last_state[0][0], last_state[0][0] + last_state[1][0]], [last_state[0][1], last_state[0][1] + last_state[1][1]], "b-")
    last_state = come_from[last_state]
save_pdf("solution" if SOLVE else "raceway")
