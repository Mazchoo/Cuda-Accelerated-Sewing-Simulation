
__device__ __inline__ float normL2(float3 v) {
    return sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
}

__global__ void update_position_with_friction(float* accelerations,
                                              float* velocities,
                                              float* vertices,
                                              const unsigned int nr_vertices,
                                              const float dampening) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= nr_vertices) return;

    float3 vertex = make_float3(
        vertices[idx * 3],
        vertices[idx * 3 + 1],
        vertices[idx * 3 + 2]
    );
    float3 velocity = make_float3(
        velocities[idx * 3],
        velocities[idx * 3 + 1],
        velocities[idx * 3 + 2]
    );
    float3 acceleration = make_float3(
        accelerations[idx * 3],
        accelerations[idx * 3 + 1],
        accelerations[idx * 3 + 2]
    );

    vertices[idx * 3] += velocity.x * TIME_DELTA;
    vertices[idx * 3 + 1] += velocity.y * TIME_DELTA;
    vertices[idx * 3 + 2] += velocity.z * TIME_DELTA;

    velocity.x += acceleration.x * TIME_DELTA;
    velocity.y += acceleration.y * TIME_DELTA;
    velocity.z += acceleration.z * TIME_DELTA;

    velocity.x *= dampening;
    velocity.y *= dampening;
    velocity.z *= dampening;

    float velocity_norm = normL2(velocity);
    if (velocity_norm > TERMINAL_VELOCITY) {
        velocity.x *= TERMINAL_VELOCITY / velocity_norm;
        velocity.y *= TERMINAL_VELOCITY / velocity_norm;
        velocity.z *= TERMINAL_VELOCITY / velocity_norm;
    }

    velocities[idx * 3] = velocity.x;
    velocities[idx * 3 + 1] = velocity.y;
    velocities[idx * 3 + 2] = velocity.z;

    accelerations[idx * 3] *= dampening;
    accelerations[idx * 3 + 1] *= dampening;
    accelerations[idx * 3 + 2] *= dampening;
}
