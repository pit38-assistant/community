### Running Scripts

The easiest way to run the scripts in this repository is using **[uv](https://docs.astral.sh/uv/)**, a modern and incredibly fast Python tool manager.
It will automatically handle the Python interpreter and any necessary dependencies:
```bash
uv run https://raw.githubusercontent.com/pit38-assistant/community/main/convert_bunq.py input.csv output.csv

```

### If `uv` is not installed (one-time setup):

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

```
