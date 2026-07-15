# Apex News Ninja Backend - Setup Guide

This guide will help you set up and run the backend application.

## Prerequisites

1. **Python 3.9+** installed
2. **MongoDB Atlas** account (or local MongoDB)
3. **Redis** server (local or remote)
4. **API Keys** (optional, for news fetching)

## Step 1: Install Dependencies

```bash
cd ApexNewsNinja_Backend
pip install -r requirements.txt
```

## Step 2: Create Environment File

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```
   (On Linux/Mac: `cp .env.example .env`)

2. Open `.env` and fill in the required values (see below)

## Step 3: Configure Required Environment Variables

### Required Variables (Must be set):

#### 1. MongoDB Connection
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/apex_news_ninja?retryWrites=true&w=majority
```
- Get this from your MongoDB Atlas dashboard
- Make sure your IP address (`197.211.52.70/32`) is whitelisted in MongoDB Atlas Network Access

#### 2. Redis Connection
```env
REDIS_URL=redis://localhost:6379/0
```

**If you don't have Redis installed:**

**Windows:**
- Download from: https://github.com/microsoftarchive/redis/releases
- Or use Docker: `docker run -d -p 6379:6379 redis:alpine`

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

**Temporary workaround (skip Redis while testing):**

If you can't run Redis yet, set this in `.env` to disable scheduler jobs that require it:

```
SCHEDULER_ENABLED=False
```

The API will still run; just remember to turn it back on and start Redis before enabling scheduled news fetching or digests.

#### 3. JWT Secret Keys
Generate secure random keys (at least 32 characters):

**Using Python:**
```bash
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_REFRESH_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

**Or use online generator:**
- Visit: https://generate-secret.vercel.app/32

Add to `.env`:
```env
JWT_SECRET_KEY=your-generated-secret-key-here-minimum-32-chars
JWT_REFRESH_SECRET_KEY=your-generated-refresh-secret-key-here-minimum-32-chars
```

### Optional Variables (Can be left empty for basic setup):

- `NEWSAPI_KEY` - For news fetching (get from https://newsapi.org/)
- `CRYPTOCOMPARE_API_KEY` - For crypto news
- `FMP_API_KEY` - For financial news
- `WAWP_API_KEY` - For WhatsApp integration

## Step 4: Verify Setup

### Check MongoDB Connection
Make sure your MongoDB Atlas IP whitelist includes: `197.211.52.70/32`

### Check Redis is Running
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

## Step 5: Run the Application

### Option 1: Using run.bat (Windows)
```bash
run.bat
```

### Option 2: Using run.py (All platforms)
```bash
python run.py
```

### Option 3: Using uvicorn directly
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 6: Verify It's Working

1. **Check the console** - You should see:
   ```
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

2. **Test the health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```
   Or open in browser: http://localhost:8000/health

3. **Check API documentation:**
   - Open: http://localhost:8000/docs

## Common Issues & Solutions

### Issue: "MONGODB_URL is required"
**Solution:** Make sure `.env` file exists and contains `MONGODB_URL`

### Issue: "JWT secret keys must be at least 32 characters"
**Solution:** Generate longer keys using the Python command above

### Issue: "Connection refused" (Redis)
**Solution:** 
- Make sure Redis is running: `redis-cli ping`
- Check `REDIS_URL` in `.env` matches your Redis setup

### Issue: "SSL handshake failed" (MongoDB)
**Solution:** 
- Check MongoDB Atlas IP whitelist includes `197.211.52.70/32`
- Update certificates: `pip install --upgrade certifi pymongo motor`
- See `TROUBLESHOOTING_MONGODB.md` for more details

### Issue: "Module not found"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: Port 8000 already in use
**Solution:** 
- Change port in `.env`: `PORT=8001`
- Or stop the process using port 8000

## Development vs Production

### Development Mode
- Set `DEBUG=True` in `.env`
- API docs available at `/docs`
- Auto-reload enabled

### Production Mode
- Set `DEBUG=False` in `.env`
- API docs disabled
- Use proper SSL certificates
- Set up nginx reverse proxy (see `NGINX_SETUP.md`)

## Next Steps

1. ✅ Set up `.env` file with required variables
2. ✅ Install and start Redis
3. ✅ Verify MongoDB connection
4. ✅ Run the application
5. ✅ Test the API endpoints
6. ✅ Set up nginx (optional, for production)

## Getting Help

- Check `TROUBLESHOOTING_MONGODB.md` for MongoDB issues
- Check `NGINX_SETUP.md` for production deployment
- Review application logs for detailed error messages

