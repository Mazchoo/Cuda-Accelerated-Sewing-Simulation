# Cuda Accelerated Sewing Simulation

<img width="1488" height="925" alt="Screenshot 2025-09-07 233723" src="https://github.com/user-attachments/assets/27363af6-852c-4a8d-80d6-91b0c5ed5e7f" />

## Description

Python simulation of clothing model from a basic 2D pattern using and a dynamic avatar from an .obj file. Models tensile forces, gravity, collisions and sewing constraints. Runs a PyQT5 GUI for display or can render the result of each frame.

Simulation runs at approximately: 200 frames per second on a NVIDIA GeForce RTX 4050 Laptop GPU.

## Work in Progress

- [ ] Fix unwanted movement added to the system when position based contraints interact with forces
    - ~~Remove velocity and acceleration in plane collision and/or gravity~~
    - ~~Try applying Coulomb friction on collision~~
    - Try RMS prop and momentum for dynamic friction change, apply friction to acceleration
- [ ] Add zooming and panning to QT widget display
- [ ] Added ability to view and edit material properties
- [ ] Add controls to tweak physics parameters live
- [ ] Optimize the set-up of clothing and simulation/make a loading animation
- [ ] Add a shader that displays normal as a color and kernels that display properties such as stress, energy, shear and bend
- [ ] Add a pause update button and forward one frame button

## Installation

1. This project requires a machine with an nvidia GPU to run (tested with Cuda 12.8)
2. Install a Visual Studio (Desktop development with C++) to get cl. You may need to add cl to path. Running cl in the command line should give:

```
usage: cl [ option... ] filename... [ /link linkoption... ]
Microsoft (R) C/C++ Optimizing Compiler Version 19.43.34810 for x64
Copyright (C) Microsoft Corporation.  All rights reserved.
```

3. Install the Cuda framework. The version of cuda must be the one that corresponds with the compiler version.
4. Download and install pycuda (clone the repo and run pip install . in the path). The following flag must be turned on in setup.py

```
Switch("CUDA_ENABLE_GL", True, "Enable CUDA GL interoperability")
```

5. Install the other requirments in requirements.txt in a Python enviornment.
6. You will need to allow python to use GPU acceleration for rendering.

```NVIDIA Control Panel → Manage 3D settings → Program Settings → Add python.exe → set "Preferred graphics processor" = High-performance NVIDIA processor```
