from gpiozero import Button

# Button GPIO Pin mappings
button_a = Button(5)
button_b = Button(6)
button_x = Button(16)
button_y = Button(24)

def button_pressed(button_name):
    print(f"{button_name} pressed")

button_a.when_pressed = lambda: button_pressed("A")
button_b.when_pressed = lambda: button_pressed("B")
