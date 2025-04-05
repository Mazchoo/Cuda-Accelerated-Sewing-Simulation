import webbrowser
import os

# Specify the path to your HTML file
html_file_path = os.path.join(os.path.dirname(__file__), 'handbook.html')  # Adjust this to your actual file name

# Check if the file exists
if os.path.isfile(html_file_path):
    # Open the HTML file in the default web browser
    webbrowser.open(f'file:///{html_file_path.replace(os.sep, "/")}')
else:
    print(f"File not found: {html_file_path}")
