DStore - Online Footwear E-commerce Platform
DStore is a powerful, feature-rich e-commerce website designed specifically for footwear sales. Built on Django 5.0.7, the platform offers a seamless experience for both users and administrators, combining modern design, responsive UI, secure authentication, and robust backend management.

🌐 Website Overview
DStore empowers users to shop online for shoes with ease, offering category-based browsing, real-time order tracking, and secure payment gateways. On the admin side, it provides full control over product inventory, order processing, and user management, all from a sleek dashboard interface.

🎯 Key Features
👟 Customer-Facing Features
User Authentication
Secure registration, login, and profile management using Django Allauth.

Social Login
Login via Google and Facebook accounts for added convenience.

Product Browsing & Search
Navigate through products by category, brand, and keywords with fast search.

Wishlist/Favorites
Add products to favorites for later consideration.

Shopping Cart & Checkout
Update cart contents, calculate totals, and proceed through a streamlined checkout flow.

Order Management
View order history and current status with estimated delivery timelines.

Responsive Design
Optimized UI for desktops, tablets, and mobile devices.

🛠️ Admin Dashboard
Product Management
Create, update, and delete footwear listings, including images and stock levels.

Order & Invoice Handling
Update order statuses, mark payments, and generate PDF invoices.

User Management
View customer info and assign roles or permissions.

Content Management
Use CKEditor 5 to edit product descriptions and site content with rich text support.

Inventory Monitoring
Keep track of stock levels and manage imports or low-stock alerts.

Analytics Dashboard
View revenue summaries, product performance, and customer activity using Django Jazzmin interface.

💳 Payment Gateways
VNPay Integration
Secure and local payment gateway for Vietnamese users.

MoMo Wallet
Quick mobile payments through MoMo API.

🛠️ Technology Stack

Component	Technology
Backend	Django 5.0.7
Frontend	HTML, CSS, JavaScript
Database	MySQL (utf8mb4 charset)
Admin UI	Django Jazzmin
Authentication	Django Allauth
Content Editor	Django CKEditor 5
Payment Integration	VNPay, MoMo
Sessions	Custom middleware-based session management
🚀 Installation Guide
Prerequisites
Python 3.8 or above

MySQL 5.7 or newer

pip (Python package manager)

Step-by-Step Setup
Clone the repository

bash
Copy
Edit
git clone https://github.com/dudiff/bangiaydjango.git
cd bangiaydjango
Create and activate a virtual environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate     # For Windows
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Configure your .env file
(Set database credentials, secret keys, API credentials, etc.)

Apply migrations

bash
Copy
Edit
python manage.py makemigrations
python manage.py migrate
Create superuser

bash
Copy
Edit
python manage.py createsuperuser
Run the server

bash
Copy
Edit
python manage.py runserver
Now access the site at http://127.0.0.1:8000

📦 Project Structure
bash
Copy
Edit
bangiaydjango/
│
├── core/               # Core functionality
├── users/              # User management (registration, profiles)
├── products/           # Product listing and detail pages
├── orders/             # Order tracking and checkout
├── cart/               # Cart system
├── promotions/         # Discount codes and promotions
├── templates/          # HTML templates
├── static/             # CSS, JS, and images
├── media/              # Uploaded product images
├── manage.py
└── requirements.txt
