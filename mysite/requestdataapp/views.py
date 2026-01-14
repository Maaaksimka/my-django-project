from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from requestdataapp.forms import UserBioForm, UploadFileForm

SIZE = 1048576 * 2


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render(request, "requestdataapp/request-query-params.html", context=context)

def user_form(request: HttpRequest)-> HttpResponse:
    context = {
        "form": UserBioForm(),
    }
    return render(request, "requestdataapp/user-bio-form.html", context=context)

def handle_file_upload(request: HttpRequest) -> HttpResponse:

    context = {
        "form": UploadFileForm(),
        "size": SIZE,
    }

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # myfile = request.FILES["myfile"]
            myfile = form.cleaned_data["file"]
            # print("myfile", myfile.size)
            if myfile.size <= SIZE:
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                print("saved file", filename)
                return render(request, "requestdataapp/file-upload.html", context=context)
            else:
                return render(request, "requestdataapp/file-size-does-not-match.html", context=context)
        else:
            form = UploadFileForm()

    return render(request, "requestdataapp/file-upload.html", context=context)