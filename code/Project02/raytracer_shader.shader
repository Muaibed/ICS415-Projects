#define MAX_SPHERES 50
float hash12(vec2 p)
{
	vec3 p3  = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}
vec2 hash22(vec2 p)
{
    vec3 p3 = fract(vec3(p.xyx) * vec3(.1031, .1030, .0973));
    p3 += dot(p3, p3.yzx+33.33);
    return fract((p3.xx+p3.yz)*p3.zy);

}
vec3 hash32(vec2 p)
{
    vec3 p3 = fract(vec3(p.xyx) * vec3(.1031, .1030, .0973));
    p3 += dot(p3, p3.yxz+33.33);
    return fract((p3.xxy+p3.yzz)*p3.zyx);
}

vec3 random_in_unit_sphere(vec2 p) {
    float test = 0.;
    while (test < 9999.) {
        vec3 pt = hash32(p * 10000. + test) * 2. - 1.;
        float len = length(pt);
        if (len * len >= 1.) {
            test += 1.;
            continue;
        }
        return pt;
    }
}

vec3 random_unit_vector(vec2 p) {
    return normalize(random_in_unit_sphere(p));
}

vec3 random_in_unit_disk(vec2 p) {
    float test = 0.;
    while (test < 9999.) {
        vec3 pt = vec3(hash22(p * 10000. + test) * 2. - 1., 0);
        float len = length(pt);
        if (len * len >= 1.) {
            test += 1.;
            continue;
        }
        return pt;
    }
}


const int material_lambertian = 0;
const int material_metal = 1;
const int material_dielectric = 2;

struct ray {
    vec3 origin;
    vec3 dir;
};

struct material {
    int type;
    vec3 albedo;
    float metal_fuzz;
    float dielectric_index_of_refraction;
};

struct hit_record {
    vec3 p;
    vec3 normal;
    float t;
    material material;
};

struct sphere {
    vec3 center;
    float radius;
    material material;
};


vec3 randomVec3(float seed) {
    return vec3(fract(sin(seed * 12.9898) * 43758.5453),
                fract(sin(seed * 78.233) * 43758.5453),
                fract(sin(seed * 45.164) * 43758.5453));
}

sphere[MAX_SPHERES] spheres;
void generateRandomSpheres() {
    // ground
    spheres[1] = sphere(vec3( 0.0, -1000., -1.0), 1000., material(material_lambertian, vec3(0.5), 0., 0.));

    spheres[2] = sphere(vec3(0.0,    1.0, 2.),   1.0, material(material_dielectric, vec3(0), 0., 1.5));
    spheres[3] = sphere(vec3( -4.0,    1.0, 4.),   1.0, material(material_metal, vec3(0.7, 0.6, 0.5), 0., 0.));
    spheres[4] = sphere(vec3( 4.0,    1.0, 0.),   1.0, material(material_lambertian, vec3(0.7, 0.3, 0.6), 0., 0.));

    for (int i = 5; i < MAX_SPHERES; i++) {
        float seed = float(i) * 1.244;
        vec3 position = vec3(
            mix(-8.0, 8.0, randomVec3(seed).x),  
            0.2,                                   
            mix(-8.0, 8.0, randomVec3(seed).z)   
        );        
        float radius = 0.2;
        vec3 color = randomVec3(seed * 2.0);
        int materialType = int(mod(seed * 10.0, 3.0));
        float fuzz = materialType == 2 ? mix(0.0, 0.5, randomVec3(seed).y) : 0.0;
        float refraction = materialType == 1 ? 1.5 : 0.0;
        
        spheres[i] = sphere(position, radius, material(materialType, color, fuzz, refraction));
    }
}


bool hit_sphere(sphere sph, ray r, float t_min, float t_max, out hit_record rec) {    
    vec3 oc = r.origin - sph.center;
    float a = dot(r.dir, r.dir);
    float half_b = dot(oc, r.dir);
    float c = dot(oc, oc) - sph.radius * sph.radius;
    float discriminant = half_b * half_b - a * c;
    if (discriminant < 0.) {
        return false;
    }
    
    float sqrtd = sqrt(discriminant);
    
    // Find the nearest root that lies in the acceptable range
    float root = (-half_b - sqrtd) / a; // the t. from -b - sqrt(dis) / 2a
    if (root < t_min || t_max < root) {
        root = (-half_b + sqrtd) / a;
        if (root < t_min || t_max < root) {
            return false;
        }
    }
    
    vec3 p = r.origin + r.dir * root;
    rec = hit_record(p, (p - sph.center) / sph.radius, root, sph.material);
    
    return true;
}

bool hit(ray r, float t_min, float t_max, out hit_record rec) {
    bool hit_anything = false;
    float closest_so_far = t_max;
    
    hit_record rec_;
    for (int i = 0; i < spheres.length(); i++) {
        if (hit_sphere(spheres[i], r, t_min, closest_so_far, rec_)) {
            hit_anything = true;
            closest_so_far = rec_.t;
            rec = rec_;
        }
    }
    
    return hit_anything;
}

