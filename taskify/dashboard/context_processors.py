from .models import companyDetails

def company_context(request):
    """
    Context processor to add company details to all templates
    """
    try:
        company = companyDetails.get_instance()
        return {
            'company': company,
            'company_logo': company.company_logo,
            'company_name': company.company_name,
        }
    except Exception:
        # Return empty values if company details don't exist
        return {
            'company': None,
            'company_logo': None,
            'company_name': None,
        } 