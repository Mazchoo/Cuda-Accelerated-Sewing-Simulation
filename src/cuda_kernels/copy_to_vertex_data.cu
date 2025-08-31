__global__ void copy_to_vertex_data(float *open_gl_data,
                                    const float *vertices,
                                    const float *normals,
                                    const unsigned int nr_vertices)
{
    int idx = threadIdx.x + blockIdx.x * blockDim.x;
    if (idx >= nr_vertices) return;

    // Copy position
    open_gl_data[idx * 8] = vertices[idx * 3];
    open_gl_data[idx * 8 + 1] = vertices[idx * 3 + 1];
    open_gl_data[idx * 8 + 2] = vertices[idx * 3 + 2];

    // Copy normal
    open_gl_data[idx * 8 + 5] = normals[idx * 3];
    open_gl_data[idx * 8 + 6] = normals[idx * 3 + 1];
    open_gl_data[idx * 8 + 7] = normals[idx * 3 + 2];
}