bool near_zero(vec3 p) {
    float s = 1e-8;
    return p.x < s && p.y < s && p.z < s;
}

float reflectance(float cosine, float ref_idx) {
    // Use Schlick's approximation for reflectance
    float r0 = (1. - ref_idx) / (1. + ref_idx);
    r0 = r0 * r0;
    return r0 + (1. - r0) * pow((1. - cosine), 5.);
}

bool scatter(hit_record rec, ray r, vec2 seed, out vec3 attenuation, out ray scattered) {
    material m = rec.material;
    
    if (m.type == material_lambertian) {
        vec3 scatter_direction = rec.normal + random_unit_vector(seed);
    
        // catch degenerate scatter direction
        if (near_zero(scatter_direction)) {
            scatter_direction = rec.normal;
        }

        scattered = ray(rec.p, scatter_direction);
        attenuation = m.albedo;
        return true;
    } else if (m.type == material_metal) {
        vec3 reflected = reflect(normalize(r.dir), rec.normal);
        scattered = ray(rec.p, reflected + m.metal_fuzz * random_in_unit_sphere(seed));
        attenuation = m.albedo;
        return dot(scattered.dir, rec.normal) > 0.;
    } else if (m.type == material_dielectric) {
        attenuation = vec3(1);
        
        bool front_face = dot(r.dir, rec.normal) < 0.;
        vec3 adjusted_normal = front_face ? rec.normal : -rec.normal;
        float ref = m.dielectric_index_of_refraction;
        float refraction_ratio = front_face ? 1.0/ref : ref;
        
        vec3 unit_direction = normalize(r.dir);
        float cos_theta = min(dot(-unit_direction, adjusted_normal), 1.0);
        float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
        
        bool cannot_refract = refraction_ratio * sin_theta > 1.0;
        vec3 direction;

        if (cannot_refract || reflectance(cos_theta, refraction_ratio) > hash12(seed)) {
            direction = reflect(unit_direction, adjusted_normal);
        } else {
            direction = refract(unit_direction, adjusted_normal, refraction_ratio);
        }
        
        scattered = ray(rec.p, direction);
        return true;
    }
}

vec3 ray_color(in ray r, vec2 seed, int max_depth) {
    vec3 color = vec3(1);
    
    int depth = max_depth;
    hit_record rec;
    while (depth > 0) {
        if (hit(r, 0.001, 99999., rec)) {
            ray scattered;
            vec3 attenuation;
            if (scatter(rec, r, seed + float(depth), attenuation, scattered)) {
                r = scattered;
                color = attenuation * color;
            }
        } else {
            // hit bg, aka nothing
            vec3 unit_direction = normalize(r.dir);
            float t = 0.5 * (unit_direction.y + 1.0);
            color *= mix(vec3(1.), vec3(0.5, 0.7, 1.0), t);

            break;
        }
        
        depth--;
    }
    
    if (depth == 0) {
        return vec3(0);
    }
    return color;    
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    generateRandomSpheres();
    // image
    float samples_per_pixel = 10.;
    int max_depth = 6; // number of ray bounces
    
    // camera
    vec3 lookfrom = vec3(-11, 2.0, 5.0);
    vec3 lookat = vec3(0, 0, 0);
    vec3 vup = vec3(0, 1, 0);
    float vfov = 30.0;
    float aspect_ratio = iResolution.x / iResolution.y;
    float aperture = 0.1;
    float focus_dist = 10.0;
    
    float theta = radians(vfov);
    float h = tan(theta / 2.);
    float viewport_height = 2.0 * h;
    float viewport_width = aspect_ratio * viewport_height;
    
    vec3 w = normalize(lookfrom - lookat);
    vec3 u = normalize(cross(vup, w));
    vec3 v = cross(w, u);
    
    vec3 origin = lookfrom;
    vec3 horizontal = focus_dist * viewport_width * u;
    vec3 vertical = focus_dist * viewport_height * v;
    vec3 lower_left_corner = origin - horizontal / 2. - vertical / 2. - focus_dist * w;
    
    float lens_radius = aperture / 2.;
    
    vec3 color = vec3(0);
    for (float s = 0.; s < samples_per_pixel; s++) {
        vec2 rand = hash22(fragCoord * 10000. + s);
               
        vec2 normalizedCoord = (fragCoord + rand) / (iResolution.xy - 1.);
        vec3 rd = lens_radius * random_in_unit_disk(normalizedCoord);
        vec3 offset = u * rd.x + v * rd.y;
        ray r = ray(
            origin + offset, 
            lower_left_corner + normalizedCoord.x * horizontal + normalizedCoord.y * vertical - origin - offset
        );
        color += ray_color(r, normalizedCoord, max_depth);
    }
    
    fragColor = vec4(sqrt(color / samples_per_pixel), 1.0);
}