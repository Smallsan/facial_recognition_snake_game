import tkinter as tk
import threading
import random
from deepface import DeepFace
import cv2

class Snake(tk.Canvas):
    SNAKE_SPEED = 100

    def __init__(self):
        super().__init__(width=800, height=820, background="black", highlightthickness=0)

        self.speed_text = self.create_text(70, 10, anchor="nw", 
                                           text=f"Speed: {self.SNAKE_SPEED} Lower Is Faster, Higher is Slower", 
                                           fill="white", font=("TkDefaultFont", 14))


        self.snake_positions = [(100, 100), (80, 100), (60, 100)]
        self.food_position = self.set_new_food_position()
        self.score = 0

        self.direction = "Right"

        self.bind_all("<Key>", self.on_key_press)

        self.load_assets()
        self.draw_border()

        self.pack()

        self.after(100, self.perform_actions)

    def draw_border(self):
        self.create_rectangle(10, 10, 790, 810, outline="white")

    def load_assets(self):
        for position in self.snake_positions:
            self.create_rectangle(*position, *(x+20 for x in position), fill="green", tag="snake")
        self.create_rectangle(*self.food_position, *(x+20 for x in self.food_position), fill="red", tag="food")

    def set_new_food_position(self):
        while True:
            x_position = random.randint(2, 38) * 20
            y_position = random.randint(4, 39) * 20
            food_position = (x_position, y_position)

            if food_position not in self.snake_positions:
                return food_position
                
    def on_key_press(self, e):
        new_direction = e.keysym

        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}

        if new_direction in opposites and opposites[new_direction] != self.direction:
            self.direction = new_direction

    def perform_actions(self):
        if self.check_collisions():
            return

        self.check_food_collision()

        self.move_snake()

        self.after(self.SNAKE_SPEED, self.perform_actions)

    def check_collisions(self):
        head_x_position, head_y_position = self.snake_positions[0]

        return (
            head_x_position in (0, 800)
            or head_y_position in (0, 820)
            or (head_x_position, head_y_position) in self.snake_positions[1:]
        )
    
    def check_food_collision(self):
        if self.snake_positions[0] == self.food_position:
            self.score += 1
            self.snake_positions.append(self.snake_positions[-1])
            self.create_rectangle(*self.snake_positions[-1], *(x+20 for x in self.snake_positions[-1]), fill="green", tag="snake")
            self.delete("food")
            self.food_position = self.set_new_food_position()
            self.create_rectangle(*self.food_position, *(x+20 for x in self.food_position), fill="red", tag="food")

    def move_snake(self):
        head_x_position, head_y_position = self.snake_positions[0]

        if self.direction == "Left":
            new_head_position = (head_x_position - 20, head_y_position)
        elif self.direction == "Right":
            new_head_position = (head_x_position + 20, head_y_position)
        elif self.direction == "Up":
            new_head_position = (head_x_position, head_y_position - 20)
        elif self.direction == "Down":
            new_head_position = (head_x_position, head_y_position + 20)

        self.snake_positions = [new_head_position] + self.snake_positions[:-1]

        for segment, position in zip(self.find_withtag("snake"), self.snake_positions):
            self.coords(segment, *position, *(x+20 for x in position))


    def adjust_speed_based_on_expression(self):
        print("Starting adjust_speed_based_on_expression")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame")
                break
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

            # Check if result is a list
            if isinstance(result, list):
                # If it's a list, use the first dictionary in the list
                result = result[0]

            expression = result['dominant_emotion']

            if expression == 'happy':
                self.SNAKE_SPEED = self.SNAKE_SPEED + 2
                print("Happy expression detected, speed increased to", self.SNAKE_SPEED)
            elif expression == 'sad':
                self.SNAKE_SPEED = self.SNAKE_SPEED - 2
                print("Sad expression detected, speed decreased to", self.SNAKE_SPEED)
            elif expression == 'neutral':
                self.SNAKE_SPEED = self.SNAKE_SPEED - 1
                print("Sad expression detected, speed decreased to", self.SNAKE_SPEED)

            # Update the speed display
            self.itemconfigure(self.speed_text, text=f"Speed: {self.SNAKE_SPEED}")

            # Display the frame
            cv2.imshow('Webcam Feed', frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting adjust_speed_based_on_expression")
                break

        cap.release()
        cv2.destroyAllWindows()

    

root = tk.Tk()
root.title("Snake Game")
board = Snake()

threading.Thread(target=board.adjust_speed_based_on_expression, daemon=True).start()

root.mainloop()