import tempfile
from django.shortcuts import render, redirect
from .forms import UploadCSVFileForm
import pandas as pd
import os
from itertools import zip_longest


from pprint import pprint

def handle_uploaded_file(f):
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        for chunk in f.chunks():
            fp.write(chunk)
        fp.flush()
        return fp.name
    
    return None


def upload_file(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UploadCSVFileForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # get the uploaded files
                    cgpa_file = handle_uploaded_file(request.FILES['Student_File'])
                    teacher_list_file = handle_uploaded_file(request.FILES['Teacher_File'])

                    # cread csv into pandas
                    cgpas = pd.read_csv(cgpa_file)
                    teachers = pd.read_csv(teacher_list_file)

                    # sort by CGPA column
                    sorted_cgpa = cgpas.sort_values(by=["CGPA"], ascending=False, ignore_index=True)

                    # add roll and teachers
                    cgpaNteacher = assign_teachers(sorted_cgpa["Roll"].tolist(), teachers["Teachers"].tolist())

                    # convert to html for the web
                    html_table = cgpaNteacher.to_html(index=False)

                    # convert to csv for downloading
                    csv_content = cgpaNteacher.to_csv(index=False)

                    # the next form
                    form = UploadCSVFileForm()

                    # delete temporary files created by handle_uploaded_file
                    os.unlink(cgpa_file)
                    os.unlink(teacher_list_file)

                    #return response
                    return render(request, 'upload_csv.html', {'form': form, 'csv_content': csv_content, 'html_table': html_table})
                except:
                    return render(request, 'upload_csv.html', {'message': 'Incorrect input file'})

        form = UploadCSVFileForm()
        return render(request, 'upload_csv.html', {'form': form})
    else:
        return redirect("accounts/login")

def assign_teachers(rolls, teachers):
    teacher_length = len(teachers)
    #slice_factor = teacher_length-3

    # slice the list according to teacher list length
    sliced_rolls = []
    while len(rolls) > 0:
        sliced_rolls.append(list(rolls[:teacher_length]))
        rolls = rolls[teacher_length:]

    # transpose the list
    allocated_rolls = []
    for sliced_roll in zip_longest(*sliced_rolls, fillvalue=None):
        l = [x for x in list(sliced_roll) if x is not None]
        allocated_rolls.append(l)

    df = pd.DataFrame(allocated_rolls)

    df["Supervisor"] = pd.Series(teachers)
    df.fillna('', inplace=True)

    # n_teachers = teachers
    # df_len = len(df.index)

    # # make the teacher list same as the size of the data frame append the same list multiple times
    # while n_teachers.size <= df_len:
    #     n_teachers = pd.concat([n_teachers, teachers], ignore_index=True)

    # # create new column in the dataframe

    # df["Teacher"] = n_teachers
    
    # df = df.groupby(["Teacher"]).agg({"Roll": lambda x: x.tolist()}).reset_index()

    return df
