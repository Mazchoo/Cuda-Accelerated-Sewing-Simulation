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

__global__ void apply_stress(float *acceleration,
                             const float* const vertices,
                             const unsigned int* const stress_relations,
                             const unsigned int nr_stress_relations) {
    int pair_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (pair_idx >= nr_stress_relations) return;
    const float EPSILON = 1e-10f;

    unsigned int from_ind = stress_relations[pair_idx * 2];
    unsigned int to_ind = stress_relations[pair_idx * 2 + 1];

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
    float distance = normL2(vector);
    float stress_amount = distance / STRESS_RESTING_AMOUNT;
    if (stress_amount > 1 + STRESS_THRESHOLD) {
        float3 vector_norm = vector;
        scaleVector(vector_norm, 1 / stress_amount);
        vector = subtract(vector, vector_norm);
        scaleVector(vector, STRESS_WEIGHTING / STRESS_RESTING_AMOUNT);

        acceleration[from_ind * 3] += vector.x;
        acceleration[from_ind * 3 + 1] += vector.y;
        acceleration[from_ind * 3 + 2] += vector.z;
        acceleration[to_ind * 3] -= vector.x;
        acceleration[to_ind * 3 + 1] -= vector.y;
        acceleration[to_ind * 3 + 2] -= vector.z;
    } else if (stress_amount < 1 - STRESS_THRESHOLD) {
        if (stress_amount > EPSILON) {
            float3 vector_norm = vector;
            scaleVector(vector_norm, 1 / stress_amount);
            vector = subtract(vector, vector_norm);
        }
        scaleVector(vector, STRESS_WEIGHTING / STRESS_RESTING_AMOUNT);

        acceleration[from_ind * 3] += vector.x;
        acceleration[from_ind * 3 + 1] += vector.y;
        acceleration[from_ind * 3 + 2] += vector.z;
        acceleration[to_ind * 3] -= vector.x;
        acceleration[to_ind * 3 + 1] -= vector.y;
        acceleration[to_ind * 3 + 2] -= vector.z;
    }
}
