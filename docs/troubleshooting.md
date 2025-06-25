The error indicates that the `fastapi` module is not installed in your Python environment:

```
ModuleNotFoundError: No module named 'fastapi'
```

---

### ✅ Solution

Since you're using **Python 3.13**, ensure you're installing packages in the correct environment.

Please run:

```bash
python3.13 -m pip install fastapi uvicorn scikit-learn pandas joblib
```

If you are using a virtual environment (recommended), activate it first:

```bash
source /path/to/venv/bin/activate
```

Then run the installation command again:

```bash
pip install fastapi uvicorn scikit-learn pandas joblib
```

---

### 🧪 After Installation

Re-run your FastAPI server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Let me know if you encounter any further errors or would like assistance setting up a `requirements.txt` or systemd service for deployment.
