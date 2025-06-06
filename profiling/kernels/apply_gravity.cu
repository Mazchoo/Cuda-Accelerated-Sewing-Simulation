__global__ void apply_gravity(float *acceleration, int num_acceleration) {
    int pt_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (pt_idx >= num_acceleration) return;

    acceleration[pt_idx * 3 + 1] = -GRAVITY;
}
