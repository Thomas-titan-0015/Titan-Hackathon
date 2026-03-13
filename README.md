# 💎 Tanishq Luxury Jewelry E-Commerce Platform

A sophisticated AI-powered e-commerce platform for luxury jewelry, built for a hackathon. Features intelligent product recommendations, conversational AI chatbot, and complete shopping experience.

## ✨ Features

### 🛍️ E-Commerce Features
- **Product Catalog**: Browse jewelry by categories (Rings, Necklaces, Earrings, Bracelets, Pendants, Bangles)
- **Advanced Search & Filters**: Price range, category, and search functionality
- **Shopping Cart & Wishlist**: Full shopping experience with persistent storage
- **Guest Checkout**: Shop without registration
- **Order Management**: Complete order lifecycle with promo codes
- **User Profiles**: DOB/anniversary tracking for personalized experiences

### 🤖 AI-Powered Features
- **Conversational Chatbot**: Powered by Titan AI Gateway for natural jewelry consultations
- **Personalized Recommendations**: AI-driven product suggestions based on user preferences
- **Smart Categorization**: Categories reorder based on browsing history
- **Intelligent Routing**: Chatbot adapts conversation flow based on user intent

### 🔐 Security & Authentication
- **JWT Authentication**: Secure token-based authentication
- **Phone Verification**: SMS OTP verification via Fast2SMS
- **Email OTP**: Registration verification
- **Role-based Access**: Admin and user roles
- **API Security**: Protected endpoints with API key middleware

### 📊 Admin Dashboard
- **Analytics Dashboard**: Real-time user and session analytics
- **User Management**: View and manage all users
- **Chat Monitoring**: Track conversation sessions and performance
- **Recommendation Analytics**: Monitor AI recommendation effectiveness

## 🛠️ Tech Stack

### Backend
- **Python 3.13** with **FastAPI**
- **SQLAlchemy** ORM with SQLite database
- **OpenAI SDK** with Titan AI Gateway integration
- **JWT** authentication with bcrypt password hashing
- **Pydantic** for data validation

### Frontend
- **Vanilla HTML/CSS/JavaScript** (No frameworks)
- **Responsive Design** with modern CSS
- **Progressive Web App** features
- **Real-time Updates** via API polling

### AI & Integrations
- **Titan AI Gateway**: Enterprise AI infrastructure
- **Fast2SMS**: SMS OTP delivery
- **IP Geolocation**: User location detection

## 🚀 Quick Start

### Prerequisites
- Python 3.13 or higher
- Internet connection for AI services

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Titan-Hackathon.git
   cd Titan-Hackathon
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy and edit .env file
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start the server**
   ```bash
   py -m uvicorn app.main:app --reload --port 8000
   ```

5. **Open in browser**
   ```
   http://localhost:8000
   ```

## 📁 Project Structure

```
├── backend/                 # Python FastAPI server
│   ├── app/
│   │   ├── main.py         # Main application & static file serving
│   │   ├── db/             # Database models & setup
│   │   ├── routers/        # API endpoints
│   │   ├── agents/         # AI conversation logic
│   │   ├── services/       # External integrations
│   │   └── schemas/        # Data validation models
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment configuration
│   └── seed.py            # Database seeding
├── frontend/               # Static HTML/CSS/JS
│   ├── *.html             # Application pages
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript modules
├── .gitignore             # Git ignore rules
├── PROJECT_DOCUMENTATION.txt  # Technical documentation
├── RUNNING_INSTRUCTIONS.txt   # Setup guide
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Security
JWT_SECRET="your-jwt-secret-key"
API_SECRET_KEY="your-api-key"

# AI Integration
TITAN_AI_KEY="your-titan-ai-jwt-token"
AI_GATEWAY="https://ai.titan.in/gateway"

# SMS (Optional)
FAST2SMS_KEY="your-fast2sms-key"

# Email (Optional)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"
```

## 🎯 Demo Credentials

### Admin Access
- **Email**: admin@tanishq.com
- **Password**: Admin@123
- **Dashboard**: http://localhost:8000/dashboard.html

### User Accounts
- **Priya**: priya@tanishq.com / User@123
- **Rahul**: rahul@tanishq.com / User@123

## 🌟 Key Highlights

- **AI-First Design**: Every interaction is enhanced with AI
- **Production Ready**: Complete authentication, security, and error handling
- **Scalable Architecture**: Clean separation of concerns
- **Modern UX**: Smooth animations and responsive design
- **Enterprise Integration**: Real AI gateway and SMS services

## 📈 Performance

- **FastAPI**: High-performance async web framework
- **SQLite**: Lightweight database for development
- **Static File Serving**: Direct file serving for optimal performance
- **Lazy Loading**: Images load on demand
- **Session Storage**: Efficient client-side state management

## 🔒 Security

- **API Key Protection**: All endpoints protected with middleware
- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Stateless authentication
- **Input Validation**: Pydantic models prevent injection
- **CORS Configuration**: Controlled cross-origin access

## 🚀 Deployment

### Quick Demo (ngrok)
```bash
# Install ngrok
npm install -g ngrok

# Start server
py -m uvicorn app.main:app --port 8000

# Create tunnel
ngrok http 8000
```

### Production (Render.com)
1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project was created for a hackathon and is available for educational purposes.

## 🙏 Acknowledgments

- **Titan Company Limited** for the AI infrastructure
- **Fast2SMS** for SMS services
- **OpenAI** for the AI SDK
- **FastAPI** team for the excellent framework

---

**Built with ❤️ for the Tanishq Luxury Jewelry Hackathon**