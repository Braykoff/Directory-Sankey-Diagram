import plotly.graph_objects as go
from plotly.offline import plot
from pathlib import Path
import math
import argparse

def generate(pathString, ignoreFiles, htmlOut, imgOut, width, height):
    # Make sure at least one output
    if htmlOut == None and imgOut == None:
        htmlOut = "output.html"

    path = Path(pathString)

    # Check if path exists
    if not path.exists():
        raise Exception(f"Path '{path}' does not exist!")
    
    # Init Sankey diagram
    labels = [] # Label names
    sources = [] # Source of each flow (idx in labels)
    targets = [] # Target of each flow (idx in labels)
    values = [] # Value (width) of each flow

    addedPaths = [] # indexes here match indexes in labels

    # Walk directories
    walk = list(path.walk())
    total = len(walk)
    tenPercent = max(math.floor(total / 10), 1)

    for i in range(total):
        root, _, files = walk[i]
        # Add root folder
        labels.append(root.parts[-1])
        rootIdx = len(labels)-1
        addedPaths.append(root)
        
        if len(addedPaths) > 1:
            # This is not the first path, create flow to parent path
            prevIndex = addedPaths.index(root.parent)
            sources.append(prevIndex)
            targets.append(rootIdx)

            directorySize = sum(file.stat().st_size for file in root.rglob("*") if file.is_file())
            values.append(directorySize) # sum of size of all descendent files

        # Add child files
        if not ignoreFiles:
            for file in files:
                labels.append(file)
                sources.append(rootIdx)
                targets.append(len(labels)-1)
                values.append(root.joinpath(file).stat().st_size) # file size in bytes

                addedPaths.append(None) # to keep indexes here congruent with labels

        # Output every 10%
        if i % tenPercent == 0:
            print(f"Checked {i+1} of {total} subdirectories")
    
    # Create figure
    fig = go.Figure(data=[go.Sankey(
        node = {
            "pad": 15,
            "thickness": 20,
            "line": {"color": "black", "width": 0.5},
            "label": labels,
            "color": "blue"
        },
        link = {
           "source": sources,
           "target": targets,
           "value": values 
        }
    )])

    fig.update_layout(
        title_text=str(path.absolute()), 
        font_size=12,
        autosize=False,
        width=width,
        height=height
    )
    
    if htmlOut is not None:
        plot(fig, filename=str(htmlOut))

    if imgOut is not None:
        fig.write_image(str(imgOut), width=width, height=height)

# Run
if __name__ == "__main__":
    # Init arg parser
    parser = argparse.ArgumentParser(
        prog="Directory Size Sankey Diagram",
        description="Generates a Sankey Diagram depicting the size of a directory's contents")
    
    parser.add_argument(
        "root",
        help="The root directory to scan",
        nargs=1)
    parser.add_argument(
        "--ignoreFiles",
        action="store_true",
        help="Ignores files while generating diagram (only includes directories)")
    parser.add_argument(
        "--htmlOut",
        nargs=1,
        help="Output location of the HTML file")
    parser.add_argument(
        "--imgOut",
        nargs=1,
        help="Output location of the image file")
    parser.add_argument(
        "--width",
        nargs=1,
        help="Output width (default 3840)",
        type=int,
        default=[3840])
    parser.add_argument(
        "--height",
        nargs=1,
        help="Output height (default 2160)",
        type=int,
        default=[2160])
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Makes the output verbose")
    
    args = parser.parse_args()
    
    # Run
    generate(
        args.root[0],
        args.ignoreFiles,
        None if args.htmlOut is None else args.htmlOut[0],
        None if args.imgOut is None else args.imgOut[0],
        args.width[0],
        args.height[0]
    )
