def ai_health_check_controller():
    """Health check endpoint for AI service"""
    return {
        "status":"healthy",
        "message":"AI service is running"
    }