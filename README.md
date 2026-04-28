# CSCI40-E-15 Midterm Project

## Members
- Chua, Phoebe
- Linchangco, Ricki
- Macasaet, Javier
- Pangilinan, Chloe
- Villasurda, Ezekiel

# Setup Guide

## Prerequisites

- **Python**
- **pip**
- **Git**

## Setup Instructions
1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

2. Create and Activate a Virtual Environment

Windows
```bash
python -m venv myenv
myenv\Scripts\activate
```

macOS / Linux
```bash
python3 -m venv myenv
source myenv/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Generate the Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

5. Use the Secret Key in the .env file
```bash
touch .env
```

```bash
# insert inside .env file
SECRET_KEY='your_generated_secret_key_here'
```

6. Run the Development Server
```bash
python manage.py runserver
```
