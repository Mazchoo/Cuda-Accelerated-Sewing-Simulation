# Pyscript-Sewing-Simulation

## Basic Description

Models sewing using a .dxf clothing design and a dynamic avatar from an .obj file. Models tensile forces and sewing forces. Using Web-GPU hardware acceleration for display.

## List of Stuff ToDo

- [x] Import sewing and contours into a json
- [x] Extract 3D data from an .obj file and render it
- [x] Refactor sewing json to split "to" and "from" sewing
- [x] Create conversion function to mesh grid for clothing and render it on 3D plot
- [ ] Add pairs of points to body and pieces to get initial positions for alignment
      - e.g. (shoulder, wrist) on both body and piece => piece offsets to match shoulder and rotates to orient to wrist
- [ ] Create 3D plot that shows pieces and avatar as vertices in different colors that can update steps in a simulation
- [x] Extract all horizontal, vertical and diagonal grid pairs for forces modelling
- [ ] Model a falling vertical piece with stretching forces and collision occurs at y=0
- [ ] Model a falling piece with collision on the avatar
- [ ] Add initialisation where piece "wraps" around body
      - Take vertical line through center of the piece and match to closest points on the body
      - Going progressively outwards from vertical line on each side of piece on each side
      - Maintain a distance of a certain amount to the avatar by applying an offset
      - Apply offset to all remaining vertices on each side
- [ ] Model sewing forces with multiple pieces
- [ ] Bonus - automatically predict location of body parts on any humanoid mesh

## Some Pictures

2D sewing view

![Figure_1](https://github.com/user-attachments/assets/d0678c08-eb7b-4471-add4-7a9fa208e130)

Project avatar view in plotly (left), external OpenGL viewer (right)

<span>
<img src="https://github.com/user-attachments/assets/8ce24b74-0122-4266-8c19-ca209e1b0b4e" alt="Plotly Avatar" width="400">
<img src="https://github.com/user-attachments/assets/984ccd6d-aaaa-45c2-958f-76159043bf50" alt="Plotly Avatar" width="400">
</span>

