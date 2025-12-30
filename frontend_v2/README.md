# Institute Management System - Frontend

3D Animated Landing Page with Glassmorphism Design

## Features
- 3D Graduation Cap Animation (Three.js)
- Particle Background Effects
- Glassmorphism UI
- Pricing Plans in INR
- Demo Mode
- Role-based Login Modal

## Backend API
Connected to: https://yashamishra.pythonanywhere.com/api

## Local Development

Open `index.html` in a web browser or use a local server:

```bash
python3 -m http.server 8000
```

Visit: http://localhost:8000

## Netlify Deployment

### Quick Deploy (Recommended)

1. **Push to GitHub** (if not already done):
```bash
cd /path/to/frontend_v2
git add .
git commit -m "Prepare for Netlify deployment"
git push origin main
```

2. **Deploy to Netlify**:
   - Go to [netlify.com](https://netlify.com)
   - Click "Add new site" →  "Import an existing project"
   - Choose GitHub and select your repository
   - Configure:
     - **Base directory**: `frontend_v2`
     - **Build command**: (leave empty)
     - **Publish directory**: `.`
   - Click "Deploy site"

3. **Get Your URL**:
   - After deployment, you'll get a URL like: `https://your-site.netlify.app`
   - You can customize this under "Domain settings"

### Post-Deployment

Update CORS on backend to allow requests from your Netlify URL.

## Alternative Deployment Options

- **GitHub Pages**: Ready to deploy
- **Vercel**: One-click deployment
- **Any Static Host**: Just upload the files

## Files Structure

```
frontend_v2/
├── index.html          # Main landing page
├── css/
│   └── style.css      # Glassmorphism styles
├── js/
│   ├── app.js         # Main application logic
│   ├── particles.js   # Particle animation
│   └── 3d-scene.js    # Three.js 3D objects
├── netlify.toml       # Netlify configuration
└── _redirects         # SPA routing
```

## Live Demo

- **Frontend**: Will be deployed to Netlify
- **Backend API**: https://yashamishra.pythonanywhere.com
- **API Docs**: https://yashamishra.pythonanywhere.com/api/schema/swagger-ui/

## Contact

📞 Demo: 8356926231
