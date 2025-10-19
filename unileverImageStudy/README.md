# 🧠 Mindsurve - IPED Research Study Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen.svg)](#)

A **production-ready** Flask application for conducting IPED (Individual Parameter Estimation Design) research studies with comprehensive task timing analytics, anonymous respondent participation, and dual storage support (Azure Blob Storage + Local File System).

---

## 🚀 **Quick Start (Production)**

### **1. Prerequisites**
- **Python 3.9+**
- **MongoDB 6.0+**
- **Git**

### **2. Installation**
```bash
# Clone repository
git clone <repository-url>
cd unileverImageStudy

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
nano .env  # Edit with your settings

# Start production server
python start_production.py
```

### **3. Access Application**
- **Main App**: http://localhost:55000
- **Health Check**: http://localhost:55000/health
- **Dashboard**: http://localhost:55000/dashboard

---

## 🏗️ **Architecture & Features**

### **Core Functionality**
- ✅ **Multi-Step Study Creation**: 3-step wizard for IPED studies
- ✅ **Dual Study Types**: Grid and layer-based image studies
- ✅ **Anonymous Participation**: Public access without registration
- ✅ **Advanced Analytics**: Task timing and interaction tracking
- ✅ **IPED Algorithm**: Automated task matrix generation
- ✅ **Dual Storage**: Azure Blob Storage + Local File System
- ✅ **Data Export**: JSON/CSV with complete timing data

### **Security & Performance**
- ✅ **Production Security**: CSRF protection, rate limiting, security headers
- ✅ **Comprehensive Logging**: Structured logging with performance metrics
- ✅ **Error Handling**: Graceful error handling with detailed logging
- ✅ **Health Monitoring**: Built-in health check endpoints
- ✅ **Database Optimization**: Optimized MongoDB connections and indexes

### **Technology Stack**
- **Backend**: Flask 2.3.3 + Python 3.9+
- **Database**: MongoDB 6.0+ with MongoEngine ODM
- **Authentication**: Flask-Login + Flask-WTF + bcrypt
- **Frontend**: Pure HTML5, CSS3, JavaScript (no external dependencies)
- **Storage**: Azure Blob Storage + Local File System
- **Deployment**: Docker + Nginx + Gunicorn
- **Monitoring**: Structured logging + health checks

---

## 📋 **System Requirements**

### **Minimum Requirements**
- **OS**: Linux/macOS/Windows
- **Python**: 3.9 or higher
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for Azure storage

### **Production Requirements**
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.9+
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 50GB+ SSD storage
- **Database**: MongoDB 6.0+ (local or Atlas)
- **Network**: Stable internet connection

---

## 🔧 **Configuration**

### **Environment Variables (.env)**
```bash
# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
WTF_CSRF_ENABLED=True

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=mindsurve_production

# =============================================================================
# STORAGE CONFIGURATION
# =============================================================================
USE_LOCAL_STORAGE=false  # true for local, false for Azure
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_CONTAINER_NAME=mindsurve-images

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
SESSION_COOKIE_SECURE=True  # Set to True with HTTPS
BCRYPT_LOG_ROUNDS=12

# =============================================================================
# PERFORMANCE CONFIGURATION
# =============================================================================
MAX_CONTENT_LENGTH=10485760  # 10MB
WORKERS=4  # Gunicorn workers
```

### **Storage Modes**

#### **Azure Storage (Recommended for Production)**
```bash
USE_LOCAL_STORAGE=false
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_CONTAINER_NAME=mindsurve-images
```

#### **Local Storage (Development/Testing)**
```bash
USE_LOCAL_STORAGE=true
LOCAL_UPLOAD_FOLDER=local_uploads
```

---

## 🚀 **Deployment Options**

### **Option 1: Direct Python (Recommended for Development)**
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your settings

# Start MongoDB
sudo systemctl start mongod

# Run application
python start_production.py
```

### **Option 2: Docker (Recommended for Production)**
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Option 3: Gunicorn (Production Server)**
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:55000 --workers 4 --timeout 120 start_production:app
```

### **Option 4: Systemd Service (Linux Production)**
```bash
# Create service file
sudo nano /etc/systemd/system/mindsurve.service

# Enable and start service
sudo systemctl enable mindsurve
sudo systemctl start mindsurve
sudo systemctl status mindsurve
```

---

## 📚 **Usage Guide**

### **For Study Creators**

