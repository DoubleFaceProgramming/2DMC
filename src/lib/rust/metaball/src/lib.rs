use pyo3::prelude::*;
use rand::prelude::*;
use rand_chacha::ChaCha8Rng;

struct Coord {
    x: i32,
    y: i32,
}

impl Coord {
    fn dist_sqr(&self, other: &Coord) -> f32 {
        ((self.x - other.x).pow(2) + (self.y - other.y).pow(2)) as f32
    }
}

struct MetaBall {
    center: Coord,
    radius: f32,
}

impl MetaBall {
    fn new(x: i32, y: i32, r: f32) -> Self {
        Self {
            center: Coord { x, y },
            radius: r,
        }
    }
}

#[pyfunction]
fn blob(seed: i64) -> PyResult<Vec<(i32, i32)>> {
    let mut rng = ChaCha8Rng::seed_from_u64(if seed < 0 { (-seed * 2 - 1) as u64 } else { (seed * 2) as u64 });

    let mut balls = vec![];
    for _ in 0..rng.gen_range(3..4 + 1) {
        balls.push(MetaBall::new(rng.gen_range(4..11 + 1) as i32, rng.gen_range(4..11 + 1) as i32, rng.gen_range(2..4 + 1) as f32))
    }

    let mut coordinates = vec![];
    for y in 0..16 {
       for x in 0..16 {
            let mut val = 0.0;
            for ball in &balls {
                let distance_squared = ball.center.dist_sqr(&Coord {x, y});
                val += if distance_squared == 0.0 {
                    10.0
                } else {
                    ball.radius * ball.radius / distance_squared / 1.6
                };
            }
            if val > 1.2 {
                coordinates.push((x, y))
            }
        }
    }

    Ok(coordinates)
}

#[pymodule]
fn metaball(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(blob, m)?)?;
    Ok(())
}