__global__ void zero_out_normals(float* normals, const int nr_normals) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= nr_normals) return;

    float* vn = normals + idx * 3;
    vn[0] = vn[1] = vn[2] = 0.0f;
}

__global__ void sum_normals_over_triangles(
    float* normals,
    const float* vertices,
    const int* indices,
    const int nr_triangles
) {
    int triangle_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (triangle_idx >= nr_triangles) return;

    // Fetch triangle indices
    int i0 = indices[triangle_idx * 3];
    int i1 = indices[triangle_idx * 3 + 1];
    int i2 = indices[triangle_idx * 3 + 2];

    // Positions
    float3 p0 = make_float3(vertices[i0 * 3], vertices[i0 * 3 + 1], vertices[i0 * 3 + 2]);
    float3 p1 = make_float3(vertices[i1 * 3], vertices[i1 * 3 + 1], vertices[i1 * 3 + 2]);
    float3 p2 = make_float3(vertices[i2 * 3], vertices[i2 * 3 + 1], vertices[i2 * 3 + 2]);

    // Face normal (cross product of edges)
    float3 e1 = make_float3(p1.x - p0.x, p1.y - p0.y, p1.z - p0.z);
    float3 e2 = make_float3(p2.x - p0.x, p2.y - p0.y, p2.z - p0.z);

    float3 fn;
    fn.x = e1.y * e2.z - e1.z * e2.y;
    fn.y = e1.z * e2.x - e1.x * e2.z;
    fn.z = e1.x * e2.y - e1.y * e2.x;

    // Atomically accumulate normals (to avoid race conditions)
    atomicAdd(&normals[i0 * 3], fn.x);
    atomicAdd(&normals[i0 * 3 + 1], fn.y);
    atomicAdd(&normals[i0 * 3 + 2], fn.z);

    atomicAdd(&normals[i1 * 3], fn.x);
    atomicAdd(&normals[i1 * 3 + 1], fn.y);
    atomicAdd(&normals[i1 * 3 + 2], fn.z);

    atomicAdd(&normals[i2 * 3], fn.x);
    atomicAdd(&normals[i2 * 3 + 1], fn.y);
    atomicAdd(&normals[i2 * 3 + 2], fn.z);
}

// Kernel to normalize accumulated normals
__global__ void normalize_normals(float* normals, const int nr_normals) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= nr_normals) return;

    float* vn = normals + idx * 3;
    float nx = vn[0], ny = vn[1], nz = vn[2];
    float len = sqrtf(nx * nx + ny * ny + nz * nz);

    if (len > 1e-12f) {
        vn[0] = nx / len;
        vn[1] = ny / len;
        vn[2] = nz / len;
    }
}
