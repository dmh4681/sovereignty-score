#!/usr/bin/env python3
"""
AI Philosophy Agent - Sovereignty Wisdom Engine
Applies sovereignty principles and expert knowledge to user behavioral insights
"""

import os
import sys
import json
from datetime import datetime
from openai import OpenAI
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from behavior_insights_agent import BehavioralInsightsAgent
from assistant_utils import call_openai_assistant

class SovereigntyPhilosophyAgent:
    """
    Applies sovereignty principles and expert wisdom to behavioral insights
    to generate personalized philosophical guidance
    """
    
    def __init__(self, openai_api_key=None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Load sovereignty knowledge base
        self.sovereignty_principles = self._load_sovereignty_principles()
        self.expert_knowledge = self._load_expert_knowledge()
        self.path_philosophies = self._load_path_philosophies()
        
        # Create or get the Philosophy Assistant
        self.assistant_id = self._create_philosophy_assistant()
    
    def _load_sovereignty_principles(self):
        """Load core sovereignty principles and philosophies"""
        return {
            "core_principles": [
                "Personal sovereignty is built through daily discipline across multiple domains",
                "Health, wealth, and freedom are interconnected - weakness in one erodes the others",
                "Small, consistent actions compound into unshakeable autonomy over time",
                "True freedom comes from internal systems, not external circumstances",
                "Sovereignty is not selfish - it's the foundation for serving others powerfully",
                "Your body, mind, and resources are your last pieces of private property",
                "The exit is not external - it's internal. Build yourself into someone who can't be controlled",
                "Discipline today builds the freedom to choose tomorrow"
            ],
            "key_philosophies": {
                "time_preference": "Low time preference thinking - sacrifice immediate pleasure for long-term sovereignty",
                "anti_fragility": "Build systems that get stronger under stress, not just resilient",
                "skin_in_the_game": "Align your incentives with your values - put your own resources at risk",
                "via_negativa": "Often what you don't do matters more than what you do - eliminate the harmful",
                "compound_sovereignty": "Daily habits compound into life-changing systems over months and years",
                "first_principles": "Think from first principles, not conventional wisdom or social proof"
            },
            "sovereignty_mantras": [
                "Sovereignty is the new health plan",
                "You can't outrun the collapse, but you can outlast it",
                "Every meal, every workout, every investment is a vote for your freedom",
                "Build yourself into someone the system can't touch",
                "Health is wealth, wealth is freedom, freedom is sovereignty"
            ]
        }
    
    def _load_expert_knowledge(self):
        """Load expert knowledge from Huberman, Cavaliere, Pollan, Hyman"""
        return {
            "huberman_principles": [
                "Optimize circadian rhythms - light exposure and eating windows matter",
                "Stress + recovery cycles build resilience in mind and body",
                "Dopamine management is sovereignty - delay gratification for deeper satisfaction",
                "Morning sunlight and movement set the foundation for mental clarity",
                "Cold exposure and heat shock proteins build anti-fragility"
            ],
            "cavaliere_principles": [
                "Train like your life depends on it - because it does",
                "Consistency beats intensity - show up imperfectly rather than perfectly occasionally",
                "Progressive overload applies to all sovereignty domains, not just lifting",
                "Recovery is earned through work, not given through rest",
                "Your body is your first line of defense against an uncertain world"
            ],
            "pollan_principles": [
                "Eat food, not too much, mostly plants - simplicity is sovereignty",
                "Cook your own food - control your inputs, control your outcomes",
                "The dinner table is where culture and values are transmitted",
                "Real food connects you to the earth and breaks dependence on industrial systems",
                "Mindful eating is meditation in action"
            ],
            "hyman_principles": [
                "Food is medicine - every bite is either healing or harming",
                "Systemic health requires systemic thinking - body, environment, and society are connected",
                "Inflammation is the root of modern disease - choose anti-inflammatory living",
                "Environmental toxins steal sovereignty - minimize exposure, maximize detox",
                "Regenerative practices heal both personal and planetary health"
            ]
        }
    
    def _load_path_philosophies(self):
        """Load path-specific philosophical frameworks"""
        return {
            "default": {
                "philosophy": "Balanced sovereignty across all domains",
                "core_wisdom": "Master the fundamentals before advancing to specialization",
                "growth_approach": "Steady, sustainable progress across mind, body, and resources"
            },
            "financial_path": {
                "philosophy": "Bitcoin and minimalism as paths to economic sovereignty", 
                "core_wisdom": "Every dollar not spent on consumption is a vote for your future freedom",
                "growth_approach": "Aggressive saving, conservative living, long-term accumulation",
                "mantras": ["Stack sats, stay humble", "Live below your means, invest above your dreams"]
            },
            "mental_resilience": {
                "philosophy": "Inner strength as the foundation of all sovereignty",
                "core_wisdom": "A disciplined mind cannot be conquered by external chaos",
                "growth_approach": "Daily practices that build mental anti-fragility and clarity",
                "mantras": ["Still mind, strong heart", "Clarity is the ultimate currency"]
            },
            "physical_optimization": {
                "philosophy": "Physical sovereignty as the foundation for all other freedoms",
                "core_wisdom": "Your body is your most important asset - train it like one",
                "growth_approach": "Progressive overload in strength, nutrition, and recovery",
                "mantras": ["Strong body, sovereign life", "Train hard, live free"]
            },
            "spiritual_growth": {
                "philosophy": "Consciousness and presence as the deepest form of sovereignty",
                "core_wisdom": "True freedom is liberation from unconscious patterns and reactivity",
                "growth_approach": "Mindful practices that cultivate awareness and compassion",
                "mantras": ["Present moment, infinite possibilities", "Consciousness is sovereignty"]
            },
            "planetary_stewardship": {
                "philosophy": "Personal sovereignty aligned with planetary regeneration",
                "core_wisdom": "What heals the earth heals the self - sovereignty and sustainability are one",
                "growth_approach": "Regenerative practices that benefit both personal and environmental health",
                "mantras": ["Heal the soil, heal the soul", "Regenerative sovereignty"]
            }
        }
    
    def _create_philosophy_assistant(self):
        """Create or retrieve the OpenAI Philosophy Assistant"""
        
        assistant_instructions = f"""
You are the Sovereignty Philosophy Agent, a master of personal sovereignty principles and wisdom traditions. Your role is to take behavioral insights about users and apply deep sovereignty philosophy to generate personalized guidance.

CORE SOVEREIGNTY PRINCIPLES:
{json.dumps(self.sovereignty_principles, indent=2)}

EXPERT KNOWLEDGE BASE:
{json.dumps(self.expert_knowledge, indent=2)}

PATH-SPECIFIC PHILOSOPHIES:
{json.dumps(self.path_philosophies, indent=2)}

Your responses should:
1. Apply sovereignty principles to the user's specific behavioral patterns
2. Reference relevant expert knowledge (Huberman, Cavaliere, Pollan, Hyman)
3. Use path-specific philosophical frameworks
4. Generate wisdom that connects daily habits to larger sovereignty goals
5. Provide philosophical context for why certain changes matter
6. Create inspiring but grounded guidance rooted in sovereignty principles

Response format should be structured JSON with:
- philosophical_framework: Core philosophical approach for this user
- sovereignty_guidance: Specific sovereignty wisdom for their situation  
- expert_insights: Relevant expert knowledge applications
- path_wisdom: Path-specific philosophical guidance
- deeper_meaning: Connection between daily habits and larger sovereignty goals
- philosophical_challenges: Questions or challenges to deepen their practice
- sovereignty_mantras: Personal mantras aligned with their journey

Always ground philosophical wisdom in practical action while elevating the meaning and purpose behind sovereignty practices.
"""
        
        try:
            # Try to find existing assistant (you might want to store the ID)
            # For now, create a new one each time (in production, you'd store the ID)
            assistant = self.client.beta.assistants.create(
                name="Sovereignty Philosophy Agent",
                instructions=assistant_instructions,
                model="gpt-4o",
                tools=[]
            )
            
            return assistant.id
            
        except Exception as e:
            print(f"Error creating Philosophy Assistant: {e}")
            raise
    
    def generate_philosophical_guidance(self, username):
        """
        Generate personalized sovereignty philosophy guidance for a user
        
        Args:
            username (str): User to generate guidance for
            
        Returns:
            dict: Philosophical guidance and wisdom
        """
        print(f"🛡️ Generating sovereignty philosophy for {username}...")
        
        # Get behavioral insights first
        behavioral_agent = BehavioralInsightsAgent()
        behavioral_insights = behavioral_agent.analyze_user_psychology(username)
        
        if not behavioral_insights or "error" in behavioral_insights:
            return {"error": "Could not get behavioral insights"}
        
        # Prepare the philosophical analysis request
        analysis_request = self._prepare_philosophy_request(behavioral_insights)
        
        # Get philosophical guidance from AI
        try:
            philosophical_guidance = self._get_ai_philosophical_guidance(analysis_request)
            
            # Structure the complete philosophical analysis
            complete_guidance = {
                "user_profile": behavioral_insights["user_profile"],
                "behavioral_context": self._extract_key_behavioral_context(behavioral_insights),
                "philosophical_analysis": philosophical_guidance,
                "actionable_wisdom": self._generate_actionable_wisdom(philosophical_guidance, behavioral_insights),
                "sovereignty_roadmap": self._create_sovereignty_roadmap(philosophical_guidance, behavioral_insights),
                "timestamp": datetime.now().isoformat()
            }
            
            return complete_guidance
            
        except Exception as e:
            print(f"Error generating philosophical guidance: {e}")
            return {"error": str(e)}
    
    def _prepare_philosophy_request(self, behavioral_insights):
        """Prepare the request for AI philosophical analysis"""
        
        # Extract key information for philosophical analysis
        user_profile = behavioral_insights.get("user_profile", {})
        motivation = behavioral_insights.get("motivation_analysis", {})
        habits = behavioral_insights.get("habit_formation_phase", {})
        path_alignment = behavioral_insights.get("path_alignment", {})
        coaching_strategy = behavioral_insights.get("coaching_strategy", {})
        psychological_profile = behavioral_insights.get("psychological_profile", {})
        opportunities = behavioral_insights.get("growth_opportunities", [])
        risks = behavioral_insights.get("risk_assessment", [])
        
        request = f"""
USER SOVEREIGNTY ANALYSIS REQUEST

User Profile:
- Username: {user_profile.get('username', 'Unknown')}
- Path: {user_profile.get('path', 'Unknown')}
- Sovereignty Archetype: {psychological_profile.get('sovereignty_archetype', 'Unknown')}

Current State:
- Motivation State: {motivation.get('state', 'Unknown')}
- Habit Formation Phase: {habits.get('phase', 'Unknown')}
- Path Alignment: {path_alignment.get('overall_alignment', 0)}%
- Mastery Level: {path_alignment.get('mastery_level', 'Unknown')}

Coaching Context:
- Primary Need: {coaching_strategy.get('primary_need', 'Unknown')}
- Coaching Tone: {coaching_strategy.get('coaching_tone', 'Unknown')}
- Message Focus: {coaching_strategy.get('message_focus', 'Unknown')}

Growth Opportunities:
{json.dumps(opportunities, indent=2)}

Risk Assessment:
{json.dumps(risks, indent=2)}

Path Strengths: {path_alignment.get('path_strengths', [])}
Path Challenges: {path_alignment.get('path_challenges', [])}

Please provide sovereignty philosophy guidance that addresses this user's specific situation, applying the appropriate sovereignty principles and expert knowledge for their path and current state.
"""
        
        return request
    
    def _get_ai_philosophical_guidance(self, analysis_request):
        """Get philosophical guidance from OpenAI Assistant"""
        
        try:
            # Create a thread for this philosophical analysis
            thread = self.client.beta.threads.create()
            
            # Send the analysis request
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=analysis_request
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
                return {"raw_wisdom": response_content}
                
        except Exception as e:
            print(f"Error getting AI philosophical guidance: {e}")
            return {"error": str(e)}
    
    def _extract_key_behavioral_context(self, behavioral_insights):
        """Extract key behavioral context for philosophical analysis"""
        return {
            "motivation_state": behavioral_insights.get("motivation_analysis", {}).get("state"),
            "habit_phase": behavioral_insights.get("habit_formation_phase", {}).get("phase"),
            "sovereignty_archetype": behavioral_insights.get("psychological_profile", {}).get("sovereignty_archetype"),
            "primary_coaching_need": behavioral_insights.get("coaching_strategy", {}).get("primary_need"),
            "path_alignment_score": behavioral_insights.get("path_alignment", {}).get("overall_alignment", 0),
            "key_strengths": behavioral_insights.get("path_alignment", {}).get("path_strengths", []),
            "key_challenges": behavioral_insights.get("path_alignment", {}).get("path_challenges", [])
        }
    
    def _generate_actionable_wisdom(self, philosophical_guidance, behavioral_insights):
        """Generate actionable wisdom from philosophical guidance"""
        
        # Extract actionable items from philosophical guidance
        actionable_items = []
        
        # Get path-specific actions
        path = behavioral_insights.get("user_profile", {}).get("path", "default")
        path_philosophy = self.path_philosophies.get(path, {})
        
        # Add path-specific actionable wisdom
        if path == "financial_path":
            actionable_items.extend([
                "Set up automatic Bitcoin DCA to remove emotion from accumulation",
                "Track every expense for one week to identify sovereignty leaks",
                "Calculate the true cost of convenience purchases in future Bitcoin value"
            ])
        elif path == "spiritual_growth":
            actionable_items.extend([
                "Begin each day with 5 minutes of mindful breathing before checking devices",
                "Practice gratitude by listing 3 specific things each evening",
                "Take one daily action that benefits the environment as spiritual practice"
            ])
        elif path == "physical_optimization":
            actionable_items.extend([
                "Prioritize sleep as the foundation of all other sovereignty practices",
                "Plan and prep 3 meals at the start of each week",
                "Add 5 minutes to current workout duration to practice progressive overload"
            ])
        
        # Add coaching-specific actions based on primary need
        coaching_need = behavioral_insights.get("coaching_strategy", {}).get("primary_need")
        if coaching_need == "celebration":
            actionable_items.append("Share your sovereignty journey with one person who could benefit")
        elif coaching_need == "intervention":
            actionable_items.append("Choose one smallest possible sovereignty action and commit to it daily")
        elif coaching_need == "optimization":
            actionable_items.append("Identify your sovereignty bottleneck and focus 80% of energy there")
        
        return {
            "immediate_actions": actionable_items[:3],
            "weekly_practices": actionable_items[3:6] if len(actionable_items) > 3 else [],
            "monthly_challenges": actionable_items[6:] if len(actionable_items) > 6 else []
        }
    
    def _create_sovereignty_roadmap(self, philosophical_guidance, behavioral_insights):
        """Create a sovereignty development roadmap"""
        
        current_phase = behavioral_insights.get("habit_formation_phase", {}).get("phase", "formation")
        path = behavioral_insights.get("user_profile", {}).get("path", "default")
        
        roadmap = {
            "current_stage": current_phase,
            "next_milestone": self._determine_next_milestone(current_phase, behavioral_insights),
            "3_month_goals": self._generate_3_month_goals(path, current_phase),
            "12_month_vision": self._generate_12_month_vision(path, behavioral_insights),
            "sovereignty_principles_to_study": self._recommend_principles_study(behavioral_insights)
        }
        
        return roadmap
    
    def _determine_next_milestone(self, current_phase, behavioral_insights):
        """Determine the next milestone for this user"""
        if current_phase == "formation":
            return "Establish 30-day consistency in 2 core sovereignty practices"
        elif current_phase == "maintenance":
            return "Achieve 80%+ path alignment and build 3 concurrent habit streaks"
        elif current_phase == "mastery":
            return "Mentor others and develop advanced sovereignty protocols"
        elif current_phase == "erosion":
            return "Rebuild foundation with one non-negotiable daily practice"
        else:
            return "Define and commit to sovereignty north star"
    
    def _generate_3_month_goals(self, path, current_phase):
        """Generate 3-month sovereignty goals"""
        base_goals = [
            "Achieve 80%+ daily tracking consistency",
            "Build 30+ day streak in primary sovereignty practice",
            "Increase average sovereignty score by 15 points"
        ]
        
        path_specific_goals = {
            "financial_path": ["Accumulate 100,000+ sats", "Reduce monthly expenses by 15%"],
            "physical_optimization": ["Increase strength in compound movements", "Cook 90% of meals at home"],
            "spiritual_growth": ["Establish daily meditation practice", "Complete monthly environmental challenges"],
            "mental_resilience": ["Build stress resilience protocols", "Read 3 sovereignty-focused books"],
            "planetary_stewardship": ["Reduce personal carbon footprint by 20%", "Start regenerative practice"]
        }
        
        return base_goals + path_specific_goals.get(path, [])
    
    def _generate_12_month_vision(self, path, behavioral_insights):
        """Generate 12-month sovereignty vision"""
        mastery_level = behavioral_insights.get("path_alignment", {}).get("mastery_level", "Beginner")
        
        visions = {
            "financial_path": "Accumulate 1+ Bitcoin, reduce living expenses to <50% of income, build sovereign income streams",
            "physical_optimization": "Achieve advanced fitness markers, master meal prep systems, optimize recovery protocols",
            "spiritual_growth": "Maintain daily contemplative practice, integrate mindfulness into all activities, serve environmental healing",
            "mental_resilience": "Build anti-fragile mindset, master stress response, develop learning systems that compound",
            "planetary_stewardship": "Live regeneratively, influence others toward sustainability, heal local ecosystem",
            "default": "Achieve sovereignty across all domains, mentor others, build resilient systems for uncertain times"
        }
        
        base_vision = visions.get(path, visions["default"])
        
        if mastery_level in ["Advanced", "Master"]:
            base_vision += ", become a sovereignty teacher and system builder"
        
        return base_vision
    
    def _recommend_principles_study(self, behavioral_insights):
        """Recommend sovereignty principles to study"""
        coaching_need = behavioral_insights.get("coaching_strategy", {}).get("primary_need")
        path = behavioral_insights.get("user_profile", {}).get("path", "default")
        
        principles = []
        
        if coaching_need == "intervention":
            principles.extend(["Via negativa - what to eliminate", "Anti-fragility - growing stronger through stress"])
        elif coaching_need == "optimization":
            principles.extend(["Compound sovereignty", "Skin in the game"])
        else:
            principles.extend(["Low time preference thinking", "First principles reasoning"])
        
        # Add path-specific principles
        if path == "financial_path":
            principles.append("Austrian economics and sound money principles")
        elif path == "spiritual_growth":
            principles.append("Consciousness as the deepest sovereignty")
        
        return principles[:3]  # Limit to top 3

def main():
    """Test the Philosophy Agent with our test users"""
    print("🛡️  SOVEREIGNTY PHILOSOPHY AGENT")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        print("   You can add it to your .env file or set it in your environment.")
        return
    
    try:
        agent = SovereigntyPhilosophyAgent(api_key)
        print("✅ Philosophy Agent initialized successfully")
        
        # Test with one user first (test3 - the one with real email)
        username = "test3"
        print(f"\n🔍 Generating sovereignty philosophy for {username}...")
        
        guidance = agent.generate_philosophical_guidance(username)
        
        if guidance and "error" not in guidance:
            print(f"✅ Philosophical guidance generated for {username}")
            
            # Show key philosophical insights
            behavioral_context = guidance.get("behavioral_context", {})
            philosophical_analysis = guidance.get("philosophical_analysis", {})
            actionable_wisdom = guidance.get("actionable_wisdom", {})
            roadmap = guidance.get("sovereignty_roadmap", {})
            
            print(f"\n📊 BEHAVIORAL CONTEXT:")
            print(f"   🧠 Motivation: {behavioral_context.get('motivation_state', 'Unknown').title()}")
            print(f"   📈 Phase: {behavioral_context.get('habit_phase', 'Unknown').title()}")
            print(f"   🛡️  Archetype: {behavioral_context.get('sovereignty_archetype', 'Unknown').replace('_', ' ').title()}")
            print(f"   🎯 Path Alignment: {behavioral_context.get('path_alignment_score', 0):.0f}%")
            
            print(f"\n🛡️  PHILOSOPHICAL GUIDANCE:")
            if isinstance(philosophical_analysis, dict):
                for key, value in list(philosophical_analysis.items())[:3]:  # Show first 3 items
                    if isinstance(value, str):
                        print(f"   • {key.replace('_', ' ').title()}: {value[:100]}...")
                    elif isinstance(value, list):
                        print(f"   • {key.replace('_', ' ').title()}: {len(value)} insights")
            
            print(f"\n💡 ACTIONABLE WISDOM:")
            immediate = actionable_wisdom.get("immediate_actions", [])
            for i, action in enumerate(immediate[:3], 1):
                print(f"   {i}. {action}")
            
            print(f"\n🗺️  SOVEREIGNTY ROADMAP:")
            print(f"   🎯 Next Milestone: {roadmap.get('next_milestone', 'Not defined')}")
            print(f"   📅 12-Month Vision: {roadmap.get('12_month_vision', 'Not defined')[:80]}...")
            
        else:
            print(f"❌ Error generating guidance: {guidance.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error initializing Philosophy Agent: {e}")
        print("   Make sure you have OpenAI API key set and sufficient credits.")
    
    print(f"\n" + "=" * 60)
    print("🚀 Philosophy Agent testing complete!")
    print("Next: Email Composer Agent to turn this wisdom into beautiful coaching emails...")
    print("=" * 60)

if __name__ == "__main__":
    main()