# Simple pygame program

# Import and initialize the pygame library
import pygame
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([1280, 720])
#
colors = []
index_colors = 0
for r in range(256):
    for g in range(256):
        for b in range(256):
            colors.append([r, g, b])
#
print(len(colors))
print((colors[index_colors][0], colors[index_colors][1], colors[index_colors][2]))
break
#
# Run until the user asks to quit
running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((colors[index_colors][0], colors[index_colors][1], colors[index_colors][2]))
    index_colors += 1
    if(index_colors >= len(index_colors)):
        index_colors = 0

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()