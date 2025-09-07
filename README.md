# Cuda Accelerated Sewing Simulation

<img width="1478" height="916" alt="image" src="https://github.com/user-attachments/assets/e073a73e-ea4e-4b6d-a5fe-5f20aa3da7eb" />

## Description

Python simulation of clothing model from a basic 2D pattern using and a dynamic avatar from an .obj file. Models tensile forces, gravity, collisions and sewing constraints. Runs a PyQT5 GUI for display or can render the result of each frame.

Simulation runs at approximately: 200 frames per second on a NVIDIA GeForce RTX 4050 Laptop GPU.

## Work in Progress

- [ ] Fix unwanted energy added to the system when position based contraints interact with forces
- [ ] Add zooming and panning to QT widget display
- [ ] Added ability to view and edit material properties
- [ ] Add controls to tweak physics parameters live
