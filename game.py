import pygame
import sys
from bullet import Bullet
from characters import Player, Zombie
import random
from util import check_collision, get_collision

class ZombieShooter:

    def __init__(self, window_width, window_height, world_height, world_width, fps):
        self.window_width = window_width
        self.window_height = window_height
        self.world_height = world_height
        self.world_width = world_width

        self.screen = pygame.display.set_mode((window_width, window_height))

        pygame.display.set_caption('Zombie Shooter')

        self.font = pygame.font.SysFont(None, 36)  # Font size 36

        self.clock = pygame.time.Clock() 
        self.fps = fps

        self.player = Player(world_height=self.world_height, world_width=self.world_width)

        self.background_color = (181, 101, 29) # Light brown
        self.wall_color = (1, 50, 32)
        self.border_color = (255, 0, 0)

        self.bullets = []
        self.zombies = []

        self.walls = [
            pygame.Rect(200, 200, 400, 50),  # A horizontal wall
            pygame.Rect(850, 500, 50, 400),  # A vertical wall
            pygame.Rect(1000, 1000, 300, 50), # Another horizontal wall
            # Add more walls as needed
        ]


    def game_over(self):
        game_over_font = pygame.font.SysFont(None, 100)  # Font size 100 for a big message

        # Render the "You Died" message
        game_over_surface = game_over_font.render('You Died', True, (255, 0, 0))  # Red text
        game_over_rect = game_over_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))

        # Blit the message to the screen
        self.screen.blit(game_over_surface, game_over_rect)

        # Update the display to show the message
        pygame.display.flip()

        # Pause for 2 seconds (2000 milliseconds) before quitting
        pygame.time.wait(2000)

        # Quit the game
        pygame.quit()
        sys.exit()

    def step(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Shooting event: spacebar to fire self.bullets
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # bullet = Bullet(player_x + player_size // 2, player_y + player_size // 2, player.direction)
                        bullet = Bullet(self.player.x, self.player.y, self.player.direction)
                        self.bullets.append(bullet)
                        print("Space pressed. Bullet fired")

            if len(self.zombies) < 5 and random.randint(1, 100) < 3:  # 3% chance of spawning a zombie per frame
                self.zombies.append(Zombie(world_height=self.world_height, world_width=self.world_width, size=80, speed=random.randint(1,2)))  # Instantiate a new zombie

            # Get key presses
            keys = pygame.key.get_pressed()
                
            new_player_x = self.player.x
            if keys[pygame.K_a]:  # Left
                new_player_x -= self.player.speed
                self.player.direction = "left"
            if keys[pygame.K_d]:  # Right
                new_player_x += self.player.speed
                self.player.direction = "right"

            new_player_rect = pygame.Rect(new_player_x, self.player.y, self.player.size, self.player.size)

            collision = check_collision(new_player_rect, self.walls)

            if not collision:
                self.player.x = new_player_x
            

            new_player_y = self.player.y
            if keys[pygame.K_w]:  # Up
                new_player_y -= self.player.speed
                self.player.direction = "up"
            if keys[pygame.K_s]:  # Down
                new_player_y += self.player.speed
                self.player.direction = "down"

            new_player_rect = pygame.Rect(self.player.x, new_player_y, self.player.size, self.player.size)

            collision = check_collision(new_player_rect, self.walls)

            if not collision:
                self.player.y = new_player_y

            # Check for collision with walls
            collision = False
            
            # Update camera position (centered on player)
            camera_x = self.player.x - self.window_width // 2
            camera_y = self.player.y - self.window_height // 2

            # Keep camera within world bounds
            camera_x = max(0, min(camera_x, self.world_width - self.window_width))
            camera_y = max(0, min(camera_y, self.world_height - self.window_height))


            # Move self.zombies toward player and check for collisions with self.bullets
            self.zombies_temp = []
            for zombie in self.zombies:
                if check_collision(zombie.rect, self.bullets):
                    bullet = get_collision(zombie.rect, self.bullets)
                    self.player.score += 1
                    self.bullets.remove(bullet)
                    bullet = None
                elif check_collision(zombie.rect, [self.player.rect]):
                    self.player.health -= 1
                else:
                    self.zombies_temp.append(zombie)
            
            self.zombies = self.zombies_temp


            for zombie in self.zombies:
                zombie.move_toward_player(self.player.x, self.player.y, self.walls)

            # Drawing
            self.screen.fill(self.background_color)  # Fill the screen with white (background)

            score_surface = self.font.render(f'Score: {self.player.score}', True, (0, 0, 0))  # Render the score with black color
            self.screen.blit(score_surface, (10, 10))  # Draw the score at the top-left corner (10, 10)
            health_surface = self.font.render(f'Health: {self.player.health}', True, (0, 0, 0))  # Render the score with black color
            self.screen.blit(health_surface, (10, 35))  # Draw the score at the top-left corner (10, 10)


            # Move and draw self.bullets
            for bullet in self.bullets:
                bullet.move()
                bullet.draw(self.screen, camera_x, camera_y)

            # Draw self.zombies
            # for zombie in self.zombies:
            #     zombie.draw(screen, camera_x, camera_y)

            # Draw the player (adjusted for the camera position)
            player_image = self.player.images[self.player.direction]
            self.player.rect = player_image.get_rect(center=(self.player.x, self.player.y))

            for zombie in self.zombies:
                zombie.draw(self.screen, camera_x, camera_y)


            self.screen.blit(player_image, (self.player.x - camera_x, self.player.y - camera_y))
            
            # Draw the world boundaries for testing
            pygame.draw.rect(self.screen, self.border_color, (0 - camera_x, 0 - camera_y, self.world_width, self.world_height), 5)

            for wall in self.walls:
                pygame.draw.rect(self.screen, self.wall_color, (wall.x - camera_x, wall.y - camera_y, wall.width, wall.height))

            # Update the display
            pygame.display.flip()

            if self.player.health <= 0:
                self.game_over()

            # Cap the frame rate
            self.clock.tick(self.fps)