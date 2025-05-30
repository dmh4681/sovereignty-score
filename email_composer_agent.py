#!/usr/bin/env python3
"""
Email Composer Agent - Sovereignty Coaching Email Creator
Creates personalized coaching emails from behavioral insights and philosophical guidance
"""

import os
import sys
import json
from datetime import datetime
from openai import OpenAI
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_philosophy_agent import SovereigntyPhilosophyAgent

class EmailComposerAgent:
    """
    Creates compelling, personalized sovereignty coaching emails
    from behavioral insights and philosophical guidance
    """
    
    def __init__(self, openai_api_key=None, mailgun_api_key=None, mailgun_domain=None):
        # OpenAI setup
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Mailgun setup (optional for testing)
        self.mailgun_api_key = mailgun_api_key or os.getenv("MAILGUN_API_KEY")
        self.mailgun_domain = mailgun_domain or os.getenv("MAILGUN_DOMAIN")
        
        # Email templates and styles
        self.email_styles = self._load_email_styles()
        self.subject_line_templates = self._load_subject_templates()
        
        # Create Email Composer Assistant
        self.assistant_id = self._create_email_composer_assistant()
    
    def _load_email_styles(self):
        """Load email styling and tone configurations"""
        return {
            "gentle_supportive": {
                "tone": "warm, understanding, non-judgmental",
                "language": "encouraging, soft, patient",
                "approach": "meet them where they are, small steps, compassion"
            },
            "challenging_growth": {
                "tone": "direct, inspiring, high-energy",
                "language": "powerful, action-oriented, confident",
                "approach": "push boundaries, next level thinking, ambitious goals"
            },
            "motivational_direct": {
                "tone": "energetic, clear, motivating",
                "language": "straightforward, inspiring, practical",
                "approach": "clear action steps, motivational stories, achievable goals"
            },
            "philosophical_reflective": {
                "tone": "thoughtful, deep, contemplative",
                "language": "philosophical, meaningful, introspective",
                "approach": "deeper meaning, spiritual insights, consciousness expansion"
            },
            "data_driven_practical": {
                "tone": "logical, evidence-based, systematic",
                "language": "precise, analytical, results-focused",
                "approach": "metrics, strategies, optimization, clear ROI"
            },
            "encouraging_rebuilding": {
                "tone": "hopeful, patient, rebuilding-focused",
                "language": "resilient, comeback-oriented, foundation-building",
                "approach": "fresh start, learning from setbacks, sustainable progress"
            }
        }
    
    def _load_subject_templates(self):
        """Load subject line templates by coaching type"""
        return {
            "celebration": [
                "🏆 Your sovereignty streak is inspiring, {name}",
                "🔥 {streak_count} days strong - you're building something special",
                "✨ Your {path} mastery is showing, {name}",
                "🛡️ Sovereignty update: You're crushing it"
            ],
            "optimization": [
                "🚀 Ready for the next level, {name}?",
                "⚡ Your sovereignty foundation is solid - time to build up",
                "🎯 Advanced {path} protocols unlocked",
                "🧠 You've mastered the basics - here's what's next"
            ],
            "course_correction": [
                "🗺️ Recalibrating your sovereignty compass, {name}",
                "🛡️ Getting back on the sovereignty path",
                "⚖️ Realigning with your {path} values",
                "🎯 Course correction: Your sovereignty matters too much to drift"
            ],
            "intervention": [
                "💙 Sovereignty check-in: How are you really doing, {name}?",
                "🌅 Every sovereign warrior needs a reset sometimes",
                "🛡️ Your sovereignty journey isn't over - it's just paused",
                "💪 Rebuilding sovereignty, one small step at a time"
            ],
            "education": [
                "🧠 The sovereignty principle that changed everything",
                "📚 New insights for your {path} journey",
                "🔍 The hidden connection between {habit} and freedom",
                "💡 Sovereignty science: Why {topic} matters"
            ],
            "re_engagement": [
                "🛡️ Your sovereignty score misses you, {name}",
                "⚡ Ready to reclaim your sovereignty momentum?",
                "🎯 The {path} community needs leaders like you",
                "🌟 Your comeback story starts now"
            ]
        }
    
    def _create_email_composer_assistant(self):
        """Create the Email Composer OpenAI Assistant"""
        
        assistant_instructions = f"""
You are the Sovereignty Email Composer Agent, a master of crafting compelling, personalized coaching emails that inspire action and build sovereignty.

Your role is to take behavioral insights and philosophical guidance and create beautiful, actionable coaching emails that:

1. **Connect personally** - Reference specific user data and patterns
2. **Inspire philosophically** - Apply sovereignty principles meaningfully  
3. **Drive action** - Include clear, achievable next steps
4. **Build momentum** - Celebrate progress and create motivation for more
5. **Match tone perfectly** - Adapt communication style to user psychology

EMAIL STYLE GUIDELINES:
{json.dumps(self.email_styles, indent=2)}

SOVEREIGNTY BRAND VOICE:
- Direct but not preachy
- Philosophical but practical  
- Inspiring but grounded
- Personal but not overly familiar
- Confident but not arrogant
- Encouraging but not patronizing

STRUCTURAL ELEMENTS:
- **Hook:** Compelling opening that connects to their specific situation
- **Recognition:** Acknowledge their progress and/or challenges authentically
- **Wisdom:** Apply relevant sovereignty principles to their context
- **Action:** 2-3 specific, achievable steps aligned with their path
- **Vision:** Connect daily actions to larger sovereignty goals
- **Momentum:** End with energy and motivation to continue

Your response should be a JSON object with:
- subject_line: Compelling subject that would make them want to open
- email_body: Complete email in plain text (no HTML)
- tone_used: The primary tone/style applied
- key_themes: Main themes emphasized in the email
- call_to_action: Primary action you want them to take
- follow_up_suggestion: When/how to follow up based on their response

Always write emails that feel personal, meaningful, and actionable - emails that someone would actually want to read and would inspire them to take sovereignty-building action.
"""
        
        try:
            assistant = self.client.beta.assistants.create(
                name="Sovereignty Email Composer",
                instructions=assistant_instructions,
                model="gpt-4o",
                tools=[]
            )
            
            return assistant.id
            
        except Exception as e:
            print(f"Error creating Email Composer Assistant: {e}")
            raise
    
    def compose_coaching_email(self, username, user_email=None):
        """
        Compose a personalized coaching email for a user
        
        Args:
            username (str): User to compose email for
            user_email (str): User's email address (optional, for sending)
            
        Returns:
            dict: Complete email composition with metadata
        """
        print(f"✉️ Composing sovereignty coaching email for {username}...")
        
        # Get philosophical guidance first
        philosophy_agent = SovereigntyPhilosophyAgent(self.openai_api_key)
        philosophical_guidance = philosophy_agent.generate_philosophical_guidance(username)
        
        if not philosophical_guidance or "error" in philosophical_guidance:
            return {"error": "Could not get philosophical guidance"}
        
        # Prepare email composition request
        composition_request = self._prepare_email_request(philosophical_guidance, username)
        
        # Get email composition from AI
        try:
            email_composition = self._get_ai_email_composition(composition_request)
            
            # Structure the complete email package
            complete_email = {
                "user_profile": philosophical_guidance["user_profile"],
                "email_composition": email_composition,
                "philosophical_context": self._extract_email_context(philosophical_guidance),
                "email_ready_for_send": self._format_for_sending(email_composition, username, user_email),
                "metadata": {
                    "composed_at": datetime.now().isoformat(),
                    "coaching_type": philosophical_guidance.get("behavioral_context", {}).get("primary_coaching_need"),
                    "user_archetype": philosophical_guidance.get("behavioral_context", {}).get("sovereignty_archetype"),
                    "path": philosophical_guidance.get("user_profile", {}).get("path")
                }
            }
            
            return complete_email
            
        except Exception as e:
            print(f"Error composing email: {e}")
            return {"error": str(e)}
    
    def _prepare_email_request(self, philosophical_guidance, username):
        """Prepare the email composition request"""
        
        # Extract key context for email composition
        user_profile = philosophical_guidance.get("user_profile", {})
        behavioral_context = philosophical_guidance.get("behavioral_context", {})
        philosophical_analysis = philosophical_guidance.get("philosophical_analysis", {})
        actionable_wisdom = philosophical_guidance.get("actionable_wisdom", {})
        roadmap = philosophical_guidance.get("sovereignty_roadmap", {})
        
        request = f"""
SOVEREIGNTY COACHING EMAIL COMPOSITION REQUEST

User Context:
- Username: {username}
- Path: {user_profile.get('path', 'Unknown')}
- Motivation State: {behavioral_context.get('motivation_state', 'Unknown')}
- Habit Phase: {behavioral_context.get('habit_phase', 'Unknown')}
- Sovereignty Archetype: {behavioral_context.get('sovereignty_archetype', 'Unknown')}
- Primary Coaching Need: {behavioral_context.get('primary_coaching_need', 'Unknown')}
- Path Alignment Score: {behavioral_context.get('path_alignment_score', 0)}%

Key Strengths: {behavioral_context.get('key_strengths', [])}
Key Challenges: {behavioral_context.get('key_challenges', [])}

Philosophical Guidance Summary:
{json.dumps(philosophical_analysis, indent=2) if isinstance(philosophical_analysis, dict) else str(philosophical_analysis)[:500]}

Immediate Actions Recommended:
{json.dumps(actionable_wisdom.get('immediate_actions', []), indent=2)}

Sovereignty Roadmap:
- Next Milestone: {roadmap.get('next_milestone', 'Not defined')}
- 12-Month Vision: {roadmap.get('12_month_vision', 'Not defined')}

Please compose a personalized sovereignty coaching email that:
1. Acknowledges their specific situation and progress authentically
2. Applies relevant sovereignty philosophy to their context
3. Provides clear, actionable next steps aligned with their path
4. Inspires them to continue their sovereignty journey
5. Uses the appropriate tone for their psychological state

The email should feel personal, meaningful, and actionable - something that would genuinely help and motivate this specific person on their sovereignty path.
"""
        
        return request
    
    def _get_ai_email_composition(self, composition_request):
        """Get email composition from OpenAI Assistant"""
        
        try:
            # Create a thread for email composition
            thread = self.client.beta.threads.create()
            
            # Send the composition request
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=composition_request
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            while True:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id, 
                    run_id=run.id
                )
                if run.status == "completed":
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Assistant run failed with status: {run.status}")
                time.sleep(1)
            
            # Get the response
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            response_content = messages.data[0].content[0].text.value
            
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(response_content)
            except json.JSONDecodeError:
                # If not JSON, structure it manually
                return {
                    "subject_line": "Your sovereignty journey continues",
                    "email_body": response_content,
                    "tone_used": "motivational_direct",
                    "key_themes": ["sovereignty_building"],
                    "call_to_action": "Continue daily sovereignty tracking",
                    "follow_up_suggestion": "Follow up in 1 week to check progress"
                }
                
        except Exception as e:
            print(f"Error getting AI email composition: {e}")
            return {"error": str(e)}
    
    def _extract_email_context(self, philosophical_guidance):
        """Extract key context for email metadata"""
        return {
            "motivation_state": philosophical_guidance.get("behavioral_context", {}).get("motivation_state"),
            "coaching_need": philosophical_guidance.get("behavioral_context", {}).get("primary_coaching_need"),
            "path_alignment": philosophical_guidance.get("behavioral_context", {}).get("path_alignment_score"),
            "sovereignty_archetype": philosophical_guidance.get("behavioral_context", {}).get("sovereignty_archetype"),
            "key_focus_areas": philosophical_guidance.get("behavioral_context", {}).get("key_challenges", [])
        }
    
    def _format_for_sending(self, email_composition, username, user_email=None):
        """Format the email for actual sending"""
        
        if not isinstance(email_composition, dict):
            return {"error": "Invalid email composition format"}
        
        subject = email_composition.get("subject_line", "Your sovereignty journey continues")
        body = email_composition.get("email_body", "")
        
        # Add sovereignty signature
        body += "\n\n" + "─" * 50
        body += "\n🛡️ **Stay Sovereign,**"
        body += "\n*The Sovereignty Score Team*"
        body += "\n\n*P.S. - Remember: Sovereignty is the new health plan. Every choice you make today builds the freedom you'll enjoy tomorrow.*"
        body += "\n\n📊 Track your progress: [Return to your Sovereignty Dashboard](http://localhost:8501)"
        
        return {
            "to_email": user_email or "test@example.com",
            "subject": subject,
            "body": body,
            "sender": f"Sovereignty Score Coach <coach@{self.mailgun_domain}>" if self.mailgun_domain else "coach@sovereigntyscore.com",
            "ready_to_send": bool(user_email and self.mailgun_api_key and self.mailgun_domain)
        }
    
    def send_email(self, email_package, test_mode=True):
        """
        Send the composed email via Mailgun
        
        Args:
            email_package (dict): Complete email package from compose_coaching_email
            test_mode (bool): If True, just shows what would be sent without sending
            
        Returns:
            dict: Send result
        """
        
        email_ready = email_package.get("email_ready_for_send", {})
        
        if not email_ready.get("ready_to_send", False):
            return {
                "status": "not_ready",
                "message": "Email not ready to send - missing email address or Mailgun config",
                "email_preview": email_ready
            }
        
        if test_mode:
            return {
                "status": "test_mode",
                "message": "Test mode - email not actually sent",
                "email_preview": {
                    "to": email_ready["to_email"],
                    "subject": email_ready["subject"],
                    "body_preview": email_ready["body"][:200] + "..."
                }
            }
        
        # Actually send via Mailgun
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                auth=("api", self.mailgun_api_key),
                data={
                    "from": email_ready["sender"],
                    "to": email_ready["to_email"],
                    "subject": email_ready["subject"],
                    "text": email_ready["body"],
                    "h:Reply-To": email_ready["sender"],
                    "o:tracking": "yes",
                    "o:tracking-clicks": "yes",
                    "o:tracking-opens": "yes"
                }
            )
            
            if response.status_code == 200:
                return {
                    "status": "sent",
                    "message": "Email sent successfully!",
                    "mailgun_response": response.json()
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Failed to send email: {response.status_code}",
                    "error": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error sending email: {str(e)}"
            }

