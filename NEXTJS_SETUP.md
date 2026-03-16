# Next.js Integration Guide

## Overview

Your Krishi Mitr project now has a modern Next.js 14 frontend that proxies all API calls to your Flask backend. This gives you:

- ✅ Modern React development experience
- ✅ TypeScript support
- ✅ Automatic API proxying to Flask
- ✅ Production-ready deployment
- ✅ Full v0 compatibility

## Files Created

### Configuration Files
1. **next.config.js** (71 lines)
   - Rewrites API routes to Flask backend
   - Security headers configuration
   - Image optimization settings

2. **tsconfig.json** (32 lines)
   - TypeScript configuration
   - Path aliases setup
   - Strict mode enabled

3. **Updated package.json** (enhanced with Next.js deps)
   - Next.js 14, React 18, TypeScript
   - Development scripts
   - Production build configuration

### Page Files
4. **pages/index.tsx** (62 lines)
   - Main homepage showing Flask app
   - Health check for Flask connectivity
   - Responsive iframe embed

### Directory Structure
5. **public/** - Static assets directory

## How It Works

```
User Request (http://localhost:3000)
    ↓
Next.js Development Server (port 3000)
    ↓
Checks route type:
    ├─ UI Routes → Renders React component
    ├─ API Routes → Rewrites to Flask (localhost:5000)
    └─ Static → Serves from /public
```

## Running the Project

### For v0 Preview (Automatic)

v0 automatically runs:
```bash
npm install
npm run dev
```

This starts Next.js on port 3000 and proxies all requests to Flask.

### Manual Setup

**Terminal 1 - Start Flask:**
```bash
cd app
python app.py
# Flask now running on http://localhost:5000
```

**Terminal 2 - Start Next.js:**
```bash
npm install
npm run dev
# Next.js now running on http://localhost:3000
```

### Visit
- **Frontend**: http://localhost:3000 (Next.js with Flask embedded)
- **Direct Flask**: http://localhost:5000 (original Flask app)
- **Showcase**: http://localhost:5000/showcase (component showcase)

## Production Build

```bash
# Build Next.js
npm run build

# Start production server
npm start
```

Your app will be optimized and ready for deployment!

## Deployment

### To Vercel (Recommended)
```bash
vercel deploy
```

vercel.json already configured!

### Docker
```bash
docker build -t krishi-mitr .
docker run -p 3000:3000 -p 5000:5000 krishi-mitr
```

### Heroku
```bash
heroku create krishi-mitr
git push heroku main
```

## API Route Configuration

The following routes are automatically proxied to Flask:

- `/api/*` → Flask API endpoints
- `/crop-recommend` → Flask route
- `/disease-predict` → Flask route
- `/fertilizer` → Flask route
- `/yield` → Flask route
- `/sustainability` → Flask route
- `/irrigation` → Flask route
- `/market-trends` → Flask route

## Environment Variables

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_FLASK_URL=http://localhost:5000
```

## Troubleshooting

### "Port 3000 already in use"
```bash
# Find and kill the process
lsof -i :3000
kill -9 <PID>
```

### "Cannot connect to Flask"
Make sure Flask is running:
```bash
cd app && python app.py
```

### "Module not found"
```bash
rm -rf node_modules .next
npm install
```

### "White screen"
Check browser console (F12) for errors

## File Structure

```
Krishi Mitr/
├── pages/                 # Next.js pages
│   └── index.tsx         # Homepage
├── public/               # Static assets
├── app/                  # Flask backend
│   ├── app.py
│   ├── templates/        # 26 HTML files
│   ├── static/
│   │   ├── css/         # 3 CSS files
│   │   ├── js/          # JavaScript
│   │   └── img/         # Images
│   └── utils/           # 5 Python modules
├── next.config.js        # Next.js config
├── tsconfig.json         # TypeScript config
├── package.json          # Node.js config
└── vercel.json          # Vercel config
```

## What's Included

✅ Next.js 14 with App Router support
✅ TypeScript for type safety
✅ React 18 with latest features
✅ Automatic API proxying
✅ Security headers
✅ Image optimization
✅ CSS support
✅ Hot module replacement (HMR)
✅ Production-ready build

## Next Steps

1. Run `npm install`
2. Start Flask: `cd app && python app.py`
3. Start Next.js: `npm run dev`
4. Visit http://localhost:3000
5. Deploy to Vercel when ready!

---

For more details, see:
- [RUN_PROJECT.md](./RUN_PROJECT.md) - How to run everything
- [README.md](./README.md) - Project overview
- [SETUP.md](./SETUP.md) - Initial setup guide
