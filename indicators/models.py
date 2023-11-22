from django.db import models
from schools.models import District, ServiceType
from django.utils import timezone


MEDIA_OUTLETS = (
        ('', 'Select a media outlet'),
        ('Notice Board', 'Notice Board'),
        ('Radio', 'Radio'),
        ('Local online news outlet', 'Local online news outlet'),
        ('Print Newspaper', 'Print Newspaper'),
        ('WhatsApp', 'WhatsApp'),
        ('Other Social Media', 'Other Social Media'),
        ('Other', 'Other'),
    )

ANSWER_CHOICE_TRUST = (
        ('', 'Select an answer'),
        ('A lot', 'A lot'),
        ('Somewhat', 'Somewhat'),
        ('Just a little', 'Just a little'),
        ('Not at all', 'Not at all'),
    )

ANSWER_CHOICE_COMM_STABILITY = (
        ('', 'Select an answer'),
        ('Very much', 'Very much'),
        ('Not at all', 'Not at all'),
    )

BRIBERY_SERVICES = (
        ('', 'Select a service'),
        ('Medical services', 'Medical services'),
        ('Public school', 'Public school'),
        ('Identity documents', 'Identity documents'),
    )

AGRI_SATISFACTION = (
        ('', 'Select a service'),
        ('Improved seeds supply', 'Improved seeds supply'),
        ('Training on farming techniques', 'Training on farming techniques'),
        ('Agricultural machines', 'Agricultural machines'),
        ('Fertilizers', 'Fertilizers'),
        ('Processing facilities', 'Processing facilities'),
        ('Advice on farming techniques', 'Advice on farming techniques'),
        ('Financial loans', 'Financial loans'),
    )
    
class Indicator(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Indicators"
    
    def __str__(self):
        return self.name
    
class IndicatorData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, null=True, blank=True)
    media_outlets = models.CharField(max_length=100, choices=MEDIA_OUTLETS, blank=True, null=True)
    answer_choice_trust = models.CharField(max_length=100, choices=ANSWER_CHOICE_TRUST, blank=True, null=True)
    answer_choice_comm_stability = models.CharField(max_length=100, choices=ANSWER_CHOICE_COMM_STABILITY, blank=True, null=True)
    bribery_services = models.CharField(max_length=100, choices=BRIBERY_SERVICES, blank=True, null=True)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Indicator Data"
    
    def __str__(self):
        return self.indicator.name
    
class SatisfactionData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True)
    satisfaction_services = models.CharField(max_length=100, choices=AGRI_SATISFACTION, blank=True, null=True)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Satisfaction Data"
    
    def __str__(self):
        return self.indicator.name
    

class CitizenPrioritiesData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    date_submitted = models.DateField(auto_now_add=False)
    
    class Meta:
        verbose_name_plural = "Citizen Priorities Data"
    
    def __str__(self):
        return self.indicator.name
    
class TrustInLocalAuthorities(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    answer_choice = models.CharField(max_length=100)
    indicator_value = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Trust In Local Authorities"
    
    def __str__(self):
        return self.indicator.name
    
class NPSEResults(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    indicator_value = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "NPSE Results"
    
    def __str__(self):
        return self.indicator.name

class CommunityStability(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    answer_choice = models.CharField(max_length=100)
    indicator_value = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Community Stability"
    
    def __str__(self):
        return self.indicator.name

class BudgetAllocation(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Budget Allocation"
    
    def __str__(self):
        return self.indicator.name
    
class BriberyReductionData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    services = models.CharField(max_length=100)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Bribery Reduction Data"
    
    def __str__(self):
        return self.indicator.name
    
class AnnualReportPublishedData(models.Model): 
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    media_outlets = models.CharField(max_length=100, choices=MEDIA_OUTLETS)
    indicator_value = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Annual Report Published Data"
    
    def __str__(self):
        return self.indicator.name

class LocalOwnSourceRevenueData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Local Own Source Revenue Data"
    
    def __str__(self):
        return self.indicator.name

class AuditRecommendationsData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Audit Recommendations Data"
    
    def __str__(self):
        return self.indicator.name
    
class LCMisuseRevenueData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "LC Misuse Revenue Data"
    
    def __str__(self):
        return self.indicator.name
    
class AwarenessLCBudgetData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Awareness LC Budget Data"
    
    def __str__(self):
        return self.indicator.name
    
class AwarenessLCProjectsData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    indicator_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Awareness LC Projects Data"
    
    def __str__(self):
        return self.indicator.name
    
class JointAdvocacyInitiativesData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    indicator_value = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("approved", "Approved")], default="pending")
    date_submitted = models.DateField(auto_now_add=False, default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Joint Advocacy Initiatives Data"
    
    def __str__(self):
        return self.indicator.name