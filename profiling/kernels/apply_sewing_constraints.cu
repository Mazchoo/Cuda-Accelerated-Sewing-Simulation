
__device__ __inline__ float3 subtract(float3 a, float3 b) {
    return make_float3(a.x - b.x, a.y - b.y, a.z - b.z);
}

__device__ __inline__ float normL2(float3 v) {
    return sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
}

__device__ __inline__ void scaleVector(float3 &v, float s) {
    v.x *= s;
    v.y *= s;
    v.z *= s;
}

__global__ void apply_sewing_constraints(float* vertices,
                                         const unsigned int* const sewing_indices,
                                         const unsigned int nr_sewing) {
    int pair_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (pair_idx >= nr_sewing) return;
    const float EPSILON = 1e-2f;

    unsigned int from_ind = sewing_indices[pair_idx * 2];
    unsigned int to_ind = sewing_indices[pair_idx * 2 + 1];

    float3 from_vertex = make_float3(
        vertices[from_ind * 3],
        vertices[from_ind * 3 + 1],
        vertices[from_ind * 3 + 2]
    );
    float3 to_vertex = make_float3(
        vertices[to_ind * 3],
        vertices[to_ind * 3 + 1],
        vertices[to_ind * 3 + 2]
    );

    float3 vector = subtract(to_vertex, from_vertex);
    float vectorNorm = normL2(vector);
    if (vectorNorm < EPSILON) {
        return;
    }
    
    float adjustment = min(vectorNorm / 2, SEWING_MAX_ADJUSTMENT);

    scaleVector(vector, (adjustment / vectorNorm));
    vertices[from_ind * 3] += vector.x;
    vertices[from_ind * 3 + 1] += vector.y;
    vertices[from_ind * 3 + 2] += vector.z;
    vertices[to_ind * 3] -= vector.x;
    vertices[to_ind * 3 + 1] -= vector.y;
    vertices[to_ind * 3 + 2] -= vector.z;
}
