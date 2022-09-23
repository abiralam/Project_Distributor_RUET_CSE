from django import forms

class UploadCSVFileForm(forms.Form):
    Student_File = forms.FileField()
    Teacher_File = forms.FileField()