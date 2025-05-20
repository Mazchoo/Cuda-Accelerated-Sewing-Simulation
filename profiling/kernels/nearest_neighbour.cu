__device__ __forceinline__ float square_dist(float3 a, float3 b) {
    float dx = (a.x - b.x);
    float dy = (a.y - b.y);
    float dz = (a.z - b.z);
    return dx * dx + dy * dy + dz * dz;
}

__global__ void find_min_distance_index(const float *points, const float *query, int *min_idx,
                                        float *min_distance, int num_points) {
    __shared__ float shared_distances[1024];
    __shared__ int shared_idx[1024];

    int global_idx = threadIdx.x + blockIdx.x * blockDim.x;
    int tid = threadIdx.x;
    if (global_idx < num_points) {
        shared_distances[threadIdx.x] = square_dist(
            make_float3(
                points[global_idx * 3],
                points[global_idx * 3 + 1],
                points[global_idx * 3 + 2]
            ), make_float3(
                query[0],
                query[1],
                query[2]
            ));
        shared_idx[threadIdx.x] = global_idx;
    }
    __syncthreads();

    // Perform reduction to find the minimum
    for (int stride = 1; stride < blockDim.x; stride *= 2) {
        if (tid % (2 * stride) == 0) {
            if (shared_distances[tid + stride] < shared_distances[tid]) {
                shared_distances[tid] = shared_distances[tid + stride];
                shared_idx[tid] = shared_idx[tid + stride];
            }
        }
        __syncthreads();
    }

    if (tid == 0) {
        min_distance[blockIdx.x] = shared_distances[0];
        min_idx[blockIdx.x] = shared_idx[0];
    }
}
