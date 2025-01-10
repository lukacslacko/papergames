import random

RADIUS = 30
OUT_RATIO = 1
IN_RATIO = 0.2
GRID_SIZE = 6
W = 297
H = 210

def randpoint():
  return (RADIUS + random.random() * (W - 2*RADIUS), RADIUS + random.random() * (H - 2*RADIUS))

def randpoints():
  pts = [randpoint()]
  while True:
    nextpts = [randpoint() for _ in range(1000)]
    # Discard points that are too close to existing points
    nextpts = [p for p in nextpts if all(((p[0]-x[0])**2 + (p[1]-x[1])**2) > 4*RADIUS**2 for x in pts)]
    # Choose the point closest to the selected points
    if not nextpts:
      break
    # pts.append(min(nextpts, key=lambda p: min((p[0]-x[0])**2 + (p[1]-x[1])**2 for x in pts)))
    # pts.append(min(nextpts, key=lambda p: sum((p[0]-x[0])**2 + (p[1]-x[1])**2 for x in pts)))
    pts.append(min(nextpts, key=lambda p: -sum(((p[0]-x[0])**2 + (p[1]-x[1])**2)**.5 for x in pts)))
  return pts

def min_spanning_tree(pts):
  edges = []
  components = {}
  all_edges = [(i,j) for i in range(len(pts)) for j in range(i+1, len(pts))]
  all_edges.sort(key=lambda e: (pts[e[0]][0]-pts[e[1]][0])**2 + (pts[e[0]][1]-pts[e[1]][1])**2)
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
    return ((x - x1)**2 + (y - y1)**2)**0.5
  t = ((x - x1) * dx + (y - y1) * dy) / (dx**2 + dy**2)
  t = max(0, min(1, t))
  return ((x - (x1 + t * dx))**2 + (y - (y1 + t * dy))**2)**0.5

def distance_from_edges(p, edges):
  return min(distance_from_segment(p, a, b) for a, b in edges)

def render_graph(edges, to_pdf=False):
  pixels = []
  # Edges is a list of ((x1, y1), (x2, y2)) tuples.
  # Render the graph as a matplotlib figure, making the axis span [0,W] and [0,H].
  import matplotlib.pyplot as plt
  # for (x1, y1), (x2, y2) in edges:
  #   plt.plot([x1, x2], [y1, y2], 'k-')
  # Draw a circle of radius RADIUS around each point
  # for edge in edges:
  #   for x, y in edge:
  #     plt.gca().add_artist(plt.Circle((x, y), RADIUS, fill=False))
  # Create a figure WxH in mm.
  plt.figure(figsize=(W/25.4, H/25.4))
  plt.xlim(0, W)
  plt.ylim(0, H)
  # Iterate over all integer pixels and render them if they are between 0.1 * RADIUS and 0.9 * RADIUS from the nearest edge.
  for x in range(0, W, GRID_SIZE):
    for y in range(0, H, GRID_SIZE):
      if distance_from_edges((x, y), edges) < OUT_RATIO*RADIUS and distance_from_edges((x, y), edges) > IN_RATIO * RADIUS:
        plt.plot([x], [y], 'ro', alpha=0.7, fillstyle='none')
        pixels.append((x, y))
  # Draw a grey grid every GRID_SIZE units
  for x in range(0, W, GRID_SIZE):
    plt.plot([x, x], [0, H], 'k-', alpha=0.1)
  for y in range(0, H, GRID_SIZE):
    plt.plot([0, W], [y, y], 'k-', alpha=0.1)

  shape = "g-"
  d = GRID_SIZE * .7
  dd = GRID_SIZE - d
  for x in range(0, W, GRID_SIZE):
    for y in range(0, H, GRID_SIZE):
      square = [(x,y) in pixels, (x+GRID_SIZE,y) in pixels, (x+GRID_SIZE,y+GRID_SIZE) in pixels, (x,y+GRID_SIZE) in pixels]
      if square.count(True) == 0:
        continue
      if square.count(True) == 4:
        continue
      if square.count(True) == 3:
        if not square[0]:
          plt.plot([x, x+dd], [y+dd, y], shape)
        if not square[1]:
          plt.plot([x+d, x+GRID_SIZE], [y, y+dd], shape)
        if not square[2]:
          plt.plot([x+d, x+GRID_SIZE], [y+GRID_SIZE, y+d], shape)
        if not square[3]:
          plt.plot([x, x+dd], [y+d, y+GRID_SIZE], shape)
      if square.count(True) == 1:
        if square[0]:
          plt.plot([x, x+d], [y+d, y], shape)
        if square[1]:
          plt.plot([x+dd, x+GRID_SIZE], [y, y+d], shape)
        if square[2]:
          plt.plot([x+dd, x+GRID_SIZE], [y+GRID_SIZE, y+dd], shape)
        if square[3]:
          plt.plot([x, x+d], [y+dd, y+GRID_SIZE], shape)
      if square.count(True) == 2:
        if square[0] and square[1]:
          plt.plot([x, x+GRID_SIZE], [y+d, y+d], shape)
        if square[2] and square[3]:
          plt.plot([x, x+GRID_SIZE], [y+dd, y+dd], shape)
        if square[0] and square[3]:
          plt.plot([x+d, x+d], [y, y+GRID_SIZE], shape)
        if square[1] and square[2]:
          plt.plot([x+dd, x+dd], [y, y+GRID_SIZE], shape)
        if square[0] and square[2]:
          plt.plot([x, x+d], [y+d, y], shape)
          plt.plot([x+dd, x+GRID_SIZE], [y+GRID_SIZE, y+dd], shape)
        if square[1] and square[3]:
          plt.plot([x+dd, x+GRID_SIZE], [y, y+d], shape)
          plt.plot([x, x+d], [y+dd, y+GRID_SIZE], shape)
  if not to_pdf:
    plt.show()
  else:
    # Only render the inside of the figure, no axis, no labels, no other things.
    plt.axis('off')
    plt.savefig('raceway.pdf', bbox_inches='tight', pad_inches=0)


pts = randpoints()
print(len(pts))
edges = min_spanning_tree(pts)
render_graph(edges, to_pdf=True)
