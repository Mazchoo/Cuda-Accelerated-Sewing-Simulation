
__device__ __inline__ float dot_product(float3 a, float3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

__device__ __inline__ float3 projection(const float3& a, const float3& b) {
    // Get remove projection updated assumes b has norm 1
    float dot_ab = dot_product(a, b);
    return make_float3(
        dot_ab * b.x,
        dot_ab * b.y,
        dot_ab * b.z
    );
}

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

// ToDo - Some other check is needed to ensure that vertices are not sewn twice
__global__ void apply_sewing_constraints(float* vertices,
                                         float* velocities,
                                         float* accelerations,
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

    float3 vectorNormalised = make_float3(vector.x, vector.y, vector.z);
    scaleVector(vectorNormalised, (1.0f / vectorNorm));

    float adjustment = min(vectorNorm / 2, SEWING_MAX_ADJUSTMENT);

    scaleVector(vector, (adjustment / vectorNorm));

    vertices[from_ind * 3] += vector.x;
    vertices[from_ind * 3 + 1] += vector.y;
    vertices[from_ind * 3 + 2] += vector.z;

    vertices[to_ind * 3] -= vector.x;
    vertices[to_ind * 3 + 1] -= vector.y;
    vertices[to_ind * 3 + 2] -= vector.z;

    from_vertex = make_float3(
        velocities[from_ind * 3],
        velocities[from_ind * 3 + 1],
        velocities[from_ind * 3 + 2]
    );

    vector = projection(from_vertex, vectorNormalised);
    velocities[from_ind * 3] -= vector.x;
    velocities[from_ind * 3 + 1] -= vector.y;
    velocities[from_ind * 3 + 2] -= vector.z;

    from_vertex = make_float3(
        accelerations[from_ind * 3],
        accelerations[from_ind * 3 + 1],
        accelerations[from_ind * 3 + 2]
    );

    vector = projection(from_vertex, vectorNormalised);
    accelerations[from_ind * 3] -= vector.x;
    accelerations[from_ind * 3 + 1] -= vector.y;
    accelerations[from_ind * 3 + 2] -= vector.z;

    to_vertex = make_float3(
        velocities[to_ind * 3],
        velocities[to_ind * 3 + 1],
        velocities[to_ind * 3 + 2]
    );

    vector = projection(to_vertex, vectorNormalised);
    velocities[to_ind * 3] -= vector.x;
    velocities[to_ind * 3 + 1] -= vector.y;
    velocities[to_ind * 3 + 2] -= vector.z;

    to_vertex = make_float3(
        accelerations[to_ind * 3],
        accelerations[to_ind * 3 + 1],
        accelerations[to_ind * 3 + 2]
    );

    vector = projection(to_vertex, vectorNormalised);
    accelerations[to_ind * 3] -= vector.x;
    accelerations[to_ind * 3 + 1] -= vector.y;
    accelerations[to_ind * 3 + 2] -= vector.z;
}
