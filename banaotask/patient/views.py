from django.shortcuts import render
from django.shortcuts import redirect
from doctor.models import *
# Create your views here.


def logout(request):
    if "email" in request.session:
        del request.session['email']
        return redirect("login")
    else:
        return redirect("login")
    
def patient_dashboard(request):
    if "email" in request.session:

        uid = User.objects.get(email = request.session['email'])

        pid = Patient.objects.get(user_id=uid)
        context = {
            'uid': uid,
            'pid': pid,
        }
        return render(request, "patient/patient-dashboard.html", context)
    
def all_blogs(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')
    if selected_category_id:
        blogs = Blog.objects.filter(category__id=selected_category_id)
    else:
        blogs = Blog.objects.all()
    context = {'categories': categories, 'blogs': blogs}
    return render(request, 'patient/all-blogs.html', context)
