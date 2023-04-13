from django.shortcuts import render
from .models import *
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def login(request):
    if request.method == 'POST':
        pusername = request.POST['username']
        ppassword = request.POST['password']

        try:
            uid = User.objects.get(username=pusername)
        except User.DoesNotExist:
            # Display error message if the username doesn't exist
            error_message = 'Invalid username'
            return render(request, 'doctor/login.html', {'error_message': error_message})

        if uid.password == ppassword:
            if uid.role == "doctor":
                did = Doctor.objects.get(user_id=uid)
                request.session['email'] = uid.email  # session store
                context = {
                    'uid': uid,
                    'did': did,
                }
                return render(request, "doctor/doc-dashboard.html", context)

            elif uid.role == "patient":
                pid = Patient.objects.get(user_id=uid)
                request.session['email'] = uid.email  # session store
                context = {
                    'uid': uid,
                    'pid': pid,
                }
                return render(request, "patient/patient-dashboard.html", context)
        else:
            # Display error message if the password doesn't match
            error_message = 'Invalid password'
            return render(request, 'doctor/login.html', {'error_message': error_message})

    return render(request, 'doctor/login.html')


                        
def signup(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        role = request.POST.get('role')
        profile_pic = request.FILES.get('profilepic')

        # Check if passwords match
        if password != confirm_password:
            return render(request, 'doctor/signup.html', {'emsg': 'Passwords do not match'})

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'doctor/signup.html', {'emsg': 'Email is already registered'})

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'doctor/signup.html', {'emsg': 'Username is already taken'})

        uid = User.objects.create(username=username, email=email, password=password, role=role)
        if role == 'doctor':
            did = Doctor.objects.create(user_id = uid, address=address, city=city, state=state, pincode=pincode, profile_pic=profile_pic,firstname=firstname,lastname=lastname, confirm_password=confirm_password)
            return redirect('login')
        elif role == 'patient':
            pid = Patient.objects.create(user_id=uid, address=address, city=city, state=state, pincode=pincode, profile_pic=profile_pic,firstname=firstname,lastname=lastname, confirm_password=confirm_password)
            return redirect('login')
        
    return render(request, 'doctor/signup.html')

            
def logout(request):
    if "email" in request.session:
        del request.session['email']
        return redirect("login")
    else:
        return redirect("login")


@login_required(login_url='login')
def doc_dashboard(request):
    if "email" in request.session:

        uid = User.objects.get(email = request.session['email'])

        did = Doctor.objects.get(user_id=uid)
        context = {
            'uid': uid,
            'did': did,
        }
        return render(request, "doctor/doc-dashboard.html", context)


def add_blog(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'doctor/add-blogs.html', context)

def dr_add_blog(request):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        did = Doctor.objects.get(user_id=uid)

        if request.method == "POST":
            category_id = request.POST.get("category")
            category = Category.objects.get(pk=category_id)
            if request.POST.get("submit_draft"):
                draft_blog = Draft_Blog.objects.create(
                    user_id=uid,
                    title=request.POST['title'],
                    category=category,
                    description=request.POST['content'],
                )

                if request.FILES:
                    draft_blog.blog_pic = request.FILES['image']
                    draft_blog.save()

                msg = "Blog saved as draft successfully..!!"

            elif request.POST.get("submit_post"):
                blog = Blog.objects.create(
                    user_id=uid,
                    title=request.POST['title'],
                    category=category,
                    description=request.POST['content'],
                )

                if request.FILES:
                    blog.blog_pic = request.FILES['image']
                    blog.save()

                msg = "Blog posted successfully..!!"
            else:
                msg = "Invalid request"

        return render(request, "doctor/add-blogs.html", {"msg": msg})
    else:
        return redirect("login")


def my_blog(request):
    blogs = Blog.objects.all()
    return render(request, 'doctor/my-blogs.html', {'blogs': blogs})

def my_draft_blog(request):
    draft_blog = Draft_Blog.objects.all()
    context = {'draft_blog': draft_blog}
    return render(request, 'doctor/my-draft-blogs.html', context)

def post_draft_blog(request, id):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        did = Doctor.objects.get(user_id=uid)

        draft_blog = Draft_Blog.objects.get(id=id)

        if request.method == 'POST':
            # Create a new blog post from the draft blog
            blog = Blog.objects.create(
                user_id=uid,
                title=draft_blog.title,
                category=draft_blog.category,
                description=draft_blog.description,
                blog_pic=draft_blog.blog_pic,
            )

            # Delete the draft blog from the database
            draft_blog.delete()

            messages.success(request, 'Your blog post has been created!')
            return redirect('my-blogs')

    context = {'draft_blog': draft_blog}
    return render(request, 'doctor/my-draft-blogs.html', context)