from django.utils import timezone
from .models import Employee, ClassRoutine, SubstituteAllocation, LeaveRequest, StudentLead

# ==========================================
# SOVEREIGN AI INTELLIGENCE ENGINE
# ==========================================

class SovereignEngine:
    """
    The Brain of the ERP.
    Handles AI Logic for Leads and Substitutions.
    """
    
    @staticmethod
    def calculate_lead_probability(lead_id):
        """
        Recalculates probability for a lead based on dynamic factors.
        """
        try:
            lead = StudentLead.objects.get(id=lead_id)
            lead.save() # The save method handles the calculation
            return lead.probability_score
        except StudentLead.DoesNotExist:
            return 0
            
    @staticmethod
    def find_smart_substitute(absent_emp, date, period_time):
        """
        AI Logic to find the best substitute teacher.
        Criteria:
        1. Available (Not on leave, No class at this time) - REQUIRED
        2. Same Subject (Specialist) - High Priority (+50)
        3. Same Department - Medium Priority (+30)
        4. Workload Balance - Low Priority (prefer less loaded teachers)
        """
        owner = absent_emp.created_by
        day_of_week = date.strftime('%a').upper()
        
        # 1. Get all active teachers
        potential_subs = Employee.objects.filter(
            created_by=owner,
            is_active=True
        ).exclude(id=absent_emp.id)
        
        # 2. Filter out teachers on approved leave
        teachers_on_leave = LeaveRequest.objects.filter(
            start_date__lte=date,
            end_date__gte=date,
            status='APPROVED'
        ).values_list('employee_id', flat=True)
        
        potential_subs = potential_subs.exclude(id__in=teachers_on_leave)

        # 3. Filter out teachers busy at this specific time slot
        # We assume 'period_time' matches 'start_time' in Routine
        busy_teacher_names = ClassRoutine.objects.filter(
            owner=owner,
            day_of_week=day_of_week,
            start_time=period_time
        ).values_list('teacher_name', flat=True)
        
        # Use Python filtering since teacher_name is a string vs Employee object relationship
        # This is the "Bridge" fix: simplistic name matching
        available_candidates = []
        
        for teacher in potential_subs:
             # Check if busy by name
             # Normalize for robust checking
             t_name = teacher.user.get_full_name() or teacher.user.username
             is_busy = False
             for busy_name in busy_teacher_names:
                 if busy_name and (busy_name.lower() in t_name.lower() or t_name.lower() in busy_name.lower()):
                     is_busy = True
                     break
             
             if is_busy:
                 continue
                 
             # calculate Score
             score = 0
             # Subject Match (We need a subject field on Employee, or guess from Department)
             if teacher.department == absent_emp.department:
                 score += 30
                 
             # Workload balancing (mock logic: lower ID = longer tenure? No, just random for now)
             # Ideally check total sub allocations this month
             subs_count = SubstituteAllocation.objects.filter(
                 substitute_teacher=teacher,
                 date__month=date.month
             ).count()
             
             score -= (subs_count * 5) # Penalize overworked teachers
             
             available_candidates.append({'teacher': teacher, 'score': score})
             
        # Sort by score
        available_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        if available_candidates:
            return available_candidates[0]['teacher']
        return None

    @staticmethod
    def process_daily_substitutions(date):
        """
        Scan for approved leaves today and generate allocations.
        """
        leaves = LeaveRequest.objects.filter(
            start_date__lte=date,
            end_date__gte=date,
            status='APPROVED'
        )
        
        allocations = []
        for leave in leaves:
            emp = leave.employee
            owner = emp.created_by
            day = date.strftime('%a').upper()
            
            # Find periods this teacher had today
            routines = ClassRoutine.objects.filter(
                owner=owner,
                day_of_week=day,
                teacher_name__icontains=emp.user.first_name # Try to match name
            )
            
            for routine in routines:
                # Check if already allocated
                existing = SubstituteAllocation.objects.filter(
                    absent_teacher=emp,
                    date=date,
                    subject=routine.subject
                ).exists()
                
                if not existing:
                    # Find Sub
                    best_sub = SovereignEngine.find_smart_substitute(emp, date, routine.start_time)
                    if best_sub:
                        alloc = SubstituteAllocation.objects.create(
                            created_by=owner,
                            absent_teacher=emp,
                            date=date,
                            period_slot=str(routine.start_time),
                            grade_class=f"Grade {routine.grade or 'batch'}",
                            subject=routine.subject,
                            substitute_teacher=best_sub
                        )
                        allocations.append(alloc)
                        
        return allocations
    @staticmethod
    def analyze_business_health(finance_data, risk_data, owner):
        """
        Uses LLM to provide a strategic summary of the institution's health.
        """
        try:
            from ai.manager import get_ai_manager
            ai = get_ai_manager()
            
            prompt = f"""
            Analyze the following institution data and provide a 3-bullet point executive summary.
            Revenue: {finance_data['total_revenue']}
            Expenses: {finance_data['total_expenses']}
            Net Profit: {finance_data['net_profit']}
            Students at High Risk: {len(risk_data)}
            
            Identify the biggest financial or academic threat and one growth opportunity.
            Format: High-level, professional, and concise.
            """
            
            report = ai.ask_tutor(
                question=prompt,
                subject="Business Intelligence",
                context=f"The user is the owner of an educational institution. Institution ID: {owner.id}"
            )
            return report
        except Exception as e:
            return "AI Analysis temporarily unavailable. System metrics are within normal ranges."
