# SaveTogether Backend API

A comprehensive REST API for the SaveTogether stockvel (group savings) application. This backend replaces Firebase services with a custom Python Flask API that provides user authentication, stockvel management, and contribution tracking.

## 🚀 Features

- **User Authentication**: JWT-based registration, login, and profile management
- **Stockvel Management**: Create, join, and manage savings groups
- **Contribution Tracking**: Record and track member contributions
- **Search Functionality**: Find users and stockvels
- **PostgreSQL/SQLite Support**: Flexible database configuration
- **Docker Ready**: Easy deployment with Docker and docker-compose
- **Production Ready**: Gunicorn WSGI server with health checks

## 🛠 Technologies Used

- **Framework**: Flask 3.0 with Flask-SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Database**: PostgreSQL (production) / SQLite (development)
- **Security**: Werkzeug password hashing, CORS protection
- **Deployment**: Docker, Gunicorn WSGI server
- **Environment**: python-dotenv for configuration

## 📋 Requirements

- Python 3.11+
- PostgreSQL (production) or SQLite (development)
- Docker (optional)

## 🔧 Setup Instructions

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd savetogether-backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux  
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

5. **Run the application:**
   ```bash
   python src/main.py
   ```

The API will be available at `http://localhost:5000`

### Docker Deployment

1. **Build and run with Docker:**
   ```bash
   docker build -t savetogether-backend .
   docker run -p 5000:5000 savetogether-backend
   ```

2. **Or use docker-compose:**
   ```bash
   docker-compose up --build
   ```

### EC2 Deployment

1. **Prepare your EC2 instance:**
   ```bash
   # Update packages
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   sudo apt install docker.io docker-compose -y
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   ```

2. **Deploy the application:**
   ```bash
   # Clone your repository
   git clone <your-repo-url>
   cd savetogether-backend
   
   # Set up environment
   cp .env.example .env
   nano .env  # Configure for production
   
   # Build and run
   docker-compose up -d --build
   ```

3. **Set up reverse proxy (optional):**
   Use nginx to serve your API on port 80/443

## 📚 API Documentation

### Base URL
- Development: `http://localhost:5000/api`
- Production: `https://your-domain.com/api`

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword",
  "phone": "+1234567890"
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer <access_token>
```

### Stockvel Endpoints

#### Create Stockvel
```http
POST /api/stockvels/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "My Savings Group",
  "description": "Monthly savings for vacation",
  "target_amount": 10000.00,
  "monthly_contribution": 500.00,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "max_members": 10
}
```

#### Get User's Stockvels
```http
GET /api/stockvels/
Authorization: Bearer <access_token>
```

#### Join Stockvel
```http
POST /api/stockvels/{stockvel_id}/join
Authorization: Bearer <access_token>
```

#### Make Contribution
```http
POST /api/stockvels/{stockvel_id}/contribute
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 500.00,
  "description": "Monthly contribution"
}
```

#### Get Contributions
```http
GET /api/stockvels/{stockvel_id}/contributions
Authorization: Bearer <access_token>
```

### User Endpoints

#### Get User Stats
```http
GET /api/users/stats
Authorization: Bearer <access_token>
```

#### Search Users
```http
GET /api/users/search?q=john
Authorization: Bearer <access_token>
```

### Health Check
```http
GET /api/health
```

## 🗄 Database Schema

### Users Table
- `id` (Primary Key)
- `email` (Unique)
- `name`
- `password_hash`
- `phone`
- `created_at`
- `is_active`

### Stockvels Table
- `id` (Primary Key)
- `name`
- `description`
- `target_amount`
- `current_amount`
- `monthly_contribution`
- `start_date`
- `end_date`
- `created_by` (Foreign Key to Users)
- `max_members`
- `is_active`

### StockvelMembers Table
- `id` (Primary Key)
- `stockvel_id` (Foreign Key)
- `user_id` (Foreign Key)
- `joined_at`
- `is_admin`
- `total_contributed`

### Contributions Table
- `id` (Primary Key)
- `stockvel_id` (Foreign Key)
- `user_id` (Foreign Key)
- `amount`
- `contribution_date`
- `description`

## 🔐 Security Features

- JWT token-based authentication
- Password hashing with Werkzeug
- CORS protection
- Input validation and sanitization
- SQL injection prevention through SQLAlchemy ORM
- Environment-based configuration

## 📊 Monitoring & Health

- Health check endpoint: `/api/health`
- Docker health checks configured
- Error handling with proper HTTP status codes
- Logging for debugging and monitoring

## 🚀 Production Considerations

1. **Environment Variables**: Ensure all sensitive data is in environment variables
2. **Database**: Use PostgreSQL in production
3. **Security**: Change default JWT secrets
4. **SSL**: Use HTTPS in production
5. **Monitoring**: Set up logging and monitoring
6. **Backup**: Regular database backups
7. **Scaling**: Consider load balancers for high traffic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 📧 Support

For support, email [your-email@example.com] or create an issue in the repository.