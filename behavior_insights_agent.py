#!/usr/bin/env python3
"""
Behavioral Insights Agent - Sovereignty Score Psychology Engine
Interprets data patterns into psychological insights and coaching strategies
"""

import os
import sys
import json
from datetime import datetime, timedelta
from enum import Enum

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_intelligence_agent import DataIntelligenceAgent

class MotivationState(Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    BURNOUT = "burnout"
    REBUILDING = "rebuilding"

class HabitPhase(Enum):
    FORMATION = "formation"
    MAINTENANCE = "maintenance"
    MASTERY = "mastery"
    EROSION = "erosion"
    CRISIS = "crisis"

class CoachingNeed(Enum):
    CELEBRATION = "celebration"
    OPTIMIZATION = "optimization"
    COURSE_CORRECTION = "course_correction"
    INTERVENTION = "intervention"
    EDUCATION = "education"
    RE_ENGAGEMENT = "re_engagement"

class BehavioralInsightsAgent:
    """
    Interprets behavioral data patterns into psychological insights
    and actionable coaching strategies
    """
    
    def __init__(self):
        self.path_personalities = self._load_path_personalities()
        
    def _load_path_personalities(self):
        """Load expected behavioral patterns for each sovereignty path"""
        return {
            "default": {
                "core_values": ["balance", "consistency", "gradual_progress"],
                "key_activities": ["meditation", "home_cooked_meals", "read_or_learned"],
                "growth_indicators": ["score_improvement", "streak_building", "activity_diversity"],
                "risk_factors": ["weekend_drops", "inconsistent_logging", "low_engagement"]
            },
            "financial_path": {
                "core_values": ["discipline", "long_term_thinking", "accumulation"],
                "key_activities": ["invested_bitcoin", "no_spending", "read_or_learned"],
                "growth_indicators": ["investment_consistency", "spending_discipline", "learning_streaks"],
                "risk_factors": ["investment_gaps", "lifestyle_inflation", "short_term_thinking"]
            },
            "mental_resilience": {
                "core_values": ["inner_strength", "clarity", "emotional_regulation"],
                "key_activities": ["meditation", "gratitude", "read_or_learned"],
                "growth_indicators": ["meditation_consistency", "learning_engagement", "stress_management"],
                "risk_factors": ["meditation_gaps", "overwhelm_patterns", "mental_fatigue"]
            },
            "physical_optimization": {
                "core_values": ["strength", "performance", "longevity"],
                "key_activities": ["strength_training", "home_cooked_meals", "exercise_minutes"],
                "growth_indicators": ["workout_consistency", "nutrition_discipline", "recovery_balance"],
                "risk_factors": ["overtraining", "nutrition_lapses", "inconsistent_recovery"]
            },
            "spiritual_growth": {
                "core_values": ["presence", "meaning", "connection"],
                "key_activities": ["meditation", "gratitude", "environmental_action"],
                "growth_indicators": ["mindfulness_practice", "gratitude_consistency", "conscious_living"],
                "risk_factors": ["spiritual_bypassing", "disconnection", "lack_of_grounding"]
            },
            "planetary_stewardship": {
                "core_values": ["sustainability", "responsibility", "systems_thinking"],
                "key_activities": ["environmental_action", "home_cooked_meals", "no_spending"],
                "growth_indicators": ["environmental_consistency", "conscious_consumption", "systems_awareness"],
                "risk_factors": ["eco_anxiety", "perfectionism", "overwhelm"]
            }
        }
    
    def analyze_user_psychology(self, username):
        """
        Generate comprehensive psychological insights for a user
        
        Args:
            username (str): User to analyze
            
        Returns:
            dict: Psychological insights and coaching recommendations
        """
        print(f"🧠 Analyzing psychological patterns for {username}...")
        
        # Get data intelligence insights
        data_agent = DataIntelligenceAgent()
        data_insights = data_agent.analyze_user(username)
        
        if not data_insights or "error" in data_insights:
            return {"error": "Could not get data insights"}
        
        # Generate psychological analysis
        psychological_insights = {
            "user_profile": data_insights["user_profile"],
            "motivation_analysis": self._analyze_motivation_state(data_insights),
            "habit_formation_phase": self._analyze_habit_phase(data_insights),
            "behavioral_patterns": self._analyze_behavioral_patterns(data_insights),
            "path_alignment": self._analyze_path_alignment(data_insights),
            "psychological_profile": self._generate_psychological_profile(data_insights),
            "coaching_strategy": self._determine_coaching_strategy(data_insights),
            "intervention_priorities": self._identify_intervention_priorities(data_insights),
            "growth_opportunities": self._identify_growth_opportunities(data_insights),
            "risk_assessment": self._assess_behavioral_risks(data_insights),
            "timestamp": datetime.now().isoformat()
        }
        
        return psychological_insights
    
    def _analyze_motivation_state(self, data_insights):
        """Analyze current motivation and energy levels"""
        behavioral = data_insights.get("behavioral_insights", {})
        trend_analysis = data_insights.get("trend_analysis", {})
        data_summary = data_insights.get("data_summary", {})
        
        # Get motivation indicators
        motivation_level = behavioral.get("motivation_indicators", {}).get("level", "unknown")
        days_since_last = behavioral.get("days_since_last_entry", 0)
        score_trend = trend_analysis.get("score_trends", {}).get("trend_direction", "stable")
        avg_score = data_summary.get("score_stats", {}).get("average", 0)
        
        # Determine motivation state
        if days_since_last > 7:
            state = MotivationState.LOW
            indicators = ["Extended absence from tracking", "Possible disengagement"]
        elif motivation_level == "high" and score_trend == "improving":
            state = MotivationState.HIGH
            indicators = ["Strong recent performance", "Positive trajectory", "Active engagement"]
        elif avg_score < 25 and score_trend == "declining":
            state = MotivationState.BURNOUT
            indicators = ["Declining performance", "Possible overwhelm", "Need for reset"]
        elif score_trend == "improving" and avg_score < 40:
            state = MotivationState.REBUILDING
            indicators = ["Recovery in progress", "Building momentum", "Fragile but positive"]
        else:
            state = MotivationState.MODERATE
            indicators = ["Steady state", "Room for optimization", "Stable foundation"]
        
        return {
            "state": state.value,
            "confidence": self._calculate_confidence(data_insights),
            "indicators": indicators,
            "energy_level": self._assess_energy_level(data_insights),
            "burnout_risk": self._assess_burnout_risk(data_insights),
            "momentum": self._assess_momentum(data_insights)
        }
    
    def _analyze_habit_phase(self, data_insights):
        """Determine what phase of habit formation the user is in"""
        streak_analysis = data_insights.get("streak_analysis", {})
        data_summary = data_insights.get("data_summary", {})
        consistency = data_insights.get("consistency_patterns", {})
        
        total_days = data_summary.get("total_days", 0)
        avg_score = data_summary.get("score_stats", {}).get("average", 0)
        
        # Analyze streak patterns
        strong_streaks = sum(1 for activity, stats in streak_analysis.items() 
                           if stats.get("current_streak", 0) >= 14)
        
        # Determine phase
        if total_days < 30:
            phase = HabitPhase.FORMATION
            characteristics = ["Early stages", "Building foundation", "High variability expected"]
        elif avg_score >= 70 and strong_streaks >= 2:
            phase = HabitPhase.MASTERY
            characteristics = ["Advanced practitioner", "Sustainable systems", "Ready for optimization"]
        elif avg_score >= 50 and total_days >= 90:
            phase = HabitPhase.MAINTENANCE
            characteristics = ["Established routine", "Consistent performance", "Stable foundation"]
        elif avg_score < 35 or strong_streaks == 0:
            phase = HabitPhase.EROSION
            characteristics = ["Struggling with consistency", "Habits breaking down", "Needs intervention"]
        else:
            phase = HabitPhase.FORMATION
            characteristics = ["Building momentum", "Developing consistency", "Progress visible"]
        
        return {
            "phase": phase.value,
            "characteristics": characteristics,
            "stability_score": self._calculate_stability_score(data_insights),
            "time_in_phase": self._estimate_time_in_phase(data_insights, phase),
            "readiness_for_advancement": self._assess_advancement_readiness(data_insights)
        }
    
    def _analyze_behavioral_patterns(self, data_insights):
        """Identify key behavioral patterns and tendencies"""
        consistency = data_insights.get("consistency_patterns", {})
        streak_analysis = data_insights.get("streak_analysis", {})
        behavioral = data_insights.get("behavioral_insights", {})
        
        patterns = {
            "consistency_profile": {
                "weekday_strength": consistency.get("weekday_performance", {}).get("average_score", 0),
                "weekend_challenge": abs(consistency.get("weekend_drop", 0)) > 10,
                "overall_stability": behavioral.get("behavioral_stability", "unknown")
            },
            "activity_preferences": self._identify_activity_preferences(streak_analysis),
            "performance_patterns": {
                "peak_performance_indicators": self._identify_peak_patterns(data_insights),
                "struggle_indicators": self._identify_struggle_patterns(data_insights),
                "volatility_factors": self._identify_volatility_factors(data_insights)
            },
            "engagement_style": self._determine_engagement_style(data_insights)
        }
        
        return patterns
    
    def _analyze_path_alignment(self, data_insights):
        """Analyze how well user aligns with their chosen sovereignty path"""
        path = data_insights.get("user_profile", {}).get("path", "unknown")
        path_performance = data_insights.get("path_performance", {})
        streak_analysis = data_insights.get("streak_analysis", {})
        
        if path not in self.path_personalities:
            return {"error": f"Unknown path: {path}"}
        
        path_profile = self.path_personalities[path]
        
        # Analyze alignment with path-specific activities
        key_activities = path_profile["key_activities"]
        activity_performance = {}
        
        for activity in key_activities:
            if activity in streak_analysis:
                stats = streak_analysis[activity]
                activity_performance[activity] = {
                    "consistency_rate": stats.get("consistency_rate", 0),
                    "current_streak": stats.get("current_streak", 0),
                    "alignment_score": self._calculate_activity_alignment(stats, path)
                }
        
        overall_alignment = path_performance.get("path_alignment_score", 0)
        mastery_level = path_performance.get("path_mastery_level", "Unknown")
        
        return {
            "overall_alignment": overall_alignment,
            "mastery_level": mastery_level,
            "activity_performance": activity_performance,
            "path_strengths": self._identify_path_strengths(activity_performance, path_profile),
            "path_challenges": self._identify_path_challenges(activity_performance, path_profile),
            "alignment_trend": self._calculate_alignment_trend(data_insights),
            "path_optimization_opportunities": self._identify_path_optimization(activity_performance, path_profile)
        }
    
    def _generate_psychological_profile(self, data_insights):
        """Generate a psychological profile of the user"""
        motivation = self._analyze_motivation_state(data_insights)
        habits = self._analyze_habit_phase(data_insights)
        patterns = self._analyze_behavioral_patterns(data_insights)
        
        # Determine personality traits based on data
        traits = []
        
        if motivation["state"] == "high":
            traits.append("highly_motivated")
        if habits["phase"] in ["maintenance", "mastery"]:
            traits.append("disciplined")
        if patterns["consistency_profile"]["overall_stability"] == "stable":
            traits.append("consistent")
        
        # Determine coaching receptivity
        receptivity = "high" if motivation["state"] in ["high", "rebuilding"] else "moderate"
        if motivation["state"] == "burnout":
            receptivity = "low"
        
        return {
            "personality_traits": traits,
            "coaching_receptivity": receptivity,
            "learning_style": self._determine_learning_style(data_insights),
            "communication_preferences": self._determine_communication_preferences(data_insights),
            "change_readiness": self._assess_change_readiness(data_insights),
            "sovereignty_archetype": self._determine_sovereignty_archetype(data_insights)
        }
    
    def _determine_coaching_strategy(self, data_insights):
        """Determine the best coaching approach for this user"""
        motivation = self._analyze_motivation_state(data_insights)
        habits = self._analyze_habit_phase(data_insights)
        path_alignment = self._analyze_path_alignment(data_insights)
        
        # Determine primary coaching need
        if motivation["state"] == "burnout":
            primary_need = CoachingNeed.INTERVENTION
        elif motivation["state"] == "low":
            primary_need = CoachingNeed.RE_ENGAGEMENT
        elif habits["phase"] == "mastery":
            primary_need = CoachingNeed.OPTIMIZATION
        elif path_alignment.get("overall_alignment", 0) < 50:
            primary_need = CoachingNeed.COURSE_CORRECTION
        elif motivation["state"] == "high":
            primary_need = CoachingNeed.CELEBRATION
        else:
            primary_need = CoachingNeed.EDUCATION
        
        return {
            "primary_need": primary_need.value,
            "coaching_tone": self._determine_coaching_tone(motivation, habits),
            "message_focus": self._determine_message_focus(data_insights, primary_need),
            "urgency_level": self._determine_urgency_level(motivation, habits),
            "recommended_frequency": self._recommend_email_frequency(motivation, habits),
            "success_metrics": self._define_success_metrics(primary_need, data_insights)
        }
    
    def _identify_intervention_priorities(self, data_insights):
        """Identify what needs immediate attention"""
        priorities = []
        
        motivation = self._analyze_motivation_state(data_insights)
        behavioral = data_insights.get("behavioral_insights", {})
        streak_analysis = data_insights.get("streak_analysis", {})
        
        # High priority interventions
        if motivation["state"] == "burnout":
            priorities.append({
                "priority": "critical",
                "area": "motivation_recovery",
                "action": "Reduce pressure, focus on small wins, rebuild foundation"
            })
        
        if behavioral.get("days_since_last_entry", 0) > 5:
            priorities.append({
                "priority": "high",
                "area": "re_engagement",
                "action": "Gentle reminder to return to tracking, identify barriers"
            })
        
        # Medium priority interventions
        broken_streaks = [activity for activity, stats in streak_analysis.items() 
                         if stats.get("longest_streak", 0) > 14 and stats.get("current_streak", 0) == 0]
        
        if broken_streaks:
            priorities.append({
                "priority": "medium",
                "area": "streak_recovery",
                "action": f"Help rebuild {', '.join(broken_streaks)} consistency"
            })
        
        return priorities
    
    def _identify_growth_opportunities(self, data_insights):
        """Identify areas where user can grow and improve"""
        opportunities = []
        
        streak_analysis = data_insights.get("streak_analysis", {})
        path_alignment = self._analyze_path_alignment(data_insights)
        habits = self._analyze_habit_phase(data_insights)
        
        # Streak building opportunities
        for activity, stats in streak_analysis.items():
            consistency_rate = stats.get("consistency_rate", 0)
            if 30 <= consistency_rate <= 70:  # Room for improvement
                opportunities.append({
                    "type": "habit_strengthening",
                    "area": activity,
                    "potential": f"Increase {activity} consistency from {consistency_rate:.0f}% to 80%+"
                })
        
        # Path alignment opportunities
        if path_alignment.get("overall_alignment", 0) < 80:
            opportunities.append({
                "type": "path_optimization",
                "area": "sovereignty_alignment",
                "potential": "Deeper alignment with chosen sovereignty path"
            })
        
        # Phase advancement opportunities
        if habits["readiness_for_advancement"]:
            opportunities.append({
                "type": "level_advancement",
                "area": "sovereignty_mastery",
                "potential": f"Ready to advance from {habits['phase']} to next level"
            })
        
        return opportunities
    
    def _assess_behavioral_risks(self, data_insights):
        """Assess risks to long-term sovereignty journey"""
        risks = []
        
        motivation = self._analyze_motivation_state(data_insights)
        consistency = data_insights.get("consistency_patterns", {})
        behavioral = data_insights.get("behavioral_insights", {})
        
        # Burnout risk
        if motivation["burnout_risk"] > 0.7:
            risks.append({
                "risk": "burnout",
                "severity": "high",
                "indicators": ["High burnout risk detected", "Unsustainable pace"],
                "mitigation": "Reduce intensity, focus on sustainability"
            })
        
        # Consistency risk
        weekend_drop = abs(consistency.get("weekend_drop", 0))
        if weekend_drop > 20:
            risks.append({
                "risk": "weekend_consistency",
                "severity": "medium",
                "indicators": [f"{weekend_drop:.0f} point weekend drop"],
                "mitigation": "Develop weekend-specific strategies"
            })
        
        # Engagement risk
        if behavioral.get("behavioral_stability") == "volatile":
            risks.append({
                "risk": "inconsistent_engagement",
                "severity": "medium",
                "indicators": ["High score volatility", "Unpredictable patterns"],
                "mitigation": "Identify stability factors, create routine anchors"
            })
        
        return risks
    
    # Helper methods for calculations
    def _calculate_confidence(self, data_insights):
        """Calculate confidence in the motivation assessment"""
        total_days = data_insights.get("data_summary", {}).get("total_days", 0)
        if total_days < 30:
            return "low"
        elif total_days < 90:
            return "medium"
        else:
            return "high"
    
    def _assess_energy_level(self, data_insights):
        """Assess user's current energy level"""
        recent_scores = data_insights.get("trend_analysis", {}).get("score_trends", {}).get("recent_average", 0)
        if recent_scores > 70:
            return "high"
        elif recent_scores > 45:
            return "moderate"
        else:
            return "low"
    
    def _assess_burnout_risk(self, data_insights):
        """Calculate burnout risk score"""
        volatility = data_insights.get("behavioral_insights", {}).get("score_volatility", 0)
        trend = data_insights.get("trend_analysis", {}).get("score_trends", {}).get("trend_direction", "stable")
        
        risk = 0.0
        if volatility > 25:
            risk += 0.3
        if trend == "declining":
            risk += 0.4
        
        return min(risk, 1.0)
    
    def _assess_momentum(self, data_insights):
        """Assess current momentum"""
        trend_direction = data_insights.get("trend_analysis", {}).get("score_trends", {}).get("trend_direction", "stable")
        improvement = data_insights.get("trend_analysis", {}).get("score_trends", {}).get("improvement", 0)
        
        if trend_direction == "improving" and improvement > 5:
            return "strong_positive"
        elif trend_direction == "improving":
            return "positive"
        elif trend_direction == "declining":
            return "negative"
        else:
            return "neutral"
    
    def _calculate_stability_score(self, data_insights):
        """Calculate how stable the user's habits are"""
        volatility = data_insights.get("behavioral_insights", {}).get("score_volatility", 0)
        return max(0, 100 - volatility)
    
    def _estimate_time_in_phase(self, data_insights, phase):
        """Estimate how long user has been in current phase"""
        total_days = data_insights.get("data_summary", {}).get("total_days", 0)
        # This is simplified - in a real system you'd analyze trend changes
        return f"~{min(total_days, 90)} days"
    
    def _assess_advancement_readiness(self, data_insights):
        """Assess if user is ready to advance to next phase"""
        avg_score = data_insights.get("data_summary", {}).get("score_stats", {}).get("average", 0)
        streak_count = sum(1 for stats in data_insights.get("streak_analysis", {}).values() 
                          if stats.get("current_streak", 0) >= 7)
        
        return avg_score > 60 and streak_count >= 2
    
    def _identify_activity_preferences(self, streak_analysis):
        """Identify which activities user excels at"""
        preferences = {"strengths": [], "challenges": []}
        
        for activity, stats in streak_analysis.items():
            consistency = stats.get("consistency_rate", 0)
            if consistency > 70:
                preferences["strengths"].append(activity)
            elif consistency < 30:
                preferences["challenges"].append(activity)
        
        return preferences
    
    def _identify_peak_patterns(self, data_insights):
        """Identify when user performs best"""
        weekday_avg = data_insights.get("consistency_patterns", {}).get("weekday_performance", {}).get("average_score", 0)
        weekend_avg = data_insights.get("consistency_patterns", {}).get("weekend_performance", {}).get("average_score", 0)
        
        if weekday_avg > weekend_avg + 10:
            return ["Strong weekday performance"]
        elif weekend_avg > weekday_avg + 10:
            return ["Strong weekend performance"]
        else:
            return ["Consistent across week"]
    
    def _identify_struggle_patterns(self, data_insights):
        """Identify when user struggles most"""
        weekend_drop = data_insights.get("consistency_patterns", {}).get("weekend_drop", 0)
        if weekend_drop > 15:
            return ["Weekend performance drops", "May need weekend-specific strategies"]
        return []
    
    def _identify_volatility_factors(self, data_insights):
        """Identify what causes performance volatility"""
        volatility = data_insights.get("behavioral_insights", {}).get("score_volatility", 0)
        if volatility > 20:
            return ["High score variability", "Inconsistent routine factors"]
        return ["Stable performance patterns"]
    
    def _determine_engagement_style(self, data_insights):
        """Determine how user engages with the system"""
        days_since_last = data_insights.get("behavioral_insights", {}).get("days_since_last_entry", 0)
        total_days = data_insights.get("data_summary", {}).get("total_days", 0)
        
        if days_since_last <= 1:
            return "highly_engaged"
        elif days_since_last <= 3:
            return "regularly_engaged"
        elif total_days > 200:
            return "long_term_user"
        else:
            return "sporadic_user"
    
    def _calculate_activity_alignment(self, stats, path):
        """Calculate how well an activity aligns with the user's path"""
        # This could be more sophisticated based on path-specific weightings
        return min(stats.get("consistency_rate", 0), 100)
    
    def _identify_path_strengths(self, activity_performance, path_profile):
        """Identify user's strengths within their path"""
        strengths = []
        for activity in path_profile["key_activities"]:
            if activity in activity_performance:
                perf = activity_performance[activity]
                if perf.get("alignment_score", 0) > 70:
                    strengths.append(f"Strong {activity} consistency")
        return strengths
    
    def _identify_path_challenges(self, activity_performance, path_profile):
        """Identify user's challenges within their path"""
        challenges = []
        for activity in path_profile["key_activities"]:
            if activity in activity_performance:
                perf = activity_performance[activity]
                if perf.get("alignment_score", 0) < 40:
                    challenges.append(f"Inconsistent {activity} practice")
        return challenges
    
    def _calculate_alignment_trend(self, data_insights):
        """Calculate if path alignment is improving or declining"""
        # Simplified - would analyze alignment over time
        trend_direction = data_insights.get("trend_analysis", {}).get("score_trends", {}).get("trend_direction", "stable")
        return trend_direction
    
    def _identify_path_optimization(self, activity_performance, path_profile):
        """Identify optimization opportunities within the path"""
        opportunities = []
        for activity in path_profile["key_activities"]:
            if activity in activity_performance:
                perf = activity_performance[activity]
                consistency = perf.get("consistency_rate", 0)
                if 50 <= consistency <= 80:
                    opportunities.append(f"Optimize {activity} from {consistency:.0f}% to 85%+")
        return opportunities
    
    def _determine_learning_style(self, data_insights):
        """Determine how user best learns and receives information"""
        read_learned_stats = data_insights.get("streak_analysis", {}).get("read_or_learned", {})
        if read_learned_stats.get("consistency_rate", 0) > 60:
            return "information_seeker"
        else:
            return "action_oriented"
    
    def _determine_communication_preferences(self, data_insights):
        """Determine preferred communication style"""
        path = data_insights.get("user_profile", {}).get("path", "unknown")
        motivation_state = self._analyze_motivation_state(data_insights)["state"]
        
        if path == "spiritual_growth":
            return "philosophical_reflective"
        elif path == "financial_path":
            return "data_driven_practical"
        elif motivation_state == "low":
            return "gentle_encouraging"
        else:
            return "direct_motivational"
    
    def _assess_change_readiness(self, data_insights):
        """Assess how ready user is for changes/challenges"""
        motivation = self._analyze_motivation_state(data_insights)
        habits = self._analyze_habit_phase(data_insights)
        
        if motivation["state"] == "high" and habits["phase"] in ["maintenance", "mastery"]:
            return "high"
        elif motivation["state"] in ["moderate", "rebuilding"]:
            return "moderate"
        else:
            return "low"
    
    def _determine_sovereignty_archetype(self, data_insights):
        """Determine user's sovereignty archetype based on behavior"""
        path = data_insights.get("user_profile", {}).get("path", "unknown")
        mastery_level = data_insights.get("path_performance", {}).get("path_mastery_level", "Beginner")
        streak_analysis = data_insights.get("streak_analysis", {})
        
        strong_activities = [activity for activity, stats in streak_analysis.items() 
                           if stats.get("consistency_rate", 0) > 70]
        
        if mastery_level == "Master" and len(strong_activities) >= 4:
            return "sovereignty_master"
        elif path == "financial_path" and "invested_bitcoin" in strong_activities:
            return "financial_sovereign"
        elif path == "physical_optimization" and "strength_training" in strong_activities:
            return "physical_sovereign"
        elif path == "spiritual_growth" and "meditation" in strong_activities:
            return "spiritual_sovereign"
        elif len(strong_activities) >= 2:
            return "emerging_sovereign"
        else:
            return "sovereignty_seeker"
    
    def _determine_coaching_tone(self, motivation, habits):
        """Determine appropriate coaching tone"""
        if motivation["state"] == "burnout":
            return "gentle_supportive"
        elif motivation["state"] == "high" and habits["phase"] == "mastery":
            return "challenging_growth"
        elif motivation["state"] == "rebuilding":
            return "encouraging_rebuilding"
        else:
            return "motivational_direct"
    
    def _determine_message_focus(self, data_insights, primary_need):
        """Determine what the message should focus on"""
        if primary_need == CoachingNeed.CELEBRATION:
            return "achievements_and_progress"
        elif primary_need == CoachingNeed.INTERVENTION:
            return "support_and_reset"
        elif primary_need == CoachingNeed.OPTIMIZATION:
            return "next_level_challenges"
        elif primary_need == CoachingNeed.COURSE_CORRECTION:
            return "realignment_and_refocus"
        else:
            return "education_and_inspiration"
    
    def _determine_urgency_level(self, motivation, habits):
        """Determine how urgent the coaching intervention is"""
        if motivation["state"] == "burnout":
            return "high"
        elif motivation["state"] == "low":
            return "medium"
        else:
            return "low"
    
    def _recommend_email_frequency(self, motivation, habits):
        """Recommend how often to send coaching emails"""
        if motivation["state"] == "high":
            return "weekly"
        elif motivation["state"] == "low":
            return "bi_weekly"
        else:
            return "weekly"
    
    def _define_success_metrics(self, primary_need, data_insights):
        """Define what success looks like for this coaching intervention"""
        if primary_need == CoachingNeed.RE_ENGAGEMENT:
            return ["Return to daily tracking", "Score improvement", "Streak rebuilding"]
        elif primary_need == CoachingNeed.OPTIMIZATION:
            return ["Score increase by 10+ points", "New streak milestones", "Advanced habit adoption"]
        elif primary_need == CoachingNeed.INTERVENTION:
            return ["Stabilized tracking", "Reduced volatility", "Improved motivation indicators"]
        elif primary_need == CoachingNeed.CELEBRATION:
            return ["Continued momentum", "Inspiration to others", "Next level goal setting"]
        else:
            return ["Increased engagement", "Improved path alignment", "Knowledge application"]

def main():
    """Test the Behavioral Insights Agent with our test users"""
    print("🧠 SOVEREIGNTY BEHAVIORAL INSIGHTS AGENT")
    print("=" * 60)
    
    agent = BehavioralInsightsAgent()
    
    # Test with our test users
    test_users = ["test3", "test_planetary", "test_physical", "test_financial"]
    
    for username in test_users:
        print(f"\n🔍 Analyzing psychological patterns for {username}...")
        insights = agent.analyze_user_psychology(username)
        
        if insights and "error" not in insights:
            print(f"✅ Psychological analysis complete for {username}")
            
            # Show key psychological insights
            motivation = insights.get("motivation_analysis", {})
            habits = insights.get("habit_formation_phase", {})
            coaching = insights.get("coaching_strategy", {})
            profile = insights.get("psychological_profile", {})
            path_alignment = insights.get("path_alignment", {})
            
            print(f"   🧠 Motivation State: {motivation.get('state', 'Unknown').title()}")
            print(f"   📈 Habit Phase: {habits.get('phase', 'Unknown').title()}")
            print(f"   🎯 Path Alignment: {path_alignment.get('overall_alignment', 0):.0f}%")
            print(f"   🏆 Mastery Level: {path_alignment.get('mastery_level', 'Unknown')}")
            print(f"   🤖 Sovereignty Archetype: {profile.get('sovereignty_archetype', 'Unknown').replace('_', ' ').title()}")
            print(f"   💌 Coaching Need: {coaching.get('primary_need', 'Unknown').replace('_', ' ').title()}")
            print(f"   🗣️  Coaching Tone: {coaching.get('coaching_tone', 'Unknown').replace('_', ' ').title()}")
            
            # Show intervention priorities
            priorities = insights.get("intervention_priorities", [])
            if priorities:
                print(f"   🚨 Priority Interventions:")
                for priority in priorities[:2]:  # Show top 2
                    print(f"      • {priority['priority'].title()}: {priority['area'].replace('_', ' ').title()}")
            
            # Show growth opportunities
            opportunities = insights.get("growth_opportunities", [])
            if opportunities:
                print(f"   🌱 Growth Opportunities:")
                for opp in opportunities[:2]:  # Show top 2
                    print(f"      • {opp['type'].replace('_', ' ').title()}: {opp['area'].replace('_', ' ').title()}")
            
            # Show risk assessment
            risks = insights.get("risk_assessment", [])
            if risks:
                print(f"   ⚠️  Behavioral Risks:")
                for risk in risks[:2]:  # Show top 2
                    print(f"      • {risk['risk'].replace('_', ' ').title()} ({risk['severity']})")
        else:
            print(f"❌ Error analyzing {username}: {insights.get('error', 'Unknown error')}")
    
    print(f"\n" + "=" * 60)
    print("🚀 Behavioral Insights Agent testing complete!")
    print("This psychological analysis will feed the AI Philosophy and Email Composer agents...")
    print("=" * 60)

if __name__ == "__main__":
    main()