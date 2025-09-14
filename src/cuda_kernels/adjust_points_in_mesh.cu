
__device__ __inline__ float3 cross_product(float3 a, float3 b) {
    return make_float3(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    );
}

__device__ __inline__ float dot_product(float3 a, float3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

__device__ __inline__ float3 subtract(float3 a, float3 b) {
    return make_float3(a.x - b.x, a.y - b.y, a.z - b.z);
}

__device__ __inline__ float3 add(float3 a, float3 b) {
    return make_float3(a.x + b.x, a.y + b.y, a.z + b.z);
}


__device__ __inline__ float square_dist(float3 a, float3 b) {
    return (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y) + (a.z - b.z) * (a.z - b.z);
}

__device__ __inline__ float clamp(float value) {
    return max(0.0f, min(value, 1.0f));
}

__device__ __inline__ float3 scalar_multiply(float3 p, float scalar) {
    return make_float3(p.x * scalar, p.y * scalar, p.z * scalar);
}

__device__ __inline__ float3 get_v0(const float* const triangles, int idx) {
    return make_float3(
        triangles[idx * 9],
        triangles[idx * 9 + 1],
        triangles[idx * 9 + 2]
    );
}

__device__ __inline__ float3 get_edge1(const float* const triangles, int idx) {
    return make_float3(
        triangles[idx * 9 + 3],
        triangles[idx * 9 + 4],
        triangles[idx * 9 + 5]
    );
}

__device__ __inline__ float3 get_edge2(const float* const triangles, int idx) {
    return make_float3(
        triangles[idx * 9 + 6],
        triangles[idx * 9 + 7],
        triangles[idx * 9 + 8]
    );
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

__device__ int ray_intersects_triangle(float3& query, const float3& dir,
                                       float3 v0, float3 edge1, float3 edge2) {
    const float EPSILON = 1e-7f;
    float3 b;
    float v;

    float3 a = cross_product(dir, edge2);
    float det = dot_product(edge1, a);
    if (fabsf(det) < EPSILON)
        return 0;

    float3 c = subtract(query, v0);
    float u = dot_product(a, c);
    if (det > EPSILON) {
        if (u < 0 || u > det)
            return 0;

        b = cross_product(c, edge1);
        v = dot_product(b, dir);
        if (v < 0 || u + v > det)
            return 0;
    } else {
        if (u > 0 || u < det)
            return 0;

        b = cross_product(c, edge1);
        v = dot_product(b, dir);
        if (v > 0 || u + v < det)
            return 0;
    }

    float inv_det = 1.0f / det;
    float t = inv_det * dot_product(edge2, b);

    if (t < EPSILON || t > 1 - EPSILON)
        return 0;

    return 1;
}


__device__ float3 closest_point_on_triangle(const float3 p,
                                            const float3 a,
                                            const float3 ab,
                                            const float3 ac) {
    float3 ap = subtract(p, a);
    float d1 = dot_product(ab, ap);
    float d2 = dot_product(ac, ap);

    // Check if P in vertex region outside A
    if (d1 <= 0.0f && d2 <= 0.0f)
        return a;

    float3 b = add(a, ab);
    float3 bp = subtract(p, b);
    float d3 = dot_product(ab, bp);
    float d4 = dot_product(ac, bp);

    // Check if P in vertex region outside B
    if (d3 >= 0.0f && d4 <= d3)
        return b;

    float vc = d1 * d4 - d3 * d2;
    if (vc <= 0.0f && d1 >= 0.0f && d3 <= 0.0f) {
        float v = d1 / (d1 - d3);
        return add(a, scalar_multiply(ab, v));  // Edge AB
    }

    float3 c = add(a, ac);
    float3 cp = subtract(p, c);
    float d5 = dot_product(ab, cp);
    float d6 = dot_product(ac, cp);

    // Check if P in vertex region outside C
    if (d6 >= 0.0f && d5 <= d6)
        return c;

    float vb = d5 * d2 - d1 * d6;
    if (vb <= 0.0f && d2 >= 0.0f && d6 <= 0.0f) {
        float w = d2 / (d2 - d6);
        return add(a, scalar_multiply(ac, w));  // Edge AC
    }

    float va = d3 * d6 - d5 * d4;
    if (va <= 0.0f && (d4 - d3) >= 0.0f && (d5 - d6) >= 0.0f) {
        float w = (d4 - d3) / ((d4 - d3) + (d5 - d6));
        return add(b, scalar_multiply(subtract(c, b), w));  // Edge BC
    }

    // Inside face region. Compute barycentric coordinates (u,v,w)
    float denom = 1.0f / (va + vb + vc);
    float v = vb * denom;
    float w = vc * denom;
    return add(a, add(scalar_multiply(ab, v), scalar_multiply(ac, w)));
}

__global__ void adjust_point_in_mesh(const float* const triangles,
                                     const unsigned int num_triangles,
                                     float* vertices,
                                     float* velocities,
                                     float* accelerations,
                                     const unsigned int num_points,
                                     const float* const normals,
                                     const float* const centers) {
    int pt_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (pt_idx >= num_points) return;
    const float EPSILON = 1e-7f;

    float3 query = make_float3(
        vertices[pt_idx * 3],
        vertices[pt_idx * 3 + 1],
        vertices[pt_idx * 3 + 2]
    );
    const float3 ray_dir = make_float3(1.0f, 1.0f, 1.0f);

    int hit_count = 0;
    for (int tri_idx = 0; tri_idx < num_triangles; ++tri_idx) {
        hit_count += ray_intersects_triangle(
            query, ray_dir, get_v0(triangles, tri_idx),
            get_edge1(triangles, tri_idx), get_edge2(triangles, tri_idx)
        );
    }

    if (hit_count % 2 == 1) {
        float closest_distance_sq = 1e20;
        float closest_distance = 1e20;
        int closest_index = 0;

        for (int tri_idx = 0; tri_idx < num_triangles; ++tri_idx) {
            // Eliminate possibilities with triangle inequality
            float dist_to_center = sqrtf(square_dist(
                make_float3(
                    centers[tri_idx * 4],
                    centers[tri_idx * 4 + 1],
                    centers[tri_idx * 4 + 2]
                ), query));
            float radius = centers[tri_idx * 4 + 3];
            if (closest_distance < dist_to_center - radius) {
                continue;
            }

            // Find closest point on triangle
            float3 closest_point = closest_point_on_triangle(
                query, get_v0(triangles, tri_idx),
                get_edge1(triangles, tri_idx), get_edge2(triangles, tri_idx)
            );
            float distance = square_dist(closest_point, query);

            if (distance < EPSILON) {
                return;
            }
            if (distance < closest_distance_sq) {
                closest_index = tri_idx;
                closest_distance_sq = distance;
                closest_distance = sqrtf(closest_distance_sq);
            }
        }

        float3 normal = make_float3(
            normals[closest_index * 3],
            normals[closest_index * 3 + 1],
            normals[closest_index * 3 + 2]
        );
        float3 adjustment = scalar_multiply(normal, closest_distance);

        vertices[pt_idx * 3] += adjustment.x;
        vertices[pt_idx * 3 + 1] = max(query.y + adjustment.y, 0.0f);
        vertices[pt_idx * 3 + 2] += adjustment.z;

        // Velocity removed along normal
        float3 velocity = make_float3(
            velocities[pt_idx * 3],
            velocities[pt_idx * 3 + 1],
            velocities[pt_idx * 3 + 2]
        );
        adjustment = projection(velocity, normal);

        velocities[pt_idx * 3] -= adjustment.x;
        velocities[pt_idx * 3 + 1] -= adjustment.y;
        velocities[pt_idx * 3 + 2] -= adjustment.z;

        // Force removed along normal
        float3 accerlation = make_float3(
            accelerations[pt_idx * 3],
            accelerations[pt_idx * 3 + 1],
            accelerations[pt_idx * 3 + 2]
        );
        adjustment = projection(accerlation, normal);

        accelerations[pt_idx * 3] -= adjustment.x;
        accelerations[pt_idx * 3 + 1] -= adjustment.y;
        accelerations[pt_idx * 3 + 2] -= adjustment.z;
    }
}
