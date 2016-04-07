import datetime
from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    coll_date = forms.DateField(input_formats=['%Y-%m-%d'])
    coll_time = forms.TimeField(input_formats=['%H:%M'])

    class Meta:
        model = Order
        exclude = ['order_time', 'collection_time', 'completed']

    def save(self, commit=True):
        obj = super(OrderForm, self).save(commit=False)
        data = self.cleaned_data
        today = data['coll_date']
        tm = data['coll_time']
        obj.collection_time = datetime.datetime.combine(today, tm)
        if commit:
            obj.save()
        return obj
