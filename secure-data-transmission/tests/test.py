import time

def clear_last_line():
    print('\033[F', end='') # Move cursor to the beginning of the line
    # print('\033[K', end='') # Clear from cursor to end of line

print("This is the first line.")
print("This is the second line.")
time.sleep(2)
clear_last_line() # Clear "This is the second line."
print("This is a new second line.")