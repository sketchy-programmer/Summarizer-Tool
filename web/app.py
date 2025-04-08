from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import stripe
import os
import openai
import io
import zipfile
import tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortify.db'
app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

stripe.api_key = app.config['STRIPE_SECRET_KEY']
openai.api_key = app.config['OPENAI_API_KEY']
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html', stripe_public_key=app.config['STRIPE_PUBLIC_KEY'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Login unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/download')
@login_required
def download():
    return render_template('download.html', user=current_user)

@app.route('/download_links')
@login_required
def download_links():
    return render_template('download_links.html', user=current_user)

@app.route('/web-tool')
@login_required
def web_tool():
    return render_template('web_tool.html', user=current_user)

@app.route('/api/summarize', methods=['POST'])
@login_required
def api_summarize():
    if not current_user.is_premium and request.headers.get('X-Request-Source') != 'demo':
        return jsonify({
            'success': False,
            'message': 'Premium subscription required for this feature'
        }), 403
    
    data = request.json
    text = data.get('text', '')
    min_length = data.get('min_length', 100)
    max_length = data.get('max_length', 150)
    style = data.get('style', 'default')
    
    # Validate input
    if not text or len(text.strip()) < 50:
        return jsonify({
            'success': False,
            'message': 'Text is too short to summarize'
        }), 400
    
    try:
        # Define style instructions
        style_instructions = {
            "default": "Provide a clear and concise summary",
            "academic": "Provide a formal academic summary with structured points and technical language",
            "casual": "Provide a casual, conversational summary in simple language",
            "business": "Provide a professional business-oriented summary focusing on key actionable insights",
            "creative": "Provide a creative and engaging summary with vivid language"
        }
        
        style_instruction = style_instructions.get(style, style_instructions["default"])
        
        client = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=[
                {
                    "role": "system", 
                    "content": f"{style_instruction} between {min_length}-{max_length} words. Capture the key points and main ideas."
                },
                {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'result': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/paraphrase', methods=['POST'])
@login_required
def api_paraphrase():
    if not current_user.is_premium and request.headers.get('X-Request-Source') != 'demo':
        return jsonify({
            'success': False,
            'message': 'Premium subscription required for this feature'
        }), 403
    
    data = request.json
    text = data.get('text', '')
    min_length = data.get('min_length', 100)
    max_length = data.get('max_length', 200)
    style = data.get('style', 'default')
    
    # Validate input
    if not text or len(text.strip()) < 20:
        return jsonify({
            'success': False,
            'message': 'Text is too short to paraphrase'
        }), 400
    
    try:
        # Define style instructions
        style_instructions = {
            "default": "Rewrite this text in a clear and concise manner",
            "academic": "Rewrite this text in a formal academic style with technical language",
            "casual": "Rewrite this text in a casual, conversational tone with simple language",
            "business": "Rewrite this text in a professional business style",
            "creative": "Rewrite this text in a creative and engaging style with vivid language"
        }
        
        style_instruction = style_instructions.get(style, style_instructions["default"])
        
        client = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=[
                {
                    "role": "system", 
                    "content": f"{style_instruction}. The output should be between {min_length}-{max_length} words while preserving the original meaning."
                },
                {"role": "user", "content": f"Paraphrase the following text:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        paraphrased = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'result': paraphrased
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': 100,  # $1.00
                'product_data': {
                    'name': 'Shortify Premium',
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('payment_success', _external=True),
        cancel_url=url_for('index', _external=True),
    )
    return redirect(session.url, code=303)

@app.route('/payment-success')
@login_required
def payment_success():
    # Update user to premium
    current_user.is_premium = True
    db.session.commit()
    flash('Your payment was successful! You now have premium access.', 'success')
    return redirect(url_for('download'))

@app.route('/api/code-summarize', methods=['POST'])
@login_required
def api_code_summarize():
    if not current_user.is_premium and request.headers.get('X-Request-Source') != 'demo':
        return jsonify({
            'success': False,
            'message': 'Premium subscription required for this feature'
        }), 403
    
    data = request.json
    code = data.get('text', '')
    max_length = data.get('max_length', 150)
    language = data.get('language', None)
    
    # Validate input
    if not code or len(code.strip()) < 20:
        return jsonify({
            'success': False,
            'message': 'Code snippet is too short to summarize'
        }), 400
    
    try:
        # If language is not specified, attempt to detect it
        language_prompt = f"The code is written in {language}." if language else "Detect the programming language and note it in your response."
        
        client = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a code analysis expert. {language_prompt} Provide a clear, concise explanation of what this code does in {max_length} words or less. Focus on the overall purpose, key functions, and important logic. Include any important edge cases or potential issues."
                },
                {"role": "user", "content": f"Summarize this code:\n\n```\n{code}\n```"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'result': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/download_app_platform/<platform>')
@login_required
def download_app_platform(platform):
    # Check if user has premium access
    if not current_user.is_premium:
        flash('Premium access required to download the application', 'danger')
        return redirect(url_for('download'))
    
    # Create an in-memory file-like object to store the zip
    memory_file = io.BytesIO()
    
    # Create a zip file
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Determine which executable to include based on platform
        if platform == 'windows':
            exe_path = os.path.join(app.root_path, 'static', 'Shortify-Windows.exe')
            exe_filename = 'Shortify-Windows.exe'
        elif platform == 'macos':
            exe_path = os.path.join(app.root_path, 'static', 'AISummarizer-MacOS')
            exe_filename = 'Shortify-MacOS'
        elif platform == 'linux':
            exe_path = os.path.join(app.root_path, 'static', 'AISummarizer-Linux.AppImage')
            exe_filename = 'Shortify-Linux.AppImage'
        else:
            # Default to Windows if platform not specified
            exe_path = os.path.join(app.root_path, 'static', 'Shortify-Windows.exe')
            exe_filename = 'Shortify-Windows.exe'
            
        # Add the executable to the zip file if it exists
        if os.path.exists(exe_path):
            zf.write(exe_path, exe_filename)
        else:
            # If executable doesn't exist, create a placeholder for testing
            zf.writestr(exe_filename, b'This is a placeholder for the actual executable')
        
        # Create a .env file with the API key
        api_key_content = "OPENAI_API_KEY=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"
        zf.writestr('.env', api_key_content)
        
        # Add README.txt file with instructions
        readme_content = """
Shortify - AI Text Summarizer
=============================

Thank you for downloading Shortify!

IMPORTANT SETUP INFORMATION:
1. Keep the .env file and application executable in the SAME DIRECTORY
2. Do not delete or modify the .env file - it contains your API key
3. The application will not work without the .env file

Basic Usage:
1. Run the Shortify application
2. Select text in any application
3. Press Ctrl+C to copy it
4. Right-click the Shortify icon and choose an action: 
   - Summarize: Creates a concise summary
   - Paraphrase: Rewrites the text in different words
   - Code Summarize: Explains code snippets
5. Use the Settings option to customize the behavior

For help or issues, please contact support@shortify.app
"""
        zf.writestr('README.txt', readme_content)
    
    # Reset the memory file position to the beginning
    memory_file.seek(0)
    
    # Set the appropriate filename based on platform
    filename = f"Shortify-{platform.capitalize()}.zip"
    
    # Send the file to the user
    return send_file(
        memory_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/zip'
    )

def initialize_database():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)