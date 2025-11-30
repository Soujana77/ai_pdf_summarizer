from django.shortcuts import render

def home(request):
    return render(request, 'notes/home.html')
from .forms import UploadPDFForm

def upload_pdf(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'notes/success.html')
    else:
        form = UploadPDFForm()
    return render(request, 'notes/upload.html', {'form': form})