#### **1. Account Setup**
1. Register at `/register`
2. Verify email (if configured)
3. Login at `/login`

#### **2. Creating a Study**
1. **Step 1**: Basic information (title, background, language)
2. **Step 2**: Study configuration (type, questions, elements)
3. **Step 3**: Task generation and launch

#### **3. Study Management**
- **Dashboard**: View all studies and statistics
- **Analytics**: Detailed timing and interaction data
- **Export**: Download results in JSON/CSV format
- **Share**: Generate public participation URLs

### **For Study Participants**

#### **1. Accessing Studies**
1. Use the shared study URL
2. Read study information and consent
3. Complete classification questions (optional)
4. Follow study instructions
5. Complete rating tasks
6. Submit responses

#### **2. Study Types**
- **Grid Studies**: Rate elements in a grid layout
- **Layer Studies**: Rate layered image combinations

---

## 🔍 **Monitoring & Maintenance**

### **Health Checks**
```bash
# Application health
curl http://localhost:55000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-01-27T10:30:00Z",
  "database": "connected",
  "storage": "azure",
  "version": "1.0.0"
}
```

### **Logging**
- **Application Logs**: `logs/mindsurve.log`
- **Error Logs**: `logs/mindsurve_errors.log`
- **Log Rotation**: Automatic (10MB files, 5 backups)

### **Database Maintenance**
```bash
# Create indexes (run once)
python -c "from app import create_tables; create_tables()"

# Cleanup old data (optional)
python scripts/cleanup_completed_studies.py
```

### **Backup Strategy**
1. **Database**: Regular MongoDB backups
2. **Files**: Azure Blob Storage (automatic) or local file backups
3. **Configuration**: Version control for `.env` and config files

---

## 🛠️ **Development**

### **Project Structure**
```
unileverImageStudy/
├── app.py                 # Main application factory
├── start_production.py    # Production startup script
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── docker-compose.yml    # Docker configuration
├── Dockerfile           # Docker image definition
├── nginx/               # Nginx configuration
├── models/              # Database models
├── routes/              # Flask blueprints
├── templates/           # HTML templates
├── static/              # CSS, JS, images
├── utils/               # Utility functions
├── scripts/             # Maintenance scripts
└── logs/                # Application logs
```

### **Key Components**
- **`app.py`**: Flask application factory with security and logging
- **`config.py`**: Environment-based configuration management
- **`utils/storage_manager.py`**: Dual storage abstraction layer
- **`utils/task_calculation.py`**: IPED algorithm implementation
- **`utils/logging_config.py`**: Structured logging configuration

### **Database Models**
- **`User`**: Study creators with authentication
- **`Study`**: Complete study configuration and IPED matrices
- **`StudyDraft`**: Temporary study data during creation
- **`StudyResponse`**: Anonymous participant responses
- **`TaskSession`**: Individual task timing data

---

## 🔒 **Security Features**

### **Authentication & Authorization**
- **Flask-Login**: Session management
- **bcrypt**: Password hashing
- **CSRF Protection**: Cross-site request forgery prevention
- **Rate Limiting**: API and form submission limits

### **Security Headers**
- **X-Content-Type-Options**: Prevent MIME sniffing
- **X-Frame-Options**: Prevent clickjacking
- **X-XSS-Protection**: XSS protection
- **Strict-Transport-Security**: HTTPS enforcement
- **Referrer-Policy**: Control referrer information

### **Data Protection**
- **Input Validation**: Server-side form validation
- **File Upload Security**: Type and size restrictions
- **SQL Injection Prevention**: MongoEngine ODM protection
- **Session Security**: Secure cookie configuration

---

## 📊 **Performance Optimization**

### **Database Optimization**
- **Connection Pooling**: Optimized MongoDB connections
- **Indexes**: Strategic database indexes for fast queries
- **Query Optimization**: Efficient database queries

### **Caching Strategy**
- **Redis Caching**: Optional Redis integration
- **Static File Caching**: Browser caching for static assets
- **Response Caching**: Cached API responses

### **File Handling**
- **Image Optimization**: Automatic image compression
- **CDN Integration**: Azure CDN for static assets
- **Lazy Loading**: Progressive image loading

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Database Connection Failed**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check connection string
grep MONGODB .env

# Test connection
python -c "from mongoengine import connect; connect('mindsurve_production')"
```

#### **File Upload Issues**
```bash
# Check storage configuration
grep USE_LOCAL_STORAGE .env

