use pyo3::{prelude::*, py_run};

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b * 2).to_string())
}

#[pyfunction]
fn square_as_string(a: usize) -> PyResult<String> {
    Ok((a * a).to_string())
}

fn register_square(py: Python, parent_module: &PyModule) -> PyResult<()> {
    let module = PyModule::new(py, "square")?;

    module.add_function(wrap_pyfunction!(square_as_string, module)?)?;
    parent_module.add_submodule(module)?;

    Ok(())
}

fn register_submodule<A , R>(name: &str, python: Python, parent: &PyModule, funcs: Vec<&dyn Fn(A) -> R>) -> PyResult<()> {
    let name = &(parent.name()?.to_owned() + name);
    let child = PyModule::new(python, name)?;

    for func in &funcs {
        // child.add_function(wrap_pyfunction!(func, child)?)?;
    }

    py_run!(python, child, format!("import sys; sys.modules[{}] = child_module", name).as_str()); // https://github.com/PyO3/pyo3/issues/1517#issuecomment-808664021
    parent.add_submodule(child)?;

    Ok(())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust(py: Python, m: &PyModule) -> PyResult<()> {
    // register_square(py, m)?;
    m.add_function(wrap_pyfunction!(square_as_string, m)?)?;
    Ok(())
}

// #[pymodule]
// fn rust(py: Python<'_>, m: &PyModule) -> PyResult<()> {
//     register_child_module(py, m)?;
//     Ok(())
// }

// fn register_child_module(py: Python<'_>, parent_module: &PyModule) -> PyResult<()> {
//     let child_module = PyModule::new(py, "rust.child_module")?;
//     child_module.add_function(wrap_pyfunction!(func, child_module)?)?;
//     py_run!(py, child_module, "import sys; sys.modules['rust.child_module'] = child_module");
//     parent_module.add_submodule(child_module)?;
//     Ok(())
// }

// #[pyfunction]
// fn func() -> String {
//     "func".to_string()
// }
