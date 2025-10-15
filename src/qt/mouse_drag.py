"""Handle drag and drop events"""


class MouseDrag:
    # Initialize drag tracking variables
    _drag_start_pos = None
    _is_dragging = False

    @staticmethod
    def mouse_press_handler(event):
        if event.button() == 1:  # Left mouse button
            MouseDrag._drag_start_pos = (event.x(), event.y())
            MouseDrag._is_dragging = True

    @staticmethod
    def mouse_release_handler(event):
        if MouseDrag._is_dragging and MouseDrag._drag_start_pos:
            end_pos = (event.x(), event.y())
            drag_vector = (
                end_pos[0] - MouseDrag._drag_start_pos[0],
                end_pos[1] - MouseDrag._drag_start_pos[1],
            )

            MouseDrag._is_dragging = False
            MouseDrag._drag_start_pos = None

            print(drag_vector)
