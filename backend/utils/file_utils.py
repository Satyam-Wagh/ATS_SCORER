class FileParsingError(Exception):
    pass
class TextExtractionError(Exception):
    pass
class FileUploadError(Exception):
    pass

def get_default_grammar_results():
    return {
        'total_errors':         0,
        'critical_errors':      [],
        'moderate_errors':      [],
        'minor_errors':         [],
        'grammar_score':        100,
        'penalty_applied':      0,
        'error_free_percentage': 100,
        '_component_status':    'unavailable',
        '_note': 'Grammar checking unavailable.'
    }

def get_default_location_results():
    return {
        'location_found':     False,
        'detected_locations': [],
        'privacy_risk':       'unknown',
        'recommendations':    ['Location detection unavailable.'],
        'penalty_applied':    0,
        '_component_status':  'unavailable',
        '_note': 'Location detection unavailable.'
    }