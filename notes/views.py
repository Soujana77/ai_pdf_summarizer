from django.shortcuts import render
from .forms import UploadPDFForm
from .utils import (
    extract_text, 
    generate_summary,
    generate_keywords,
    generate_bullets,
    explain_like_5,
    simplify_text,
    translate_text,
    generate_flashcards,
    extract_keywords,
    generate_quiz
)

# -----------------------
# HOME PAGE
# -----------------------
def home(request):
    return render(request, 'notes/home.html')


# -----------------------
# PDF UPLOAD + AI SUMMARY
# -----------------------
def upload_pdf(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            saved_file = form.save()
            pdf_path = saved_file.file.path

            # Extract text
            full_text = extract_text(pdf_path)

            # Limit text for summary (avoid long API cost)
            summary = generate_summary(full_text[:1500])

            context = {
                'text': full_text,
                'summary': summary,
            }
            return render(request, 'notes/show_text.html', context)

    else:
        form = UploadPDFForm()

    return render(request, 'notes/upload.html', {'form': form})


# -----------------------
# EXTRA AI TOOL VIEWS
# -----------------------
def ai_keywords(request):
    text = request.GET.get("text", "")
    result = generate_keywords(text)
    return render(request, "notes/ai_tool_output.html", {
        "title": "Keywords",
        "result": result
    })


def ai_bullets(request):
    text = request.GET.get("text", "")
    result = generate_bullets(text)
    return render(request, "notes/ai_tool_output.html", {
        "title": "Bullet Notes",
        "result": result
    })


def ai_explain5(request):
    text = request.GET.get("text", "")
    result = explain_like_5(text)
    return render(request, "notes/ai_tool_output.html", {
        "title": "Explain Like I'm 5",
        "result": result
    })


def ai_simplify(request):
    text = request.GET.get("text", "")
    result = simplify_text(text)
    return render(request, "notes/ai_tool_output.html", {
        "title": "Simplified Text",
        "result": result
    })


def ai_translate(request):
    text = request.GET.get("text", "")
    lang = request.GET.get("lang", "Kannada")
    result = translate_text(text, lang)
    return render(request, "notes/ai_tool_output.html", {
        "title": f"Translation to {lang}",
        "result": result
    })

# -----------------------
# NEW LEARNING TOOLS
# -----------------------
def flashcards_view(request):
    text = request.GET.get("text", "")
    if text:
        flashcards = generate_flashcards(text)
    else:
        flashcards = []
    
    return render(request, "notes/flashcards.html", {
        "text": text,
        "flashcards": flashcards
    })


def keywords_view(request):
    text = request.GET.get("text", "")
    if text:
        keywords = extract_keywords(text)
    else:
        keywords = []
        
    return render(request, "notes/keywords.html", {
        "text": text,
        "keywords": keywords
    })


def quiz_view(request):
    text = request.GET.get("text", "")
    if text:
        quiz = generate_quiz(text)
    else:
        quiz = []
        
    return render(request, "notes/quiz.html", {
        "text": text,
        "quiz": quiz
    })
