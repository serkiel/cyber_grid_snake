import math
import random

ITEM_FOOD = 0
ITEM_OBSTACLE = 1

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_radius = 25
        self.state = "IDLE"  # IDLE, EAT, DODGE, HURT
        self.state_timer = 0
        self.lives = 3
        
    def reset(self):
        self.state = "IDLE"
        self.state_timer = 0
        self.lives = 3
        
    def update(self):
        if self.state_timer > 0:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = "IDLE"
                
    def eat(self):
        if self.state != "HURT":
            self.state = "EAT"
            self.state_timer = 15  # frames of eating action
            
    def dodge(self):
        if self.state != "HURT":
            self.state = "DODGE"
            self.state_timer = 20  # frames of dodging action
            
    def hurt(self):
        self.state = "HURT"
        self.state_timer = 30
        self.lives -= 1

class Item:
    def __init__(self, x, y, item_type, speed):
        self.x = x
        self.y = y
        self.type = item_type
        self.speed = speed
        self.radius = 20
        self.active = True
        
    def update(self):
        if self.active:
            self.x -= self.speed
