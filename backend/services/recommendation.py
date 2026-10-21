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
#generator03: location recommendations
def generate_location_recommendations(location_detail:dict):
    recommendations    = []
    detected_locations = location_results.get('detected_locations', [])
    privacy_risk       = location_results.get('privacy_risk', 'none')

    if privacy_risk == 'none' or not detected_locations:
        return recommendations

    addresses = [loc for loc in detected_locations if loc.get('type') == 'address']
    zip_codes = [loc for loc in detected_locations if loc.get('type') == 'zip']

    action_items = []
    for addr in addresses[:2]:
        action_items.append(f"Remove full address: '{addr.get('text', '')}'")

    for z in zip_codes[:2]:
        action_items.append(f"Remove zip code: '{z.get('text', '')}'")
    action_items.append("Keep only 'City, State' in your contact header")

    if privacy_risk == 'high':
        priority    = Priority.CRITICAL
        impact      = 5.0
        description = (
            'Your resume contains detailed location information that poses a privacy risk. '
            'Full addresses and zip codes are unnecessary and can be used to identify your location.'
        )
    elif privacy_risk == 'medium':
        priority    = Priority.HIGH
        impact      = 3.0
        description = (
            "Your resume contains multiple location mentions. Consider simplifying to just "
            "'City, State' in your contact header."
        )
    else:
        priority    = Priority.MEDIUM
        impact      = 2.0
        description = (
            'Minor location information detected. Consider reviewing for unnecessary location details.'
        )

    recommendations.append(Recommendation(
        title        = 'Protect Your Location Privacy',
        description  = description,
        priority     = priority,
        impact_score = impact,
        category     = 'location',
        action_items = action_items,
    ))
    return recommendations
#generator05: formatting and structure recommendations
def generate_formating_recommendation(score:dict,section:dict):
    recommendations=[]
    formating_score=score.get("formating_score",0.0)

    section_recommendations={  'experience': "Add a clear 'Experience' or 'Work History' section",
        'education':  "Add an 'Education' section with your qualifications",
        'skills':     "Add a 'Skills' section listing your technical and soft skills",
        'summary':    "Consider adding a 'Summary' or 'Objective' section at the top",
        'projects':   "Consider adding a 'Projects' section to showcase your work",}
    missing_sections=[]
    for k,v in section_recommendations.items():
        content=section.get(k,'')
        if not content or len(content)<20:
            missing_sections.append((k,v))

    core_missing=[(k,v) for k,v in missing_sections if k in ['experience', 'education', 'skills']]
    optional_missing=[(k,v) for k,v in missing_sections if k in ['summary', 'projects']]

    if core_missing:
        recommendations.append(Recommendation(title        = 'Consider Adding Optional Sections',
            description  = 'Adding a summary and projects section can strengthen your resume.',
            priority     = Priority.LOW,
            impact_score = 2.0,
            category     = 'formatting',
            action_items = [suggestion for _, suggestion in optional_missing]))

    if optional_missing and formating_score<15:
        recommendations.append(Recommendation(title        = 'Consider Adding Optional Sections',
            description  = 'Adding a summary and projects section can strengthen your resume.',
            priority     = Priority.LOW,
            impact_score = 2.0,
            category     = 'formatting',
            action_items = [suggestion for _, suggestion in optional_missing]))
    if formating_score<12:
        recommendations.append(Recommendation(
              title        = 'Improve Resume Structure',
            description  = (
                f'Your formatting score is {formatting_score:.1f}/20. '
                'Better structure will improve ATS parsing and readability.'
            ),
            priority     = Priority.HIGH,
            impact_score = 5.0,
            category     = 'formatting',
            action_items = [
                'Use bullet points to list achievements and responsibilities',
                'Add clear section headers (Experience, Education, Skills)',
                'Ensure consistent formatting throughout',
                'Use a clean, single-column layout',
            ]
        ))
    return recommendations

def _prioritize_recommendations(recommendations:list[Recommendation]):
    priority_order = {
        Priority.CRITICAL: 0,
        Priority.HIGH:     1,
        Priority.MEDIUM:   2,
        Priority.LOW:      3,
    }
    return sorted(recommendations,key=lambda r:(priority_order[r.priority],-r.impact_score))

#main function
def genrate_recommendations(
    skill_validation_results: dict,
    grammar_results: dict,
    location_results: dict,
    score_results: dict,
    sections: dict[str, str],):
    all_records=[]

    all_records.extend(genarate_skill_recommendation(skill_validation_results))
    all_records.extend(generate_formating_recommendation(score_results,sections))
    all_records.extend(generate_location_recommendations(location_detail=location_results))
    all_records.extend(genrate_grammer_suggestions(grammar_results))

    priotized=_prioritize_recommendations(all_records)

    critical=[i for i in priotized if i.priority==Priority.CRITICAL]
    high=[i for i in priotized if i.priority== Priority.HIGH]
    medium=[i for i in priotized if i.priority==  Priority.MEDIUM]
    low=[i for i in priotized if i.priority==  Priority.LOW]

    return {
        'all_recommendations':      priotized,
        'critical_recommendations': critical,
        'high_recommendations':     high,
        'medium_recommendations':   medium,
        'low_recommendations':      low,
        'total_count':              len(priotized),
       # 'estimated_improvement':    estimated_improvement,
    }

def genrate_recommendation_summary(recommendation_result:dict):
    totle=recommendation_result.get("total_count",0)
    critical=len(recommendation_result.get("critical_recommendations",[]))
    high=len(recommendation_result.get("high_recommendations"))
    medium=len(recommendation_result.get("medium_recommendations"))

    if totle==0:
        return 'Excellent! No major recommendations. Your resume is well-optimized.'

    if critical>0:
        return  f'Found {totle} recommendation(s) including {critical} critical issue(s). '
    elif high>0:
        return  f'Found {totle} recommendation(s) including {high} high issue(s). '
    else:
        return  f'Found {totle} recommendation(s)'