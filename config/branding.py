# =============================================================================
# FILE: config/branding.py
# PURPOSE: University ki branding aur identity yahan define hoti hai.
# ⚠️  NAYI UNIVERSITY KE LIYE SIRF YEH FILE CHANGE KARO
#
# Kya change karna hai:
# 1. UNIVERSITY_NAME
# 2. UNIVERSITY_SHORT_NAME
# 3. UNIVERSITY_LOGO_URL
# 4. PRIMARY_COLOR
# 5. CONTACT information
# =============================================================================


# =============================================================================
# 🏫 UNIVERSITY INFORMATION
# ⚠️  CHANGE THIS FOR NEW CLIENT/UNIVERSITY
# =============================================================================
UNIVERSITY_NAME = "Minhaj University Lahore"
UNIVERSITY_SHORT_NAME = "MUL"
UNIVERSITY_TAGLINE = "Excellence in Education"
UNIVERSITY_WEBSITE = "https://www.mul.edu.pk"
UNIVERSITY_LOGO_URL = "https://www.mul.edu.pk/images/logo.png"  # Logo URL

# =============================================================================
# 📞 CONTACT INFORMATION
# ⚠️  CHANGE THIS FOR NEW CLIENT/UNIVERSITY
# =============================================================================
CONTACT_EMAIL = "info@mul.edu.pk"
CONTACT_PHONE = "+92-42-35761999"
CONTACT_ADDRESS = "Township, Lahore, Pakistan"

# =============================================================================
# 🎨 UI BRANDING COLORS
# ⚠️  CHANGE THIS FOR NEW CLIENT/UNIVERSITY
# Hex color codes use karo
# =============================================================================
PRIMARY_COLOR = "#1E3A5F"      # Dark blue (MUL ka color)
SECONDARY_COLOR = "#C8A951"    # Gold/Yellow
ACCENT_COLOR = "#FFFFFF"       # White
BACKGROUND_COLOR = "#F4F7FB"   # Light gray background
TEXT_COLOR = "#2C2C2C"         # Dark text

# =============================================================================
# 🤖 CHATBOT IDENTITY
# ⚠️  CHANGE THIS FOR NEW CLIENT
# =============================================================================
BOT_NAME = "MUL Assistant"
BOT_EMOJI = "🎓"
BOT_DESCRIPTION = "AI-powered Information Assistant for Minhaj University Lahore"

# =============================================================================
# 📱 APP SETTINGS
# ⚠️  CHANGE TITLE AND ICON FOR NEW CLIENT
# =============================================================================
APP_TITLE = f"{BOT_EMOJI} {UNIVERSITY_SHORT_NAME} AI Assistant"
APP_SUBTITLE = f"Your intelligent guide to {UNIVERSITY_NAME}"
APP_ICON = "🎓"  # Streamlit page icon

# =============================================================================
# 💬 WELCOME MESSAGES
# ⚠️  CHANGE THESE FOR NEW CLIENT
# =============================================================================
WELCOME_MESSAGE = f"""
Welcome to **{UNIVERSITY_NAME}** AI Assistant! 🎓

I can help you with:
- 📚 Admissions information and eligibility
- 💰 Fee structures and scholarships
- 🏫 Available programs (BS, MS, PhD)
- 📋 Admission process and deadlines
- 📍 Campus facilities and contact info
- ❓ Any other university-related queries

**Ask me anything about {UNIVERSITY_SHORT_NAME}!**
"""

EXAMPLE_QUESTIONS = [
    "What are the admission requirements for BS Computer Science?",
    "What is the fee structure for BS AI?",
    "When does Spring 2026 admission open?",
    "What scholarships are available?",
    "What is the eligibility for MS programs?",
    "How can I contact the admission office?",
]

# =============================================================================
# 🏷️ FOOTER TEXT
# =============================================================================
FOOTER_TEXT = f"© 2024 {UNIVERSITY_NAME} | AI Assistant powered by RAG Technology"