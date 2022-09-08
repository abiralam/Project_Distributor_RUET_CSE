from django import forms

class UploadCSVFileForm(forms.Form):
    cgpa_file = forms.FileField()
    teacher_list_file = forms.FileField()