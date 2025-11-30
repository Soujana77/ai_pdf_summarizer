from django.shortcuts import render
from .forms import UploadPDFForm
from .utils import extract_text

def home(request):
    return render(request, 'notes/home.html')

def upload_pdf(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            saved_file = form.save()  # save file in media folder
            pdf_path = saved_file.file.path  # full path
            
            # extract text
            full_text = extract_text(pdf_path)

            # send extracted text to page
            return render(request, 'notes/show_text.html', {'text': full_text})
    else:
        form = UploadPDFForm()
    
    return render(request, 'notes/upload.html', {'form': form})
