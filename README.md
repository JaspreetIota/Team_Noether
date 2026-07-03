# Corporate Tools Platform

An evolving web and mobile platform for practical corporate automation tools.
The product supports free utilities, paid advanced services, and custom tools
that can be private to one customer or published in a revenue-sharing
marketplace.

## Current MVP

- `corporate_tools_phase1/` contains standalone Python services for document,
  spreadsheet, HR, finance, compliance, and workflow automation.
- `toolkit_browser_demo/` contains a browser-based interactive product demo for
  testing the tool catalogue and representative workflows.

## Run the Python tools

```powershell
cd corporate_tools_phase1
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

See the toolkit README for individual command examples.

## Run the browser demo

```powershell
python -m http.server 8787 --directory toolkit_browser_demo
```

Then open `http://127.0.0.1:8787/`.

## Development workflow

Each enhancement or new service should be committed separately with a concise,
descriptive commit message. Generated customer files, secrets, and local runtime
artifacts must not be committed.

