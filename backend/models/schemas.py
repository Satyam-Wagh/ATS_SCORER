from pydantic import BaseModel

class IssueDetails(BaseModel):
    issue_title: str
    severity_level: str
    ats_impact: str
    explanation: str
    where_it_appears: str
    how_to_fix: str
    action_items: list[str] = []
    example_improvement: str

class ComponentScores(BaseModel):
    formatting: float
    keywords: float
    content: float
    skill_validation: float
    ats_compatibility: float

class JDComparison(BaseModel):
    match_percentage: float
    semantic_similarity: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    #skills_gap: list[str]
class SkillValidationDetails(BaseModel):
    validated: list[dict] = []       # [{'skill': str, 'projects': [str]}]
    unvalidated: list[str] = []                # ['Flask', 'A/B Testing', ...]
    total: int = 0
    validated_count: int = 0
    validation_pct: float = 0.0

class AnalysisResponse(BaseModel):
    ATS_score: float
    component_scores: ComponentScores
    issues_summary: list[str]
    detailed_feedback: list[IssueDetails]
    jd_match_analysis: None
    skill_validation_details: None

    ats_score: float
    keyword_match: float = 0.0
    missing_keywords: list[str] = []
    matched_keywords: list[str] = []
    suggestions: list[str] = []
    strengths: list[str] = []
    critical_issues: list[str] = []
    skills: list[str] = []
    jd_comparison: None
    warnings: list[str] = []
    #interpretation: str = ""