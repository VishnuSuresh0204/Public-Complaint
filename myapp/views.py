from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import *
# Create your views here.

def index(request):
    return render(request, "index.html")


def register_public(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # Prevent duplicate username
        if Login.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("/register")

        try:
            login_obj = Login.objects.create_user(
                username=username,
                password=password,
                userType="citizen",
                viewPass=password
            )
        except:
            messages.error(request, "Error creating account. Try again.")
            return redirect("/register")

        # Create Citizen profile
        Citizen.objects.create(
            loginid=login_obj,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect("/login")

    return render(request, "user_register.html")

def register_staff(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        dept_id = request.POST.get("department")

        if Login.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("/register_staff")

        login_obj = Login.objects.create_user(
            username=username,
            password=password,
            userType="staff",
            viewPass=password
        )

        department = Department.objects.get(id=dept_id)

        Staff.objects.create(
            loginid=login_obj,
            name=request.POST.get("name"),
            department=department,
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            profile_pic=request.FILES.get("profile_pic"),
            status="pending"
        )

        messages.success(request, "Staff registered successfully.")
        return redirect("/login")

    departments = Department.objects.all()
    return render(request, "staff_register.html", {
        "departments": departments
    })


def register_worker(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        dept_id = request.POST.get("department")

        if Login.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("/register_worker")

        login_obj = Login.objects.create_user(
            username=username,
            password=password,
            userType="worker",
            viewPass=password
        )

        department = Department.objects.get(id=dept_id)

        Worker.objects.create(
            loginid=login_obj,
            name=request.POST.get("name"),
            department=department,
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            profile_pic=request.FILES.get("profile_pic"),
            status="pending"
        )

        messages.success(request, "Worker registered successfully. Please wait for admin approval.")
        return redirect("/login")

    departments = Department.objects.all()
    return render(request, "worker_register.html", {
        "departments": departments
    })


def login_view(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            messages.error(request, "Invalid username or password")
            return redirect("/login")

        # ================= ADMIN LOGIN =================
        if user.userType == "admin":
            login(request, user)
            request.session["aid"] = user.id
            return redirect("/admin_home")

        # ================= STAFF LOGIN =================
        if user.userType == "staff":
            try:
                staff = Staff.objects.get(loginid=user)
                if staff.status == "blocked":
                    messages.error(request, "Your account has been blocked. Please contact administrator.")
                    return redirect("/login")
                if staff.status != "active":
                    messages.error(request, "Staff account not approved yet or rejected.")
                    return redirect("/login")
            except Staff.DoesNotExist:
                messages.error(request, "Staff profile not found")
                return redirect("/login")

            login(request, user)
            request.session["sid"] = user.id
            return redirect("/staff_home")

        # ================= CITIZEN LOGIN =================
        if user.userType == "citizen":
            try:
                citizen = Citizen.objects.get(loginid=user)
                if citizen.status == "blocked":
                    messages.error(request, "Your account has been blocked. Please contact administrator.")
                    return redirect("/login")
                if citizen.status != "active":
                    messages.error(request, "Account is not active.")
                    return redirect("/login")
            except Citizen.DoesNotExist:
                messages.error(request, "Citizen profile not found")
                return redirect("/login")

            login(request, user)
            request.session["cid"] = user.id
            return redirect("/citizen_home")

        # ================= WORKER LOGIN =================
        if user.userType == "worker":
            try:
                worker = Worker.objects.get(loginid=user)
                if worker.status == "blocked":
                    messages.error(request, "Your account has been blocked. Please contact administrator.")
                    return redirect("/login")
                if worker.status != "active":
                    messages.error(request, "Worker account not approved yet or rejected.")
                    return redirect("/login")
            except Worker.DoesNotExist:
                messages.error(request, "Worker profile not found")
                return redirect("/login")

            login(request, user)
            request.session["wid"] = user.id
            return redirect("/worker_home")

        # ================= INVALID USER =================
        messages.error(request, "Invalid account type")
        return redirect("/login")

    return render(request, "login.html")

def admin_home(request):
    return render(request, "ADMIN/index.html")

def admin_view_users(request):
    users = Citizen.objects.all()
    return render(request, "ADMIN/view_users.html", {"users": users})


def admin_view_staff(request):
    staff_list = Staff.objects.all()
    return render(request, "ADMIN/view_staff.html", {"staff": staff_list})


def approve_staff(request):
    staff_id = request.GET.get("id")

    try:
        staff = Staff.objects.get(id=staff_id)
        staff.status = "active"
        staff.save()
        messages.success(request, "Staff approved successfully")
    except:
        messages.error(request, "Staff not found")

    return redirect("/view_staff")

def block_staff(request):
    staff_id = request.GET.get("id")
    try:
        staff = Staff.objects.get(id=staff_id)
        staff.status = "blocked"
        staff.save()
        messages.success(request, "Staff blocked")
    except:
        messages.error(request, "Staff not found")
    return redirect("/view_staff")

def unblock_staff(request):
    staff_id = request.GET.get("id")
    try:
        staff = Staff.objects.get(id=staff_id)
        staff.status = "active"
        staff.save()
        messages.success(request, "Staff unblocked")
    except:
        messages.error(request, "Staff not found")
    return redirect("/view_staff")

def reject_staff(request):
    staff_id = request.GET.get("id")
    try:
        staff = Staff.objects.get(id=staff_id)
        staff.status = "rejected"
        staff.save()
        messages.success(request, "Staff rejected")
    except:
        messages.error(request, "Staff not found")
    return redirect("/view_staff")

def block_citizen(request):
    citizen_id = request.GET.get("id")
    try:
        citizen = Citizen.objects.get(id=citizen_id)
        citizen.status = "blocked"
        citizen.save()
        messages.success(request, "Citizen blocked")
    except:
        messages.error(request, "Citizen not found")
    return redirect("/admin_view_users")

def unblock_citizen(request):
    citizen_id = request.GET.get("id")
    try:
        citizen = Citizen.objects.get(id=citizen_id)
        citizen.status = "active"
        citizen.save()
        messages.success(request, "Citizen unblocked")
    except:
        messages.error(request, "Citizen not found")
    return redirect("/admin_view_users")


def admin_view_workers(request):
    workers = Worker.objects.all()
    return render(request, "ADMIN/view_workers.html", {"workers": workers})


def approve_worker(request):
    worker_id = request.GET.get("id")
    try:
        worker = Worker.objects.get(id=worker_id)
        worker.status = "active"
        worker.save()
        messages.success(request, "Worker approved successfully")
    except:
        messages.error(request, "Worker not found")
    return redirect("/admin_view_workers")


def reject_worker(request):
    worker_id = request.GET.get("id")
    try:
        worker = Worker.objects.get(id=worker_id)
        worker.status = "rejected"
        worker.save()
        messages.success(request, "Worker rejected")
    except:
        messages.error(request, "Worker not found")
    return redirect("/admin_view_workers")


def block_worker(request):
    worker_id = request.GET.get("id")
    try:
        worker = Worker.objects.get(id=worker_id)
        worker.status = "blocked"
        worker.save()
        messages.success(request, "Worker blocked")
    except:
        messages.error(request, "Worker not found")
    return redirect("/admin_view_workers")


def unblock_worker(request):
    worker_id = request.GET.get("id")
    try:
        worker = Worker.objects.get(id=worker_id)
        worker.status = "active"
        worker.save()
        messages.success(request, "Worker unblocked")
    except:
        messages.error(request, "Worker not found")
    return redirect("/admin_view_workers")

def admin_view_complaints(request):
    if 'aid' not in request.session:
        return redirect('/login/')

    complaints = Complaint.objects.all().order_by('-created_at')
    complaint_data = []

    for c in complaints:
        latest_action = ComplaintAction.objects.filter(complaint=c).order_by('-action_date').first()
        complaint_data.append({
            "complaint": c,
            "latest_action": latest_action
        })

    return render(request, "ADMIN/view_complaints.html", {"complaint_data": complaint_data})

def admin_add_department(request):
    # Admin session check
    if 'aid' not in request.session:
        return redirect('/login/')

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        if Department.objects.filter(name=name).exists():
            messages.error(request, "Department already exists.")
        else:
            Department.objects.create(
                name=name,
                description=description
            )
            messages.success(request, "Department added successfully.")

        return redirect('/admin_add_department/')

    departments = Department.objects.all().order_by('name')

    return render(request, "ADMIN/add_department.html", {
        "departments": departments
    })

def admin_view_department(request):
    # Admin session check
    if 'aid' not in request.session:
        return redirect('/login/')

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        if Department.objects.filter(name=name).exists():
            messages.error(request, "Department already exists.")
        else:
            Department.objects.create(
                name=name,
                description=description
            )
            messages.success(request, "Department added successfully.")

        return redirect('/admin_view_department/')

    departments = Department.objects.all().order_by('name')

    return render(request, "ADMIN/view_department.html", {
        "departments": departments
    })

def admin_edit_department(request):
    # Admin session check
    if 'aid' not in request.session:
        return redirect('/login/')

    dept_id = request.GET.get('id')
    try:
        dept = Department.objects.get(id=dept_id)
    except Department.DoesNotExist:
        messages.error(request, "Department not found.")
        return redirect('/admin_view_department/')

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        # Check if the new name already exists for a different department
        if Department.objects.filter(name=name).exclude(id=dept_id).exists():
            messages.error(request, "Department name already exists.")
        else:
            dept.name = name
            dept.description = description
            dept.save()
            messages.success(request, "Department updated successfully.")
            return redirect('/admin_view_department/')

    return render(request, "ADMIN/edit_department.html", {
        "department": dept
    })

def admin_delete_department(request):
    # Admin session check
    if 'aid' not in request.session:
        return redirect('/login/')

    dept_id = request.GET.get('id')
    try:
        dept = Department.objects.get(id=dept_id)
        dept.delete()
        messages.success(request, "Department deleted successfully.")
    except Department.DoesNotExist:
        messages.error(request, "Department not found.")

    return redirect('/admin_view_department/')




def admin_view_feedbacks(request):
    feedbacks = Feedback.objects.select_related(
        'citizen', 'complaint'
    ).order_by('-created_at')

    return render(request, "ADMIN/view_feedbacks.html", {
        "feedbacks": feedbacks
    })


def admin_reply_feedback(request, feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)

    if request.method == "POST":
        reply = request.POST.get('reply')
        feedback.reply = reply
        feedback.save()
        return redirect('/admin_view_feedback/')

    return render(request, "ADMIN/reply_feedback.html", {
        "feedback": feedback
    })


def admin_view_reports(request):
    reports = Report.objects.select_related(
        'complaint', 'reporter'
    ).order_by('-created_at')

    return render(request, "ADMIN/view_reports.html", {
        "reports": reports
    })


def staff_home(request):
    try:
        staff = Staff.objects.get(loginid_id=request.session['sid'])
    except:
        return redirect('/login/')
    return render(request, "STAFF/index.html", {"staff": staff})


def staff_assign_worker(request):
    if 'sid' not in request.session:
        return redirect('/login/')

    try:
        staff = Staff.objects.get(loginid_id=request.session['sid'])
    except Staff.DoesNotExist:
        return redirect('/login/')

    complaint_id = request.GET.get('id')
    if not complaint_id:
        return redirect('/staff_complaints/')

    complaint = Complaint.objects.get(id=complaint_id)
    workers = Worker.objects.filter(department=staff.department, status="active")

    if request.method == "POST":
        worker_id = request.POST.get('worker_id')
        worker = Worker.objects.get(id=worker_id)
        complaint.worker = worker
        complaint.status = "Assigned"
        complaint.save()
        
        ComplaintAction.objects.create(
            complaint=complaint,
            staff=staff,
            action_note=f"Assigned to worker {worker.name}",
            status_updated_to="Assigned"
        )
        
        messages.success(request, f"Work assigned to {worker.name}")
        return redirect('/staff_complaints/')

    return render(request, "STAFF/assign_worker.html", {
        "staff": staff,
        "complaint": complaint,
        "workers": workers
    })


def worker_home(request):
    if 'wid' not in request.session:
        return redirect('/login/')
    try:
        worker = Worker.objects.get(loginid_id=request.session['wid'])
    except Worker.DoesNotExist:
        return redirect('/login/')
    return render(request, "WORKER/index.html", {"worker": worker})


def worker_view_assigned_works(request):
    if 'wid' not in request.session:
        return redirect('/login/')
    try:
        worker = Worker.objects.get(loginid_id=request.session['wid'])
    except Worker.DoesNotExist:
        return redirect('/login/')

    works = Complaint.objects.filter(worker=worker).order_by('-created_at')
    return render(request, "WORKER/view_assigned_works.html", {
        "worker": worker,
        "works": works
    })


def worker_update_work_status(request):
    if 'wid' not in request.session:
        return redirect('/login/')
    try:
        worker = Worker.objects.get(loginid_id=request.session['wid'])
    except Worker.DoesNotExist:
        return redirect('/login/')

    complaint_id = request.GET.get('id')
    complaint = Complaint.objects.get(id=complaint_id, worker=worker)

    if request.method == "POST":
        status = request.POST.get('status')
        note = request.POST.get('note')
        image = request.FILES.get('image')

        ComplaintAction.objects.create(
            complaint=complaint,
            worker=worker,
            action_note=note,
            action_image=image,
            status_updated_to=status,
            is_verified=False
        )
        
        # We don't update complaint status yet, staff must verify
        messages.success(request, "Work status updated. Waiting for staff verification.")
        return redirect('/worker_view_assigned_works/')

    return render(request, "WORKER/update_work.html", {
        "worker": worker,
        "complaint": complaint
    })


def staff_verify_work_update(request):
    if 'sid' not in request.session:
        return redirect('/login/')
    
    action_id = request.GET.get('action_id')
    action = ComplaintAction.objects.get(id=action_id)
    
    if request.method == "POST":
        action.is_verified = True
        action.save()
        
        # Update the main complaint status
        action.complaint.status = action.status_updated_to
        action.complaint.save()
        
        messages.success(request, "Work update verified successfully")
        return redirect(f'/staff_complaint_detail/?id={action.complaint.id}')
    
    return redirect('/staff_complaints/')


def my_profile(request):
    staff_member = Staff.objects.filter(loginid=request.user).first()
    return render(request, "STAFF/staff_profile.html", {"staff": staff_member})

def staff_complaints(request):
    # Session check
    if 'sid' not in request.session:
        return redirect('/login/')

    try:
        staff = Staff.objects.get(loginid_id=request.session['sid'])
    except Staff.DoesNotExist:
        return redirect('/login/')

    complaints = Complaint.objects.filter(
        department=staff.department
    ).select_related('citizen').order_by('-created_at')

    return render(
        request,
        "STAFF/staff_complaints.html",
        {
            "staff": staff,
            "complaints": complaints
        }
    )
def add_complaint_action(request):
    if 'sid' not in request.session:
        return redirect('/login/')

    try:
        staff = Staff.objects.get(loginid_id=request.session['sid'])
    except Staff.DoesNotExist:
        return redirect('/login/')

    if request.method == "POST":
        complaint_id = request.POST.get('complaint_id')

        complaint = Complaint.objects.filter(
            id=complaint_id,
            department=staff.department
        ).first()

        if not complaint:
            return redirect('/staff_complaints/')

        # Redirect to the action page with complaint_id in GET
        return redirect(f'/staff_complaint_action_page/?complaint_id={complaint.id}')
    
    return redirect('/staff_complaints/')


def staff_complaint_action_page(request):
    if 'sid' not in request.session:
        return redirect('/login/')

    try:
        staff = Staff.objects.get(loginid_id=request.session['sid'])
    except Staff.DoesNotExist:
        return redirect('/login/')

    complaint_id = request.GET.get('complaint_id')
    if not complaint_id:
        return redirect('/staff_complaints/')

    complaint = Complaint.objects.filter(
        id=complaint_id,
        department=staff.department
    ).first()

    if not complaint:
        return redirect('/staff_complaints/')

    if request.method == "POST":
        ComplaintAction.objects.create(
            complaint=complaint,
            staff=staff,
            action_note=request.POST.get("action_note"),
            status_updated_to=request.POST.get("status_updated_to"),
            action_image=request.FILES.get("action_image")
        )
        complaint.status = request.POST.get("status_updated_to")
        complaint.save()
        return redirect('/staff_complaints/')

    actions = ComplaintAction.objects.filter(
        complaint=complaint
    ).select_related('staff').order_by('-action_date')

    return render(request, "STAFF/add_complaint_action.html", {
        "staff": staff,
        "complaint": complaint,
        "actions": actions
    })




def citizen_home(request):
    return render(request, "CITIZEN/index.html")

def citizen_add_complaint(request):
    if 'cid' not in request.session:
        return redirect('/login')

    try:
        citizen = Citizen.objects.get(loginid_id=request.session['cid'])
    except Citizen.DoesNotExist:
        return redirect('/login')

    departments = Department.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        
        # Get detailed location fields
        area = request.POST.get("area")
        landmark = request.POST.get("landmark")
        district = request.POST.get("district")
        pincode = request.POST.get("pincode")
        
        # Format location string
        location = f"{area}, Near {landmark}, {district}, PIN: {pincode}"
        
        department_id = request.POST.get("department")
        image = request.FILES.get("damaged_image")

        department = None
        if department_id:
            department = Department.objects.get(id=department_id)

        Complaint.objects.create(
            citizen=citizen,
            title=title,
            description=description,
            location=location,
            department=department,
            damaged_image=image
        )

        return redirect("/citizen_home")

    return render(request, "CITIZEN/add_complaint.html", {
        "departments": departments
    })

def user_view_complaints(request):
    if 'cid' not in request.session:
        return redirect('/login/')

    try:
        citizen = Citizen.objects.get(loginid_id=request.session['cid'])
    except Citizen.DoesNotExist:
        return redirect('/login/')

    complaints = Complaint.objects.filter(
        citizen=citizen
    ).order_by('-created_at')

    complaint_data = []
    for c in complaints:
        # Get the latest action uploaded by staff (official workdone image)
        workdone_action = ComplaintAction.objects.filter(
            complaint=c,
            staff__isnull=False
        ).exclude(action_image='').order_by('-action_date').first()
        
        # Check if feedback already exists for this complaint
        feedback_exists = Feedback.objects.filter(complaint=c, citizen=citizen).exists()
        
        complaint_data.append({
            "complaint": c,
            "workdone_action": workdone_action,
            "feedback_exists": feedback_exists
        })

    return render(request, "CITIZEN/view_complaints.html", {
        "complaint_data": complaint_data
    })

def add_feedback(request):
    if 'cid' not in request.session:
        return redirect('/login/')

    try:
        citizen = Citizen.objects.get(loginid_id=request.session['cid'])
    except Citizen.DoesNotExist:
        return redirect('/login/')

    if request.method == "POST":
        complaint_id = request.POST.get('complaint_id')
        message = request.POST.get('message')
        rating = request.POST.get('rating')

        try:
            complaint = Complaint.objects.get(
                id=complaint_id,
                citizen=citizen,
                status__in=["Completed", "Finished"]
            )
        except Complaint.DoesNotExist:
            messages.error(request, "Invalid complaint or not completed yet.")
            return redirect('/user_view_complaints/')

        # Check if feedback already exists for this complaint
        if Feedback.objects.filter(complaint=complaint, citizen=citizen).exists():
            messages.error(request, "You have already submitted feedback for this complaint.")
            return redirect('/view_feedbacks/')

        Feedback.objects.create(
            citizen=citizen,
            complaint=complaint,
            message=message,
            rating=rating
        )
        messages.success(request, "Feedback added successfully.")
        return redirect('/view_feedbacks/')

    # GET method - render feedback form
    complaint_id = request.GET.get('id')
    if not complaint_id:
        return redirect('/user_view_complaints/')
        
    try:
        complaint = Complaint.objects.get(id=complaint_id, citizen=citizen)
    except Complaint.DoesNotExist:
        return redirect('/user_view_complaints/')

    # If feedback already exists, redirect to edit
    if Feedback.objects.filter(complaint=complaint, citizen=citizen).exists():
        feedback = Feedback.objects.get(complaint=complaint, citizen=citizen)
        return redirect(f'/edit_feedback/?id={feedback.id}')

    return render(request, "CITIZEN/add_feedback.html", {
        "complaint": complaint
    })

def edit_feedback(request):
    if 'cid' not in request.session:
        return redirect('/login/')

    try:
        citizen = Citizen.objects.get(loginid_id=request.session['cid'])
    except Citizen.DoesNotExist:
        return redirect('/login/')

    feedback_id = request.GET.get('id')
    if not feedback_id:
        return redirect('/view_feedbacks/')

    try:
        feedback = Feedback.objects.get(id=feedback_id, citizen=citizen)
    except Feedback.DoesNotExist:
        return redirect('/view_feedbacks/')

    if request.method == "POST":
        feedback.message = request.POST.get('message')
        feedback.rating = request.POST.get('rating')
        feedback.save()
        messages.success(request, "Feedback updated successfully.")
        return redirect('/view_feedbacks/')

    return render(request, "CITIZEN/edit_feedback.html", {
        "feedback": feedback
    })

def delete_feedback(request):
    if 'cid' not in request.session:
        return redirect('/login/')

    feedback_id = request.GET.get('id')
    try:
        citizen = Citizen.objects.get(loginid_id=request.session['cid'])
        feedback = Feedback.objects.get(id=feedback_id, citizen=citizen)
        feedback.delete()
        messages.success(request, "Feedback deleted successfully.")
    except (Citizen.DoesNotExist, Feedback.DoesNotExist):
        messages.error(request, "Feedback not found or access denied.")

    return redirect('/view_feedbacks/')



def view_feedbacks(request):
    # Ensure user is logged in
    if 'cid' not in request.session:
        return redirect('/login/')

    try:
        citizen = Citizen.objects.get(loginid_id=request.session['cid'])
    except Citizen.DoesNotExist:
        return redirect('/login/')

    # Get only feedbacks submitted by this citizen
    feedbacks = Feedback.objects.filter(citizen=citizen).select_related('complaint').order_by('-created_at')

    return render(request, "CITIZEN/view_feedbacks.html", {
        "feedbacks": feedbacks
    })



def add_report(request):
    if 'cid' not in request.session:
        return redirect('/login/')

    try:
        citizen = Citizen.objects.get(loginid_id=request.session['cid'])
    except Citizen.DoesNotExist:
        return redirect('/login/')

    complaint_id = request.GET.get('id')
    if not complaint_id:
        return redirect('/user_view_complaints/')

    try:
        complaint = Complaint.objects.get(
            id=complaint_id,
            citizen=citizen,
            status__in=["Completed", "Finished"]
        )
    except Complaint.DoesNotExist:
        return redirect('/user_view_complaints/')

    if request.method == "POST":
        subject = request.POST.get('subject')
        description = request.POST.get('description')

        Report.objects.create(
            reporter=citizen,
            complaint=complaint,
            subject=subject,
            description=description
        )
        return redirect('/view_reports/')

    return render(request, "CITIZEN/add_report.html", {
        "complaint": complaint
    })


def view_reports(request):
    if 'cid' not in request.session:
        return redirect('/login/')

    reports = Report.objects.select_related(
        'complaint', 'reporter'
    ).order_by('-created_at')

    return render(request, "CITIZEN/view_reports.html", {
        "reports": reports
    })


def staff_complaint_detail(request):
    if 'sid' not in request.session:
        return redirect('/login/')

    complaint_id = request.GET.get('id')
    if not complaint_id:
        return redirect('/staff_complaints/')

    try:
        staff = Staff.objects.get(loginid_id=request.session['sid'])
        complaint = Complaint.objects.get(
            id=complaint_id,
            department=staff.department
        )
    except (Staff.DoesNotExist, Complaint.DoesNotExist):
        return redirect('/staff_complaints/')

    actions = ComplaintAction.objects.filter(complaint=complaint).order_by('-action_date')

    return render(request, "STAFF/complaint_detail.html", {
        "complaint": complaint,
        "actions": actions,
        "staff": staff
    })


def citizen_complaint_detail(request):
    if 'cid' not in request.session:
        return redirect('/login/')

    complaint_id = request.GET.get('id')
    if not complaint_id:
        return redirect('/user_view_complaints/')

    try:
        citizen = Citizen.objects.get(loginid_id=request.session['cid'])
        complaint = Complaint.objects.get(
            id=complaint_id,
            citizen=citizen
        )
    except (Citizen.DoesNotExist, Complaint.DoesNotExist):
        return redirect('/user_view_complaints/')

    # Filter actions to show ONLY those uploaded by staff
    actions = ComplaintAction.objects.filter(
        complaint=complaint,
        staff__isnull=False
    ).order_by('-action_date')

    return render(request, "CITIZEN/complaint_detail.html", {
        "complaint": complaint,
        "actions": actions
    })


def admin_complaint_detail(request):
    if 'aid' not in request.session:
        return redirect('/login/')

    complaint_id = request.GET.get('id')
    if not complaint_id:
        return redirect('/admin_view_complaints/')

    try:
        complaint = Complaint.objects.get(id=complaint_id)
    except Complaint.DoesNotExist:
        return redirect('/admin_view_complaints/')

    actions = ComplaintAction.objects.filter(complaint=complaint).order_by('-action_date')

    return render(request, "ADMIN/complaint_detail.html", {
        "complaint": complaint,
        "actions": actions
    })


def chat_list(request):
    if 'sid' in request.session:
        # Staff sees workers in their department
        staff = Staff.objects.get(loginid_id=request.session['sid'])
        contacts = Worker.objects.filter(department=staff.department, status="active")
        context = {"staff": staff, "contacts": contacts, "role": "staff"}
        return render(request, "STAFF/chat_list.html", context)
    
    elif 'wid' in request.session:
        # Worker sees staff in their department
        worker = Worker.objects.get(loginid_id=request.session['wid'])
        contacts = Staff.objects.filter(department=worker.department, status="active")
        context = {"worker": worker, "contacts": contacts, "role": "worker"}
        return render(request, "WORKER/chat_list.html", context)
    
    return redirect('/login/')


def chat_messages(request, receiver_id):
    if 'sid' not in request.session and 'wid' not in request.session:
        return redirect('/login/')
    
    sender_login = request.user
    receiver_login = Login.objects.get(id=receiver_id)
    
    if request.method == "POST":
        msg = request.POST.get('message')
        if msg:
            Chat.objects.create(
                sender=sender_login,
                receiver=receiver_login,
                message=msg
            )
        return redirect(f'/chat_messages/{receiver_id}/')

    # Get messages between these two users
    messages_list = Chat.objects.filter(
        models.Q(sender=sender_login, receiver=receiver_login) |
        models.Q(sender=receiver_login, receiver=sender_login)
    ).order_by('timestamp')

    template = ""
    user_info = {}
    if 'sid' in request.session:
        staff = Staff.objects.get(loginid_id=request.session['sid'])
        receiver_worker = Worker.objects.get(loginid=receiver_login)
        template = "chat.html" # Shared template
        user_info = {"name": staff.name, "role": "staff"}
    elif 'wid' in request.session:
        worker = Worker.objects.get(loginid_id=request.session['wid'])
        receiver_staff = Staff.objects.get(loginid=receiver_login)
        template = "chat.html" # Shared template
        user_info = {"name": worker.name, "role": "worker"}

    return render(request, template, {
        "messages_list": messages_list,
        "receiver_login": receiver_login,
        "user_info": user_info
    })
