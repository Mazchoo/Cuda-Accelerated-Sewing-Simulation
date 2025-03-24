""" Show all pieces in 2D to inspect shape and turn-points """
import json

import matplotlib.pyplot as plt
import numpy as np


def show_each_piece(clothing_data: dict, offset: tuple):
    current_offset = np.array([0, 0], dtype=np.float64)
    for piece in clothing_data.values():
        contour = np.array(piece["contour"], dtype=np.float64)
        contour += current_offset
        xs, ys = contour[:, 0], contour[:, 1]
        plt.plot(xs, ys, c='r')

        turn_points = np.array(piece["turn_points"])
        turn_points += current_offset
        xs, ys = turn_points[:, 0], turn_points[:, 1]

        # Plot as crosses
        plt.scatter(xs, ys, marker='x', color='b')
        for i, (x, y) in enumerate(turn_points):
            plt.text(x, y, str(i), c='g')

        current_offset += offset

    plt.axis('equal')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    with open('./assets/sewing_shirt.json', 'r', encoding='utf-8') as f:
        clothing_data = json.load(f)
    show_each_piece(clothing_data, (100, 0))