# Check permissions
ls -la local_uploads/

# Check Azure credentials
python -c "from utils.azure_storage import test_connection; test_connection()"
```

#### **Performance Issues**
```bash
# Check logs
tail -f logs/mindsurve.log

# Monitor resources
htop
df -h

# Check database performance
mongostat
```

### **Debug Mode**
```bash
# Enable debug mode
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG

# Run with debug
python start_production.py
```

---

## 📈 **Scaling Considerations**

### **Horizontal Scaling**
- **Load Balancer**: Nginx or cloud load balancer
- **Multiple Instances**: Run multiple app instances
- **Database Clustering**: MongoDB replica sets
- **CDN**: Content delivery network for static assets

### **Vertical Scaling**
- **Memory**: Increase RAM for larger studies
- **CPU**: More workers for concurrent users
- **Storage**: Larger storage for file uploads
- **Database**: More powerful MongoDB instance

---

## 🤝 **Support & Contributing**

### **Getting Help**
1. **Documentation**: Check this README and inline comments
2. **Logs**: Check application logs for error details
3. **Health Check**: Use `/health` endpoint for system status
4. **Issues**: Create GitHub issues for bugs or feature requests

### **Contributing**
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏆 **Production Checklist**

### **Pre-Deployment**
- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] Storage configuration verified
- [ ] Security settings reviewed
- [ ] Logging configured
- [ ] Health checks working

### **Post-Deployment**
- [ ] Application accessible
- [ ] Health check responding
- [ ] User registration working
- [ ] Study creation functional
- [ ] File uploads working
- [ ] Data export functional
- [ ] Monitoring in place

---

**🎯 Ready for Production!** This application is production-ready with comprehensive security, logging, monitoring, and error handling. Follow the deployment guide above to get started.

### Environment Variables

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
DEBUG=False

# MongoDB Configuration
MONGODB_URI=mongodb://username:password@host:port/database

# Storage Configuration
USE_LOCAL_STORAGE=false  # Set to true for local storage
LOCAL_UPLOAD_FOLDER=local_uploads

# Azure Storage (if using Azure)
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_CONTAINER_NAME=your-container

# File Upload Configuration
MAX_CONTENT_LENGTH=5242880
UPLOAD_FOLDER=./uploads

# Security Configuration
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

### MongoDB Configuration

```javascript
// MongoDB connection string format
mongodb://username:password@host:port/database?authSource=admin

// Example
mongodb://admin:password123@localhost:27017/iped_system?authSource=admin
```

## 📊 IPED Algorithm

### Task Matrix Generation

The system implements the IPED algorithm to generate balanced task assignments:

1. **Parameter Input**:
   - Number of elements (4-16)
   - Tasks per consumer (1-100)
   - Number of respondents (1-10,000)
   - Min/max active elements per task

2. **Matrix Generation**:
   - Creates candidate task pool
   - Ensures balanced element distribution
   - Validates constraints (min/max active elements)
   - Generates respondent-specific task sequences

3. **Task Structure**:
   ```json
   {
     "0": [  // Respondent 0
       {
         "task_id": "0_0",
         "elements_shown": {"E1": 1, "E2": 0, "E3": 1, ...},
         "task_index": 0
       }
     ]
   }
   ```

## 🔒 Security Features

### Authentication & Authorization
- Secure password hashing with bcrypt
- Session management with Flask-Login
- CSRF protection for all forms
- Secure cookie configuration

### File Upload Security
- File type validation (images only)
- File size limits (16MB max)
- Secure filename generation
- Upload directory isolation

### Rate Limiting
- API endpoint rate limiting
- Login attempt throttling
- Anonymous user protection

## 📈 Analytics & Reporting

### Task Timing Analytics
- **Individual Task Timing**: Start/end timestamps and duration
- **Element Interaction Tracking**: View time, hover count, click count
- **Page Visibility Tracking**: Handle tab switching and minimize
- **Abandonment Detection**: Track incomplete tasks and reasons

### Data Export Options
- **JSON Export**: Complete data structure preservation
- **CSV Export**: Compatible with statistical analysis software
- **Timing Data**: Include all interaction and timing information
- **Anonymized Options**: Remove identifying information

### Real-time Dashboard
- **Response Tracking**: Live completion statistics
- **Performance Metrics**: Average completion times
- **Geographic Distribution**: IP-based analytics
- **Trend Analysis**: Daily/weekly completion patterns

## 🛠️ Maintenance Scripts

### Available Scripts

#### 1. Auto-Abandon In-Progress Responses
**Script**: `scripts/auto_abandon_inprogress.py`
**Purpose**: Automatically marks in-progress responses as abandoned if there's no activity for more than 10 minutes.
**Frequency**: Run every 5 minutes

#### 2. Cleanup Completed Studies
**Script**: `scripts/cleanup_completed_studies.py`
**Purpose**: 
- Deletes panelist task data for completed studies to free up database space
- Marks all in-progress responses as abandoned
**Frequency**: Run daily (recommended) or weekly

### Setting Up Cron Jobs

1. **Edit crontab**:
   ```bash
   crontab -e
   ```

2. **Add these lines**:
   ```bash
   # Auto-abandon inactive responses every 5 minutes
   */5 * * * * cd /path/to/unileverImageStudy && source venv/bin/activate && python3 scripts/auto_abandon_inprogress.py >> logs/auto_abandon.log 2>&1

   # Clean up completed studies daily at 2 AM
   0 2 * * * cd /path/to/unileverImageStudy && source venv/bin/activate && python3 scripts/cleanup_completed_studies.py >> logs/cleanup.log 2>&1
   ```

3. **Save and exit**

4. **Verify**:
   ```bash
   crontab -l
   ```

### Monitor Logs
```bash
# View auto-abandon logs
tail -f logs/auto_abandon.log

