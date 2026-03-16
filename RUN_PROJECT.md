# Running Krishi Mitr - Complete Guide

## Quick Start (3 minutes)

### Option 1: Run Everything at Once (Recommended)

```bash
# Terminal 1: Install dependencies
npm install
pip install -r requirements.txt

# Terminal 1: Start Flask backend
cd app
python app.py

# Terminal 2 (in another tab): Start Next.js frontend
npm run dev
```

Then visit:
- **Frontend**: http://localhost:3000 (Next.js - main interface)
- **Direct Flask**: http://localhost:5000 (if you want to see Flask directly)
- **Showcase**: http://localhost:5000/showcase (component showcase)

---

## Option 2: Flask Only (Original Setup)

If you want to run just the Flask app:

```bash
cd app
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000

---

## Option 3: Next.js Frontend Only

If Flask is already running on port 5000:

```bash
npm install
npm run dev
```

Visit: http://localhost:3000

---

## For v0 Preview

v0 automatically detects and runs:

```bash
npm install
npm run dev
```

This starts the Next.js development server on port 3000, which:
- ✅ Proxies Flask API calls to http://localhost:5000
- ✅ Shows your complete frontend
- ✅ Displays your Flask app in an iframe
- ✅ Allows full interaction with all features

---

## Production Deployment

### To Vercel

```bash
# vercel.json is already configured
vercel deploy
```

### With Docker

```bash
docker build -t krishi-mitr .
docker run -p 5000:5000 -p 3000:3000 krishi-mitr
```

### With Heroku

```bash
heroku create krishi-mitr
git push heroku main
```

---

## Environment Variables

Create `.env.local` for local development:

```bash
# Copy from .env.example
cp .env.example .env.local

# Edit with your values
MONGO_URI=your_mongodb_uri
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
WEATHER_API_KEY=your_weather_key
GEMINI_API_KEY=your_gemini_key
```

---

## Troubleshooting

### "Port 3000 already in use"
```bash
# Windows
netstat -ano | findstr :3000

# Mac/Linux
lsof -i :3000
kill -9 <PID>
```

### "Flask connection refused"
Make sure Flask is running on port 5000:
```bash
cd app && python app.py
```

### "Module not found errors"
```bash
# Reinstall dependencies
npm install
cd app && pip install -r requirements.txt
```

### "White screen of death"
1. Check browser console (F12 → Console tab)
2. Check Flask terminal for errors
3. Verify environment variables in `.env.local`

---

## Available Commands

```bash
# Development
npm run dev          # Start Next.js dev server
npm run flask        # Start Flask backend
npm run showcase     # Start both (if configured)

# Production
npm run build        # Build Next.js for production
npm start            # Start production Next.js server
npm run prod         # Build + start production

# Code Quality
npm run lint         # Lint Next.js + Flask code
npm run format       # Format all code
npm run test         # Run tests

# Flask Commands
cd app
python app.py        # Development
gunicorn -w 4 app:app  # Production
```

---

## Project Structure

```
Krishi Mitr/
├── pages/                 # Next.js pages (new)
│   └── index.tsx         # Home page
├── public/               # Static assets
├── app/                  # Flask backend (existing)
│   ├── app.py           # Main Flask app
│   ├── templates/       # HTML templates (26 files)
│   ├── static/
│   │   ├── css/        # Stylesheets (3 files, 1,342 lines)
│   │   ├── js/         # JavaScript (295 lines)
│   │   └── img/        # Images
│   ├── utils/          # Python utilities (5 modules)
│   ├── requirements.txt # Python dependencies
│   └── config.py       # Configuration
├── package.json        # Node.js configuration
├── next.config.js      # Next.js configuration
├── tsconfig.json       # TypeScript configuration
├── vercel.json         # Vercel deployment config
└── README.md          # Project documentation
```

---

## What's Happening Behind the Scenes

1. **Next.js** (port 3000) - Modern React framework for frontend
2. **Flask** (port 5000) - Python backend with AI agents
3. **Proxy** - Next.js automatically forwards API calls to Flask
4. **iframe** - Home page shows Flask UI in an iframe
5. **API Integration** - All data flows through Flask backend

---

## Next Steps

1. ✅ Run `npm install`
2. ✅ Run `cd app && python app.py` (Terminal 1)
3. ✅ Run `npm run dev` (Terminal 2)
4. ✅ Visit http://localhost:3000
5. ✅ Enjoy Krishi Mitr!

---

## Support

For issues or questions:
- Check [SETUP.md](./SETUP.md) for detailed setup
- Read [FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md) for frontend info
- See [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) for architecture details
- Visit [START_HERE.md](./START_HERE.md) for quick reference
