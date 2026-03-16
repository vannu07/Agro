# Krishi Mitr - Quick Start

## 60 Seconds to Running

```bash
git clone https://github.com/vannu07/Agro.git
cd Agro
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
cd app && python app.py
# Visit http://localhost:5000
```

## Environment Variables (.env)

```env
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/krishi_mitr
WEATHER_API_KEY=your-weatherapi-key
GEMINI_API_KEY=your-gemini-key
FLASK_SECRET_KEY=random-32-char-string
```

## Features

- Crop recommendation
- Disease detection
- Fertilizer advice
- Yield prediction
- Sustainability planning
- Smart irrigation
- AI chatbot
- User profiles
- Activity logging

## Key Routes

Public: `/`, `/login`, `/api/health`
Protected: `/dashboard`, `/crop-recommend`, `/disease`, `/fertilizer`, `/yield`, `/sustainability`, `/irrigation`, `/profile`

## Troubleshooting

**Port in use?**
```bash
lsof -i :5000 && kill -9 <PID>
```

**MongoDB fails?**
- Verify connection string
- Check IP whitelist in MongoDB Atlas

**Auth0 fails?**
- Check credentials in .env
- Verify callback URL in Auth0 app settings

## Resources

- Detailed setup: SETUP.md
- All improvements: IMPROVEMENTS.md
- API reference: IMPROVEMENTS.md

## Production

```bash
# Heroku
git push heroku main

# Docker
docker build -t krishi-mitr .
docker run -p 5000:5000 --env-file .env krishi-mitr

# Standard
gunicorn -w 4 app:app
```

---
**Version**: 1.0.0-production-ready