def main():
    """Test the Email Composer Agent"""
    print("✉️ SOVEREIGNTY EMAIL COMPOSER AGENT")
    print("=" * 60)
    
    # Check for API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    mailgun_key = os.getenv("MAILGUN_API_KEY")
    mailgun_domain = os.getenv("MAILGUN_DOMAIN")
    
    if not openai_key:
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        return
    
    try:
        agent = EmailComposerAgent(openai_key, mailgun_key, mailgun_domain)
        print("✅ Email Composer Agent initialized successfully")
        
        # Test with test3 (the one with real email for testing)
        username = "test3"
        test_email = "your-email@example.com"  # Replace with real email for testing
        
        print(f"\n📝 Composing personalized coaching email for {username}...")
        
        email_package = agent.compose_coaching_email(username, test_email)
        
        if email_package and "error" not in email_package:
            print(f"✅ Email composition complete!")
            
            # Show email composition details
            composition = email_package.get("email_composition", {})
            email_ready = email_package.get("email_ready_for_send", {})
            metadata = email_package.get("metadata", {})
            
            print(f"\n📊 EMAIL METADATA:")
            print(f"   🎯 Coaching Type: {metadata.get('coaching_type', 'Unknown').replace('_', ' ').title()}")
            print(f"   🛡️  User Archetype: {metadata.get('user_archetype', 'Unknown').replace('_', ' ').title()}")
            print(f"   📈 Path: {metadata.get('path', 'Unknown').replace('_', ' ').title()}")
            
            print(f"\n✉️ EMAIL COMPOSITION:")
            print(f"   📧 Subject: {composition.get('subject_line', 'No subject')}")
            print(f"   🗣️  Tone: {composition.get('tone_used', 'Unknown').replace('_', ' ').title()}")
            print(f"   🎯 Call to Action: {composition.get('call_to_action', 'No CTA')}")
            print(f"   📅 Follow-up: {composition.get('follow_up_suggestion', 'No follow-up')}")
            
            # Show email preview
            print(f"\n📄 EMAIL PREVIEW:")
            print("─" * 60)
            print(f"To: {email_ready.get('to_email', 'No email')}")
            print(f"Subject: {email_ready.get('subject', 'No subject')}")
            print("─" * 60)
            email_body = email_ready.get('body', 'No body')
            print(email_body[:500] + "..." if len(email_body) > 500 else email_body)
            print("─" * 60)
            
            # Test sending (in test mode)
            print(f"\n📤 Testing email send...")
            send_result = agent.send_email(email_package, test_mode=True)
            print(f"   Status: {send_result.get('status', 'Unknown')}")
            print(f"   Message: {send_result.get('message', 'No message')}")
            
            if send_result.get('status') == 'test_mode':
                print("\n💡 To actually send emails:")
                print("   1. Replace test_email with real email address")
                print("   2. Ensure Mailgun API key and domain are configured")
                print("   3. Set test_mode=False in send_email call")
        
        else:
            print(f"❌ Error composing email: {email_package.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error initializing Email Composer Agent: {e}")
    
    print(f"\n" + "=" * 60)
    print("🚀 Email Composer Agent testing complete!")
    print("Your complete AI Sovereignty Coaching System is now ready! 🛡️")
    print("=" * 60)

if __name__ == "__main__":
    main()