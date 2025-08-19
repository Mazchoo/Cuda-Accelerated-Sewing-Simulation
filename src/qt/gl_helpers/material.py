''' Represents data for current material '''
from typing import Union, Dict, Optional

from OpenGL.GL import (glBindTexture, glGenTextures, glGenerateMipmap, glActiveTexture,
                       glTexParameter, glTexImage2D, glDeleteTextures,
                       glUniform3fv, glUniform1f)
from OpenGL.GL import (GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
                       GL_REPEAT, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER,
                       GL_NEAREST, GL_LINEAR, GL_RGBA, GL_UNSIGNED_BYTE, GL_TEXTURE0)
from PIL import Image
import numpy as np

from src.qt.gl_helpers.typing import ColorRGB
from src.qt.gl_helpers.material_parameters import MaterialParameters
from src.qt.gl_helpers.uploadable_abc import OpenGLUploadable


class Material(OpenGLUploadable):
    ''' Represent a material to switch to it when necessary '''

    texture: int
    slot: int
    material_properties: MaterialParameters

    globals: Dict[str, str]
    ambient_weighting_glob_id: Optional[int]
    diffuse_weighting_glob_id: Optional[int]
    specular_weighting_glob_id: Optional[int]
    specular_exponent_glob_id: Optional[int]
    opacicty_glob_id: Optional[int]
    specular_tint_glob_id: Optional[int]

    def __init__(self, texture_source: Union[str, ColorRGB],
                 params: MaterialParameters, slot: int = GL_TEXTURE0, **globals):
        ''' Source can a file name or a single color '''
        self.material_properties = params
        self.globals = globals

        self.slot = slot
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

        image.transpose(Image.Transpose.ROTATE_90)
        image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        image_data = image.tobytes("raw", "RGBA")

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def set_all_globals(self):
        ''' Update all player properties on the GPU '''
        props = self.material_properties
        glUniform3fv(self.ambient_weighting_glob_id, 1, props.ambient_weighting)
        glUniform3fv(self.diffuse_weighting_glob_id, 1, props.diffuse_weighting)
        glUniform3fv(self.specular_weighting_glob_id, 1, props.specular_weighting)
        glUniform1f(self.specular_exponent_glob_id, props.specular_exponent)
        glUniform1f(self.opacicty_glob_id, props.opacity)
        glUniform1f(self.specular_tint_glob_id, props.specular_tint)

        glActiveTexture(self.slot)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):
        ''' Clean up memory when finished '''
        glDeleteTextures(1, (self.texture, ))
