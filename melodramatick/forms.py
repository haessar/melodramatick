from django import forms


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class TxtImportForm(forms.Form):
    txt_file = forms.FileField()
