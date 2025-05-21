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

__device__ __inline__ float3 get_v0(float *triangles, int idx) {
    return make_float3(
        triangles[idx * 9],
        triangles[idx * 9 + 1],
        triangles[idx * 9 + 2]
    );
}

__device__ __inline__ float3 get_edge1(float *triangles, int idx) {
    return make_float3(
        triangles[idx * 9 + 3],
        triangles[idx * 9 + 4],
        triangles[idx * 9 + 5]
    );
}

__device__ __inline__ float3 get_edge2(float *triangles, int idx) {
    return make_float3(
        triangles[idx * 9 + 6],
        triangles[idx * 9 + 7],
        triangles[idx * 9 + 8]
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

__device__ float3 closest_point_on_triangle(float3& query,
                                            float3 v0, float3 edge1, float3 edge2) {
    const float EPSILON = 1e-10f;
    float3 q_to_v0 = subtract(query, v0);

    float d1 = dot_product(edge1, q_to_v0);
    float d2 = dot_product(edge2, q_to_v0);
    float d3 = dot_product(edge1, edge1);
    float d4 = dot_product(edge1, edge2);
    float d5 = dot_product(edge2, edge2);

    float denom = d3 * d5 - d4 * d4 + EPSILON;
    float v_clamped = clamp((d5 * d1 - d4 * d2) / denom);
    float w_clamped = clamp((d3 * d2 - d4 * d1) / denom);
    float u_clamped = clamp(1 - v_clamped - w_clamped);

    float sum_clamped = u_clamped + v_clamped + w_clamped;
    float3 u_vec = scalar_multiply(v0, u_clamped / sum_clamped);
    float3 v_vec = scalar_multiply(add(v0, edge1), v_clamped / sum_clamped);
    float3 w_vec = scalar_multiply(add(v0, edge2), w_clamped / sum_clamped);

    return add(w_vec, add(u_vec, v_vec));
}

__global__ void adjust_point_in_mesh(float *triangles, int num_triangles,
                                     float *points, int num_points,
                                     float *normals, float *centers) {
    int pt_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (pt_idx >= num_points) return;

    float3 query = make_float3(
        points[pt_idx * 3],
        points[pt_idx * 3 + 1],
        points[pt_idx * 3 + 2]
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
            if (closest_distance_sq < dist_to_center - radius) {
                continue;
            }

            // Find closest point on triangle
            float3 closest_point = closest_point_on_triangle(
                query, get_v0(triangles, tri_idx),
                get_edge1(triangles, tri_idx), get_edge2(triangles, tri_idx)
            );
            float distance = square_dist(closest_point, query);

            if (distance < closest_distance_sq) {
                closest_index = tri_idx;
                closest_distance_sq = distance;
            }
        }

        float3 normal = make_float3(
            normals[closest_index * 3],
            normals[closest_index * 3 + 1],
            normals[closest_index * 3 + 2]
        );
        float3 adjustment = scalar_multiply(normal, sqrtf(closest_distance_sq));

        points[pt_idx * 3] += adjustment.x;
        points[pt_idx * 3 + 1] += adjustment.y;
        points[pt_idx * 3 + 2] += adjustment.z;
    }
}
