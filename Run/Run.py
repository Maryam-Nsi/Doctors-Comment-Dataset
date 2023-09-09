import subprocess
import time
import os

current_directory = os.path.dirname(os.path.realpath(__file__))

subprocess.run(["python",  os.path.join(current_directory,"comment.py")])

subprocess.run(["python",  os.path.join(current_directory,"consume.py")])

print("All messages received")
