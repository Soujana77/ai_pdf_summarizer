from django.shortcuts import render
from .forms import UploadPDFForm
from .utils import extract_text, generate_summary
def home(request):
    return render(request, 'notes/home.html')

def upload_pdf(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            saved_file = form.save()
            pdf_path = saved_file.file.path

            # Extract text
            full_text = extract_text(pdf_path)

            # Limit text for summary
            summary = generate_summary(full_text[:1500])

            context = {
                'text': full_text,
                'summary': summary,
            }
            return render(request, 'notes/show_text.html', context)

    else:
        form = UploadPDFForm()

    return render(request, 'notes/upload.html', {'form': form})
