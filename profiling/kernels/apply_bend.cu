
__device__ __inline__ float3 subtract(float3 a, float3 b) {
    return make_float3(a.x - b.x, a.y - b.y, a.z - b.z);
}

__device__ __inline__ float normL2(float3 v) {
    return sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
}

__device__ __inline__ float squareNorm(float3 v) {
    return v.x * v.x + v.y * v.y + v.z * v.z;
}

__device__ __inline__ float dotProduct(float3 v1, float3 v2) {
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
}

__device__ __inline__ void scaleVector(float3 &v, float s) {
    v.x *= s;
    v.y *= s;
    v.z *= s;
}

__device__ __inline__ float3 crossProduct(float3 v1, float3 v2) {
    return make_float3(v1.y * v2.z - v2.y * v1.z, v1.z * v2.x - v2.z * v1.x, v1.x * v2.y - v2.x * v1.y);
}

__global__ void apply_bend(float *acceleration, float *vertices,
                           unsigned int* bend_relations, int nr_bend_relations) {
    int pair_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (pair_idx >= nr_bend_relations) return;
    const float EPSILON = 1e-10f;

    unsigned int start_ind = bend_relations[pair_idx * 3];
    unsigned int middle_ind = bend_relations[pair_idx * 3 + 1];
    unsigned int end_ind = bend_relations[pair_idx * 3 + 2];

    float3 start_vertex = make_float3(
        vertices[start_ind * 3],
        vertices[start_ind * 3 + 1],
        vertices[start_ind * 3 + 2]
    );
    float3 middle_vertex = make_float3(
        vertices[middle_ind * 3],
        vertices[middle_ind * 3 + 1],
        vertices[middle_ind * 3 + 2]
    );
    float3 end_vertex = make_float3(
        vertices[end_ind * 3],
        vertices[end_ind * 3 + 1],
        vertices[end_ind * 3 + 2]
    );

    float3 vector = subtract(end_vertex, start_vertex);
    float distance = squareNorm(vector);
    if (distance < EPSILON) {
        return;
    }
    
    float3 middle_to_start = subtract(middle_vertex, start_vertex);
    float3 middle_cross = crossProduct(middle_to_start, vector);
    float middle_cross_distance = normL2(middle_cross);
    float bend_stress = middle_cross_distance / distance;
    if (bend_stress < BEND_THRESHOLD) {
        return;
    }

    float middle_projection = dotProduct(middle_to_start, vector) / distance;
    scaleVector(vector, middle_projection);
    // Vector is now closest point on line
    float3 middle_to_line = subtract(vector, middle_to_start);
    scaleVector(middle_to_line, BEND_WEIGHTING);

    acceleration[middle_ind * 3] += middle_to_line.x;
    acceleration[middle_ind * 3 + 1] += middle_to_line.y;
    acceleration[middle_ind * 3 + 2] += middle_to_line.z;
}
