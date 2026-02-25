from django.db import models
from django.contrib.auth.models import AbstractUser


class Login(AbstractUser):
    userType = models.CharField(max_length=50)  
    # admin / user / staff / volunteer / worker

    viewPass = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username
    
class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Citizen(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Staff(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    profile_pic = models.ImageField(upload_to="staff_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="active")

    def __str__(self):
        return self.name


class Worker(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    profile_pic = models.ImageField(upload_to="worker_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="pending")

    def __str__(self):
        return self.name


class Complaint(models.Model):
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    damaged_image = models.ImageField(upload_to="complaint_images", null=True, blank=True)
    status = models.CharField(max_length=50, default="Pending")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class ComplaintAction(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True)

    action_note = models.TextField()
    action_image = models.ImageField(
        upload_to="action_images",
        null=True,
        blank=True
    )

    status_updated_to = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)

    action_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Action on {self.complaint.title}"


class Chat(models.Model):
    sender = models.ForeignKey(Login, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(Login, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"


class Notification(models.Model):
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)

    message = models.CharField(max_length=300)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class Feedback(models.Model):
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)

    message = models.TextField()
    rating = models.IntegerField(null=True, blank=True)

    reply = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.complaint.title}"


class Report(models.Model):
    reporter = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)

    subject = models.CharField(max_length=200)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
