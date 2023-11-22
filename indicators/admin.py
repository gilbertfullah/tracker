from django.contrib import admin
from .models import Indicator, IndicatorData, SatisfactionData, CitizenPrioritiesData, TrustInLocalAuthorities, NPSEResults, CommunityStability, BudgetAllocation, \
    BriberyReductionData, AnnualReportPublishedData, LocalOwnSourceRevenueData, AuditRecommendationsData, LCMisuseRevenueData, \
        AwarenessLCBudgetData, AwarenessLCProjectsData, JointAdvocacyInitiativesData



class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_per_page = 10





admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(IndicatorData)
admin.site.register(SatisfactionData)
admin.site.register(CitizenPrioritiesData)
admin.site.register(TrustInLocalAuthorities)
admin.site.register(NPSEResults)
admin.site.register(CommunityStability)
admin.site.register(BudgetAllocation)
admin.site.register(BriberyReductionData)
admin.site.register(AnnualReportPublishedData)
admin.site.register(LocalOwnSourceRevenueData)

admin.site.register(AuditRecommendationsData)
admin.site.register(LCMisuseRevenueData)
admin.site.register(AwarenessLCBudgetData)
admin.site.register(AwarenessLCProjectsData)
admin.site.register(JointAdvocacyInitiativesData)