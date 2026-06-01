# FoodAdvisor

A FastAPI app that recommends nearby restaurants based on location, cuisine, and user demand.

## Environment variables

Set these variables before starting the service:

- `AMAP_KEY`
- `DEEPSEEK_KEY`

## Local run

```powershell
python app.py
```

The app listens on `PORT` when it is set, otherwise it uses `2025`.

## Deploy on Render

This repo includes:

- `render.yaml`
- `requirements.txt`
- `.python-version`

After pushing the repo to GitHub:

1. Create a new Blueprint or Web Service in Render from this repository.
2. Add `AMAP_KEY` and `DEEPSEEK_KEY` in the Render environment settings.
3. Deploy the service.
