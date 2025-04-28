
import numpy as np

from src.utils.file_io import read_json
from src.utils.read_mtl import parse_mtl, parse_vertex
from src.simulation.mesh import MeshData, get_annotated_locations_from_dict


def parse_texture_coord(line):
    ''' Parse value of the form texture coordinares, e.g. 0.491723 -0.123703 '''
    vertex = [float(x) for x in line.split(' ')]

    if len(vertex) != 2:
        raise ValueError(f'Texture Coord {line} is wrong length.')

    v_original = vertex[0]
    vertex[0] = -vertex[1]
    vertex[1] = v_original

    return vertex


def parse_face(line):
    '''
        parse face coordinates e.g. 4/4/4 5/5/5 6/6/6,
        expect all three vertex, texture and normal coordinates to be present
    '''
    face = [[int(x) for x in f.split('/')] for f in line.split(' ')]

    if len(face) not in [3, 4]:
        raise ValueError(f'Face {line} is not a triangle or quad.')

    output = []

    if len(face) == 3:
        output.append(face)
    elif len(face) == 4:
        output.append(face[:3])
        output.append(face[2:] + [face[0]])

    return output


def convert_parsed_data_to_numpy(faces, vertices, textures, normals):
    ''' Create an array of all vertices to draw in triplets for every face. '''
    texture_data = {
        path: {'count': 0, 'offset': 0} for path in faces.keys()
    }

    vertex_data = []
    index_data = []

    ind = 0
    seen_faces = []
    for path, face_list in faces.items():
        texture_data[path]['offset'] = len(index_data)

        for face in face_list:
            face_inds = []

            for vert_ind, tex_ind, normal_ind in face:
                vertex_tuple = (vert_ind, tex_ind, normal_ind)
                if vertex_tuple in seen_faces:
                    face_inds.append(seen_faces.index(vertex_tuple))
                else:
                    seen_faces.append(vertex_tuple)
                    vertex_data.append(vertices[vert_ind - 1] + textures[tex_ind - 1] + normals[normal_ind - 1])
                    face_inds.append(ind)
                    ind += 1

            index_data.append(face_inds)

        texture_data[path]['count'] = len(index_data) - texture_data[path]['offset']

    return np.array(vertex_data, dtype=np.float32), np.array(index_data, dtype=np.int32), texture_data


def parse_obj(file_path: str, annotation_path: str):
    ''' Parse every line of an .obj file into material dict and vertex numpy array '''
    mtl_dict = parse_mtl(file_path)
    annotations = read_json(annotation_path)

    faces = {}
    current_texture = ''

    vertices = []
    textures = []
    normals = []
    with open(file_path, 'r') as f:
        while line := f.readline():
            line = line.strip()
            flag = line[:line.find(' ')]
            line_content = line[len(flag) + 1:]

            if flag == 'usemtl':
                current_texture = mtl_dict[line_content]['texture']
                if current_texture not in faces:
                    faces[current_texture] = []
            elif flag == 'v':
                vertices.append(parse_vertex(line_content))
            elif flag == 'vt':
                textures.append(parse_texture_coord(line_content))
            elif flag == 'vn':
                normals.append(parse_vertex(line_content))
            elif flag == 'f':
                faces[current_texture].extend(parse_face(line_content))

    vertex_data, index_data, texture_data = convert_parsed_data_to_numpy(
        faces, vertices, textures, normals
    )

    mesh = MeshData(vertex_data, index_data, texture_data,
                    annotations=get_annotated_locations_from_dict(annotations))

    return mesh


if __name__ == '__main__':
    mesh = parse_obj('./assets/BodyMesh.obj', './assets/BodyAnnotations.json')
    print(len(mesh._vertex_data), "vertice parsed")
    x_min = mesh._vertex_data[:, 0].min()
    x_max = mesh._vertex_data[:, 0].max()
    y_min = mesh._vertex_data[:, 1].min()
    y_max = mesh._vertex_data[:, 1].max()
    z_min = mesh._vertex_data[:, 2].min()
    z_max = mesh._vertex_data[:, 2].max()
    print(f"Vertex range x {x_max-x_min:.3f}, y: {y_max-y_min:.3f}, z: {z_max-z_min:.3f}")
