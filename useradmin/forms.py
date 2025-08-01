from core.models import Product
from django import forms
# from bootstrap_datepicker_plus import DatePickerInput



class AddProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Product Title", "class":"form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Product Description", "class":"form-control"}))
    price = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': "Sale Price", "class":"form-control"}))
    old_price = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': "Old Price", "class":"form-control"}))
    type = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Type of product e.g organic cream", "class":"form-control"}))
    stock_count = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': "How many are in stock?", "class":"form-control"}))
    life = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "How long would this product live?", "class":"form-control"}))
    mfd = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'placeholder': "e.g: 22-11-02", "class":"form-control"}))
    tags = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Tags", "class":"form-control"}))
    image = forms.ImageField(widget=forms.FileInput(attrs={"class":"form-control"}))

    base_price = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Base Price', 'class': 'form-control'}), required=False)
    max_price = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Max Price', 'class': 'form-control'}), required=False)
    selling_price = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Selling Price', 'class': 'form-control'}), required=False)
    weekly_sales = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Weekly Sales', 'class': 'form-control'}), required=False)
    last_week_sales = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Last Week Sales', 'class': 'form-control'}), required=False)
    price_adjustment_step = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Price Adjustment Step', 'class': 'form-control'}), required=False)

    class Meta:
        model = Product
        fields = [
            'title',
            'image',
            'description',
            'price',
            'old_price',
            'base_price',
            'max_price',
            'selling_price',
            'weekly_sales',
            'last_week_sales',
            'price_adjustment_step',
            'specifications',
            'type',
            'stock_count',
            'life',
            'mfd',
            'tags',
            'digital',
            'category',
        ]
        widgets = {
            # 'mdf': DateTimePickerInput
        }