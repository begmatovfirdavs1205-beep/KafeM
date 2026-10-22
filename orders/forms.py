import re

from django import forms

from orders.models import Order


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label="Ваше имя", max_length=120)
    phone = forms.CharField(label="Номер телефона", max_length=30)
    fulfillment = forms.ChoiceField(label="Как получить заказ", choices=Order.Fulfillment.choices, initial=Order.Fulfillment.DELIVERY, widget=forms.RadioSelect)
    address = forms.CharField(label="Адрес доставки", max_length=250, required=False)
    comment = forms.CharField(label="Комментарий к заказу", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 9 or len(digits) > 15:
            raise forms.ValidationError("Укажите корректный номер телефона.")
        return phone

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("fulfillment") == Order.Fulfillment.DELIVERY and not cleaned.get("address", "").strip():
            self.add_error("address", "Укажите адрес доставки.")
        if cleaned.get("fulfillment") == Order.Fulfillment.PICKUP:
            cleaned["address"] = ""
        return cleaned
