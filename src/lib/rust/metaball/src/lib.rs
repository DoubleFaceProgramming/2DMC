use pyo3::prelude::*;
use rand::Rng;

struct Coord {
    x: i32,
    y: i32,
}

impl Coord {
    fn dist(&self, other: &Coord) -> f32 {
        (((self.x - other.x).pow(2) + (self.y - other.y).pow(2)) as f32).sqrt()
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
fn blob() -> PyResult<Vec<Vec<&'static str>>> {
    let mut rng = rand::thread_rng();
    let mut balls = vec![];
    for i in 0..rng.gen_range(3..4 + 1) {
        balls.push(MetaBall::new(rng.gen_range(4..11 + 1) as i32, rng.gen_range(4..11 + 1) as i32, rng.gen_range(2..4 + 1) as f32))
    }

    let mut res = vec![];
    for y in 0..16 {
       res.push(vec![]);
       for x in 0..16 {
           let mut val = 0.0;
           for ball in &balls {
               let distance = ball.center.dist(&Coord {x, y});
               // There's probably a way to use casting to bool like you would in python but im too dum
               val += if distance == 0.0 {
                   10.0
               } else {
                   ball.radius / distance / 2.0
               };
           }
           res[y as usize].push(if val > 1.2 { "#" } else { "." });
        }
    }

    Ok(res)
}

#[pyfunction]
fn n_blobs(n: i32) -> PyResult<Vec<Vec<Vec<&'static str>>>> {
    let mut res = vec![];
    for i in 0..n {
        res.push(blob().unwrap());
    }
    Ok(res)
}

/// A Python module implemented in Rust.
#[pymodule]
fn metaball(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(blob, m)?)?;
    m.add_function(wrap_pyfunction!(n_blobs, m)?)?;
    Ok(())
}