# 🚀 Running Scripts

The easiest way to run the scripts in this repository is using **[uv]()**, a modern and incredibly fast Python tool manager.

### 1. Install `uv`

If you don't have it yet, run:

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

```

---

### 2. Run the Converter

You don't need to clone this repository or manage a virtual environment. You can run the script directly from GitHub using `uv run`.

`uv` will automatically handle the Python interpreter and any necessary dependencies in a temporary, isolated sandbox:

```bash
uv run https://raw.githubusercontent.com/pit38-assistant/community/main/convert_bunq.py input.csv output.csv

```
