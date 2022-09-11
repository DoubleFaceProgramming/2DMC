use pyo3::{prelude::*, py_run};

pub mod metaball;

fn register_submodule<'a>(python: &'a Python, parent: &'a PyModule, name: &'a str) -> PyResult<&'a PyModule> {
    // This function is scuffed but should work

    // parent.name()? == "rust.rust"
    // we want "rust"
    let parents_name = parent.name()?.split(".").collect::<Vec<&str>>()[1];
    // rust.rust<name>
    let fullname = &(parent.name()?.to_owned() + name);
    let child = PyModule::new(*python, fullname)?;
    py_run!(*python, child, format!("import sys; sys.modules['{}'] = child", parents_name.to_owned() + "." + name).as_str()); // https://github.com/PyO3/pyo3/issues/1517#issuecomment-808664021
    parent.add_submodule(child)?;

    Ok(child)
}

#[pymodule]
fn rust(python: Python, module: &PyModule) -> PyResult<()> {
    let metaball = register_submodule(&python, module, "metaball")?;
    metaball.add_function(wrap_pyfunction!(metaball::blob, metaball)?)?;

    Ok(())
}
