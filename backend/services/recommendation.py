#it will tell us to what issue fix first
from dataclasses import dataclass
from enum import Enum

class Priority(Enum):
    CRITICLE="high"
    HIGH="high"
    MEDIUM="medium"
    LOW="low"
#priority.CRITICLE

@dataclass
class Recommendation:
    title:        str
    description:  str
    priority:     Priority
    impact_score: float
    category:     str
    action_items: list[str]

#genarate 0.1
def genarate_skill_recommendation(skill_validation_results:dict):
    unvalidated=skill_validation_results.get("unvalidated_skills",[])
    validation_pct=skill_validation_results.get("validation_percentage",0.0)
    recommendation=[]
    if not unvalidated:
        return recommendation
    if validation_pct<0.4:
        priority,impact=Priority.CRITICLE,8.0
    elif validation_pct<0.6:
        priority,impact=Priority.HIGH,0.6
    elif validation_pct<0.4:
        priority,impact=Priority.MEDIUM,0.4
    else:
        priority,impact=Priority.LOW,0..2

    action_items=[f"Add a projetc for '{skill}' or remove this skill "for skill in unvalidated[:5]]
    if len(unvalidated)>5:
        action_items.append(f"...and {len(unvalidated)-5} unvalidated skill(s)")

    recommendation.append(Recommendation(
         title        = 'Validate Your Listed Skills',
        description  = (
            f'{len(unvalidated)} skill(s) are not demonstrated in your projects or experience. '
            'ATS systems and recruiters look for evidence that you\'ve actually used the skills you claim.'
        ),
        priority     = priority,
        impact_score = impact,
        category     = 'skill_validation',
        action_items = action_items,
    ))

    return recommendation

#genrate 02:grammer suggestions
def genrate_grammer_suggestions(grammer_results:dict):
    recommeendations=[]

    critical_errors = grammer_results.get('critical_errors', [])
    moderate_errors = grammer_results.get('moderate_errors', [])
    minor_errors    = grammer_results.get('minor_errors', [])

    totle_errors=len(critical_errors)+len(moderate_errors)+len(minor_errors)

    if totle_errors==0:
        return recommeendations

    if critical_errors:
        items=[]
        for i in critical_errors[:5]:
            word=i.get("error_text","unknown")
            suggest=i.get("suggestions",[])
            suffix=f"-> '{suggest[0]}'" if suggest else ''
            items.append(f"Fix '{word}'{suffix}: {i.get('message', '')}")
        if len(critical_errors)>5:
            items.append(f'... and {len(critical_errors) - 5} more critical error(s)')

        recommeendations.append(Recommendation( title        = 'Fix Critical Spelling/Grammar Errors',
            description  = (
                f'{len(critical_errors)} critical error(s) found. These spelling mistakes or '
                'major grammar issues will make your resume look unprofessional.'
            ),
            priority     = Priority.CRITICAL,
            impact_score = min(10.0, len(critical_errors) * 2.0),
            category     = 'grammar',
            action_items = items))

    if moderate_errors:
        items=[]
        for i in moderate_errors[:5]:
            word=i.get("error_text","unknown")
            suggest=i.get("suggestions",[])
            suffix=f"-> '{suggest[0]}'" if suggest else ''
            items.append(f"Fix '{word}'{suffix}: {i.get('message', '')}")
        if len(moderate_errors)>5:
            items.append(f'... and {len(moderate_errors) - 5} more critical error(s)')
    
        recommeendations.append(Recommendation( title        = 'Address Punctuation and Capitalization Issues',
            description  = (
                f'{len(moderate_errors)} moderate error(s) found. '
                'These punctuation or capitalization issues should be corrected.'
            ),
            priority     = Priority.HIGH,
            impact_score = min(6.0, len(moderate_errors) * 1.0),
            category     = 'grammar',
            action_items = items,))
    if minor_errors and len(minor_errors)>=3:
        items=[]
        for i in minor_errors[:5]:
            word=i.get("error_text","unknown")
            suggest=i.get("suggestions",[])
            suffix=f"-> '{suggest[0]}'" if suggest else ''
            items.append(f"Fix '{word}'{suffix}: {i.get('message', '')}")
        if len(minor_errors)>5:
            items.append(f'... and {len(minor_errors) - 5} more critical error(s)')
    
        recommeendations.append(Recommendation(title = 'Consider Style Improvements',
            description  = (
                f'{len(minor_errors)} minor style suggestion(s) found. '
                'These are optional improvements for better readability.'
            ),
            priority     = Priority.LOW,
            impact_score = 1.0,
            category     = 'grammar',
            action_items = [
                f'Review {len(minor_errors)} style suggestion(s) for improved readability',
                'Use consistent formatting throughout',
            ],))
    return recommeendations