import plotly.graph_objects as go
import sys
import os

def generate(path):
    a = os.walk(path)
    for b in a:
        print(b)

# Run
if __name__ == "__main__":
    generate(sys.argv[1])