from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Div, Field, HTML, Layout, Row
from django import forms
from django_filters.fields import RangeField


class WorkFilterFormHelper(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False
        self.helper.form_class = 'form-horizontal'
        layout_fields = []
        for field_name, field in self.fields.items():
            if isinstance(field, RangeField):
                slider_field = Field(field_name, template="forms/fields/range-slider.html")
            else:
                layout_fields.append(Field(field_name, css_class="custom-select custom-select-sm"))
        dropdowns = Div(Row(*layout_fields), css_class="col-md-8")
        self.helper.layout = Layout(Row(dropdowns,
                                    Div(slider_field, css_class="col-md-4")),
                                    Row(StrictButton("Filter", name='submit', type='submit', css_class='btn btn-primary'),
                                        HTML('<a class="btn btn-secondary" href={% url "work:index" %}>Reset</a>')))
