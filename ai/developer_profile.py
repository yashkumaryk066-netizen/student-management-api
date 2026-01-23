"""
Developer Profile Configuration
Centralized profile information for AI system identity
"""

DEVELOPER_PROFILE = {
    "name": "Yash A Mishra",
    "full_name": "Yash Ankush Mishra",
    "title": "Advanced Software Architect & Developer",
    "company": "Telepathy Infotech",
    "position": "Software Developer",
    "education": {
        "degree": "BCA (Bachelor of Computer Applications)",
        "university": "Bhagalpur University",
        "completion_year": "2024",
        "period": "2021-2024"
    },
    "personal": {
        "dob": "30/05/2004",
        "age": 21,  # Calculated as of 2026
        "location": "India"
    },
    "professional": {
        "expertise": [
            "Full-Stack Web Development",
            "AI Integration & System Architecture",
            "Educational Technology Solutions",
            "Python & Django Backend",
            "React & Modern Frontend",
            "Database Design & Optimization"
        ],
        "projects": [
            "Y.S.M Advanced Education System",
            "AI-Powered Student Management Platform",
            "Multi-Provider AI Integration System"
        ],
        "skills": [
            "Python", "Django", "JavaScript", "React",
            "AI Integration", "System Architecture",
            "Database Management", "API Development"
        ]
    },
    "contact": {
        "profile_image": "/static/images/yash_profile.jpg",
        "profile_image_alt": "Yash Ankush Mishra - Developer"
    },
    "social": {
        "github": "yashkumaryk066",
        "project_repo": "student-management-api"
    }
}

def get_developer_profile():
    """Get complete developer profile"""
    return DEVELOPER_PROFILE

def get_profile_summary():
    """Get formatted profile summary for AI context"""
    profile = DEVELOPER_PROFILE
    return f"""
**Developer: {profile['name']}**
- **Position:** {profile['position']} at {profile['company']}
- **Education:** {profile['education']['degree']} from {profile['education']['university']}
- **Date of Birth:** {profile['personal']['dob']}
- **Expertise:** {', '.join(profile['professional']['expertise'][:3])}
- **Profile Image:** {profile['contact']['profile_image']}
"""

def get_profile_for_identity_query():
    """Get formatted profile for 'Who created you?' type queries"""
    profile = DEVELOPER_PROFILE
    return f"""
# 🎯 About My Creator

![Developer Profile]({profile['contact']['profile_image']})

## 👨‍💻 {profile['full_name']}

**Professional Identity:**
- 💼 **Current Role:** {profile['position']} at **{profile['company']}**
- 🎓 **Education:** {profile['education']['degree']} from **{profile['education']['university']}** ({profile['education']['period']})
- 🎂 **Date of Birth:** {profile['personal']['dob']}

**Technical Expertise:**
{chr(10).join([f'- ✨ {skill}' for skill in profile['professional']['expertise']])}

**Notable Projects:**
{chr(10).join([f'- 🚀 {project}' for project in profile['professional']['projects']])}

---

**Yash A Mishra** is an advanced software developer specializing in educational technology and AI integration. He created the **Y.S.M Advanced Education System** - a comprehensive platform that leverages cutting-edge AI to revolutionize student management and learning experiences.

His vision combines modern software architecture with intelligent automation to make education more accessible, efficient, and personalized.
"""

# Quick access functions
def get_developer_name():
    return DEVELOPER_PROFILE['name']

def get_developer_company():
    return DEVELOPER_PROFILE['company']

def get_developer_education():
    return f"{DEVELOPER_PROFILE['education']['degree']} from {DEVELOPER_PROFILE['education']['university']}"

def get_profile_image():
    return DEVELOPER_PROFILE['contact']['profile_image']