# View cleanup logs
tail -f logs/cleanup.log
```

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask pytest-mongodb

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Test storage modes
python test_storage_modes.py
```

### Test Coverage
- Unit tests for models and utilities
- Integration tests for API endpoints
- Form validation testing
- Database operation testing
- Storage mode testing

## 🚀 Production Deployment

### Prerequisites
- SSL certificates for HTTPS
- Domain name configuration
- MongoDB production setup
- Redis for session storage (optional)

### Deployment Steps
1. **Environment Setup**: Configure production environment variables
2. **SSL Configuration**: Set up SSL certificates
3. **Database Setup**: Configure MongoDB with authentication
4. **Service Configuration**: Set up systemd services
5. **Monitoring**: Configure logging and monitoring
6. **Backup**: Set up automated backup procedures

### Performance Optimization
- **MongoDB Indexing**: Optimize database queries
- **Static File Serving**: Configure Nginx for static files
- **Caching**: Implement Redis caching layer
- **Load Balancing**: Set up multiple application instances

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start
1. Check Python environment is activated
2. Verify MongoDB is running
3. Check file permissions
4. Review log files for errors

#### Database Connection Issues
1. Verify MongoDB connection in `config.py`
2. Check MongoDB is accessible
3. Ensure all required models are imported
4. Check network connectivity

#### File Upload Issues
1. Check storage configuration (Azure vs Local)
2. Verify file permissions
3. Check disk space (for local storage)
4. Verify Azure credentials (for Azure storage)

#### Cron Jobs Not Working
1. Verify cron service is running
2. Check absolute paths are correct
3. Ensure logs directory exists
4. Test script manually first

### Performance Issues

#### Slow Study Details Page
- The application has been optimized with:
  - MongoDB timeout fixes
  - Optimized database queries
  - Reduced data loading
  - Better error handling

#### High Memory Usage
- Regular cleanup scripts help manage memory
- Monitor database size
- Consider archiving old studies

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- Follow PEP 8 Python style guidelines
- Add comprehensive docstrings
- Include type hints where appropriate
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)

### Issues & Questions
- Create an issue on GitHub
- Check existing issues for solutions
- Review the documentation

### Community
- Join our discussion forum
- Contribute to the project
- Share your use cases

## 🔄 Changelog

### Version 2.0.0
- Added dual storage system (Azure + Local)
- Improved performance optimizations
- Enhanced error handling
- Better maintenance scripts

### Version 1.0.0
- Initial release with core IPED functionality
- Multi-step study creation wizard
- Anonymous respondent participation
- Comprehensive task timing analytics
- Production-ready deployment configuration

## 📞 Contact

- **Project Maintainer**: Dheeraj Joshi
- **Email**: dlovej009@gmail.com
- **GitHub**: dheeraj009joshi

---

**Note**: This system is designed for research purposes and includes comprehensive data collection. Ensure compliance with relevant privacy regulations (GDPR, CCPA, etc.) when deploying in production environments.