__global__ void zero_out_normals(float* vertices, const int numVerts) {
    int vid = blockIdx.x * blockDim.x + threadIdx.x;
    if (vid >= numVerts) return;

    float* v = vertices + vid * 8;
    v[5] = v[6] = v[7] = 0.0f;
}

__global__ void sum_normals_over_triangles(
    float* vertices,
    const int* indices,
    const int nrTriangles
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= nrTriangles) return;

    // Fetch triangle indices
    int i0 = indices[tid * 3 + 0];
    int i1 = indices[tid * 3 + 1];
    int i2 = indices[tid * 3 + 2];

    // Positions
    float3 p0 = make_float3(vertices[i0 * 8], vertices[i0 * 8 + 1], vertices[i0 * 8 + 2]);
    float3 p1 = make_float3(vertices[i1 * 8], vertices[i1 * 8 + 1], vertices[i1 * 8 + 2]);
    float3 p2 = make_float3(vertices[i2 * 8], vertices[i2 * 8 + 1], vertices[i2 * 8 + 2]);

    // Face normal (cross product of edges)
    float3 e1 = make_float3(p1.x - p0.x, p1.y - p0.y, p1.z - p0.z);
    float3 e2 = make_float3(p2.x - p0.x, p2.y - p0.y, p2.z - p0.z);

    float3 fn;
    fn.x = e1.y * e2.z - e1.z * e2.y;
    fn.y = e1.z * e2.x - e1.x * e2.z;
    fn.z = e1.x * e2.y - e1.y * e2.x;

    // Atomically accumulate normals (to avoid race conditions)
    atomicAdd(&vertices[i0 * 8 + 5], fn.x);
    atomicAdd(&vertices[i0 * 8 + 6], fn.y);
    atomicAdd(&vertices[i0 * 8 + 7], fn.z);

    atomicAdd(&vertices[i1 * 8 + 5], fn.x);
    atomicAdd(&vertices[i1 * 8 + 6], fn.y);
    atomicAdd(&vertices[i1 * 8 + 7], fn.z);

    atomicAdd(&vertices[i2 * 8 + 5], fn.x);
    atomicAdd(&vertices[i2 * 8 + 6], fn.y);
    atomicAdd(&vertices[i2 * 8 + 7], fn.z);
}

// Kernel to normalize accumulated normals
__global__ void normalize_normals(float* vertices, const int numVerts) {
    int vid = blockIdx.x * blockDim.x + threadIdx.x;
    if (vid >= numVerts) return;

    float* v = vertices + vid * 8;
    float nx = v[5], ny = v[6], nz = v[7];
    float len = sqrtf(nx * nx + ny * ny + nz * nz);

    if (len > 1e-12f) {
        v[5] = nx / len;
        v[6] = ny / len;
        v[7] = nz / len;
    }
}
