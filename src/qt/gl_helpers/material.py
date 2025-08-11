''' Represents data for current material '''
from typing import Union

from OpenGL.GL import (glBindTexture, glGenTextures, glGenerateMipmap, glActiveTexture,
                       glTexParameter, glTexImage2D, glDeleteTextures)
from OpenGL.GL import (GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
                       GL_REPEAT, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER,
                       GL_NEAREST, GL_LINEAR, GL_RGBA, GL_UNSIGNED_BYTE, GL_TEXTURE0)
from PIL import Image
import numpy as np

from src.qt.gl_helpers.typing import ColorRGB


class Material:
    ''' Represent a material to switch to it when necessary '''
    __slots__ = 'texture'

    texture: int

    def __init__(self, texture_source: Union[str, ColorRGB]):
        ''' Source can a file name or a single color '''
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        if isinstance(texture_source, str):
            image = Image.open(texture_source).convert("RGBA")
        else:
            texture_array = np.array([[texture_source]], dtype=np.float32)
            image = Image.fromarray(texture_array, mode="RGBA")

        image_width, image_height, _ = image.shape
        image.transpose(Image.Transpose.ROTATE_90)
        image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        image_data = image.tobytes("raw", "RGBA")

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self, slot=GL_TEXTURE0):
        ''' Switch to using this texture '''
        glActiveTexture(slot)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):
        ''' Clean up memory when finished '''
        glDeleteTextures(1, (self.texture, ))
