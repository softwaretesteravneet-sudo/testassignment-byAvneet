# Rapidusertests Playwright suite

Full approach, flows, markers, and browser notes are in the [repository README](../README.md).

```powershell
pip install -r requirements.txt
python -m playwright install chrome
copy .env.example .env
# fill .env from the assignment PDF, then:
pytest
pytest -n 0 --headed
```
